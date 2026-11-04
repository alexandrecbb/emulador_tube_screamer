"""Record actual final check outputs without treating environment as accuracy."""
import os,subprocess,time,datetime
from ts808_validation.artifacts import ROOT,atomic_json
from ts808_validation.simulator import sha256
out=ROOT/'validation/results/mvp-2026-11-04';out.mkdir(parents=True,exist_ok=True)
env=dict(os.environ,PYTHONPATH=str(ROOT/'validation'),TS808_NATIVE_TESTS='1');rows=[]
commands=[('doctor-c',['.venv/bin/python','-m','ts808_validation','doctor','--toolchain','validation/toolchain.json']),('doctor-f',['.venv/bin/python','-m','ts808_validation','doctor','--toolchain','validation/toolchain-pilot-f.json']),('ctest-checked',['.tools/cmake-4.4.5-linux-x86_64/bin/ctest','--preset','offline-checks']),('ctest-release',['.tools/cmake-4.4.5-linux-x86_64/bin/ctest','--preset','offline-release']),('pytest-native',['.venv/bin/python','-m','pytest','validation/tests','-q'])]
for name,command in commands:
    start=time.monotonic();r=subprocess.run(command,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);path=out/(name+'.log');path.write_text(r.stdout)
    rows.append(dict(name=name,command=command,exit_code=r.returncode,elapsed_s=time.monotonic()-start,log=path.name,sha256=sha256(path)));atomic_json(out/'verification.json',dict(recorded_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),checks=rows,status='passed' if all(c['exit_code']==0 for c in rows) else 'failed',scope='Tests/environment only; numerical MVP outcomes are recorded separately'))
    print(name,r.returncode,r.stdout.splitlines()[-1:] if r.stdout else [],flush=True)
    if r.returncode:raise SystemExit(r.returncode)
