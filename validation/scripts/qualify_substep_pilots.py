"""Requalify the approved substep execution, retaining every new payload on F:."""
import copy
import shutil
import subprocess
import time
from pathlib import Path

from ts808_validation.artifacts import ROOT, atomic_json, configure_substeps, finalize_run, load_json
from ts808_validation.audio_qualification import qualify_audio
from ts808_validation.cli import doctor
from ts808_validation.compare import compare, validator_hash
from ts808_validation.simulator import sha256
from ts808_validation.persist import ReferenceSession

OUTPUT=Path('/mnt/f/ts808-validation/substeps-20261104')
EXECUTABLE=ROOT/'build/offline-release/ts808_offline'
TOOLCHAIN=ROOT/'validation/toolchain-pilot-f.json'


def main():
    cfg=load_json(TOOLCHAIN)
    if doctor(TOOLCHAIN)['status']!='passed':
        raise ValueError('F: qualification failed')
    OUTPUT.mkdir(parents=True,exist_ok=True)
    catalog=load_json(ROOT/'reference/ts808/cases.json')
    revisions=load_json(ROOT/'reference/ts808/case_revisions.json')['revisions']
    replacements={r['base_case_id']:r['case'] for r in revisions}
    catalog['cases']=[configure_substeps(copy.deepcopy(replacements.get(c['case_id'],c)),192000) for c in catalog['cases']]
    atomic_json(OUTPUT/'cases.json',catalog)
    jobs=[(r['case'],ROOT/'runs/mvp-revised-pilots-norm'/r['case']['case_id'],'nominal','refined',ROOT/'validation/toolchain.json') for r in revisions]
    overload=next(c for c in catalog['cases'] if c['case_id']=='overload_high')
    jobs.append((overload,ROOT/'runs/mvp-pilots-02/overload_high','nominal-alt-guard','refined-alt-guard',TOOLCHAIN))
    summary=dict(pilots=[],full_matrix_authorized=False,integration_rate_Hz=768000,
                 executable_sha256=sha256(EXECUTABLE),validator_sha256=validator_hash())
    atomic_json(OUTPUT/'pilots.json',summary)
    for base,source,nominal,refined,provenance_path in jobs:
        session=ReferenceSession()
        physical=OUTPUT/base['case_id'];physical.mkdir(exist_ok=True)
        refs={}
        for level,folder in [('nominal',nominal),('refined',refined)]:
            target=physical/level
            if not target.exists():shutil.copytree(source/folder,target)
            refs[level]=target
        provenance=load_json(provenance_path)
        row=dict(case_id=base['case_id'],references={k:str(v) for k,v in refs.items()},
                 reference_toolchain=str(provenance_path),measurements=[])
        summary['pilots'].append(row)
        atomic_json(OUTPUT/'pilots.json',summary)
        for rate in (192000,384000):
            case=configure_substeps(copy.deepcopy(base),rate)
            case['execution']['purpose']='target'
            target=physical/str(rate);target.mkdir(exist_ok=True)
            cp=target/'case.json'
            if cp.exists() and load_json(cp)!=case:raise ValueError('Existing case changed')
            atomic_json(cp,case)
            started=time.monotonic()
            if not (target/'run').exists():
                result=subprocess.run([str(EXECUTABLE),'--case',str(cp),'--output',str(target/'run')],capture_output=True)
                atomic_json(target/'execution.json',dict(elapsed_s=time.monotonic()-started,exit_code=result.returncode,stderr=result.stderr.decode()))
                if result.returncode:raise RuntimeError(result.stderr.decode())
            run=load_json(target/'run/run.json')
            if run['trace']['integrity']=='verified' and run['build']['executable_sha256']!=summary['executable_sha256']:
                raise ValueError('Existing pilot used another executable')
            finalize_run(target/'run',cp,EXECUTABLE)
            print('C++ completed',base['case_id'],rate,flush=True)
            report_dir=target/('comparison-'+validator_hash()[:10])
            report=load_json(report_dir/'report.json') if (report_dir/'report.json').exists() else compare(target/'run',refs['nominal'],refs['refined'],report_dir,provenance,reference_session=session)
            print('Numerical',base['case_id'],rate,report['outcomes'],flush=True)
            if report['outcomes']['wav']!='passed':
                report=qualify_audio(cp,target/'run',refs['nominal'],refs['refined'],report_dir,cfg,reference_config=provenance,reference_session=session)
            row['measurements'].append(dict(rate_Hz=rate,integration_rate_Hz=768000,
                                            comparison_directory=str(report_dir),report_sha256=sha256(report_dir/'report.json'),
                                            outcomes=report['outcomes']))
            atomic_json(OUTPUT/'pilots.json',summary)
            print('Pilot',base['case_id'],rate,report['outcomes'],flush=True)
    summary['full_matrix_authorized']=len(summary['pilots'])==3 and all(
        len(p['measurements'])==2 and all(m['outcomes'][k]=='passed' for m in p['measurements'] for k in ('reference','numerical','wav'))
        for p in summary['pilots'])
    atomic_json(OUTPUT/'pilots.json',summary)
    return 0 if summary['full_matrix_authorized'] else 40


if __name__=='__main__':
    raise SystemExit(main())
