"""Canonical suite index; fail closed before the matrix if pilots/resources fail."""
import copy,shutil,subprocess,time,uuid,os,re
from pathlib import Path
from .artifacts import ROOT,load_json,atomic_json,finalize_run,configure_substeps
from .simulator import sha256,prepare_request,run_request
from .persist import import_reference,validate_schema,publish_report,ReferenceSession
from .compare import compare,validator_hash


def file_ref(root,path):return dict(path=str(path.relative_to(root)),sha256=sha256(path))


def aggregate(values):
    if 'failed' in values:return 'failed'
    if 'pending' in values:return 'pending'
    return 'passed' if 'passed' in values else 'not_applicable'


def verify_substep_pilots(pilots,executable):
    if pilots.get('executable_sha256')!=sha256(executable) or pilots.get('validator_sha256')!=validator_hash():
        raise ValueError('Pilot executable/validator identity differs from matrix')
    rows=pilots.get('pilots',[])
    if len(rows)!=3 or len({p['case_id'] for p in rows})!=3:
        raise ValueError('Three distinct physical pilots are required')
    for p in rows:
        measurements=p.get('measurements',[])
        if len(measurements)!=2 or {m['rate_Hz'] for m in measurements}!={192000,384000}:
            raise ValueError('Missing target-rate pilot measurement')
        for m in measurements:
            path=Path(m['comparison_directory'])/'report.json'
            if sha256(path)!=m['report_sha256']:raise ValueError('Changed pilot report')
            report=load_json(path);validate_schema('report',report)
            if report['inputs']['validator_sha256']!=pilots['validator_sha256']:
                raise ValueError('Pilot report was produced by another validator')
            target=path.parent.parent
            run_path=target/'run/run.json'
            if sha256(run_path)!=report['inputs']['run_sha256'] or sha256(target/'case.json')!=report['inputs']['case_sha256']:
                raise ValueError('Pilot run/case bytes changed')
            if load_json(run_path)['build']['executable_sha256']!=pilots['executable_sha256']:
                raise ValueError('Pilot run used another model executable')
            if report['case_id']!=p['case_id'] or report['execution_config'].get('integration_rate_Hz')!=768000 or report['execution_config']['rate_Hz']!=m['rate_Hz']:
                raise ValueError('Pilot report execution differs from requested matrix')
            if any(report['outcomes'][k]!='passed' for k in ('reference','numerical','wav')):
                raise ValueError('Pilot reference/numerical/WAV gate failed')


def validate_summary(summary,cases):
    validate_schema('suite_summary',summary)
    expected={(c['case_id'],r,c['physical_case_sha256']) for c in cases for r in ((192000,384000) if c['analysis_kind']=='transient' else (None,))}
    actual=[(e['case_id'],e['rate_Hz'],e['physical_case_sha256']) for e in summary['entries']]
    if len(actual)!=len(set(actual)) or set(actual)!=expected:raise ValueError('Omitted/duplicate/unexpected suite entry')
    paths=[summary['manifest'],summary['toolchain']]
    paths.extend(e[k] for e in summary['entries'] for k in ('case','run','nominal','refined','report') if e[k] is not None)
    for ref in paths:
        path=Path(ref['path'])
        if path.is_absolute() or '..' in path.parts or '\\' in ref['path'] or ':' in ref['path']:raise ValueError('Suite path escapes root')
    for e in summary['entries']:
        if any(e[k] is None for k in ('case','run','nominal','refined','report')) and not e['reason']:raise ValueError('Missing artifact reason')
        if e['status']=='passed' and (e['exit_code']!=0 or any(e[k] is None for k in ('case','run','nominal','refined','report'))):raise ValueError('Passing entry lacks evidence')


