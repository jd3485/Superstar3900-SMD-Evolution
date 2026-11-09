#!/usr/bin/env python3
"""V5.3 independent static audit regression tests (NOT KiCad ERC/DRC)."""
import tempfile,unittest,shutil
from pathlib import Path
from audit_indipendente_v53 import RX,ST,extract,check_footprint_libraries,parse
S=(RX/(ST+'.kicad_sch')).read_text()
B=(RX/(ST+'.kicad_pcb')).read_text()

class TestStaticV53(unittest.TestCase):
 def test_clean(self):
  r=extract(S,B);self.assertFalse(r['errors'] or r['warnings'])
 def test_31_pin_nets(self):self.assertEqual(extract(S,B)['sch_pins'],31)
 def test_31_wires(self):self.assertEqual(extract(S,B)['wires'],31)
 def test_31_labels(self):self.assertEqual(extract(S,B)['labels'],31)
 def test_15_components(self):self.assertEqual(len(extract(S,B)['schematic_pin_nets']),15)
 def test_15_footprints(self):self.assertEqual(len(extract(S,B)['pcb_pad_nets']),15)
 def test_8_nets(self):
  r=extract(S,B)
  nets={net for x in r['schematic_pin_nets'].values() for net in x['nets'].values()}
  self.assertEqual(len(nets),8)
 def test_sma_multiple_ground_pads(self):
  r=extract(S,B)
  for name in ('J101','J102','J103','J104'):
   self.assertEqual(r['pcb_pad_nets'][name]['nets']['2'],['GND_RF'])
 def test_local_libraries_match(self):self.assertEqual(check_footprint_libraries(B),[])
 def test_bad_board_net_is_detected(self):
  orig='(net 2 "RF_LNA_INPUT") (tstamp'
  self.assertIn(orig,B)
  r=extract(S,B.replace(orig,'(net 2 "ERRATA_V53") (tstamp',1))
  self.assertTrue(any(x[0]=='PIN-NET' for x in r['errors']))
 def test_bad_wire_endpoint_is_detected(self):
  broken=S.replace('(xy 35.160 70.000)','(xy 35.150 70.000)',1)
  self.assertNotEqual(S,broken)
  self.assertTrue(extract(broken,B)['warnings'])
 def test_bad_schematic_label_is_detected(self):
  orig='(label "RF_LNA_IC_IN" (at 65.160 70.000 0)'
  self.assertIn(orig,S)
  broken=S.replace(orig,'(label "RF_TEST_CORROTTA" (at 65.160 70.000 0)',1)
  self.assertTrue(any(x[0]=='PIN-NET' for x in extract(broken,B)['errors']))
 def test_wrong_component_value_is_detected(self):
  orig='(property "Value" "ADL5535"'
  self.assertIn(orig,B)
  broken=B.replace(orig,'(property "Value" "ADL9999"',1)
  self.assertTrue(any(x[0]=='value' for x in extract(S,broken)['errors']))
 def test_wrong_footprint_is_detected(self):
  orig='(footprint "S3900E_v33:C_0402"'
  self.assertIn(orig,B)
  broken=B.replace(orig,'(footprint "S3900E_v33:INVENTED"',1)
  self.assertTrue(any(x[0]=='footprint' for x in extract(S,broken)['errors']))
 def test_invalid_uuid_link_is_detected(self):
  orig='(path "/8a793700-1a2e-43d4-83b4-94186f9d58c2/'
  self.assertIn(orig,B)
  broken=B.replace(orig,'(path "/00000000-0000-0000-0000-000000000000/',1)
  self.assertTrue(any(x[0]=='path' for x in extract(S,broken)['errors']))
 def test_unbalanced_s_expression_is_rejected(self):
  with self.assertRaises(Exception):parse('(kicad_sch (uuid "broken")')
 def test_trailing_tokens_are_rejected(self):
  with self.assertRaises(Exception):parse('(x) (y)')
 def test_footprint_library_geometry_corruption_is_detected(self):
  import audit_indipendente_v53 as audit
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)
   for pretty in RX.glob('*.pretty'):
    shutil.copytree(pretty,root/pretty.name)
   target=root/'S3900E_V38_Review.pretty/CONSMA002_SMD_SHAPED_REVIEW.kicad_mod'
   s=target.read_text();self.assertIn('(size 2.050 2.050)',s)
   target.write_text(s.replace('(size 2.050 2.050)','(size 2.060 2.050)',1))
   old= audit.RX
   try:
    audit.RX=root
    bad=check_footprint_libraries(B)
    self.assertTrue(any(x['ref']=='J101' for x in bad))
   finally:audit.RX=old

if __name__=='__main__':unittest.main(verbosity=2)
