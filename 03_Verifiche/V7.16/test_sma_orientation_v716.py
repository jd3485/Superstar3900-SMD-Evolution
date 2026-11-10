"""V7.16 guard: SMA 180-degree placement is mechanical, not a DRC workaround."""
import math
import re
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.15"))
from audit_rx_topologia_v715 import PCB,LIB,forms,footprint_refs,pad_signatures
V716=ROOT/"03_Verifiche"/"V7.16"
PREV=(ROOT/"04_KiCad"/"Modulo_RX_Test_50ohm_V7.12_SCHEMATIC_REPAIR_NOT_FOR_FAB"
      /"S3900E_RX_STANDALONE_V7_12_NOT_FOR_FAB.kicad_pcb")
OUTER={"J9101":(28,36,0),"J9102":(122,36,180),
       "J9103":(28,65,0),"J9104":(122,65,180)}

def local_courtyard(fp):
    # SMD SMA library has two perimeter rectangles; F.CrtYd is the authoritative
    # electronic courtyard. This does NOT qualify vendor 3D extrusion or assembly.
    m=re.search(r'\(fp_rect \(start ([-\d.]+) ([-\d.]+)\) \(end ([-\d.]+) ([-\d.]+)\).*?\(layer "F.CrtYd"\)',fp,re.S)
    if not m: raise AssertionError("SMA courtyard not parsed")
    return tuple(float(x) for x in m.groups())

def x_limits_after_footprint_rotation(fp):
    m=re.search(r'\(footprint "[^"]+" \(layer "[^"]+"\).*?\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)',fp)
    if not m: raise AssertionError("SMA position missing")
    x=float(m[1]);angle=float(m[3] or 0)
    x1,_,x2,_=local_courtyard(fp)
    # These source instances use exclusively 0 and 180 degree orientations.
    if angle==0: return (x+x1,x+x2)
    if angle==180: return (x-x2,x-x1)
    raise AssertionError("unexpected SMA orientation")

class TestV716SMAOrientation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src=PCB.read_text(encoding="utf-8")
        cls.fps=footprint_refs(cls.src)

    def test_01_pcb_original_byte_preserved(self):
        self.assertEqual(PCB.read_bytes(),PREV.read_bytes())

    def test_02_no_source_V716_kicad_pcb_modification(self):
        self.assertNotIn("V7.16_",PCB.as_posix())
        self.assertEqual(len(forms(self.src,"via")),70)
        self.assertEqual(len(forms(self.src,"segment")),44)

    def test_03_sma_reference_inventory(self):
        self.assertTrue(set(OUTER).issubset(self.fps))

    def test_04_sma_rotation_intent(self):
        for ref,(x,y,ang) in OUTER.items():
            with self.subTest(ref=ref):
                m=re.search(r'\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\)',self.fps[ref])
                self.assertEqual((float(m[1]),float(m[2]),float(m[3] or 0)),(x,y,ang))

    def test_05_courtyard_overhangs_pcb_both_outer_edges(self):
        for ref in ("J9101","J9103"):
            left,right=x_limits_after_footprint_rotation(self.fps[ref])
            self.assertAlmostEqual(20-left,7.2,places=4)
            self.assertLess(right,130)
        for ref in ("J9102","J9104"):
            left,right=x_limits_after_footprint_rotation(self.fps[ref])
            self.assertAlmostEqual(right-130,7.2,places=4)
            self.assertGreater(left,20)

    def test_06_rotation_zero_candidate_would_point_RIGHT_sma_inwards(self):
        for ref in ("J9102","J9104"):
            f=self.fps[ref]
            hypothetical=f.replace("(at 122 "+("36" if ref=="J9102" else "65")+" 180)",
                                   "(at 122 "+("36" if ref=="J9102" else "65")+")",1)
            self.assertNotEqual(hypothetical,f)
            a,b=x_limits_after_footprint_rotation(hypothetical)
            self.assertGreater(a,20)
            self.assertLess(b,130)

    def test_07_custom_pad_local_geometry_unchanged_for_all_sma(self):
        expected=pad_signatures(LIB.read_text())
        for ref in OUTER:
            self.assertEqual(pad_signatures(self.fps[ref]),expected)

    def test_08_center_contact_and_four_ground_pads_per_sma(self):
        for ref in OUTER:
            pads=forms(self.fps[ref],"pad")
            self.assertEqual(len(pads),5)
            self.assertEqual(sorted(re.match(r'\(pad "([^"]+)"',p)[1] for p in pads),["1","2","2","2","2"])
            self.assertTrue(all('(net 1 "GND_RF")' in p for p in pads[1:]))

    def test_09_footprint_library_is_candidate_not_vendor_qualification(self):
        self.assertEqual(len(forms(LIB.read_text(),"pad")),5)
        self.assertIn("SHAPED_REVIEW",str(LIB))
        self.assertIn("NOT_FOR_FAB",str(PCB))

    def test_10_tx_stays_absent_and_15_interfaces_open(self):
        import csv
        matrix=ROOT/"04_KiCad"/"Assemblaggio_RX_Power_V7.10_NOT_FOR_FAB"/"MATRICE_INTERFACCE_DA_QUALIFICARE_V7_10.csv"
        with matrix.open(newline="",encoding="utf-8") as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),15)
        self.assertTrue(all(r["physical_connection"]=="OPEN" and r["qualification"]=="HOLD"
                            and r["tx_permission"]=="0" for r in rows))

if __name__=="__main__":unittest.main()
