import copy,subprocess,time
from ts808_validation.artifacts import ROOT,load_json,atomic_json,finalize_run
base=load_json(ROOT/'runs/mvp-pilots-02/overload_high/192000/case.json');case=copy.deepcopy(base)
for key in ('atol_current_A','atol_voltage_V','rtol_residual','atol_increment_current_A','atol_increment_voltage_V','rtol_increment'):case['execution']['solver'][key]/=10
p=ROOT/'runs/mvp-qualification/overload-192000-tighter10';p.mkdir(exist_ok=True);atomic_json(p/'case.json',case)
t=time.monotonic();r=subprocess.run([str(ROOT/'build/offline-release/ts808_offline'),'--case',str(p/'case.json'),'--output',str(p/'run')],capture_output=True)
atomic_json(p/'execution.json',dict(elapsed_s=time.monotonic()-t,exit_code=r.returncode,stderr=r.stderr.decode(),scope='Separately identified diagnostic, not replacement of a failed target case'))
if r.returncode==0:finalize_run(p/'run',p/'case.json',ROOT/'build/offline-release/ts808_offline')
print(r.returncode,r.stderr.decode(),flush=True)
