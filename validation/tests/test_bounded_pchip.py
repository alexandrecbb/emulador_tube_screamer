"""Block boundaries preserve SciPy slopes without full-reference coefficients."""
import numpy as np
import pytest
from scipy.interpolate import PchipInterpolator
from ts808_validation import reconstruct


@pytest.mark.parametrize('columns', [False, True])
def test_blocked_pchip_matches_full_scipy(monkeypatch, columns):
    rng=np.random.default_rng(812)
    times=np.cumsum(rng.uniform(.001,.01,1003))
    values=np.sin(times*17)+.1*np.cos(times*31)
    if columns:values=np.column_stack((values,values**2))
    target=np.unique(np.r_[times, np.linspace(times[0],times[-1],4001)])
    expected=PchipInterpolator(times,values,axis=0)(target)
    sizes=[]
    def bounded(t,v,**kwargs):
        sizes.append(len(t))
        return PchipInterpolator(t,v,**kwargs)
    monkeypatch.setattr(reconstruct,'SOURCE_BLOCK',31)
    monkeypatch.setattr(reconstruct,'PchipInterpolator',bounded)
    actual=reconstruct.pchip(times,values,target)
    np.testing.assert_array_equal(actual,expected)
    assert max(sizes)<=36
    assert len(sizes)>20


def test_discontinuity_preserves_one_sided_domains(monkeypatch):
    times=np.arange(101)/100
    values=np.where(times<.5,np.sin(times),10+np.cos(times))
    target=np.r_[np.linspace(0,.49,98),np.linspace(.5,1,101)]
    expected=np.r_[PchipInterpolator(times[:50],values[:50])(target[:98]),
                   PchipInterpolator(times[50:],values[50:])(target[98:])]
    monkeypatch.setattr(reconstruct,'SOURCE_BLOCK',7)
    np.testing.assert_array_equal(reconstruct.pchip(times,values,target,discontinuities=[.5]),expected)


def test_invalid_axis_at_block_boundary(monkeypatch):
    monkeypatch.setattr(reconstruct,'SOURCE_BLOCK',7)
    times=np.arange(30,dtype=float);times[7]=times[6]
    with pytest.raises(ValueError,match='increasing'):
        reconstruct.pchip(times,times,[1,2])


@pytest.mark.parametrize('count',[100,101,112,113])
def test_decimation_matches_full_leave_out(monkeypatch,count):
    monkeypatch.setattr(reconstruct,'SOURCE_BLOCK',7)
    rng=np.random.default_rng(count)
    times=np.cumsum(rng.uniform(.01,.02,count));values=np.sin(times*9)
    keep=np.unique(np.r_[np.arange(0,count,2),count-1]);omitted=np.arange(1,count-1,2)
    interp=PchipInterpolator(times[keep],values[keep])
    target=np.linspace(times[0],times[-1],403)
    summary,coarse=reconstruct.decimation_diagnostic(times,values,target)
    error=interp(times[omitted])-values[omitted]
    np.testing.assert_array_equal(coarse,interp(target))
    assert summary['error_rms']==pytest.approx(np.sqrt(np.mean(error**2)),rel=1e-14)
    assert summary['error_peak']==np.max(abs(error))
    assert summary['reference_rms']==pytest.approx(np.sqrt(np.mean(values[omitted]**2)),rel=1e-14)
    assert summary['reference_peak']==np.max(abs(values[omitted]))
