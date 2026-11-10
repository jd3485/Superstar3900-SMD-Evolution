"""V7.4 software and historical CSV checks. NO physical peripheral is touched."""
import csv
import math
from itertools import product
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"08_Firmware_Prototipi"/"V7.4"))
sys.path.insert(0,str(ROOT/"08_Firmware_Prototipi"/"V7.3"))
import dac900_bridge_offline_v74 as m
import duc_if2_causale_v73 as v73


class TestBridgeV74(unittest.TestCase):
    def test_01_clock_rates_and_ratio(self):
        self.assertEqual(m.SAMPLE_RATE_HZ,3840000)
        self.assertEqual(m.AUDIO_RATE_HZ,48000)
        self.assertEqual(m.UPSAMPLE,80)
        self.assertAlmostEqual(m.CLOCK_PERIOD_NS,260.4166666667,places=6)
        self.assertAlmostEqual(m.CLOCK_HALF_PERIOD_NS,130.2083333333,places=6)

    def test_02_vendor_binary_conversion(self):
        self.assertEqual(m.current_output_a(0),0.0)
        self.assertAlmostEqual(m.current_output_a(1023),0.02*1023/1024)
        self.assertAlmostEqual(m.complementary_current_a(0),0.02*1023/1024)
        self.assertEqual(m.complementary_current_a(1023),0.0)
        self.assertAlmostEqual(m.current_output_a(512),0.01)

    def test_03_complementary_current_sum(self):
        for code in (0,1,256,511,512,768,1023):
            self.assertAlmostEqual(m.current_output_a(code)+m.complementary_current_a(code),
                                   0.02*1023/1024)

    def test_04_current_rejects_invalid_inputs(self):
        for code in (-1,1024,1.0,None,True,"512"):
            with self.assertRaises(ValueError): m.current_output_a(code)
        for fs in (-0.1,0,0.001,0.021,float("nan"),float("inf")):
            with self.assertRaises(ValueError): m.current_output_a(100,fs)

    def test_05_doubly_terminated_ideal_iv(self):
        r=m.effective_resistance_ohm()
        self.assertAlmostEqual(r,24.95,places=5)
        v=m.ideal_terminated_voltage_v(1023)
        self.assertAlmostEqual(v,0.02*1023/1024*24.95,places=10)
        self.assertGreater(v,0.49)
        self.assertLess(v,0.50)
        self.assertEqual(m.ideal_terminated_voltage_v(0),0.0)

    def test_06_voltage_monotone(self):
        vals=[m.ideal_terminated_voltage_v(code) for code in range(0,1024,23)]
        self.assertTrue(all(0 <= a < b < 0.51 for a,b in zip(vals,vals[1:])))

    def test_07_resistor_one_percent_extremes(self):
        lo,hi=m.load_tolerance_sweep()
        nominal=m.ideal_terminated_voltage_v(1023)
        self.assertLess(lo,nominal)
        self.assertGreater(hi,nominal)
        self.assertGreater(lo,nominal*0.989)
        self.assertLess(hi,nominal*1.011)

    def test_08_load_validation(self):
        for r in (0,-10,float("nan"),float("inf")):
            with self.assertRaises(ValueError): m.effective_resistance_ohm(r,49.9)
        with self.assertRaises(ValueError): m.effective_resistance_ohm(49.9,0)
        with self.assertRaises(ValueError): m.load_tolerance_sweep(tolerance_fraction=.1)

    def test_09_power_and_compliance(self):
        q=m.analog_study(1023)
        self.assertTrue(q["output_compliance_in_vendor_range"])
        self.assertLess(q["shunt_power_w"],0.0051)
        self.assertLess(q["termination_power_w"],0.0051)
        self.assertLess(q["termination_voltage_v"],1.25)
        self.assertFalse(q["hardware_implemented"])
        self.assertFalse(q["rf_tx_allowed"])

    def test_10_clock_budget_fifo_and_bytes(self):
        b=m.clock_data_budget()
        self.assertEqual(b["data_toggle_rate_upper_bits_per_second"],38400000)
        self.assertEqual(b["packed_bus_bytes_per_second"],7680000)
        self.assertEqual(b["buffer_bytes_for_512_audio_samples"],81920)
        self.assertEqual(b["packed_word_bytes"],2)
        self.assertFalse(b["physical_clock_source"])
        self.assertFalse(b["physical_parallel_bridge"])

    def test_11_clock_fifo_normal_trace(self):
        bridge=m.OfflineParallelBridge()
        bridge.enqueue([0,512,1023])
        a=bridge.cycle()
        z=bridge.cycle()
        last=bridge.cycle()
        self.assertEqual((a["hypothetical_word"],z["hypothetical_word"],last["hypothetical_word"]),
                         (0,512,1023))
        self.assertEqual(last["queued"],0)
        self.assertAlmostEqual(a["following_falling_edge_ns"],m.CLOCK_HALF_PERIOD_NS)
        self.assertAlmostEqual(z["rising_edge_ns"],m.CLOCK_PERIOD_NS)
        self.assertEqual(last["virtual_cycles"],3)
        self.assertTrue(all(k["pd_asserted_in_model"] for k in (a,z,last)))
        self.assertTrue(all(k["rf_tx_allowed"] is False for k in (a,z,last)))

    def test_12_fifo_underflow_latches_fault(self):
        bridge=m.OfflineParallelBridge()
        self.assertEqual(bridge.cycle()["fault"],"FIFO_UNDERFLOW")
        self.assertEqual(bridge.cycle()["virtual_cycles"],0)
        with self.assertRaises(RuntimeError): bridge.enqueue([1])

    def test_13_fifo_overflow_is_fail_closed(self):
        bridge=m.OfflineParallelBridge()
        with self.assertRaises(OverflowError): bridge.enqueue([300]*1025)
        self.assertEqual(bridge.queued,0)
        self.assertEqual(bridge.cycle()["fault"],"FIFO_OVERFLOW")

    def test_14_invalid_code_faults_and_rolls_back(self):
        bridge=m.OfflineParallelBridge()
        bridge.enqueue([1,2])
        with self.assertRaises(ValueError): bridge.enqueue([3,1024,4])
        self.assertEqual(bridge.queued,0)
        self.assertEqual(bridge.fault,"INVALID_CODE")

    def test_15_supply_and_clock_faults(self):
        a=m.OfflineParallelBridge()
        a.enqueue([7])
        self.assertEqual(a.cycle(clock_present=False)["fault"],"CLOCK_MISSING")
        b=m.OfflineParallelBridge()
        b.enqueue([7])
        self.assertEqual(b.cycle(supply_good=False)["fault"],"POWER_NOT_GOOD")
        self.assertEqual(b.queued,0)

    def test_16_timing_violation_and_bounds(self):
        for params in (
            dict(valid_before_rising_ns=1),
            dict(valid_after_rising_ns=1),
            dict(valid_before_rising_ns=float("nan")),
            dict(valid_after_rising_ns=float("inf")),
            dict(valid_after_rising_ns=m.CLOCK_HALF_PERIOD_NS+1),
        ):
            bridge=m.OfflineParallelBridge()
            bridge.enqueue([7])
            self.assertEqual(bridge.cycle(**params)["fault"],"DATA_TIMING_NOT_MET")
            self.assertEqual(bridge.queued,0)
            self.assertTrue(bridge.diagnostics()["pd_asserted_in_model"])
        self.assertGreater(m.ASSUMED_REQUIRED_SETUP_NS,m.TI_DATASHEET_SETUP_TYP_NS)
        self.assertGreater(m.ASSUMED_REQUIRED_HOLD_NS,m.TI_DATASHEET_HOLD_TYP_NS)

    def test_17_independent_clock_drift_budget(self):
        self.assertEqual(m.fifo_skew_samples(0,100),0)
        self.assertAlmostEqual(m.fifo_skew_samples(50,1),192)
        self.assertAlmostEqual(m.fifo_skew_samples(-50,1),-192)
        self.assertAlmostEqual(m.fifo_skew_samples(50,1024/192),1024,places=6)
        for x,seconds in ((float("nan"),1),(20,-1)):
            with self.assertRaises(ValueError): m.fifo_skew_samples(x,seconds)

    def test_18_all_control_states_tx_denied(self):
        self.assertFalse(m.DAC_MOUNTED)
        self.assertFalse(m.BRIDGE_MOUNTED)
        self.assertFalse(m.CLOCK_SOURCE_MOUNTED)
        self.assertFalse(m.PD_PHYSICALLY_RELEASED)
        self.assertFalse(m.ANALOG_LINK_MOUNTED)
        self.assertFalse(m.TX_RF_ENABLED)
        keys=("ptt","dac_present","pll","fault_ok","supply_good","pa","clock","bridge","bench")
        for states in product((False,True),repeat=len(keys)):
            self.assertIs(m.tx_permission(**dict(zip(keys,states))),False)

    def test_19_dnp_bom_netlist_and_v73_vendor_pin_untouched(self):
        bom=ROOT/"07_Componenti"/"BOM_DAC_BRIDGE_IV_V7.4.csv"
        net=ROOT/"01_Specifiche"/"V7.4"/"NETLIST_CONTRATTI_DNP_V7.4.csv"
        older=ROOT/"01_Specifiche"/"V7.3"/"NETLIST_PIN_DAC900_V7.3.csv"
        with bom.open(newline="",encoding="utf-8") as f: comp=list(csv.DictReader(f))
        with net.open(newline="",encoding="utf-8") as f: rows=list(csv.DictReader(f))
        with older.open(newline="",encoding="utf-8") as f: pins=list(csv.DictReader(f))
        self.assertEqual(len(comp),7)
        self.assertEqual(len(rows),8)
        self.assertTrue(all(x["assembly"]=="DNP" for x in comp+rows))
        self.assertTrue(all(x["mpn"]=="Vishay CRCW060349R9FKEA" for x in comp
                            if x["reference"] in ("R7501","R7502")))
        self.assertEqual(len([x for x in pins if x["reference"]=="U7401"]),28)
        self.assertTrue(all(x["assembly"]=="DNP" for x in pins))
        self.assertIn("UNROUTED",next(x["concept_net"] for x in pins
                       if x["reference"]=="U7401" and x["pin"]=="22"))
        # R7503 remains unpopulated, separating analogue DAC from any filter.
        link={x["pin"]:x["concept_net"] for x in rows if x["reference"]=="R7503"}
        self.assertEqual(link,{"1":"DAC_IOUT_NOT_CONNECTED",
                               "2":"F7401_LPF_NOT_CONNECTED"})

    def test_20_streaming_model_to_hypothetical_dac_codes(self):
        v=v73.CausalIF2("AM").process([0.0]*8)
        self.assertEqual(len(v),640)
        codes=v73.quantize_unsigned_10bit(v)
        self.assertEqual(len(codes),640)
        bridge=m.OfflineParallelBridge()
        bridge.enqueue(codes)
        trace=[bridge.cycle() for _ in range(5)]
        self.assertEqual([z["hypothetical_word"] for z in trace],codes[:5])
        volts=[m.ideal_terminated_voltage_v(code) for code in codes]
        self.assertTrue(all(0<=v<0.51 for v in volts))
        self.assertTrue(all(not z["rf_tx_allowed"] for z in trace))

    def test_21_historic_270_plan_preserved(self):
        plan=ROOT/"02_Piano_Frequenze"/"V6.4"/"PIANO_PLL_LO_270_RX_V6.4.csv"
        with plan.open(newline="",encoding="utf-8") as f: rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),270)
        self.assertEqual(sum(r["alfa"]=="1" for r in rows),30)
        for row in rows:
            self.assertEqual(int(row["tx_permitted_v64"]),0)
            self.assertEqual(int(row["lo_hz"])-int(row["rf_hz"]),10_695_000)

if __name__=="__main__":
    unittest.main()
