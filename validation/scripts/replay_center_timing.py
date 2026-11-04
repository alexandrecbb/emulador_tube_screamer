"""Restore missing monotonic pilot timings by a bit-identical temporary replay."""
import subprocess,tempfile,time
from pathlib import Path
from ts808_validation.artifacts import ROOT,load_json,atomic_json,finalize_run
p=ROOT/'runs/mvp-revised-pilots-norm/tone_center_f1000_a100mv-warmup2s';rows=[]
for rate in (192000,384000):
    target=p/str(rate)
    with tempfile.TemporaryDirectory(prefix='ts808-timing-') as temp:
        output=Path(temp)/'run';start=time.monotonic();r=subprocess.run([str(ROOT/'build/offline-release/ts808_offline'),'--case',str(target/'case.json'),'--output',str(output)],capture_output=True);elapsed=time.monotonic()-start
        if r.returncode:raise RuntimeError(r.stderr.decode())
        replay=finalize_run(output,target/'case.json',ROOT/'build/offline-release/ts808_offline');original=load_json(target/'run/run.json')
        if replay['trace']['sha256']!=original['trace']['sha256']:raise ValueError('Timing replay changed trace bytes')
        row=dict(rate_Hz=rate,elapsed_s=elapsed,exit_code=0,trace_sha256=replay['trace']['sha256'],sample_count=replay['trace']['shape'][0],byte_length=replay['trace']['byte_length'],measurement_kind='monotonic timing replay with bit-identical trace; temporary duplicate payload removed');rows.append(row);atomic_json(target/'execution-measurement.json',row);print(row,flush=True)
atomic_json(p/'timing-replay.json',dict(measurements=rows))
