"""V7.20 tests: real external ngspice AC, 270-channel hypothetical PLL model, ERC power HOLD."""
import json
import math
import unittest
from pathlib import Path
from verify_pll_spice_270_v720 import (ROOT,OUT,PLAN,HIST,CIR,fixture,crossover,band_sweep,z_vtune)
from audit_native_power_v720 import (EXPECTED,NET,ERC,SOURCE_MASTER,export_net_nodes)
class V720PLLAndPower(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pll=json.loads((OUT/"v720.linear_pll_spice_270_channels.json").read_text())
        cls.power=json.loads((OUT/"v720.native_undriven_power_ledger.json").read_text())
        cls.v=fixture()

    def test_01_passive_filter_spice_elements_exact(self):
        self.assertEqual(set(self.v),{"C1","C2","C3","R2","R3"})
        self.assertEqual(self.v["R2"],620)
        self.assertEqual(self.v["R3"],22)

    def test_02_independent_nominal_crossover_consistent_historical(self):
        a,b=crossover(self.v,55e6,3750,2.5e-3)
        historical=json.loads(HIST.read_text())["nominal"]
        self.assertAlmostEqual(a,historical["crossover_Hz"],delta=3)
        self.assertAlmostEqual(b,historical["phase_margin_deg"],delta=.1)

    def test_03_spice_independent_ac_current_to_vtune_match(self):
        sp=self.pll["ngspice_passive_analytical_crosscheck"]
        self.assertGreater(sp["ngspice_ac_points"],90)
        self.assertLess(sp["max_relative_magnitude_error"],1e-3)
        for point in sp["examples"]:
            self.assertAlmostEqual(point["ngspice_zmag_ohm"],
                                   point["independent_nodal_zmag_ohm"],
                                   delta=point["independent_nodal_zmag_ohm"]*1e-3)

    def test_04_original_source_circuit_is_real_repo_fixture(self):
        self.assertIn("I_TEST 0 cp AC 1",CIR.read_text())
        self.assertIn("R3 cp vt 22",CIR.read_text())
        self.assertIn("C3 vt 0 2.2n",CIR.read_text())

    def test_05_270_integer_n_exact_no_register_claim(self):
        vals=self.pll["sweep_exact_270_channel_project_plan"]
        self.assertEqual(vals["channels"],270)
        self.assertEqual(vals["cases"],2430)
        self.assertTrue(vals["all_cases_are_hypothetical"])

    def test_06_model_all_cases_crossing_and_margin_are_finite(self):
        v=self.pll["sweep_exact_270_channel_project_plan"]
        for field in ("min_crossover_case","max_crossover_case","min_margin_case","max_margin_case"):
            self.assertTrue(math.isfinite(v[field]["crossover_hz"]))
            self.assertTrue(math.isfinite(v[field]["phase_margin_deg"]))
            self.assertGreater(v[field]["crossover_hz"],0)

    def test_07_vendor_model_NOT_executed(self):
        self.assertFalse(self.pll["pllatinum_sim_executed"])
        self.assertFalse(self.pll["actual_vco_gain_characterized"])
        self.assertFalse(self.pll["assumed_icp_registers_programmed"])
        self.assertFalse(self.pll["validated_phase_noise_or_spurs"])
        self.assertEqual(self.pll["acceptance"],"MODEL_COHERENCE_ONLY_NOT_RF_APPROVAL")

    def test_08_legacy_4000_MC_NOT_vendor_PVT(self):
        historical=json.loads(HIST.read_text())
        self.assertEqual(historical["montecarlo"]["samples"],4000)
        self.assertEqual(historical["montecarlo"]["pm_below_45_count"],2)
        self.assertIn("No TI PLLatinum Sim run",historical["limitations"])

    def test_09_six_power_pin_errors_all_represented(self):
        self.assertEqual(self.power["count"],6)
        expected={ref+":"+pin for ref,pin in EXPECTED}
        actual={x["reference"]+":"+x["pin"] for x in self.power["undriven_power_pins"]}
        self.assertEqual(actual,expected)

    def test_10_six_inputs_no_power_output_on_same_kicad_net(self):
        self.assertEqual(len(export_net_nodes(NET)),100)
        self.assertTrue(all(x["same_net_power_out_count"]==0 for x in self.power["undriven_power_pins"]))

    def test_11_power_domains_remain_independent(self):
        bykey={(x["reference"],x["pin"]):x for x in self.power["undriven_power_pins"]}
        self.assertTrue(bykey["U200","8"]["exact_kicad_native_net"].endswith("/EFUSE_RTN"))
        self.assertTrue(bykey["U2","2"]["exact_kicad_native_net"].endswith("/GND_MAIN"))
        self.assertNotEqual(bykey["U6203","2"]["exact_kicad_native_net"],
                            bykey["U2","2"]["exact_kicad_native_net"])
        self.assertEqual(self.power["voltage_domains_joined_without_qualification"],0)

    def test_12_13v8_input_not_cloaked_by_power_flag(self):
        self.assertEqual(self.power["artificial_pwr_flags_added"],0)
        self.assertEqual(self.power["power_source_waivers_added"],0)
        self.assertFalse(self.power["gnd_main_to_efuse_rtn_short_added"])

    def test_13_original_kicad_circuit_remains_7_sheet_HOLD(self):
        src=SOURCE_MASTER.read_text()
        self.assertIn("NO FAB / NO TX",src)
        self.assertNotIn("(wire (pts",src)
        self.assertIn("Gerarchico_Alimentazioni_V7.19",src)

    def test_14_no_spice_study_licenses_fab_or_tx(self):
        self.assertTrue(self.pll["not_for_fabrication"])
        self.assertTrue(self.pll["no_tx"])
        self.assertTrue(self.power["no_fab"])
        self.assertTrue(self.power["no_tx"])

    def test_15_analog_linear_study_does_not_close_root_erc(self):
        self.assertEqual(self.power["root_erc_errors"],36)
        self.assertEqual(self.power["root_erc_warnings"],340)
        self.assertEqual(self.power["root_nets"],100)
        self.assertTrue(self.power["all_15_crossmodule_contracts_open_hold"])
if __name__=="__main__":unittest.main()
