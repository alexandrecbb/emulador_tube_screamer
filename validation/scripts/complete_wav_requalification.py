"""Run the remaining WAV remedies in isolated processes, then audit all 128 entries."""
import argparse
import copy
from pathlib import Path
import shutil
import subprocess
import sys

from requalify_wav_references import PILOT, rejected_cases
from ts808_validation.artifacts import ROOT, atomic_json, load_json
from ts808_validation.qualification import consolidate
from ts808_validation.resources import estimate
from ts808_validation.simulator import sha256
from ts808_validation.suite import aggregate, suite, validate_summary

SLOW_CASE = 'tone_edge_t000_f5000_a100mv-warmup2s'

def execution_order(cases, isolate_slow):
    return sorted(cases, key=lambda c: c['case_id'] == SLOW_CASE) if isolate_slow else cases



def measured_native_growth(matrix):
    cases = load_json(matrix/'cases.json')['cases']
    directories = set()
    for case in cases:
        for level in ('nominal', 'refined'):
            manifest = load_json(matrix/case['case_id']/level/'reference.json')
            directories.add(Path(manifest['source']['request']['locator']['wsl_path']).parent)
    for source in matrix.rglob('native-wav-source.json'):
        manifest = load_json(source)
        directories.add(Path(manifest['files']['audio.wav']['locator']['wsl_path']).parent)
    retained = sum(p.stat().st_size for d in directories for p in d.rglob('*') if p.is_file())
    baseline = estimate(cases, 1)
    factor = max(1.3891729125976562, (retained-baseline['pcm_payload_bytes']) /
                 (baseline['minimum_numerical_reference_bytes']+baseline['minimum_export_raw_bytes']))
    return dict(retained_native_bytes=retained, adaptive_factor=factor,
                original_directories=sorted(str(d) for d in directories))


