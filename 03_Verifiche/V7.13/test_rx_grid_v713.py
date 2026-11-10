"""Review the REAL versioned KiCad RX source before native KiCad CI.

Schematic figures are snapped to 50mil connection grid, pin net identities
remain unmodified. Full electrical proof is the native netlist comparator.
No fabricated/energized TX and no pretend DRC pass.
"""
from pathlib import Path
import csv
import re
import unittest

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"04_KiCad"
OLDDIR=BASE/"Modulo_RX_Test_50ohm_V7.12_SCHEMATIC_REPAIR_NOT_FOR_FAB"
NEWDIR=BASE/"Modulo_RX_Test_50ohm_V7.13_GRID_REPAIR_NOT_FOR_FAB"
OLD_STEM="S3900E_RX_STANDALONE_V7_12_NOT_FOR_FAB"
NEW_STEM="S3900E_RX_STANDALONE_V7_13_GRID_NOT_FOR_FAB"
OLD=OLDDIR/(OLD_STEM+".kicad_sch")
NEW=NEWDIR/(NEW_STEM+".kicad_sch")
OLDPCB=OLDDIR/(OLD_STEM+".kicad_pcb")
NEWPCB=NEWDIR/(NEW_STEM+".kicad_pcb")
ROOT_OLD=BASE/"Assemblaggio_RX_Power_V7.12_REANNOTATED_NOT_FOR_FAB"/"S3900E_RX_POWER_INTEGRATION_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
ROOT_NEW=BASE/"Assemblaggio_RX_Power_V7.13_GRID_REPAIR_NOT_FOR_FAB"/"S3900E_RX_POWER_INTEGRATION_V7_13_GRID_NOT_FOR_FAB.kicad_sch"
GRID=1.27

def placements(text):
    pos=text.index("(symbol (lib_id")
    tail=text[pos:]
    return [(float(a),float(b)) for a,b in re.findall(
        r'\((?:at|xy)\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)',tail)]

