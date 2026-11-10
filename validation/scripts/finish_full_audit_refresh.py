"""Snapshot the completed audit and bind pilot records to recomputed reports."""
from pathlib import Path
import shutil
import subprocess
import time
from ts808_validation.artifacts import ROOT, atomic_json, load_json
from ts808_validation.compare import validator_hash
from ts808_validation.simulator import sha256
from ts808_validation.suite import verify_substep_pilots

OUT=Path('/mnt/f/ts808-validation/full-audit-20261109-r1')
SNAPSHOT=ROOT/'validation/results/full-audit-2026-11-09-r1'

def main():
    while True:
        state=subprocess.run(['systemctl','--user','show','ts808-full-audit-20261109-r1.service','--property=ActiveState','--value'],capture_output=True,text=True,check=True).stdout.strip()
        if state not in ('active','activating'):break
        time.sleep(30)
    status=load_json(OUT/'status.json')
    SNAPSHOT.mkdir(exist_ok=True)
    if status['status']!='completed':
        atomic_json(SNAPSHOT/'finalization.json',dict(status='blocked_by_incomplete_audit',executor=status));return
    result=load_json(OUT/'qualification/qualification.json')
    if result['validator_sha256']!=validator_hash() or result['entry_count']!=128 or result['assessment_completion']!='completed':
        raise ValueError('Incomplete/stale final assessment')
    pilots=load_json(Path('/mnt/f/ts808-validation/substeps-20261104/pilots.json'))
    for pilot in pilots['pilots']:
        references=[]
        for measurement in pilot['measurements']:
            path=OUT/'reports'/pilot['case_id']/str(measurement['rate_Hz'])/'comparison/report.json'
            report=load_json(path)
            measurement.update(comparison_directory=str(path.parent),report_sha256=sha256(path),outcomes=report['outcomes'])
            references.append({k:str(Path(report['reference_qualification'][k]['manifest_path']['wsl_path']).parent) for k in ('nominal','refined')})
        if references[0]!=references[1]:raise ValueError('Pilot target rates use different physical references')
        pilot['references']=references[0]
    pilots['validator_sha256']=validator_hash()
    pilots['full_matrix_authorized']=all(m['outcomes'][k]=='passed' for p in pilots['pilots'] for m in p['measurements'] for k in ('reference','numerical','wav'))
    verify_substep_pilots(pilots,ROOT/'build/offline-release/ts808_offline')
    atomic_json(OUT/'pilots.json',pilots)
    for name in ('status.json','pilots.json','cases.json'):
        shutil.copy2(OUT/name,SNAPSHOT/name)
    for entry in result['entries']:
        target=SNAPSHOT/'reports'/entry['case_id']/str(entry['rate_Hz'] or 192000);target.mkdir(parents=True,exist_ok=True)
        shutil.copy2(Path(entry['report_path']),target/'report.json')
    shutil.copytree(OUT/'qualification',SNAPSHOT/'qualification',dirs_exist_ok=True)
    atomic_json(SNAPSHOT/'finalization.json',dict(status='completed',entry_count=result['entry_count'],automatic_qualification=result['automatic_qualification'],failed_entry_count=result['failed_entry_count'],pilots_verified=True,shutdown_authorized=False,mvp_accepted=False))
    p=ROOT/'SESSION_HANDOFF.md'
    p.write_text('## AUDITORIA128 CONCLUÍDA E PILOTOS ATUALIZADOS — 2026-11-09\n\n'+str(dict(automatic_qualification=result['automatic_qualification'],entries=result['entry_count'],failed=result['failed_entry_count'],verified_files=result['verified_file_count']))+'\n\nValidador '+validator_hash()+'. Evidências '+str(OUT)+'.\nSnapshot '+str(SNAPSHOT)+'. Referências originais preservadas.\nABX humano e aceitação MVP permanecem separados; desligamento revogado.\nHistórico abaixo.\n\n'+p.read_text())

if __name__=='__main__':main()
