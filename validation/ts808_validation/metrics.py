"""Frozen T8/T18 voltage, response and time-domain gates."""
import numpy as np
from .persist import check


def rms(x): return float(np.sqrt(np.mean(np.square(np.abs(x)))))


def null_checks(prefix, actual, reference, budget=1.):
    error=actual-reference; rr=rms(reference); rp=float(np.max(np.abs(reference)))
    return [check(prefix+'_rms',rms(error),budget*(1e-6 if rr<1e-3 else rr*1e-3),'V'),
            check(prefix+'_peak',float(np.max(np.abs(error))),budget*(1e-5 if rr<1e-3 else rp*1e-2),'V')]


def bode_checks(prefix, actual, reference, budget=1.):
    mask=np.abs(reference)>=1e-6; checks=[]
    if np.any(mask):
        ratio=actual[mask]/reference[mask]
        checks += [check(prefix+'_magnitude',float(np.max(np.abs(20*np.log10(np.abs(ratio))))),.2*budget,'dB'),
                   check(prefix+'_phase',float(np.max(np.abs(np.angle(ratio,deg=True)))),2*budget,'deg')]
    if np.any(~mask): checks += [check(prefix+'_complex_floor',float(np.max(np.abs(actual[~mask]-reference[~mask]))),1e-6*budget,'V/V')]
    return checks


def local_checks(prefix, actual, reference, rate, budget=1.):
    size=round(.020*rate); checks=[]
    for start in range(0,len(actual)-1,size):
        stop=min(start+size,len(actual)-1)
        checks.extend(null_checks(f'{prefix}_{start}_{stop}',actual[start:stop],reference[start:stop],budget))
    return checks


def spectrum(signal,rate,frequency):
    n=len(signal); bins=np.arange(1,int(20000//frequency)+1)*frequency*n/rate
    if np.max(np.abs(bins-np.round(bins)))>1e-8: raise ValueError('Noncoherent steady FFT')
    return 2*np.fft.rfft(signal)[np.round(bins).astype(int)]/n


def harmonic_checks(actual,reference,uncertainty,rate,frequency):
    a=spectrum(actual,rate,frequency);r=spectrum(reference,rate,frequency);u=spectrum(uncertainty,rate,frequency)
    resolved=(np.abs(r)>np.abs(r[0])*1e-4)&(np.abs(r)>10*np.abs(u));checks=[]
    for k in np.flatnonzero(resolved):
        checks.append(check(f'harmonic_{k+1}',float(abs(20*np.log10(abs(a[k]/r[k])))),1,'dB'))
    at=float(np.linalg.norm(a[1:])/abs(a[0]));rt=float(np.linalg.norm(r[1:])/abs(r[0]));floor=max(1e-5,float(np.linalg.norm(u[1:])/abs(r[0])))
    checks.append(check('thd',abs(at-rt)/rt if rt>floor else abs(at-rt),.05 if rt>floor else floor,'relative' if rt>floor else 'absolute',reason=f'Reference THD={rt}; uncertainty floor={floor}'))
    return checks


def fitted_harmonics(y,t,f):
    k=np.arange(1,int(20000//f)+1);angle=2*np.pi*t[:,None]*f*k
    matrix=np.column_stack((np.ones(len(t)),np.sin(angle),np.cos(angle)))
    c=np.linalg.lstsq(matrix,y,rcond=None)[0];a=c[1:len(k)+1]+1j*c[len(k)+1:]
    return c[0],a,float(np.linalg.norm(a[1:])/abs(a[0]))


def settling_checks(y,t,f,prefix):
    mid=len(y)//2; d,a,thd=fitted_harmonics(y,t,f);d1,a1,h1=fitted_harmonics(y[:mid],t[:mid],f);d2,a2,h2=fitted_harmonics(y[mid:],t[mid:],f)
    return [check(prefix+'_fundamental',float(abs(a1[0]-a2[0])/abs(a[0])),.001,'relative'),check(prefix+'_dc',float(abs(d1-d2)),1e-5,'V'),
            check(prefix+'_thd',abs(h1-h2)/thd if thd>1e-5 else abs(h1-h2),.01 if thd>1e-5 else 1e-5,'relative' if thd>1e-5 else 'absolute')]


def recovery_index(data,names,rate):
    columns=[names.index(n)+1 for n in ('output','vref','input_base','output_base')]
    limits=np.array([.001,.01,.01,.01]);inside=np.all(abs(data[:,columns]-data[0,columns])<=limits,axis=1)
    sustain=round(.01*rate);start=round(.2*rate)
    bad=np.flatnonzero(~inside[start:])+start
    candidate=start
    for b in bad:
        if b-candidate>=sustain:return candidate
        candidate=b+1
    return candidate if len(data)-candidate>=sustain else None
