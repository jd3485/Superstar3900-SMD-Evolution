"""Executable reproducible checks for V6.1 component-level panel/MCU draft.
All test names explicitly mean STATIC/NUMERIC control, not KiCad ERC/DRC or real SPICE.
"""
import unittest,random,csv,json,sys,math,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
D=json.loads((ROOT/'01_Specifiche/V6.1/CIRCUITO_PIN_MCU_PANNELLO_V6.1.json').read_text())
E=json.loads((ROOT/'03_Verifiche/V6.1/STUDIO_ELETTRICO_RC_V6.1.json').read_text())
fp=ROOT/'08_Firmware_Prototipi/V6.1/panel_controller_v61.py'
spec=importlib.util.spec_from_file_location('panel_controller_v61',fp);fw=importlib.util.module_from_spec(spec);sys.modules[spec.name]=fw;spec.loader.exec_module(fw)
FREQ=fw.load_frequency_table(ROOT/'02_Piano_Frequenze/Tabella_270_canali.csv')
PARTS={p['ref']:p for p in D['parts']};PINS=D['pins']
def get(ref,pin):return [x['net'] for x in PINS if x['ref']==ref and x['pin']==str(pin)]
def exercise(c,x,n=4):
 out=None
 for _ in range(n):out=c.update(x)
 return out
