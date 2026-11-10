"""PCHIP on explicit continuous domains; bounded workspace, no alignment fit."""
import numpy as np
from scipy.interpolate import PchipInterpolator

# Each interval uses the same local derivatives as the full SciPy interpolant.
# Two neighbours on either side preserve interior slopes and true end slopes.
SOURCE_BLOCK = 65536


def pchip(times, values, target, *, discontinuities=()):
    times=np.asarray(times,dtype=np.float64);values=np.asarray(values);target=np.asarray(target,dtype=np.float64)
    if times.ndim!=1 or target.ndim!=1 or values.shape[0]!=len(times) or len(times)<2:
        raise ValueError('Invalid interpolation shapes')
    if np.iscomplexobj(values):
        raise ValueError('Transient PCHIP requires real values')
    for array in (times,values,target):
        for start in range(0,len(array),SOURCE_BLOCK):
            if not np.isfinite(array[start:start+SOURCE_BLOCK]).all():
                raise ValueError('Nonfinite interpolation input')
    for array in (times,target):
        for start in range(0,len(array),SOURCE_BLOCK):
            if not np.all(np.diff(array[max(0,start-1):start+SOURCE_BLOCK])>0):
                raise ValueError('Strictly increasing timestamps required')
    if len(target) and (target[0]<times[0] or target[-1]>times[-1]):
        raise ValueError('Extrapolation forbidden')
    boundaries=[times[0],*discontinuities,times[-1]]
    if any(a>=b for a,b in zip(boundaries,boundaries[1:])):
        raise ValueError('Discontinuities must be ordered and inside the domain')
    result=np.empty((len(target),)+values.shape[1:],dtype=np.float64)
    for index,(start,stop) in enumerate(zip(boundaries,boundaries[1:])):
        last=index==len(boundaries)-2
        lo=int(np.searchsorted(times,start));hi=int(np.searchsorted(times,stop,side='right' if last else 'left'))
        a=int(np.searchsorted(target,start));b=int(np.searchsorted(target,stop,side='right' if last else 'left'))
        if a==b:continue
        if hi-lo<2 or target[a]<times[lo] or target[b-1]>times[hi-1]:
            raise ValueError('Insufficient one-sided coverage at discontinuity')
        for left in range(lo,hi-1,SOURCE_BLOCK):
            right=min(left+SOURCE_BLOCK,hi-1)
            ta=max(a,int(np.searchsorted(target,times[left])))
            tb=min(b,int(np.searchsorted(target,times[right],side='right' if right==hi-1 else 'left')))
            if ta==tb:continue
            first=max(lo,left-2);end=min(hi,right+3)
            result[ta:tb]=PchipInterpolator(times[first:end],values[first:end],axis=0,
                                            extrapolate=False)(target[ta:tb])
    return result


def decimation_diagnostic(times, values, target):
    """Same even-sample/end-point leave-out test, with bounded scratch arrays."""
    count=len(times)
    coarse=np.empty(len(target),dtype=np.float64)
    error_sum=reference_sum=error_peak=reference_peak=0.
    samples=0
    for left in range(0,count-1,SOURCE_BLOCK*2):
        right=min(left+SOURCE_BLOCK*2,count-1)
        # left is even; retain two even neighbours on each side for slopes.
        indices=np.arange(max(0,left-4),min(count,right+5),2)
        if right+5>=count and indices[-1]!=count-1:
            indices=np.r_[indices,count-1]
        tx=times[indices];vx=values[indices]
        interpolation=PchipInterpolator(tx,vx,extrapolate=False)
        omitted=np.arange(left+1,right,2)
        if len(omitted):
            reference=values[omitted];error=interpolation(times[omitted])-reference
            error_sum+=float(np.sum(error**2));reference_sum+=float(np.sum(reference**2))
            error_peak=max(error_peak,float(np.max(abs(error))))
            reference_peak=max(reference_peak,float(np.max(abs(reference))))
            samples+=len(omitted)
        a=int(np.searchsorted(target,times[left]))
        b=int(np.searchsorted(target,times[right],side='right' if right==count-1 else 'left'))
        coarse[a:b]=interpolation(target[a:b])
    return dict(error_rms=float(np.sqrt(error_sum/samples)),error_peak=error_peak,
                reference_rms=float(np.sqrt(reference_sum/samples)),reference_peak=reference_peak),coarse
