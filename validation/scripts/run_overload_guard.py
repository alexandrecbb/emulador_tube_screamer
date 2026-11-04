import uuid
from pathlib import Path
from ts808_validation.artifacts import ROOT,load_json,atomic_json
from ts808_validation.simulator import prepare_request,run_request
from ts808_validation.cli import make_deck,doctor
cfg=load_json(ROOT/'validation/toolchain-pilot-f.json');cp=ROOT/'runs/mvp-pilots-02/overload_high/case.json';case=load_json(cp)
if doctor(ROOT/'validation/toolchain-pilot-f.json')['status']!='passed':raise ValueError('F root doctor failed')
for refined in (False,True):
 level='refined' if refined else 'nominal';d=Path(cfg['workspace']['wsl_root'])/('overload-high-alt-guard-'+level+'-'+uuid.uuid4().hex)
 deck=make_deck(case,refined).replace('.temp 25','.temp 25\n.options solver=alt')
 prepare_request(ROOT/'reference/ts808',cp,d,request_id=d.name,settings=dict(level=level,maxstep_s=1/(384000*8*(2 if refined else 1)),dc_protocol='solver=alt; gminsteps=0 srcsteps=0; endpoint guard of one maxstep'),deck=deck)
 atomic_json(cp.parent/(level+'-alt-guard-request.json'),dict(directory=str(d),toolchain='validation/toolchain-pilot-f.json'))
 print(d,flush=True);print(run_request(d,Path(cfg['tools']['ltspice']['path']))['completion'],flush=True)
