from pathlib import Path
import sys
import unittest
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ts808_validation.reference import read_native
from ts808_validation.reconstruct import pchip

FIXTURES=Path(__file__).parent/'fixtures'


class NativeReader(unittest.TestCase):
    def read(self,name,kind,**kwargs):
        return read_native(FIXTURES/(name+'.raw'),FIXTURES/(name+'.log'),analysis_kind=kind,
                           trace_names=['V(output)'],**kwargs)

    def test_dc_ac_and_complex_normalization(self):
        dc=self.read('ltspice26_dc','dc');self.assertAlmostEqual(dc['traces']['V(output)'][0],.1,places=10)
        ac=self.read('ltspice26_ac','ac');frequency=ac['axis']
        expected=1/(1+2j*np.pi*frequency*.001)
        self.assertLess(np.max(np.abs(ac['traces']['V(output)']-expected)),1e-10)

    def test_transient_matches_independent_rc_solution(self):
        data=self.read('ltspice26_tran64','transient');t=data['axis']
        expected=np.where(t<.001,0,.1*(1-np.exp(-np.maximum(t-.001,0)/.001)))
        self.assertLess(np.max(np.abs(data['traces']['V(output)']-expected)),1e-7)

    def test_precision_truncation_and_selection_rejected(self):
        for name in ('ltspice26_tran32','ltspice26_truncated'):
            with self.subTest(name=name),self.assertRaises(ValueError):
                read_native(FIXTURES/(name+'.raw'),FIXTURES/'ltspice26_tran64.log',analysis_kind='transient',trace_names=['V(output)'])
        with self.assertRaises(ValueError): self.read('ltspice26_ac','dc')
        with self.assertRaises(ValueError): self.read('ltspice26_stepped','transient')
        a=self.read('ltspice26_stepped','transient',step_index=0)
        b=self.read('ltspice26_stepped','transient',step_index=1)
        self.assertGreater(a['traces']['V(output)'][-1],b['traces']['V(output)'][-1])

    def test_pchip_no_extrapolation_and_exact_linear_fixture(self):
        times=np.array([0,.1,.3,.8,1.]);target=np.linspace(0,1,101)
        np.testing.assert_allclose(pchip(times,2*times+1,target),2*target+1,atol=1e-14)
        for bad_times,bad_target in [(times,[-.1]),([0,.1,.1,1],[0,.5]),(times,[.5,.2])]:
            with self.assertRaises(ValueError):pchip(bad_times,np.ones(len(bad_times)),bad_target)
        with self.assertRaises(ValueError):pchip(times,times,[.2,.6,.9],discontinuities=[.5])


def test_mapped_spicelib_backend_matches_buffered(monkeypatch):
    from ts808_validation import reference
    fixtures=Path(__file__).parent/'fixtures'
    import numpy as np
    for filename,kind,names in [('ltspice26_tran64','transient',['V(output)']),('ltspice26_ac','ac',['V(output)'])]:
        regular=reference.read_native(fixtures/(filename+'.raw'),fixtures/(filename+'.log'),analysis_kind=kind,trace_names=names)
        monkeypatch.setattr(reference,'MAPPED_RAW_THRESHOLD',0)
        mapped=reference.read_native(fixtures/(filename+'.raw'),fixtures/(filename+'.log'),analysis_kind=kind,trace_names=names)
        np.testing.assert_array_equal(regular['axis'],mapped['axis'])
        for name in names:np.testing.assert_array_equal(regular['traces'][name],mapped['traces'][name])
        monkeypatch.setattr(reference,'MAPPED_RAW_THRESHOLD',64*1024*1024)
