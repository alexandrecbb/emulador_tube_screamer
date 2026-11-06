import copy
import runpy

import pytest

from ts808_validation.artifacts import ROOT, atomic_json, load_json, validate_case
from ts808_validation.simulator import sha256


def script(name):
    return runpy.run_path(str(ROOT/'validation/scripts'/name))


def test_duration_remedy_covers_exactly_the_paired_rejections():
    assessment = load_json(ROOT/'validation/results/qualification-2026-11-05/automatic-qualification.json')
    failed = {e['case_id'] for e in assessment['entries'] if e['failed_checks']}
    catalog = load_json(ROOT/'reference/ts808/cases.json')['cases']
    revisions = load_json(ROOT/'reference/ts808/case_revisions.json')['revisions']
    new = [r for r in revisions if r['base_case_id'] in failed]
    assert len(failed) == len(new) == 25
    revise = script('resolve_dc_settling.py')['revise']
    for revision in new:
        base = next(c for c in catalog if c['case_id']==revision['base_case_id'])
        before = copy.deepcopy(base)
        current = revise(base)
        assert base == before
        assert current == revision['case']
        assert current['circuit'] == base['circuit']
        assert current['stimulus'] == base['stimulus']
        assert current['analysis']['required_checks'] == base['analysis']['required_checks']
        assert current['analysis']['windows'] == [dict(id='steady',start_s=2.,stop_s=2.5,role='steady')]
        assert current['physical_case_sha256'] != base['physical_case_sha256']
        validate_case(current)


def test_merge_retains_original_passes_and_replaces_rejected_identities(tmp_path):
    merge = script('run_settling_requalification.py')['merge_transients']
    catalog = load_json(ROOT/'reference/ts808/cases.json')
    bases = [c for c in catalog['cases'] if c['case_id'] in
             ('tone_center_f1000_a010mv','tone_center_f82_a010mv')]
    revised = script('resolve_dc_settling.py')['revise'](bases[0])
    hashes = 'a'*64
    outcomes = dict(reference='passed',numerical='passed',wav='passed',listening='not_applicable',combined='passed')

    def partition(path,cases):
        path.mkdir()
        atomic_json(path/'cases.json',dict(catalog,cases=cases))
        atomic_json(path/'toolchain.json',{})
        rows = []
        for c in cases:
            for rate in (192000,384000):
                name = f"{c['case_id']}-{rate}.json"
                atomic_json(path/name,dict(outcomes=outcomes))
                ref = dict(path=name,sha256=sha256(path/name))
                rows.append(dict(case_id=c['case_id'],physical_case_sha256=c['physical_case_sha256'],rate_Hz=rate,
                    **{key:dict(ref) for key in ('case','run','nominal','refined','report')},
                    status='passed',exit_code=0,reason='fixture'))
        atomic_json(path/'summary.json',dict(schema_version=1,suite_id='fixture',
            manifest=dict(path='cases.json',sha256=hashes),toolchain=dict(path='toolchain.json',sha256=hashes),
            rates_Hz=[192000,384000],completion='completed',entries=rows,outcomes=outcomes,exit_code=0))

    old,new = tmp_path/'old',tmp_path/'new'
    partition(old,bases)
    partition(new,[revised])
    before = sha256(old/'summary.json')
    complete = tmp_path/'complete.json'
    atomic_json(complete,dict(catalog,cases=[revised,bases[1]]))
    merged = load_json(merge(old,new,tmp_path/'combined',complete))
    assert sha256(old/'summary.json') == before
    assert len(merged['entries']) == 4
    assert {r['case_id'] for r in merged['entries']} == {revised['case_id'],bases[1]['case_id']}
    for row in merged['entries']:
        assert sha256(tmp_path/'combined'/row['report']['path']) == row['report']['sha256']
    broken = load_json(new/'summary.json')
    broken['entries'].pop()
    atomic_json(new/'summary.json',broken)
    with pytest.raises(ValueError,match='Omitted/duplicate/unexpected'):
        merge(old,new,tmp_path/'missing',complete)


def test_partial_resume_checks_reference_integrity_and_physical_identity(tmp_path):
    from ts808_validation.suite import resumed_reference
    class Session:
        def __init__(self):self.calls=[]
        def consume(self,path,config):
            self.calls.append((path,config))
            if config.get('corrupt'):raise ValueError('Changed original bytes')
    session=Session();case={'physical_case_sha256':'a'*64}
    assert resumed_reference(tmp_path,case,{},session) is None
    assert not session.calls
    atomic_json(tmp_path/'reference.json',case)
    assert resumed_reference(tmp_path,case,{},session)==tmp_path
    assert session.calls==[(tmp_path,{})]
    with pytest.raises(ValueError,match='Changed original bytes'):
        resumed_reference(tmp_path,case,{'corrupt':True},session)
    with pytest.raises(ValueError,match='Changed resumed reference case'):
        resumed_reference(tmp_path,{'physical_case_sha256':'b'*64},{},session)


def test_delivery_requires_complete_coverage_but_preserves_rejection():
    gate=script('complete_settling_delivery.py')['delivery_gate']
    complete=dict(assessment_completion='completed',entry_count=128,physical_case_count=91,
                  automatic_qualification='failed')
    gate({'status':'completed'},complete)
    for key,value in [('assessment_completion','incomplete'),('entry_count',127),('physical_case_count',90)]:
        with pytest.raises(ValueError,match='Complete 91-case/128-entry'):
            gate({'status':'completed'},dict(complete,**{key:value}))
    with pytest.raises(ValueError,match='Complete 91-case/128-entry'):
        gate({'status':'running'},complete)
