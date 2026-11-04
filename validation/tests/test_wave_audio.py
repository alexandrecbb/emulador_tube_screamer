import tempfile
from pathlib import Path
import numpy as np
import pytest
from scipy.io import wavfile
from ts808_validation.wave_audio import calibrated,qualify_native,listening_filter,listening_pair,wav_header

@pytest.mark.parametrize('rate',[192000,384000])
def test_common_fir_and_exact_support(rate):
    h,checks=listening_filter(rate)
    assert all(c['status']=='passed' for c in checks)
    m=rate//48000;d=64*m;n=round(3.5*rate)+1;t=np.arange(n)/rate
    for x in (np.full(n,.125),.1*np.sin(2*np.pi*1000*t),np.eye(1,n,round(.5*rate))[0]*.1):
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)/'pair';checks,meta=listening_pair(x,x,rate,output)
            r,y=wavfile.read(output/'cpp.wav');assert r==48000 and len(y)==167872
            for k in (64,65,24000,167935):
                direct=np.dot(h,x[k*m+d-np.arange(len(h))])/8
                assert abs(float(y[k-64])-direct)<=np.finfo(np.float32).eps*max(abs(direct),1e-8)+1e-16
            assert meta['first_k']==64 and meta['stop_k']==167936 and meta['dc_removal']=='none'
            assert all(c['status']=='passed' for c in checks)

@pytest.mark.parametrize('rate',[192000,384000])
def test_pcm_quantization_grid_and_local_failure(rate):
    n=round(.04*rate);x=.123+.2*np.sin(2*np.pi*1000*np.arange(n)/rate)
    q=np.round(x/8*2**31).astype(np.int32)
    assert np.max(abs(q.astype(float)*8/2**31-x))<=4/2**31
    with tempfile.TemporaryDirectory() as temp:
        p=Path(temp)/'native.wav';wavfile.write(p,rate,q)
        assert all(c['status']=='passed' for c in qualify_native(p,x,x,rate))
        for bad_rate,bad in [(48000,q),(rate,q[:-1]),(rate,np.column_stack((q,q))),(rate,q.astype(np.float32)),(rate,np.full(n,2**31-1,dtype=np.int32))]:
            wavfile.write(p,bad_rate,bad)
            with pytest.raises(ValueError):qualify_native(p,x,x,rate)
        e=np.zeros(n);e[:100]=2e-5;wavfile.write(p,rate,np.round((x+e)/8*2**31).astype(np.int32))
        assert any(c['status']=='failed' for c in qualify_native(p,x,x,rate))

@pytest.mark.parametrize('x',[[np.nan],[np.inf],[8.],[-8.]])
def test_clipping(x):
    with pytest.raises(ValueError):calibrated(x)


def test_retained_real_native_pcm_fixtures():
    from ts808_validation.reference import read_native
    from ts808_validation.reconstruct import pchip
    fixtures=Path(__file__).parent/'fixtures'
    native=read_native(fixtures/'wav_rc_deck.raw',fixtures/'wav_rc_deck.log',analysis_kind='transient',trace_names=['V(output)'])
    for rate,name in ((192000,'pcm192.wav'),(384000,'pcm384.wav')):
        t=np.arange(round(.004*rate))/rate;ref=pchip(native['axis'],native['traces']['V(output)'],t)
        if rate==192000:
            assert wav_header(fixtures/('wav_rc_'+name))['data_bytes']==769*4
            with pytest.raises(ValueError):qualify_native(fixtures/('wav_rc_'+name),ref,None,rate)
        else:
            checks=qualify_native(fixtures/('wav_rc_'+name),ref,None,rate)
            assert all(c['status']=='passed' for c in checks if not c['id'].startswith('wav_reference_uncertainty'))
            assert all(c['status']=='not_evaluated' for c in checks if c['id'].startswith('wav_reference_uncertainty'))


def test_endpoint_exclusive_real_native_pcm_fixtures():
    fixtures=Path(__file__).parent/'fixtures'
    for name,rate in [('pcm192',192000),('pcm384',384000)]:
        p=fixtures/('wav_qualified_'+name+'_pcm.wav')
        if not p.exists():pytest.skip('Generate qualified native fixtures first')
        header=wav_header(p)
        assert header['rate_Hz']==rate and header['format']==1 and header['data_bytes']==round(.004*rate)*4
        from ts808_validation.reference import read_native
        from ts808_validation.reconstruct import pchip
        raw=read_native(fixtures/'wav_rc_deck.raw',fixtures/'wav_rc_deck.log',analysis_kind='transient',trace_names=['V(output)'])
        t=np.arange(round(.004*rate))/rate;ref=pchip(raw['axis'],raw['traces']['V(output)'],t)
        checks=qualify_native(p,ref,None,rate)
        assert all(c['status']=='passed' for c in checks if not c['id'].startswith('wav_reference_uncertainty'))
