#!/usr/bin/env python3
"""Pure-Python static regression tests - NOT hardware testing nor DRC."""
import importlib.util
import math
import unittest
from pathlib import Path
S=Path(__file__).with_name('audit_rf_v41.py')
spec=importlib.util.spec_from_file_location('aud',S)
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)

class AuditV41Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.r=a.generate()
    def test_board_outline(self): self.assertEqual(self.r['pcb_outline_mm'],[110.,62.])
    def test_legacy_board_hash(self):
        self.assertEqual(self.r['pcb_sha256'],'57dd24b13edb5dc987e3ad8cdae0d2d8cc7a1fa3aefb455a63ebc86559eec489')
    def test_connector_count(self): self.assertEqual(len(self.r['sma']),4)
    def test_custom_land_geometry(self):
        for val in self.r['sma'].values():
            self.assertEqual(val['rf_pad_diameter_mm'],2.05)
            self.assertEqual(val['ground_custom_pad_count'],4)
            self.assertAlmostEqual(val['ground_y_span_mm'],7.40)
            self.assertAlmostEqual(val['vertical_difference_mm'],-0.36)
    def test_kicad_no_fab(self):
        self.assertFalse(self.r['native_erc_drc_performed'])
        self.assertIn('BLOCKED',self.r['manufacturing_release'])
    def test_unfilled_zones(self):
        self.assertEqual(self.r['ground_zones'],{'declared':4,'refilled':0})
    def test_paddle(self):
        x=self.r['adl5535']
        self.assertEqual(x['paddle_size_mm'],[1.8,3.48])
        self.assertAlmostEqual(x['quiescent_input_power_w_typical'],0.485)
        self.assertEqual(x['via_centers_within_paddle_count'],0)
        self.assertAlmostEqual(x['closest_ground_via']['copper_edge_distance_to_paddle_mm'],0.5,places=3)
        self.assertTrue(x['explicit_track_paddle_to_nearest_via'])
    def test_pi_nominal(self):
        n=self.r['attenuator']['ideal_dc_nominal'];self.assertAlmostEqual(n['insertion_loss_db'],6.012876,places=5)
        self.assertAlmostEqual(n['input_return_loss_db'],67.035927,places=5)
    def test_value_perturbation(self):
        good=a.pi_attenuator(150,37.4,150)
        changed=a.pi_attenuator(150,50,150)
        self.assertGreater(changed['insertion_loss_db'],good['insertion_loss_db'])
    def test_1percent_corner_count(self):
        t=self.r['attenuator']['hypothetical_1percent_corner_analysis']
        self.assertEqual(t['corner_count'],8)
        self.assertLess(t['loss_db_min'],6.02)
        self.assertGreater(t['loss_db_max'],6.0)
    def test_special_circles_vs_boxes(self):
        rect=(1,1,3,3)
        self.assertEqual(a.circle_to_box_distance(2,2,.3,rect),0)
        self.assertAlmostEqual(a.circle_to_box_distance(0,2,.3,rect),.7)
    def test_rotate_180(self):
        t=a.parse_board();fp=a.footprint_map(t)['J102']
        self.assertEqual(tuple(round(x,3) for x in a.local_to_board(fp,1,2)),(121.,34.))

if __name__=='__main__':unittest.main(verbosity=2)
