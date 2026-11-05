import copy
import json
import subprocess

import numpy as np
import pytest

from ts808_validation.artifacts import ROOT, configure_substeps, finalize_run, load_json, validate_case
from ts808_validation.persist import validate_schema

BINARY=ROOT/'build/offline-checks/ts808_offline'


def case_named(name):
    return copy.deepcopy(next(c for c in load_json(ROOT/'reference/ts808/cases.json')['cases'] if c['case_id']==name))


def execute(root,case):
    root.mkdir()
    path=root/'case.json'
    path.write_text(json.dumps(case))
    result=subprocess.run([str(BINARY),'--case',str(path),'--output',str(root/'run')],capture_output=True)
    return result,path


@pytest.mark.parametrize('rate,steps',[(192000,4),(384000,2)])
def test_ac_uses_internal_rate_and_preserves_execution_identity(tmp_path,rate,steps):
    case=configure_substeps(case_named('ac_d050_t050_v050'),rate)
    validate_case(case)
    result,path=execute(tmp_path/'substeps',case)
    assert result.returncode==0,result.stderr
    run=finalize_run(path.parent/'run',path,BINARY)
    validate_schema('run',run)
    assert run['execution_config']['substeps']==steps
    assert run['execution_config']['integration_rate_Hz']==768000
    direct=case_named('ac_d050_t050_v050')
    direct['execution'].update(rate_Hz=768000,purpose='pilot')
    result,other=execute(tmp_path/'direct',direct)
    assert result.returncode==0,result.stderr
    assert (path.parent/'run/response.f64le').read_bytes()==(other.parent/'run/response.f64le').read_bytes()
    run['execution_config']['substeps']=1
    run['execution_config']['integration_rate_Hz']=rate
    (path.parent/'run/run.json').write_text(json.dumps(run))
    with pytest.raises(ValueError,match='integration configuration'):
        finalize_run(path.parent/'run',path,BINARY)


@pytest.mark.parametrize('changes',[{'substeps':4},{'integration_rate_Hz':768000},
                                  {'substeps':2,'integration_rate_Hz':384000},
                                  {'substeps':4,'integration_rate_Hz':192000},
                                  {'substeps':True,'integration_rate_Hz':192000}])
def test_invalid_substep_pairs_are_rejected_before_output(tmp_path,changes):
    case=case_named('dc_d050_t050_v050')
    case['execution'].update(changes)
    with pytest.raises(Exception):validate_case(case)
    result,path=execute(tmp_path/'invalid',case)
    assert result.returncode==10
    assert not (path.parent/'run').exists()


def test_failed_internal_step_never_publishes_partial_output_sample(tmp_path):
    case=configure_substeps(case_named('overload_high'),192000)
    case['execution']['solver']['max_newton_transient']=1
    result,path=execute(tmp_path/'failed',case)
    assert result.returncode==21,result.stderr
    run=load_json(path.parent/'run/run.json')
    failure=load_json(path.parent/'run/failure.json')
    validate_schema('failure',failure)
    diag=failure['diagnostics']
    external=failure['failed_sample_index']
    internal=diag['failed_internal_sample_index']
    assert (external-1)*4<internal<=external*4
    assert diag['failed_substep_index']==(internal-1)%4+1
    assert diag['failed_internal_time_s']==internal/768000
    trace=np.fromfile(path.parent/'run/traces.f64le',dtype='<f8').reshape(-1,32)
    assert len(trace)==external==run['completion']['written_samples']
    assert trace[-1,0]==(external-1)/192000
    with pytest.raises(ValueError,match='Failed/incomplete'):
        finalize_run(path.parent/'run',path,BINARY)
