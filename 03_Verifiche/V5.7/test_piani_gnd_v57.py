#!/usr/bin/env python3
"""Regression and adversarial checks for analytical upper-bound zone study, NOT DRC."""
from __future__ import annotations
import json,sys,unittest
from pathlib import Path
from shapely.geometry import box
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'03_Verifiche/V5.7'))
from audit_piani_gnd_v57 import audit,approximate_pour
sys.path.insert(0,str(ROOT/'03_Verifiche/V5.5'))
from audit_rame_v55 import PCB
TEXT=PCB.read_text(encoding='utf-8')

class TestZoneEnvelope(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=audit(TEXT)
    def assert_bad(self,src,code):
        self.assertNotEqual(src,TEXT,'mutation failed to modify original')
        out=audit(src)
        self.assertEqual('STATIC_ENVELOPE_FAIL',out['status'])
        self.assertTrue(any(code in e for e in out['errors']),out['errors'])
        self.assertFalse(out['fabrication_allowed'])
    def test_01_baseline(self):self.assertEqual(self.r['status'],'STATIC_ENVELOPE_PASS_NATIVE_PENDING')
    def test_02_fcu_24pads(self):self.assertEqual(self.r['ground_pads_fcu'],24)
    def test_03_70_vias(self):self.assertEqual(self.r['ground_vias_fcu'],70)
    def test_04_four_unfilled(self):self.assertEqual(self.r['ground_zones_unfilled'],4)
    def test_05_vias_each_zone(self):
        for v in self.r['layers'].values():self.assertEqual(v['gnd_vias_geom_in_zone'],70)
    def test_06_vias_largest_region(self):
        for v in self.r['layers'].values():self.assertEqual(v['gnd_vias_geom_touch_largest_hypothetical_region'],70)
    def test_07_one_geom_region_each(self):
        for v in self.r['layers'].values():self.assertEqual(v['hypothetical_region_count'],1)
    def test_08_fcu_area_regression(self):
        self.assertAlmostEqual(self.r['layers']['F.Cu']['largest_hypothetical_area_mm2'],6323.1042,places=3)
    def test_09_fcu_fraction(self):self.assertAlmostEqual(self.r['layers']['F.Cu']['largest_region_fraction_of_outline'],.960789,places=5)
    def test_10_internal_ideal_area(self):
        for layer in ('In1.Cu','In2.Cu','B.Cu'):
            self.assertEqual(self.r['layers'][layer]['zone_area_mm2'],6581.16)
            self.assertEqual(self.r['layers'][layer]['largest_hypothetical_area_mm2'],6581.16)
    def test_11_ground_pads_fcu(self):self.assertEqual(self.r['layers']['F.Cu']['fcu_gnd_pads_geom_touch_largest_hypothetical_region'],24)
    def test_12_via_edge_annulus_margin(self):
        self.assertAlmostEqual(self.r['layers']['F.Cu']['min_via_annulus_to_zone_outline_mm'],2.05)
    def test_13_never_native(self):
        self.assertEqual(self.r['native_drc'],'NOT_RUN');self.assertEqual(self.r['native_zone_refill'],'NOT_RUN')
        self.assertFalse(self.r['fabrication_allowed']);self.assertFalse(self.r['tx_allowed'])
    def test_14_thermal_not_modeled(self):
        self.assertEqual(self.r['layers']['F.Cu']['pad_thermal_spokes'],'NOT_MODELED')
    def test_15_clearance_sensitivity(self):
        higher=audit(TEXT,0.50)
        self.assertLess(higher['layers']['F.Cu']['largest_hypothetical_area_mm2'],self.r['layers']['F.Cu']['largest_hypothetical_area_mm2'])
    def test_16_reject_clearance_extreme(self):
        with self.assertRaises(ValueError):audit(TEXT,1.1)
    def test_17_test_barrier_split(self):
        z=box(20.7,20.7,129.3,81.3)
        f=approximate_pour(z,[box(74,20,75,82)],.30)
        self.assertEqual(f.geom_type,'MultiPolygon')
        self.assertEqual(len(f.geoms),2)
    def test_18_wrong_zone_layer(self):
        self.assert_bad(TEXT.replace('(zone (net 1) (net_name "GND_RF") (layer "In2.Cu")',
                 '(zone (net 1) (net_name "GND_RF") (layer "F.Cu")',1),'DUPLICATE_ZONE_LAYER')
    def test_19_wrong_zone_net(self):
        self.assert_bad(TEXT.replace('(zone (net 1) (net_name "GND_RF") (layer "In1.Cu")',
                   '(zone (net 6) (net_name "GND_RF") (layer "In1.Cu")',1),'ZONE_NET_NOT_GND')
    def test_20_changed_zone_clearance(self):
        self.assert_bad(TEXT.replace('(connect_pads (clearance 0.3))','(connect_pads (clearance 0.1))',1),'ZONE_CLEARANCE_CHANGED')
    def test_21_changed_spoke(self):
        self.assert_bad(TEXT.replace('(thermal_bridge_width 0.5)','(thermal_bridge_width 0.1)',1),'ZONE_THERMAL_PARAMETERS_CHANGED')
    def test_22_filled_zone_unverified(self):
        self.assert_bad(TEXT.replace('(hatch edge 0.5)','(filled_polygon (layer "F.Cu")) (hatch edge 0.5)',1),
                         'ZONE_ALREADY_FILLED_NATIVE_REAUDIT_REQUIRED')
    def test_23_via_outside(self):
        self.assert_bad(TEXT.replace('(via (at 67.640 32.500)','(via (at 19.000 32.500)',1),'VIA_ANNULUS_OUTSIDE_ZONE')
    def test_24_via_wrong_net(self):
        self.assert_bad(TEXT.replace('(via (at 67.640 32.500) (size 0.55) (drill 0.25) (layers "F.Cu" "B.Cu") (net 1)',
                               '(via (at 67.640 32.500) (size 0.55) (drill 0.25) (layers "F.Cu" "B.Cu") (net 2)',1),'VIA_NET_NOT_GND')
    def test_25_via_unexpected_layers(self):
        self.assert_bad(TEXT.replace('(via (at 67.640 32.500) (size 0.55) (drill 0.25) (layers "F.Cu" "B.Cu")',
                         '(via (at 67.640 32.500) (size 0.55) (drill 0.25) (layers "F.Cu" "In1.Cu")',1),'VIA_NOT_STANDARD_F_TO_B')
    def test_26_unsupported_inner_track(self):
        self.assert_bad(TEXT.replace('(segment (start 28.000 36.000) (end 51.450 36.000) (width 0.280) (layer "F.Cu") (net 2)',
                         '(segment (start 28.000 36.000) (end 51.450 36.000) (width 0.280) (layer "In1.Cu") (net 2)',1),'NON_GND_TRACK_ON_INNER_OR_BACK_LAYER')
    def test_27_reduced_outline_margin(self):
        self.assert_bad(TEXT.replace('(polygon (pts (xy 20.7 20.7) (xy 129.3 20.7) (xy 129.3 81.3) (xy 20.7 81.3)))',
                         '(polygon (pts (xy 20.1 20.7) (xy 129.3 20.7) (xy 129.3 81.3) (xy 20.1 81.3)))',1),'ZONE_EDGE_MARGIN_TOO_SMALL')
    def test_28_via_reach_regression(self):
        self.assertEqual(sum(v['gnd_vias_geom_touch_largest_hypothetical_region'] for v in self.r['layers'].values()),280)
    def test_29_no_approved_pass_claim(self):
        self.assertIn('UPPER_BOUND',self.r['study_type'])
        self.assertTrue(any('does NOT compute KiCad' in s for s in self.r['limitations']))
    def test_30_board_sha(self):self.assertEqual(len(self.r['board_sha256']),64)

if __name__=='__main__':unittest.main(verbosity=2)
