"""Keep the targeted remedy scoped to qualified paired WAV failures."""
import runpy
import pytest
from ts808_validation.artifacts import ROOT


def test_final_remedy_rejects_changed_scope(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'validation/scripts'))
    module = runpy.run_path(str(ROOT/'validation/scripts/repair_remaining_wav.py'))
    case = dict(case_id=module['CASE'])
    manifest = dict(cases=[case])
    assessment = dict(assessment_completion='completed', entry_count=128, entries=[
        dict(case_id=case['case_id'], rate_Hz=rate,
             outcomes=dict(reference='passed', numerical='passed', wav='failed'),
             failed_checks=[dict(id='wav_reference_uncertainty_rms')]) for rate in (192000,384000)])
    assert module['select_case'](assessment, manifest) == [case]
    assessment['entries'][0]['outcomes']['numerical'] = 'failed'
    with pytest.raises(ValueError):
        module['select_case'](assessment, manifest)
    assessment['assessment_completion'] = 'incomplete'
    with pytest.raises(ValueError):
        module['select_case'](assessment, manifest)