def produce_native_reference(case,base,physical,level,cfg,solver,*,tolerance_scale=1.,solver_fallback=False,topology_nodeset=False):
    """Retain each native attempt; retry producer failure with the other solver."""
    from .cli import make_deck
    refined=level=='refined'
    attempts=[]
    candidates=[solver]+([{'norm':'alt','alt':'norm'}[solver]] if solver_fallback else [])
    for candidate in candidates:
        dest=Path(cfg['workspace']['wsl_root'])/(case['case_id']+'-'+level+'-'+uuid.uuid4().hex)
        deck=make_deck(case,refined).replace('.temp 25','.temp 25\n.options solver='+candidate)
        if tolerance_scale!=1:
            deck=re.sub(r'\b(reltol|abstol|vntol|chgtol)=([0-9.eE+-]+)',
                        lambda m:f'{m[1]}={float(m[2])*tolerance_scale:.17g}',deck)
        if topology_nodeset:
            zeros={'input','tone_rc','output','z_clip','z_tone'}
            emitters={'input_emitter','output_emitter','output_cap'}
            guesses=[]
            for name in case['trace_columns'][1:]:
                if name.startswith('i_'):continue
                native={'z_clip':'xclip:z','z_tone':'xtone:z'}.get(name,name)
                value=0 if name in zeros else 3.85 if name in emitters else 4.5
                guesses.append(f'V({native})={value}')
            deck=deck.replace('.end','.nodeset '+' '.join(guesses)+'\n.end')
        prepare_request(ROOT/'reference/ts808',base,dest,request_id=dest.name,
                        settings=dict(level=level,maxstep_s=1/(384000*8*(2 if refined else 1)),
                                      dc_protocol='gminsteps=0 srcsteps=0; pseudo-transient audited'+
                                      ('; independent topology T22 nodeset' if topology_nodeset else '')),deck=deck)
        row=dict(directory=str(dest),request_sha256=sha256(dest/'request.json'),solver=candidate,
                 tolerance_scale=tolerance_scale,topology_nodeset=topology_nodeset,status='running')
        attempts.append(row)
        atomic_json(physical/(level+'-attempts.json'),dict(attempts=attempts))
        try:
            run_request(dest,Path(cfg['tools']['ltspice']['path']))
        except RuntimeError as error:
            row.update(status='failed',error=str(error))
            atomic_json(physical/(level+'-attempts.json'),dict(attempts=attempts))
            if candidate==candidates[-1]:raise
            print('Native producer retry',case['case_id'],level,candidate,'failed; trying',candidates[-1],flush=True)
            continue
        # Reader, provenance and coverage errors remain blocking; never hide them.
        imported=physical/level
        import_reference(dest,imported,cfg)
        row['status']='completed'
        atomic_json(physical/(level+'-attempts.json'),dict(attempts=attempts))
        atomic_json(physical/(level+'-request.json'),dict(directory=str(dest),request_sha256=row['request_sha256']))
        return imported


