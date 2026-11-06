"""Prepare explicit T18 duration revisions and check C++ settling before native runs.

This does not promote a C++ diagnostic to numerical/reference/WAV qualification.
Original cases and reports remain unchanged. New evidence must use new directories.
"""
import argparse
import copy
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess

import numpy as np

from ts808_validation.artifacts import (ROOT, atomic_json, canonical_hash,
                                       configure_substeps, finalize_run, load_json,
                                       validate_case)
from ts808_validation.metrics import settling_checks
from ts808_validation.resources import estimate
from ts808_validation.simulator import sha256


def revise(case, warmup=2.0):
    revised = copy.deepcopy(case)
    revised['case_id'] = case['case_id'] + f'-warmup{warmup:g}s'
    stop = warmup + .5
    revised['analysis']['windows'] = [dict(id='steady', start_s=warmup,
                                          stop_s=stop, role='steady')]
    revised['analysis']['time'].update(duration_s=stop,
        sample_count=round(stop * revised['execution']['rate_Hz']) + 1)
    revised['physical_descriptor']['time']['duration_s'] = stop
    revised['physical_descriptor']['windows'] = copy.deepcopy(revised['analysis']['windows'])
    revised['physical_case_sha256'] = canonical_hash(revised['physical_descriptor'])
    return revised


def prepare(assessment, destination):
    if destination.exists():
        raise ValueError('Preparation destination must be new; preserve previous evidence')
    old = load_json(assessment)
    rejected = {}
    for entry in old['entries']:
        if entry['failed_checks']:
            if {c['id'] for c in entry['failed_checks']} != {'cpp_settling_dc', 'reference_settling_dc'}:
                raise ValueError('Unexpected rejection; duration-only remedy is not justified')
            rejected.setdefault(entry['case_id'], []).append(entry)
    catalog = load_json(ROOT/'reference/ts808/cases.json')
    revisions_path = ROOT/'reference/ts808/case_revisions.json'
    revisions = load_json(revisions_path)
    cases = []
    new_revisions = []
    for case_id, entries in sorted(rejected.items()):
        if {e['rate_Hz'] for e in entries} != {192000, 384000}:
            raise ValueError('Expected the same physical rejection on both target grids')
        base = next(c for c in catalog['cases'] if c['case_id'] == case_id)
        revised = revise(base)
        existing = next((r for r in revisions['revisions'] if r['case']['case_id'] == revised['case_id']), None)
        if existing and existing['case'] != revised:
            raise ValueError('Conflicting explicit revision')
        if not existing:
            new_revisions.append(dict(base_case_id=case_id,
                reason='T18 explicit duration revision: both C++ and LTspice failed the 10 uV DC settling gate in the original 0.5–1 s window; retain all gates, stimulus and circuit, extend warm-up to 2 s based on independently qualified Center/High pilots.',
                case=revised))
        cases.append(configure_substeps(copy.deepcopy(revised), 192000))
    if not cases:
        raise ValueError('No paired DC settling failures to revise')
    revisions['revisions'].extend(new_revisions)
    # This is the explicit catalog of allowed revisions, not an acceptance record.
    atomic_json(revisions_path, revisions)
    for case in cases:
        validate_case(case)
    destination.mkdir(parents=True, exist_ok=False)
    manifest = dict(schema_version=1, model_id=catalog['model_id'],
                    rates_Hz=[192000, 384000], cases=cases)
    atomic_json(destination/'cases.json', manifest)
    replacements = {r['base_case_id']:r['case'] for r in revisions['revisions']}
    complete = copy.deepcopy(catalog)
    complete['cases'] = [configure_substeps(copy.deepcopy(replacements.get(c['case_id'], c)), 192000)
                         for c in catalog['cases']]
    atomic_json(destination/'complete-cases.json', complete)
    plan = estimate(cases)
    free = shutil.disk_usage('/mnt/f').free
    # Use measured original RAW growth as well as the analytical lower bound.
    observed_factors = []
    for entries in rejected.values():
        report = load_json(Path(entries[0]['report_path']))
        raw_bytes = 0
        for level in ('nominal', 'refined'):
            ref = load_json(Path(report['reference_qualification'][level]['manifest_path']['wsl_path']))
            raw_bytes += Path(ref['source']['raw']['locator']['wsl_path']).stat().st_size
        observed_factors.append(raw_bytes/(384000*8*256*3))
    conservative = estimate(cases, max(1.05, *observed_factors))
    atomic_json(destination/'plan.json', dict(recorded_at_utc=datetime.now(timezone.utc).isoformat(),
        source_assessment=str(assessment.resolve()), source_sha256=sha256(assessment),
        revised_physical_cases=len(cases), revised_entries=2*len(cases),
        analytical_plan=plan, measured_growth_plan=conservative, free_bytes=free,
        additional_free_bytes=max(0, conservative['estimated_required_bytes']-free),
        native_storage_gate='passed' if free>=conservative['estimated_required_bytes'] else 'blocked',
        automatic_qualification='pending', mvp_accepted=False))
    return cases


