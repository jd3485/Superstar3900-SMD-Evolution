"""Static source-preservation guards; KiCad CLI separately proves exported nets."""
import re
import csv
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
K=ROOT/"04_KiCad"
ORIG_RX=K/"Modulo_RX_Test_50ohm_V5.2_PARITY_LINK_STUDY_NOT_FOR_FAB"/"S3900E_RX_TEST_50R_V5_2_LINKED_STUDY_NOT_FOR_FAB.kicad_sch"
ORIG_MCU=K/"Modulo_MCU_CODEC_V2.1"/"S3900E_MCU_CODEC_AFE_V2_1_DRAFT.kicad_sch"
ORIG_PCB=K/"Modulo_RX_Test_50ohm_V7.11_DRC_REPAIR_NOT_FOR_FAB"/"S3900E_RX_TEST_50R_V7_11_DRILL_LIBRARY_REPAIR_NOT_FOR_FAB.kicad_pcb"
NEW_RX=K/"Modulo_RX_Test_50ohm_V7.12_SCHEMATIC_REPAIR_NOT_FOR_FAB"/"S3900E_RX_STANDALONE_V7_12_NOT_FOR_FAB.kicad_sch"
NEW_MCU=K/"Modulo_MCU_CODEC_V7.12_REANNOTATED_NOT_FOR_FAB"/"S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
NEW_PCB=NEW_RX.with_suffix(".kicad_pcb")
NEW_TOP=K/"Assemblaggio_RX_Power_V7.12_REANNOTATED_NOT_FOR_FAB"/"S3900E_RX_POWER_INTEGRATION_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
ORIG_TOP=K/"Assemblaggio_RX_Power_V7.10_NOT_FOR_FAB"/"S3900E_RX_POWER_INTEGRATION_V7_10_NOT_FOR_FAB.kicad_sch"

def refs(text):
    return re.findall(r'\(property "Reference" "([A-Za-z]+\d+)"',text)

def map_to_range(text, offset):
    return [re.sub(r'\d+$',lambda m:str(int(m.group())+offset),a) for a in refs(text)]

class NativeCadV712(unittest.TestCase):
    def test_01_versioned_native_schematic_and_pcb_exist(self):
        for p in (NEW_RX,NEW_MCU,NEW_PCB,NEW_TOP):
            self.assertTrue(p.is_file())
            self.assertIn("NOT_FOR_FAB",str(p))
            self.assertGreater(p.stat().st_size,2500 if p==NEW_TOP else 5000)
    def test_02_mcu_exact_46_reference_transform(self):
        self.assertEqual(len(refs(ORIG_MCU.read_text())),46)
        self.assertEqual(refs(NEW_MCU.read_text()),map_to_range(ORIG_MCU.read_text(),6000))
    def test_03_rx_exact_15_reference_transform(self):
        self.assertEqual(len(refs(ORIG_RX.read_text())),15)
        self.assertEqual(refs(NEW_RX.read_text()),map_to_range(ORIG_RX.read_text(),9000))
    def test_04_rx_schematic_matches_physical_board_15_refs(self):
        rx=set(refs(NEW_RX.read_text()))
        board=set(refs(NEW_PCB.read_text()))
        self.assertEqual(len(rx),15)
        self.assertEqual(rx,board)
    def test_05_rx_board_keeps_same_8_nonzero_nets(self):
        old=ORIG_PCB.read_text()
        new=NEW_PCB.read_text()
        nets=r'(?m)^  \(net \d+ "[^"]*"\)'
        self.assertEqual(re.findall(nets,old),re.findall(nets,new))
        self.assertFalse(any("TX_" in a for a in re.findall(nets,new)))
    def test_06_v711_corrected_drills_retained(self):
        old=ORIG_PCB.read_text();new=NEW_PCB.read_text()
        vias=r'\(via \(at ([\d.]+) ([\d.]+)\) \(size ([\d.]+)\) \(drill ([\d.]+)\)'
        self.assertEqual(re.findall(vias,old),re.findall(vias,new))
        self.assertIn('(drill 0.30)',new)
    def test_07_root_correct_links_and_no_circuit_interconnections(self):
        s=NEW_TOP.read_text()
        for p in (NEW_RX,NEW_MCU):
            relative="../"+p.parent.name+"/"+p.name
            self.assertIn(relative,s)
            self.assertTrue((NEW_TOP.parent/relative).resolve().is_file())
        self.assertEqual(s.count('(property "Sheetfile"'),3)
        self.assertNotIn('(wire (pts',s)
        self.assertNotIn('(global_label "',s)
    def test_08_cross_module_reference_spaces_disjoint(self):
        power=K/"Gerarchico_Alimentazioni_V1.5"
        powerfiles=[power/"S3900E_AUX_POWER_V1_5.kicad_sch"]+list(power.glob("0*.kicad_sch"))
        p_refs={x for path in powerfiles for x in refs(path.read_text())}
        m_refs=set(refs(NEW_MCU.read_text()))
        r_refs=set(refs(NEW_RX.read_text()))
        self.assertFalse(p_refs & m_refs)
        self.assertFalse(p_refs & r_refs)
        self.assertFalse(m_refs & r_refs)
    def test_09_tx_gates_unchanged_and_interfaces_open(self):
        manifest=K/"Assemblaggio_RX_Power_V7.10_NOT_FOR_FAB"/"MATRICE_INTERFACCE_DA_QUALIFICARE_V7_10.csv"
        with manifest.open(newline="",encoding="utf-8") as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),15)
        self.assertTrue(all(a["physical_connection"]=="OPEN" and a["qualification"]=="HOLD" and a["tx_permission"]=="0" for a in rows))
    def test_10_original_sources_preserved(self):
        self.assertIn("V2.0 DRAFT",ORIG_MCU.read_text())
        self.assertIn("V4.5 LIB PORTABLE STUDY",ORIG_RX.read_text())
        self.assertIn("V7.10 - ISOLATED SHEETS",ORIG_TOP.read_text())
    def test_11_project_symbol_instance_annotation_updated(self):
        for p in (NEW_MCU, NEW_RX):
            s=p.read_text()
            a=re.findall(r'\(property "Reference" "([A-Za-z]+\d+)"',s)
            b=re.findall(r'\(reference "([A-Za-z]+\d+)"\)',s)
            self.assertEqual(sorted(a),sorted(b))
    def test_12_no_native_qualification_claimed(self):
        self.assertNotIn("(wire (pts",NEW_TOP.read_text())
        self.assertNotIn("(global_label ",NEW_TOP.read_text())
        self.assertNotIn("TX_",",".join(refs(NEW_RX.read_text())))

if __name__=="__main__":
    unittest.main()