def suite(cases_path,toolchain_path,executable,rates,output,pilots_path,*,native_solver='norm',resume_from=None,native_solver_overrides=None,native_tolerance_scale=1.,native_solver_fallback=False,native_topology_nodeset=False,continue_native_failures=False):
    if rates!=[192000,384000]:raise ValueError('Required rates are 192000 and 384000')
    if native_solver not in ('norm','alt'):raise ValueError('Invalid native solver')
    if not 0<native_tolerance_scale<=1:raise ValueError('Native tolerances may only be tightened')
    overrides=native_solver_overrides or {}
    if any(s not in ('norm','alt') for s in overrides.values()):raise ValueError('Invalid case solver override')
    from .cli import doctor,make_deck
    if doctor(toolchain_path)['status']!='passed':raise ValueError('Unqualified toolchain')
    cases=load_json(cases_path)['cases'];cfg=load_json(toolchain_path)
    def copy_payload(source,destination):
        if str(source).endswith('.f64le'):
            try:os.link(source,destination);return destination
            except OSError:pass
        return shutil.copy2(source,destination)
    if resume_from is not None:
        resume_from=Path(resume_from)
        if sha256(resume_from/'cases.json')!=sha256(cases_path) or sha256(resume_from/'toolchain.json')!=sha256(toolchain_path):
            raise ValueError('Resume manifest/toolchain differs')
        previous=load_json(resume_from/'summary.json');validate_summary(previous,cases)
        shutil.copytree(resume_from,output,copy_function=copy_payload)
        atomic_json(output/'resume-source.json',dict(directory=str(resume_from),summary_sha256=sha256(resume_from/'summary.json')))
    else:
        output.mkdir(parents=True,exist_ok=False);shutil.copyfile(cases_path,output/'cases.json');shutil.copyfile(toolchain_path,output/'toolchain.json')
    summary=dict(schema_version=1,suite_id=output.name,manifest=file_ref(output,output/'cases.json'),toolchain=file_ref(output,output/'toolchain.json'),rates_Hz=rates,completion='incomplete',entries=[],outcomes={k:'pending' for k in ('reference','numerical','wav','listening','combined')},exit_code=50)
    for c in sorted(cases,key=lambda c:c['case_id']):
        for rate in (rates if c['analysis_kind']=='transient' else (None,)):
            summary['entries'].append(dict(case_id=c['case_id'],physical_case_sha256=c['physical_case_sha256'],rate_Hz=rate,case=None,run=None,nominal=None,refined=None,report=None,status='not_evaluated',exit_code=None,reason='Required work not invoked'))
    if resume_from is not None:
        summary['entries']=copy.deepcopy(previous['entries'])
        for e in summary['entries']:
            if e['report'] is None:
                e.update(status='not_evaluated',exit_code=None,reason='Pending explicit resumed attempt')
    def publish():
        validate_summary(summary,cases);atomic_json(output/'summary.json',summary)
        (output/'summary.md').write_text('# '+summary['suite_id']+'\n\n'+str(summary['outcomes'])+'\n\n'+ '\n'.join(f"- {e['case_id']} / {e['rate_Hz']}: {e['status']} — {e['reason']}" for e in summary['entries'])+'\n')
    publish()
    pilots=load_json(pilots_path)
    if not pilots.get('full_matrix_authorized',False):
        summary.update(completion='failed',exit_code=31)
        for e in summary['entries']:e['reason']='Pilot numerical/reference gates not approved; full matrix blocked';e['exit_code']=50
        measurements=[m for p in pilots.get('pilots',[]) for m in p.get('measurements',[]) if 'outcomes' in m]
        for category in ('reference','numerical','wav'):
            summary['outcomes'][category]=aggregate([m['outcomes'][category] for m in measurements]+['pending'])
        summary['outcomes']['combined']='failed' if any(v=='failed' for v in summary['outcomes'].values()) else 'pending'
        summary['exit_code']=50;publish();return 50
    if any(c['execution'].get('substeps',1)>1 for c in cases):
        verify_substep_pilots(pilots,executable)
    from .resources import estimate
    pending_cases=[c for c in cases if resume_from is None or
                   not all(e['report'] is not None for e in summary['entries'] if e['case_id']==c['case_id'])]
    plan=estimate(pending_cases)
    plan['resumed_physical_cases']=len(cases)-len(pending_cases)
    native_root=Path(cfg['workspace']['wsl_root'])
    free=shutil.disk_usage(native_root).free;output_free=shutil.disk_usage(output).free
    same_volume=native_root.stat().st_dev==output.stat().st_dev
    enough=(free>=plan['estimated_required_bytes']) if same_volume else (free>=plan['native_required_bytes'] and output_free>=plan['output_required_bytes'])
    atomic_json(output/'resource-gate.json',dict(plan,status='passed' if enough else 'failed',native_free_bytes=free,output_free_bytes=output_free,same_volume=same_volume))
    if not enough:
        summary.update(completion='failed',exit_code=50)
        for e in summary['entries']:e['reason']='Insufficient retained native RAW storage for full matrix';e['exit_code']=50
        publish();return 50
    # Physical references are produced once and reused explicitly by both target grids.
    try:
        for case in sorted(cases,key=lambda c:({'dc':0,'ac':1,'transient':2}[c['analysis_kind']],c['case_id'])):
            if case['analysis_kind']=='ac':
                dc_id='dc_'+case['case_id'][3:]
                dc=next((e for e in summary['entries'] if e['case_id']==dc_id),None)
                if dc is None or dc['status']!='passed':
                    entry=next(e for e in summary['entries'] if e['case_id']==case['case_id'])
                    entry.update(exit_code=31,reason='Corresponding loaded DC reference/model comparison is not qualified')
                    publish();continue
            print('Matrix case',case['case_id'],flush=True)
            session=ReferenceSession()
            existing=[e for e in summary['entries'] if e['case_id']==case['case_id']]
            if resume_from is not None and all(e['report'] is not None for e in existing):
                pilot=next((p for p in pilots.get('pilots',[]) if p['case_id']==case['case_id']),None)
                provenance=load_json(Path(pilot['reference_toolchain'])) if pilot else cfg
                for e in existing:
                    for key in ('case','run','nominal','refined','report'):
                        ref=e[key]
                        if sha256(output/ref['path'])!=ref['sha256']:raise ValueError('Changed resumed metadata')
                    report=load_json(output/e['report']['path']);validate_schema('report',report)
                    run=load_json(output/e['run']['path']);validate_schema('run',run)
                    if (report['inputs']['validator_sha256']!=validator_hash() or run['build']['executable_sha256']!=sha256(executable)
                            or report['inputs']['run_sha256']!=e['run']['sha256'] or report['inputs']['case_sha256']!=e['case']['sha256']
                            or report['physical_case_sha256']!=case['physical_case_sha256']
                            or run['physical_case_sha256']!=case['physical_case_sha256']
                            or run['completion']['state']!='completed' or run['trace']['integrity']!='verified'
                            or sha256((output/e['run']['path']).parent/'traces.f64le')!=run['trace']['sha256']):
                        raise ValueError('Changed/stale resumed run or report')
                    for level in ('nominal','refined'):
                        manifest=output/e[level]['path']
                        session.consume(manifest.parent,provenance)
                        if sha256(manifest)!=report['reference_qualification'][level]['manifest_sha256']:
                            raise ValueError('Resumed reference differs from report')
                session.verify();publish();print('Matrix resumed completed case',case['case_id'],flush=True);continue
            if resume_from is not None and (output/case['case_id']).exists():
                (output/case['case_id']).rename(output/(case['case_id']+'-incomplete-preserved-'+uuid.uuid4().hex[:8]))
            physical=output/case['case_id'];physical.mkdir();base=physical/'case.json';atomic_json(base,case);references={}
            reference_cfg=cfg
            reuse=next((p for p in pilots.get('pilots',[]) if p['case_id']==case['case_id'] and p.get('references')),None)
            if reuse:
                reference_cfg=load_json(Path(reuse['reference_toolchain']))
                for level,source in reuse['references'].items():
                    if level not in ('nominal','refined'):raise ValueError('Unexpected pilot reference level')
                    references[level]=physical/level;shutil.copytree(source,references[level])
                if set(references)!={'nominal','refined'}:raise ValueError('Incomplete pilot reference pair')
                # Recheck original bytes in this command, then reuse the exact
                # qualified runs/reports instead of regenerating passed work.
                for path in references.values():session.consume(path,reference_cfg)
                def copy_payload(source,destination):
                    if str(source).endswith('.f64le'):
                        try:
                            os.link(source,destination);return destination
                        except OSError:pass
                    return shutil.copy2(source,destination)
                for measured in reuse['measurements']:
                    rate=measured['rate_Hz'];source_report=Path(measured['comparison_directory'])
                    source_target=source_report.parent;target=physical/str(rate);target.mkdir()
                    shutil.copyfile(source_target/'case.json',target/'case.json')
                    shutil.copytree(source_target/'run',target/'run',copy_function=copy_payload)
                    shutil.copytree(source_report,target/'comparison')
                    report=load_json(target/'comparison/report.json');run=load_json(target/'run/run.json')
                    if (sha256(target/'case.json')!=report['inputs']['case_sha256'] or
                            sha256(target/'run/run.json')!=report['inputs']['run_sha256'] or
                            sha256(target/'run/traces.f64le')!=run['trace']['sha256'] or
                            run['physical_case_sha256']!=case['physical_case_sha256']):
                        raise ValueError('Changed qualified pilot bytes')
                    for level,path in references.items():
                        if sha256(path/'reference.json')!=report['reference_qualification'][level]['manifest_sha256']:
                            raise ValueError('Reused reference differs from qualified pilot')
                    e=next(e for e in summary['entries'] if e['case_id']==case['case_id'] and e['rate_Hz']==rate)
                    e.update(case=file_ref(output,target/'case.json'),run=file_ref(output,target/'run/run.json'),
                             nominal=file_ref(output,references['nominal']/'reference.json'),refined=file_ref(output,references['refined']/'reference.json'),
                             report=file_ref(output,target/'comparison/report.json'),status='passed',exit_code=0,
                             reason='Qualified substep pilot reused after original-byte integrity checks')
                    session.verify();publish()
                    print('Matrix reused pilot',case['case_id'],rate,flush=True)
                continue
            try:
                for refined in (() if reuse else (False,True)):
                    level='refined' if refined else 'nominal'
                    solver=overrides.get(case['case_id'],'alt' if case['case_id'].startswith('overload_') else native_solver)
                    references[level]=produce_native_reference(case,base,physical,level,cfg,solver,
                        tolerance_scale=native_tolerance_scale,solver_fallback=native_solver_fallback,
                        topology_nodeset=native_topology_nodeset)
                    print('Reference',case['case_id'],level,'completed',flush=True)
            except RuntimeError as error:
                if not continue_native_failures:raise
                for entry in existing:
                    entry.update(status='not_evaluated',exit_code=30,
                                 reason='Native producer failed; numerical/WAV gates not evaluated: '+str(error))
                print('Matrix native failure retained; continuing',case['case_id'],str(error),flush=True)
                publish();continue
            for rate in (rates if case['analysis_kind']=='transient' else (192000,)):
                c=copy.deepcopy(case);c['execution']['rate_Hz']=rate
                if 'substeps' in c['execution']:configure_substeps(c,rate)
                if c['analysis_kind']=='transient':c['analysis']['time']['sample_count']=round(c['analysis']['time']['duration_s']*rate)+1
                target=physical/str(rate);target.mkdir();cp=target/'case.json';atomic_json(cp,c)
                e=next(e for e in summary['entries'] if e['case_id']==c['case_id'] and e['rate_Hz']==(rate if c['analysis_kind']=='transient' else None))
                e['case']=file_ref(output,cp)
                for level in references:e[level]=file_ref(output,references[level]/'reference.json')
                p=subprocess.run([str(executable),'--case',str(cp),'--output',str(target/'run')],capture_output=True)
                if p.returncode:e.update(status='failed',exit_code=p.returncode,reason=p.stderr.decode(errors='replace'));publish();continue
                finalize_run(target/'run',cp,executable);e['run']=file_ref(output,target/'run/run.json')
                report=compare(target/'run',references['nominal'],references['refined'],target/'comparison',reference_cfg,reference_session=session)
                if c['analysis_kind']=='ac':
                    secondary=target/'comparison/ac384000';secondary.mkdir();c384=copy.deepcopy(c);c384['execution']['rate_Hz']=384000
                    if 'substeps' in c384['execution']:configure_substeps(c384,384000)
                    atomic_json(secondary/'case.json',c384)
                    completed=subprocess.run([str(executable),'--case',str(secondary/'case.json'),'--output',str(secondary/'run')],capture_output=True)
                    if completed.returncode:
                        from .persist import check
                        report['checks'].append(check('bode_384000',None,.2,'dB',reason=completed.stderr.decode(errors='replace')));report['outcomes']['numerical']='pending'
                    else:
                        finalize_run(secondary/'run',secondary/'case.json',executable)
                        extra=compare(secondary/'run',references['nominal'],references['refined'],secondary/'comparison',reference_cfg,reference_session=session)
                        for check384 in extra['checks']:
                            check384['id']+='-384000';report['checks'].append(check384)
                        report['outcomes']['numerical']=aggregate([report['outcomes']['numerical'],extra['outcomes']['numerical']])
                        report['artifacts'].append(dict(path='ac384000/comparison/report.json',sha256=sha256(secondary/'comparison/report.json'),status='generated',reason='Independent target-rate AC report and finalized run'))
                    report['outcomes']['combined']=aggregate([report['outcomes']['reference'],report['outcomes']['numerical']])
                    publish_report(target/'comparison',report)
                if c['analysis_kind']=='transient' and not c['case_id'].startswith('linear_'):
                    from .audio_qualification import qualify_audio
                    report=qualify_audio(cp,target/'run',references['nominal'],references['refined'],target/'comparison',cfg,reference_config=reference_cfg,reference_session=session)
                e['report']=file_ref(output,target/'comparison/report.json')
                required=[report['outcomes'][k] for k in ('reference','numerical','wav') if report['outcomes'][k]!='not_applicable']
                ok=all(value=='passed' for value in required)
                e.update(status='passed' if ok else 'failed' if 'failed' in required else 'not_evaluated',exit_code=0 if ok else 40 if 'failed' in required else 50,reason='Numerical phase completed; WAV/listening outcomes separate')
                print('Matrix result',case['case_id'],rate,report['outcomes'],flush=True)
                for k,v in report['outcomes'].items():summary['outcomes'][k]=aggregate([summary['outcomes'][k],v])
                publish()
    except (KeyboardInterrupt,Exception) as error:
        summary.update(completion='failed',exit_code=50)
        for e in summary['entries']:
            if e['exit_code'] is None:e.update(exit_code=50,reason='Interrupted/uninvoked: '+str(error))
        summary['exit_code']=next((e['exit_code'] for e in summary['entries'] if e['exit_code']),50)
        publish();raise
    # Cross-case linearity cannot be accepted from an isolated run.
    for condition in ('center','high'):
        for rate in rates:
            targets=[output/f'linear_{condition}_a{a}uv'/str(rate) for a in ('010','020')]
            if all((t/'comparison/report.json').exists() for t in targets):
                from .linearity import qualify_pair
                from .audio_qualification import qualify_audio
                qualify_pair(output,condition,rate,cfg)
                for target in targets:
                    physical=target.parent
                    result=qualify_audio(target/'case.json',target/'run',physical/'nominal',physical/'refined',target/'comparison',cfg)
                    entry=next(e for e in summary['entries'] if e['case_id']==physical.name and e['rate_Hz']==rate)
                    required=[result['outcomes'][k] for k in ('reference','numerical','wav')]
                    entry.update(report=file_ref(output,target/'comparison/report.json'),status='passed' if all(v=='passed' for v in required) else 'failed' if 'failed' in required else 'not_evaluated',exit_code=0 if all(v=='passed' for v in required) else 40 if 'failed' in required else 50)
    reports=[load_json(output/e['report']['path']) for e in summary['entries'] if e['report'] is not None]
    for category in summary['outcomes']:
        summary['outcomes'][category]=aggregate([r['outcomes'][category] for r in reports]+(['pending'] if len(reports)!=len(summary['entries']) else []))
    if all(summary['outcomes'][k]=='passed' for k in ('reference','numerical','wav')):
        from .abx import prepare_session
        primary=output/'listen_high/384000/comparison';session=prepare_session(primary/'report.json',primary/'listening/cpp.wav',primary/'listening/reference.wav',primary/'abx',None,family_id='primary')
        report=load_json(primary/'report.json');report['artifacts'].append(dict(path='abx/blinded/session.json',sha256=sha256(primary/'abx/blinded/session.json'),status='generated',reason='Twenty blinded trials; human responses pending; key stored separately'))
        publish_report(primary,report)
        entry=next(e for e in summary['entries'] if e['case_id']=='listen_high' and e['rate_Hz']==384000);entry['report']=file_ref(output,primary/'report.json')
    summary['completion']='completed' if all(e['status']=='passed' for e in summary['entries']) else 'failed'
    summary['exit_code']=next((e['exit_code'] for e in summary['entries'] if e['exit_code']),0);publish();return summary['exit_code']
