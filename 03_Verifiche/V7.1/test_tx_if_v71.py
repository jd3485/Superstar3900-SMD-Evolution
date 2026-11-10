"""Unit and repository-consistency tests, no RF hardware involved.
Run at repo root: python3 -m unittest discover -s 03_Verifiche/V7.1 -p 'test_*.py' -v
"""
import csv
from itertools import product
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "08_Firmware_Prototipi" / "V7.1"))
import tx_if_offline_v71 as tx


class TxIFV71(unittest.TestCase):
    def test_frequency_constants(self):
        self.assertEqual(tx.IF1_HZ, 10_695_000)
        self.assertEqual(tx.LO2_HZ - tx.IF2_HZ, 9_785_000)

    def test_sideband_inversion(self):
        center = 27_065_000
        self.assertEqual(tx.frequency_plan(center, "USB", 1000)["rf_difference_hz"], center + 1000)
        self.assertEqual(tx.frequency_plan(center, "LSB", 1000)["rf_difference_hz"], center - 1000)
        for mode in ("AM", "FM"):
            self.assertEqual(tx.frequency_plan(center, mode)["rf_difference_hz"], center)
        self.assertEqual(tx.frequency_plan(center, "CW")["rf_difference_hz"], center + 700)

    def test_both_upconversion_images(self):
        p = tx.frequency_plan(25_615_000, "AM")
        self.assertEqual(p["if1_wanted_hz"], 10_695_000)
        self.assertEqual(p["if1_unwanted_hz"], 9_785_000)
        self.assertEqual(p["rf_image_hz"], 47_005_000)
        self.assertEqual(tx.frequency_plan(28_305_000, "AM")["rf_image_hz"], 49_695_000)

    def test_invalid_modes_and_ranges(self):
        for bad in ("TX", "PA", "INVALID"):
            with self.assertRaises(ValueError):
                tx.frequency_plan(27_065_000, bad)
        with self.assertRaises(ValueError):
            tx.frequency_plan(29_000_000, "AM")
        with self.assertRaises(ValueError):
            tx.if2_frequency_for_tone("USB", 2800)

    def test_no_software_tx_path_all_controls(self):
        keys = ("ptt", "pa_mode", "fault_loop_ok", "pll_locked", "tx_arm", "bench_key")
        for state in product((False, True), repeat=len(keys)):
            self.assertIs(tx.rf_tx_permission(**dict(zip(keys, state))), False)
        self.assertIs(tx.TX_LO_LINK_FITTED, False)
        self.assertIs(tx.TX_MIXERS_FITTED, False)
        self.assertIs(tx.TX_RF_OUTPUT_LINK_FITTED, False)

    def test_offline_waveforms_only(self):
        self.assertAlmostEqual(tx.offline_if2_samples("AM", 1)[0], 1.35)
        self.assertEqual(tx.offline_if2_samples("CW", 32), [0.0] * 32)
        self.assertEqual(len(tx.offline_if2_samples("FM", 100)), 100)
        self.assertNotEqual(tx.offline_if2_samples("CW", 1, cw_key_down=True), [0.0])
        with self.assertRaises(ValueError):
            tx.offline_if2_samples("USB", 10, sample_rate_hz=48_000)

    def test_historic_270_channel_plan_if_present(self):
        path = ROOT / "02_Piano_Frequenze" / "V6.4" / "PIANO_PLL_LO_270_RX_V6.4.csv"
        if not path.is_file():
            self.skipTest("historic V6.4 plan not present in this partial checkout")
        with path.open(newline="", encoding="utf-8") as fh:
            records = list(csv.DictReader(fh))
        self.assertEqual(len(records), 270)
        self.assertEqual(sum(int(r["alfa"]) for r in records), 30)
        for r in records:
            f = int(r["rf_hz"])
            self.assertEqual(tx.frequency_plan(f, "AM")["lo1_candidate_hz"], int(r["lo_hz"]))
            self.assertEqual(tx.frequency_plan(f, "AM")["rf_image_hz"], int(r["if_image_hz"]))
            self.assertFalse(tx.frequency_plan(f, "AM")["tx_permitted"])
            self.assertEqual(int(r["tx_permitted_v64"]), 0)

    def test_dnp_bom_and_netlist_if_present(self):
        bom_path = ROOT / "07_Componenti" / "BOM_TX_IF_V7.1.csv"
        net_path = ROOT / "01_Specifiche" / "V7.1" / "NETLIST_PIN_TO_NET_TX_V7.1.csv"
        if not bom_path.is_file() or not net_path.is_file():
            self.skipTest("V7.1 BOM/netlist not in partial checkout")
        with bom_path.open(newline="", encoding="utf-8") as fh:
            bom = list(csv.DictReader(fh))
        self.assertTrue(bom)
        for row in bom:
            self.assertEqual(row["montaggio"], "DNP")
        with net_path.open(newline="", encoding="utf-8") as fh:
            pinrows = list(csv.DictReader(fh))
        for ref in ("U7201", "U7202"):
            pins = {int(r["pin"]) for r in pinrows if r["ref"] == ref}
            self.assertEqual(pins, {1, 2, 3, 4, 5, 6})
        self.assertTrue(all(r["montaggio"] == "DNP" for r in pinrows))


if __name__ == "__main__":
    unittest.main()
