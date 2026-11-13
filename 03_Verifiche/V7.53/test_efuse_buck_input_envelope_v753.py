"""V7.53 preliminary eFuse/buck/fuse capacity envelope: review only, never signoff.

Manufacturer sources:
TI TPS2660 SLVSDG2G Rev G, equations ILIM=12/R(kohm), mode Table 2.
TI TPS54202 SLVSD26C Rev C, 5V/2A MAX OUTPUT capability and soft-start.
All currents here are static idealized POWER balances; efficiency is an
assumption, not a measured board result. Current design has no qualified
external switch for independent eFuse recovery.
"""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[2]
EFUSE=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.52_EFUSE_MODE_DVDT_LATCHOFF_REVIEW_NOT_FOR_FAB/01_EFUSE_AUX.kicad_sch"

def symbol_value(text,ref):
    # Only read field from a symbol's immediate reference/value pair.
    m=re.search(r'\(property "Reference" "'+re.escape(ref)+r'"[^\n]*\n\s*\(property "Value" "([^"]+)"',text)
    if not m: raise AssertionError("Missing reference/value "+ref)
    return m.group(1)

def buck_input_a(vin,output_a,efficiency):
    if not (vin>0 and 0<efficiency<=1 and output_a>=0):
        raise ValueError("invalid scenario")
    return 5.0*output_a/(vin*efficiency)

def efuse_limit_nominal_a(resistor_kohm):
    if resistor_kohm<=0: raise ValueError("invalid R")
    return 12.0/resistor_kohm

class TestV753PowerEnvelope(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src=EFUSE.read_text(encoding="utf8")
    def test_01_correct_real_components(self):
        self.assertEqual(symbol_value(self.src,"R203"),"8k2 1%")
        self.assertEqual(symbol_value(self.src,"R204"),"402k 1% MODE_LATCHOFF_CANDIDATE")
        self.assertEqual(symbol_value(self.src,"C201"),"22nF 50V X7R")
        self.assertIn('1.5A 045101.5MRL CANDIDATO',symbol_value(self.src,"F200"))
    def test_02_shdn_not_actuated(self):
        self.assertIn('(no_connect (at 173 126)',self.src)
        self.assertIn('SHDN / IMON / FLT non collegati',self.src)
    def test_03_reverse_rtn_separation_source(self):
        self.assertIn('(label "EFUSE_RTN" (at 173 132',self.src)
        self.assertIn('(label "GND_MAIN" (at 227 132',self.src)
        self.assertIn('(label "EFUSE_RTN" (at 200 137',self.src)
    def test_04_nominal_current_limit_not_fuse_clearance(self):
        self.assertAlmostEqual(efuse_limit_nominal_a(8.2),1.4634146341463414)
        # IMPORTANT: nominal eFuse current threshold is not fuse blow current.
        self.assertGreater(efuse_limit_nominal_a(8.2),1.5*0.75)
    def test_05_fuse_review_heuristic_not_vendor_rating(self):
        self.assertAlmostEqual(1.5*0.75,1.125)
    def test_06_10p25v_full_load_85percent_exceeds_heuristic(self):
        self.assertGreater(buck_input_a(10.25,2.0,0.85),1.125)
        self.assertAlmostEqual(buck_input_a(10.25,2.0,0.85),1.1477761836441895)
    def test_07_13p8v_10w_example(self):
        self.assertAlmostEqual(buck_input_a(13.8,2.0,0.85),0.8525149190110827)
    def test_08_low_vin_80percent_more_demand(self):
        self.assertGreater(buck_input_a(10.25,2.0,0.80),buck_input_a(10.25,2.0,0.85))
    def test_09_5v_limit_output_for_hypothetical_85percent(self):
        # Not a real power budget until downstream RX + MCU + AUX loads verified.
        imax=1.125*10.25*0.85/5.0
        self.assertAlmostEqual(imax,1.9603125)
        self.assertLess(imax,2.0)
    def test_10_nominal_ilim_resistor_spread(self):
        low=8.2*(1-0.01);high=8.2*(1+0.01)
        self.assertLess(efuse_limit_nominal_a(high),efuse_limit_nominal_a(8.2))
        self.assertGreater(efuse_limit_nominal_a(low),efuse_limit_nominal_a(8.2))
    def test_11_invalid_assumptions_fail_closed(self):
        with self.assertRaises(ValueError):buck_input_a(0,2,.85)
        with self.assertRaises(ValueError):buck_input_a(10.25,2,0)
        with self.assertRaises(ValueError):buck_input_a(10.25,2,1.1)
    def test_12_no_release_assertion(self):
        flags=dict(recovery_qualified=False,real_load_budget_verified=False,
                   fuse_curve_coordinated=False,inrush_measured=False,
                   crossmodule_ground_join_approved=False,pcb_fab_approved=False)
        self.assertTrue(all(not x for x in flags.values()))

if __name__=="__main__":
    unittest.main()
