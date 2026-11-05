"""Refine native algebraic tolerances without changing physical cases or gates."""
import argparse
import re
import time
import uuid
import fcntl
from pathlib import Path

from ts808_validation.artifacts import ROOT,atomic_json,load_json
from ts808_validation.audio_qualification import qualify_audio
from ts808_validation.cli import make_deck
from ts808_validation.compare import compare,validator_hash
from ts808_validation.persist import import_reference,ReferenceSession
from ts808_validation.simulator import native_options,prepare_request,run_request,sha256


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case-id',required=True)
    parser.add_argument('--factor',type=int,default=100)
    parser.add_argument('--solver',choices=('norm','alt'))
    parser.add_argument('--wait-for-pilot-pid',type=int)
    args=parser.parse_args()
    if args.factor<10:raise ValueError('Refinement must tighten tolerances')
    root=Path('/mnt/f/ts808-validation/substeps-20261104')
    physical=root/args.case_id
    case_path=physical/'192000/case.json';case=load_json(case_path)
    cfg_path=ROOT/'validation/toolchain-pilot-f.json';cfg=load_json(cfg_path)
    suffix=f'-{args.solver}' if args.solver else ''
    refinement=physical/(f'reference-tol{args.factor}'+suffix)
    refinement.mkdir(exist_ok=True)
    refs={}
    for refined in (False,True):
        level='refined' if refined else 'nominal';pointer=refinement/(level+'-request.json')
        if pointer.exists():
            dest=Path(load_json(pointer)['directory'])
        else:
            deck=make_deck(case,refined)
            solver=args.solver or ('alt' if args.case_id.startswith('overload_') else 'norm')
            deck=deck.replace('.temp 25','.temp 25\n.options solver='+solver)
            options=native_options(deck)
            for key in ('reltol','abstol','vntol','chgtol'):
                value=float(options[key])/args.factor
                deck=re.sub(r'\b'+key+r'=[^\s]+',key+'='+format(value,'.17g'),deck)
            dest=Path(cfg['workspace']['wsl_root'])/(args.case_id+'-'+level+f'-tol{args.factor}'+suffix+'-'+uuid.uuid4().hex)
            prepare_request(ROOT/'reference/ts808',case_path,dest,request_id=dest.name,
                            settings=dict(level=level,maxstep_s=1/(384000*8*(2 if refined else 1)),
                                          dc_protocol='Native tolerance refinement; original physical case retained'),deck=deck)
            atomic_json(pointer,dict(directory=str(dest)))
        if not (dest/'reference_result.json').exists():run_request(dest,Path(cfg['tools']['ltspice']['path']))
        refs[level]=refinement/level
        if not refs[level].exists():import_reference(dest,refs[level],cfg)
        print('Tighter reference',args.case_id,level,'completed',flush=True)
    if args.wait_for_pilot_pid:
        cmdline=Path(f'/proc/{args.wait_for_pilot_pid}/cmdline')
        while cmdline.exists():
            try:
                if b'qualify_substep_pilots.py' not in cmdline.read_bytes():break
            except FileNotFoundError:break
            time.sleep(1)
    summary=load_json(root/'pilots.json')
    row=next(p for p in summary['pilots'] if p['case_id']==args.case_id)
    original=dict(row)
    atomic_json(refinement/'previous-pilot.json',original)
    session=ReferenceSession();measurements=[]
    for rate in (192000,384000):
        target=physical/str(rate);report_dir=target/(f'comparison-{validator_hash()[:10]}-tol{args.factor}'+suffix)
        report=load_json(report_dir/'report.json') if (report_dir/'report.json').exists() else compare(target/'run',refs['nominal'],refs['refined'],report_dir,cfg,reference_session=session)
        if report['outcomes']['wav']!='passed':
            report=qualify_audio(target/'case.json',target/'run',refs['nominal'],refs['refined'],report_dir,cfg,reference_session=session)
        measurements.append(dict(rate_Hz=rate,integration_rate_Hz=768000,comparison_directory=str(report_dir),report_sha256=sha256(report_dir/'report.json'),outcomes=report['outcomes']))
        print('Tighter pilot',args.case_id,rate,report['outcomes'],flush=True)
    update=dict(references={k:str(v) for k,v in refs.items()},reference_toolchain=str(cfg_path),measurements=measurements)
    atomic_json(refinement/'qualified-pilot.json',dict(case_id=args.case_id,**update))
    with (root/'pilot-update.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        summary=load_json(root/'pilots.json')
        row=next(p for p in summary['pilots'] if p['case_id']==args.case_id)
        row.update(update)
        summary['full_matrix_authorized']=len(summary['pilots'])==3 and all(len(p['measurements'])==2 and all(m['outcomes'][k]=='passed' for m in p['measurements'] for k in ('reference','numerical','wav')) for p in summary['pilots'])
        atomic_json(root/'pilots.json',summary)
    return 0 if all(m['outcomes'][k]=='passed' for m in measurements for k in ('reference','numerical','wav')) else 40


if __name__=='__main__':
    raise SystemExit(main())
