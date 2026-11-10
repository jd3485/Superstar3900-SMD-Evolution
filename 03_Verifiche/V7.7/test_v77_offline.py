"""V7.7 model, hazard inventory, DNP and pinout-HOLD checks (offline)."""
import csv
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"08_Firmware_Prototipi"/"V7.7"))
sys.path.insert(0,str(ROOT/"08_Firmware_Prototipi"/"V7.6"))
import quantizzazione_e_sicurezza_offline_v77 as q

RTL=ROOT/"08_Firmware_Prototipi"/"V7.7"/"rtl"/"top_virtuale_v77.v"


class V77(unittest.TestCase):
    def test_01_quantization_snr_is_numerical_only(self):
        m=q.analyze_quantized_multitone()
        self.assertEqual(m["sample_count"],30720)
        self.assertEqual(m["audio_tones_hz"],[750,1250])
        self.assertGreater(m["quantization_snr_db"],46)
        self.assertLess(m["quantization_snr_db"],75)
        self.assertTrue(m["numerical_quantization_only"])
        self.assertIs(m["rf_permission"],False)

    def test_02_quantization_no_code_overflow(self):
        m=q.analyze_quantized_multitone()
        self.assertTrue(0<=m["code_min"]<=m["code_max"]<=1023)
        self.assertLess(m["peak_abs_input"],1.0)
        self.assertAlmostEqual(m["headroom"],0.70)

    def test_03_quantized_step_retains_previous_headroom_warning(self):
        m=q.analyze_quantized_step()
        self.assertGreater(m["peak"],0.45)
        self.assertLess(m["peak"],0.49)
        self.assertGreater(m["overshoot_percent"],12)
        self.assertLess(m["overshoot_percent"],17)
        self.assertTrue(0<=m["min_code"]<=m["peak_code"]<=1023)
        self.assertTrue(m["codes_do_not_represent_real_dac_io"])

    def test_04_decoding_is_bounded(self):
        a=q.decode_codes([0,512,1023])
        self.assertEqual(len(a),3)
        self.assertAlmostEqual(a[0],-1/0.7,places=5)
        self.assertAlmostEqual(a[-1],1/0.7,places=5)
        with self.assertRaises(ValueError): q.decode_codes([0],headroom=0)

    def test_05_hazards_explicitly_not_hardware_qualified(self):
        self.assertGreaterEqual(len(q.HAZARDS),10)
        for name in q.HAZARDS:
            p=q.study_hazard(name)
            self.assertTrue(p["independent_pd_assertion_required"])
            self.assertTrue(p["independent_rf_open_circuit_required"])
            self.assertFalse(p["hardware_fault_tolerant"])
            self.assertEqual(p["electrical_qualification_status"],"NOT_RUN")
            self.assertFalse(p["rf_permission"])
        with self.assertRaises(ValueError): q.study_hazard("ENABLE_RF")

    def test_06_hardware_is_unavailable_in_model(self):
        self.assertFalse(q.HARDWARE_PRESENT)
        self.assertFalse(q.PHYSICAL_DAC_PD_CONTROLLED)
        self.assertFalse(q.RF_CONNECTION_PRESENT)
        self.assertFalse(q.SUPERVISOR_ELECTRICAL_SCHEMATIC_VERIFIED)
        self.assertFalse(q.SINGLE_FAULT_PROTECTION_VALIDATED)

    def test_07_permission_is_unconditionally_false(self):
        for control in (True,False):
            self.assertFalse(q.tx_permission(ptt=control,supervisor=control,fpga=control))

    def test_08_top_has_constant_zero_hw_outputs(self):
        v=RTL.read_text(encoding="utf-8")
        self.assertIn("module v77_offline_top",v)
        for output in ("tx_rf_permission","dac_pd_released","analog_path_connected"):
            self.assertIn("assign "+output+"=1'b0;",v)
        self.assertIn("v76_virtual_fifo_guard",v)
        self.assertIn("v76_clock_ce",v)

    def test_09_top_exposes_diagnostics_not_a_physical_dac(self):
        v=RTL.read_text(encoding="utf-8")
        self.assertIn("diagnostic_sample_word",v)
        self.assertIn("independent_pd_guard_ok_virtual",v)
        self.assertIn("external_clock_watchdog_ok_virtual",v)
        self.assertNotIn("output wire dac900_clk",v)

    def test_10_new_bom_all_dnp_and_open(self):
        p=ROOT/"07_Componenti"/"BOM_TOP_VIRTUALE_V7.7.csv"
        with p.open(encoding="utf-8",newline="") as f: rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),8)
        self.assertTrue(all(x["assembly"]=="DNP" for x in rows))
        self.assertTrue(all(x["physical_connection"]=="OPEN" for x in rows))

    def test_11_new_netlist_all_dnp_and_open(self):
        p=ROOT/"01_Specifiche"/"V7.7"/"NETLIST_VIRTUAL_DIAGNOSTICA_V7.7.csv"
        with p.open(encoding="utf-8",newline="") as f: rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),10)
        self.assertTrue(all(x["assembly"]=="DNP" for x in rows))
        self.assertTrue(all(x["physical_connection"]=="OPEN" for x in rows))
        self.assertTrue(all(x["hardware_pin_verified"]=="NO" for x in rows))

    def test_12_pinout_primary_xlsx_remains_hold(self):
        p=ROOT/"01_Specifiche"/"V7.6"/"SG48_PIN_PLAN_CANDIDATE_V7.6.csv"
        with p.open(encoding="utf-8",newline="") as f: rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),49)
        self.assertTrue(all(x["assembly"]=="DNP" for x in rows))
        self.assertTrue(all("HOLD" in x["design_qualification"] for x in rows))
        self.assertIn("NOT_VENDOR_XLSX_CROSSCHECK",rows[0]["design_qualification"])

    def test_13_270_channel_historical_baseline_unchanged(self):
        p=ROOT/"02_Piano_Frequenze"/"V6.4"/"PIANO_PLL_LO_270_RX_V6.4.csv"
        with p.open(encoding="utf-8",newline="") as f: rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),270)
        self.assertEqual(sum(x["alfa"]=="1" for x in rows),30)
        self.assertTrue(all(int(x["tx_permitted_v64"])==0 for x in rows))

    def test_14_earlier_v76_is_dnp_and_open(self):
        p=ROOT/"01_Specifiche"/"V7.6"/"NETLIST_VIRTUAL_IO_V7.6.csv"
        with p.open(encoding="utf-8",newline="") as f: rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),8)
        self.assertTrue(all(x["physical_connection"]=="OPEN" for x in rows))


if __name__=="__main__":
    unittest.main()
