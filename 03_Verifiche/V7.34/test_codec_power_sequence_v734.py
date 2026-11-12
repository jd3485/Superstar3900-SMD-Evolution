"""V7.34 TI SLAA492A nominal startup checks; not hardware or native KiCad validation."""
import math
import unittest

R_WEAK_OHM = 10_000.0
C_AVDD_BULK_F = 10e-6
C_AVDD_LOCAL_F = 100e-9
IOVDD_NOMINAL_V = 3.3
R_LDO_SELECT_OHM = 4_700
R_RESET_OHM = 47_000
TI_POST_RESET_MIN_S = 0.001


def weak_charge_5tau_seconds(r_ohm, cap_f):
    if r_ohm <= 0 or cap_f <= 0:
        raise ValueError('R and C must be positive')
    return 5.0 * r_ohm * cap_f


def input_thresholds(iovdd_volts):
    """Datasheet 7.11 for 1.6V < IOVDD, nominal threshold test, not measured."""
    if not 1.6 < iovdd_volts <= 3.6:
        raise ValueError('Regime is restricted to IOVDD > 1.6V and <= 3.6V')
    return 0.7 * iovdd_volts, 0.3 * iovdd_volts


class TestCodecPowerSequence(unittest.TestCase):
    def test_01_approx_nominal_avdd_charge_not_real_startup(self):
        self.assertAlmostEqual(weak_charge_5tau_seconds(R_WEAK_OHM, C_AVDD_BULK_F+C_AVDD_LOCAL_F), .505)
        self.assertAlmostEqual(weak_charge_5tau_seconds(R_WEAK_OHM, 1.1e-6), .055)

    def test_02_3v3_logic_thresholds_from_ti(self):
        vih,vil=input_thresholds(IOVDD_NOMINAL_V)
        self.assertAlmostEqual(vih, 2.31)
        self.assertAlmostEqual(vil, 0.99)

    def test_03_explicit_post_reset_write_gate(self):
        self.assertGreaterEqual(TI_POST_RESET_MIN_S, 0.001)
        # A host must check supplies and defer register access after reset.
        # The 505 ms RC estimate is not the minimum reset delay.
        self.assertGreater(weak_charge_5tau_seconds(R_WEAK_OHM,10.1e-6),TI_POST_RESET_MIN_S)

    def test_04_bias_values_are_nominal_not_guaranteed_logic(self):
        self.assertEqual(R_LDO_SELECT_OHM, 4700)
        self.assertEqual(R_RESET_OHM, 47000)
        # TI logic table conditions mention 5uA; here this is a hypothetical ONLY.
        hypothetical_current = 5e-6
        self.assertAlmostEqual(hypothetical_current * R_LDO_SELECT_OHM, .0235)
        self.assertAlmostEqual(hypothetical_current * R_RESET_OHM, .235)

    def test_05_fail_closed_on_invalid_ranges(self):
        with self.assertRaises(ValueError):
            weak_charge_5tau_seconds(0, 10e-6)
        with self.assertRaises(ValueError):
            input_thresholds(1.5)

if __name__ == '__main__':
    unittest.main()
