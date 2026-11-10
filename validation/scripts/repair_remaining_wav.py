"""Diagnose the final WAV rejection, try a fresh native pair, then audit all entries."""
import argparse
import gc
from pathlib import Path
import shutil
import subprocess
import sys

from complete_wav_requalification import measured_native_growth, merge_matrices
from requalify_wav_references import rejected_cases
from ts808_validation.artifacts import ROOT, atomic_json, load_json
from ts808_validation.compare import validator_hash
from ts808_validation.qualification import consolidate
from ts808_validation.resources import estimate
from ts808_validation.simulator import sha256
from ts808_validation.suite import suite

CASE = 'tone_high_f5000_a500mv-warmup2s'


def select_case(assessment, manifest):
    if assessment['assessment_completion'] != 'completed' or assessment['entry_count'] != 128:
        raise ValueError('A complete 128-entry source audit is required')
    cases = rejected_cases(assessment, manifest)
    if len(cases) != 1 or cases[0]['case_id'] != CASE:
        raise ValueError('Unexpected rejection scope; diagnose separately')
    return cases


def diagnose(source, output):
    import numpy as np
    from ts808_validation.reference import read_native
    from ts808_validation.reconstruct import pchip
    target = np.arange(round(2.5*192000))/192000
    values = []
    originals = []
    for level in ('nominal', 'refined'):
        manifest = load_json(source/CASE/'matrix'/CASE/level/'reference.json')
        directory = Path(manifest['source']['request']['locator']['wsl_path']).parent
        native = read_native(directory/'deck.raw', directory/'deck.log',
                             analysis_kind='transient', trace_names=['V(output)'])
        values.append(pchip(native['axis'], native['traces']['V(output)'], target))
        originals.append(dict(directory=str(directory), request_sha256=sha256(directory/'request.json')))
        del native
        gc.collect()
    delta = values[0]-values[1]
    rows = []
    for start, stop in ((0,.005),(.005,.1),(.1,.5),(.5,2),(2,2.5),(0,2.5)):
        error = delta[(target >= start) & (target < stop)]
        rows.append(dict(start_s=start, stop_s=stop, rms_V=float(np.sqrt(np.mean(error**2))),
                         peak_V=float(np.max(np.abs(error))),
                         mean_V=float(np.mean(error)),
                         standard_deviation_V=float(np.std(error)),
                         dc_energy_fraction=float(np.mean(error)**2/np.mean(error**2))
                         if np.any(error) else 0.0))
    atomic_json(output/'diagnosis.json', dict(scope='Diagnostic only; no fitting or exclusion from gates',
                rate_Hz=192000, originals=originals, intervals=rows))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--stage', choices=('diagnose','worker'))
    parser.add_argument('--solver', choices=('norm','alt'), default='norm')
    parser.add_argument('--tolerance-scale', type=float, default=.01)
    parser.add_argument('--growth-margin', type=float, default=1.)
    args = parser.parse_args()
    if not 0 < args.tolerance_scale <= .01 or not 1 <= args.growth_margin <= 10:
        parser.error('Require tolerance scale in (0,.01] and growth margin in [1,10]')
    source, output = args.source.resolve(), args.output.resolve()
    if args.stage == 'diagnose':
        diagnose(source, output)
        return
    if args.stage == 'worker':
        code = suite(output/'selected-cases.json', ROOT/'validation/toolchain-pilot-f.json',
                     ROOT/'build/offline-release/ts808_offline', [192000,384000], output/'matrix',
                     Path('/mnt/f/ts808-validation/substeps-20261104/pilots.json'),
                     native_solver=args.solver, native_tolerance_scale=args.tolerance_scale, native_topology_nodeset=True)
        raise SystemExit(code)
    if output.exists() or not output.is_relative_to(Path('/mnt/f/ts808-validation')):
        raise ValueError('Use a new F: output directory')
    assessment_path = source/'qualification/qualification.json'
    assessment, manifest = load_json(assessment_path), load_json(source/'cases.json')
    selected = select_case(assessment, manifest)
    if assessment['validator_sha256'] != validator_hash():
        raise ValueError('Source validator identity differs')
    growth = measured_native_growth(source/CASE/'matrix')
    budget = estimate(selected, growth['adaptive_factor'] * args.growth_margin)
    free = shutil.disk_usage('/mnt/f').free
    output.mkdir()
    atomic_json(output/'plan.json', dict(source=str(source), source_sha256=sha256(assessment_path),
                solver=args.solver, tolerance_scale=args.tolerance_scale, growth_margin=args.growth_margin, budget=budget, free_bytes=free,
                measured_growth=growth, shutdown_authorized=False, mvp_accepted=False))
    atomic_json(output/'cases.json', manifest)
    atomic_json(output/'selected-cases.json', dict(manifest, cases=selected))
    status = dict(status='running', mvp_accepted=False, shutdown_authorized=False)
    try:
        if free < budget['estimated_required_bytes']:
            raise RuntimeError('Insufficient space; no producer started')
        for stage in ('diagnose','worker'):
            status['status'] = stage
            atomic_json(output/'status.json', status)
            code = subprocess.run([sys.executable,'-u',str(Path(__file__).resolve()),
                        '--source',str(source),'--output',str(output),'--stage',stage,
                        '--solver',args.solver,'--tolerance-scale',str(args.tolerance_scale),
                        '--growth-margin',str(args.growth_margin)],check=False).returncode
            if code != 0 and not (stage == 'worker' and code == 40):
                raise RuntimeError(f'Incomplete {stage}: {code}')
        summary = merge_matrices(source/'combined-transients', [output/'matrix'],
                                 output/'combined-transients', manifest)
        for name in ('matrix-alt','hold-diagnosis-20261104'):
            (output/name).symlink_to((source/name).resolve(), target_is_directory=True)
        status['status'] = 'auditing'
        atomic_json(output/'status.json', status)
        result = consolidate(output, output/'qualification', summary, require_passed=False)
        status.update(status='completed', automatic_qualification=result['automatic_qualification'],
                      entry_count=result['entry_count'], failed_entry_count=result['failed_entry_count'])
    except BaseException as error:
        status.update(status='interrupted', reason=str(error))
        raise
    finally:
        atomic_json(output/'status.json', status)


if __name__ == '__main__':
    main()
