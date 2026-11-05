import copy
import os
import pytest

from ts808_validation.qualification import EvidenceAudit, reconcile, assessment, wav_source_settings_match
from ts808_validation.simulator import sha256
from ts808_validation.artifacts import ROOT, atomic_json, load_json


def catalog():
    return [dict(case_id='dc', analysis_kind='dc', physical_case_sha256='a'),
            dict(case_id='tone', analysis_kind='transient', physical_case_sha256='b')]


def rows():
    return [dict(case_id='dc', rate_Hz=None, physical_case_sha256='a'),
            dict(case_id='tone', rate_Hz=192000, physical_case_sha256='b'),
            dict(case_id='tone', rate_Hz=384000, physical_case_sha256='b')]


def test_legacy_wav_settings_allow_only_missing_derived_native_options():
    request = dict(level='nominal', maxstep_s=1e-7, dc_protocol='solver=norm',
                   wav=dict(rate_Hz=192000, scale_V_per_FS=8),
                   native_options=dict(solver='norm', method='trap'))
    legacy = {k: copy.deepcopy(v) for k, v in request.items() if k != 'native_options'}
    assert wav_source_settings_match(request, legacy)
    assert wav_source_settings_match(request, copy.deepcopy(request))
    for key, value in [('maxstep_s', 2e-7), ('dc_protocol', 'solver=alt'),
                       ('native_options', dict(solver='alt', method='trap')),
                       ('unexpected', True)]:
        wrong = dict(legacy, **{key: value})
        assert not wav_source_settings_match(request, wrong)
    wrong = copy.deepcopy(legacy)
    wrong['wav']['scale_V_per_FS'] = 4
    assert not wav_source_settings_match(request, wrong)
    wrong = dict(legacy)
    del wrong['maxstep_s']
    assert not wav_source_settings_match(request, wrong)


def test_canonical_coverage_rejects_omitted_duplicate_and_extra_entries():
    expected, found = reconcile(catalog(), rows())
    assert len(expected) == len(found) == 3
    with pytest.raises(ValueError, match='Missing'):
        reconcile(catalog(), rows()[:-1])
    with pytest.raises(ValueError, match='Duplicate qualification'):
        reconcile(catalog(), rows()+rows()[:1])
    with pytest.raises(ValueError, match='Unexpected'):
        reconcile(catalog(), rows()+[dict(case_id='extra', rate_Hz=None)])


def test_canonical_coverage_rejects_wrong_physical_identity():
    bad = copy.deepcopy(rows())
    bad[1]['physical_case_sha256'] = 'different-circuit'
    with pytest.raises(ValueError, match='Physical identity'):
        reconcile(catalog(), bad)
    with pytest.raises(ValueError, match='Duplicate physical'):
        reconcile(catalog()+catalog()[:1], rows())


def test_assessment_preserves_failed_checks_and_distinguishes_blocked_from_uninvoked_wav():
    failure = dict(required=True, applicable=True, status='failed', id='settling_dc')
    report = dict(outcomes=dict(reference='passed', numerical='failed', wav='pending'),
                  checks=[failure], reference_qualification={'checks': []})
    result = assessment(report, 'transient')
    assert result == dict(evaluated=True, wav_blocked_by_failed_gate=True, failed_checks=[failure])
    report['outcomes']['numerical'] = 'passed'
    result = assessment(report, 'transient')
    assert not result['evaluated'] and not result['wav_blocked_by_failed_gate']
    assert result['failed_checks'] == [failure]


