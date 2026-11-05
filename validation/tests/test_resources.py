from ts808_validation.resources import estimate
from ts808_validation.artifacts import ROOT,load_json


def test_storage_plan_covers_export_producers_and_model_traces():
    cases=load_json(ROOT/'reference/ts808/cases.json')['cases']
    plan=estimate(cases)
    assert plan['minimum_numerical_reference_bytes']==93664051200
    assert plan['minimum_export_raw_bytes']>0
    assert plan['model_trace_bytes']>0
    assert plan['native_required_bytes']>plan['minimum_numerical_reference_bytes']+plan['minimum_export_raw_bytes']+plan['pcm_payload_bytes']
    assert plan['output_required_bytes']>=plan['model_trace_bytes']
    longer=[dict(c,analysis=dict(c['analysis'],time=dict(c['analysis']['time'],duration_s=2*c['analysis']['time']['duration_s']))) if c['analysis_kind']=='transient' else c for c in cases]
    assert estimate(longer)['estimated_required_bytes']>plan['estimated_required_bytes']
