"""Tighten native references for WAV failures without changing cases or validators.

Use a new F: directory. The pilot exercises the worst rejected physical case;
--all requires space for every rejected case before starting any producer.
"""
import argparse
import copy
from datetime import datetime, timezone
from pathlib import Path
import shutil

from ts808_validation.artifacts import ROOT, atomic_json, load_json
from ts808_validation.resources import estimate
from ts808_validation.simulator import sha256
from ts808_validation.suite import suite

PILOT = 'tone_edge_t100_f5000_a100mv-warmup2s'


def rejected_cases(assessment, manifest):
    rejected = {}
    for entry in assessment['entries']:
        if entry['outcomes']['wav'] != 'failed':
            continue
        if any(entry['outcomes'][key] != 'passed' for key in ('reference', 'numerical')):
            raise ValueError('WAV-only remedy requires qualified numerical references')
        if any(not c['id'].startswith('wav_') for c in entry['failed_checks']):
            raise ValueError('Non-WAV rejection requires a separate diagnosis')
        rejected.setdefault(entry['case_id'], set()).add(entry['rate_Hz'])
    if not rejected or any(rates != {192000, 384000} for rates in rejected.values()):
        raise ValueError('Expected paired WAV rejections on both target grids')
    cases = [copy.deepcopy(c) for c in manifest['cases'] if c['case_id'] in rejected]
    if len(cases) != len(rejected):
        raise ValueError('Assessment/manifest coverage differs')
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--all', action='store_true', help='Otherwise run only the worst rejected case')
    parser.add_argument('--resume-from', type=Path, help='Preserved attempt with identical cases and native settings')
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or not output.is_relative_to(Path('/mnt/f/ts808-validation')):
        raise ValueError('A new F: output directory is required')
    source = args.source.resolve()
    assessment_path = source/'qualification/qualification.json'
    assessment = load_json(assessment_path)
    if assessment['assessment_completion'] != 'completed':
        raise ValueError('Complete source assessment required')
    manifest = load_json(source/'cases.json')
    all_cases = rejected_cases(assessment, manifest)
    cases = all_cases if args.all else [c for c in all_cases if c['case_id'] == PILOT]
    if not cases:
        raise ValueError('Worst-case pilot is missing')
    if args.resume_from is not None:
        previous = load_json(args.resume_from/'plan.json')
        if (previous['source_sha256'] != sha256(assessment_path)
                or previous['tolerance_scale'] != .01
                or load_json(args.resume_from/'cases.json') != dict(manifest, cases=cases)):
            raise ValueError('Resume source, cases or native tolerances differ')
    output.mkdir(parents=True, exist_ok=False)
    atomic_json(output/'cases.json', dict(manifest, cases=cases))
    # The observed factor from settling runs is a lower bound for this pilot.
    # Its actual retained growth must be measured before scheduling all cases.
    factor = 1.3891729125976562
    budget = estimate(cases, factor)
    free = shutil.disk_usage('/mnt/f').free
    plan = dict(recorded_at_utc=datetime.now(timezone.utc).isoformat(),
                source_assessment=str(assessment_path), source_sha256=sha256(assessment_path),
                tolerance_scale=.01, physical_cases=len(cases), entries=2*len(cases),
                complete_remedy_cases=len(all_cases), budget=budget,
                full_budget=estimate(all_cases, factor), free_bytes=free,
                storage_gate='passed' if free >= budget['estimated_required_bytes'] else 'blocked',
                scope='Full WAV duration including onset; unchanged physical cases, maxsteps, circuit and gates',
                mvp_accepted=False)
    atomic_json(output/'plan.json', plan)
    if plan['storage_gate'] != 'passed':
        atomic_json(output/'status.json', dict(status='blocked_storage', mvp_accepted=False))
        raise RuntimeError('Insufficient F: space; no native producer started')
    atomic_json(output/'status.json', dict(status='running', mvp_accepted=False))
    try:
        code = suite(output/'cases.json', ROOT/'validation/toolchain-pilot-f.json',
                     ROOT/'build/offline-release/ts808_offline', [192000,384000],
                     output/'matrix', Path('/mnt/f/ts808-validation/substeps-20261104/pilots.json'),
                     native_solver='alt', native_tolerance_scale=.01,
                     resume_from=args.resume_from/'matrix' if args.resume_from else None,
                     native_topology_nodeset=True,
                     native_solver_overrides={'tone_edge_t000_f5000_a100mv-warmup2s':'norm'})
        summary = load_json(output/'matrix/summary.json')
        atomic_json(output/'status.json',dict(status='completed' if code in (0,40) else 'incomplete',
                    exit_code=code, outcomes=summary['outcomes'],
                    scope='Targeted WAV requalification; full 128-entry audit still required',
                    mvp_accepted=False))
    except BaseException as error:
        atomic_json(output/'status.json',dict(status='failed', reason=str(error), mvp_accepted=False))
        raise


if __name__ == '__main__':
    main()
