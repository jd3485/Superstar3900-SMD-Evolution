#!/usr/bin/env python3
"""SMA V4.3 hypothesis regression. Never claim KiCad or TE signoff."""
import importlib.util,unittest,sys
from pathlib import Path
P=Path(__file__).with_name('crea_e_verifica_candidato_sma_v43.py')
s=importlib.util.spec_from_file_location('s3900gen43',P);m=importlib.util.module_from_spec(s)
sys.dont_write_bytecode=True;s.loader.exec_module(m)
class VerifyV43(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=m.run(write=False)
    def test_baseline_sha(self):self.assertEqual(self.r['source_sha256'],m.EXPECTED_SHA)
    def test_changes_not_identical(self):self.assertNotEqual(self.r['candidate_sha256'],self.r['source_sha256'])
    def test_candidate_matches_work_file(self):self.assertEqual(self.r['candidate_sha256'],__import__('hashlib').sha256(m.CANDIDATE.read_bytes()).hexdigest())
    def test_16_pads_only(self):self.assertTrue(self.r['edits_exactly_16_ground_pad_centers'])
    def test_span_before(self):self.assertTrue(all(s['local_ground_span_mm']==7.4 for s in self.r['original']['sma'].values()))
    def test_span_after(self):self.assertTrue(all(s['local_ground_span_mm']==7.76 for s in self.r['candidate']['sma'].values()))
    def test_other_components_count(self):self.assertEqual(self.r['original']['board_footprints'],self.r['candidate']['board_footprints'])
    def test_trace_count_untouched(self):self.assertEqual(self.r['original']['segments'],self.r['candidate']['segments'])
    def test_via_count_untouched(self):self.assertEqual(self.r['original']['vias'],self.r['candidate']['vias'])
    def test_zones_unfilled(self):self.assertEqual(self.r['candidate']['unfilled_zones'],4)
    def test_net_count(self):self.assertEqual(self.r['original']['nets'],self.r['candidate']['nets'])
    def test_clearance_nominal(self):self.assertAlmostEqual(self.r['candidate']['minimum_inter_net_gap_FCu_mm'],.45)
    def test_no_short_under_review_threshold(self):self.assertEqual(self.r['candidate']['pairs_under_0p20mm'],0)
    def test_ground_pads_path_to_vias(self):self.assertEqual(self.r['candidate']['ground_pads_without_via_path'],[])
    def test_signal_islands(self):self.assertTrue(all(n['islands']==1 for n in self.r['candidate']['signal_nets']))
    def test_four_sma(self):self.assertEqual(set(self.r['candidate']['sma']),{'J101','J102','J103','J104'})
    def test_orientation(self):self.assertEqual([self.r['candidate']['sma'][x]['rotation_degrees'] for x in ('J101','J102','J103','J104')],[0,180,0,180])
    def test_paste_still_present(self):self.assertTrue(all(s['paste_layers_all'] for s in self.r['candidate']['sma'].values()))
    def test_not_te_approved(self):self.assertFalse(self.r['te_land_pattern_approved'])
    def test_not_native_kicad(self):self.assertEqual(self.r['native_kicad_DRC'],'NOT RUN')
    def test_fab_block(self):self.assertEqual(self.r['fabrication'],'BLOCKED')
if __name__=='__main__':unittest.main(verbosity=2)
