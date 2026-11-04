import copy
from pathlib import Path
import numpy as np
import pytest
from ts808_validation.artifacts import ROOT,load_json
from ts808_validation.persist import validate_schema
from ts808_validation.metrics import null_checks,bode_checks,local_checks,recovery_index


def test_schema_unknown_keys_and_versions():
    for name in ('run','failure','report','reference_request','reference_result','imported_reference','suite_summary','abx_session'):
        schema=load_json(ROOT/'schemas'/f'{name}.schema.json')
        from jsonschema import Draft202012Validator
        Draft202012Validator.check_schema(schema)
        with pytest.raises(Exception):validate_schema(name,{'schema_version':2})
        with pytest.raises(Exception):validate_schema(name,{'schema_version':1,'unexpected':True})


def test_independent_numeric_limits():
    ref=np.ones(1000)
    assert null_checks('null',ref+.0011,ref)[0]['status']=='failed'
    assert null_checks('silent',np.full(1000,2e-6),np.zeros(1000))[0]['status']=='failed'
    assert bode_checks('floor',np.array([2e-6]),np.array([0j]))[0]['status']=='failed'
    assert bode_checks('phase',np.array([np.exp(1j*np.deg2rad(3))]),np.array([1+0j]))[1]['status']=='failed'
    x=np.zeros(192000);y=x.copy();y[100:150]=.001
    assert any(c['status']=='failed' for c in local_checks('local',y,x,192000))


def test_suite_expected_entries_and_failure_dominates():
    from ts808_validation.suite import validate_summary,aggregate
    cases=load_json(ROOT/'reference/ts808/cases.json')['cases']
    ref=dict(path='cases.json',sha256='a'*64)
    summary=dict(schema_version=1,suite_id='test',manifest=ref,toolchain=ref,rates_Hz=[192000,384000],completion='incomplete',entries=[],outcomes={k:'pending' for k in ('reference','numerical','wav','listening','combined')},exit_code=50)
    for c in cases:
        for r in ((192000,384000) if c['analysis_kind']=='transient' else (None,)):
            summary['entries'].append(dict(case_id=c['case_id'],physical_case_sha256=c['physical_case_sha256'],rate_Hz=r,case=None,run=None,nominal=None,refined=None,report=None,status='not_evaluated',exit_code=None,reason='Uninvoked'))
    validate_summary(summary,cases)
    for mutation in ('omitted','duplicate','wrong_identity','false_pass'):
        bad=copy.deepcopy(summary)
        if mutation=='omitted':bad['entries'].pop()
        elif mutation=='duplicate':bad['entries'].append(copy.deepcopy(bad['entries'][0]))
        elif mutation=='wrong_identity':bad['entries'][0]['physical_case_sha256']='b'*64
        else:bad['entries'][0].update(status='passed',exit_code=0)
        with pytest.raises(ValueError):validate_summary(bad,cases)
    assert aggregate(['passed','pending','failed'])=='failed'
    assert aggregate(['passed','pending'])=='pending'


def test_standalone_compare_requires_refinement(tmp_path):
    from ts808_validation.cli import main
    assert main(['compare','--case',str(tmp_path/'case.json'),'--run',str(tmp_path/'run'),'--reference',str(tmp_path/'nominal'),'--output',str(tmp_path/'report')])==31


def test_overflow_json_and_explicit_settling_revisions(tmp_path):
    from ts808_validation.artifacts import validate_case
    p=tmp_path/'nonfinite.json';p.write_text('{"value":1e9999}')
    with pytest.raises(ValueError):load_json(p)
    revisions=load_json(ROOT/'reference/ts808/case_revisions.json')
    for revision in revisions['revisions']:
        validate_case(revision['case'])
        changed=copy.deepcopy(revision['case']);changed['stimulus']['peak_V']*=2
        with pytest.raises(ValueError):validate_case(changed)


def test_recovery_numpy_metric_is_finite_persisted_json(tmp_path):
    from ts808_validation.persist import check
    from ts808_validation.artifacts import atomic_json
    p=tmp_path/'check.json';atomic_json(p,check('recovery',np.int64(1),1,'samples'))
    assert load_json(p)['value']==1
    with pytest.raises(ValueError):check('invalid',np.nan,1)


def test_refinement_checks_actual_options_not_labels():
    from ts808_validation.compare import validate_native_refinement
    from ts808_validation.simulator import native_options
    from ts808_validation.cli import make_deck
    c=next(c for c in load_json(ROOT/'reference/ts808/cases.json')['cases'] if c['analysis_kind']=='transient')
    n=native_options(make_deck(c));r=native_options(make_deck(c,True));validate_native_refinement(n,r)
    for key,value in [('reltol','1e-6'),('method','gear'),('numdgt','6'),('srcsteps','10'),('gshunt','1e-9'),('solver','alternate')]:
        bad=dict(r);bad[key]=value
        with pytest.raises(ValueError):validate_native_refinement(n,bad)