def merge_matrices(original, replacements, destination, manifest):
    """Replace exact physical IDs, retaining original payload locations via links."""
    replacement_ids = set()
    for matrix in replacements:
        ids = {c['case_id'] for c in load_json(matrix/'cases.json')['cases']}
        if replacement_ids & ids:
            raise ValueError('Overlapping replacement cases')
        replacement_ids.update(ids)
    merged = copy.deepcopy(load_json(original/'summary.json'))
    original_ids = {e['case_id'] for e in merged['entries']}
    if not replacement_ids <= original_ids:
        raise ValueError('Replacement includes unknown physical cases')
    destination.mkdir(exist_ok=False)
    rows = []
    for index, matrix in enumerate([original, *replacements]):
        label = f'partition-{index}'
        (destination/label).symlink_to(matrix.resolve(), target_is_directory=True)
        for entry in load_json(matrix/'summary.json')['entries']:
            if index == 0 and entry['case_id'] in replacement_ids:
                continue
            entry = copy.deepcopy(entry)
            for key in ('case', 'run', 'nominal', 'refined', 'report'):
                if entry[key] is not None:
                    entry[key]['path'] = label+'/'+entry[key]['path']
            rows.append(entry)
    ids = {e['case_id'] for e in rows}
    selected = dict(manifest, cases=[c for c in manifest['cases'] if c['case_id'] in ids])
    atomic_json(destination/'cases.json', selected)
    shutil.copyfile(original/'toolchain.json', destination/'toolchain.json')
    merged.update(suite_id='wav-requalification-merged', entries=rows)
    for key, name in [('manifest', 'cases.json'), ('toolchain', 'toolchain.json')]:
        merged[key] = dict(path=name, sha256=sha256(destination/name))
    merged['outcomes'] = {key: aggregate([
        load_json(destination/e['report']['path'])['outcomes'][key] if e['report'] else 'pending'
        for e in rows]) for key in merged['outcomes']}
    merged['completion'] = 'completed' if all(e['report'] for e in rows) else 'incomplete'
    merged['exit_code'] = 40 if 'failed' in merged['outcomes'].values() else 50 if 'pending' in merged['outcomes'].values() else 0
    validate_summary(merged, selected['cases'])
    atomic_json(destination/'summary.json', merged)
    return destination/'summary.json'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--pilot', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--resume-from', type=Path)
    parser.add_argument('--isolate-slow', action='store_true', help='Run slow case last with a fresh alt solver pair')
    parser.add_argument('--worker-cases', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker_cases:
        code = suite(args.worker_cases, ROOT/'validation/toolchain-pilot-f.json',
                     ROOT/'build/offline-release/ts808_offline', [192000, 384000], args.output,
                     Path('/mnt/f/ts808-validation/substeps-20261104/pilots.json'),
                     native_solver='alt', native_tolerance_scale=.01, native_topology_nodeset=True,
                     resume_from=args.resume_from,
                     native_solver_overrides={SLOW_CASE: 'alt' if args.isolate_slow else 'norm'})
        raise SystemExit(code)
    if not args.source or not args.pilot:
        parser.error('--source and --pilot are required')
    output = args.output.resolve()
    if output.exists() or not output.is_relative_to(Path('/mnt/f/ts808-validation')):
        raise ValueError('A new F: directory is required')
    source, pilot = args.source.resolve(), args.pilot.resolve()
    assessment_path = source/'qualification/qualification.json'
    assessment = load_json(assessment_path)
    if assessment['assessment_completion'] != 'completed':
        raise ValueError('Source assessment is incomplete')
    manifest = load_json(source/'cases.json')
    rejected = rejected_cases(assessment, manifest)
    pilot_plan = load_json(pilot/'plan.json')
    pilot_status = load_json(pilot/'status.json')
    pilot_cases = load_json(pilot/'matrix/cases.json')['cases']
    if (pilot_plan['source_sha256'] != sha256(assessment_path)
            or pilot_plan['tolerance_scale'] != .01
            or pilot_status['status'] != 'completed'
            or any(pilot_status['outcomes'][k] != 'passed' for k in ('reference', 'numerical', 'wav'))
            or pilot_cases != [c for c in rejected if c['case_id'] == PILOT]):
        raise ValueError('Pilot source, cases or qualification mismatch')
    remaining = [c for c in rejected if c['case_id'] != PILOT]
    remaining = execution_order(remaining, args.isolate_slow)
    previous = args.resume_from.resolve() if args.resume_from else None
    completed = set()
    if previous:
        old_plan = load_json(previous/'plan.json')
        if (old_plan['source_sha256'] != sha256(assessment_path)
                or Path(old_plan['pilot']).resolve() != pilot
                or load_json(previous/'cases.json') != manifest):
            raise ValueError('Resume source, pilot or manifest differs')
        for case in remaining:
            matrix = previous/case['case_id']/'matrix'
            if (matrix/'summary.json').exists():
                old = load_json(matrix/'summary.json')
                validate_summary(old, [case])
                if old['completion'] == 'completed':
                    completed.add(case['case_id'])
    growth = measured_native_growth(pilot/'matrix')
    budget = estimate([c for c in remaining if c['case_id'] not in completed], growth['adaptive_factor'])
    free = shutil.disk_usage('/mnt/f').free
    output.mkdir()
    atomic_json(output/'plan.json', dict(source_sha256=sha256(assessment_path),
                pilot=str(pilot), measured_growth=growth, budget=budget, free_bytes=free,
                isolate_slow=args.isolate_slow, slow_solver='alt' if args.isolate_slow else 'norm',
                remaining_cases=len(remaining)-len(completed), resume_from=str(previous) if previous else None, mvp_accepted=False))
    atomic_json(output/'cases.json', manifest)
    status = dict(status='blocked_storage' if free < budget['estimated_required_bytes'] else 'running',
                  completed_cases=1, required_cases=len(rejected), mvp_accepted=False)
    atomic_json(output/'status.json', status)
    if status['status'] == 'blocked_storage':
        raise RuntimeError(f"Need {budget['estimated_required_bytes']} bytes; have {free}; no producer started")
    try:
        matrices = [pilot/'matrix']
        failed = []
        for case in remaining:
            case_dir = output/case['case_id']
            case_dir.mkdir()
            atomic_json(case_dir/'cases.json', dict(manifest, cases=[case]))
            resume_matrix = previous/case['case_id']/'matrix' if previous else None
            if args.isolate_slow and case['case_id'] == SLOW_CASE:
                resume_matrix = None  # A solver change requires a fresh nominal/refined pair.
            resume_args = ['--resume-from', str(resume_matrix)] if resume_matrix and (resume_matrix/'summary.json').exists() else []
            if args.isolate_slow:
                resume_args.append('--isolate-slow')
            if case['case_id'] not in completed:
                required = estimate([case], growth['adaptive_factor'])['estimated_required_bytes']
                if shutil.disk_usage('/mnt/f').free < required:
                    raise RuntimeError('Insufficient free space before case '+case['case_id'])
            status['current_case'] = case['case_id']
            atomic_json(output/'status.json', status)
            code = subprocess.run([sys.executable, '-u', str(Path(__file__).resolve()),
                                   '--worker-cases', str(case_dir/'cases.json'),
                                   '--output', str(case_dir/'matrix'), *resume_args], check=False).returncode
            if code not in (0, 40):
                failed.append(dict(case_id=case['case_id'], exit_code=code))
                status['incomplete_cases'] = failed
                atomic_json(output/'status.json', status)
                continue
            matrices.append(case_dir/'matrix')
            status['completed_cases'] += 1
            atomic_json(output/'status.json', status)
        if failed:
            raise RuntimeError('Incomplete cases after processing queue: '+str(failed))
        summary = merge_matrices(source/'combined-transients', matrices,
                                 output/'combined-transients', manifest)
        for name in ('matrix-alt', 'hold-diagnosis-20261104'):
            (output/name).symlink_to((source/name).resolve(), target_is_directory=True)
        status['status'] = 'auditing'
        atomic_json(output/'status.json', status)
        result = consolidate(output, output/'qualification', summary, require_passed=False)
        status.update(status='completed', automatic_qualification=result['automatic_qualification'],
                      assessment_completion=result['assessment_completion'], entry_count=result['entry_count'])
    except BaseException as error:
        status.update(status='interrupted', reason=str(error))
        raise
    finally:
        atomic_json(output/'status.json', status)


if __name__ == '__main__':
    main()