def cpp_checks(cases, destination, executable, selected):
    rows = []
    required = sum((round(2.5*r)+1)*256 for _ in selected for r in (192000,384000))
    if shutil.disk_usage(destination).free < required + 2*1024**3:
        raise ValueError('Insufficient F: space for diagnostic traces and reserve')
    for case in cases:
        if case['case_id'].removesuffix('-warmup2s') not in selected:
            continue
        for rate in (192000, 384000):
            current = configure_substeps(copy.deepcopy(case), rate)
            target = destination/'cpp-diagnostics'/case['case_id']/str(rate)
            target.mkdir(parents=True, exist_ok=False)
            cp = target/'case.json'
            atomic_json(cp, current)
            print('C++ settling diagnostic',case['case_id'],rate,flush=True)
            with (target/'execute.log').open('w') as log:
                subprocess.run([str(executable), '--case', str(cp), '--output', str(target/'run')],
                               stdout=log, stderr=subprocess.STDOUT, check=True)
            run = finalize_run(target/'run', cp, executable)
            data = np.memmap(target/'run/traces.f64le', dtype='<f8', mode='r',
                             shape=tuple(run['trace']['shape']))
            window = current['analysis']['windows'][0]
            mask = (data[:,0]>=window['start_s']) & (data[:,0]<window['stop_s'])
            checks = settling_checks(data[mask,current['trace_columns'].index('output')],
                                     data[mask,0], current['stimulus']['frequency_Hz'], 'cpp_settling')
            rows.append(dict(case_id=current['case_id'],rate_Hz=rate,checks=checks,
                             run=str(target/'run/run.json'), run_sha256=sha256(target/'run/run.json')))
            atomic_json(destination/'cpp-diagnostics.json',dict(scope='C++ settling diagnostic only; native reference and WAV remain mandatory',
                        executable_sha256=sha256(executable),entries=rows,
                        status='failed' if any(c['status']!='passed' for row in rows for c in row['checks']) else 'passed',
                        automatic_qualification='pending'))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assessment',type=Path,default=ROOT/'validation/results/qualification-2026-11-05/automatic-qualification.json')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--cpp-check',nargs='+',default=[])
    args = parser.parse_args()
    if not args.output.resolve().is_relative_to(Path('/mnt/f/ts808-validation')):
        raise ValueError('New validation artifacts must be on authorized F: root')
    cases = prepare(args.assessment,args.output)
    if args.cpp_check:
        known = {c['case_id'].removesuffix('-warmup2s') for c in cases}
        if set(args.cpp_check)-known:
            raise ValueError('Unknown diagnostic case')
        cpp_checks(cases,args.output,ROOT/'build/offline-release/ts808_offline',args.cpp_check)
    print((args.output/'plan.json').read_text(),flush=True)


if __name__ == '__main__':
    main()
