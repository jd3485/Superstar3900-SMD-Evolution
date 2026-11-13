"""V7.73 native seven-sheet ERC error inventory; no waiver and no fabricated fix."""
from pathlib import Path
from collections import Counter
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc
OUT=ROOT/"03_Verifiche/V7.73/output-ci"
def audit():
    d=native_erc(ROOT/"03_Verifiche/V7.72/output-ci/v772.revised.erc.rpt")
    assert (d["errors"],d["warnings"],d["total"])==(28,180,208)
    errors=[e for e in d["findings"] if e["severity"]=="error"]
    assert len(errors)==28 and all(e["sheet"] and e["category"] and e["locations"] for e in errors)
    rows=[dict(id="ERC-E%02d"%i,**e,status="OPEN_UNRESOLVED",waiver=False,root_cause_verified=False)
          for i,e in enumerate(errors,1)]
    by_category=dict(sorted(Counter(e["category"] for e in rows).items()))
    by_sheet=dict(sorted(Counter(e["sheet"] for e in rows).items()))
    assert sum(by_category.values())==sum(by_sheet.values())==28
    result=dict(revision="V7.73",source="KiCad9 V7.72 seven-sheet native ERC",
                errors=rows,by_category=by_category,by_sheet=by_sheet,
                error_count=28,warning_count=180,NO_FAB=True,NO_TX=True,
                NO_GERBER=True,NO_PCBWAY=True,crossmodule_15_OPEN_HOLD=True,
                SG48_HOLD=True,D200_TVS_DNP=True,full_pcb_DRC_completed=False)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v773_native_28_errors.json").write_text(json.dumps(result,indent=2)+"\n")
    lines=["# V7.73 — inventario completo errori ERC nativi","",
           "KiCad9 sette fogli V7.72: 28 errori e 180 warning; nessuna correzione o waiver.","",
           "## Categorie"]+["- %s: %d"%(k,v) for k,v in by_category.items()]
    lines+=["","## Fogli"]+["- %s: %d"%(k,v) for k,v in by_sheet.items()]
    lines+=["","## Tutti i 28 errori aperti"]
    for row in rows:
        lines+=["","### %s — %s (%s)"%(row["id"],row["category"],row["sheet"]),
                row["message"]]+["- "+loc for loc in row["locations"]]+["Stato OPEN, causa e fix non qualificati."]
    lines+=["","15 crossmodule OPEN/HOLD, SG48 HOLD, D200 DNP, EFUSE_RTN separato da GND_MAIN.",
            "Nessuna PCB unificata, nessun DRC globale. NO FAB / NO GERBER / NO PCBWAY / NO TX."]
    (OUT/"v773_native_28_errors.md").write_text("\n".join(lines)+"\n")
    for row in rows:print("ERC TRIAGE",row["id"],row["category"],row["sheet"],row["locations"][0])
    return result
class TestNativeTriage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.d=audit()
    def test_01_count(self):self.assertEqual(self.d["error_count"],28)
    def test_02_warnings(self):self.assertEqual(self.d["warning_count"],180)
    def test_03_exact_entries(self):self.assertEqual(len(self.d["errors"]),28)
    def test_04_by_category(self):self.assertEqual(sum(self.d["by_category"].values()),28)
    def test_05_by_sheet(self):self.assertEqual(sum(self.d["by_sheet"].values()),28)
    def test_06_all_open(self):self.assertTrue(all(x["status"]=="OPEN_UNRESOLVED" for x in self.d["errors"]))
    def test_07_no_waivers(self):self.assertFalse(any(x["waiver"] for x in self.d["errors"]))
    def test_08_no_fabricated_cause(self):self.assertFalse(any(x["root_cause_verified"] for x in self.d["errors"]))
    def test_09_locations(self):self.assertTrue(all(x["locations"] for x in self.d["errors"]))
    def test_10_crossmodule(self):self.assertTrue(self.d["crossmodule_15_OPEN_HOLD"])
    def test_11_sg48(self):self.assertTrue(self.d["SG48_HOLD"])
    def test_12_tvs(self):self.assertTrue(self.d["D200_TVS_DNP"])
    def test_13_no_drc(self):self.assertFalse(self.d["full_pcb_DRC_completed"])
    def test_14_no_fab(self):self.assertTrue(self.d["NO_FAB"] and self.d["NO_GERBER"])
    def test_15_no_tx(self):self.assertTrue(self.d["NO_TX"] and self.d["NO_PCBWAY"])
if __name__=="__main__":unittest.main()
