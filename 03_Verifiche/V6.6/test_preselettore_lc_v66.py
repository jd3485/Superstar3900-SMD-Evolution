#!/usr/bin/env python3
"""Test incrementali V6.6; solo coerenza/networks numeriche, NON hardware."""
import csv
import importlib.util
import json
import math
import unittest
from dataclasses import replace
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location('v66sim',HERE/'simula_preselettore_lc_v66.py')
sim=importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name]=sim
spec.loader.exec_module(sim)

class TestF501V66(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ch=sim.load_channels()
        cls.p=sim.Parts()
        cls.nom=sim.summary(cls.p)
        cls.data=json.loads((HERE/'RISULTATI_ANALISI_LC_V6.6.json').read_text())

    def test_01_rx_count(self): self.assertEqual(len(self.ch),270)
    def test_02_unique_rf(self): self.assertEqual(len({int(c['rf_hz']) for c in self.ch}),270)
    def test_03_six_bands(self): self.assertEqual({c['banda'] for c in self.ch},set('ABCDEF'))
    def test_04_alfa_30(self): self.assertEqual(sum(int(c['alfa']) for c in self.ch),30)
    def test_05_each_band_45(self):
        for b in 'ABCDEF': self.assertEqual(sum(c['banda']==b for c in self.ch),45)
    def test_06_rx_range(self):
        rf=[int(c['rf_hz']) for c in self.ch]
        self.assertEqual((min(rf),max(rf)),(25615000,28305000))
    def test_07_image_range(self):
        f=[int(c['immagine_hz']) for c in self.ch]
        self.assertEqual((min(f),max(f)),(47005000,49695000))
    def test_08_image_offset(self):
        for c in self.ch: self.assertEqual(int(c['immagine_hz'])-int(c['rf_hz']),21390000)
    def test_09_lo_high(self):
        for c in self.ch: self.assertEqual(int(c['lo_hz'])-int(c['rf_hz']),10695000)
    def test_10_tx_disabled(self): self.assertTrue(all(c['tx_enabled']=='False' for c in self.ch))
    def test_11_series_caps(self): self.assertAlmostEqual(self.p.c1_f,17.5e-12,delta=1e-22)
    def test_12_series_match(self): self.assertEqual(self.p.c1_f,self.p.c3_f)
    def test_13_shunt_caps(self): self.assertAlmostEqual(self.p.c2_f,1591e-12,delta=1e-22)
    def test_14_series_inductors(self): self.assertEqual(self.p.l1_h,self.p.l3_h)
    def test_15_shunt_inductor(self): self.assertEqual(self.p.l2_h,22e-9)
    def test_16_lc_resonance_l1(self):
        fr=1/(2*math.pi*math.sqrt(self.p.l1_h*self.p.c1_f))
        self.assertLess(abs(fr-sim.F0_HZ),0.1e6)
    def test_17_lc_resonance_l2(self):
        fr=1/(2*math.pi*math.sqrt(self.p.l2_h*self.p.c2_f))
        self.assertLess(abs(fr-sim.F0_HZ),0.1e6)
    def test_18_z0(self): self.assertEqual(sim.Z0,50.0)
    def test_19_f0_geom(self): self.assertAlmostEqual(sim.F0_HZ, math.sqrt(25e6*29e6),delta=.01)
    def test_20_finite(self):
        for f in [25.615e6,27e6,28.305e6,47.005e6,49.695e6]:
            s21,s11=sim.two_port(f,self.p)
            self.assertTrue(np.isfinite(s21)); self.assertTrue(np.isfinite(s11))
    def test_21_passive(self):
        s21,s11=sim.two_port(np.linspace(20e6,70e6,500),self.p)
        self.assertLessEqual(np.max(abs(s21)**2+abs(s11)**2),1.0000001)
    def test_22_q_effect(self):
        low=sim.summary(replace(self.p,q_l1=30,q_l2=30,q_l3=30))
        self.assertGreater(low['rx_insertion_loss_db_max'],self.nom['rx_insertion_loss_db_max'])
    def test_23_image_500f(self):
        high=sim.summary(replace(self.p,c_feed_f=.5e-12))
        self.assertLess(high['image_attenuation_db_min'],self.nom['image_attenuation_db_min']-10)
    def test_24_image_1pf(self):
        high=sim.summary(replace(self.p,c_feed_f=1e-12))
        self.assertLess(high['image_attenuation_db_min'],31)
    def test_25_nominal_img(self): self.assertGreater(self.nom['image_attenuation_db_min'],50)
    def test_26_nominal_rx(self): self.assertLess(self.nom['rx_insertion_loss_db_max'],6)
    def test_27_nominal_return_loss_problem(self):
        self.assertLess(self.nom['rx_return_loss_db_min'],10)
    def test_28_no_vendor_parts_qualified(self):
        self.assertTrue(self.data['remaining_gates'][0].startswith('Q/SRF'))
    def test_29_vendor_passband(self):
        vend=self.data['external_datasheet_candidate']
        self.assertLessEqual(vend['passband_mhz'][0]*1e6,min(int(c['rf_hz']) for c in self.ch))
        self.assertGreaterEqual(vend['passband_mhz'][1]*1e6,max(int(c['rf_hz']) for c in self.ch))
    def test_30_vendor_stopband(self):
        vend=self.data['external_datasheet_candidate']
        self.assertLessEqual(vend['image_stopband_mhz'][0]*1e6,min(int(c['immagine_hz']) for c in self.ch))
    def test_31_vendor_pin(self): self.assertEqual(self.data['external_datasheet_candidate']['input_pad'],1)
    def test_32_vendor_out(self): self.assertEqual(self.data['external_datasheet_candidate']['output_pad'],8)
    def test_33_vendor_ground(self): self.assertEqual(self.data['external_datasheet_candidate']['ground_pad_numbers'],[2,3,4,5,6,7])
    def test_34_records_full(self):
        with (HERE/'RISPOSTA_270_CANALI_LC_V6.6.csv').open(newline='',encoding='utf-8') as f:
            self.assertEqual(len(list(csv.DictReader(f))),270)
    def test_35_monte_carlo_n(self): self.assertEqual(self.data['monte_carlo']['n'],4000)
    def test_36_monte_carlo_fraction(self):
        frac=self.data['monte_carlo']['fraction_rx_loss_above_6dB']
        self.assertGreater(frac,.05)
    def test_37_no_forced_pass(self):
        self.assertGreater(self.data['monte_carlo']['fraction_relative_image_rejection_below_40dB'],.1)
    def test_38_tx_not_approved_document(self):
        doc=(ROOT/'01_Specifiche/V6.6/SCHEMA_PRESELETTORE_LC_V6.6.md').read_text(encoding='utf-8')
        self.assertIn('NO TX',doc); self.assertIn('NO FAB',doc)
    def test_39_negative_freq_guard(self):
        with self.assertRaises(ValueError): sim.two_port(-1)
    def test_40_zero_q_guard(self):
        with self.assertRaises(ValueError): sim.two_port(27e6,replace(self.p,q_l1=0))
    def test_41_nominal_reporting_reproducible(self):
        self.assertAlmostEqual(self.nom['rx_insertion_loss_db_max'],self.data['nominal']['rx_insertion_loss_db_max'],places=9)
    def test_42_user_data_no_tx(self):
        with (HERE/'RISPOSTA_270_CANALI_LC_V6.6.csv').open(newline='',encoding='utf-8') as f:
            self.assertTrue(all(row['tx_enabled']=='False' for row in csv.DictReader(f)))
    def test_43_fft_fi_not_affected(self):
        for row in self.ch:
            self.assertEqual(abs(int(row['lo_hz'])-int(row['rf_hz'])),10695000)
            self.assertEqual(abs(int(row['lo_hz'])-int(row['immagine_hz'])),10695000)
    def test_44_no_spice_native_claim(self):
        doc=(ROOT/'01_Specifiche/V6.6/SCHEMA_PRESELETTORE_LC_V6.6.md').read_text(encoding='utf-8')
        self.assertIn('ngspice non eseguito',doc)
    def test_45_spice_source(self): self.assertTrue((HERE/'PRESELETTORE_LC_50R_V6.6.cir').is_file())
    def test_46_source_vendor(self):
        s=(ROOT/'01_Specifiche/V6.6/CONFRONTO_F501_V6.6.md').read_text(encoding='utf-8')
        self.assertIn('SXBP-27R5+',s)
    def test_47_netlist_edges(self):
        with (ROOT/'01_Specifiche/V6.6/NETLIST_COMPONENTI_PRESELETTORE_V6.6.csv').open(newline='',encoding='utf-8') as f:
            l=list(csv.DictReader(f))
        self.assertEqual(len(l),22)
    def test_48_srf_guard(self):
        self.assertGreater(self.p.srf_l1_hz,49.695e6)
    def test_49_free_q(self):
        big=replace(self.p,q_l1=1e9,q_l2=1e9,q_l3=1e9,q_c=1e9,
                    srf_l1_hz=1e12,srf_l2_hz=1e12,srf_l3_hz=1e12,c_feed_f=0)
        s,ref=sim.two_port(sim.F0_HZ,big)
        self.assertAlmostEqual(abs(s),1,places=5)
        self.assertLess(abs(ref),1e-3)  # E-series values are not exact center-match
    def test_50_ideal_3db_corners(self):
        big=replace(self.p,l1_h=50/(2*math.pi*4e6),l3_h=50/(2*math.pi*4e6),
            l2_h=(50*(4e6/sim.F0_HZ))/(2*2*math.pi*sim.F0_HZ),
            c1_f=1/((2*math.pi*sim.F0_HZ)**2*(50/(2*math.pi*4e6))),
            c3_f=1/((2*math.pi*sim.F0_HZ)**2*(50/(2*math.pi*4e6))),
            c2_f=2/(50*2*math.pi*4e6),
            q_l1=1e10,q_l2=1e10,q_l3=1e10,q_c=1e10,
            srf_l1_hz=1e12,srf_l2_hz=1e12,srf_l3_hz=1e12,c_feed_f=0)
        loss=sim.attenuation_db(sim.two_port(np.array([25e6,29e6]),big)[0])
        self.assertTrue(np.allclose(loss,3.01029996,atol=.002),loss)

if __name__=='__main__':
    unittest.main(verbosity=2)
