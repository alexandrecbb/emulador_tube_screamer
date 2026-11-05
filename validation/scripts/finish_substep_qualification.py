"""Merge completed refinement evidence and conditionally execute the matrix."""
import argparse
import time
from pathlib import Path

from ts808_validation.artifacts import ROOT,atomic_json,load_json
from ts808_validation.persist import validate_schema
from ts808_validation.simulator import sha256
from ts808_validation.suite import suite


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wait-for-pids',type=int,nargs='+',default=[])
    args=parser.parse_args()
    for pid in args.wait_for_pids:
        cmdline=Path(f'/proc/{pid}/cmdline')
        while cmdline.exists():
            try:
                if b'refine_substep_pilot_reference.py' not in cmdline.read_bytes():break
            except FileNotFoundError:break
            time.sleep(1)
    root=Path('/mnt/f/ts808-validation/substeps-20261104')
    summary=load_json(root/'pilots.json')
    atomic_json(root/'pilots-before-refinement-merge.json',summary)
    for case_id,suffix in [('tone_high_f1000_a500mv-warmup2s','-alt'),('overload_high','')]:
        physical=root/case_id
        reference=physical/('reference-tol100'+suffix)
        measurements=[]
        for rate in (192000,384000):
            directory=physical/str(rate)/('comparison-'+summary['validator_sha256'][:10]+'-tol100'+suffix)
            report=load_json(directory/'report.json');validate_schema('report',report)
            if not (directory/'native-wav-source.json').exists():
                raise ValueError('Refinement did not produce complete WAV evidence')
            measurements.append(dict(rate_Hz=rate,integration_rate_Hz=768000,comparison_directory=str(directory),report_sha256=sha256(directory/'report.json'),outcomes=report['outcomes']))
        row=next(p for p in summary['pilots'] if p['case_id']==case_id)
        row.update(references={level:str(reference/level) for level in ('nominal','refined')},reference_toolchain=str(ROOT/'validation/toolchain-pilot-f.json'),measurements=measurements)
    summary['full_matrix_authorized']=len(summary['pilots'])==3 and all(len(p['measurements'])==2 and all(m['outcomes'][k]=='passed' for m in p['measurements'] for k in ('reference','numerical','wav')) for p in summary['pilots'])
    atomic_json(root/'pilots.json',summary)
    if not summary['full_matrix_authorized']:
        print('Matrix remains blocked by measured pilot reference/numerical/WAV outcomes',flush=True)
        return 40
    return suite(root/'cases.json',ROOT/'validation/toolchain-pilot-f.json',ROOT/'build/offline-release/ts808_offline',[192000,384000],root/'matrix',root/'pilots.json')


if __name__=='__main__':
    raise SystemExit(main())
