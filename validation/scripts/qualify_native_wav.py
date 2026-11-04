"""Native PCM32 fixture: writer simulation covers exactly the required frame grid.

The independent numerical reference includes t=T. Export-only requests stop at
T-h/2, after the last frame T-h and before excluded endpoint T. No WAV is trimmed.
"""
from pathlib import Path
import uuid,shutil
import numpy as np
from ts808_validation.artifacts import ROOT,load_json,atomic_json
from ts808_validation.simulator import prepare_request,run_request,sha256
from ts808_validation.reference import read_native
from ts808_validation.reconstruct import pchip
from ts808_validation.wave_audio import qualify_native

cfg=load_json(ROOT/'validation/toolchain.json');cp=ROOT/'runs/mvp-qualification/audit-case.json';base=(ROOT/'validation/tests/fixtures/ltspice26_tran64.cir').read_text();sources={}
for name,rate in [('refined',None),('pcm192',192000),('pcm384',384000)]:
    d=Path(cfg['workspace']['wsl_root'])/('wav-qualified-'+name+'-'+uuid.uuid4().hex);deck=base
    if rate is None:
        deck=deck.replace('3.2552083333333332e-07','1.6276041666666666e-07').replace('reltol=1e-6','reltol=1e-7').replace('abstol=1e-12','abstol=1e-13').replace('vntol=1e-9','vntol=1e-10').replace('chgtol=1e-16','chgtol=1e-17')
    else:
        stop=.004-.5/rate
        deck=deck.replace('.tran 0 0.004',f'.tran 0 {stop:.17g}').replace('.save ','.save V(wav_export) ').replace('.end',f'Bwav wav_export 0 V={{V(output)/8}}\n.wave pcm.wav 32 {rate} V(wav_export)\n.end')
    request=prepare_request(ROOT/'reference/ts808',cp,d,request_id=d.name,settings=dict(purpose='RC native WAV qualification fixture',rate_Hz=rate,physical_duration_s=.004,wav_domain='[0,T)',transient_stop_s=.004 if rate is None else stop),deck=deck)
    if rate is not None:request['expected_outputs'].append('pcm.wav');atomic_json(d/'request.json',request)
    run_request(d,Path(cfg['tools']['ltspice']['path']));sources[name]=d;print(name,d,flush=True)
nominal_dir=Path(load_json(ROOT/'runs/mvp-qualification/wav-fixture-source.json')['directory'])
nominal=read_native(nominal_dir/'deck.raw',nominal_dir/'deck.log',analysis_kind='transient',trace_names=['V(output)'])
refined=read_native(sources['refined']/'deck.raw',sources['refined']/'deck.log',analysis_kind='transient',trace_names=['V(output)']);rows=[]
for name,rate in [('pcm192',192000),('pcm384',384000)]:
    t=np.arange(round(.004*rate))/rate;n=pchip(nominal['axis'],nominal['traces']['V(output)'],t);r=pchip(refined['axis'],refined['traces']['V(output)'],t)
    checks=qualify_native(sources[name]/'pcm.wav',n,r,rate);rows.append(dict(rate_Hz=rate,source_directory=str(sources[name]),checks=checks))
    for filename in ('deck.cir','deck.raw','deck.log','pcm.wav'):
        shutil.copyfile(sources[name]/filename,ROOT/'validation/tests/fixtures'/('wav_qualified_'+name+'_'+filename))
atomic_json(ROOT/'runs/mvp-qualification/native-wav-qualified.json',dict(results=rows,refined_directory=str(sources['refined']),nominal_directory=str(nominal_dir),scope='RC native export path; not pedal or listening qualification'))
print([(r['rate_Hz'],all(c['status']=='passed' for c in r['checks'])) for r in rows],flush=True)
