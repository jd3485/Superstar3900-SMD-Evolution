#!/usr/bin/env python3
"""Unit tests for a *static* 31-pin PCB-to-schematic mapping, NOT KiCad ERC."""
import csv, hashlib, importlib.util, io, json, unittest, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('sync_v44',HERE/'sincronizza_schema_rx_v44.py')
m=importlib.util.module_from_spec(s)
sys.dont_write_bytecode=True
try:s.loader.exec_module(m)
finally:sys.dont_write_bytecode=False

class TestV44(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.text,cls.rows,cls.parts=m.new_schematic_text()
 def test_01_board_sha(self):self.assertEqual(hashlib.sha256(m.PCB.read_bytes()).hexdigest(),m.SRC_SHA)
 def test_02_part_count(self):self.assertEqual(len(self.parts),15)
 def test_03_pin_count(self):self.assertEqual(len(self.rows),31)
 def test_04_unique_nets(self):self.assertEqual(len(set(x['net'] for x in self.rows)),8)
 def test_05_no_duplicate_ref_pin(self):self.assertEqual(len({(x['reference'],x['pin']) for x in self.rows}),31)
 def test_06_original_study_mapping_equal(self):self.assertEqual(m.parse_pcb(m.PCB),m.parse_pcb(m.PCB43))
 def test_07_original_schematic_not_modified(self):self.assertIn('V3_1_Python_DRAFT',m.OLD_SCHEM.read_text())
 def test_08_static_validation(self):self.assertTrue(m.validate_schematic(self.text,self.rows,self.parts)['all_pin_nets_match'])
 def test_09_reproducibility(self):self.assertEqual(self.text,m.new_schematic_text()[0])
 def test_10_footprints_mapped(self):self.assertTrue(m.validate_schematic(self.text,self.rows,self.parts)['footprint_ids_match'])
 def test_11_detect_wrong_net_label(self):
  wrong=self.text.replace('(label "RF_LNA_INPUT"','(label "WRONG_NET"',1)
  with self.assertRaises(AssertionError):m.validate_schematic(wrong,self.rows,self.parts)
 def test_12_detect_wrong_footprint(self):
  wrong=self.text.replace('(property "Footprint" "S3900E_V38_Review:', '(property "Footprint" "INVALID_LIB:',1)
  with self.assertRaises(AssertionError):m.validate_schematic(wrong,self.rows,self.parts)
 def test_13_detect_wrong_bom_value(self):
  wrong=self.text.replace('(property "Value" "100nF"','(property "Value" "999nF"',1)
  with self.assertRaises(AssertionError):m.validate_schematic(wrong,self.rows,self.parts)
 def test_14_stored_schematic_matches_builder(self):self.assertEqual(m.NEW.read_text(),self.text)
 def test_15_stored_csv_maps_pins(self):
  with (HERE/'NETMAP_RX_PCB_V4.4.csv').open(newline='') as f: self.assertEqual(list(csv.DictReader(f)),self.rows)
 def test_16_safety_flags_false(self):
  info=json.loads((HERE/'VERIFICA_SCHEMA_PCB_V4.4.json').read_text())
  for k in ['native_erc_executed','native_drc_executed','schematic_pcb_uuid_links_verified','cad_te_approved','thermal_approved']:
   self.assertIs(info[k],False)
 def test_17_pin_mapping_L101(self):
  net={(r['reference'],r['pin']):r['net'] for r in self.rows}
  self.assertEqual(net['L101','1'],'+5V_BENCH')
  self.assertEqual(net['L101','2'],'RF_BIAS_OUT')
 def test_18_pin_mapping_AMP(self):
  net={(r['reference'],r['pin']):r['net'] for r in self.rows}
  self.assertEqual((net['U101','1'],net['U101','2'],net['U101','3']),('RF_LNA_IC_IN','GND_RF','RF_BIAS_OUT'))
 def test_19_pad_terminals(self):
  net={(r['reference'],r['pin']):r['net'] for r in self.rows}
  self.assertEqual((net['R203','1'],net['R203','2']),('RF_ATTEN_IN','RF_ATTEN_OUT'))
 def test_20_PCB_baseline_unmodified(self):
  self.assertIn('NO FAB',m.PCB.read_text())
if __name__=='__main__':unittest.main(verbosity=2)
