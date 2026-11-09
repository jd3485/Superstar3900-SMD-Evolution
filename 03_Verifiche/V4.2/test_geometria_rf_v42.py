#!/usr/bin/env python3
"""Reproducible geometry regression, NOT KiCad native DRC."""
import importlib.util, hashlib, unittest
from pathlib import Path
P=Path(__file__).with_name('audit_geometria_rf_v42.py')
s=importlib.util.spec_from_file_location('aud42',P)
a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
class TestGeometryV42(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=a.analyze()
    def test_sha_immutable(self):self.assertEqual(self.r['pcb_sha256'],a.EXPECTED_SHA)
    def test_sma_count(self):self.assertEqual(len(self.r['sma']),4)
    def test_sma_custom_geometries(self):
        for item in self.r['sma'].values():self.assertEqual(item['ground_custom_polygon_count'],4)
    def test_sma_ground_span(self):
        for item in self.r['sma'].values():self.assertAlmostEqual(item['ground_span_mm'],7.4)
    def test_open_te_status(self):
        for item in self.r['sma'].values():self.assertIn('OPEN',item['footprint_status'])
    def test_0_36_mismatch(self):
        for item in self.r['sma'].values():self.assertAlmostEqual(item['difference_from_recommended_span_mm'],-.36)
    def test_no_2d_copper_short(self):self.assertEqual(self.r['top_copper_inter_net_clearance']['clearance_below_review_threshold_count'],0)
    def test_min_clearance(self):self.assertAlmostEqual(self.r['top_copper_inter_net_clearance']['closest_distance_mm'],.45,places=3)
    def test_seven_signal_nets(self):self.assertEqual(len(self.r['signal_net_copper_components']),7)
    def test_signal_copper_islands(self):
        for item in self.r['signal_net_copper_components']:self.assertEqual(item['copper_islands_without_zone_fill'],1)
    def test_ground_reaches_local_via(self):self.assertEqual(self.r['ground_top_copper']['ground_pads_not_reaching_a_local_via_over_explicit_F_Cu'],[])
    def test_ground_pads_count(self):self.assertEqual(self.r['ground_top_copper']['ground_pad_count'],24)
    def test_four_zones_unfilled(self):self.assertEqual(self.r['zone_status'],{'declared':4,'filled':0})
    def test_ideal_microstrip_sensitivity(self):
        z=self.r['microstrip_sensitivity_STUDY_ONLY']['dielectric_height_mm_to_Z0_ohm']
        self.assertAlmostEqual(z['0.14'],49.93,places=1)
        self.assertGreater(z['0.20'],60)
        self.assertLess(z['0.08'],36)
    def test_edge_courtyard_overhang(self):
        boxes=self.r['sma_courtyard_envelopes']
        self.assertEqual(self.r['board_outline_bounds_mm'],[20.,20.,130.,82.])
        for ref in ('J101','J103'):
            self.assertAlmostEqual(boxes[ref]['beyond_left_edge_mm'],7.2)
            self.assertAlmostEqual(boxes[ref]['beyond_right_edge_mm'],0)
        for ref in ('J102','J104'):
            self.assertAlmostEqual(boxes[ref]['beyond_right_edge_mm'],7.2)
            self.assertAlmostEqual(boxes[ref]['beyond_left_edge_mm'],0)
    def test_no_release(self):self.assertEqual(self.r['approval']['fabrication'],'BLOCKED')
    def test_via_local_path_covers_sma(self):
        self.assertEqual(self.r['ground_top_copper']['ground_via_count'],64)
    def test_custom_pad_no_primitives_rejected(self):
        fp=a.v41.footprint_map(a.v41.parse_board())['J101']
        pad=next(p for p in a.v41.subs(fp,'pad') if p[1]=='2')
        corrupted=[x for x in pad if not (isinstance(x,list) and x and x[0]=='primitives')]
        with self.assertRaises(ValueError):a.pad_top_geom(fp,corrupted)
    def test_reflection_of_rotated_sma(self):
        a101=self.r['sma']['J101']['ground_bounds_board_coords_mm']
        a102=self.r['sma']['J102']['ground_bounds_board_coords_mm']
        self.assertAlmostEqual(a101[2]-a101[0],a102[2]-a102[0])
        self.assertAlmostEqual(a101[3]-a101[1],a102[3]-a102[1])
if __name__=='__main__':unittest.main(verbosity=2)