def test_integrity_audit_rejects_mutation_even_with_restored_mtime(tmp_path):
    executable = tmp_path/'executable'
    executable.write_bytes(b'executable')
    payload = tmp_path/'payload'
    payload.write_bytes(b'original')
    audit = EvidenceAudit(executable, [])
    audit.file(payload, sha256(payload))
    audit.finish()
    stamp = payload.stat()
    payload.write_bytes(b'modified')
    os.utime(payload, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
    with pytest.raises(ValueError, match='changed during audit'):
        audit.finish()


def test_integrity_audit_rejects_bad_hash_and_changed_executable(tmp_path):
    executable = tmp_path/'executable'
    executable.write_bytes(b'executable')
    audit = EvidenceAudit(executable, [])
    with pytest.raises(ValueError, match='hash mismatch'):
        audit.file(executable, 'wrong')
    executable.write_bytes(b'new executable')
    with pytest.raises(ValueError, match='Executable/validator changed'):
        audit.finish()


@pytest.mark.parametrize('changed', ['cases.json', 'toolchain.json'])
def test_suite_resume_rejects_changed_manifest_or_toolchain_before_copying(tmp_path, monkeypatch, changed):
    from ts808_validation.suite import suite
    import ts808_validation.cli as cli
    monkeypatch.setattr(cli, 'doctor', lambda _: {'status': 'passed'})
    predecessor = tmp_path/'old'
    predecessor.mkdir()
    case = load_json(ROOT/'reference/ts808/cases.json')['cases'][0]
    atomic_json(tmp_path/'cases.json', {'cases': [case]})
    atomic_json(tmp_path/'toolchain.json', {'test': 'configuration'})
    for name in ('cases.json', 'toolchain.json'):
        (predecessor/name).write_bytes((tmp_path/name).read_bytes())
    with (predecessor/changed).open('a') as stream:
        stream.write(' ')
    with pytest.raises(ValueError, match='Resume manifest/toolchain differs'):
        suite(tmp_path/'cases.json', tmp_path/'toolchain.json', tmp_path/'executable',
              [192000,384000], tmp_path/'new', tmp_path/'pilots.json', resume_from=predecessor)
    assert not (tmp_path/'new').exists()


@pytest.mark.parametrize('nodeset', [False, True])
def test_native_solver_retry_preserves_requests_and_only_tightens_tolerances(tmp_path, monkeypatch, nodeset):
    import importlib
    module = importlib.import_module('ts808_validation.suite')
    import ts808_validation.cli as cli
    case = {'case_id': 'test', 'trace_columns': ['time', 'input', 'input_emitter', 'clip_minus', 'z_clip', 'i_test']}
    decks = []
    runs = []
    monkeypatch.setattr(cli, 'make_deck', lambda *_: '.temp 25\n.options reltol=1e-6 abstol=1e-12 vntol=1e-9 chgtol=1e-16\n.tran 0 1 0 1e-7\n.end')
    def prepare(_model, _base, destination, **kwargs):
        destination.mkdir()
        decks.append(kwargs['deck'])
        atomic_json(destination/'request.json', kwargs['settings'])
    def run(destination, _executable):
        runs.append(destination)
        if len(runs) == 1:
            raise RuntimeError('singular matrix')
    monkeypatch.setattr(module, 'prepare_request', prepare)
    monkeypatch.setattr(module, 'run_request', run)
    monkeypatch.setattr(module, 'import_reference', lambda _src, dst, _cfg: dst.mkdir())
    physical = tmp_path/'case'
    physical.mkdir()
    cfg = {'workspace': {'wsl_root': str(tmp_path)}, 'tools': {'ltspice': {'path': 'native'}}}
    result = module.produce_native_reference(case, physical/'case.json', physical, 'nominal', cfg,
                                            'alt', tolerance_scale=.01, solver_fallback=True,
                                            topology_nodeset=nodeset)
    assert result == physical/'nominal'
    attempts = load_json(physical/'nominal-attempts.json')['attempts']
    assert [a['status'] for a in attempts] == ['failed', 'completed']
    assert runs[0] != runs[1] and all((p/'request.json').exists() for p in runs)
    assert decks[0].replace('solver=alt', 'solver=norm') == decks[1]
    assert '.tran 0 1 0 1e-7' in decks[1]
    assert ('.nodeset V(input)=0 V(input_emitter)=3.85 V(clip_minus)=4.5 V(xclip:z)=0\n' in decks[1]) == nodeset
    assert 'V(i_test)' not in decks[1]
    import re
    for name, expected in [('reltol', 1e-8), ('abstol', 1e-14), ('vntol', 1e-11), ('chgtol', 1e-18)]:
        assert float(re.search(name+r'=([\deE.+-]+)', decks[1])[1]) == pytest.approx(expected)
