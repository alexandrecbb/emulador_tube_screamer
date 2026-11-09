"""Check exact physical-case replacement and the measured storage gate inputs."""
import runpy

import pytest

from ts808_validation.artifacts import ROOT, atomic_json, load_json


def functions(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'validation/scripts'))
    return runpy.run_path(str(ROOT/'validation/scripts/complete_wav_requalification.py'))


def test_merge_replaces_warmup_id_without_dropping_original_passes(tmp_path, monkeypatch):
    module = functions(monkeypatch)
    # The full schema/coverage validator runs in production; here isolate the
    # path transformation and exact-ID selection from report schema fixtures.
    module['merge_matrices'].__globals__['validate_summary'] = lambda *args: None
    manifest = dict(cases=[dict(case_id='a-warmup2s'), dict(case_id='b-warmup2s')])

    def matrix(name, ids):
        directory = tmp_path/name
        directory.mkdir()
        atomic_json(directory/'cases.json', dict(cases=[dict(case_id=i) for i in ids]))
        atomic_json(directory/'toolchain.json', {})
        rows = []
        for case_id in ids:
            report = directory/(case_id+'.json')
            atomic_json(report, dict(outcomes=dict(reference='passed', numerical='passed', wav='passed')))
            for rate in (192000, 384000):
                rows.append(dict(case_id=case_id, rate_Hz=rate, case=None, run=None,
                                 nominal=None, refined=None, report=dict(path=report.name)))
        atomic_json(directory/'summary.json', dict(entries=rows, outcomes=dict(reference='passed', numerical='passed', wav='passed')))
        return directory

    original = matrix('original', ['a-warmup2s', 'b-warmup2s'])
    replacement = matrix('replacement', ['a-warmup2s'])
    before = (original/'summary.json').read_bytes()
    result = module['merge_matrices'](original, [replacement], tmp_path/'merged', manifest)
    rows = load_json(result)['entries']
    assert len(rows) == 4
    assert all(e['report']['path'].startswith('partition-1/') for e in rows if e['case_id']=='a-warmup2s')
    assert all(e['report']['path'].startswith('partition-0/') for e in rows if e['case_id']=='b-warmup2s')
    assert all((result.parent/e['report']['path']).is_file() for e in rows)
    assert (original/'summary.json').read_bytes() == before
    with pytest.raises(ValueError, match='Overlapping'):
        module['merge_matrices'](original, [replacement, replacement], tmp_path/'duplicate', manifest)


def test_measured_budget_counts_unique_original_directories(tmp_path, monkeypatch):
    module = functions(monkeypatch)
    source = tmp_path/'native'
    source.mkdir()
    (source/'payload.raw').write_bytes(b'x'*1000)
    matrix = tmp_path/'matrix'
    case = matrix/'case'
    for level in ('nominal', 'refined'):
        (case/level).mkdir(parents=True)
        atomic_json(case/level/'reference.json', dict(source=dict(request=dict(locator=dict(wsl_path=str(source/'request.json'))))))
    atomic_json(matrix/'cases.json', dict(cases=[dict(case_id='case', analysis_kind='transient', analysis=dict(time=dict(duration_s=1)))]))
    result = module['measured_native_growth'](matrix)
    assert result['retained_native_bytes'] == 1000
    assert result['original_directories'] == [str(source)]
    assert result['adaptive_factor'] >= 1.3891729125976562


def test_slow_case_moves_to_end_without_changing_cases(monkeypatch):
    module = functions(monkeypatch)
    slow = dict(case_id=module['SLOW_CASE'])
    cases = [dict(case_id='approved'), slow, dict(case_id='pending')]
    before = list(cases)
    assert module['execution_order'](cases, True) == [cases[0], cases[2], slow]
    assert cases == before
    assert module['execution_order'](cases, False) == cases
