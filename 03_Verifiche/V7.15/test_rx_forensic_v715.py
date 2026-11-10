"""V7.15 safety/non-regression checks on genuine KiCad source artifacts."""
import re
import unittest
from pathlib import Path
from audit_rx_topologia_v715 import ROOT, PCB, LIB, SMA_REFS, audit, check, footprint_refs, forms, pad_signatures

K = ROOT / "04_KiCad"
OLD = K / "Modulo_RX_Test_50ohm_V7.12_SCHEMATIC_REPAIR_NOT_FOR_FAB" / "S3900E_RX_STANDALONE_V7_12_NOT_FOR_FAB.kicad_pcb"
ROOT14 = K / "Assemblaggio_RX_Power_V7.14_LIB_NOT_FOR_FAB" / "S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
MATRIX = K / "Assemblaggio_RX_Power_V7.10_NOT_FOR_FAB" / "MATRICE_INTERFACCE_DA_QUALIFICARE_V7_10.csv"

class TestV715ReadOnlyForensicAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = PCB.read_text(encoding="utf-8")
        cls.report = audit()
        cls.fp = footprint_refs(cls.s)

    def test_01_previous_copper_exact_bytes(self):
        self.assertEqual(PCB.read_bytes(), OLD.read_bytes())

    def test_02_inventory_consistency(self):
        check(self.report)
        self.assertEqual(self.report["footprints_total"], 15)

    def test_03_four_sma_present(self):
        self.assertTrue(set(SMA_REFS).issubset(self.fp))
        self.assertEqual(len([k for k in self.fp if k.startswith("J910")]), 5)

    def test_04_all_sma_local_pad_geometries_identical_to_archived_candidate(self):
        library = pad_signatures(LIB.read_text(encoding="utf-8"))
        for ref in SMA_REFS:
            with self.subTest(ref=ref):
                self.assertEqual(pad_signatures(self.fp[ref]), library)
                self.assertEqual(self.report["sma"][ref]["numbers"], ["1", "2", "2", "2", "2"])

    def test_05_sma_180_degree_parts_are_not_vendor_approved(self):
        for ref in ("J9102", "J9104"):
            with self.subTest(ref=ref):
                self.assertRegex(self.fp[ref], r'\(at 122 (?:36|65) 180\)')
        self.assertFalse(self.report["vendor_reference"]["mechanical_qualification"])
        self.assertFalse(self.report["vendor_reference"]["cad_dxf_step_imported"])

    def test_06_center_copper_diameter(self):
        self.assertTrue(all(x["center_pad_diameter_mm"] == 2.05
                            for x in self.report["sma"].values()))
        self.assertEqual(self.report["vendor_reference"]["center_pad_diameter_mm"], 2.05)

    def test_07_all_vias_still_on_gnd_rf_and_unchanged(self):
        self.assertEqual(len(forms(self.s,"via")), 70)
        self.assertEqual(self.report["via_net_ids"], [1])
        self.assertEqual(self.report["net_names"][1], "GND_RF")

    def test_08_zone_shells_present_but_no_saved_fill(self):
        self.assertEqual(len(forms(self.s,"zone")), 4)
        self.assertEqual(self.report["saved_filled_polygons"], 0)
        self.assertEqual({z["layer"] for z in self.report["zones"]},
                         {"F.Cu", "B.Cu", "In1.Cu", "In2.Cu"})

    def test_09_44_track_segments_unchanged(self):
        self.assertEqual(len(forms(self.s,"segment")), 44)

    def test_10_no_tx_fab_or_gerber_generation(self):
        self.assertFalse(any("TX_" in n for n in self.report["net_names"].values()))
        self.assertFalse(self.report["pcb_fabrication_permitted"])
        self.assertFalse(self.report["tx_permitted"])
        self.assertIn("NOT_FOR_FAB", str(PCB))
        self.assertFalse(ROOT14.read_text().count('(wire (pts'))

    def test_11_original_15_interface_contracts_still_hold(self):
        import csv
        with MATRIX.open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows),15)
        self.assertTrue(all(row["physical_connection"]=="OPEN"
                            and row["qualification"]=="HOLD" for row in rows))

    def test_12_native_drc_baseline_is_a_blocker_not_a_release(self):
        b = self.report["native_baseline_v714"]
        self.assertEqual((b["rx_drc_violations"],b["via_dangling"],b["unconnected_items"],
                          b["root_erc_errors"]), (72,70,63,43))
        self.assertEqual(b["sma_footprint_mismatch"], ["J9102","J9104"])
        self.assertTrue(self.report["read_only"])
        self.assertIn("not", b["status"].lower())

if __name__=="__main__": unittest.main()
