"""PCHIP on explicit continuous domains; no extrapolation or alignment fit."""
import numpy as np
from scipy.interpolate import PchipInterpolator


def pchip(times, values, target, *, discontinuities=()):
    times=np.asarray(times,dtype=np.float64);values=np.asarray(values);target=np.asarray(target,dtype=np.float64)
    if times.ndim!=1 or target.ndim!=1 or values.shape[0]!=len(times) or len(times)<2:
        raise ValueError('Invalid interpolation shapes')
    if not (np.isfinite(times).all() and np.isfinite(values).all() and np.isfinite(target).all()):
        raise ValueError('Nonfinite interpolation input')
    if not np.all(np.diff(times)>0) or (len(target)>1 and not np.all(np.diff(target)>0)):
        raise ValueError('Strictly increasing timestamps required')
    if len(target) and (target[0]<times[0] or target[-1]>times[-1]):
        raise ValueError('Extrapolation forbidden')
    if np.iscomplexobj(values):
        raise ValueError('Transient PCHIP requires real values')
    boundaries=[times[0],*discontinuities,times[-1]]
    if any(a>=b for a,b in zip(boundaries,boundaries[1:])):
        raise ValueError('Discontinuities must be ordered and inside the domain')
    result=np.empty((len(target),)+values.shape[1:],dtype=np.float64)
    for index,(start,stop) in enumerate(zip(boundaries,boundaries[1:])):
        # A discontinuity belongs to its right side. Never use its right-hand value on the left.
        last=index==len(boundaries)-2
        source_mask=(times>=start)&((times<=stop) if last else (times<stop))
        target_mask=(target>=start)&((target<=stop) if last else (target<stop))
        if not np.any(target_mask): continue
        tx=times[source_mask]
        if len(tx)<2 or target[target_mask][0]<tx[0] or target[target_mask][-1]>tx[-1]:
            raise ValueError('Insufficient one-sided coverage at discontinuity')
        result[target_mask]=PchipInterpolator(tx,values[source_mask],axis=0,extrapolate=False)(target[target_mask])
    return result