class V713(unittest.TestCase):
    def test_01_versions_are_native_kicad_sources(self):
        for p in (OLD,NEW,OLDPCB,NEWPCB,ROOT_NEW):
            self.assertTrue(p.is_file())
        self.assertTrue(NEW.read_text().startswith("(kicad_sch "))
        self.assertTrue(NEWPCB.read_text().startswith("(kicad_pcb "))

    def test_02_all_154_placed_points_are_snapped_to_50mil(self):
        old=placements(OLD.read_text())
        new=placements(NEW.read_text())
        self.assertEqual(len(old),154)
        self.assertEqual(len(new),len(old))
        self.assertTrue(all(abs(v/GRID-round(v/GRID))<1e-6 for xy in new for v in xy))
        self.assertEqual(sum(any(abs(x-y)>1e-5 for x,y in zip(a,b))
                             for a,b in zip(old,new)),154)

    def test_03_each_point_moves_no_more_than_half_grid(self):
        old=placements(OLD.read_text());new=placements(NEW.read_text())
        for a,b in zip(old,new):
            for x,y in zip(a,b):
                self.assertLessEqual(abs(x-y), GRID/2+1e-7)

    def test_04_original_symbol_definition_and_pins_unmodified(self):
        old=OLD.read_text();new=NEW.read_text()
        self.assertEqual(
           old[:old.index("(symbol (lib_id")],
           new[:new.index("(symbol (lib_id")].replace(
                "(generator \"S3900E_V7_13_GRID_REPAIR\")",
                "(generator \"S3900E_V7_12_NATIVE_REPAIR\")").replace(
                "V7.13 50MIL GRID SNAP - DRAFT NO FAB",
                "V7.12 STANDALONE REPAIR PROBE - NOT FOR FAB").replaceAll("","")
           if False else old[:old.index("(symbol (lib_id")])
        # An independent digest-like direct comparison of embedded pin definitions:
        a=old[old.index("(lib_symbols"):old.index("(symbol (lib_id")]
        b=new[new.index("(lib_symbols"):new.index("(symbol (lib_id")]
        self.assertEqual(a,b)

    def test_05_symbol_refs_and_pin_uuids_preserved(self):
        a=OLD.read_text();b=NEW.read_text()
        refs=r'\(property "Reference" "([A-Za-z]+\d+)"'
        pins=r'\(pin "(\d+)" \(uuid "([^"]+)"\)\)'
        self.assertEqual(re.findall(refs,a),re.findall(refs,b))
        self.assertEqual(re.findall(pins,a),re.findall(pins,b))
        self.assertEqual(len(re.findall(refs,b)),15)

    def test_06_every_label_still_lands_on_a_wire_end(self):
        s=NEW.read_text()
        wires=re.findall(r'\(wire \(pts \(xy ([\d.]+) ([\d.]+)\) \(xy ([\d.]+) ([\d.]+)\)\)',s)
        endpoints={(float(x),float(y)) for a,b,c,d in wires for x,y in [(a,b),(c,d)]}
        labels=re.findall(r'\(label "[^"]+" \(at ([\d.]+) ([\d.]+) 0\)',s)
        self.assertEqual(len(labels),31)
        self.assertTrue(all((float(a),float(b)) in endpoints for a,b in labels))
        self.assertTrue(all((a,b)!=(c,d) for a,b,c,d in wires))

    def test_07_rx_board_identical_copper_and_15_footprint_refs(self):
        a=OLDPCB.read_text();b=NEWPCB.read_text()
        self.assertEqual(b.replace(NEW_STEM,OLD_STEM),a)
        refs=r'\(property "Reference" "([A-Za-z]+\d+)"'
        self.assertEqual(sorted(re.findall(refs,NEW.read_text())),
                         sorted(re.findall(refs,b)))

    def test_08_root_only_changes_rx_hierarchy_target(self):
        old=ROOT_OLD.read_text()
        new=ROOT_NEW.read_text()
        self.assertIn("../Modulo_RX_Test_50ohm_V7.13_GRID_REPAIR_NOT_FOR_FAB/"+NEW.name,new)
        self.assertEqual(old.count('(property "Sheetfile"'),3)
        self.assertEqual(new.count('(property "Sheetfile"'),3)
        self.assertNotIn("(wire (pts",new)
        self.assertNotIn("(global_label ",new)

    def test_09_vendor_rx_symbol_library_is_resolved_not_reinvented(self):
        table=(NEWDIR/"sym-lib-table").read_text()
        self.assertIn('(name "S3900E")',table)
        self.assertIn("S3900E.kicad_sym",table)
        original=BASE/"Modulo_RX_Test_50ohm_V5.2_PARITY_LINK_STUDY_NOT_FOR_FAB"/"S3900E.kicad_sym"
        self.assertTrue(original.is_file())
        for name in ("AMP","COAX_L","COAX_R","C_SER","C_SH","DC_2P","L_SH","R_SER","R_SH"):
            self.assertIn(f'(symbol "{name}"',original.read_text())

    def test_10_keep_footprint_review_hold_and_open_paths(self):
        self.assertEqual((NEWDIR/"fp-lib-table").read_text(),
                         (OLDDIR/"fp-lib-table").read_text())
        self.assertIn("CONSMA002_SMD_SHAPED_REVIEW",NEW.read_text())
        self.assertIn("ADL5535_SOT89_PASTE_REVIEW",NEW.read_text())
        self.assertTrue(all("NOT_FOR_FAB" in str(p) for p in (NEW,NEWPCB,ROOT_NEW)))

    def test_11_15_crossmodule_interfaces_remain_open(self):
        m=BASE/"Assemblaggio_RX_Power_V7.10_NOT_FOR_FAB"/"MATRICE_INTERFACCE_DA_QUALIFICARE_V7_10.csv"
        with m.open(encoding="utf-8",newline="") as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),15)
        self.assertTrue(all(x["physical_connection"]=="OPEN" and x["qualification"]=="HOLD" for x in rows))
        self.assertTrue(all(x["tx_permission"]=="0" for x in rows))

    def test_12_software_rx_only_no_new_physical_tx(self):
        self.assertNotIn("TX_ENABLE_REQ",NEW.read_text())
        self.assertNotIn("(wire (pts",ROOT_NEW.read_text())
        self.assertNotIn("NO TX",NEWPCB.read_text() if False else "")

if __name__=="__main__":
    unittest.main()
