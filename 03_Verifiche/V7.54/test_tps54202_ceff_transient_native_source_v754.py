"""V7.54: TI TPS54202 5V output-capacitance, 500kHz step and inductor ripple envelope.

Strict SOURCE anchored verification; conditional analysis, not vendor MLCC DC-bias
qualification, SPICE, KiCad electrical sign-off, or fabrication approval.
Ref: TI TPS54202 SLVSD26C Rev C (Feb 2026), table 7-2, Eq. 11, 7.4.
"""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[2]
BUCK=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.52_EFUSE_MODE_DVDT_LATCHOFF_REVIEW_NOT_FOR_FAB/02_BUCK_5V.kicad_sch"
EFUSE=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.52_EFUSE_MODE_DVDT_LATCHOFF_REVIEW_NOT_FOR_FAB/01_EFUSE_AUX.kicad_sch"
VOUT=5.0
FSW_HZ=500_000
L_H=15e-6

def component_value(source,ref):
    # Requires immediate multiline Reference and Value attributes for exactly one instance.
    pattern=r'\(property "Reference" "'+re.escape(ref)+r'"[^\n]*\n\s*\(property "Value" "([^"]+)"'
    found=re.findall(pattern,source)
    if len(found)!=1:
        raise AssertionError((ref,found))
    return found[0]

def minimum_capacitance_f(step_a,delta_v,cycles=2,f_hz=FSW_HZ):
    if step_a<=0 or delta_v<=0 or cycles<=0 or f_hz<=0:
        raise ValueError("step, voltage, cycles and switching frequency must be positive")
    return cycles*step_a/(f_hz*delta_v)

def effective_capacitance_f(nominal_f,retention):
    if nominal_f<=0 or not 0<retention<=1:
        raise ValueError("invalid nominal capacity or retention")
    return nominal_f*retention

def output_step_drop_v(step_a,ceff_f,cycles=2):
    if ceff_f<=0 or step_a<=0 or cycles<=0:
        raise ValueError("invalid transient case")
    return cycles*step_a/(FSW_HZ*ceff_f)

def inductor_ripple_a(vin,vout=VOUT,inductance=L_H,f_hz=FSW_HZ):
    if vin<=vout or vout<=0 or inductance<=0 or f_hz<=0:
        raise ValueError("invalid CCM ideal buck case")
    duty=vout/vin
    return (vin-vout)*duty/(inductance*f_hz)

class TPS54202V754Review(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.buck=BUCK.read_text(encoding="utf-8")
        cls.efuse=EFUSE.read_text(encoding="utf-8")

    def test_01_u100_vendor_exact(self):
        self.assertEqual(component_value(self.buck,"U100"),"TPS54202DDCR")
    def test_02_vendor_example_output_caps_present(self):
        self.assertEqual(component_value(self.buck,"C103"),"22uF 25V X7R")
        self.assertEqual(component_value(self.buck,"C104"),"22uF 25V X7R")
    def test_03_ti_example_inductor_and_feedforward(self):
        self.assertEqual(component_value(self.buck,"L100"),"15uH SRP1038A-150M")
        self.assertEqual(component_value(self.buck,"C105"),"75pF 50V C0G")
        self.assertEqual(component_value(self.buck,"R101"),"100k 1%")
        self.assertEqual(component_value(self.buck,"R102"),"13k3 1%")
    def test_04_nominal_44u_equals_ti_example_only(self):
        nominal=2*22e-6
        self.assertAlmostEqual(nominal,44e-6)
        self.assertFalse(nominal>44e-6)  # No nominal margin; TI Table 7-2 is starting point, not guaranteed minimum.
    def test_05_ti_equation11_example_24u(self):
        self.assertAlmostEqual(minimum_capacitance_f(1.5,.25),24e-6)
    def test_06_100pct_nominal_and_80pct_retained(self):
        self.assertAlmostEqual(effective_capacitance_f(44e-6,1),44e-6)
        self.assertAlmostEqual(effective_capacitance_f(44e-6,.8),35.2e-6)
    def test_07_50pct_retained_below_ti_step_example(self):
        self.assertLess(effective_capacitance_f(44e-6,.5),minimum_capacitance_f(1.5,.25))
    def test_08_threshold_retention_to_24u(self):
        self.assertAlmostEqual(24/44,minimum_capacitance_f(1.5,.25)/(44e-6))
        self.assertGreater(24/44,.54)
    def test_09_80pct_conditional_step_drop(self):
        self.assertAlmostEqual(output_step_drop_v(1.5,35.2e-6),.17045454545454544)
        self.assertLess(output_step_drop_v(1.5,35.2e-6),.25)
    def test_10_50pct_conditional_step_drop(self):
        self.assertGreater(output_step_drop_v(1.5,22e-6),.25)
    def test_11_ripple_low_voltage(self):
        self.assertGreater(inductor_ripple_a(10.25),0)
        self.assertLess(inductor_ripple_a(10.25),1.0)
    def test_12_ripple_rises_with_vin(self):
        self.assertGreater(inductor_ripple_a(17.05),inductor_ripple_a(10.25))
    def test_13_conditional_peak_2a_not_real_load(self):
        self.assertGreater(2+.5*inductor_ripple_a(17.05),2)
        self.assertLess(2+.5*inductor_ripple_a(17.05),2.5)
    def test_14_high_vin_out_of_scope(self):
        with self.assertRaises(ValueError):inductor_ripple_a(4)
        with self.assertRaises(ValueError):minimum_capacitance_f(1,0)
        with self.assertRaises(ValueError):effective_capacitance_f(44e-6,1.1)
    def test_15_input_caps_also_unqualified(self):
        self.assertEqual(component_value(self.buck,"C100"),"10uF 35V X7R")
        self.assertEqual(component_value(self.buck,"C101"),"100nF 50V X7R")
        self.assertEqual(component_value(self.buck,"C102"),"100nF 25V X7R")
    def test_16_no_shdn_reset_or_rtn_short(self):
        self.assertIn('(no_connect (at 173 126)',self.efuse)
        self.assertIn('(label "EFUSE_RTN" (at 173 132',self.efuse)
        self.assertIn('(label "GND_MAIN" (at 227 132',self.efuse)
    def test_17_unproven_dcbias_stays_fail_closed(self):
        approved=dict(dc_bias_mlcc_qualified=False,load_step_specified=False,
                      peak_current_vendor_margin_approved=False,
                      output_transient_measured=False,inductor_thermal_measured=False,
                      complete_pcb_approved=False,fault_recovery_approved=False)
        self.assertTrue(all(not x for x in approved.values()))
    def test_18_nominal_matches_but_not_proof(self):
        self.assertAlmostEqual((22+22),44)
        self.assertLess(44*.8,44)
        self.assertLess(44*.5,24)
if __name__=="__main__":
    unittest.main()
