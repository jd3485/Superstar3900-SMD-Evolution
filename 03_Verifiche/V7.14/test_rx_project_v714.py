"""Guard the V7.14 real KiCad 9 RX project (NOT RF hardware qualification)."""
import json,re,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[2]/"04_KiCad"
D=R/"Modulo_RX_Test_50ohm_V7.14_LIB_DIAGNOSTIC_NOT_FOR_FAB"
S="S3900E_RX_LIB_V7_14_NOT_FOR_FAB"
A=D/(S+".kicad_sch");B=D/(S+".kicad_pcb");P=D/(S+".kicad_pro")
O=R/"Modulo_RX_Test_50ohm_V7.13_GRID_NOT_FOR_FAB"/"S3900E_RX_GRID_V7_13_NOT_FOR_FAB.kicad_sch"
OB=R/"Modulo_RX_Test_50ohm_V7.12_SCHEMATIC_REPAIR_NOT_FOR_FAB"/"S3900E_RX_STANDALONE_V7_12_NOT_FOR_FAB.kicad_pcb"
ARC=R/"Modulo_RX_Test_50ohm_V5.2_PARITY_LINK_STUDY_NOT_FOR_FAB"

def refs(s):return re.findall(r'\(property "Reference" "([A-Za-z]+\d+)"',s)
class TestNativeKiCadRxV714(unittest.TestCase):
    def test_01_real_project_files(self):
        for f in (A,B,P):self.assertTrue(f.is_file())
        self.assertTrue(A.read_text().startswith("(kicad_sch "))
        self.assertTrue(B.read_text().startswith("(kicad_pcb "))
    def test_02_project_json_and_name(self):
        p=json.loads(P.read_text())
        self.assertEqual(p["meta"]["filename"],S+".kicad_pro")
        self.assertIn("schematic",p)
    def test_03_symbol_library_local_source_exact(self):
        s=(D/"sym-lib-table").read_text()
        self.assertIn('(name "S3900E")',s)
        self.assertIn("$"+"{KIPRJMOD}/S3900E.kicad_sym",s)
        self.assertEqual((D/"S3900E.kicad_sym").read_bytes(),
                         (ARC/"S3900E.kicad_sym").read_bytes())
    def test_04_footprints_reference_existing_previously_archived_libraries(self):
        s=(D/"fp-lib-table").read_text()
        for n in ("S3900E_V38_Review","S3900E_v33","S3900E_v35"):
            self.assertIn('(name "'+n+'")',s)
            self.assertTrue((ARC/(n+".pretty")).is_dir())
    def test_05_15_reference_names_untouched(self):
        self.assertEqual(refs(O.read_text()),refs(A.read_text()))
        self.assertEqual(len(refs(A.read_text())),15)
    def test_06_15_board_schematic_references_identical(self):
        self.assertEqual(sorted(refs(A.read_text())),sorted(refs(B.read_text())))
    def test_07_board_geometry_full_bytes_unchanged(self):
        self.assertEqual(B.read_bytes(),OB.read_bytes())
    def test_08_symbol_definitions_unchanged(self):
        def cached(s):return s[s.index("(lib_symbols "):s.index("(symbol (lib_id")]
        self.assertEqual(cached(O.read_text()),cached(A.read_text()))
    def test_09_electrical_schema_unchanged(self):
        prev=O.read_text().replace("S3900E_RX_GRID_V7_13_NOT_FOR_FAB",S)
        now=A.read_text().replace("V7.14 SYMBOL LIB DIAGNOSTIC — NO FAB / NO TX",
                                  "V7.13 GRID ALIGNED RX / NOT FOR FAB")
        self.assertEqual(prev,now)
    def test_10_no_real_tx_paths_or_production(self):
        nets=re.findall(r'(?m)^  \(net \d+ "([^"]*)"\)',B.read_text())
        self.assertFalse(any("TX_" in n for n in nets))
        self.assertIn("NOT_FOR_FAB",str(B))
    def test_11_cached_library_has_all_symbol_categories(self):
        s=(D/"S3900E.kicad_sym").read_text()
        for n in ("AMP","COAX_L","COAX_R","C_SER","C_SH","DC_2P","L_SH","R_SER","R_SH"):
            self.assertIn('(symbol "'+n+'"',s)
    def test_12_legacy_lib_footprints_present(self):
        for n in ("S3900E_V38_Review","S3900E_v33","S3900E_v35"):
            self.assertTrue(list((ARC/(n+".pretty")).glob("*.kicad_mod")))

class TestIntegratedSevenSheetRootV714(unittest.TestCase):
    def setUp(self):
        self.base=R/"Assemblaggio_RX_Power_V7.14_LIB_NOT_FOR_FAB"
        self.stem="S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB"
        self.sch=self.base/(self.stem+".kicad_sch")
        self.pro=self.base/(self.stem+".kicad_pro")
    def test_13_real_parent_project_contains_three_valid_child_sheets(self):
        self.assertTrue(self.sch.is_file() and self.pro.is_file())
        src=self.sch.read_text()
        links=re.findall(r'\(property "Sheetfile" "([^"]+)"',src)
        self.assertEqual(len(links),3)
        self.assertTrue(all((self.base/link).resolve().is_file() for link in links))
        self.assertTrue(any("V7.14_LIB_DIAGNOSTIC_NOT_FOR_FAB" in link for link in links))
    def test_14_parent_uses_same_local_archived_rx_libraries(self):
        self.assertIn('(name "S3900E")',(self.base/"sym-lib-table").read_text())
        f=(self.base/"fp-lib-table").read_text()
        for n in ("S3900E_V38_Review","S3900E_v33","S3900E_v35"):
            self.assertIn('(name "'+n+'")',f)
        self.assertEqual(json.loads(self.pro.read_text())["meta"]["filename"],
                         self.stem+".kicad_pro")
    def test_15_no_physical_crossmodule_connections_added(self):
        src=self.sch.read_text()
        self.assertNotIn("(wire (pts",src)
        self.assertNotIn("(global_label ",src)
        self.assertIn("NO FAB / NO TX",src)
        manifest=R/"Assemblaggio_RX_Power_V7.10_NOT_FOR_FAB"/"MATRICE_INTERFACCE_DA_QUALIFICARE_V7_10.csv"
        import csv
        with manifest.open(newline="",encoding="utf-8") as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),15)
        self.assertTrue(all(row["physical_connection"]=="OPEN"
                            and row["qualification"]=="HOLD"
                            and row["tx_permission"]=="0" for row in rows))

if __name__=="__main__":unittest.main()
