"""Prevent the targeted native remedy from hiding unrelated rejections."""
import copy
import runpy

import pytest

from ts808_validation.artifacts import ROOT, load_json


def inputs():
    root = ROOT/'validation/results/settling-requalification-2026-11-06-r4'
    assessment = load_json(root/'qualification.json')
    # Cases remain repo-native; this unit check does not require the F: volume.
    catalog = load_json(ROOT/'reference/ts808/cases.json')
    revisions = load_json(ROOT/'reference/ts808/case_revisions.json')['revisions']
    replacements = {r['base_case_id']:r['case'] for r in revisions}
    catalog['cases'] = [copy.deepcopy(replacements.get(c['case_id'],c)) for c in catalog['cases']]
    function = runpy.run_path(str(ROOT/'validation/scripts/requalify_wav_references.py'))['rejected_cases']
    return function, assessment, catalog


def test_wav_remedy_selects_only_paired_failures_without_changing_cases():
    function, assessment, manifest = inputs()
    before = copy.deepcopy(manifest)
    selected = function(assessment, manifest)
    assert len(selected) == 11
    assert manifest == before
    assert {c['case_id'] for c in selected} == {
        e['case_id'] for e in assessment['entries'] if e['outcomes']['wav']=='failed'}
    selected[0]['circuit']['unexpected'] = True
    assert manifest == before


@pytest.mark.parametrize('corruption', ['numerical', 'unpaired', 'check', 'missing_case'])
def test_wav_remedy_blocks_unrelated_or_incomplete_evidence(corruption):
    function, assessment, manifest = inputs()
    entry = next(e for e in assessment['entries'] if e['outcomes']['wav']=='failed')
    if corruption == 'numerical':
        entry['outcomes']['numerical'] = 'failed'
    elif corruption == 'unpaired':
        assessment['entries'].remove(entry)
    elif corruption == 'check':
        entry['failed_checks'].append(dict(id='cpp_settling_dc'))
    else:
        manifest['cases'] = [c for c in manifest['cases'] if c['case_id']!=entry['case_id']]
    with pytest.raises(ValueError):
        function(assessment, manifest)
