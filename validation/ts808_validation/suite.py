"""Canonical suite index; fail closed before the matrix if pilots/resources fail."""
import copy,shutil,subprocess,time,uuid
from pathlib import Path
from .artifacts import ROOT,load_json,atomic_json,finalize_run
from .simulator import sha256,prepare_request,run_request
from .persist import import_reference,validate_schema,publish_report
from .compare import compare


def file_ref(root,path):return dict(path=str(path.relative_to(root)),sha256=sha256(path))


def aggregate(values):
    if 'failed' in values:return 'failed'
    if 'pending' in values:return 'pending'
    return 'passed' if 'passed' in values else 'not_applicable'


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


def suite(cases_path,toolchain_path,executable,rates,output,pilots_path):
    if rates!=[192000,384000]:raise ValueError('Required rates are 192000 and 384000')
    from .cli import doctor,make_deck
    if doctor(toolchain_path)['status']!='passed':raise ValueError('Unqualified toolchain')
    cases=load_json(cases_path)['cases'];cfg=load_json(toolchain_path)
    output.mkdir(parents=True,exist_ok=False);shutil.copyfile(cases_path,output/'cases.json');shutil.copyfile(toolchain_path,output/'toolchain.json')
    summary=dict(schema_version=1,suite_id=output.name,manifest=file_ref(output,output/'cases.json'),toolchain=file_ref(output,output/'toolchain.json'),rates_Hz=rates,completion='incomplete',entries=[],outcomes={k:'pending' for k in ('reference','numerical','wav','listening','combined')},exit_code=50)
    for c in sorted(cases,key=lambda c:c['case_id']):
        for rate in (rates if c['analysis_kind']=='transient' else (None,)):
            summary['entries'].append(dict(case_id=c['case_id'],physical_case_sha256=c['physical_case_sha256'],rate_Hz=rate,case=None,run=None,nominal=None,refined=None,report=None,status='not_evaluated',exit_code=None,reason='Required work not invoked'))
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
    minimum_bytes=sum(c['analysis']['time']['duration_s'] for c in cases if c['analysis_kind']=='transient')*384000*8*256*3
    free=shutil.disk_usage(cfg['workspace']['wsl_root']).free
    if free<minimum_bytes*1.1:
        atomic_json(output/'resource-gate.json',dict(status='failed',free_bytes=free,minimum_reference_bytes=minimum_bytes,required_headroom_factor=1.1))
        summary.update(completion='failed',exit_code=50)
        for e in summary['entries']:e['reason']='Insufficient retained native RAW storage for full matrix';e['exit_code']=50
        publish();return 50
    # Physical references are produced once and reused explicitly by both target grids.
    try:
        for case in sorted(cases,key=lambda c:c['case_id']):
            physical=output/case['case_id'];physical.mkdir();base=physical/'case.json';atomic_json(base,case);references={}
            for refined in (False,True):
                level='refined' if refined else 'nominal';dest=Path(cfg['workspace']['wsl_root'])/(case['case_id']+'-'+level+'-'+uuid.uuid4().hex)
                prepare_request(ROOT/'reference/ts808',base,dest,request_id=dest.name,settings=dict(level=level,maxstep_s=1/(384000*8*(2 if refined else 1)),dc_protocol='gminsteps=0 srcsteps=0; pseudo-transient audited'),deck=make_deck(case,refined))
                atomic_json(physical/(level+'-request.json'),dict(directory=str(dest),request_sha256=sha256(dest/'request.json')))
                run_request(dest,Path(cfg['tools']['ltspice']['path']));references[level]=physical/level;import_reference(dest,references[level],cfg)
            for rate in (rates if case['analysis_kind']=='transient' else (192000,)):
                c=copy.deepcopy(case);c['execution']['rate_Hz']=rate
                if c['analysis_kind']=='transient':c['analysis']['time']['sample_count']=round(c['analysis']['time']['duration_s']*rate)+1
                target=physical/str(rate);target.mkdir();cp=target/'case.json';atomic_json(cp,c)
                e=next(e for e in summary['entries'] if e['case_id']==c['case_id'] and e['rate_Hz']==(rate if c['analysis_kind']=='transient' else None))
                e['case']=file_ref(output,cp)
                for level in references:e[level]=file_ref(output,references[level]/'reference.json')
                p=subprocess.run([str(executable),'--case',str(cp),'--output',str(target/'run')],capture_output=True)
                if p.returncode:e.update(status='failed',exit_code=p.returncode,reason=p.stderr.decode(errors='replace'));publish();continue
                finalize_run(target/'run',cp,executable);e['run']=file_ref(output,target/'run/run.json')
                report=compare(target/'run',references['nominal'],references['refined'],target/'comparison',cfg)
                if c['analysis_kind']=='ac':
                    secondary=target/'comparison/ac384000';secondary.mkdir();c384=copy.deepcopy(c);c384['execution']['rate_Hz']=384000;atomic_json(secondary/'case.json',c384)
                    completed=subprocess.run([str(executable),'--case',str(secondary/'case.json'),'--output',str(secondary/'run')],capture_output=True)
                    if completed.returncode:
                        from .persist import check
                        report['checks'].append(check('bode_384000',None,.2,'dB',reason=completed.stderr.decode(errors='replace')));report['outcomes']['numerical']='pending'
                    else:
                        finalize_run(secondary/'run',secondary/'case.json',executable)
                        extra=compare(secondary/'run',references['nominal'],references['refined'],secondary/'comparison',cfg)
                        for check384 in extra['checks']:
                            check384['id']+='-384000';report['checks'].append(check384)
                        report['outcomes']['numerical']=aggregate([report['outcomes']['numerical'],extra['outcomes']['numerical']])
                        report['artifacts'].append(dict(path='ac384000/comparison/report.json',sha256=sha256(secondary/'comparison/report.json'),status='generated',reason='Independent target-rate AC report and finalized run'))
                    publish_report(target/'comparison',report)
                if c['analysis_kind']=='transient' and not c['case_id'].startswith('linear_'):
                    from .audio_qualification import qualify_audio
                    report=qualify_audio(cp,target/'run',references['nominal'],references['refined'],target/'comparison',cfg)
                e['report']=file_ref(output,target/'comparison/report.json')
                required=[report['outcomes'][k] for k in ('reference','numerical','wav') if report['outcomes'][k]!='not_applicable']
                ok=all(value=='passed' for value in required)
                e.update(status='passed' if ok else 'failed' if 'failed' in required else 'not_evaluated',exit_code=0 if ok else 40 if 'failed' in required else 50,reason='Numerical phase completed; WAV/listening outcomes separate')
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
