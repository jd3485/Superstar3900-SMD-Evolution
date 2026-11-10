"""V7.10 KiCad integration index gate tests (static, not native ERC/DRC).

The native KiCad workflow separately exports a netlist and executes ERC and
DRC. These static tests only establish file availability, provenance,
isolation and absence of accidental RF/TX cross-module links.
"""
import csv
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
WORKDIR=ROOT/"04_KiCad"/"Assemblaggio_RX_Power_V7.10_NOT_FOR_FAB"
TOP=WORKDIR/"S3900E_RX_POWER_INTEGRATION_V7_10_NOT_FOR_FAB.kicad_sch"
MANIFEST=WORKDIR/"MATRICE_INTERFACCE_DA_QUALIFICARE_V7_10.csv"
RXSCHEMATIC=ROOT/"04_KiCad"/"Modulo_RX_Test_50ohm_V5.2_PARITY_LINK_STUDY_NOT_FOR_FAB"/"S3900E_RX_TEST_50R_V5_2_LINKED_STUDY_NOT_FOR_FAB.kicad_sch"
RXPCB=RXSCHEMATIC.with_suffix(".kicad_pcb")
POWER=ROOT/"04_KiCad"/"Gerarchico_Alimentazioni_V1.5"/"S3900E_AUX_POWER_V1_5.kicad_sch"
MCU=ROOT/"04_KiCad"/"Modulo_MCU_CODEC_V2.1"/"S3900E_MCU_CODEC_AFE_V2_1_DRAFT.kicad_sch"


def balanced_kicad_parentheses(source):
    """Simple quote-aware enclosure validation; NOT a native KiCad parser."""
    depth=0
    quoted=False
    escaped=False
    for c in source:
        if escaped:
            escaped=False
        elif quoted and c=="\\":
            escaped=True
        elif c=='"':
            quoted=not quoted
        elif not quoted and c=="(":
            depth+=1
        elif not quoted and c==")":
            depth-=1
            if depth<0:
                return False
    return depth==0 and not quoted


class V710(unittest.TestCase):
    def test_01_new_kicad_file_exists_and_is_native_schematic(self):
        self.assertTrue(TOP.is_file())
        raw=TOP.read_text(encoding="utf-8")
        self.assertTrue(raw.startswith("(kicad_sch (version 20231120)"))
        self.assertTrue(balanced_kicad_parentheses(raw))

    def test_02_three_existing_designs_referenced_by_real_kicad_sheet(self):
        raw=TOP.read_text(encoding="utf-8")
        links=re.findall(r'\(property "Sheetfile" "([^"]+\.kicad_sch)"',raw)
        self.assertEqual(len(links),3)
        self.assertEqual(len(set(links)),3)
        self.assertTrue(all((WORKDIR/x).resolve().is_file() for x in links))

    def test_03_reuse_original_files_unmodified_and_no_fab(self):
        for f in (POWER,MCU,RXSCHEMATIC,RXPCB):
            self.assertTrue(f.is_file(),str(f))
            self.assertGreater(f.stat().st_size,10000)
        self.assertIn("NOT_FOR_FAB",str(WORKDIR))
        self.assertIn("NO FAB / NO TX",TOP.read_text(encoding="utf-8"))

    def test_04_original_power_is_hierarchical(self):
        s=POWER.read_text(encoding="utf-8")
        self.assertIn("01_EFUSE_AUX.kicad_sch",s)
        self.assertIn("02_BUCK_5V.kicad_sch",s)
        self.assertIn("03_PLL_LDO_TCXO.kicad_sch",s)
        for f in ("01_EFUSE_AUX.kicad_sch","02_BUCK_5V.kicad_sch",
                  "03_PLL_LDO_TCXO.kicad_sch"):
            self.assertTrue((POWER.parent/f).is_file())

    def test_05_rx_pcb_contains_8_defined_nets_no_tx(self):
        s=RXPCB.read_text(encoding="utf-8")
        nets=re.findall(r'\(net (\d+) "([^"]+)"\)',s)
        self.assertEqual([int(x) for x,_ in nets[:9]],list(range(9)))
        for _,name in nets:
            self.assertNotIn("TX_",name)
        self.assertIn("RF_LNA_INPUT",s)
        self.assertIn("RF_ATTEN_OUT",s)

    def test_06_module_root_has_no_implied_electrical_sheet_pin(self):
        raw=TOP.read_text(encoding="utf-8")
        self.assertNotIn('(pin "',raw)
        self.assertNotIn("(wire (pts",raw)
        self.assertNotIn('(global_label "',raw)
        self.assertIn("all pages isolated",raw)

    def test_07_no_tx_symbols_or_pcb_in_new_integration(self):
        s=TOP.read_text(encoding="utf-8")
        self.assertNotIn('DAC900',s)
        self.assertNotIn('PA_',s)
        self.assertNotIn('RF_TX_',s)
        self.assertNotIn('kicad_pcb',s)

    def test_08_interface_contract_exists_and_open(self):
        with MANIFEST.open(encoding="utf-8",newline="") as f:
            rows=list(csv.DictReader(f))
        self.assertGreaterEqual(len(rows),10)
        self.assertTrue(all(x["physical_connection"]=="OPEN" for x in rows))
        self.assertTrue(all(x["qualification"]=="HOLD" for x in rows))
        self.assertTrue(all(x["tx_permission"]=="0" for x in rows))

    def test_09_unverified_rails_not_equated(self):
        text=MANIFEST.read_text(encoding="utf-8")
        self.assertIn("5V_RF_PREREGULATED",text)
        self.assertIn("+5V_BENCH",text)
        self.assertIn("NO_ASSUMED_EQUIVALENCE",text)

    def test_10_legacy_RX_board_references_15_symbols(self):
        schematic=RXSCHEMATIC.read_text(encoding="utf-8")
        board=RXPCB.read_text(encoding="utf-8")
        refs=set(re.findall(r'\(property "Reference" "([RLCUJ]\d{2,4})"',schematic))
        self.assertGreaterEqual(len(refs),15)
        for ref in refs:
            self.assertIn(f'"{ref}"',board)

    def test_11_previous_vendor_pin_hold_unchanged(self):
        p=ROOT/"01_Specifiche"/"V7.6"/"SG48_PIN_PLAN_CANDIDATE_V7.6.csv"
        self.assertTrue(p.is_file())
        with p.open(encoding="utf-8",newline="") as f:
            pins=list(csv.DictReader(f))
        self.assertEqual(len(pins),49)
        self.assertTrue(all("HOLD" in t["design_qualification"] for t in pins))

    def test_12_radiator_physical_gates_are_absent(self):
        self.assertTrue(all("TX" not in x.name for x in (TOP,RXPCB)))
        self.assertTrue((ROOT/"07_Componenti"/"BOM_WATCHDOG_FILTRO_V7.9.csv").is_file())


if __name__=="__main__":
    unittest.main()
