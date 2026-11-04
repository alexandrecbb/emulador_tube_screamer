from pathlib import Path
import tempfile
import numpy as np
import pytest
from scipy.io import wavfile
from ts808_validation.abx import prepare_session,evaluate_family
from ts808_validation.artifacts import atomic_json,load_json
from ts808_validation.simulator import sha256


def test_gates_blinding_and_missing_humans():
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp);a=root/'a.wav';b=root/'b.wav';x=np.full(167872,.01,dtype=np.float32)
        wavfile.write(a,48000,x);wavfile.write(b,48000,x*.99)
        report=dict(case_id='listen_high',physical_case_sha256='a'*64,execution_config={'rate_Hz':384000},outcomes={k:'pending' for k in ('reference','numerical','wav')},artifacts=[dict(status='generated',sha256=sha256(p)) for p in (a,b)])
        rp=root/'report.json';atomic_json(rp,report)
        with pytest.raises(ValueError):prepare_session(rp,a,b,root/'blocked','listener',seed=42)
        assert not (root/'blocked').exists()
        report['outcomes']={k:'passed' for k in ('reference','numerical','wav')};atomic_json(rp,report)
        s=prepare_session(rp,a,b,root/'session','listener',seed=42)
        assert len(s['trials'])==20 and all(t['response'] is None for t in s['trials'])
        assert not any(word in str(s).lower() for word in ('answer','seed','mapping','cpp','reference'))
        with pytest.raises(ValueError):evaluate_family([(root/'session/blinded/session.json',root/'session/private/key.json')],'primary')


def test_blinded_file_hashes_do_not_reveal_assignments(tmp_path):
    from scipy.io import wavfile
    from ts808_validation.artifacts import atomic_json
    from ts808_validation.simulator import sha256
    a=tmp_path/'a.wav';b=tmp_path/'b.wav'
    wavfile.write(a,48000,np.full(167872,.01,dtype=np.float32));wavfile.write(b,48000,np.full(167872,.02,dtype=np.float32))
    rp=tmp_path/'report.json';atomic_json(rp,dict(case_id='listen_high',physical_case_sha256='a'*64,execution_config={'rate_Hz':384000},outcomes={k:'passed' for k in ('reference','numerical','wav')},artifacts=[dict(status='generated',sha256=sha256(p)) for p in (a,b)]))
    s=prepare_session(rp,a,b,tmp_path/'blind','listener',seed=11)
    assert len({f['sha256'] for f in s['artifacts']})==22
    key=load_json(tmp_path/'blind/private/key.json')
    for index,assignment in enumerate(key['assignments'],1):
        _,actual=wavfile.read(tmp_path/'blind/blinded'/f'X{index:02}.wav')
        _,expected=wavfile.read(tmp_path/'blind/blinded'/(assignment['answer']+'.wav'))
        np.testing.assert_array_equal(actual,expected)
