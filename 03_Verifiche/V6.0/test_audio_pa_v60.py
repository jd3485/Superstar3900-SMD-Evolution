#!/usr/bin/env python3
"""Static design guards, not SPICE, ERC/DRC, or hardware validation."""
import csv, json, itertools, sys, importlib.util, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DES=ROOT/'01_Specifiche/V6.0/CIRCUITO_COMPONENTI_AUDIO_PA_V6.0.json'
FW=ROOT/'08_Firmware_Prototipi/V6.0/audio_controller_v60.py'
sp=importlib.util.spec_from_file_location('audio_controller_v60',FW)
m=importlib.util.module_from_spec(sp);sys.modules[sp.name]=m;sp.loader.exec_module(m)

def read():return json.loads(DES.read_text(encoding='utf-8'))
def pin(d,ref,no):
 return [p['net'] for p in d['pins'] if p['ref']==ref and p['pin']==str(no)]
def net(d,net):return {p['ref']+'.'+p['pin'] for p in d['pins'] if p['net']==net}

class V60(unittest.TestCase):
 def setUp(self):self.d=read()
 def test_01_design_nonfabrication(self):
  self.assertFalse(self.d['pcb_ready']);self.assertFalse(self.d['kicad_native']);self.assertFalse(self.d['hardware_tested'])
 def test_02_component_refs_unique(self):
  self.assertEqual(len({p['ref'] for p in self.d['parts']}),len(self.d['parts']))
 def test_03_1pin_on_1net(self):
  self.assertEqual(len({(p['ref'],p['pin']) for p in self.d['pins']}),len(self.d['pins']))
 def test_04_all_parts_have_nets(self):
  self.assertEqual({p['ref'] for p in self.d['parts']},{p['ref'] for p in self.d['pins']})
 def test_05_mux_16pins(self):self.assertEqual({int(p['pin']) for p in self.d['pins'] if p['ref']=='U601'},set(range(1,17)))
 def test_06_amp_28pins(self):self.assertEqual({int(p['pin']) for p in self.d['pins'] if p['ref']=='U604'},set(range(1,29)))
 def test_07_opamp_8pins(self):self.assertEqual({int(p['pin']) for p in self.d['pins'] if p['ref']=='U602'},set(range(1,9)))
 def test_08_mux_channel_map(self):
  for p,n in {13:'AF_AM',14:'AF_FM',15:'AF_USB',12:'AF_LSB',1:'AF_CW'}.items():self.assertEqual(pin(self.d,'U601',p),[n])
 def test_09_unused_mux_parked(self):
  for p in (2,4,5):self.assertEqual(pin(self.d,'U601',p),['VMID_AUD'])
 def test_10_mux_fail_off(self):
  self.assertEqual(pin(self.d,'U601',6),['MUX_EN_N']);self.assertIn('R601.1' if False else 'R601.1',net(self.d,'MUX_EN_N'))
  self.assertIn('R601.2',net(self.d,'3V3_AF'))
 def test_11_mux_power(self):self.assertEqual(pin(self.d,'U601',16),['3V3_AF']);self.assertEqual(pin(self.d,'U601',8),['AGND'])
 def test_12_btl_outs_positive(self):
  self.assertEqual(pin(self.d,'U604',18),pin(self.d,'U604',20));self.assertEqual(pin(self.d,'U604',18),['OUTP_RAW'])
 def test_13_btl_outs_negative(self):
  self.assertEqual(pin(self.d,'U604',23),pin(self.d,'U604',25));self.assertEqual(pin(self.d,'U604',23),['OUTN_RAW'])
 def test_14_speaker_relays_not_grounded(self):
  s=[p for p in self.d['pins'] if p['ref'] in ('J602','J603')]
  self.assertEqual(len(s),4)
  self.assertTrue(all(p['net'] not in ('AGND','PGND','DGND','SHIELD_CHASSIS') for p in s))
 def test_15_btl_switches_both(self):
  for p in ('COM_P','COM_N','NC_P','NC_N','NO_P','NO_N'):self.assertEqual(len(pin(self.d,'K601',p)),1)
  self.assertNotEqual(pin(self.d,'K601','COM_P'),pin(self.d,'K601','COM_N'))
 def test_16_amp_sd_default_low(self):
  self.assertIn('R650.1',net(self.d,'AMP_SD'));self.assertIn('R650.2',net(self.d,'AGND'))
 def test_17_power_amp_range(self):
  self.assertIn('13V8_AUD',self.d['power_domains']['power_amp_v'])
 def test_18_amp_all_pvcc(self):
  for p in (15,16,27,28):self.assertEqual(pin(self.d,'U604',p),['13V8_AUD'])
 def test_19_amp_gain_low(self):
  for p in (5,6):self.assertEqual(pin(self.d,'U604',p),['AGND'])
 def test_20_amp_four_bootstraps(self):
  for p in (17,21,22,26):self.assertTrue(pin(self.d,'U604',p)[0].startswith(('BSP_','BSN_')))
  self.assertEqual({p['ref'] for p in self.d['parts'] if p['ref'] in ('C657','C658','C659','C660')},set(('C657','C658','C659','C660')))
 def test_21_audio_codec_paths_isolated(self):
  self.assertNotEqual(pin(self.d,'J606',1),pin(self.d,'J606',2))
  self.assertEqual(pin(self.d,'J606',1),['CODEC_ADC_L']);self.assertEqual(pin(self.d,'J606',2),['CODEC_ADC_R'])
 def test_22_no_tx_signal(self):
  self.assertTrue(all('TX_ENABLE' not in p['net'] and 'TX_MOD' not in p['net'] for p in self.d['pins']))
  self.assertEqual(pin(self.d,'J606',6),['RESERVED_NO_CONNECT'])
 def test_23_pa_hardware_visible(self):self.assertEqual(pin(self.d,'J604',12),['PA_MODE_HW'])
 def test_24_speaker_jacks_distinct(self):
  self.assertNotEqual({p['net'] for p in self.d['pins'] if p['ref']=='J602'},
                      {p['net'] for p in self.d['pins'] if p['ref']=='J603'})
 def test_25_five_demodulations(self):
  self.assertEqual([pin(self.d,'J605',x)[0] for x in range(1,6)],['DEMOD_'+x for x in ['AM','FM','USB','LSB','CW']])
 def test_26_test_5_rx_modes(self):
  for rx in m.RxMode:
   o=m.control(m.Inputs(rx_mode=rx));self.assertEqual(o.mode,'RX')
   self.assertEqual(o.mux_code,m.MUX_CODES[rx]);self.assertEqual(o.amp_sd,1)
 def test_27_pa_with_ptt_audio_only(self):
  for mode in m.RxMode:
   o=m.control(m.Inputs(rx_mode=mode,pa_mode_hw=True,pa_ptt_pressed=True,tx_requested=True))
   self.assertEqual(o.dac_left,'MIC');self.assertTrue(o.relay_pa);self.assertFalse(o.rf_tx_permission)
 def test_28_pa_no_ptt_mute(self):
  o=m.control(m.Inputs(rx_mode=m.RxMode.AM,pa_mode_hw=True))
  self.assertEqual(o.amp_sd,0);self.assertEqual(o.dac_left,'MUTE')
 def test_29_pa_ch9_pa_priority(self):
  o=m.control(m.Inputs(rx_mode=m.RxMode.CW,pa_mode_hw=True,ch9=True,pa_ptt_pressed=True))
  self.assertEqual(o.mode,'PA');self.assertEqual(o.mux_enable_n,1)
 def test_30_unqualified_tx_fail(self):
  o=m.control(m.Inputs(rx_mode=m.RxMode.CW,tx_requested=True))
  self.assertEqual(o.mode,'UNQUALIFIED_TX');self.assertFalse(o.rf_tx_permission);self.assertEqual(o.amp_sd,0)
 def test_31_all_faults_mute(self):
  for name in ('power_good','codec_ready','relay_settled','transition','amp_fault','hw_amp_arm'):
   x={name: False if name in ('power_good','codec_ready','relay_settled','hw_amp_arm') else True}
   out=m.control(m.Inputs(rx_mode=m.RxMode.FM,**x));self.assertEqual(out.amp_sd,0,name)
 def test_32_exhaustive_safety(self):
  choices=[False,True]
  for mode in m.RxMode:
   for pa,ptt,ch9,tx,power,codec,relay,trans,fault,arm in itertools.product(choices,repeat=10):
    x=m.Inputs(mode,pa,ptt,ch9,tx,power,codec,relay,trans,fault,arm)
    o=m.control(x)
    self.assertFalse(o.rf_tx_permission);self.assertEqual(o.dac_right,'MUTE')
    if o.amp_sd: self.assertTrue(power and codec and relay and (not trans) and (not fault) and arm)
    if o.relay_pa:self.assertTrue(pa)
    if o.pa_audio_audible:self.assertTrue(pa and ptt)
 def test_33_bom_consistent(self):
  with (ROOT/'07_Componenti/BOM_AUDIO_PA_V6.0.csv').open(encoding='utf-8') as f: rows=list(csv.DictReader(f))
  self.assertEqual({r['Ref'] for r in rows},{p['ref'] for p in self.d['parts']})
 def test_34_netlist_consistent(self):
  with (ROOT/'01_Specifiche/V6.0/NETLIST_PIN_AUDIO_PA_V6.0.csv').open(encoding='utf-8') as f: rows=list(csv.DictReader(f))
  self.assertEqual({(r['ref'],r['pin'],r['net']) for r in rows},{(p['ref'],p['pin'],p['net']) for p in self.d['pins']})
 def test_35_file_readme_no_certification(self):
  self.assertFalse(self.d['pcb_ready']);self.assertFalse(self.d['hardware_tested'])

if __name__=='__main__':unittest.main(verbosity=1)
