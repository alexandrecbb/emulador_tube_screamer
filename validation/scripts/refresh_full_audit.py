"""Recompute all canonical reports from preserved evidence, then audit coverage."""
import copy
import gc
from pathlib import Path
import shutil
import subprocess
import sys
from ts808_validation.artifacts import ROOT, atomic_json, load_json
from ts808_validation.compare import compare, validator_hash
from ts808_validation.audio_qualification import qualify_audio, requalify_existing_audio
from ts808_validation.persist import ReferenceSession, publish_report
from ts808_validation.simulator import sha256
from ts808_validation.suite import aggregate
from ts808_validation.qualification import consolidate

SOURCE=Path('/mnt/f/ts808-validation/wav-completion-20261108-r4')
OUT=Path('/mnt/f/ts808-validation/full-audit-20261109-r1')
FIX=Path('/mnt/f/ts808-validation/memory-requalification-20261109-r1')
CASE='tone_high_f5000_a500mv-warmup2s'
CFG=load_json(ROOT/'validation/toolchain-pilot-f.json')
CONFIGS=[CFG,load_json(ROOT/'validation/toolchain.json')]

def config_for(report):
    path=Path(report['reference_qualification']['nominal']['manifest_path']['wsl_path'])
    request=Path(load_json(path)['source']['request']['locator']['wsl_path'])
    return next(c for c in CONFIGS if request.is_relative_to(Path(c['workspace']['wsl_root'])))

def refs_for(report):
    return {k:Path(report['reference_qualification'][k]['manifest_path']['wsl_path']).parent for k in ('nominal','refined')}

def refresh(old_path,target,session):
    old=load_json(old_path);origin=old_path.parent.parent
    if sha256(origin/'case.json')!=old['inputs']['case_sha256'] or sha256(origin/'run/run.json')!=old['inputs']['run_sha256']:
        raise ValueError('Changed original case/run metadata')
    target.mkdir(parents=True,exist_ok=False)
    shutil.copy2(origin/'case.json',target/'case.json')
    (target/'run').symlink_to(origin/'run',target_is_directory=True)
    refs=refs_for(old);cfg=config_for(old)
    report=compare(target/'run',refs['nominal'],refs['refined'],target/'comparison',cfg,reference_session=session)
    case=load_json(target/'case.json')
    if case['analysis_kind']=='ac':
        extra=refresh(old_path.parent/'ac384000/comparison/report.json',target/'comparison/ac384000',session) if case['execution']['rate_Hz']==192000 else None
        if extra:
            for check in extra['checks']:
                check=copy.deepcopy(check);check['id']+='-384000';report['checks'].append(check)
            report['outcomes']['numerical']=aggregate([report['outcomes']['numerical'],extra['outcomes']['numerical']])
            report['outcomes']['combined']=aggregate([report['outcomes']['reference'],report['outcomes']['numerical']])
            report['artifacts'].append(dict(path='ac384000/comparison/report.json',sha256=sha256(target/'comparison/ac384000/comparison/report.json'),status='generated',reason='Recomputed independent 384 kHz AC comparison'))
            publish_report(target/'comparison',report)
    elif case['analysis_kind']=='transient' and not case['case_id'].startswith('linear_'):
        if case['case_id']=='listen_high':
            report=qualify_audio(target/'case.json',target/'run',refs['nominal'],refs['refined'],target/'comparison',CFG,reference_config=cfg,reference_session=session)
        else:
            report=requalify_existing_audio(target/'case.json',target/'run',refs['nominal'],refs['refined'],target/'comparison',old_path.parent/'native-wav-source.json',CFG,reference_config=cfg,reference_session=session)
    return report

