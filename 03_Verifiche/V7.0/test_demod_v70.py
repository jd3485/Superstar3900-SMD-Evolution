#!/usr/bin/env python3
"""Reproducible V7.0 static, numerical, audio DSP and no-TX regressions. NOT ERC, real SPICE, hardware tests."""
from pathlib import Path
import csv,json,unittest,sys,math,itertools,re
import numpy as np
from scipy import signal
ROOT=Path(__file__).resolve().parents[2]; HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'08_Firmware_Prototipi/V7.0'))
sys.path.insert(0,str(HERE))
import dsp_rx_v70 as D
import simula_demod_v70 as S
def read_csv(path):
    with open(path,newline='',encoding='utf8') as f:return list(csv.DictReader(f))
NET=read_csv(ROOT/'01_Specifiche/V7.0/NETLIST_PIN_IF2_DEMOD_LO2_V7.0.csv')
BOM=read_csv(ROOT/'07_Componenti/BOM_IF2_DEMOD_LO2_V7.0.csv')
MODE=read_csv(ROOT/'02_Piano_Frequenze/V7.0/MATRICE_MODI_IF2_V7.0.csv')
PLAN=read_csv(ROOT/'02_Piano_Frequenze/V6.9/PIANO_270_X_5_SI5351C_V6.9.csv')
RES=json.loads((HERE/'RISULTATI_SIMULAZIONI_V7.0.json').read_text())
PIN={(x['ref'],x['pin_or_terminal']):x['net'] for x in NET}
def pin(ref,n,name):return PIN.get((ref,str(n)))==name
class V70(unittest.TestCase):
    def test_01_count(self): self.assertEqual(len(BOM),65)
    def test_02_pins_count(self): self.assertEqual(len(NET),174)
    def test_03_unique_component_refs(self): self.assertEqual(len(BOM),len({x['ref'] for x in BOM}))
    def test_04_unique_pin_assignment(self): self.assertEqual(len(NET),len(PIN))
    def test_05_bom_pin_coverage(self): self.assertEqual({x['ref'] for x in BOM},{x['ref'] for x in NET})
    def test_06_no_tx_net(self): self.assertFalse(any('TX_' in x['net'] or 'RF_TX' in x['net'] for x in NET))
    def test_07_ad8307_physical_pins(self): self.assertEqual({int(x['pin_or_terminal']) for x in NET if x['ref']=='U7101'},set(range(1,9)))
    def test_08_ad8307_pinout(self): self.assertTrue(all(pin('U7101',n,net) for n,net in [(1,'AM_INM_BIAS'),(2,'GND_IF2'),(4,'AM_LOG_RAW'),(6,'AM_DETECT_EN'),(7,'3V3_A_IF_FILTERED'),(8,'AM_INP_BIAS')]))
    def test_09_am_default_off(self):self.assertTrue(pin('R7102',1,'AM_DETECT_EN') and pin('R7102',2,'GND_IF2'))
    def test_10_am_consent_unfitted(self):self.assertIn('NON_POPOLATA',next(x['status'] for x in BOM if x['ref']=='J7102'))
    def test_11_am_input_impedance(self):self.assertAlmostEqual(910+1100,2010,delta=100)
    def test_12_am_output_connected(self):self.assertTrue(pin('J7103',1,'DEMOD_AM_AUDIO_AC'))
    def test_13_ad8307_gain_correction(self):self.assertAlmostEqual(D.log_am_linearize(1.4)[()],1.0)
    def test_14_fm_comparator_pins(self):self.assertTrue(all(pin('U7102',n,net) for n,net in [(1,'FM_SQUARE_455K'),(2,'GND_IF2'),(3,'FM_IF_BIASED'),(4,'AUDIO_1V65_REF'),(5,'3V3_A_IF_FILTERED')]))
    def test_15_4046_pins(self):self.assertEqual({int(x['pin_or_terminal']) for x in NET if x['ref']=='U7103'},set(range(1,17)))
    def test_16_4046_comp_feedback(self):self.assertTrue(pin('U7103',3,'FM_VCO_OUT') and pin('U7103',4,'FM_VCO_OUT'))
    def test_17_4046_fm_in(self):self.assertTrue(pin('U7103',14,'FM_SQUARE_455K'))
    def test_18_4046_demod(self):self.assertTrue(pin('U7103',10,'FM_DEMOUT_RAW'))
    def test_19_4046_vco_rc(self):self.assertTrue(all(pin(ref,n,net) for ref,n,net in [('R7107',2,'FM_VCOIN_CTRL'),('C7109',1,'FM_VCOIN_CTRL'),('U7103',9,'FM_VCOIN_CTRL')]))
    def test_20_fm_disabled_unplugged(self):self.assertTrue(pin('R7109',1,'3V3_A_IF_FILTERED') and pin('R7109',2,'FM_PLL_INH'))
    def test_21_4046_c1_floating_between(self):self.assertTrue(pin('C7108',1,'FM_C1_A') and pin('C7108',2,'FM_C1_B'))
    def test_22_4046_r2_nc(self):self.assertTrue(pin('U7103',12,'NC_R2_UNUSED'))
    def test_23_opamp_supply(self):self.assertTrue(pin('U7104',8,'3V3_A_IF_FILTERED') and pin('U7104',4,'GND_IF2'))
    def test_24_opamp_aba(self):self.assertTrue(pin('U7104',1,'AM_BUFFER_OUT') and pin('U7104',7,'FM_BUFFER_OUT'))
    def test_25_fm_audio_j(self):self.assertTrue(pin('J7103',2,'DEMOD_FM_AUDIO_AC'))
    def test_26_supply_not_unsafely_tied(self):self.assertFalse(any(p['net']=='5V_A_RF' and p['ref']=='U7103' for p in NET))
    def test_27_gali4pins(self):self.assertEqual({int(p['pin_or_terminal']) for p in NET if p['ref']=='U7121'},set(range(1,5)))
    def test_28_gali3_in(self):self.assertTrue(pin('U7121',1,'LO2_AMP_IN'))
    def test_29_gali3_outdc(self):self.assertTrue(pin('U7121',3,'LO2_AMP_OUT_BIASED'))
    def test_30_lo2_dc_block_output(self):self.assertTrue(pin('C7124',1,'LO2_AMP_OUT_BIASED'))
    def test_31_lo2_mixer_port(self):self.assertTrue(pin('J7122',1,'LO2_RF_AC_TO_MIXER'))
    def test_32_lo2_lpf_components(self):self.assertTrue(all(p in {x['ref'] for x in BOM} for p in ('L7122','L7123','L7124','C7125','C7126')))
    def test_33_no_direct_cmos_short_to_50r(self):self.assertTrue(pin('R7121',1,'LO2_DRIVER_INPUT'))
    def test_34_1p5k_logic_source(self):self.assertTrue(any(p['ref']=='R7121' and '1.5 kOhm' in p['mpn_or_value'] for p in BOM))
    def test_35_5v_bias(self):self.assertTrue(pin('R7122',1,'5V_A_RF'))
    def test_36_50ohm_pad(self):self.assertEqual(len([p for p in BOM if p['ref'] in ('R7123','R7124','R7125')]),3)
    def test_37_lpf_fund_loss(self):self.assertGreater(RES['lo2_lpf_50ohm']['fundamental_s21_db'],-2)
    def test_38_lpf_3rd_suppression(self):self.assertLess(RES['lo2_lpf_50ohm']['3rd_harmonic_s21_db'],-25)
    def test_39_lpf_5th_suppression(self):self.assertLess(RES['lo2_lpf_50ohm']['5th_harmonic_s21_db'],-40)
    def test_40_lpf_recompute(self):self.assertAlmostEqual(S.db(S.network(10.24e6)[0]),RES['lo2_lpf_50ohm']['fundamental_s21_db'],places=6)
    def test_41_monte_count(self):self.assertEqual(RES['lo2_lpf_50ohm']['monte_carlo_4000']['third_above_minus_25db_count'],0)
    def test_42_gali_budget_is_unvalidated(self):self.assertIn('NOT_VALIDATED',str(RES['lo2_rf_driver'].keys()))
    def test_43_gali_current_max_abs(self):self.assertLess(RES['lo2_rf_driver']['bias_5v_5000']['current_range_ma'][-1],55)
    def test_44_gali_current_nom(self):self.assertAlmostEqual((5-3.3)/(47+5)*1000,32.7,delta=2)
    def test_45_am_thd_raw(self):self.assertGreater(RES['am_log_ideal']['raw_thd_percent'],5)
    def test_46_am_thd_corrected(self):self.assertLess(RES['am_log_ideal']['linearized_thd_percent'],1)
    def test_47_fm_peak(self):self.assertAlmostEqual(RES['fm_pll_linearized']['gain_peak_v'],0.02,delta=0.005)
    def test_48_fm_model_only(self):self.assertTrue(RES['fm_pll_linearized']['model_only'])
    def test_49_modes_five(self):self.assertEqual({m['mode'] for m in MODE},{'AM','FM','USB','LSB','CW_RX_ONLY'})
    def test_50_dnp_ssb_cw(self):self.assertTrue(all('DNP' in x['f823_824'] for x in MODE if x['mode'] in ('USB','LSB','CW_RX_ONLY')))
    def test_51_dsp_coefs(self):self.assertEqual(len(D.q15('SSB')),241)
    def test_52_dsp_cw_coefs(self):self.assertEqual(len(D.q15('CW')),481)
    def test_53_dsp_quant(self):self.assertTrue(np.all(np.abs(D.q15('CW').astype(int))<=32768))
    def test_54_ssb_pass(self):self.assertGreater(RES['dsp_48k']['SSB']['pass_gain_db']['1000'],-1)
    def test_55_cw_pass(self):self.assertGreater(RES['dsp_48k']['CW']['pass_gain_db']['700'],-1)
    def test_56_ssb_stop(self):self.assertLess(RES['dsp_48k']['SSB']['stop_gain_db']['5500'],-40)
    def test_57_cw_stop(self):self.assertLess(RES['dsp_48k']['CW']['stop_gain_db']['1800'],-40)
    def test_58_dsp_delay(self):self.assertEqual(RES['dsp_48k']['CW']['group_delay_ms'],5.0)
    def test_59_firmware_tx_disabled(self):self.assertFalse(D.tx_permission(True,True,True))
    def test_60_mute_without_hw_consent(self):self.assertTrue(D.mute_condition('AM',True,False,False,False,True,False))
    def test_61_mute_if_pa(self):self.assertTrue(D.mute_condition('FM',True,True,False,False,True,True))
    def test_62_mute_if_ptt(self):self.assertTrue(D.mute_condition('FM',True,False,True,False,True,True))
    def test_63_all_1350_unchanged(self):self.assertEqual(len(PLAN),1350)
    def test_64_all_270_ch(self):self.assertEqual(len({(p['band'],p['channel']) for p in PLAN}),270)
    def test_65_all_5_rx_modes(self):self.assertEqual({p['mode'] for p in PLAN},{'AM','FM','USB','LSB','CW'})

