#!/usr/bin/env python3
"""Test V6.4 matematici, logici, integrazione documentale; NON KiCad, NON spettro."""
import csv
import json
import math
import random
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'03_Verifiche/V6.4'))
sys.path.insert(0,str(ROOT/'08_Firmware_Prototipi/V6.4'))
import simula_pll_v64 as pll
from pll_lo_guard_v64 import RxPllGuard, State


class TestPlan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table,cls.st=pll.report()
    def test_01_count(self):self.assertEqual(len(self.table),270)
    def test_02_six_bands(self):self.assertEqual(set(x['banda'] for x in self.table),set('ABCDEF'))
    def test_03_45_each(self):
        self.assertTrue(all(sum(x['banda']==b for x in self.table)==45 for b in 'ABCDEF'))
    def test_04_alpha_count(self):self.assertEqual(sum(x['alfa'] for x in self.table),30)
    def test_05_270_ids_unique(self):self.assertEqual(len({(x['banda'],x['canale']) for x in self.table}),270)
    def test_06_270_freq_unique(self):self.assertEqual(len({x['rf_hz'] for x in self.table}),270)
    def test_07_integer_n(self):self.assertTrue(all(x['pll_num']==0 and x['pll_den']==1 for x in self.table))
    def test_08_rdiv(self):self.assertTrue(all(x['r_div']==10 for x in self.table))
    def test_09_pfd(self):self.assertTrue(all(x['pfd_hz']==1_280_000 for x in self.table))
    def test_10_divider(self):self.assertTrue(all(x['out_div']==128 for x in self.table))
    def test_11_rf_lo_if_equation(self):self.assertTrue(all(x['lo_hz']-x['rf_hz']==pll.IF_HZ for x in self.table))
    def test_12_vco_divider_equation(self):self.assertTrue(all(x['vco_hz']//128==x['lo_hz'] for x in self.table))
    def test_13_vco_pfd_equation(self):self.assertTrue(all(x['vco_hz']==x['pll_n']*x['pfd_hz'] for x in self.table))
    def test_14_image_equation(self):self.assertTrue(all(x['if_image_hz']-x['rf_hz']==2*pll.IF_HZ for x in self.table))
    def test_15_vco_range(self):self.assertTrue(all(3_200_000_000 <= x['vco_hz'] <=6_400_000_000 for x in self.table))
    def test_16_pfd_integer_mode_range(self):self.assertTrue(pll.INT_PFD_MIN_HZ<=pll.PFD_HZ<=pll.INT_PFD_MAX_HZ)
    def test_17_no_rf_tx(self):self.assertTrue(all(x['tx_permitted_v64']==0 for x in self.table))
    def test_18_chnine_d(self):
        self.assertEqual(next(x['rf_hz'] for x in self.table if x['banda']=='D' and x['canale']=='9'),27_065_000)
    def test_19_legacy_channel_23_24(self):
        self.assertEqual(next(x['rf_hz'] for x in self.table if x['banda']=='D' and x['canale']=='23'),27_255_000)
        self.assertEqual(next(x['rf_hz'] for x in self.table if x['banda']=='D' and x['canale']=='24'),27_235_000)
    def test_20_minimum_and_maximum(self):
        self.assertEqual(self.st['rx_min_hz'],25_615_000);self.assertEqual(self.st['rx_max_hz'],28_305_000)
        self.assertEqual(self.st['lo_min_hz'],36_310_000);self.assertEqual(self.st['lo_max_hz'],39_000_000)
    def test_21_no_register_words(self):self.assertEqual(self.st['tics_pro_register_profile'],'NOT_GENERATED')
    def test_22_invalid_negative_rf(self):
        with self.assertRaises(ValueError):pll.synthesize('A','1',-1)
    def test_23_invalid_type_rf(self):
        with self.assertRaises(ValueError):pll.synthesize('A','1',25_615_000.0)
    def test_24_invalid_key(self):
        with self.assertRaises(ValueError):pll.synthesize('','1',25_615_000)
    def test_25_invalid_frequency_division(self):
        with self.assertRaises(ValueError):pll.synthesize('A','1',25_615_001)
    def test_26_vco_out_of_range(self):
        with self.assertRaises(ValueError):pll.synthesize('Z','1',1_000_000)
    def test_27_csv_exact(self):
        with (ROOT/'02_Piano_Frequenze/V6.4/PIANO_PLL_LO_270_RX_V6.4.csv').open() as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),270)
        self.assertEqual({(r['banda'],r['canale'],int(r['rf_hz'])) for r in rows},
                         {(r['banda'],r['canale'],r['rf_hz']) for r in self.table})
    def test_28_json_exact(self):
        data=json.loads((ROOT/'03_Verifiche/V6.4/RISULTATI_SIMULAZIONI_PLL_V6.4.json').read_text())
        self.assertEqual(data['canali'],270)
        self.assertEqual(data['vco_max_hz'],self.st['vco_max_hz'])
    def test_29_oscillator_scenario_bound(self):
        st=self.st['tcxo_scenario'];self.assertLessEqual(st['max_absolute_lo_error_hz_sample'],st['absolute_max_bound_for_all_channels_hz']+1e-4)
    def test_30_repeatability(self):
        a=pll.stress_oscillator(self.table,n=100,seed=9)
        self.assertEqual(a,pll.stress_oscillator(self.table,n=100,seed=9))
    def test_31_oscillator_bad_args(self):
        with self.assertRaises(ValueError):pll.stress_oscillator(self.table,n=0)
    def test_32_thermal_flag_150ma(self):
        self.assertTrue(pll.linear_3v3_pll_budget(load_ma=150)['thermal_125c_limit_exceeded'])
    def test_33_thermal_nominal_not_over_125(self):
        self.assertFalse(pll.linear_3v3_pll_budget(load_ma=105)['thermal_125c_limit_exceeded'])
    def test_34_bad_thermal_args(self):
        with self.assertRaises(ValueError):pll.linear_3v3_pll_budget(input_v=3.3, output_v=5)
    def test_35_board_pins_mcu_reserved(self):
        path=ROOT/'01_Specifiche/V6.1/PINMAP_MCU_LQFP64_V6.1.csv'
        with path.open() as f:rows=list(csv.DictReader(f))
        signals={'PLL_CS_N':'PA4','PLL_SCK':'PA5','PLL_SDI':'PA7','PLL_MUXOUT':'PB0','PLL_CE':'PB1'}
        for sig,gpio in signals.items():
            self.assertEqual([x['gpio'] for x in rows if x['rete']==sig],[gpio])
    def test_36_v63_pll_budget_exists_no_double_count(self):
        with (ROOT/'01_Specifiche/V6.3/BILANCIO_CORRENTI_V6.3.csv').open() as f:rows=list(csv.DictReader(f))
        vals=[x for x in rows if x['Carico']=='PLL_LO']
        self.assertEqual(len(vals),1)
        self.assertEqual(vals[0]['Rail'],'5V_RF')
        self.assertGreaterEqual(float(vals[0]['I_nominale_A']),0.13)
    def test_37_old_table_parity(self):
        with (ROOT/'02_Piano_Frequenze/Tabella_LMX2572_270_Integer_N_V0.5.csv').open() as f:old=list(csv.DictReader(f))
        self.assertEqual(len(old),270)
        self.assertEqual([(x['banda'],x['canale'],int(x['lo_hz']),int(x['pll_n_integer'])) for x in old],
                         [(x['banda'],x['canale'],x['lo_hz'],x['pll_n']) for x in self.table])
    def test_38_clock_format_source(self):
        src=(ROOT/'08_Firmware_Prototipi/lmx2572_spi_transport_v15.py').read_text()
        self.assertIn('explicitly_validated',src)
        self.assertIn('build_frame',src)
    def test_39_phase_noise_not_run(self):self.assertIn('NOT_RUN',self.st['jitter_phase_noise_spectrum'])
    def test_40_every_row_unvalidated(self):
        self.assertTrue(all('NON_PROFILO' in x['status'] for x in self.table))


