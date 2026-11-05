"""Estimate retained reference, export and model payloads on the qualified F: root."""
import argparse
import shutil
from datetime import datetime, timezone
from pathlib import Path

from ts808_validation.artifacts import ROOT, atomic_json, load_json


from ts808_validation.resources import estimate


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args=parser.parse_args()
    if args.output.exists():
        raise ValueError('Storage plan destination must be new')
    cfg=load_json(ROOT/'validation/toolchain-pilot-f.json')
    native_root=Path(cfg['workspace']['wsl_root'])
    if not native_root.resolve().is_relative_to(Path('/mnt/f')):
        raise ValueError('Expected qualified F: native workspace')
    cases=load_json(ROOT/'reference/ts808/cases.json')['cases']
    revisions=load_json(ROOT/'reference/ts808/case_revisions.json')['revisions']
    replacements={r['base_case_id']:r['case'] for r in revisions}
    active=[replacements.get(c['case_id'],c) for c in cases]
    pilots=load_json(ROOT/'validation/results/mvp-2026-11-04/pilots.json')['pilots']
    ratios=[]
    for pilot in pilots:
        reference=[m for m in pilot['measurements'] if 'level' in m]
        if len(reference)!=2:
            continue
        duration=next(c for c in active if c['case_id']==pilot['case_id'])['analysis']['time']['duration_s']
        ratios.append(sum(m['bytes'] for m in reference)/(duration*384000*8*256*3))
    factor=max([1.0,*ratios])
    free=shutil.disk_usage(native_root).free
    scenarios={}
    for name, catalog in [('original',cases),('two_explicit_revisions',active)]:
        plan=estimate(catalog,factor)
        plan['storage_gate']='passed' if plan['estimated_required_bytes']<=free else 'failed'
        scenarios[name]=plan
    all_tones=[dict(c,analysis=dict(c['analysis'],time=dict(c['analysis']['time'],duration_s=2.5)))
               if c['case_id'].startswith('tone_') else c for c in active]
    plan=estimate(all_tones,factor)
    plan['storage_gate']='passed' if plan['estimated_required_bytes']<=free else 'failed'
    scenarios['all_tones_warmup2s_hypothesis']=plan
    atomic_json(args.output,dict(recorded_at_utc=datetime.now(timezone.utc).isoformat(),
                                native_root=str(native_root), output_root='/mnt/f/ts808-validation',
                                free_bytes=free, scenarios=scenarios,
                                scope='Planning only; no pilot or case acceptance. Assumes all new payloads on F:. Adaptive growth can exceed pilot observations.'))
    print(scenarios,flush=True)


if __name__=='__main__':
    main()
