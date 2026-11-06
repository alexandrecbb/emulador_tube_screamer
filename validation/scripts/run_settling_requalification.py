"""Run the explicitly revised cases, then audit them with unchanged original passes."""
import argparse
import copy
import os
from pathlib import Path
import shutil

from ts808_validation.artifacts import ROOT, atomic_json, load_json, validate_case
from ts808_validation.qualification import consolidate
from ts808_validation.resources import estimate
from ts808_validation.simulator import sha256
from ts808_validation.suite import aggregate, suite, validate_summary


def merge_transients(old_matrix, revised_matrix, destination, complete_manifest):
    """Reference original directories via links; never rewrite or duplicate payloads."""
    destination.mkdir(parents=True, exist_ok=False)
    replacements = {c['case_id'].removesuffix('-warmup2s') for c in load_json(revised_matrix/'cases.json')['cases']}
    merged = copy.deepcopy(load_json(old_matrix/'summary.json'))
    rows = []
    for label, matrix in [('original', old_matrix), ('revised', revised_matrix)]:
        (destination/label).symlink_to(matrix.resolve(),target_is_directory=True)
        for row in load_json(matrix/'summary.json')['entries']:
            if label == 'original' and row['case_id'] in replacements:
                continue
            row = copy.deepcopy(row)
            for key in ('case','run','nominal','refined','report'):
                if row[key] is not None:
                    row[key]['path'] = label + '/' + row[key]['path']
            rows.append(row)
    merged.update(suite_id='settling-requalification-merged',entries=rows)
    manifest = load_json(complete_manifest)
    expected_ids = {e['case_id'] for e in rows}
    manifest['cases'] = [c for c in manifest['cases'] if c['case_id'] in expected_ids]
    atomic_json(destination/'cases.json',manifest)
    shutil.copyfile(revised_matrix/'toolchain.json',destination/'toolchain.json')
    for key in ('manifest','toolchain'):
        filename = 'cases.json' if key=='manifest' else 'toolchain.json'
        merged[key] = dict(path=filename,sha256=sha256(destination/filename))
    merged['outcomes'] = {key:aggregate([load_json(destination/r['report']['path'])['outcomes'][key]
                                       if r['report'] else 'pending' for r in rows])
                          for key in merged['outcomes']}
    merged['completion'] = 'completed' if all(r['report'] for r in rows) else 'incomplete'
    merged['exit_code'] = 40 if 'failed' in merged['outcomes'].values() else 50 if 'pending' in merged['outcomes'].values() else 0
    validate_summary(merged,manifest['cases'])
    atomic_json(destination/'summary.json',merged)
    return destination/'summary.json'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepared',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--resume-from',type=Path)
    args = parser.parse_args()
    if args.output.exists() or not args.output.resolve().is_relative_to(Path('/mnt/f/ts808-validation')):
        raise ValueError('Use a new output directory on F:')
    plan = load_json(args.prepared/'plan.json')
    if sha256(Path(plan['source_assessment'])) != plan['source_sha256']:
        raise ValueError('Source assessment changed')
    cases = load_json(args.prepared/'cases.json')['cases']
    for case in cases:
        validate_case(case)
    pending=cases
    if args.resume_from is not None:
        previous=load_json(args.resume_from/'revised-matrix/summary.json')
        pending=[c for c in cases if not all(e['report'] is not None for e in previous['entries'] if e['case_id']==c['case_id'])]
    budget = estimate(pending,plan['measured_growth_plan']['adaptive_factor'])
    free = shutil.disk_usage('/mnt/f').free
    if free < budget['estimated_required_bytes']:
        raise RuntimeError(f"F: storage gate blocked: need {budget['estimated_required_bytes']} bytes free, have {free}; no native producer started")
    old_root = Path('/mnt/f/ts808-validation/substeps-20261104')
    old_assessment = load_json(Path(plan['source_assessment']))
    old_partition = next(Path(e['partition']).parent for e in old_assessment['entries']
                         if e['case_id']==cases[0]['case_id'].removesuffix('-warmup2s'))
    args.output.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(args.prepared/'complete-cases.json',args.output/'cases.json')
    for name in ('matrix-alt','hold-diagnosis-20261104'):
        (args.output/name).symlink_to(old_root/name,target_is_directory=True)
    status = dict(status='running',pid=os.getpid(),automatic_qualification='pending',mvp_accepted=False)
    atomic_json(args.output/'status.json',status)
    try:
        code = suite(args.prepared/'cases.json', ROOT/'validation/toolchain-pilot-f.json',
                     ROOT/'build/offline-release/ts808_offline',[192000,384000],
                     args.output/'revised-matrix',old_root/'pilots.json',native_solver='alt',
                     resume_from=args.resume_from/'revised-matrix' if args.resume_from else None,
                     native_solver_overrides={'tone_edge_t000_f5000_a100mv-warmup2s':'norm'},
                     native_topology_nodeset=True,continue_native_failures=True)
        if code not in (0,40):
            raise RuntimeError(f'Revised matrix incomplete: exit {code}')
        summary = merge_transients(old_partition,args.output/'revised-matrix',
                                   args.output/'combined-transients',args.output/'cases.json')
        result = consolidate(args.output,args.output/'qualification',summary,require_passed=False)
        status.update(status='completed',automatic_qualification=result['automatic_qualification'],
                      assessment_completion=result['assessment_completion'])
    except BaseException as error:
        status.update(status='interrupted' if isinstance(error,KeyboardInterrupt) else 'failed',reason=str(error))
        raise
    finally:
        atomic_json(args.output/'status.json',status)


if __name__ == '__main__':
    main()