class TestGuard(unittest.TestCase):
    def make_ready(self):
        g=RxPllGuard()
        g.step(0,request=True,power_good=True,ref_good=True)
        g.step(1,request=True,power_good=True,ref_good=True)
        g.step(2,request=True,power_good=True,ref_good=True,profile_loaded=True)
        g.step(3,request=True,power_good=True,ref_good=True,lock_detect=True)
        p=g.step(6,request=True,power_good=True,ref_good=True,lock_detect=True)
        return g,p
    def test_41_start_default_off(self):self.assertEqual(RxPllGuard().state,State.OFF)
    def test_42_start_disabled_without_power(self):
        g=RxPllGuard();p=g.step(0,request=True,power_good=False,ref_good=False)
        self.assertFalse(p.ce);self.assertEqual(g.state,State.OFF)
    def test_43_ce_with_good_sources(self):
        g=RxPllGuard();p=g.step(0,request=True,power_good=True,ref_good=True)
        self.assertTrue(p.ce);self.assertFalse(p.audio_rx_unmuted)
    def test_44_wait_for_settling(self):
        g=RxPllGuard();g.step(0,request=True,power_good=True,ref_good=True)
        g.step(0.49,request=True,power_good=True,ref_good=True)
        self.assertEqual(g.state,State.SETTLING)
    def test_45_wait_profile_then_lock(self):
        g=RxPllGuard();g.step(0,request=True,power_good=True,ref_good=True)
        g.step(1,request=True,power_good=True,ref_good=True)
        self.assertEqual(g.state,State.WAIT_PROFILE)
        g.step(2,request=True,power_good=True,ref_good=True,profile_loaded=True)
        self.assertEqual(g.state,State.WAIT_LOCK)
    def test_46_ready_only_after_lock_dwell(self):
        g,p=self.make_ready();self.assertEqual(g.state,State.RX_READY);self.assertTrue(p.audio_rx_unmuted)
    def test_47_lock_loss_mutes_rx(self):
        g,p=self.make_ready()
        p=g.step(7,request=True,power_good=True,ref_good=True,lock_detect=False)
        self.assertFalse(p.audio_rx_unmuted);self.assertEqual(g.state,State.WAIT_LOCK)
    def test_48_pa_mutes_immediately(self):
        g,p=self.make_ready()
        p=g.step(7,request=True,power_good=True,ref_good=True,lock_detect=True,pa_active=True)
        self.assertFalse(p.ce);self.assertFalse(p.audio_rx_unmuted);self.assertEqual(g.state,State.OFF)
    def test_49_power_loss_fault(self):
        g,p=self.make_ready()
        p=g.step(7,request=True,power_good=False,ref_good=True,lock_detect=True)
        self.assertFalse(p.ce);self.assertFalse(p.audio_rx_unmuted);self.assertEqual(g.state,State.FAULT)
    def test_50_ref_loss_fault(self):
        g,p=self.make_ready()
        p=g.step(7,request=True,power_good=True,ref_good=False,lock_detect=True)
        self.assertFalse(p.ce);self.assertEqual(g.state,State.FAULT)
    def test_51_external_fault(self):
        g,p=self.make_ready()
        p=g.step(7,request=True,power_good=True,ref_good=True,lock_detect=True,fault=True)
        self.assertEqual(g.state,State.FAULT)
    def test_52_manual_stop_clears_fault(self):
        g,p=self.make_ready()
        g.step(7,request=True,power_good=True,ref_good=True,fault=True)
        g.step(8,request=False,power_good=True,ref_good=True)
        self.assertEqual(g.state,State.OFF)
    def test_53_retune_mutes(self):
        g,p=self.make_ready()
        p=g.step(7,request=True,power_good=True,ref_good=True,lock_detect=True,retune_request=True)
        self.assertEqual(g.state,State.WAIT_PROFILE);self.assertFalse(p.audio_rx_unmuted)
    def test_54_tx_always_false_ready(self):
        g,p=self.make_ready();self.assertFalse(p.tx_enable)
    def test_55_tx_always_false_random(self):
        rng=random.Random(45);g=RxPllGuard();now=0
        for _ in range(10_000):
            now+=rng.uniform(.1,5)
            signals=dict(request=rng.choice([False,True]),power_good=rng.choice([False,True]),
                         ref_good=rng.choice([False,True]),profile_loaded=rng.choice([False,True]),
                         lock_detect=rng.choice([False,True]),pa_active=rng.choice([False,True]),
                         retune_request=rng.choice([False,True]),fault=rng.choice([False,True]))
            pins=g.step(now,**signals)
            self.assertFalse(pins.tx_enable)
            if pins.audio_rx_unmuted:
                self.assertTrue(pins.ce)
                self.assertTrue(signals['lock_detect'] and signals['power_good'] and signals['ref_good'])
                self.assertFalse(signals['pa_active'])
    def test_56_monotonic_timestamp(self):
        g=RxPllGuard();g.step(10,request=False,power_good=False,ref_good=False)
        with self.assertRaises(ValueError):g.step(9,request=False,power_good=False,ref_good=False)
    def test_57_negative_timestamp(self):
        with self.assertRaises(ValueError):RxPllGuard().step(-1,request=False,power_good=False,ref_good=False)
    def test_58_settling_below_vendor_min(self):
        with self.assertRaises(ValueError):RxPllGuard(settle_ms=0.1)
    def test_59_invalid_lock_dwell(self):
        with self.assertRaises(ValueError):RxPllGuard(lock_dwell_ms=-1)
    def test_60_no_profile_no_audio(self):
        g=RxPllGuard();g.step(0,request=True,power_good=True,ref_good=True)
        for t in range(1,40):
            p=g.step(t,request=True,power_good=True,ref_good=True,lock_detect=True)
            self.assertFalse(p.audio_rx_unmuted)
        self.assertEqual(g.state,State.WAIT_PROFILE)

if __name__=='__main__':unittest.main(verbosity=1)
