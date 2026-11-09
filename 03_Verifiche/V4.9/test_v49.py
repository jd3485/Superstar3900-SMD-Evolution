#!/usr/bin/env python3
"""Regressioni indipendenti del rischio via-in-pad + stencil V4.9 (NON DRC)."""
import hashlib
import json
import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from audit_via_stencil_v49 import ROOT, BOARD, AUDIT48, analyse

class ManufacturabilityPreflight(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v = analyse(ROOT)

    def test_01_reference_board_unchanged(self):
        self.assertTrue(self.v['previous_v48_candidate_sha256_match'])

    def test_02_four_layer_and_thickness(self):
        self.assertEqual(self.v['copper_layer_count'],4)
        self.assertEqual(self.v['board_thickness_mm'],1.6)

    def test_03_pad_and_paste_dimensions(self):
        self.assertEqual(self.v['U101']['thermal_pad_size_mm'],[1.8,3.48])
        self.assertEqual(self.v['U101']['paste_size_mm'],[1.62,3.132])

    def test_04_paste_ratio(self):
        self.assertEqual(self.v['U101']['paste_margin_ratio'],-0.1)
        self.assertEqual(self.v['U101']['paste_coverage_ratio_vs_pad'],0.81)

    def test_05_six_vias_under_paste(self):
        self.assertEqual(self.v['via_count'],6)
        self.assertTrue(self.v['six_via_centers_under_paste'])
        self.assertTrue(self.v['all_six_holes_fully_under_paste'])

    def test_06_copper_vias_inside_pad(self):
        self.assertTrue(self.v['all_six_via_copper_inside_pad'])
        self.assertTrue(self.v['all_six_gnd'])

    def test_07_drill_and_ring(self):
        self.assertTrue(all(v['drill']==0.25 and v['copper_diameter']==0.55 for v in self.v['vias']))
        self.assertAlmostEqual(self.v['nominal_annular_ring_mm'],0.15)
        self.assertAlmostEqual(self.v['nominal_aspect_ratio'],6.4)

    def test_08_min_edge_stays_within_opening(self):
        self.assertGreater(min(v['min_hole_edge_to_paste_edge_mm'] for v in self.v['vias']),0.27)

    def test_09_safety_gates_not_approved(self):
        self.assertFalse(self.v['authorized_for_fabrication'])
        self.assertEqual(self.v['pcbway_process_approval'],'NOT_RECEIVED')
        self.assertEqual(self.v['native_kicad_drc'],'NOT_RUN')
        self.assertEqual(self.v['native_kicad_erc'],'NOT_RUN')

    def test_10_stencil_change_detected(self):
        # Cambiare molto l'apertura deve essere rilevato: no fiducia cieca nel JSON V4.8.
        with tempfile.TemporaryDirectory() as tmp:
            r=Path(tmp)
            b=r/BOARD; b.parent.mkdir(parents=True)
            s=(ROOT/BOARD).read_text()
            self.assertIn('(solder_paste_margin_ratio -0.100)',s)
            b.write_text(s.replace('(solder_paste_margin_ratio -0.100)', '(solder_paste_margin_ratio -0.900)',1))
            a=r/AUDIT48; a.parent.mkdir(parents=True); shutil.copyfile(ROOT/AUDIT48,a)
            bad=analyse(r)
            self.assertFalse(bad['six_via_centers_under_paste'])
            self.assertFalse(bad['previous_v48_candidate_sha256_match'])

    def test_11_missing_thermal_via_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=Path(tmp)
            b=r/BOARD; b.parent.mkdir(parents=True)
            s=(ROOT/BOARD).read_text()
            self.assertIn('(via (at 67.640 32.500)',s)
            b.write_text(s.replace('(via (at 67.640 32.500)','(via (at 66.640 32.500)',1))
            a=r/AUDIT48; a.parent.mkdir(parents=True); shutil.copyfile(ROOT/AUDIT48,a)
            with self.assertRaises(ValueError): analyse(r)

    def test_12_wrong_pad_net_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=Path(tmp)
            b=r/BOARD; b.parent.mkdir(parents=True)
            s=(ROOT/BOARD).read_text()
            needle='(solder_paste_margin_ratio -0.100) (zone_connect 2) (net 1 "GND_RF")'
            self.assertIn(needle,s)
            b.write_text(s.replace(needle,needle.replace('GND_RF','WRONG_NET'),1))
            a=r/AUDIT48; a.parent.mkdir(parents=True); shutil.copyfile(ROOT/AUDIT48,a)
            with self.assertRaises(ValueError): analyse(r)

    def test_13_required_project_documents(self):
        self.assertTrue((ROOT/'06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf').exists())
        self.assertTrue((ROOT/'RIPRENDI_IN_UNA_NUOVA_CHAT.md').exists())

    def test_14_copper_original_v38_kept(self):
        self.assertTrue((ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V4.5_LIBS_PORTABILI_NOT_FOR_FAB').is_dir())
        self.assertTrue((ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V4.8_TERMICA_6VIE_STUDIO_NON_FAB').is_dir())

if __name__ == '__main__':
    unittest.main(verbosity=2)
