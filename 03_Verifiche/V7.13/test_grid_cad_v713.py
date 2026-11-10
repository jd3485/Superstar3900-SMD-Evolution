"""V7.13 source invariants supplement (not replace) native KiCad ERC/netlist."""
import re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
K=ROOT/"04_KiCad"
V12=K/"Modulo_RX_Test_50ohm_V7.12_SCHEMATIC_REPAIR_NOT_FOR_FAB"/"S3900E_RX_STANDALONE_V7_12_NOT_FOR_FAB.kicad_sch"
V13=K/"Modulo_RX_Test_50ohm_V7.13_GRID_NOT_FOR_FAB"/"S3900E_RX_GRID_V7_13_NOT_FOR_FAB.kicad_sch"
PCB=K/"Modulo_RX_Test_50ohm_V7.12_SCHEMATIC_REPAIR_NOT_FOR_FAB"/"S3900E_RX_STANDALONE_V7_12_NOT_FOR_FAB.kicad_pcb"
ROOT13=K/"Assemblaggio_RX_Power_V7.13_GRID_NOT_FOR_FAB"/"S3900E_RX_POWER_V7_13_GRID_NOT_FOR_FAB.kicad_sch"
SYM=re.compile(r'\(symbol \(lib_id "[^"]+"\) \(at ([\d.]+) ([\d.]+) (\d+)\)')
WIRE=re.compile(r'\(wire \(pts \(xy ([\d.]+) ([\d.]+)\) \(xy ([\d.]+) ([\d.]+)\)\)')
LABEL=re.compile(r'\(label "([^"]+)" \(at ([\d.]+) ([\d.]+) (\d+)\)')
REF=re.compile(r'\(property "Reference" "([A-Za-z]+\d+)"')
GRID=1.27
def snap(s):
    return f"{round(float(s)/GRID)*GRID:.3f}"
def collection(text):
    return list(SYM.finditer(text)),list(WIRE.finditer(text)),list(LABEL.finditer(text))
class V713(unittest.TestCase):
    def test_01_legitimate_versioned_native_files_exist(self):
        for p in (V12,V13,PCB,ROOT13):
            self.assertTrue(p.is_file(),p)
        self.assertTrue(V13.read_text().startswith("(kicad_sch "))
        self.assertIn("NOT_FOR_FAB",str(V13))
    def test_02_15_31_31_original_elements_preserved(self):
        old=collection(V12.read_text()); new=collection(V13.read_text())
        self.assertEqual([len(x) for x in old],[15,31,31])
        self.assertEqual([len(x) for x in new],[15,31,31])
    def test_03_all_coordinates_exact_grid(self):
        symbols,wires,labels=collection(V13.read_text())
        coords=[(m.group(1),m.group(2)) for m in symbols]
        coords += [(m.group(2),m.group(3)) for m in labels]
        for m in wires:coords.extend([(m.group(1),m.group(2)),(m.group(3),m.group(4))])
        for x,y in coords:
            self.assertAlmostEqual(float(x)/GRID,round(float(x)/GRID),places=6)
            self.assertAlmostEqual(float(y)/GRID,round(float(y)/GRID),places=6)
    def test_04_every_symbol_moved_only_to_nearest_grid(self):
        old,new=collection(V12.read_text())[0],collection(V13.read_text())[0]
        for a,b in zip(old,new):
            self.assertEqual((snap(a.group(1)),snap(a.group(2)),a.group(3)),
                             (b.group(1),b.group(2),b.group(3)))
    def test_05_wire_and_labels_snap_without_element_merging(self):
        old=collection(V12.read_text());new=collection(V13.read_text())
        for a,b in zip(old[1],new[1]):
            self.assertEqual(tuple(snap(a.group(i)) for i in range(1,5)),b.groups())
        for a,b in zip(old[2],new[2]):
            self.assertEqual(a.group(1),b.group(1))
            self.assertEqual(tuple(snap(a.group(i)) for i in (2,3)),
                             tuple(b.group(i) for i in (2,3)))
    def test_06_same_15_physical_refs_as_V712_PCB(self):
        old=set(REF.findall(V12.read_text()))
        new=set(REF.findall(V13.read_text()))
        pcb=set(REF.findall(PCB.read_text()))
        self.assertEqual(len(old),15)
        self.assertEqual(old,new)
        self.assertEqual(new,pcb)
    def test_07_cached_pin_geometry_on_grid(self):
        s=V13.read_text()
        pins=re.findall(r'\(pin (?:passive|input|output|power_in|power_out|bidirectional|no_connect) line \(at ([-\d.]+) ([-\d.]+) \d+\)',s)
        self.assertGreaterEqual(len(pins),19)
        for xy in pins:
            self.assertTrue(all(abs(float(x)/GRID-round(float(x)/GRID))<1e-7 for x in xy))
    def test_08_root_references_grid_RX_not_predecessor(self):
        root=ROOT13.read_text()
        self.assertIn("../Modulo_RX_Test_50ohm_V7.13_GRID_NOT_FOR_FAB/S3900E_RX_GRID_V7_13_NOT_FOR_FAB.kicad_sch",root)
        self.assertIn("../Modulo_MCU_CODEC_V7.12_REANNOTATED_NOT_FOR_FAB/",root)
        self.assertIn("../Gerarchico_Alimentazioni_V1.5/",root)
        self.assertNotIn('(wire (pts',root)
    def test_09_project_local_vendor_unqualified_libraries_explicit(self):
        parent=V13.parent
        for table in ("sym-lib-table","fp-lib-table"):
            self.assertTrue((parent/table).is_file())
        sym=(parent/"sym-lib-table").read_text()
        self.assertIn('name "S3900E"',sym)
        self.assertIn("NOT FOR FAB",sym)
        fplib=(parent/"fp-lib-table").read_text()
        for name in ("S3900E_v33","S3900E_v35","S3900E_V38_Review"):
            self.assertIn(name,fplib)
            self.assertTrue((parent/"../Modulo_RX_Test_50ohm_V5.2_PARITY_LINK_STUDY_NOT_FOR_FAB"/(name+".pretty")).is_dir())
    def test_10_no_tx_and_no_fab(self):
        self.assertNotIn('(wire (pts',ROOT13.read_text())
        self.assertFalse(any("TX_" in name for name,_,_,_ in LABEL.findall(V13.read_text())))
        self.assertTrue((V13.parent/"sym-lib-table").read_text().find("NOT FOR FAB")>=0)

if __name__=="__main__":unittest.main()
