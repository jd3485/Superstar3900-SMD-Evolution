"""V7.18 guardrails for manufacturer-grounded eFuse dual-output pin-model ECO."""
import csv
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.18"))
from check_efuse_out_native_v718 import (BASE, NEW, OLD_POWER, NEW_POWER,
                                         EFUSE, AFTER, BEFORE, PIN15, ALL_CHILDREN, check_sources)
CSV=ROOT/"04_KiCad"/"Assemblaggio_RX_Power_V7.17_INTEGRATION_HOLD_NOT_FOR_FAB"/"MATRICE_INTERFACCE_PROPOSTE_V7_17_OPEN_HOLD.csv"

class TestEfuSemanticECO(unittest.TestCase):
    def test_01_only_pin16_semantic_type_changes(self):
        self.assertEqual(check_sources()["eFuse_out16_semantic_model"],"passive")

    def test_02_original_version_still_has_manufacturer_two_outputs(self):
        self.assertEqual((OLD_POWER/EFUSE).read_text().count(BEFORE),1)

    def test_03_candidate_pin16_modeled_one_passive(self):
        self.assertEqual((NEW_POWER/EFUSE).read_text().count(AFTER),1)

    def test_04_candidate_pin15_remains_one_power_driver(self):
        self.assertEqual((NEW_POWER/EFUSE).read_text().count(PIN15),1)

    def test_05_eFuse_footprint_and_pin_numbering_not_changed(self):
        a=(OLD_POWER/EFUSE).read_text()
        b=(NEW_POWER/EFUSE).read_text()
        self.assertEqual(a.replace(BEFORE,AFTER),b)
        for term in ["TPS26600PWPT", "Package_SO:TSSOP-16-1EP_4.4x5mm_P0.65mm",
                     '(number "15"', '(number "16"', 'EFUSE_RTN','GND_MAIN']:
            self.assertIn(term,b)

    def test_06_other_power_children_byte_identical(self):
        for name in ALL_CHILDREN[1:]:
            with self.subTest(name=name):
                self.assertEqual((OLD_POWER/name).read_bytes(),(NEW_POWER/name).read_bytes())

    def test_07_root_only_relinks_local_power_variant(self):
        a=BASE.read_text()
        b=NEW.read_text()
        self.assertIn("../Gerarchico_Alimentazioni_V1.5/",a)
        self.assertIn("../Gerarchico_Alimentazioni_V7.18_PINMODEL_NOT_FOR_FAB/",b)
        self.assertEqual(a.count('(property "Sheetfile"'),b.count('(property "Sheetfile"'))
        self.assertEqual(a.count('(wire (pts'),b.count('(wire (pts'))
        self.assertEqual(a.count('(pin "'),b.count('(pin "'))

    def test_08_all_15_interface_connections_still_open_hold(self):
        with CSV.open(newline="",encoding="utf-8") as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),15)
        self.assertTrue(all(r["physical_connection"]=="OPEN" and
                            r["qualification"]=="HOLD" and r["tx_permission"]=="0" for r in rows))

    def test_09_eFuse_rtn_not_short_to_main(self):
        s=(NEW_POWER/EFUSE).read_text()
        self.assertIn("EFUSE_RTN",s)
        self.assertIn("GND_MAIN",s)
        self.assertIn("devono rimanere separati",s)

    def test_10_tx_remains_unrealized(self):
        self.assertNotIn("(wire (pts",NEW.read_text())
        self.assertNotIn('(pin "',NEW.read_text())
        self.assertIn("NO FAB / NO TX",NEW.read_text())

    def test_11_eFuse_part_still_same_16pin_htssop(self):
        src=(NEW_POWER/EFUSE).read_text()
        self.assertIn("TPS26600_PWP",src)
        self.assertIn("TPS26600PWPT",src)

    def test_12_copper_source_not_part_of_eco(self):
        self.assertFalse(list((ROOT/"04_KiCad"/"Assemblaggio_RX_Power_V7.18_POWER_PINMODEL_NOT_FOR_FAB").glob("*.kicad_pcb")))

if __name__=="__main__":unittest.main()
