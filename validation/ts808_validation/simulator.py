"""Local WSL/native Windows producer. Completion is separate from accuracy."""
from __future__ import annotations

import hashlib
import errno
import time
import re
import json
from pathlib import Path
import shutil
import subprocess


def sha256(path: Path) -> str:
    digest=hashlib.sha256()
    with path.open('rb',buffering=0) as stream:
        while True:
            position=stream.tell()
            for attempt in range(4):
                try:
                    block=stream.read(65536)
                    break
                except OSError as error:
                    if error.errno!=errno.ENOMEM or attempt==3:raise
                    stream.seek(position);time.sleep(.05*(attempt+1))
            if not block:break
            digest.update(block)
    return digest.hexdigest()


def confined(root: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or '\\' in relative or ':' in relative:
        raise ValueError('Expected a portable relative path')
    result = (root / path).resolve()
    if not result.is_relative_to(root.resolve()) or result == root.resolve():
        raise ValueError('Path escapes root')
    return result


def windows_path(path: Path) -> str:
    return subprocess.check_output(['wslpath', '-w', str(path.resolve())], text=True).strip()


def native_options(deck: str) -> dict:
    options={}
    for line in deck.splitlines():
        line=line.strip()
        if line.lower().startswith('.options '):
            for key,value in re.findall(r'([a-zA-Z_][a-zA-Z_0-9]*)=([^\s]+)',line):options[key.lower()]=value
        elif line.lower().startswith('.temp '):options['temp']=line.split()[1]
    return options


def prepare_request(source: Path, case_path: Path, destination: Path, *,
                    request_id: str, settings: dict, deck: str) -> dict:
    """Stage immutable small inputs in a NEW shared-drive directory."""
    case = json.loads(case_path.read_text())
    settings=dict(settings,native_options=native_options(deck))
    destination.mkdir(parents=True, exist_ok=False)
    for name in ('models.lib', 'component_map.json', 'device_spec.md', 'run_reference.ps1'):
        shutil.copyfile(source / name, destination / name)
    shutil.copyfile(case_path, destination / 'case.json')
    (destination / 'deck.cir').write_text(deck, encoding='utf-8')
    inputs = [dict(path=name, size_bytes=(destination / name).stat().st_size,
                   sha256=sha256(destination / name)) for name in
              ('deck.cir', 'models.lib', 'case.json', 'component_map.json',
               'device_spec.md', 'run_reference.ps1')]
    request = dict(schema_version=1, request_id=request_id, case_id=case['case_id'],
                   physical_case_sha256=case['physical_case_sha256'],
                   analysis_kind=case['analysis_kind'], reference_settings=settings,
                   inputs=inputs, expected_outputs=['deck.raw', 'deck.log'],
                   trace_map=json.loads((source / 'component_map.json').read_text())['trace_map'])
    (destination / 'request.json').write_text(json.dumps(request, indent=2, allow_nan=False)+'\n')
    return request


def run_request(request_directory: Path, executable: Path) -> dict:
    import fcntl
    lock_path=Path(__file__).resolve().parents[2]/'runs/native-producer.lock'
    lock_path.parent.mkdir(exist_ok=True)
    with lock_path.open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        return _run_request(request_directory,executable)


def _run_request(request_directory: Path, executable: Path) -> dict:
    request_path = request_directory / 'request.json'
    request_hash = sha256(request_path)
    request = json.loads(request_path.read_text())
    for entry in request['inputs']:
        path = confined(request_directory, entry['path'])
        if path.stat().st_size != entry['size_bytes'] or sha256(path) != entry['sha256']:
            raise ValueError('Staged input identity mismatch')
    # Native helper owns timeout and PID tree. A launcher failure cannot imply completion.
    process = subprocess.Popen([
        'powershell.exe', '-NoProfile', '-NonInteractive', '-File',
        windows_path(request_directory / 'run_reference.ps1'),
        '-RequestDirectory', windows_path(request_directory),
        '-ExecutablePath', windows_path(executable),
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = process.communicate(timeout=1830)
    except (subprocess.TimeoutExpired, KeyboardInterrupt):
        (request_directory/'cancel.requested').write_text('Caller cancellation; helper owns native PID tree\n')
        stdout, stderr = process.communicate(timeout=30)
        raise RuntimeError('Cancelled reference; finalized helper result retained')
    completed = subprocess.CompletedProcess(process.args, process.returncode, stdout, stderr)
    if completed.returncode != 0:
        raise RuntimeError(f'Native producer failed ({completed.returncode}): '
                           + completed.stderr.decode('utf-8', errors='replace'))
    result = json.loads((request_directory / 'reference_result.json').read_text(encoding='utf-8'))
    if (result['completion'] != 'completed' or result['request_sha256'] != request_hash
            or result['request_id'] != request['request_id']
            or result['physical_case_sha256'] != request['physical_case_sha256']
            or sha256(request_path) != request_hash):
        raise ValueError('Incomplete or mismatched producer result')
    if result['producer']['executable_sha256'] != sha256(executable):
        raise ValueError('Producer executable identity changed')
    expected = set(request['expected_outputs'])
    if {e['path'] for e in result['files']} != expected:
        raise ValueError('Unexpected native output set')
    for entry in result['files']:
        path = confined(request_directory, entry['path'])
        if path.stat().st_size != entry['size_bytes'] or sha256(path) != entry['sha256']:
            raise ValueError('Native output identity mismatch')
    return result
