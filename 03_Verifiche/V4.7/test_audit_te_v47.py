#!/usr/bin/env python3
"""Static read-only V4.7 regressions; no native CAD software represented as executed."""
import importlib.util, unittest, json, tempfile, re
from pathlib import Path
MOD=Path(__file__).with_name('audit_te_sma_v47.py')
spec=importlib.util.spec_from_file_location('auditv47',MOD)
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
class CheckV47(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.r=a.audit()
    def test_01_reference_is_exact_part(self):self.assertEqual(self.r['manufacturer_drawing']['part_number'],'CONSMA002-SMD-G')
    def test_02_reference_drawing_rev(self):self.assertEqual(self.r['manufacturer_drawing']['revision'],'D')
    def test_03_reference_center(self):self.assertEqual(self.r['manufacturer_drawing']['recommended_center_diameter_mm'],2.05)
    def test_04_study_center(self):self.assertEqual(self.r['center_pad_size_mm'],[2.05,2.05])
    def test_05_licensing_no_cad_embedded(self):self.assertEqual(self.r['cad_dxf_step'],'LISTED_BY_TE_BUT_NOT_DOWNLOADED')
    def test_06_four_placements(self):self.assertEqual(len(self.r['sma_placements']),4)
    def test_07_unique_refs(self):self.assertEqual([x['ref'] for x in self.r['sma_placements']],['J101','J102','J103','J104'])
    def test_08_footprint_pad_number_two(self):self.assertEqual(self.r['gnd_pad_count_per_connector'],4)
    def test_09_vertical_dimension(self):self.assertAlmostEqual(self.r['gnd_vertical_envelope_mm'],7.76)
    def test_10_vertical_reference(self):self.assertEqual(self.r['manufacturer_drawing']['recommended_ground_vertical_envelope_mm'],7.76)
    def test_11_lateral_symmetry(self):
        b=self.r['lateral_custom_copper_x_bounds_mm'];self.assertEqual(len(b),2)
        self.assertAlmostEqual(b[0][0],-b[1][1]);self.assertAlmostEqual(b[0][1],-b[1][0])
    def test_12_full_solder_paste_declared(self):self.assertTrue(self.r['custom_gnd_pad_solder_paste_present'])
    def test_13_paste_relief_not_explicit(self):self.assertFalse(self.r['custom_gnd_pad_paste_relief_explicit'])
    def test_14_thermal_pad(self):self.assertEqual(self.r['amplifier_exposed_pad_size_mm'],[1.8,3.48])
    def test_15_thermal_paste_ratio(self):self.assertAlmostEqual(self.r['amplifier_paste_margin_ratio'],-0.1)
    def test_16_thermal_paste_nominal_fraction(self):self.assertAlmostEqual(self.r['amplifier_nominal_paste_fraction_of_copper'],0.81)
    def test_17_thermal_paste_nominal_area(self):self.assertAlmostEqual(self.r['amplifier_nominal_paste_area_mm2'],5.0738,places=4)
    def test_18_no_claim_of_manufacturing(self):self.assertFalse(self.r['fabrication_authorized'])
    def test_19_no_claim_of_native_checks(self):self.assertEqual(self.r['native_kicad_erc_drc'],'NOT_RUN')
    def test_20_no_claim_of_thermal(self):self.assertEqual(self.r['thermal_finite_element_analysis'],'NOT_RUN')
    def test_21_sha_consistent(self):self.assertEqual(self.r['study_board_sha256'],a.sha(a.BOARD))
    def test_22_schematic_sha_consistent(self):self.assertEqual(self.r['study_schematic_sha256'],a.sha(a.SCH))
    def test_23_corruption_pad_identity_detected(self):
        node=a.p.child(a.FP.read_text('utf8'),'pad')[1]
        self.assertTrue(a.is_ground_custom_pad(node))
        self.assertFalse(a.is_ground_custom_pad(node.replace('"2" smd','"3" smd')))
    def test_24_corruption_polygon_detected(self):
        node=a.p.child(a.FP.read_text('utf8'),'pad')[1]
        orig=a.custom_bounds(node)
        changed=a.custom_bounds(node.replace('(at -2.850 -3.130)','(at -2.850 -3.000)'))
        self.assertNotEqual(orig['bounds_mm'],changed['bounds_mm'])
    def test_25_no_fabrication_tags(self):self.assertIn('NOT_APPROVED',self.r['conformity'])
    def test_26_machine_report_valid_json(self):
        data=json.loads((a.DST/'AUDIT_SMA_TE_V4.7.json').read_text('utf8'))
        self.assertEqual(data['version'],'4.7')
    def test_27_no_mutation_of_board(self):
        before=a.sha(a.BOARD)
        a.audit()
        self.assertEqual(before,a.sha(a.BOARD))
    def test_28_no_mutation_of_footprint(self):
        before=a.sha(a.FP)
        a.audit()
        self.assertEqual(before,a.sha(a.FP))
if __name__=='__main__':unittest.main(verbosity=2)
