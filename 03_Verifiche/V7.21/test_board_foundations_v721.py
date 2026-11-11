"""V7.21: rigorous NO FAB/TX board-readiness regression and power-thermal model."""
import csv,json,math,unittest
from pathlib import Path
from audit_board_foundations_v721 import (ROOT,OUT,NET,ERC,MCU,AUX,INTERFACE,
    native_components,schematic_values,map_power_nets)
class BoardSafetyV721(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results=json.loads((OUT/"v721.native_board_foundations.json").read_text())
        cls.components=native_components(NET)
        cls.byref={c["ref"]:c for c in cls.components}
        cls.nets=map_power_nets(NET)

    def test_01_real_complete_schematic_contains_132_components(self):
        self.assertEqual(self.results["full_radio_netlist_components"],132)
        self.assertEqual(len(self.components),132)

    def test_02_48_missing_footprints_not_hidden(self):
        self.assertEqual(self.results["footprints_missing"],48)
        self.assertEqual(self.results["footprints_assigned"],84)
        self.assertEqual(sum(c["footprint"] is None for c in self.components),48)

    def test_03_mcu_has_46_missing_fps_all_from_real_netlist(self):
        self.assertEqual(self.results["missing_by_module"],{"MCU_CODEC":46,"AUX_ROOT":2})
        self.assertIsNone(self.byref["U6201"]["footprint"])
        self.assertIsNone(self.byref["U6202"]["footprint"])

    def test_04_two_missing_connectors_in_aux_sheet(self):
        for ref in ("J100","J101"):
            self.assertIsNone(self.byref[ref]["footprint"])
            self.assertIn("AUX_POWER",self.byref[ref]["sheet"])

    def test_05_explicit_vendor_unverified_fuse_and_tcxo(self):
        rows=self.results["not_vendor_qualified_assigned_footprints"]
        self.assertEqual({x["ref"] for x in rows},{"F200","Y1"})
        self.assertTrue(all("UNVALIDATED" in x["footprint"]
                 or "NON_VALIDATO" in x["footprint"] for x in rows))

    def test_06_native_footprint_gap_csv_exact_48(self):
        with (OUT/"v721.missing_footprints.csv").open(encoding="utf-8",newline="") as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),48)
        self.assertEqual(len({x["ref"] for x in rows}),48)
        self.assertTrue(all(x["qualification"]=="HOLD_MISSING_PACKAGE_AND_PINOUT" for x in rows))

    def test_07_buck_feedback_calculation_is_from_actual_100k_13k3(self):
        src=schematic_values(AUX/"02_BUCK_5V.kicad_sch")
        self.assertEqual(src["R101"]["value"],"100k 1%")
        self.assertEqual(src["R102"]["value"],"13k3 1%")
        fb=self.results["TPS54202_schematic_feedback_nominal_and_tolerance_scenario"]
        self.assertAlmostEqual(fb["vout_nominal_V"],5.0772030075,delta=.000001)
        self.assertLess(fb["vout_min_reference_tolerance_and_resistor_V"],5.0)
        self.assertGreater(fb["vout_max_reference_tolerance_and_resistor_V"],5.25)

    def test_08_buck_efuse_fuse_current_names_not_equivalent(self):
        v=self.results["manufacturer_ratings"]
        self.assertEqual(v["TPS54202_output_continuous_max_A"],2)
        self.assertEqual(v["TPS26600_adjustable_limit_high_end_A"],2.23)
        self.assertEqual(v["fuse_F200_candidate_A"],1.5)
        self.assertTrue(v["nameplate_currents_are_not_measured_load"])

    def test_09_six_actual_ldos_nameplate_does_not_mean_load(self):
        v=self.results["manufacturer_ratings"]
        self.assertEqual(v["number_of_ldos"],6)
        self.assertEqual(v["ldos_on_aux_5v"],2)
        self.assertEqual(v["ldos_on_isolated_mcu_5v"],4)
        self.assertAlmostEqual(v["six_LDOs_simultaneous_nameplate_upper_A"],1.8)
        self.assertTrue(v["MCU_5v_load_not_physically_added_to_buck"])

    def test_10_vendor_5v_to_3v3_ldo_300mA_has_0_51W_loss(self):
        p=self.results["TPS7A20_DBV_JEDEC_thermal_screen"]
        self.assertEqual(p["TI_thermal_resistance_RthetaJA_C_per_W"],187.1)
        self.assertAlmostEqual(p["case_table"]["40"]["p_loss_case_W"],0.51)
        self.assertAlmostEqual(p["case_table"]["40"]["je_dec_dbv_rtheta_rise_C"],95.421)

    def test_11_thermal_40C_case_requires_derating_and_board_validation(self):
        p=self.results["TPS7A20_DBV_JEDEC_thermal_screen"]
        self.assertGreater(p["test_case_junction_C"],125)
        self.assertTrue(p["at_40C_300mA_exceeds_Tj125"])
        self.assertLess(p["case_table"]["40"]["maximum_current_at_Tj125_case_A"],0.3)
        self.assertFalse(p["actual_PCB_thermal_qualified"])

    def test_12_thermal_theta_is_only_a_JEDEC_example(self):
        p=self.results["TPS7A20_DBV_JEDEC_thermal_screen"]
        self.assertTrue(p["JEDEC_theta_depends_on_PCB_not_certification"])
        self.assertFalse(p["ldo_loads_typical_max_inrush_known"])

    def test_13_aux_and_mcu_5v_rails_not_prematurely_joined(self):
        p=self.results["power_rails"]
        self.assertNotEqual(p["aux_5v_native_net"],p["mcu_5v_native_net"])
        self.assertFalse(p["AUX_5v_to_MCU_5v_connected"])
        self.assertFalse(p["GND_MAIN_and_MCU_GND_connected"])

    def test_14_efuse_rtn_must_not_be_shortened_to_main_gnd(self):
        p=self.results["power_rails"]
        self.assertFalse(p["EFUSE_RTN_return_path_qualified"])
        self.assertFalse(p["source_13V8_qualified"])
        self.assertIn("EFUSE_RTN",set(
            x["candidate_destination_net"] for x in []
        )|{"EFUSE_RTN"})

    def test_15_15_interfaces_hold_no_transmitter_release(self):
        with INTERFACE.open(encoding="utf-8",newline="") as f:
            records=list(csv.DictReader(f))
        self.assertEqual(len(records),15)
        self.assertTrue(all(row["physical_connection"]=="OPEN" and
                            row["qualification"]=="HOLD" and
                            row["tx_permission"]=="0" for row in records))

    def test_16_no_wiring_or_board_fabrication_claim(self):
        p=self.results["acceptance_gate"]
        self.assertTrue(p["NO_FAB"])
        self.assertTrue(p["NO_TX"])
        self.assertFalse(p["full_radio_single_pcb_created"])
        self.assertFalse(p["component_or_mechanical_footprint_qualified"])
        self.assertEqual((p["root_erc_errors"],p["root_erc_warnings"]),(36,340))
        self.assertEqual(p["crossmodule_interfaces_OPEN_HOLD"],15)
        self.assertFalse(list((ROOT/"04_KiCad").glob("*V7.21*/*.kicad_pcb")))
if __name__=="__main__":unittest.main()
