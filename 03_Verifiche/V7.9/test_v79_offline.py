"""V7.9 clock cadence, watchdog window, RF isolation and LPF screening.

Tests only mathematical candidates and static DNP contracts, NOT hardware.
"""
import csv
import math
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"08_Firmware_Prototipi"/"V7.9"))
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.9"))
import controlli_clock_watchdog_v79 as watch
import analizza_filtro_srf_v79 as lpf


class V79(unittest.TestCase):
    def test_01_master_decimation_is_20ms_falling_period(self):
        d=watch.derive_cadence()
        self.assertEqual(d["master_ticks_per_toggle"],307200)
        self.assertAlmostEqual(d["toggle_frequency_hz"],100)
        self.assertAlmostEqual(d["falling_edges_per_second"],50)
        self.assertAlmostEqual(d["falling_edge_period_ms"],20)
        self.assertFalse(d["external_fpga_output_routed"])

    def test_02_old_v78_heartbeat_was_too_fast_for_32k_ref(self):
        x=watch.ref_sampling_risk()
        self.assertTrue(x["old_exceeds_ref_nyquist"])
        self.assertEqual(x["old_toggle_rate_hz"],3_840_000)
        self.assertTrue(x["new_below_ref_nyquist"])
        self.assertEqual(x["new_toggle_rate_hz"],100)
        self.assertAlmostEqual(x["nominal_ref_samples_per_toggle"],327.68)

    def test_03_watchdog_wdi_window_vendor_min_max_margin(self):
        x=watch.watchdog_window()
        self.assertEqual(x["vendor_lower_boundary_max_ms"],2.22)
        self.assertEqual(x["vendor_upper_boundary_min_ms"],23.375)
        self.assertTrue(x["math_window_pass"])
        self.assertGreater(x["lower_margin_ms"],17)
        self.assertGreater(x["upper_margin_ms"],3)
        self.assertFalse(x["physical_watchdog_built"])

    def test_04_window_worst_case_tolerance_study(self):
        for ppm in (0,10,20,100):
            self.assertTrue(watch.watchdog_window(ppm)["math_window_pass"])
        with self.assertRaises(ValueError): watch.watchdog_window(-1)
        with self.assertRaises(ValueError): watch.watchdog_window(float("nan"))

    def test_05_reject_invalid_rates_and_refs(self):
        with self.assertRaises(ValueError): watch.derive_cadence(0,1)
        with self.assertRaises(ValueError): watch.derive_cadence(30_720_000,-1)
        with self.assertRaises(ValueError): watch.derive_cadence(30_720_000.0,307200)
        with self.assertRaises(ValueError): watch.ref_sampling_risk(0)

    def test_06_real_watchdog_requirements_unmet(self):
        x=watch.watchdog_window()
        self.assertFalse(x["first_edge_after_power_up_verified"])
        self.assertFalse(x["external_single_fault_latch_present"])
        self.assertFalse(watch.INDEPENDENT_WATCHDOG_MOUNTED)
        self.assertFalse(watch.DAC_PD_PHYSCAL_DRIVER_PRESENT)
        self.assertFalse(watch.RF_OUTPUT_CONNECTED)

    def test_07_single_fault_hazard_cases_all_fail_closed_logically(self):
        names=("MASTER_STOPS","REF_CLOCK_STOPS","BOTH_CLOCKS_STOP",
          "WDO_STUCK_HIGH","WDO_STUCK_LOW","WDI_STUCK_HIGH",
          "WDI_STUCK_LOW","DISABLED_SET_CONFIG","DAC_PD_STUCK_LOW",
          "SUPERVISOR_UNPOWERED","SUPPLY_BACKFEED","RF_RELAY_WELDED")
        for name in names:
            d=watch.fault_study(name)
            self.assertTrue(d["unresolved_hardware_requirement"])
            self.assertFalse(d["physical_safe_state_electrically_validated"])
            self.assertFalse(d["rf_permission"])
        with self.assertRaises(ValueError): watch.fault_study("TX_ALLOWED")

    def test_08_rtl_has_exact_307200_counter_default_and_rf_constant_zero(self):
        p=ROOT/"08_Firmware_Prototipi"/"V7.9"/"rtl"/"slow_heartbeat_v79.v"
        s=p.read_text()
        self.assertGreaterEqual(s.count("MASTER_TICKS_PER_TOGGLE=307200"),1)
        self.assertIn("independent_ref_clk_virtual",s)
        self.assertIn("v78_independent_ref_monitor",s)
        self.assertGreaterEqual(s.count("assign tx_rf_permission=1'b0;"),2)
        self.assertGreaterEqual(s.count("assign dac_pd_released=1'b0;"),2)
        self.assertGreaterEqual(s.count("assign analog_path_connected=1'b0;"),2)

    def test_09_candidate_filter_values_explicit_and_different(self):
        n=lpf.nominal_elements()
        x=lpf.proposed_elements()
        self.assertEqual(len(n),7)
        self.assertEqual(len(x),7)
        self.assertAlmostEqual(x[0][1],4.7e-6)
        self.assertAlmostEqual(x[2][1],18e-6)
        self.assertGreater(x[2][1],n[2][1])
        self.assertGreater(x[0][1],n[0][1])

    def test_10_srf_parasitic_is_positive_and_physically_unvalidated(self):
        result=lpf.evaluate()
        self.assertFalse(result["physical_dac_iv_interface_validated"])
        self.assertFalse(result["vendor_component_model_validated"])
        self.assertFalse(result["vendor_q_at_455khz_known"])
        self.assertTrue(result["vendor_srf_typ_vs_min_mixed"])
        self.assertEqual(len(result["catalog_inductor_values"]),4)

    def test_11_rational_srf_model_under_images_only(self):
        for f in (455_000,3_385_000,4_295_000):
            s21,s11=lpf.approximate_abcd(f,lpf.proposed_elements())
            self.assertTrue(math.isfinite(s21.real))
            self.assertTrue(math.isfinite(s11.imag))
        with self.assertRaises(ValueError):
            lpf.approximate_abcd(12_000_000,lpf.proposed_elements())

    def test_12_filter_screen_returns_numerical_metrics_only(self):
        r=lpf.evaluate()
        self.assertTrue(math.isfinite(r["design_ideal_wanted_loss_db"]))
        self.assertTrue(math.isfinite(r["catalog_nominal_ideal_wanted_loss_db"]))
        self.assertTrue(math.isfinite(r["catalog_srf_approx_wanted_loss_db"]))
        self.assertGreater(r["catalog_srf_approx_min_image_rel_atten_db"],0)
        self.assertFalse(r["rf_permission"])

    def test_13_bom_all_dnp_open_and_vendor_parts(self):
        p=ROOT/"07_Componenti"/"BOM_WATCHDOG_FILTRO_V7.9.csv"
        with p.open(encoding="utf-8",newline="") as f: rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),11)
        self.assertTrue(all(v["assembly"]=="DNP" and v["connection"]=="OPEN" for v in rows))
        ref={x["reference"]:x for x in rows}
        self.assertEqual(ref["U8001"]["mpn"],watch.TPS3430_VENDOR_MPN)
        self.assertEqual(ref["X8001"]["mpn"],watch.ABRACON_REF_VENDOR_MPN)
        self.assertEqual(ref["L8003"]["mpn"],"MS590PNB183MSZ")

    def test_14_watchdog_dnp_pin_netlist_vendor_matched(self):
        p=ROOT/"01_Specifiche"/"V7.9"/"NETLIST_WATCHDOG_CANDIDATA_DNP_V7.9.csv"
        with p.open(encoding="utf-8",newline="") as f: rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),15)
        self.assertTrue(all(x["assembly"]=="DNP" and x["physical_connection"]=="OPEN" for x in rows))
        pins={str(x["pin_number"]):x["vendor_pin_function"] for x in rows if x["reference"]=="U8001"}
        self.assertEqual(pins,{"1":"VDD1","2":"CWD","3":"SET0","4":"CRST","5":"GND",
             "6":"SET1","7":"WDI","8":"WDO","9":"NC","10":"VDD2","PADDLE":"GND_THERMAL_PAD"})

    def test_15_no_physical_rf_permission(self):
        for f in (True,False):
            self.assertFalse(watch.tx_permission(ptt=f,watchdog=f))
            self.assertFalse(lpf.tx_permission(ptt=f,filter=f))

    def test_16_historic_rx_channel_plan_preserved(self):
        p=ROOT/"02_Piano_Frequenze"/"V6.4"/"PIANO_PLL_LO_270_RX_V6.4.csv"
        with p.open(newline="",encoding="utf-8") as fh: rows=list(csv.DictReader(fh))
        self.assertEqual(len(rows),270)
        self.assertEqual(sum(r["alfa"]=="1" for r in rows),30)
        self.assertTrue(all(int(r["tx_permitted_v64"])==0 for r in rows))

    def test_17_lattice_original_pinout_still_hold(self):
        p=ROOT/"01_Specifiche"/"V7.6"/"SG48_PIN_PLAN_CANDIDATE_V7.6.csv"
        with p.open(newline="",encoding="utf-8") as fh: rows=list(csv.DictReader(fh))
        self.assertEqual(len(rows),49)
        self.assertTrue(all("HOLD" in r["design_qualification"] for r in rows))


if __name__=="__main__":
    unittest.main()
