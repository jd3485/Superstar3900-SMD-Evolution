"""V7.8 bounded numeric, vendor provenance, DNP and independent-clock tests."""
import csv
import hashlib
import math
from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.8"))
sys.path.insert(0,str(ROOT/"08_Firmware_Prototipi"/"V7.8"))
import audit_pinout_vendor_v78 as vendor
import dsp_nonperiodico_quantizzato_v78 as dsp

RTL=(ROOT/"08_Firmware_Prototipi"/"V7.8"/"rtl"/"clock_watchdog_indipendente_v78.v")
NS="http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def synthetic_xlsx(*,missing_pin=None,mismatch_pin=None):
    """An ephemeral TEST FIXTURE, NOT a copy of vendor Lattice XLSX."""
    source=vendor.candidate_48()
    strings=[]
    rows=[]
    for pin,name in source.items():
        if pin==missing_pin:
            continue
        if pin==mismatch_pin:
            name="FABRICATED_WRONG_SIGNAL"
        index=len(strings)
        strings.append(name)
        rows.append(f'<row r="{pin}"><c r="A{pin}"><v>{pin}</v></c>'
                    f'<c r="B{pin}" t="s"><v>{index}</v></c></row>')
    ss=f'<sst xmlns="{NS}">'+"".join(f"<si><t>{x}</t></si>" for x in strings)+"</sst>"
    sheet=f'<worksheet xmlns="{NS}"><sheetData>{"".join(rows)}</sheetData></worksheet>'
    temp=tempfile.TemporaryDirectory()
    filepath=Path(temp.name)/"SYNTHETIC_NOT_VENDOR.xlsx"
    with ZipFile(filepath,"w") as out:
        out.writestr("xl/worksheets/sheet1.xml",sheet)
        out.writestr("xl/sharedStrings.xml",ss)
    return temp,filepath


