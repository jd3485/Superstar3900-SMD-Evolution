"""V7.19 fail-closed TI loop topology contract and real KiCad forensic gates."""
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.19"))
from probe_loop_endpoint_v719 import ROOT as CAD_ROOT, OUT, POWER, PLL_FILE
CONTRACT=ROOT/"01_Specifiche"/"V7.19"/"CONTRATTO_TOPOLOGIA_LOOP_PLL_TI_V7_19.json"
PLL_SRC=POWER/PLL_FILE
MATRIX=ROOT/"04_KiCad"/"Assemblaggio_RX_Power_V7.17_INTEGRATION_HOLD_NOT_FOR_FAB"/"MATRICE_INTERFACCE_PROPOSTE_V7_17_OPEN_HOLD.csv"
class LoopContractV719(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(CONTRACT.read_text())
        cls.probes=json.loads((OUT/"v719.pll_pin_forensics.json").read_text())
        cls.labels=json.loads((OUT/"v719.label_direct_native.json").read_text())
        cls.src=PLL_SRC.read_text()

    def test_01_vendor_sources_are_official_TI(self):
        self.assertEqual(self.data["evidence"]["manufacturer_datasheet"],"https://www.ti.com/lit/ds/symlink/lmx2572.pdf")
        self.assertEqual(self.data["evidence"]["manufacturer_figure"].split(" ")[1],"179")
        self.assertEqual(self.data["evidence"]["evm_fig"].split(" ")[1],"19")

    def test_02_pll_chargepump_vtune_pin_numbers(self):
        self.assertEqual(self.data["symbols"]["U1"]["pins"],{"CPout":"12","Vtune":"35"})

    def test_03_required_shunt_capacitance_value_met_on_paper_only(self):
        self.assertGreaterEqual(self.data["design_c3_nF"],self.data["minimum_shunt_capacitance_vtune_nF_TI"])
        self.assertFalse(self.data["actual_placed_c3_distance_mm_verified"])

    def test_04_12_pin_mappings_exact_3rd_order_filter(self):
        expected=self.data["expected_future_pin_nets"]
        self.assertEqual(set(expected),{"PLL_CPOUT","PLL_R2_C2","PLL_VTUNE","GND_MAIN"})
        pairs={(ref,pin):name for name,refs in expected.items() for ref,pin in refs}
        self.assertEqual(sum(map(len,expected.values())),12)
        self.assertEqual(len(pairs),12)
        self.assertEqual(pairs[("U1","12")],"PLL_CPOUT")
        self.assertEqual(pairs[("U1","35")],"PLL_VTUNE")
        self.assertEqual(pairs[("R3","1")],"PLL_CPOUT")
        self.assertEqual(pairs[("R3","2")],"PLL_VTUNE")
        self.assertEqual(pairs[("R2","2")],"PLL_R2_C2")

    def test_05_original_components_values_not_changed_by_diagnostics(self):
        for ref,v in self.data["symbols"].items():
            self.assertIn(ref,self.src)
            if "provisional_value" in v:self.assertIn('"'+v["provisional_value"]+'"',self.src)

    def test_06_critical_original_source_r2_r3_pin_geometry_preserved(self):
        self.assertIn('(symbol (lib_id "S3900E:R") (at 90 157 0)',self.src)
        self.assertIn('(symbol (lib_id "S3900E:R") (at 140 146.05 0)',self.src)
        self.assertIn('(wire (pts (xy 90 146.05) (xy 90 157))',self.src)

    def test_07_baseline_and_all_probe_clones_not_approved(self):
        self.assertTrue(self.probes["source_pll_unchanged"])
        self.assertTrue(self.probes["probes_not_approved_for_power_on_or_fab"])
        self.assertEqual(self.probes["variants"]["as_is"]["errors"],42)
        self.assertEqual(self.probes["variants"]["as_is"]["warnings"],340)

    def test_08_native_first_pin_trial_reduces_two_pin_not_connected_only(self):
        base=self.probes["variants"]["as_is"]["categories"]
        candidate=self.probes["variants"]["r2_direct_pin"]["categories"]
        self.assertEqual(base["pin_not_connected"],2)
        self.assertEqual(candidate.get("pin_not_connected",0),0)
        self.assertEqual(candidate["wire_dangling"],base["wire_dangling"])
        self.assertEqual(self.probes["variants"]["r2_direct_pin"]["errors"],40)

    def test_09_reduced_erc_does_not_imply_native_correct_filter(self):
        for name,row in self.probes["variants"].items():
            self.assertEqual(row["net_memberships_R2_R3_C1_C2_C3_U1"].get("UNUSED"),None)
            pairs=[(r,p) for net,refs in row["net_memberships_R2_R3_C1_C2_C3_U1"].items() for r,p in refs]
            self.assertNotIn(("R2","1"),pairs)
            self.assertNotIn(("R3","1"),pairs)

    def test_10_explicit_native_labels_remain_unapproved(self):
        self.assertEqual(self.labels["status"],"EPHEMERAL_PROBE_ONLY")
        self.assertFalse(self.labels["pcb_approved"])
        self.assertFalse(self.labels["tx_permitted"])
        self.assertEqual(self.labels["baseline_erc"],[42,340])

    def test_11_loop_component_values_provisional_not_vendor_signoff(self):
        self.assertFalse(self.data["vendor_approved_values"])
        self.assertFalse(self.data["actual_application_loop_bandwidth_qualified"])
        self.assertFalse(self.data["pllatinum_sim_calibration_and_phase_margin_verified"])

    def test_12_seven_sheet_interconnect_remains_open_hold(self):
        import csv
        with MATRIX.open(encoding="utf-8",newline="") as f:rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),15)
        self.assertTrue(all(x["physical_connection"]=="OPEN" and x["qualification"]=="HOLD" and x["tx_permission"]=="0" for x in rows))

    def test_13_no_v719_board_cad_fabrication(self):
        self.assertFalse(list((ROOT/"04_KiCad").glob("*V7.19*/*.kicad_pcb")))
        self.assertFalse(self.data["pcb_fabrication_permitted"])
        self.assertFalse(self.data["rf_tx_permitted"])

if __name__=="__main__":unittest.main()
