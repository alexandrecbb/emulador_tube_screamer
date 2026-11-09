"""A longer operational deadline must reach both launcher and native helper."""
import json

import pytest

from ts808_validation import simulator


@pytest.mark.parametrize('seconds', [1800, 7200])
def test_native_deadline_is_consistent(tmp_path, monkeypatch, seconds):
    monkeypatch.setenv('TS808_NATIVE_TIMEOUT_S', str(seconds))
    (tmp_path/'request.json').write_text(json.dumps(dict(inputs=[])))
    monkeypatch.setattr(simulator, 'windows_path', str)
    observed = {}

    class Process:
        returncode = 30
        args = []

        def communicate(self, timeout):
            observed['timeout'] = timeout
            return b'', b'timeout'

    def launch(args, **kwargs):
        observed['args'] = args
        return Process()

    monkeypatch.setattr(simulator.subprocess, 'Popen', launch)
    with pytest.raises(RuntimeError, match='Native producer failed'):
        simulator._run_request(tmp_path, tmp_path/'LTspice.exe')
    assert observed['timeout'] == seconds+30
    if seconds == 1800:
        assert '-TimeoutMilliseconds' not in observed['args']
        assert not (tmp_path/'launch-policy.json').exists()
    else:
        assert observed['args'][-2:] == ['-TimeoutMilliseconds', str(seconds*1000)]
        assert json.loads((tmp_path/'launch-policy.json').read_text())['request_sha256'] == simulator.sha256(tmp_path/'request.json')


@pytest.mark.parametrize('value', ['0', '-1', '21601', 'bad'])
def test_invalid_deadline_is_rejected(monkeypatch, value):
    monkeypatch.setenv('TS808_NATIVE_TIMEOUT_S', value)
    with pytest.raises(ValueError):
        simulator.native_timeout_seconds()
