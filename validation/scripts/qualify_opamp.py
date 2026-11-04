import numpy as np
from scipy.integrate import solve_ivp
from pathlib import Path
from ts808_validation.artifacts import ROOT,load_json,atomic_json
from ts808_validation.reference import read_native
from ts808_validation.reconstruct import pchip
from ts808_validation.persist import check,original_source
from ts808_validation.metrics import rms
source=Path(load_json(ROOT/'runs/mvp-qualification/opamp-scaled-transient-source.json')['directory'])
original_source(source,load_json(ROOT/'validation/toolchain.json'))
names=[f'V(x{s}{r}:z)' for s in ('p','n') for r in (2000,10000)]+[f'V(out_{s}{r})' for s in ('p','n') for r in (2000,10000)]
raw=read_native(source/'deck.raw',source/'deck.log',analysis_kind='transient',trace_names=names)
H=4.5-37/51;L=H-.25
# Independent scalar ODE, no C++ or native model implementation is imported.
def sat(z):return z if abs(z)<=L else np.copysign(L+.25*np.tanh((abs(z)-L)/.25),z)
def envelope(t):
 if t<.1 or t>=.2:return 0.
 if t<.105:return .5*(1-np.cos(np.pi*(t-.1)/.005))
 if t<.195:return 1.
 return .5*(1-np.cos(np.pi*(.2-t)/.005))
def law(t,z):return [1e6*np.tanh((2*np.pi*30*(1e5*.1*envelope(t)-z[0])-(z[0]-sat(z[0]))/1e-5)/1e6)]
solutions=[]
for tol in (1e-10,1e-12):
 solutions.append(solve_ivp(law,(0,.5),[0.],method='DOP853',rtol=tol,atol=tol*.01,max_step=.0002,dense_output=True))
t=np.arange(96001)/192000;z=solutions[-1].sol(t)[0];unc=solutions[0].sol(t)[0]-z;checks=[check('independent_ode_refinement_rms',rms(unc),1e-7,'V'),check('independent_ode_refinement_peak',float(max(abs(unc))),1e-6,'V')]
for s,sign in [('p',1),('n',-1)]:
 for r in (2000,10000):
  state=pchip(raw['axis'],raw['traces'][f'V(x{s}{r}:z)'],t);output=pchip(raw['axis'],raw['traces'][f'V(out_{s}{r})'],t)
  ideal=sign*z;out=np.array([(4.5+sat(v))/(1+(10000/51)/r) for v in ideal])
  checks.extend([check(f'{s}{r}_state_peak',float(max(abs(state-ideal))),1e-5,'V'),check(f'{s}{r}_output_peak',float(max(abs(output-out))),1e-5,'V')])
atomic_json(ROOT/'runs/mvp-qualification/opamp-qualification.json',dict(source_directory=str(source),point_count=raw['point_count'],dc_solver=raw['dc_solver'],checks=checks,status='passed' if all(c['status']=='passed' for c in checks) else 'failed',scope='Independent state integration, signed overload/recovery and 2k/10k loading; not full pedal acceptance'))
print(checks,flush=True)
