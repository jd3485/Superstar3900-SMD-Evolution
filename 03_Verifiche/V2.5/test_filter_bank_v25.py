#!/usr/bin/env python3
"""Deterministic static/unit tests for V2.5 study, NOT KiCad/ERC or RF bench tests."""
import unittest, sys, pathlib, math, json
import numpy as np
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import filter_bank_v25 as rf

class BankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b=rf.extract_bands(ROOT/'02_Piano_Frequenze/Tabella_270_canali.csv')
        cls.results=json.loads((HERE/'Risultati_V2.5.json').read_text(encoding='utf8'))

    def test_01_bands_and_positions(self):
        self.assertEqual(len(self.b),6)
        self.assertEqual(sum(len(x['freq_hz']) for x in self.b),270)
    def test_02_band_labels(self):
        self.assertEqual([x['band'] for x in self.b],list('ABCDEF'))
    def test_03_nonoverlap_monotonic(self):
        for a,b in zip(self.b[:-1],self.b[1:]):
            self.assertLess(a['hi_hz'],b['lo_hz'])
    def test_04_all_channels_include_alpha(self):
        for b in self.b:
            self.assertEqual(len(set(b['freq_hz'])),45)
    def test_05_filter_has_three_shunts_four_series(self):
        for b in self.b:
            x=rf.branch_nominal(b['center_hz'])
            self.assertEqual(len(x),10)
            self.assertEqual(sum(typ=='LPAR' for typ,val in x),3)
            self.assertEqual(sum(typ=='CS' for typ,val in x),4)
    def test_06_center_frequency_scaling(self):
        b=self.b[0];e=rf.branch_nominal(b['center_hz'])
        self.assertTrue(np.isclose(e[0][1],rf.BASE_SEED[0]*rf.F_REF/b['center_hz']))
    def test_07_passivity_across_frequency(self):
        # Passive network: |S11|^2+|S21|^2 <= 1 (complex amplitudes inferred from dB)
        e=rf.branch_nominal(self.b[3]['center_hz'])
        a,b=rf.response(e,np.linspace(10e6,70e6,400))
        s21=10**(-a/20);s11=10**(b/20)
        self.assertTrue(np.all(s11**2+s21**2 <= 1+1e-9))
    def test_08_finite_passband_results(self):
        for b in self.b:
            loss,return_loss=rf.response(rf.branch_nominal(b['center_hz']),b['freq_hz'])
            self.assertTrue(np.all(np.isfinite(loss)))
            self.assertTrue(np.all(np.isfinite(return_loss)))
    def test_09_no_frequency_image_overlap(self):
        for b in self.b:
            self.assertGreater(b['lo_hz']+21_390_000,46e6)
    def test_10_stochastic_perturb_range(self):
        import numpy as np
        e=rf.branch_nominal(self.b[3]['center_hz']);rng=np.random.default_rng(390025)
        ee=rf.mc_elements(e,rng,.02)
        self.assertTrue(all(abs(v1/v0-1)<=.020001 for (_,v0),(_,v1) in zip(e,ee)))
    def test_11_model_compare_to_V24(self):
        self.assertAlmostEqual(self.results['baseline_unbanked_HP5_LP9_Q60']['max_pass_loss_db'],1.613595530995172,places=6)
    def test_12_scenario_switch_loss_exactly_one_dB_apart(self):
        a=self.results['nominal_bank_results'];delta=[a[2*i+1]['front_max_loss_db']-a[2*i]['front_max_loss_db'] for i in range(6)]
        self.assertTrue(all(abs(d-1.0)<1e-9 for d in delta))
    def test_13_all_six_results(self):
        self.assertEqual(len(self.results['nominal_bank_results']),12)
    def test_14_no_approval(self):
        self.assertIn('NO-GO',self.results['decision'])
    def test_15_mc_count(self):
        self.assertEqual(self.results['mc_total'],6*500)

if __name__=='__main__':
    unittest.main(verbosity=2)
