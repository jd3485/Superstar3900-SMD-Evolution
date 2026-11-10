"""V7.6 offline pin/RTL contract/spectral regression, never physical TX."""
import csv
import math
import re
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.6"))
sys.path.insert(0,str(ROOT/"08_Firmware_Prototipi"/"V7.5"))
import analizza_multitono_transienti_v76 as spectra
import interpolatore_multistadio_offline_v75 as fir
import clock_pd_offline_v75 as clock

PINPATH=ROOT/"01_Specifiche"/"V7.6"/"SG48_PIN_PLAN_CANDIDATE_V7.6.csv"
PCFPATH=ROOT/"01_Specifiche"/"V7.6"/"FPGA_PINS_PROPOSTI_V7.6.pcf"
RTLPATH=ROOT/"08_Firmware_Prototipi"/"V7.6"/"rtl"/"clock_fifo_virtual_v76.v"


def load_pins():
    with PINPATH.open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))


def pcf():
    rows=[]
    for line in PCFPATH.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("set_io "):
            _,name,pin=line.split()
            rows.append((name,int(pin)))
    return rows


class TestV76(unittest.TestCase):
    def test_01_complete_sg48_dnp_inventory(self):
        x=load_pins()
        self.assertEqual(len(x),49)
        self.assertEqual({int(p["pin"]) for p in x if p["pin"].isdigit()},set(range(1,49)))
        self.assertEqual(len([p for p in x if p["pin"]=="PADDLE"]),1)
        self.assertTrue(all(p["assembly"]=="DNP" for p in x))
        self.assertTrue(all("HOLD" in p["design_qualification"] for p in x))

    def test_02_critical_fpga_rails_and_config_protected(self):
        x={p["pin"]:p for p in load_pins()}
        expected={"1":"VCCIO_2","5":"VCC","30":"VCC","29":"VCCPLL",
                  "22":"SPI_VCCIO1","24":"VPP_2V5","33":"VCCIO_0",
                  "7":"CDONE","8":"CRESET_B","39":"RGB0","40":"RGB1","41":"RGB2"}
        for key,value in expected.items():
            self.assertEqual(x[key]["source_signal"],value)
            self.assertTrue("UNALLOCATED" in x[key]["proposed_role"] or
                "NOT_ROUTED" in x[key]["proposed_role"] or
                "NOT_GENERAL_GPIO" in x[key]["proposed_role"])
        self.assertEqual(x["PADDLE"]["source_signal"],"GND_EXPOSED_PAD")

    def test_03_pcf_no_pin_collision(self):
        assignments=pcf()
        self.assertGreaterEqual(len(assignments),25)
        self.assertEqual(len(assignments),len(set(name for name,_ in assignments)))
        self.assertEqual(len(assignments),len(set(pin for _,pin in assignments)))
        self.assertTrue(all(1<=pin<=48 for _,pin in assignments))

    def test_04_pcf_agrees_with_dnp_pin_plan(self):
        entries={int(x["pin"]):x for x in load_pins() if x["pin"].isdigit()}
        for name,pin in pcf():
            role=entries[pin]["proposed_role"]
            self.assertNotIn("UNALLOCATED",role)
            self.assertNotIn("UNROUTED",role)
            self.assertNotIn("NOT_GENERAL_GPIO",role)
            self.assertNotIn("POWER_DOMAIN",role)
            self.assertTrue(role.endswith("CANDIDATE") or role.endswith("INPUT_ONLY")
                            or role=="FIFO_PUSH_VALID_IN" or
                            role.startswith("FIFO_WRITE_WORD_"))
        self.assertIn(("master_clk_candidate",35),pcf())
        self.assertIn(("dac_clk_candidate",42),pcf())

    def test_05_pcf_carries_exact_data_buses(self):
        labels=[x for x,_ in pcf()]
        for bus in ("dac_word_candidate","source_word_candidate"):
            self.assertEqual(sorted(int(re.search(r"\[(\d+)\]",x).group(1))
                for x in labels if x.startswith(bus+"[")), list(range(10)))

    def test_06_hold_vendor_pinout_and_no_hardware_claim(self):
        p=PCFPATH.read_text()
        self.assertIn("vendor",p.lower())
        self.assertIn("DO NOT USE FOR PCB",p)
        self.assertIn("NO physical DAC900",p)
        self.assertFalse(clock.FPGA_CONFIGURED_IN_HARDWARE)
        self.assertFalse(clock.DAC_PD_HARDWIRED)

    def test_07_rtl_has_const_zero_permission_and_no_physical_pin(self):
        src=RTLPATH.read_text()
        self.assertEqual(src.count("assign tx_rf_permission=1'b0;"),2)
        self.assertIn("assign dac_pd_released=1'b0;",src)
        self.assertIn("assign analog_path_connected=1'b0;",src)
        self.assertIn("FAULT",src.upper())
        self.assertNotIn("tx_enable = 1'b1",src)

    def test_08_multitone_coherent_amplitudes(self):
        d=spectra.analyze_multitone()
        self.assertAlmostEqual(d["wanted"]["750"],0.35,delta=0.01)
        self.assertAlmostEqual(d["wanted"]["1250"],0.24,delta=0.01)
        self.assertFalse(d["nominal_hardware_or_emissions_result"])

    def test_09_multitone_images_are_bounded_in_numerical_model(self):
        d=spectra.analyze_multitone()
        for f,images in d["images_relative_db"].items():
            self.assertEqual(len(images),6)
            for freq,rel in images.items():
                self.assertLess(rel,-65,(f,freq,rel))
        self.assertFalse(d["tx_rf_permission"])

    def test_10_step_has_causal_settling_without_nonfinite_samples(self):
        d=spectra.analyze_step()
        self.assertEqual(d["samples_before"],256*80)
        self.assertEqual(d["samples_rise"],512*80)
        self.assertEqual(d["samples_fall"],512*80)
        self.assertAlmostEqual(d["end_of_rise_average"],0.4,delta=0.01)
        self.assertLess(d["end_of_fall_average_abs"],0.01)
        self.assertLess(d["rise_peak"],0.7)
        self.assertFalse(d["rf_tx_permission"])

    def test_11_step_split_across_calls_is_identical(self):
        one=fir.ThreeStageInterpolator().process([0.4]*250)
        st=fir.ThreeStageInterpolator()
        segmented=st.process([0.4]*70)+st.process([0.4]*83)+st.process([0.4]*97)
        self.assertEqual(one,segmented)

    def test_12_legacy_dsp_budget_not_rtl_synthesis(self):
        b=fir.numerical_mac_budget()
        self.assertEqual(b["combined_candidate_products_sec"],86_784_000)
        self.assertFalse(b["hardware_implemented"])
        self.assertFalse(b["spectrum_or_realtime_certified"])

    def test_13_previous_model_always_denies_tx(self):
        self.assertFalse(clock.tx_permission(ptt=True,clock=True,power=True))
        self.assertFalse(fir.tx_permission(dac=True,fpga=True))
        self.assertFalse(clock.RF_OUTPUT_ROUTED)

    def test_14_historic_270_frequency_plan_intact(self):
        p=ROOT/"02_Piano_Frequenze"/"V6.4"/"PIANO_PLL_LO_270_RX_V6.4.csv"
        with p.open(encoding="utf-8",newline="") as f: rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),270)
        self.assertEqual(sum(r["alfa"]=="1" for r in rows),30)
        self.assertTrue(all(int(r["tx_permitted_v64"])==0 for r in rows))
        self.assertTrue(all(int(r["lo_hz"])-int(r["rf_hz"])==10_695_000 for r in rows))

    def test_15_new_bom_netlist_all_dnp_and_links_open(self):
        b=ROOT/"07_Componenti"/"BOM_SIMULAZIONE_RTL_V7.6.csv"
        n=ROOT/"01_Specifiche"/"V7.6"/"NETLIST_VIRTUAL_IO_V7.6.csv"
        with b.open(newline="",encoding="utf-8") as f: parts=list(csv.DictReader(f))
        with n.open(newline="",encoding="utf-8") as f: links=list(csv.DictReader(f))
        self.assertEqual(len(parts),5)
        self.assertEqual(len(links),8)
        self.assertTrue(all(x["assembly"]=="DNP" for x in parts+links))
        self.assertTrue(all(x["physical_connection"]=="OPEN" for x in links))
        self.assertFalse(any(x["physical_connection"]=="CLOSED" for x in links))


if __name__=="__main__":
    unittest.main()
