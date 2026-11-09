#!/usr/bin/env python3
"""Regression and deliberately mutated PCB source tests for V5.8 RF via-distance audit."""
from pathlib import Path
import importlib.util,unittest
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('rf58',HERE/'audit_ritorno_rf_v58.py')
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
BASE=m.PCB.read_text(encoding='utf-8')
REF=(m.ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V4.8_TERMICA_6VIE_STUDIO_NON_FAB/S3900E_RX_TEST_50R_V4_8_6VIE_STUDIO_NOT_FOR_FAB.kicad_pcb').read_text(encoding='utf-8')
RESULT=m.audit(BASE,reference_text=REF)
def replace_once(a,b):
    assert a in BASE, a
    return BASE.replace(a,b,1)
class Tests(unittest.TestCase):
    def assert_fails_with(self,txt,expected):
        r=m.audit(txt,reference_text=REF)
        self.assertEqual(r['status'],'STATIC_RF_AUDIT_FAIL')
        self.assertIn(expected,r['errors'])
        self.assertFalse(r['fabrication_allowed'])
    def test_01_baseline(self):self.assertEqual(RESULT['status'],'STATIC_RF_VIA_PROXIMITY_AUDITED_NATIVE_PENDING')
    def test_02_no_errors(self):self.assertFalse(RESULT['errors'])
    def test_03_reference_identity(self):self.assertTrue(RESULT['reference_copper_identity_v48'])
    def test_04_six_nets(self):self.assertEqual(RESULT['rf_nets'],6)
    def test_05_thirteen_tracks(self):self.assertEqual(RESULT['rf_tracks'],13)
    def test_06_ground_vias(self):self.assertEqual(RESULT['ground_via_centers'],70)
    def test_07_max_rf_atten_in(self):self.assertEqual(RESULT['by_net'][0]['net'],'RF_ATTEN_IN')
    def test_08_max_range(self):self.assertTrue(9.5<RESULT['by_net'][0]['max_nearest_gnd_via_centre_mm']<9.7)
    def test_09_segment_length(self):self.assertAlmostEqual(next(x['rf_trace_total_length_mm'] for x in RESULT['by_net'] if x['net']=='RF_ATTEN_OUT'),49.2)
    def test_10_all_flagged_as_review(self):self.assertTrue(all(x['screening_flag']=='REVIEW_RETURN_PROXIMITY' for x in RESULT['by_net']))
    def test_11_no_native(self):self.assertEqual(RESULT['native_drc'],'NOT_RUN')
    def test_12_no_fab_or_tx(self):self.assertFalse(RESULT['fabrication_allowed'] or RESULT['tx_allowed'])
    def test_13_bound(self):self.assertTrue(all(x['conservative_upper_bound_at_sample_step_mm']>=x['max_nearest_gnd_via_centre_mm'] for x in RESULT['by_net']))
    def test_14_more_fine_sampling(self):
        finer=m.audit(BASE,step_mm=0.05,reference_text=REF)
        self.assertFalse(finer['errors'])
        self.assertLess(abs(finer['by_net'][0]['max_nearest_gnd_via_centre_mm']-RESULT['by_net'][0]['max_nearest_gnd_via_centre_mm']),0.11)
    def test_15_zero_step_refused(self):
        with self.assertRaises(ValueError):m.audit(BASE,0.)
    def test_16_large_step_refused(self):
        with self.assertRaises(ValueError):m.audit(BASE,0.5)
    def test_17_removed_route(self):
        self.assert_fails_with(replace_once('(segment (start 28.000 65.000) (end 73.450 65.000)', '(segment (start 28.000 65.000) (end 73.440 65.000)'), 'COPPER_NOT_IDENTICAL_TO_V48_REFERENCE')
    def test_18_changed_trace_width(self):
        self.assert_fails_with(replace_once('(end 73.450 65.000) (width 0.280)','(end 73.450 65.000) (width 0.290)'), 'COPPER_NOT_IDENTICAL_TO_V48_REFERENCE')
    def test_19_changed_signal_net(self):
        self.assert_fails_with(replace_once('(end 73.450 65.000) (width 0.280) (layer "F.Cu") (net 7)', '(end 73.450 65.000) (width 0.280) (layer "F.Cu") (net 8)'), 'COPPER_NOT_IDENTICAL_TO_V48_REFERENCE')
    def test_20_changed_via_coordinates(self):
        self.assert_fails_with(replace_once('(via (at 54 69.45)','(via (at 54 68.45)'), 'COPPER_NOT_IDENTICAL_TO_V48_REFERENCE')
    def test_21_changed_via_net(self):
        self.assert_fails_with(replace_once('(layers "F.Cu" "B.Cu") (net 1) (tstamp "a05e5320','(layers "F.Cu" "B.Cu") (net 2) (tstamp "a05e5320'), 'GND_VIA_COUNT_OR_ASSIGNMENT_CHANGED')
    def test_22_changed_zone_layer(self):
        self.assert_fails_with(replace_once('(layer "In2.Cu") (tstamp "47f80eec','(layer "B.Cu") (tstamp "47f80eec'),'ZONE_CONFIG_CHANGED')
    def test_23_deleted_ground_zone(self):
        self.assert_fails_with(replace_once('(zone (net 1) (net_name "GND_RF") (layer "In2.Cu")','(zone (net 2) (net_name "GND_RF") (layer "In2.Cu")'),'ZONE_CONFIG_CHANGED')
    def test_24_pad_copper_changed(self):
        self.assert_fails_with(replace_once('(size 2.050 2.050)','(size 2.060 2.050)'),'COPPER_NOT_IDENTICAL_TO_V48_REFERENCE')
    def test_25_no_reference_still_not_release(self):
        r=m.audit(BASE)
        self.assertIsNone(r['reference_copper_identity_v48']);self.assertFalse(r['fabrication_allowed'])
    def test_26_net_label_changed(self):
        self.assert_fails_with(replace_once('(net 7 "RF_ATTEN_IN")','(net 7 "RF_ATTEN_RENAMED")'),'NET_SET_CHANGED')
    def test_27_sample_count_monotonic(self):
        r=m.audit(BASE,step_mm=0.1,reference_text=REF)
        self.assertGreater(sum(t['sample_count'] for t in r['by_segment']),sum(t['sample_count'] for t in RESULT['by_segment']))
    def test_28_lengths_positive(self):self.assertTrue(all(x['length_mm']>0 for x in RESULT['by_segment']))
    def test_29_all_rf_widths(self):self.assertTrue(all(x['trace_width_mm']==0.28 for x in RESULT['by_segment']))
    def test_30_all_source_positions_millimetric(self):self.assertTrue(all(len(x['worst_point_mm'])==2 for x in RESULT['by_net']))
if __name__=='__main__':unittest.main(verbosity=2)
