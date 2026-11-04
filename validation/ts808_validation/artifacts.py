"""Case identity and explicit little-endian trace integrity."""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from jsonschema import Draft202012Validator
from .simulator import confined, sha256

ROOT = Path(__file__).resolve().parents[2]


def load_json(path: Path):
    def reject(value):
        raise ValueError(f'Nonfinite JSON value: {value}')
    def real(value):
        number=float(value)
        if not math.isfinite(number):raise ValueError('Nonfinite JSON number')
        return number
    return json.loads(path.read_text(encoding='utf-8'), parse_constant=reject,parse_float=real)


def canonical_hash(descriptor: dict) -> str:
    # Every numeric field in the physical descriptor is a real SI quantity.
    # Rate-dependent integer sample counts are excluded from this projection.
    def normalize(value):
        if isinstance(value, bool):
            raise ValueError('Booleans are not physical quantities')
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, dict):
            return {key: normalize(v) for key, v in value.items()}
        if isinstance(value, list):
            return [normalize(v) for v in value]
        return value
    return hashlib.sha256(json.dumps(normalize(descriptor), sort_keys=True, separators=(',', ':'),
                                    ensure_ascii=True, allow_nan=False).encode()).hexdigest()


def validate_case(case: dict) -> None:
    Draft202012Validator(load_json(ROOT / 'schemas/case.schema.json')).validate(case)
    def finite(value):
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError('Nonfinite case')
        if isinstance(value, dict):
            for v in value.values(): finite(v)
        if isinstance(value, list):
            for v in value: finite(v)
    finite(case)
    analysis = case['analysis']
    time = analysis.get('time')
    projection = dict(analysis_kind=case['analysis_kind'], circuit=case['circuit'],
                      stimulus=case['stimulus'], time=None if time is None else
                      dict(origin_s=time['origin_s'], duration_s=time['duration_s']),
                      windows=analysis['windows'])
    if projection != case['physical_descriptor'] or canonical_hash(projection) != case['physical_case_sha256']:
        raise ValueError('Physical case identity mismatch')
    for key, filename in [('component_map_sha256', 'component_map.json'), ('device_spec_sha256', 'device_spec.md')]:
        if case['circuit'][key] != sha256(ROOT / 'reference/ts808' / filename):
            raise ValueError('Circuit input byte identity mismatch')
    rate = case['execution']['rate_Hz']
    if rate == 768000 and case['execution']['purpose'] != 'pilot':
        raise ValueError('768 kHz is pilot only')
    if time and (time['duration_s']*rate != time['sample_count']-1):
        raise ValueError('Time/count mismatch')
    if case['analysis_kind'] == 'ac':
        expected = [20.*10**(k/100) for k in range(301)]
        if analysis['frequencies_Hz'] != expected:
            raise ValueError('Frequency grid mismatch')
    # Accepted matrix is frozen, including required checks, windows and stimulus.
    catalog = load_json(ROOT / 'reference/ts808/cases.json')
    candidates=list(catalog['cases'])
    revisions_path=ROOT/'reference/ts808/case_revisions.json'
    if revisions_path.exists():
        for revision in load_json(revisions_path)['revisions']:
            revised=revision['case']
            original=next((c for c in catalog['cases'] if c['case_id']==revision['base_case_id']),None)
            if (original is None or not revision['reason'] or not revised['case_id'].startswith(original['case_id']+'-')
                    or revised['analysis_kind']!='transient' or revised['circuit']!=original['circuit']
                    or revised['stimulus']!=original['stimulus'] or revised['analysis']['required_checks']!=original['analysis']['required_checks']):
                raise ValueError('Revision may only extend an explicitly identified settling case')
            old_windows=original['analysis']['windows'];new_windows=revised['analysis']['windows']
            if (len(old_windows)!=1 or len(new_windows)!=1 or old_windows[0]['role']!='steady' or new_windows[0]['role']!='steady'
                    or new_windows[0]['start_s']<old_windows[0]['start_s']
                    or new_windows[0]['stop_s']-new_windows[0]['start_s']!=old_windows[0]['stop_s']-old_windows[0]['start_s']
                    or revised['analysis']['time']['duration_s']!=new_windows[0]['stop_s']):
                raise ValueError('Settling revision must preserve window length and extend warm-up')
            candidates.append(revised)
    baseline = next((c for c in candidates if c['case_id'] == case['case_id']), None)
    if baseline is None or baseline['physical_descriptor'] != projection or baseline['analysis']['required_checks'] != analysis['required_checks']:
        raise ValueError('Unknown or changed mandatory physical case')


def atomic_json(path: Path, document: dict) -> None:
    temp = path.with_name(path.name+'.tmp')
    temp.write_text(json.dumps(document, indent=2, allow_nan=False)+'\n')
    temp.replace(path)


def finalize_run(directory: Path, case_path: Path, executable: Path) -> dict:
    case = load_json(case_path)
    validate_case(case)
    run = load_json(directory / 'run.json')
    if run['completion']['state'] != 'completed':
        raise ValueError('Failed/incomplete run cannot qualify')
    if run['physical_case_sha256'] != case['physical_case_sha256'] or run['case_id'] != case['case_id']:
        raise ValueError('Run identity mismatch')
    trace = run['trace']
    count = case['analysis'].get('time', {}).get('sample_count', 1)
    path = confined(directory, trace['filename'])
    if (trace['filename'] != 'traces.f64le' or trace['dtype'] != '<f8' or trace['order'] != 'C'
            or trace['shape'] != [count, 32] or trace['byte_length'] != count*256
            or path.stat().st_size != count*256 or run['completion']['written_samples'] != count):
        raise ValueError('Trace length/layout mismatch')
    values = np.memmap(path, mode='r', dtype='<f8', shape=(count, 32))
    if not np.isfinite(values).all():
        raise ValueError('Nonfinite trace')
    expected = np.arange(count, dtype=np.float64)/case['execution']['rate_Hz']
    if values[0, 0] != 0 or np.any(np.abs(values[:, 0]-expected) > 4*np.spacing(expected)):
        raise ValueError('Timestamp grid mismatch')
    if count > 1 and not np.all(np.diff(values[:, 0]) > 0):
        raise ValueError('Nonmonotone grid')
    if [c['id'] for c in trace['columns']] != case['trace_columns']:
        raise ValueError('Trace column mismatch')
    trace.update(integrity='verified', sha256=sha256(path))
    if 'response' in run:
        response = run['response']; payload = confined(directory, response['filename'])
        if (response['filename'] != 'response.f64le' or response['shape'] != [301, 5]
                or response['dtype'] != '<f8' or response['order'] != 'C'
                or payload.stat().st_size != 301*5*8):
            raise ValueError('AC response layout mismatch')
        data = np.fromfile(payload, dtype='<f8').reshape(301, 5)
        if not np.isfinite(data).all() or not np.allclose(data[:, 0], case['analysis']['frequencies_Hz'], rtol=0, atol=1e-10):
            raise ValueError('Invalid AC response')
        response.update(integrity='verified', sha256=sha256(payload))
    run['case_input_sha256'] = sha256(case_path)
    run['build']['executable_sha256'] = sha256(executable)
    run['build']['source_files'] = {str(p.relative_to(ROOT)): sha256(p)
                                  for folder in ('src', 'include', 'app')
                                  for p in sorted((ROOT / folder).rglob('*')) if p.is_file()}
    atomic_json(directory / 'run.json', run)
    return run
