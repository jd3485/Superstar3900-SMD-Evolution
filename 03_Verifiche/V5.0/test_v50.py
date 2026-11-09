#!/usr/bin/env python3
"""Controlli statici V5.0 con prove di errore intenzionale; NON KiCad nativo."""
import copy, hashlib, importlib.util, json, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).parent

def load(name, filename):
    spec=importlib.util.spec_from_file_location(name,HERE/filename)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
st=load('st_v50','studio_stencil_v50.py')
gt=load('gt_v50','verifica_gate_v50.py')
kr=load('kr_v50','run_kicad_native_v50.py')

class ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'03_Verifiche/V4.9/AUDIT_VIA_STENCIL_V4.9.json').read_text())
        cls.result=st.compute(cls.data)
    def test_01_baseline_81_percent(self):self.assertEqual(self.result['option_A']['coverage_percent'],81.)
    def test_02_optionB_approx30_percent(self):self.assertAlmostEqual(self.result['option_B']['coverage_percent'],29.69,places=2)
    def test_03_no_holes_intersect_windows(self):
        for v in self.data['vias']:
            for r in st.WINDOWS:self.assertGreaterEqual(st.distance_point_rect(v['x'],v['y'],r)-v['drill']/2,0.1)
    def test_04_gap_min_0125(self):self.assertAlmostEqual(self.result['option_B']['min_drill_edge_to_aperture_mm'],0.125,places=6)
    def test_05_below_35_percent(self):self.assertLess(self.result['option_B']['coverage_percent'],35.)
    def test_06_all_windows_within_original_paste(self):
        b=self.data['U101']['paste_bbox_mm']
        for r in st.WINDOWS:self.assertTrue(b[0]<=r[0] and b[1]<=r[1] and r[2]<=b[2] and r[3]<=b[3])
    def test_07_tamper_detected(self):
        d=copy.deepcopy(self.data);d['vias'][0]['y']=33.0
        with self.assertRaisesRegex(ValueError,'troppo vicina'):st.compute(d)
    def test_08_pad_tamper_detected(self):
        d=copy.deepcopy(self.data);d['U101']['thermal_pad_bbox_mm']=[67.9,32.0,68.1,35.2]
        with self.assertRaisesRegex(ValueError,'fuori dal pad'):st.compute(d)
    def test_09_board_hash_original(self):
        p=ROOT/self.data['board_file']
        self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),self.data['board_sha256'])
    def test_10_via_six_gnd(self):self.assertTrue(self.data['all_six_gnd'] and self.data['via_count']==6)
    def test_11_gate_fail_closed(self):
        r=gt.gate(ROOT);self.assertFalse(r['fabrication_allowed']);self.assertEqual(r['release_status'],'BLOCKED_NOT_FOR_FAB')
    def test_12_nine_requirements_open(self):
        r=gt.gate(ROOT);self.assertEqual(len(r['gate_items']),9);self.assertTrue(all(q['status']=='OPEN' for q in r['gate_items']))
    def test_13_supervisor_manual_preserved(self):
        self.assertTrue((ROOT/'06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf').stat().st_size>1000)
    def test_14_native_runner_does_not_fake_checks(self):
        with tempfile.TemporaryDirectory() as td:
            r=kr.run(ROOT,Path(td),executable='/this/does/not/exist/kicad-cli')
            self.assertEqual(r['native_erc'],'NOT_RUN');self.assertEqual(r['native_drc'],'NOT_RUN')
            self.assertFalse(r['fabrication_authorized'])
    def test_15_study_no_fabrication(self):self.assertFalse(self.result['fabrication_approved'])
    def test_16_svg_exists(self):self.assertTrue((HERE/'CONFRONTO_STENCIL_U101_V5.0.svg').read_text().startswith('<svg'))
    def test_17_no_output_cam_in_v50(self):
        self.assertFalse(any(f.suffix.lower() in {'.gbr','.drl','.pos','.ger','.gko'} for f in HERE.rglob('*') if f.is_file()))
    def test_18_schematic_source(self):
        src=ROOT/kr.REL/(kr.STEM+'.kicad_sch');self.assertTrue(src.is_file())
    def test_19_release_not_production(self):self.assertFalse(json.loads((HERE/'GATE_RELEASE_V5.0.json').read_text())['fabrication_allowed'])
    def test_20_options_distinct(self):self.assertGreater(self.result['option_A']['coverage_percent'],self.result['option_B']['coverage_percent'])

if __name__=='__main__':unittest.main(verbosity=2)
