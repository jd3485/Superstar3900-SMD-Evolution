#!/usr/bin/env python3
"""Self-contained reproducibility and basic physics checks (not a native RF CAD simulator)."""
import unittest, numpy as np, math, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import rf_preselector_v24 as m
class TestNetwork(unittest.TestCase):
    def test_passivity_lossless(self):
        for pieces in [m.lowpass(9),m.highpass(5),m.highpass(5)+m.lowpass(9)]:
            t,r=m.network(pieces,np.linspace(10e6,55e6,59),q_inductor=1e12,tand_cap=0)
            np.testing.assert_allclose(abs(t)**2+abs(r)**2,1,atol=1e-9)
    def test_zero_components(self):
        t,r=m.network([],[27e6]);self.assertAlmostEqual(abs(t[0]),1);self.assertAlmostEqual(abs(r[0]),0)
    def test_cheb_response(self):
        elems=m.lowpass(9)
        freq=np.linspace(2e6,28e6,37)
        s21,_=m.network(elems,freq,q_inductor=1e12,tand_cap=0)
        # an ideal 0.1dB Chebyshev is within 0.1dB inside passband
        self.assertLessEqual(np.max(-20*np.log10(np.abs(s21))),.101)
    def test_butter_response(self):
        els=m.highpass(5,18e6)
        for freq in [10e6,18e6,27e6]:
            s,_=m.network(els,[freq],q_inductor=1e12,tand_cap=0)
            expected=10*math.log10(1+(18e6/freq)**10)
            self.assertAlmostEqual(-20*math.log10(abs(s[0])),expected,places=4)
    def test_filter_order_vs_image(self):
        vals=[m.measures(m.highpass(5)+m.lowpass(n),60)['min_image_rejection_db'] for n in (7,9,11)]
        self.assertGreater(vals[1],vals[0]+15)
        self.assertGreater(vals[2],vals[1]+15)
    def test_q_vs_insertion_loss(self):
        el=m.highpass(5)+m.lowpass(9)
        self.assertGreater(m.measures(el,25)['max_pass_loss_db'],m.measures(el,60)['max_pass_loss_db'])
    def test_image_band_arithmetic(self):
        lo=np.array([25.615,28.305])+10.695
        img=lo+10.695
        np.testing.assert_allclose(img,[47.005,49.695])
if __name__=='__main__':unittest.main(verbosity=2)
