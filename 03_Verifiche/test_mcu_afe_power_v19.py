import re, math, json, csv, unittest
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
SCH=BASE/'04_KiCad/Modulo_MCU_CODEC_V1.9/S3900E_MCU_CODEC_AFE_V1_9_DRAFT.kicad_sch'
CSV=BASE/'07_Componenti/BOM_MCU_AUDIO_PWR_AFE_V1.9_PRELIMINARE.csv'
class V19Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.s=SCH.read_text(); cls.b=list(csv.DictReader(CSV.open()))
 def test_schematic_frame(self):
  self.assertTrue(self.s.startswith('(kicad_sch'))
  self.assertTrue(self.s.rstrip().endswith(')'))
  self.assertIn('(paper "A0")',self.s)
 def test_added_ref_unique(self):
  for ref in ['U203','U204','U205','U206','FB201','C227','C228','C229','C230','R206','R207','R208']:
   self.assertEqual(len(re.findall(r'\(property "Reference" "'+ref+r'" \(at ',self.s)),1,ref)
 def test_no_orphan_netname(self):
  self.assertNotIn('(label "5V_AUX_PROTECTED"',self.s)
  self.assertIn('(label "5V_RF_PREREGULATED"',self.s)
  self.assertIn('(label "5V_DIGITAL_FILTERED"',self.s)
 def test_four_3v3_rails(self):
  for rail in ['3V3_MCU','3V3_CODEC_IO','3V3_CODEC_LDOIN','3V3_AUDIO_CLK']:
   self.assertIn('(label "'+rail+'"',self.s)
 def test_codec_inputs_behind_cap(self):
  self.assertIn('(label "MIC_CODEC_IN"',self.s)
  self.assertIn('(label "FM_CODEC_IN"',self.s)
  for net in ['MIC_PREAMP_OUT','FM_DISCRIM_RAW']:
   self.assertIn('(label "'+net+'"',self.s)
 def test_codec_ldo_pullup(self):
  self.assertIn('(label "CODEC_LDO_SELECT"',self.s)
  d={x['ref']:x for x in self.b}
  self.assertEqual((d['R206']['net1'],d['R206']['net2']),('3V3_CODEC_IO','CODEC_LDO_SELECT'))
 def test_analog_rc(self):
  fm=1/(2*math.pi*1000*10e-9)
  mic=1/(2*math.pi*1000*4.7e-9)
  self.assertTrue(15000<fm<16000)
  self.assertTrue(33000<mic<35000)
  for f in [67,254,134.4]:
   attenuation=1/math.sqrt(1+(f/fm)**2)
   self.assertGreater(attenuation,.9998)
 def test_clk_math(self):
  self.assertEqual(48000*2*32,3072000)
  self.assertEqual(12288000//48000,256)
 def test_added_bom_unique(self):
  refs=[x['ref'] for x in self.b]
  self.assertEqual(len(refs),len(set(refs)))
  self.assertEqual(len(refs),19)
 def test_source_contract_notes(self):
  self.assertTrue((BASE/'04_KiCad/Modulo_MCU_CODEC_V1.9/Contratto_Reti_V1.9.csv').exists())
if __name__=='__main__':unittest.main(verbosity=2)