class V78(unittest.TestCase):
    def test_01_vendor_original_not_provided_and_explicit_hold(self):
        s=vendor.vendor_status()
        self.assertEqual(s["qualification"],"HOLD")
        self.assertFalse(s["original_binary_acquired"])
        self.assertFalse(s["vendor_hash_authenticated"])
        self.assertFalse(s["pinout_approved_for_pcb"])

    def test_02_vendor_candidate_has_48_pins_dnp(self):
        p=vendor.candidate_48()
        self.assertEqual(len(p),48)
        self.assertEqual(set(p),set(range(1,49)))
        self.assertEqual(p[35],"IOT_46b_G0")
        self.assertEqual(p[24],"VPP_2V5")

    def test_03_synthetic_fixture_parser_never_approves(self):
        t,p=synthetic_xlsx()
        with t:
            hashval=hashlib.sha256(p.read_bytes()).hexdigest()
            result=vendor.audit_sheet_against_candidate(
                p,hashval,worksheet_path="xl/worksheets/sheet1.xml",
                pin_column="A",signal_column="B",first_data_row=1)
            self.assertTrue(result["candidate_equal_to_selected_sheet"])
            self.assertEqual(result["parsed_pins"],48)
            self.assertFalse(result["physical_pinout_approved"])
            self.assertFalse(result["actual_original_xlsx_authenticated"])
            self.assertEqual(result["qualification"],"HOLD")

    def test_04_fake_or_changed_vendor_checksum_rejected(self):
        t,p=synthetic_xlsx()
        with t:
            with self.assertRaises(ValueError):
                vendor.audit_sheet_against_candidate(
                    p,"0"*64,worksheet_path="xl/worksheets/sheet1.xml",
                    pin_column="A",signal_column="B",first_data_row=1)

    def test_05_vendor_comparison_finds_mismatched_pin(self):
        t,p=synthetic_xlsx(mismatch_pin=42)
        with t:
            sha=hashlib.sha256(p.read_bytes()).hexdigest()
            result=vendor.audit_sheet_against_candidate(
                p,sha,worksheet_path="xl/worksheets/sheet1.xml",
                pin_column="A",signal_column="B",first_data_row=1)
            self.assertFalse(result["candidate_equal_to_selected_sheet"])
            self.assertEqual([a["pin"] for a in result["mismatches"]],[42])
            self.assertFalse(result["physical_pinout_approved"])

    def test_06_vendor_comparison_finds_missing_pin(self):
        t,p=synthetic_xlsx(missing_pin=15)
        with t:
            sha=hashlib.sha256(p.read_bytes()).hexdigest()
            result=vendor.audit_sheet_against_candidate(
                p,sha,worksheet_path="xl/worksheets/sheet1.xml",
                pin_column="A",signal_column="B",first_data_row=1)
            self.assertEqual(result["missing_pins"],[15])
            self.assertFalse(result["candidate_equal_to_selected_sheet"])

    def test_07_no_auto_discovery_of_vendor_sheet_or_columns(self):
        t,p=synthetic_xlsx()
        with t:
            sha=hashlib.sha256(p.read_bytes()).hexdigest()
            with self.assertRaises(ValueError):
                vendor.audit_sheet_against_candidate(
                    p,sha,worksheet_path="../hidden.xml",
                    pin_column="A",signal_column="B",first_data_row=1)

    def test_08_nonperiodic_dsp_streaming_invariant(self):
        x=dsp.analyze()
        self.assertEqual(x["audio_samples"],384)
        self.assertEqual(x["if2_baseband_samples"],384*80)
        self.assertTrue(x["chunk_invariance"])
        self.assertFalse(x["rf_permission"])
        self.assertFalse(x["hardware_implemented"])

    def test_09_nonperiodic_10bit_error_is_bounded(self):
        r=dsp.analyze()
        self.assertTrue(0<=r["min_code"]<=r["max_code"]<=1023)
        self.assertGreater(r["ideal_quantization"]["numerical_signal_to_error_db"],40)
        self.assertFalse(r["ideal_quantization"]["physical_DAC_SFDR_measured"])
        self.assertLess(r["max_abs_float_sample"],1)

    def test_10_nonperiodic_determinism(self):
        self.assertEqual(dsp.bounded_nonperiodic_audio(384,78),
                         dsp.bounded_nonperiodic_audio(384,78))
        self.assertNotEqual(dsp.bounded_nonperiodic_audio(100,78),
                            dsp.bounded_nonperiodic_audio(100,79))

    def test_11_loud_step_fails_closed(self):
        x=dsp.check_loud_step_rejection(1.0)
        self.assertGreater(x["filtered_peak"],1.0)
        self.assertFalse(x["quantization_accepted"])
        self.assertTrue(x["if_overrange_fail_closed"])
        self.assertFalse(x["rf_permission"])

    def test_12_nonfinite_input_rejected(self):
        with self.assertRaises(ValueError):
            dsp.check_loud_step_rejection(float("nan"))
        with self.assertRaises(ValueError):
            dsp.bounded_nonperiodic_audio(513)

    def test_13_rtl_requires_reference_domain_separate_from_master(self):
        src=RTL.read_text(encoding="utf-8")
        self.assertIn("independent_ref_clk_virtual",src)
        self.assertIn("master_clk_virtual",src)
        self.assertIn("v78_independent_ref_monitor",src)
        self.assertIn("missing_heartbeat_fault_latched",src)
        self.assertIn('async_reg = "true"',src)

    def test_14_rtl_cannot_release_pd_tx_or_analog(self):
        s=RTL.read_text(encoding="utf-8")
        self.assertEqual(s.count("assign dac_pd_released=1'b0;"),1)
        self.assertEqual(s.count("assign tx_rf_permission=1'b0;"),1)
        self.assertEqual(s.count("assign analog_path_connected=1'b0;"),1)
        self.assertFalse(dsp.tx_permission(ptt=True,watchdog=True))

    def test_15_physical_supervisor_is_only_candidate_and_not_connected(self):
        p=ROOT/"07_Componenti"/"BOM_WATCHDOG_PIN_AUDIT_V7.8.csv"
        with p.open(newline="",encoding="utf-8") as fh:
            rows=list(csv.DictReader(fh))
        self.assertEqual(len(rows),8)
        self.assertTrue(all(x["assembly"]=="DNP" and x["physical_connection"]=="OPEN" for x in rows))
        self.assertEqual(next(x["vendor_mpn"] for x in rows if x["reference"]=="U7901"),
                         "Texas Instruments TPS3840PH30DBVR")

    def test_16_virtual_netlist_all_open(self):
        p=ROOT/"01_Specifiche"/"V7.8"/"NETLIST_PUNTI_APERTI_V7.8.csv"
        with p.open(newline="",encoding="utf-8") as fh:
            rows=list(csv.DictReader(fh))
        self.assertEqual(len(rows),10)
        self.assertTrue(all(x["assembly"]=="DNP" and x["physical_connection"]=="OPEN"
                            and x["physical_pin_verified"]=="NO" for x in rows))

    def test_17_preserve_270_historic_rx_positions(self):
        p=ROOT/"02_Piano_Frequenze"/"V6.4"/"PIANO_PLL_LO_270_RX_V6.4.csv"
        with p.open(newline="",encoding="utf-8") as fh:
            rows=list(csv.DictReader(fh))
        self.assertEqual(len(rows),270)
        self.assertEqual(sum(x["alfa"]=="1" for x in rows),30)
        self.assertTrue(all(int(x["tx_permitted_v64"])==0 for x in rows))

    def test_18_previous_fpga_sg48_candidate_remains_hold(self):
        p=ROOT/"01_Specifiche"/"V7.6"/"SG48_PIN_PLAN_CANDIDATE_V7.6.csv"
        with p.open(newline="",encoding="utf-8") as fh:
            rows=list(csv.DictReader(fh))
        self.assertEqual(len(rows),49)
        self.assertTrue(all("HOLD" in x["design_qualification"] for x in rows))


if __name__=="__main__":
    unittest.main()
