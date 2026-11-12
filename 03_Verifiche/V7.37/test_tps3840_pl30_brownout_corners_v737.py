"""V7.37 TPS3840PL30 + TPS7A2033 static PVT-corner interface gate.

This is a worst-case algebraic envelope based on TI SNVSB03E (May 2026) and
SBVS338H (July 2024), NOT SPICE, circuit timing, or hardware validation.
It explicitly leaves the below-VPOR and dropout/brownout regimes UNKNOWN.
"""
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMATIC = ROOT / (
    "04_KiCad/Modulo_MCU_CODEC_V7.36_C6231_MURATA_GRM15_REVIEW_NOT_FOR_FAB/"
    "S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
)
LDO_VOUT_NOM = 3.3
LDO_ACCURACY_MAX = 0.015
SUP_VIT_MINUS_NOM = 3.0
SUP_THRESHOLD_ACCURACY_MAX = 0.015
SUP_HYST_MIN = 0.075
SUP_HYST_MAX = 0.125
SUP_VPOR_MAX = 0.300
SUP_VOL_MAX = 0.200
SUP_VOH_FRACTION_MIN = 0.8
LDO_EN_LOW = 0.300
LDO_EN_HIGH = 0.900
SUP_STARTUP_US_MAX = 350
SUP_FALL_PROPAGATION_US_MAX = 30

def ldo_output_envelope():
    """Valid only at V_IN >= V_OUT_nom+0.3 V and 1-300 mA / stated T range."""
    return (LDO_VOUT_NOM * (1-LDO_ACCURACY_MAX),
            LDO_VOUT_NOM * (1+LDO_ACCURACY_MAX))

def supervisor_trip_envelope():
    """VIT- (falling) tolerance and independent VHYS range, conservative."""
    low = SUP_VIT_MINUS_NOM * (1-SUP_THRESHOLD_ACCURACY_MAX)
    high = SUP_VIT_MINUS_NOM * (1+SUP_THRESHOLD_ACCURACY_MAX)
    return {"fall_min":low,"fall_max":high,
            "rise_min":low+SUP_HYST_MIN,"rise_max":high+SUP_HYST_MAX}

def input_logic_margin():
    rail_min,_ = ldo_output_envelope()
    tri = supervisor_trip_envelope()
    return {"release":rail_min-tri["rise_max"],
            "enable_high":SUP_VOH_FRACTION_MIN*rail_min-LDO_EN_HIGH,
            "disable_low":LDO_EN_LOW-SUP_VOL_MAX}

def output_state_safety(vdd, was_high=False):
    """Envelope of permissible RESET_N levels at a steady VDD.
    'unknown' is deliberate: cannot prove EN low below VPOR or in hysteresis.
    No claim on propagation delay, transient capacitance, load, or source current.
    """
    if vdd < 0:
        raise ValueError("VDD must be nonnegative")
    if vdd < SUP_VPOR_MAX:
        return "unknown"
    p=supervisor_trip_envelope()
    if vdd < p["fall_min"]:
        return "low"
    if vdd > p["rise_max"]:
        return "high_after_startup"
    return "unknown"

def schematic_evidence():
    s=SCHEMATIC.read_text(encoding="utf-8")
    u=s.index('(property "Reference" "U6207"')
    stop=s.index("(instances ",u)
    block=s[u:stop]
    assert '(property "Value" "TPS3840PL30DBVR"' in block
    assert '(property "MPN" "TPS3840PL30DBVR"' in block
    assert 'S3900E_TPS3840_DBV5_V735_HOLD:TI_DBV0005A_5PAD_REFLOW_REVIEW' in block
    assert '(label "CODEC_LDOIN_EN_SUPERVISED" (at 919.8400 415.0000 0)' in s
    assert '(label "CODEC_LDOIN_EN_SUPERVISED" (at 1020.1600 415.0000 0)' in s
    assert '(label "3V3_CODEC_IO" (at 999.8400 404.8400 0)' in s
    return True

class TestVendorBrownoutCorners(unittest.TestCase):
    def test_01_vendor_symbol_mpn_and_link(self):
        self.assertTrue(schematic_evidence())
    def test_02_3v3_ldo_steady_output_range(self):
        low,high=ldo_output_envelope()
        self.assertAlmostEqual(low,3.2505)
        self.assertAlmostEqual(high,3.3495)
    def test_03_supervisor_fall_threshold_worst(self):
        p=supervisor_trip_envelope()
        self.assertAlmostEqual(p["fall_min"],2.955)
        self.assertAlmostEqual(p["fall_max"],3.045)
    def test_04_supervisor_rising_threshold_worst(self):
        p=supervisor_trip_envelope()
        self.assertAlmostEqual(p["rise_min"],3.030)
        self.assertAlmostEqual(p["rise_max"],3.170)
    def test_05_latched_release_margin_is_positive_if_ldo_in_regulation(self):
        self.assertAlmostEqual(input_logic_margin()["release"],0.0805)
        self.assertGreater(input_logic_margin()["release"],0)
    def test_06_supervisor_high_above_ldo_enable_high(self):
        self.assertAlmostEqual(input_logic_margin()["enable_high"],1.7004)
        self.assertGreater(input_logic_margin()["enable_high"],0)
    def test_07_supervisor_low_below_ldo_enable_low(self):
        self.assertAlmostEqual(input_logic_margin()["disable_low"],0.100)
        self.assertGreater(input_logic_margin()["disable_low"],0)
    def test_08_supply_above_vit_plus_must_not_assert_in_static_model(self):
        self.assertEqual(output_state_safety(3.251),"high_after_startup")
    def test_09_supply_below_fall_min_and_above_vpor_is_asserted(self):
        self.assertEqual(output_state_safety(2.5),"low")
    def test_10_below_vpor_must_remain_unknown(self):
        for v in (0,0.1,0.299):
            self.assertEqual(output_state_safety(v),"unknown")
    def test_11_threshold_hysteresis_band_is_unknown(self):
        for v in (2.96,3.0,3.1,3.17):
            self.assertEqual(output_state_safety(v),"unknown")
    def test_12_no_inference_for_startup_transients(self):
        self.assertEqual(SUP_STARTUP_US_MAX,350)
        self.assertEqual(SUP_FALL_PROPAGATION_US_MAX,30)
        self.assertNotEqual(SUP_STARTUP_US_MAX,SUP_FALL_PROPAGATION_US_MAX)
    def test_13_zero_rail_does_not_imply_valid_reset_pin(self):
        self.assertNotEqual(output_state_safety(0),"low")
    def test_14_negative_voltage_fails_closed(self):
        with self.assertRaises(ValueError):
            output_state_safety(-0.001)
    def test_15_no_steady_state_claim_in_dropout(self):
        # The envelope only holds under V_IN >= VOUT_nom + 0.3V
        required_input=LDO_VOUT_NOM+0.3
        self.assertAlmostEqual(required_input,3.6)
        self.assertGreater(required_input,3.3)
    def test_16_no_blanket_logic_in_hysteretic_band(self):
        # A falling trip may occur before the nominal 3.0V threshold,
        # depending on actual silicon tolerance.
        self.assertEqual(output_state_safety(3.04),"unknown")

if __name__=="__main__":
    unittest.main()
