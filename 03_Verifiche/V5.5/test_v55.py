#!/usr/bin/env python3
"""V5.5 unit tests: geometry screen and structured JSON parser, NOT native KiCad."""
from pathlib import Path
import sys,unittest,json,tempfile,copy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_rame_v55 import PCB,audit,actual_board_copper
from validate_native_reports_v55 import check_json,validate_folder
BOARD=PCB.read_text()
class CopperScreen(unittest.TestCase):
 def test_native_board_statically_clean(self):
  r=audit(BOARD);self.assertEqual(r['status'],'STATIC_SCREEN_PASS');self.assertFalse(r['fabrication_allowed'])
 def test_counts(self):
  r=audit(BOARD);self.assertEqual(r['geometry_counts'],{'pads':44,'segments':44,'vias':70,'zones':4,'filled_zone_polygons':0})
 def test_exact_minimum(self):
  r=audit(BOARD);self.assertAlmostEqual(r['minimum_cross_net_clearance']['clearance_mm'],.45,places=3)
 def test_no_native_claim(self):
  r=audit(BOARD);self.assertEqual(r['native_drc'],'NOT_RUN');self.assertEqual(r['zone_refill'],'NOT_RUN')
 def test_short_mutation_detected(self):
  original='(start 28.000 36.000) (end 51.450 36.000) (width 0.280) (layer "F.Cu") (net 2)'
  self.assertIn(original,BOARD)
  r=audit(BOARD.replace(original,original.replace('(net 2)','(net 1)'),1))
  self.assertEqual(r['status'],'STATIC_SCREEN_FAIL')
  self.assertAlmostEqual(r['minimum_cross_net_clearance']['clearance_mm'],0.0)
 def test_threshold_is_effective(self):
  r=audit(BOARD,threshold=.5);self.assertEqual(r['status'],'STATIC_SCREEN_FAIL')
 def test_anomalous_pad_parse_fails_closed(self):
  mutated=BOARD.replace('(pad "1" smd circle','(pad "1" smd unknownshape',1)
  with self.assertRaises(ValueError):audit(mutated)
 def test_same_board_deterministic(self):
  a=audit(BOARD);b=audit(BOARD);self.assertEqual(a,b)
 def test_net_pins_through_vias_count(self):
  objects,_,_=actual_board_copper(BOARD)
  self.assertEqual(sum(i['kind']=='via' for i in objects),70)
 def test_limited_to_one_layer(self):
  self.assertEqual(audit(BOARD)['layer'],'F.Cu')
class NativeSemantic(unittest.TestCase):
 def erc(self):
  return {'$schema':'https://schemas.kicad.org/erc.v1.json','source':'study.kicad_sch','kicad_version':'10.0.8',
          'sheets':[{'path':'/','violations':[]}],'included_severities':['error','warning','exclusion']}
 def drc(self):
  return {'$schema':'https://schemas.kicad.org/drc.v1.json','source':'study.kicad_pcb','kicad_version':'10.0.8',
          'violations':[],'unconnected_items':[],'schematic_parity':[],'included_severities':['error','warning','exclusion']}
 def test_erc_schema(self):self.assertEqual(check_json(self.erc(),'erc')[0],[])
 def test_drc_schema(self):self.assertEqual(check_json(self.drc(),'drc')[0],[])
 def test_erc_detects_violations(self):
  r=self.erc();r['sheets'][0]['violations']=[{'type':'pin_to_pin'}]
  self.assertIn('ERC_VIOLATIONS_NONEMPTY',check_json(r,'erc')[0])
 def test_drc_unconnected_detected(self):
  r=self.drc();r['unconnected_items']=[{'type':'unconnected'}]
  self.assertIn('UNCONNECTED_ITEMS_NONEMPTY',check_json(r,'drc')[0])
 def test_drc_parity_detected(self):
  r=self.drc();r['schematic_parity']=[{'type':'mismatch'}]
  self.assertIn('SCHEMATIC_PARITY_NONEMPTY',check_json(r,'drc')[0])
 def test_drc_normal_violations_detected(self):
  r=self.drc();r['violations']=[{'severity':'error'}]
  self.assertIn('VIOLATIONS_NONEMPTY',check_json(r,'drc')[0])
 def test_rejects_old_version(self):
  r=self.drc();r['kicad_version']='9.0.10';self.assertIn('KICAD10_VERSION_MISSING',check_json(r,'drc')[0])
 def test_rejects_fake_v54_stub(self):
  self.assertTrue(check_json({'source':'MOCK_NOT_NATIVE','violations':[]},'drc')[0])
 def test_rejects_missing_array(self):
  r=self.drc();del r['schematic_parity'];self.assertIn('SCHEMATIC_PARITY_ARRAY_MISSING',check_json(r,'drc')[0])
 def test_unavailable_folder_blocked(self):
  with tempfile.TemporaryDirectory() as d:
   r=validate_folder(d);self.assertFalse(r['fabrication_allowed']);self.assertNotEqual(r['status'],'STRUCTURE_CHECK_PASS_REVIEW_REQUIRED')
 def test_inconsistent_status_blocked(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);s={'source_unchanged':True,'release':'BLOCKED_NOT_FOR_FAB','fab_authorized':False,
       'native_erc':'EXECUTED_REVIEW_REQUIRED','native_drc':'EXECUTED_REVIEW_REQUIRED',
       'native_erc_exit_code':5,'native_drc_exit_code':0}
   (p/'STATUS_V5.4.json').write_text(json.dumps(s));(p/'ERC_V5.4.json').write_text(json.dumps(self.erc()))
   (p/'DRC_PARITY_V5.4.json').write_text(json.dumps(self.drc()))
   r=validate_folder(p);self.assertIn('STATUS_ERC_NOT_EXECUTED_CLEAN',r['issues'])
 def test_fake_clean_structural_only(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);s={'source_unchanged':True,'release':'BLOCKED_NOT_FOR_FAB','fab_authorized':False,
       'native_erc':'EXECUTED_REVIEW_REQUIRED','native_drc':'EXECUTED_REVIEW_REQUIRED',
       'native_erc_exit_code':0,'native_drc_exit_code':0}
   (p/'STATUS_V5.4.json').write_text(json.dumps(s));(p/'ERC_V5.4.json').write_text(json.dumps(self.erc()))
   (p/'DRC_PARITY_V5.4.json').write_text(json.dumps(self.drc()))
   r=validate_folder(p);self.assertEqual(r['status'],'STRUCTURE_CHECK_PASS_REVIEW_REQUIRED')
   self.assertEqual(r['provenance'],'NOT_VERIFIED_BY_JSON_ALONE')
   self.assertFalse(r['fabrication_allowed'])
if __name__=='__main__':unittest.main(verbosity=2)
