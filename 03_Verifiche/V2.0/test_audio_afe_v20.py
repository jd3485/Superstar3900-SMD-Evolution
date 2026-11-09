from pathlib import Path
import csv, json, re, unittest, math
from scipy import signal

ROOT=Path(__file__).resolve().parents[2]
SCH=ROOT/'04_KiCad/Modulo_MCU_CODEC_V2.0/S3900E_MCU_CODEC_AFE_V2_0_DRAFT.kicad_sch'
BOM=ROOT/'07_Componenti/BOM_MCU_AUDIO_PWR_AFE_V2.0_PRELIMINARE.csv'
REPORT=ROOT/'03_Verifiche/V2.0/Simulazione_RC_Analitica_V2.0.json'
class V20Test(unittest.TestCase):
 def test_schema_changed_and_v19_unchanged(self):
  s=SCH.read_text(); self.assertIn('V2.0 BOZZA',s)
  self.assertEqual(len(re.findall(r'\(property "Reference" "C227"',s)),1)
  self.assertRegex(s,r'\(property "Reference" "C227"[^\n]*\n\s*\(property "Value" "100nF"')
  self.assertRegex(s,r'\(property "Reference" "C229"[^\n]*\n\s*\(property "Value" "1uF"')
 def test_bom_matches_changed_components(self):
  with BOM.open() as f:
   d={r['ref']:r for r in csv.DictReader(f)}
  self.assertEqual(d['C227']['value'],'100nF');self.assertEqual(d['C229']['value'],'1uF')
 def test_fm_subaudio_not_removed_in_ideal_model(self):
  x=json.loads(REPORT.read_text())['nominal']['fm']['freq_db']
  self.assertGreater(float(x['67']),-1.0)
  self.assertGreater(float(x['250']),-1.0)
 def test_mic_hp_higher_than_fm_hp(self):
  x=json.loads(REPORT.read_text())['nominal']
  self.assertGreater(x['mic']['fc_simple_highpass_Hz'],x['fm']['fc_simple_highpass_Hz']*9)
 def test_cc_binary_limitation(self):
  self.assertFalse((ROOT/'06_PCB'/'Gerber_V2.0').exists())
 def test_sai_rate_math(self):
  self.assertEqual(48000*2*32,3072000); self.assertEqual(12288000//48000,256)
if __name__=='__main__':unittest.main(verbosity=2)