def main():
    OUT.mkdir(exist_ok=False)
    status=dict(status='refreshing',completed_entries=0,required_entries=128,validator_sha256=validator_hash(),shutdown_authorized=False,mvp_accepted=False)
    atomic_json(OUT/'status.json',status)
    try:
        assessment=load_json(SOURCE/'qualification/qualification.json')
        manifest=load_json(SOURCE/'cases.json');atomic_json(OUT/'cases.json',manifest)
        rows=[]
        for entry in assessment['entries']:
            old=Path(entry['report_path'])
            if sha256(old)!=entry['report_sha256']:raise ValueError('Changed source report')
            rate=entry['rate_Hz'] or 192000
            target=OUT/'reports'/entry['case_id']/str(rate)
            if entry['case_id']==CASE:
                old=FIX/str(rate)/'comparison/report.json'
            session=ReferenceSession()
            report=refresh(old,target,session);session.verify();del session;gc.collect()
            rows.append(dict(case_id=entry['case_id'],physical_case_sha256=entry['physical_case_sha256'],rate_Hz=entry['rate_Hz'],target=str(target)))
            status.update(completed_entries=len(rows),current_case=entry['case_id'],rate_Hz=entry['rate_Hz'])
            atomic_json(OUT/'rows.json',rows);atomic_json(OUT/'status.json',status)
            print('Refreshed',len(rows),entry['case_id'],rate,report['outcomes'],flush=True)
        from ts808_validation.linearity import qualify_pair
        for condition in ('center','high'):
            for rate in (192000,384000):
                for amplitude in ('010','020'):
                    physical=OUT/'reports'/f'linear_{condition}_a{amplitude}uv'
                    refs=refs_for(load_json(physical/str(rate)/'comparison/report.json'))
                    for level,path in refs.items():
                        if not (physical/level).exists():(physical/level).symlink_to(path,target_is_directory=True)
                qualify_pair(OUT/'reports',condition,rate,CFG)
                for amplitude in ('010','020'):
                    physical=OUT/'reports'/f'linear_{condition}_a{amplitude}uv';target=physical/str(rate)
                    entry=next(e for e in assessment['entries'] if e['case_id']==physical.name and e['rate_Hz']==rate)
                    old=Path(entry['report_path']);report=load_json(target/'comparison/report.json');refs=refs_for(report)
                    requalify_existing_audio(target/'case.json',target/'run',refs['nominal'],refs['refined'],target/'comparison',old.parent/'native-wav-source.json',CFG,reference_config=config_for(report))
        # All reports are freshly computed; retain each original native locator.
        for name,selected in [('matrix-alt',[]),('combined-transients',[r for r in rows if r['case_id']!='hold_center'])]:
            directory=OUT/name;directory.mkdir()
            atomic_json(directory/'cases.json',dict(manifest,cases=[c for c in manifest['cases'] if c['case_id'] in {r['case_id'] for r in selected}]))
            shutil.copy2(ROOT/'validation/toolchain-pilot-f.json',directory/'toolchain.json')
            entries=[]
            for row in selected:
                target=Path(row['target']);label=row['case_id']+'-'+str(row['rate_Hz']);(directory/label).symlink_to(target,target_is_directory=True)
                report=load_json(target/'comparison/report.json');refs=refs_for(report)
                e={k:row[k] for k in ('case_id','physical_case_sha256','rate_Hz')}
                for key,path in [('case',target/'case.json'),('run',target/'run/run.json'),('report',target/'comparison/report.json')]:
                    relative=label+'/'+str(path.relative_to(target));e[key]=dict(path=relative,sha256=sha256(path))
                for key in ('nominal','refined'):
                    link=directory/(label+'-'+key);link.symlink_to(refs[key],target_is_directory=True)
                    e[key]=dict(path=link.name+'/reference.json',sha256=sha256(refs[key]/'reference.json'))
                values=[report['outcomes'][k] for k in ('reference','numerical','wav') if report['outcomes'][k]!='not_applicable']
                ok=all(v=='passed' for v in values)
                e.update(status='passed' if ok else 'failed',exit_code=0 if ok else 40,reason='Recomputed from preserved original evidence')
                entries.append(e)
            atomic_json(directory/'summary.json',dict(schema_version=1,suite_id=name,manifest=dict(path='cases.json',sha256=sha256(directory/'cases.json')),toolchain=dict(path='toolchain.json',sha256=sha256(directory/'toolchain.json')),rates_Hz=[192000,384000],completion='completed',entries=entries,outcomes={k:aggregate([load_json(Path(r['target'])/'comparison/report.json')['outcomes'][k] for r in selected]) for k in ('reference','numerical','wav','listening','combined')},exit_code=0))
        hold=OUT/'hold-diagnosis-20261104/norm';hold.mkdir(parents=True)
        for rate in (192000,384000):(hold/str(rate)).symlink_to(OUT/'reports/hold_center'/str(rate),target_is_directory=True)
        status['status']='auditing';atomic_json(OUT/'status.json',status)
        result=consolidate(OUT,OUT/'qualification',OUT/'combined-transients/summary.json',require_passed=False)
        status.update(status='completed',automatic_qualification=result['automatic_qualification'],failed_entry_count=result['failed_entry_count'],entry_count=result['entry_count'])
    except BaseException as error:
        status.update(status='interrupted',reason=str(error));raise
    finally:
        atomic_json(OUT/'status.json',status)
        snapshot=ROOT/'validation/results/full-audit-2026-11-09-r1';snapshot.mkdir(exist_ok=True)
        shutil.copy2(OUT/'status.json',snapshot/'status.json')
        if (OUT/'qualification').exists():shutil.copytree(OUT/'qualification',snapshot/'qualification',dirs_exist_ok=True)
        handoff=ROOT/'SESSION_HANDOFF.md'
        handoff.write_text('## ATUALIZAÇÃO DOS RELATÓRIOS E AUDITORIA128 — 2026-11-09\n\n'+str(status)+'\n\nEvidências '+str(OUT)+'.\nDesligamento revogado; ABX/MVP separados. Histórico abaixo.\n\n'+handoff.read_text())

if __name__=='__main__':main()