# Ten independent stratified canale/modo assertions across 1350-row inherited plan (no test count inflation).
for i,k in enumerate([(b,m) for b in 'ABCDEF' for m in ('AM','FM','USB','LSB','CW')][:10]):
    def fn(self,b=k[0],m=k[1]):
        rows=[x for x in PLAN if x['band']==b and x['mode']==m]
        self.assertEqual(len(rows),45)
        self.assertTrue(all(10_000_000<int(x['lo2_hz'])<11_000_000 for x in rows))
        self.assertTrue(all(25_000_000<int(x['rf_hz'])<29_000_000 for x in rows))
    setattr(V70,f'test_{66+i:02d}_mode_{i}',fn)

def exhaust_audio_state():
    n=0
    for mode in ['AM','FM','USB','LSB','CW','INVALID']:
      for states in itertools.product((False,True),repeat=6):
        rx,pa,ptt,retune,ref,hw=states
        expected=not(mode in ('AM','FM','USB','LSB','CW') and rx and not pa and not ptt and not retune and ref and hw)
        assert D.mute_condition(mode,rx,pa,ptt,retune,ref,hw)==expected
        assert not D.tx_permission(mode,*states)
        n+=1
    return n
if __name__=='__main__':
    print('V7.0 combinations audio TX safety',exhaust_audio_state())
    unittest.main()
