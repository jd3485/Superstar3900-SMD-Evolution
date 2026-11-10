"""V7.5 independent, offline only, with full GitHub checkout consistency tests."""
import csv
from itertools import product
from math import cos, pi, log10
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"08_Firmware_Prototipi"/"V7.5"))
import clock_pd_offline_v75 as clock
import interpolatore_multistadio_offline_v75 as fir


def signal(count, offset=0):
    return [0.4*cos(2*pi*750*(offset+i)/48_000) for i in range(count)]


class V75(unittest.TestCase):
    def test_01_clock_integer_divisors(self):
        self.assertEqual(clock.validate_rates(),(8,640,80))
        self.assertEqual(clock.MASTER_HZ,30_720_000)
        self.assertAlmostEqual(clock.period_ns(),32.5520833333,places=7)

    def test_02_exact_edge_counts(self):
        x=clock.clock_events(0,640*5)
        self.assertEqual(len(x["dac"]),5*80)
        self.assertEqual(len(x["audio"]),5)
        self.assertEqual(x["dac"][:3],[8,16,24])
        self.assertEqual(x["audio"],[640,1280,1920,2560,3200])
        self.assertTrue(set(x["audio"]).issubset(set(x["dac"])))
        self.assertFalse(x["real_hardware"])

    def test_03_absolute_edge_segmentation(self):
        a=clock.clock_events(0,291)
        b=clock.clock_events(291,640*3-291)
        joined=clock.clock_events(0,640*3)
        self.assertEqual(a["audio"]+b["audio"],joined["audio"])
        self.assertEqual(a["dac"]+b["dac"],joined["dac"])

    def test_04_rate_rejection(self):
        for args in ((30_720_000,4_000_000,48_000),
                     (30_720_000,3_840_000,44_100),
                     (-1,3_840_000,48_000),
                     (30_720_000.0,3_840_000,48_000)):
            with self.assertRaises(ValueError): clock.validate_rates(*args)
        with self.assertRaises(ValueError): clock.clock_events(-1,10)
        with self.assertRaises(ValueError): clock.clock_events(0,500_001)
        with self.assertRaises(ValueError): clock.clock_events(0,10.0)

    def test_05_resource_budget_and_startup(self):
        s=clock.resource_plan()
        self.assertEqual(s["dac_codes_per_block"],40_960)
        self.assertEqual(s["packed_16bit_bytes_per_block"],81_920)
        self.assertEqual(s["oscillator_max_startup_ticks_ceiling"],92_160)
        self.assertEqual(s["common_clock_ratio_drift_codes"],0)
        self.assertFalse(s["physical_fpga_pins_mapped"])
        with self.assertRaises(ValueError): clock.resource_plan(block_audio=513)

    def test_06_common_ppm_shifts_frequency_not_ratio(self):
        self.assertEqual(clock.worst_case_rate_error_hz(30_720_000),307.2)
        self.assertEqual(clock.worst_case_rate_error_hz(48_000),0.48)
        self.assertEqual(clock.worst_case_rate_error_hz(3_840_000),38.4)
        self.assertEqual(clock.validate_rates(),(8,640,80))
        with self.assertRaises(ValueError): clock.worst_case_rate_error_hz(48_000,-1)

    def test_07_guard_startup_threshold_without_hardware_release(self):
        p=clock.StartupFaultPlanner(16)
        for n in range(16):
            state=p.observe(n,oscillator_rail_ok=True,fpga_core_ok=True,
                            fpga_io_ok=True,fpga_config_ok=True,
                            clock_present=True,dac_rail_ok=True,
                            supervisor_ok=True,fifo_ready=True)
        self.assertTrue(state["guard_conditions_satisfied"])
        self.assertFalse(state["rf_path_connected"])
        self.assertFalse(state["tx_permission"])
        self.assertIsNone(state["dac_pd_asserted_in_proposed_physical_circuit"])

    def test_08_fault_latched_no_recover(self):
        p=clock.StartupFaultPlanner(8)
        p.observe(0,oscillator_rail_ok=True,fpga_core_ok=True,
                  fpga_io_ok=True,fpga_config_ok=True,clock_present=True,
                  dac_rail_ok=True,supervisor_ok=True,fifo_ready=True)
        q=p.observe(2,oscillator_rail_ok=True,fpga_core_ok=True,
                  fpga_io_ok=True,fpga_config_ok=True,clock_present=True,
                  dac_rail_ok=True,supervisor_ok=True,fifo_ready=True)
        self.assertEqual(q["fault"],"MISSING_MASTER_TICKS")
        self.assertEqual(p.inject_fault("PA_RELAY_SHORT")["fault"],"MISSING_MASTER_TICKS")

    def test_09_all_256_rail_config_states_denied(self):
        names=("oscillator_rail_ok","fpga_core_ok","fpga_io_ok",
               "fpga_config_ok","clock_present","dac_rail_ok",
               "supervisor_ok","fifo_ready")
        for state in product((False,True),repeat=8):
            p=clock.StartupFaultPlanner(8)
            snap=p.observe(0,**dict(zip(names,state)))
            self.assertIs(snap["tx_permission"],False)
            self.assertIs(snap["rf_path_connected"],False)
            if not all(state):
                self.assertEqual(snap["fault"],"MISSING_RAIL_CONFIG_CLOCK_OR_DATA")
        self.assertFalse(clock.TX_PERMISSION)
        self.assertFalse(clock.CLOCK_ELECTRICALLY_CONNECTED)

    def test_10_hazard_injections(self):
        for fault in ("PD_STUCK_LOW","OSC_STANDBY_OPEN",
                      "DAC_RAIL_BACKFEED","BRIDGE_CONFIG_LOSS",
                      "LOST_SYNC","PA_RELAY_SHORT","UNKNOWN"):
            p=clock.StartupFaultPlanner()
            self.assertEqual(p.inject_fault(fault)["fault"],fault)
            self.assertFalse(p.snapshot()["tx_permission"])
        with self.assertRaises(ValueError): clock.StartupFaultPlanner().inject_fault("RELEASE_TX")

    def test_11_phase_fir_normalization(self):
        for factor in (4,5):
            table=fir.phase_coefficients(factor)
            self.assertEqual(len(table),factor)
            self.assertTrue(all(len(t)==16 for t in table))
            self.assertTrue(all(abs(sum(t)-1)<1e-10 for t in table))
        with self.assertRaises(ValueError): fir.phase_coefficients(1)
        with self.assertRaises(ValueError): fir.phase_coefficients(5,15)

    def test_12_interpolator_exact_counts(self):
        m=fir.ThreeStageInterpolator()
        y=m.process([0.0]*30)
        self.assertEqual(len(y),2_400)
        self.assertTrue(all(z==0 for z in y))
        self.assertEqual(m.stats()["stages"],[(30,150),(150,600),(600,2400)])
        self.assertFalse(m.stats()["physical_dac_connected"])

    def test_13_interpolator_chunk_invariance(self):
        x=signal(384)
        one=fir.ThreeStageInterpolator().process(x)
        state=fir.ThreeStageInterpolator()
        chunks=state.process(x[:29])+state.process(x[29:173])+state.process(x[173:300])+state.process(x[300:])
        self.assertEqual(one,chunks)

    def test_14_reset_and_zero_initialization(self):
        m=fir.ThreeStageInterpolator()
        self.assertTrue(all(z==0 for z in m.process([0]*30)))
        m.process([0.5]*24)
        m.reset()
        self.assertEqual(m.stats()["input_samples"],0)
        self.assertEqual(m.process([0.5]*60),
                         fir.ThreeStageInterpolator().process([0.5]*60))

    def test_15_constant_settling_and_validated_bounds(self):
        m=fir.ThreeStageInterpolator()
        y=m.process([0.3]*512)
        self.assertLess(max(abs(s.real-0.3) for s in y[-400:]),0.001)
        self.assertLess(max(abs(s.imag) for s in y[-400:]),1e-12)
        with self.assertRaises(ValueError): m.process([0]*513)
        with self.assertRaises(ValueError): m.process([float("nan")])
        with self.assertRaises(ValueError): m.process([1.6])

    def test_16_tone_output_is_finite_and_nontrivial(self):
        m=fir.ThreeStageInterpolator()
        y=m.process(signal(512))
        last=y[-80*120:]
        self.assertEqual(len(last),9600)
        self.assertGreater(max(z.real for z in last)-min(z.real for z in last),0.65)
        self.assertTrue(all(abs(z.imag)<1e-12 for z in last))

    def test_17_budget_improvement_is_only_arithmetic(self):
        b=fir.numerical_mac_budget()
        self.assertEqual(b["stage_rates_hz"],[240_000,960_000,3_840_000])
        self.assertEqual(b["interpolation_total_sec"],80_640_000)
        self.assertEqual(b["hilbert_reference_products_sec"],6_144_000)
        self.assertEqual(b["combined_candidate_products_sec"],86_784_000)
        self.assertEqual(b["combined_previous_direct_products_sec"],129_024_000)
        self.assertGreater(b["estimated_products_reduction_percent"],32)
        self.assertLess(b["estimated_products_reduction_percent"],34)
        self.assertFalse(b["spectrum_or_realtime_certified"])

    def test_18_mpn_pin_mapping_and_dnp(self):
        bom=ROOT/"07_Componenti"/"BOM_CLOCK_BRIDGE_V7.5.csv"
        nets=ROOT/"01_Specifiche"/"V7.5"/"NETLIST_CLOCK_GUARDS_V7.5.csv"
        with bom.open(encoding="utf-8",newline="") as fh:
            components=list(csv.DictReader(fh))
        with nets.open(encoding="utf-8",newline="") as fh:
            pins=list(csv.DictReader(fh))
        self.assertEqual(len(components),8)
        self.assertEqual(len(pins),12)
        self.assertTrue(all(r["assembly"]=="DNP" for r in components+pins))
        self.assertEqual(next(r["mpn"] for r in components if r["reference"]=="X7601"),
                         clock.OSCILLATOR_MPN)
        self.assertEqual(next(r["mpn"] for r in components if r["reference"]=="U7601"),
                         clock.FPGA_CANDIDATE_MPN)
        osc={int(r["pin"]):r["function"] for r in pins if r["reference"]=="X7601"}
        self.assertEqual(osc,{1:"STANDBY_ACTIVE_LOW",2:"GND",3:"CLOCK_OUTPUT",4:"VDD"})
        self.assertTrue(all(r["reference"]!="U7601" for r in pins))
        self.assertFalse(any(r["net"].startswith("TX_RF") for r in pins))

    def test_19_cross_revision_dnp_and_unrouted_rf(self):
        p=ROOT/"07_Componenti"/"BOM_DAC_BRIDGE_IV_V7.4.csv"
        n=ROOT/"01_Specifiche"/"V7.4"/"NETLIST_CONTRATTI_DNP_V7.4.csv"
        with p.open(encoding="utf-8",newline="") as fh: bom=list(csv.DictReader(fh))
        with n.open(encoding="utf-8",newline="") as fh: net=list(csv.DictReader(fh))
        self.assertEqual(len(bom),7)
        self.assertTrue(all(x["assembly"]=="DNP" for x in bom+net))
        self.assertFalse(clock.tx_permission(ptt=True,final=True,bench=True))
        self.assertFalse(fir.tx_permission(ptt=True,dac=True))

    def test_21_default_startup_guard_matches_vendor_upper_bound(self):
        p=clock.StartupFaultPlanner()
        self.assertEqual(p.stable_required,92_160)
        self.assertEqual(clock.resource_plan()["oscillator_max_startup_ticks_ceiling"],92_160)
        self.assertFalse(p.snapshot()["tx_permission"])
        self.assertIsNone(p.snapshot()["dac_pd_asserted_in_proposed_physical_circuit"])

    def test_22_coherent_image_spectral_spot_checks(self):
        sys.path.insert(0, str(ROOT/"03_Verifiche"/"V7.5"))
        from analizza_immagini_multistadio_v75 import analyze
        results=analyze()
        self.assertAlmostEqual(results["wanted_750hz_amplitude"],0.4,delta=0.01)
        specs={"47250":-60,"48750":-60,
               "239250":-75,"240750":-75,
               "959250":-90,"960750":-90}
        for f,limit in specs.items():
            observed=results["nominal_digital_images"][f]["relative_to_750_hz_db"]
            self.assertLess(observed,limit,(f,observed,limit))
        self.assertFalse(results["rf_permission"])
        self.assertTrue(results["analog_reconstruction_not_modeled"])

    def test_20_preserve_270_channel_plan(self):
        p=ROOT/"02_Piano_Frequenze"/"V6.4"/"PIANO_PLL_LO_270_RX_V6.4.csv"
        with p.open(encoding="utf-8",newline="") as fh: rows=list(csv.DictReader(fh))
        self.assertEqual(len(rows),270)
        self.assertEqual(sum(r["alfa"]=="1" for r in rows),30)
        for r in rows:
            self.assertEqual(int(r["tx_permitted_v64"]),0)
            self.assertEqual(int(r["lo_hz"])-int(r["rf_hz"]),10_695_000)

if __name__=="__main__":
    unittest.main()
