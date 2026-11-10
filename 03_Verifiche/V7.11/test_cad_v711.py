"""Static preflight for source-controlled KiCad V7.11 RX coupon repair.

The real KiCad 9 DRC is run separately in GitHub Actions and must NOT be
represented as passed by these Python source tests alone.
"""
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/"04_KiCad"/"Modulo_RX_Test_50ohm_V5.2_PARITY_LINK_STUDY_NOT_FOR_FAB"/"S3900E_RX_TEST_50R_V5_2_LINKED_STUDY_NOT_FOR_FAB.kicad_pcb"
DIR=ROOT/"04_KiCad"/"Modulo_RX_Test_50ohm_V7.11_DRC_REPAIR_NOT_FOR_FAB"
NEW=DIR/"S3900E_RX_TEST_50R_V7_11_DRILL_LIBRARY_REPAIR_NOT_FOR_FAB.kicad_pcb"
LIB=DIR/"fp-lib-table"
COORDS={("67.640","32.500"),("68.360","32.500"),("67.640","33.650"),
        ("68.360","33.650"),("67.640","34.800"),("68.360","34.800")}
VIA=r'\(via \(at ([0-9.]+) ([0-9.]+)\) \(size ([0-9.]+)\) \(drill ([0-9.]+)\)'

def read_vias(text):
    return {(a,b):(float(sz),float(drill)) for a,b,sz,drill in re.findall(VIA,text)}

class CadV711(unittest.TestCase):
    def test_01_real_kicad_native_board_files(self):
        self.assertTrue(OLD.exists() and NEW.exists())
        self.assertTrue(OLD.read_text().startswith("(kicad_pcb "))
        self.assertTrue(NEW.read_text().startswith("(kicad_pcb "))
        self.assertIn("NOT_FOR_FAB",str(NEW))

    def test_02_exact_six_undersized_drills_fixed(self):
        old=read_vias(OLD.read_text())
        new=read_vias(NEW.read_text())
        self.assertEqual(set(old),set(new))
        self.assertEqual(len(old),70)
        changed={k for k in old if old[k]!=new[k]}
        self.assertEqual(changed,COORDS)
        self.assertEqual({old[k] for k in changed},{(.55,.25)})
        self.assertEqual({new[k] for k in changed},{(.60,.30)})

    def test_03_no_other_board_via_changed(self):
        old=read_vias(OLD.read_text());new=read_vias(NEW.read_text())
        self.assertEqual({k:v for k,v in old.items() if k not in COORDS},
                         {k:v for k,v in new.items() if k not in COORDS})

    def test_04_netlist_and_component_inventory_unchanged(self):
        old=OLD.read_text();new=NEW.read_text()
        self.assertEqual(re.findall(r'(?m)^  \(net \d+ "[^"]*"\)',old),
                         re.findall(r'(?m)^  \(net \d+ "[^"]*"\)',new))
        self.assertEqual(re.findall(r'\(footprint "[^"]+"',old),
                         re.findall(r'\(footprint "[^"]+"',new))
        self.assertEqual(re.findall(r'\(property "Reference" "[^"]+"',old),
                         re.findall(r'\(property "Reference" "[^"]+"',new))

    def test_05_local_library_links_to_repository_sources(self):
        text=LIB.read_text()
        self.assertTrue(text.startswith("(fp_lib_table"))
        for nickname in ("S3900E_V38_Review","S3900E_v33","S3900E_v35"):
            self.assertIn(f'(name "{nickname}")',text)
            path=ROOT/"04_KiCad"/"Modulo_RX_Test_50ohm_V5.2_PARITY_LINK_STUDY_NOT_FOR_FAB"/(nickname+".pretty")
            self.assertTrue(path.is_dir(),str(path))
            self.assertTrue(list(path.glob("*.kicad_mod")))

    def test_06_safety_no_physical_tx(self):
        old=OLD.read_text();new=NEW.read_text()
        old_nets=re.findall(r'(?m)^  \(net \d+ "([^"]*)"\)',old)
        new_nets=re.findall(r'(?m)^  \(net \d+ "([^"]*)"\)',new)
        self.assertEqual(old_nets,new_nets)
        self.assertFalse(any("TX_" in name for name in new_nets))
        self.assertIn("NO FAB",new)

    def test_07_legacy_design_unchanged(self):
        self.assertIn("V3.8 CUSTOM PAD",OLD.read_text())
        self.assertIn("V7.11 DRILL",NEW.read_text())

    def test_08_drc_comparison_requires_native_outputs(self):
        x=(ROOT/"03_Verifiche"/"V7.11"/"confronta_drc_rx_v711.py").read_text()
        self.assertIn("rx_v52_legacy_drc.rpt",x)
        self.assertIn("rx_v711_repaired_drc.rpt",x)
        self.assertIn("changed_drill!=0",x)
        self.assertIn("board_fabrication_authorized",x)

if __name__=="__main__":
    unittest.main()
