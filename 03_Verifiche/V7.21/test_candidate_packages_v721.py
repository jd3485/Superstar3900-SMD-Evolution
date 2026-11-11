"""V7.21 manufacturer package candidate list: numbers-only mechanical gate, NO FAB."""
import csv,json,unittest
from audit_board_foundations_v721 import OUT,MCU,NET,native_components,schematic_values
from audit_candidate_packages_v721 import CANDIDATES
class CandidatePackagesV721(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=json.loads((OUT/"v721.candidate_IC_packages_native.json").read_text())

    def test_01_candidates_are_six_and_unique(self):
        self.assertEqual(self.report["candidate_IC_footprint_count"],6)
        self.assertEqual(len({x["ref"] for x in self.report["records"]}),6)
        self.assertEqual(len(CANDIDATES),6)

    def test_02_mcu_st_64_pin_mechanical_candidates(self):
        row=next(x for x in self.report["records"] if x["ref"]=="U6201")
        self.assertEqual(row["pad_count"],64)
        self.assertEqual(row["actual_installed_pad_numbers"],list(range(1,65)))
        self.assertTrue(row["candidate_kicad_footprint"].endswith("_P0.5mm"))

    def test_03_ti_codec_has_32_peripheral_and_one_thermal_pad(self):
        row=next(x for x in self.report["records"] if x["ref"]=="U6202")
        self.assertEqual(row["pad_count"],33)
        self.assertIn(33,row["actual_installed_pad_numbers"])
        self.assertTrue(self.report["codec_RHB_pad33_exposed_pad_requires_GND_and_stencil_review"])

    def test_04_six_pads_not_false_qualification(self):
        self.assertTrue(all(not x["symbol_pin_to_pad_mapping_vendor_verified"] for x in self.report["records"]))
        self.assertTrue(all(not x["cad_schematic_footprint_assigned"] for x in self.report["records"]))

    def test_05_four_ldos_draft_have_five_pads_each(self):
        rows=[x for x in self.report["records"] if x["ref"].startswith("U620")
              and x["ref"] in ("U6203","U6204","U6205","U6206")]
        self.assertEqual(len(rows),4)
        self.assertTrue(all(x["actual_installed_pad_numbers"]==list(range(1,6)) for x in rows))

    def test_06_same_46_blank_fps_after_candidate_study(self):
        src=schematic_values(MCU)
        self.assertEqual(src["U6201"]["footprint"],"")
        self.assertEqual(src["U6202"]["footprint"],"")
        self.assertTrue(all(src["U620"+str(i)]["footprint"]=="" for i in range(3,7)))
        self.assertEqual(sum(x["footprint"] is None for x in native_components(NET)),48)

    def test_07_other_42_missing_still_hold(self):
        self.assertTrue(self.report["other_42_missing_footprints_still_HOLD"])
        self.assertFalse(self.report["any_cad_change"])
        self.assertFalse(self.report["fabrication_release"])

    def test_08_six_csv_records_exact_and_status_hold(self):
        with (OUT/"v721.candidate_IC_packages.csv").open(newline="",encoding="utf-8") as f: rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),6)
        self.assertTrue(all(x["verification"]=="KICAD9_STANDARD_LIBRARY_PAD_NUMBERS_ONLY" for x in rows))
if __name__=="__main__":unittest.main()
