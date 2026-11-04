import uuid
from pathlib import Path
import numpy as np
from ts808_validation.artifacts import ROOT,load_json,atomic_json
from ts808_validation.simulator import prepare_request,run_request
from ts808_validation.reference import read_native
from ts808_validation.persist import check,original_source
cfg=load_json(ROOT/'validation/toolchain.json');d=Path(cfg['workspace']['wsl_root'])/('opamp-ac-'+uuid.uuid4().hex);cp=ROOT/'runs/mvp-qualification/audit-case.json'
prepare_request(ROOT/'reference/ts808',cp,d,request_id=d.name,settings=dict(level='nominal',maxstep_s=1/(384000*8),dc_protocol='Independent standalone opamp AC fixture, not pedal reference'),deck=(ROOT/'reference/ts808/check_opamp_ac.cir').read_text());run_request(d,Path(cfg['tools']['ltspice']['path']));original_source(d,cfg)
r=read_native(d/'deck.raw',d/'deck.log',analysis_kind='ac',trace_names=['V(out2k)','V(out10k)','V(xa:z)','V(xb:z)']);f=r['axis'];g=100000/(1+1j*f/30);ro=10000/51;rid=5e6;checks=[]
for name,channel,resistance in [('out2k','a',2000),('out10k','b',10000)]:
    expected=(g+ro/rid)/(g+1+ro/resistance+ro/rid);actual=r['traces']['V('+name+')'];ratio=actual/expected
    checks.extend([check(name+'_magnitude_error',float(max(abs(20*np.log10(abs(ratio))))),.02,'dB'),check(name+'_phase_error',float(max(abs(np.angle(ratio,deg=True)))),.2,'deg')])
    z=g*(1-expected);checks.append(check(name+'_state_complex_relative',float(max(abs(r['traces'][f'V(x{channel}:z)']-z)/np.maximum(abs(z),1e-12))),1e-6,'relative'))
atomic_json(ROOT/'runs/mvp-qualification/opamp-ac-qualification.json',dict(directory=str(d),point_count=r['point_count'],scope='Independent finite-A0, GBW and loaded follower/state AC law; not complete pedal AC',checks=checks,status='passed' if all(c['status']=='passed' for c in checks) else 'failed'));print(checks,flush=True)