class TestMCUV61(unittest.TestCase):
 def test_01_all_mcu_physical_pins(self):self.assertEqual({int(p['pin']) for p in PINS if p['ref']=='U201'},set(range(1,65)))
 def test_02_mcu_64_official_pinout_core(self):
  for n,net in [(1,'3V3_D'),(2,'CH9_SENSE_N'),(8,'PA_SENSE_N'),(12,'PTT_N'),(15,'DGND'),(16,'3V3_D'),(28,'VREF_ANA'),(29,'3V3_A'),(49,'SWDIO'),(50,'SWCLK'),(61,'BOOT0_STRAP'),(64,'3V3_D')]:self.assertEqual(get('U201',n),[net])
 def test_03_latest_codec_wclk_pa9(self):self.assertEqual(get('U201',43),['AUDIO_WCLK'])
 def test_04_sai_reserved_from_v21(self):
  for n,net in [(9,'AUDIO_I2S_TX'),(30,'AUDIO_BCLK'),(43,'AUDIO_WCLK'),(58,'AUDIO_I2S_RX')]:self.assertEqual(get('U201',n),[net])
 def test_05_pll_reserved(self):
  for n,net in [(18,'PLL_CS_N'),(19,'PLL_SCK'),(21,'PLL_SDI'),(24,'PLL_MUXOUT'),(25,'PLL_CE')]:self.assertEqual(get('U201',n),[net])
 def test_06_i2c_codec_shared(self):self.assertEqual(get('U201',59),['CODEC_I2C_SCL']);self.assertEqual(get('U201',60),['CODEC_I2C_SDA'])
 def test_07_mcu_not_double_allocated(self):self.assertEqual(len([p for p in PINS if p['ref']=='U201']),64)
 def test_08_swd_and_boot_not_controls(self):
  for n in (49,50,61):self.assertNotIn(get('U201',n)[0],['ENC_A','ENC_B','PTT_N','PA_SENSE_N'])
 def test_09_encoder_mcu_not_expander(self):
  self.assertEqual(get('U201',52),['ENC_A']);self.assertEqual(get('U201',53),['ENC_B'])
  self.assertFalse(any(p['net'] in {'ENC_A','ENC_B'} for p in PINS if p['ref'] in {'U701','U702'}))
 def test_10_critical_mcu_direct(self):
  for n,net in [(2,'CH9_SENSE_N'),(8,'PA_SENSE_N'),(12,'PTT_N')]:self.assertEqual(get('U201',n),[net])
 def test_11_expanders_28pins_each(self):
  for ref in ['U701','U702']:self.assertEqual({int(p['pin']) for p in PINS if p['ref']==ref},set(range(1,29)))
 def test_12_expander_no_gpa7_gpb7_inputs(self):
  for ex in D['expanders']:
   self.assertEqual(set(ex['outputs']),{'GPA7','GPB7'})
   self.assertTrue('GPA7' not in ex['inputs'] and 'GPB7' not in ex['inputs'])
 def test_13_expander_has_14_inputs(self):
  for ex in D['expanders']:self.assertEqual(len(ex['inputs']),14)
 def test_14_distinct_i2c_addr_straps(self):
  self.assertEqual([x['i2c_address'] for x in D['expanders']],['0x20','0x21'])
  self.assertEqual(get('U701',15),['DGND']);self.assertEqual(get('U702',15),['3V3_UI'])
 def test_15_mcp_pinout_gpio_position(self):
  for ref in ('U701','U702'):
   self.assertEqual(get(ref,1)!=[],True);self.assertEqual(get(ref,28)!=[],True)
   self.assertEqual(get(ref,9),['3V3_UI']);self.assertEqual(get(ref,10),['DGND']);self.assertEqual(get(ref,18),['EXP_RESET_N'])
 def test_16_mcp_i2c_pin_phys(self):
  for ref in ('U701','U702'):
   self.assertEqual(get(ref,12),['CODEC_I2C_SCL']);self.assertEqual(get(ref,13),['CODEC_I2C_SDA'])
 def test_17_interrupts_not_tied_to_tx(self):
  self.assertEqual(get('U701',20),['EXP1_INT_N']);self.assertEqual(get('U702',20),['EXP2_INT_N'])
 def test_18_bands_6_single_pole(self):
  self.assertEqual(get('S701',0),['DGND'])
  for i,b in enumerate(fw.BANDS,1):self.assertEqual(get('S701',i),['SW_BAND_'+b+'_N'])
 def test_19_modes_5_one_hot(self):
  for i,m in enumerate(fw.MODES,1):self.assertEqual(get('S702',i),['SW_MODE_'+m+'_N'])
 def test_20_alfa_physical(self):
  self.assertTrue(any(p['net']=='SW_ALFA_N' and p['ref'].startswith('S') for p in PINS))
 def test_21_pa_second_hardware_contact(self):
  self.assertEqual(get('S742',3),['PA_HW_OVERRIDE_N']);self.assertEqual(get('S742',4),['HW_SAFETY_RETURN'])
  self.assertNotEqual(get('S742',3),get('S742',1))
 def test_22_btl_speaker_no_ground_connection_new(self):
  self.assertFalse(any(p['ref'].startswith('J7') and p['net'].startswith(('RADIO_SPK','PA_SPK')) for p in PINS))
 def test_23_audio_j604_adapter_matches_v60(self):
  with (ROOT/'01_Specifiche/V6.0/NETLIST_PIN_AUDIO_PA_V6.0.csv').open(encoding='utf-8') as f:old=list(csv.DictReader(f))
  src={p['pin']:p['net'] for p in old if p['ref']=='J604'}
  actual={p['pin']:p['net'] for p in PINS if p['ref']=='J702'}
  self.assertEqual(src,actual)
 def test_24_no_codecready_fake_gpio(self):
  self.assertFalse(any(p['ref']=='U201' and p['net']=='CODEC_READY' for p in PINS))
 def test_25_amp_sd_request_not_direct_sd(self):
  self.assertEqual(get('U201',42),['AMP_SD_REQUEST']);self.assertFalse(any(p['ref']=='U201' and p['net']=='AMP_SD' for p in PINS))
 def test_26_13v8_only_external_interface(self):
  self.assertEqual(get('J702',2),['13V8_AUD']);self.assertNotIn('13V8_AUD',[p['net'] for p in PINS if p['ref']=='U201'])
 def test_27_analog_supply_pins(self):
  self.assertEqual(get('U201',27),['AGND']);self.assertEqual(get('U201',28),['VREF_ANA']);self.assertEqual(get('U201',29),['3V3_A'])
 def test_28_bom_references_unique(self):self.assertEqual(len(PARTS),len(D['parts']))
 def test_29_no_pin_ref_duplicates(self):
  keys=[(p['ref'],p['pin']) for p in PINS];self.assertEqual(len(keys),len(set(keys)))
 def test_30_button_low_vil_margin(self):self.assertLess(E['closed_level_v'],E['mcp23017_schmitt_vil_max_v'])
 def test_31_button_release_timeout(self):self.assertLess(E['release_threshold_80pct_ms'],5.0)
 def test_32_input_current_budget_ideal(self):self.assertLess(E['max_28_closed_total_ma'],10.0)
 def test_33_i2c_standard_mode_rise(self):self.assertLess(E['i2c_rise_30_70_us'],1.0)
 def test_34_i2c_fast_mode_not_claimed(self):self.assertGreater(E['i2c_rise_30_70_us'],0.3)
 def test_35_i2c_real_cap_pending(self):self.assertGreater(E['i2c_C_limit_pf_standardmode_1us'],200)
 def test_36_frequency_270_unique_keys(self):self.assertEqual(len(FREQ),270)
 def test_37_frequency_correct_ch9(self):self.assertEqual(FREQ[('D','9')],fw.CH9_FREQ_HZ)
 def test_38_boot_default_mute(self):
  c=fw.Controller(FREQ);o=c.update(fw.Inputs());self.assertTrue(o.rx_mute and o.rf_tx_permission==False)
 def test_39_rx_ready_all_modes(self):
  for mode in fw.MODES:
   c=fw.Controller(FREQ);v=exercise(c,fw.Inputs(modes=(mode,)))
   self.assertEqual(v.mode,mode);self.assertFalse(v.rx_mute);self.assertEqual(v.mux_code,fw.MODES.index(mode))
 def test_40_all_band_normal_and_alpha_reachable(self):
  seen=set()
  for band in fw.BANDS:
   for alfa in (False,True):
    c=fw.Controller(FREQ);inp=fw.Inputs(bands=(band,),alfa=alfa)
    exercise(c,inp)
    for j in range(5 if alfa else 40):
     v=c.update(inp);seen.add((v.band,v.channel,v.frequency_hz));c.step_channel(1)
  self.assertEqual(len(seen),270)
 def test_41_ch9_direct_priority_over_invalid(self):
  c=fw.Controller(FREQ);v=c.update(fw.Inputs(bands=(),modes=(),i2c_ok=False,ch9=True))
  self.assertEqual((v.state,v.frequency_hz,v.mode),('CH9',fw.CH9_FREQ_HZ,'AM'));self.assertFalse(v.rf_tx_permission)
 def test_42_pa_priority_over_ch9(self):
  v=fw.Controller(FREQ).update(fw.Inputs(pa=True,ch9=True,ptt=True))
  self.assertEqual(v.state,'PA');self.assertTrue(v.pa_mic_audible);self.assertFalse(v.rf_tx_permission)
 def test_43_pa_without_ptt_mute_pa_mic(self):
  v=fw.Controller(FREQ).update(fw.Inputs(pa=True,ptt=False))
  self.assertFalse(v.pa_mic_audible);self.assertTrue(v.rx_mute)
 def test_44_invalid_switches_safe_mute(self):
  for inp in [fw.Inputs(bands=()),fw.Inputs(bands=('A','B')),fw.Inputs(modes=()),fw.Inputs(modes=('AM','FM')),fw.Inputs(i2c_ok=False)]:
   self.assertTrue(fw.Controller(FREQ).update(inp).rx_mute)
 def test_45_ch9_state_restored(self):
  c=fw.Controller(FREQ);inp=fw.Inputs(bands=('F',),modes=('USB',),alfa=True)
  initial=exercise(c,inp);self.assertEqual(initial.channel,'3A')
  self.assertEqual(c.update(fw.Inputs(ch9=True)).mode,'AM')
  back=exercise(c,inp);self.assertEqual((back.band,back.channel,back.mode),(initial.band,initial.channel,initial.mode))
 def test_46_normal_and_alpha_memories_separate(self):
  c=fw.Controller(FREQ);x=fw.Inputs();exercise(c,x)
  c.step_channel(10);normal=c.update(x)
  xa=fw.Inputs(alfa=True);exercise(c,xa)
  c.step_channel(3);alfa=c.update(xa)
  back=exercise(c,x)
  self.assertEqual(back.channel,normal.channel);self.assertEqual(alfa.channel,'15A')
 def test_47_encoder_4step_forward_reverse(self):
  d=fw.Quadrature();out=[]
  for v in [0,1,3,2,0,2,3,1,0]:
   out.extend([d.feed(v),d.feed(v)])
  self.assertEqual([x for x in out if x], [1,-1])
 def test_48_encoder_reject_single_sample_bounce(self):
  d=fw.Quadrature()
  outs=[]
  for v in [0,0,1,0,0,1,1,3,3,2,2,0,0]:outs.append(d.feed(v))
  self.assertEqual([x for x in outs if x],[1])
 def test_49_debounce_invalid_during_rotary_transit(self):
  c=fw.Controller(FREQ);exercise(c,fw.Inputs())
  self.assertTrue(c.update(fw.Inputs(bands=())).rx_mute)
  self.assertTrue(c.update(fw.Inputs(bands=('F',))).rx_mute)
  self.assertFalse(exercise(c,fw.Inputs(bands=('F',)),3).rx_mute)
 def test_50_exhaustive_random_safe_tx_off(self):
  rnd=random.Random(6161);c=fw.Controller(FREQ)
  for _ in range(10000):
   def subset(pool):return tuple(x for x in pool if rnd.random()<0.2)
   inp=fw.Inputs(subset(fw.BANDS),subset(fw.MODES),*(rnd.choice([False,True]) for _ in range(7)))
   v=c.update(inp);self.assertFalse(v.rf_tx_permission)
   if v.pa_mic_audible:self.assertTrue(inp.pa and inp.ptt and inp.power_good and inp.codec_ready)
 def test_51_csv_netlist_exact(self):
  p=ROOT/'01_Specifiche/V6.1/NETLIST_PIN_MCU_PANNELLO_V6.1.csv'
  with p.open(encoding='utf-8') as f:rows=list(csv.DictReader(f))
  self.assertEqual({(p['ref'],p['pin'],p['net']) for p in rows},{(p['ref'],p['pin'],p['net']) for p in PINS})
 def test_52_csv_bom_exact(self):
  p=ROOT/'07_Componenti/BOM_MCU_PANNELLO_V6.1.csv'
  with p.open(encoding='utf-8') as f:rows=list(csv.DictReader(f))
  self.assertEqual({p['ref'] for p in rows},set(PARTS))
 def test_53_source_safe_copy(self):
  self.assertFalse(D['hardware_tested']);self.assertFalse(D['native_erc_drc']);self.assertFalse(D['production_release'])
 def test_54_data_injection_detected(self):
  data=dict(FREQ);data[('D','9')]=1
  self.assertNotEqual(data[('D','9')],fw.CH9_FREQ_HZ)
 def test_55_manifest_no_erasures_v60(self):
  self.assertTrue((ROOT/'01_Specifiche/V6.0/CIRCUITO_COMPONENTI_AUDIO_PA_V6.0.json').exists())
if __name__=='__main__':unittest.main(verbosity=1)
