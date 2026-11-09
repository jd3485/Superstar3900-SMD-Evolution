#!/usr/bin/env python3
"""Test modello RF/FI V6.5; negativi, parita', immagini, muted/PA/NO-TX."""
from __future__ import annotations
import csv,importlib.util,itertools,json,math,random,sys,tempfile,unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from simula_mixer_fi_v65 import (read_pll_rows,butterworth_bpf_db,simulate_mixing_ideal,
                                 monte_carlo_bpf,calculate,IF_HZ,F_LOW_HZ,F_HIGH_HZ,LO_TARGET_DBM)

def loadmod(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod;spec.loader.exec_module(mod)
    return mod

firm=loadmod(ROOT/'08_Firmware_Prototipi/V6.5/rx_frontend_guard_v65.py','frontend_v65')
pllmod=loadmod(ROOT/'08_Firmware_Prototipi/V6.4/pll_lo_guard_v64.py','pllguard_v64')

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src=read_pll_rows()
        cls.stats,cls.out=calculate()

    def test_01_count(self):self.assertEqual(len(self.src),270)
    def test_02_distinct_channels(self):self.assertEqual(len({(r['banda'],r['canale']) for r in self.src}),270)
    def test_03_alpha_count(self):self.assertEqual(sum(int(r['alfa']) for r in self.src),30)
    def test_04_six_bands(self):self.assertEqual(set(r['banda'] for r in self.src),set('ABCDEF'))
    def test_05_rx_range(self):self.assertEqual((self.stats['rf_min_hz'],self.stats['rf_max_hz']),(25615000,28305000))
    def test_06_lo_range(self):self.assertEqual((self.stats['lo_min_hz'],self.stats['lo_max_hz']),(36310000,39000000))
    def test_07_image_range(self):self.assertEqual((self.stats['image_min_hz'],self.stats['image_max_hz']),(47005000,49695000))
    def test_08_if_10695(self):self.assertEqual(IF_HZ,10695000)
    def test_09_image_offset(self):self.assertEqual(self.stats['image_separation_hz'],2*IF_HZ)
    def test_10_each_image(self):
        for r in self.out:self.assertEqual(r['immagine_hz']-r['rf_hz'],2*IF_HZ)
    def test_11_each_lo(self):
        for r in self.out:self.assertEqual(r['lo_hz']-r['rf_hz'],IF_HZ)
    def test_12_tx_never_from_csv(self):self.assertTrue(all(not r['tx_enabled'] for r in self.out))
    def test_13_bpf_center(self):self.assertAlmostEqual(butterworth_bpf_db(math.sqrt(F_LOW_HZ*F_HIGH_HZ)),0,places=7)
    def test_14_bpf_low_edge(self):self.assertAlmostEqual(butterworth_bpf_db(F_LOW_HZ),-3.0102999566,places=6)
    def test_15_bpf_high_edge(self):self.assertAlmostEqual(butterworth_bpf_db(F_HIGH_HZ),-3.0102999566,places=6)
    def test_16_bpf_symmetry(self):
        f=26400000;other=F_LOW_HZ*F_HIGH_HZ/f
        self.assertAlmostEqual(butterworth_bpf_db(f),butterworth_bpf_db(other),places=8)
    def test_17_bpf_ideal_pass(self):self.assertGreater(self.stats['min_desired_gain_db_ideal'],-.5)
    def test_18_bpf_ideal_image(self):self.assertLess(self.stats['max_image_gain_db_ideal'],-53)
    def test_19_bpf_ideal_relative_image(self):self.assertGreater(self.stats['min_relative_image_rejection_db_ideal'],53)
    def test_20_bpf_analog_order(self):self.assertEqual(self.stats['bpf_analog_pole_order'],6)
    def test_21_bpf_reject_low(self):self.assertLess(butterworth_bpf_db(10e6),-10)
    def test_22_bpf_reject_high(self):self.assertLess(butterworth_bpf_db(70e6),-50)
    def test_23_bad_band(self):
        with self.assertRaises(ValueError):butterworth_bpf_db(27000000,29e6,25e6)
    def test_24_zero_freq(self):
        with self.assertRaises(ValueError):butterworth_bpf_db(0)
    def test_25_nan_freq(self):
        with self.assertRaises(ValueError):butterworth_bpf_db(float('nan'))
    def test_26_invalid_poles(self):
        with self.assertRaises(ValueError):butterworth_bpf_db(27000000,order=0)
    def test_27_bad_mixer_sample_rate(self):
        with self.assertRaises(ValueError):simulate_mixing_ideal(fs_hz=40e6)
    def test_28_mixing_desired_if(self):
        self.assertEqual(simulate_mixing_ideal()['rx_desiderato']['peak_if_hz'],IF_HZ)
    def test_29_mixing_image_if(self):
        self.assertEqual(simulate_mixing_ideal()['immagine']['peak_if_hz'],IF_HZ)
    def test_30_mixing_relative_peak(self):
        m=simulate_mixing_ideal()
        self.assertAlmostEqual(m['rx_desiderato']['peak_amplitude_relative'],1.,places=4)
        self.assertAlmostEqual(m['immagine']['peak_amplitude_relative'],1.,places=4)
    def test_31_lo_target_power(self):self.assertAlmostEqual(self.stats['lo_drive']['power_mw'],5.01187,places=4)
    def test_32_lo_target_vrms(self):self.assertAlmostEqual(self.stats['lo_drive']['vrms'],.500593,places=5)
    def test_33_lo_require_driver(self):self.assertTrue(self.stats['lo_drive']['requires_output_stage_measurement'])
    def test_34_critical_blocker(self):self.assertGreater(self.stats['image_rejection_db_for_0dbm_blocker_and_minus110dbm_spurious_target'],self.stats['min_relative_image_rejection_db_ideal'])
    def test_35_mc_reproducible(self):self.assertEqual(monte_carlo_bpf(self.src,n=50,seed=1),monte_carlo_bpf(self.src,n=50,seed=1))
    def test_36_mc_provisional(self):self.assertLess(self.stats['monte_carlo']['min_image_rejection_db_sample'],self.stats['min_relative_image_rejection_db_ideal'])
    def test_37_mc_valid(self):self.assertGreater(self.stats['monte_carlo']['min_image_rejection_db_sample'],50)
    def test_38_mc_bad_n(self):
        with self.assertRaises(ValueError):monte_carlo_bpf(self.src,n=0)
    def test_39_if_bands(self):self.assertEqual(set(r['modalita'] for r in self.stats['filter_modes_theoretical_requirements']),{'CW','USB','LSB','AM','FM'})
    def test_40_if_q_qualifications(self):
        q={r['modalita']:r['q_caricato_ideale_approssimato'] for r in self.stats['filter_modes_theoretical_requirements']}
        self.assertGreater(q['CW'],q['USB']);self.assertGreater(q['USB'],q['FM'])
    def test_41_no_model_fake_kicad(self):self.assertEqual(self.stats['native_kicad_erc_drc'],'NOT_RUN_KICAD_MISSING')
    def test_42_no_model_fake_spice(self):self.assertEqual(self.stats['spice'],'NOT_RUN_SPICE_MODEL_MISSING')
    def test_43_no_fab(self):self.assertFalse(self.stats['production_approved'])
    def test_44_ade_pinout(self):
        with (ROOT/'01_Specifiche/V6.5/PINOUT_MIXER_ADE1_V6.5.csv').open(newline='') as f:
            pins={int(x['pin']):x['net'] for x in csv.DictReader(f)}
        self.assertEqual(pins,{1:'GND_RF',2:'IF_10M695_RAW',3:'RF_MIXER_IN_AC',4:'GND_RF',5:'GND_RF',6:'RX_LO_36_39_50R'})
    def test_45_all_fail_safe_exhaustive(self):
        for flags in itertools.product([False,True],repeat=7):
            kw=dict(zip(('power_good','pll_locked_and_ready','requested_rx','pa_active','retuning','fault','if_filter_selected'),flags))
            res=firm.frontend_guard(**kw)
            valid=all([kw['power_good'],kw['pll_locked_and_ready'],kw['requested_rx'],kw['if_filter_selected']]) and not any([kw['pa_active'],kw['retuning'],kw['fault']])
            self.assertEqual(res.if_audio_unmuted,valid)
            self.assertFalse(res.tx_enabled)
    def test_46_guard_nominal(self):
        r=firm.frontend_guard(power_good=True,pll_locked_and_ready=True,requested_rx=True,pa_active=False,retuning=False,fault=False,if_filter_selected=True)
        self.assertTrue(r.receiver_path_enabled)
    def test_47_pll_guard_integration(self):
        pll=pllmod.RxPllGuard()
        def step(ms,**over):
            kw=dict(request=True,power_good=True,ref_good=True,profile_loaded=True,lock_detect=True,pa_active=False)
            kw.update(over)
            return pll.step(ms,**kw)
        step(0);step(1);step(2);step(3);pins=step(6)
        self.assertTrue(pins.audio_rx_unmuted)
        r=firm.frontend_guard(power_good=True,pll_locked_and_ready=pins.audio_rx_unmuted,requested_rx=True,pa_active=False,retuning=False,fault=False,if_filter_selected=True)
        self.assertTrue(r.if_audio_unmuted)
        pins=step(7,pa_active=True);self.assertFalse(pins.audio_rx_unmuted)
        r=firm.frontend_guard(power_good=True,pll_locked_and_ready=pins.audio_rx_unmuted,requested_rx=True,pa_active=True,retuning=False,fault=False,if_filter_selected=True)
        self.assertFalse(r.if_audio_unmuted);self.assertFalse(r.tx_enabled)
    def test_48_many_fault_combinations(self):
        rng=random.Random(6512)
        for _ in range(10000):
            fields=(bool(rng.getrandbits(1)) for _ in range(7))
            out=firm.frontend_guard(**dict(zip(('power_good','pll_locked_and_ready','requested_rx','pa_active','retuning','fault','if_filter_selected'),fields)))
            self.assertFalse(out.tx_enabled)
    def test_49_prove_channel_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            tmp=Path(d)/'channels.csv'
            orig=ROOT/'02_Piano_Frequenze/V6.4/PIANO_PLL_LO_270_RX_V6.4.csv'
            with orig.open(newline='') as f:
                rr=list(csv.DictReader(f));keys=list(rr[0].keys())
            rr[0]['lo_hz']=str(int(rr[0]['lo_hz'])+10_000)
            with tmp.open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader();writer.writerows(rr)
            with self.assertRaises(ValueError):read_pll_rows(tmp)
    def test_50_prove_tx_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            tmp=Path(d)/'channels.csv'
            orig=ROOT/'02_Piano_Frequenze/V6.4/PIANO_PLL_LO_270_RX_V6.4.csv'
            with orig.open(newline='') as f:rr=list(csv.DictReader(f));keys=list(rr[0])
            rr[0]['tx_permitted_v64']='1'
            with tmp.open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader();writer.writerows(rr)
            with self.assertRaises(ValueError):read_pll_rows(tmp)

if __name__=='__main__':unittest.main(verbosity=1)
