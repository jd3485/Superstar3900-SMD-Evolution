"""V2.3 regression: purely linearized arithmetic, no PCB approval."""
import unittest, sys, json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from rx_cascade_v23 import Stage, passive, lna, mixer, cascade, CONFIGS, run_all

class TestCascade(unittest.TestCase):
 def test_passive_is_nf(self):self.assertAlmostEqual(cascade([passive('x',3)])['NF_dB'],3,places=9)
 def test_ideal_stage(self):self.assertAlmostEqual(cascade([Stage('ideal',10,0)])['NF_dB'],0,places=9)
 def test_cascade_friis_two_amps(self):
  q=cascade([Stage('a',10,3),Stage('b',10,3)]);self.assertAlmostEqual(q['NF_dB'],10*__import__('math').log10(1+(.0+10**(.3)-1)+(10**(.3)-1)/10),places=6)
 def test_iip3_one(self):self.assertAlmostEqual(cascade([Stage('a',10,3,17)])['IIP3_dBm'],17,places=9)
 def test_iip3_two_identical(self):
  from math import log10
  r=cascade([Stage('a',0,0,10),Stage('b',0,0,10)])
  self.assertAlmostEqual(r['IIP3_dBm'],10-10*log10(2),places=7)
 def test_nf_baseline_above_split(self):
  self.assertGreater(cascade(CONFIGS['A_v22_pre4p5_5536'])['NF_dB'],cascade(CONFIGS['B_split_5536'])['NF_dB'])
 def test_pad_improves_ip3(self):
  self.assertGreater(cascade(CONFIGS['D_split_5535_pad6'])['IIP3_dBm'],cascade(CONFIGS['C_split_5535'])['IIP3_dBm'])
 def test_pad_worsens_nf(self):
  self.assertGreater(cascade(CONFIGS['D_split_5535_pad6'])['NF_dB'],cascade(CONFIGS['C_split_5535'])['NF_dB'])
 def test_bypass_nf_worse(self):
  self.assertGreater(cascade(CONFIGS['F_lna_bypass_v22'])['NF_dB'],cascade(CONFIGS['C_split_5535'])['NF_dB'])
 def test_v22_initial_limit_not_met(self):self.assertGreater(cascade(CONFIGS['A_v22_pre4p5_5536'])['NF_dB'],6)
 def test_split_5535_target_preliminary(self):
  r=cascade(CONFIGS['C_split_5535']);self.assertLess(r['NF_dB'],6);self.assertGreater(r['IIP3_dBm'],0)
 def test_higher_lo_mixer_not_compatible(self):
  self.assertEqual(CONFIGS['G_split_5535_ADE1H_UNAVAILABLE_LO'][-1].name,'ADE-1H+ (LO +17dBm)')
 def test_report(self):
  run_all();d=json.loads((Path(__file__).resolve().parent/'Risultati_Catena_RX_V2.3.json').read_text())
  self.assertEqual(len(d['results']),7)
  self.assertIn('CANNOT be carried over',' '.join(d['assumptions']))

if __name__=='__main__':unittest.main(verbosity=2)
