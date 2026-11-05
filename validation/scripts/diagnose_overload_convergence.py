"""Recheck original bytes and diagnose recovery without changing acceptance gates."""
import argparse
from pathlib import Path

import numpy as np

from ts808_validation.artifacts import ROOT, atomic_json, load_json
from ts808_validation.metrics import recovery_index, rms, local_checks
from ts808_validation.persist import consume_reference
from ts808_validation.reconstruct import pchip
from ts808_validation.simulator import sha256


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--substep-root', type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Diagnostic destination must be new')
    physical = ROOT / 'runs/mvp-pilots-02/overload_high'
    cfg = load_json(ROOT / 'validation/toolchain-pilot-f.json')
    references = {}
    for level in ('nominal', 'refined'):
        manifest, _, native = consume_reference(physical / (level+'-alt-guard'), cfg)
        references[level] = (manifest, native)
        print('Verified original', level, flush=True)
    rows = []
    experiments = []
    quantities = ('output', 'vref', 'input_base', 'output_base')
    limits = np.array([.001, .01, .01, .01])
    traces = {}
    for rate in (192000, 384000, 768000):
        directory = physical / str(rate)
        case = load_json(directory/'case.json')
        run = load_json(directory/'run/run.json')
        payload = directory/'run/traces.f64le'
        if sha256(payload) != run['trace']['sha256']:
            raise ValueError('Changed C++ trace')
        data = np.memmap(payload, mode='r', dtype='<f8', shape=tuple(run['trace']['shape']))
        names = case['trace_columns'][1:]
        columns = [names.index(n)+1 for n in quantities]
        reconstructed = {}
        for level, (manifest, native) in references.items():
            refdata = np.zeros(data.shape)
            refdata[:, 0] = data[:, 0]
            for name, col in zip(quantities, columns):
                expression = next(t['native_expression'] for t in manifest['selection']['traces'] if t['quantity_id']==name)
                refdata[:, col] = pchip(native['axis'], native['traces'][expression], data[:, 0])
            reconstructed[level] = refdata
        def index(values):
            result = recovery_index(values, names, rate)
            return None if result is None else int(result)
        indices = {level: index(ref) for level, ref in reconstructed.items()}
        indices['cpp'] = index(data)
        if any(value is None for value in indices.values()):
            raise ValueError('Recovery was not reached')
        crossings = []
        for name, col, limit in zip(quantities, columns, limits):
            crossings.append(dict(quantity=name, limit_V=float(limit), **{
                level: dict(last_outside_index=int(bad[-1]) if len(bad) else None)
                for level, values in [('cpp', data), *reconstructed.items()]
                for bad in [np.flatnonzero((np.abs(values[:, col]-values[0, col])>limit) & (values[:, 0]>=.2))]
            }))
        nominal = reconstructed['nominal']
        refined = reconstructed['refined']
        row = dict(rate_Hz=rate, recovery_indices=indices,
                   recovery_error_samples=abs(indices['cpp']-indices['nominal']),
                   reference_recovery_uncertainty_samples=abs(indices['nominal']-indices['refined']),
                   output_rms_error_V=rms(data[:, columns[0]]-nominal[:, columns[0]]),
                   crossings=crossings)
        rows.append(row)
        traces[rate] = data
        if args.substep_root and rate in (192000, 384000):
            target = args.substep_root / f'substeps-{rate}'
            meta = load_json(target/'diagnostic.json')
            if (meta['completion']!='completed' or meta['integration_rate_Hz']!=768000
                    or meta['output_rate_Hz']!=rate or meta['sample_count']!=len(data)
                    or meta['physical_case_sha256']!=case['physical_case_sha256']):
                raise ValueError('Incomplete or mismatched substep diagnostic')
            experiment = np.fromfile(target/'traces.f64le', dtype='<f8').reshape(data.shape)
            if not np.isfinite(experiment).all() or not np.array_equal(experiment[:, 0], data[:, 0]):
                raise ValueError('Invalid experimental trace/grid')
            checks = local_checks('local', experiment[:, columns[0]], nominal[:, columns[0]], rate)
            experimental_index = index(experiment)
            if experimental_index is None:
                raise ValueError('Experimental recovery was not reached')
            experiments.append(dict(output_rate_Hz=rate, integration_rate_Hz=768000,
                                    trace_sha256=sha256(target/'traces.f64le'),
                                    recovery_index=experimental_index,
                                    recovery_error_samples=abs(experimental_index-indices['nominal']),
                                    local_failed_checks=[c for c in checks if c['status']!='passed']))
        print(row, flush=True)
    differences = []
    for coarse, fine in ((192000, 384000), (384000, 768000)):
        delta = traces[coarse]-traces[fine][::fine//coarse]
        differences.append(dict(coarse_rate_Hz=coarse, fine_rate_Hz=fine,
                                output_rms_V=rms(delta[:, 26]),
                                output_peak_V=float(np.max(abs(delta[:, 26])))))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    atomic_json(args.output, dict(scope='Temporal convergence diagnostic; does not promote finer grids to target-rate acceptance',
                                 measurements=rows, grid_differences=differences, experiments=experiments))


if __name__ == '__main__':
    main()
