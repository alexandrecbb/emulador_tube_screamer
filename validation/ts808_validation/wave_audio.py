"""T18 common calibration, native PCM verification and centered listening FIR."""
import hashlib
import struct
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.signal import firwin,freqz,fftconvolve
from .persist import check
from .metrics import rms,local_checks


def calibrated(volts):
    x=np.asarray(volts,dtype=np.float64)/8
    if not np.isfinite(x).all() or np.max(abs(x))>=1:raise ValueError('Clipped or nonfinite calibrated audio')
    return x


def wav_header(path):
    with Path(path).open('rb') as f:
        head=f.read(12)
        if head[:4]!=b'RIFF' or head[8:]!=b'WAVE':raise ValueError('Not RIFF WAVE')
        if struct.unpack('<I',head[4:8])[0]+8!=Path(path).stat().st_size:raise ValueError('RIFF length mismatch')
        fmt=None;payload=None
        while (chunk:=f.read(8)):
            if len(chunk)!=8:raise ValueError('Truncated chunk')
            name,size=struct.unpack('<4sI',chunk);data=f.read(size)
            if len(data)!=size:raise ValueError('Truncated WAV payload')
            if name==b'fmt ':fmt=struct.unpack('<HHIIHH',data[:16])
            if name==b'data':payload=size
            if size%2:f.read(1)
    if fmt is None or payload is None:raise ValueError('Missing WAV chunks')
    return dict(format=fmt[0],channels=fmt[1],rate_Hz=fmt[2],byte_rate=fmt[3],block_align=fmt[4],bits=fmt[5],data_bytes=payload)


def qualify_native(path,nominal,refined,rate):
    n=len(nominal);head=wav_header(path)
    if head!=dict(format=1,channels=1,rate_Hz=rate,byte_rate=rate*4,block_align=4,bits=32,data_bytes=n*4):raise ValueError('Wrong native PCM32 header/grid')
    actual_rate,q=wavfile.read(path)
    if q.dtype!=np.int32 or q.shape!=(n,):raise ValueError('Wrong signed PCM32 samples')
    if np.any((q==np.iinfo(np.int32).min)|(q==np.iinfo(np.int32).max)):raise ValueError('PCM endpoint clipping')
    calibrated(nominal)
    if refined is not None:calibrated(refined)
    v=q.astype(np.float64)*(8/2**31);e=v-nominal;u=None if refined is None else nominal-refined
    checks=[check('wav_header_grid',0,0),check('wav_no_clipping',0,0),check('wav_native_rms',rms(e),1e-6,'V'),check('wav_native_peak',float(max(abs(e))),1e-5,'V'),check('wav_reference_uncertainty_rms',None if u is None else rms(u),1e-7,'V'),check('wav_reference_uncertainty_peak',None if u is None else float(max(abs(u))),1e-6,'V')]
    for start in range(0,n,round(rate*.020)):
        ewin=e[start:start+round(rate*.020)];checks.extend([check(f'wav_local_rms_{start}',rms(ewin),1e-6,'V'),check(f'wav_local_peak_{start}',float(max(abs(ewin))),1e-5,'V')])
    return checks


def listening_filter(rate):
    if rate not in (192000,384000):raise ValueError('Unsupported listening input rate')
    m=rate//48000;h=firwin(128*m+1,22000,window=('kaiser',8.6),scale=True,fs=rate)
    f,response=freqz(h,worN=262144,fs=rate);db=20*np.log10(np.maximum(abs(response),1e-300))
    checks=[check('wav_filter_passband',float(max(abs(db[f<=20000]))),.01,'dB'),check('wav_filter_stopband',float(max(abs(response[f>=24000]))),1e-4,'linear')]
    return h,checks


def listening_pair(cpp,reference,rate,output):
    cpp=np.asarray(cpp);reference=np.asarray(reference)
    if len(cpp)!=round(3.5*rate)+1 or cpp.shape!=reference.shape:raise ValueError('Wrong listening input grid')
    calibrated(cpp);calibrated(reference);h,checks=listening_filter(rate);m=rate//48000;delay=64*m
    # valid[n] corresponds to centered physical input index n+delay.
    first=64;stop=167936;indices=np.arange(first,stop)*m-delay
    output.mkdir(parents=True,exist_ok=False);decoded=[]
    for name,values in [('cpp',cpp),('reference',reference)]:
        volts=fftconvolve(values,h,mode='valid')[indices];audio=calibrated(volts).astype(np.float32)
        path=output/(name+'.wav');wavfile.write(path,48000,audio);r,a=wavfile.read(path)
        if r!=48000 or a.shape!=(167872,) or a.dtype!=np.float32 or np.max(abs(a))>=1:raise ValueError('Wrong listening WAV')
        error=a.astype(float)*8-volts;decoded.append(a.astype(float)*8)
        checks.extend([check('wav_float_rms_'+name,rms(error),1e-6,'V'),check('wav_float_peak_'+name,float(max(abs(error))),1e-5,'V')])
    level=None if min(map(rms,decoded))==0 else abs(float(20*np.log10(rms(decoded[0])/rms(decoded[1]))))
    checks.append(check('wav_pair_level',level,.1,'dB'));checks.append(check('wav_listening_grid',0,0))
    metadata=dict(input_rate_Hz=rate,decimation=m,fir_length=len(h),delay_samples=delay,first_k=first,stop_k=stop,start_s=first/48000,stop_s=stop/48000,scale_V_per_FS=8,encoding='IEEE float32 mono',playback_gain=1,dc_removal='none',coefficient_sha256=hashlib.sha256(h.astype('<f8').tobytes()).hexdigest())
    return checks,metadata
