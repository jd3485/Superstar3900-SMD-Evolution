"""V7.61: native KiCad9 vendor U6207 TPS3840 symbol library completeness gate; NO FAB."""
from pathlib import Path
from collections import Counter
import json,re,sys,unittest

ROOT=Path(__file__).resolve().parents[2]
MCU=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.60_SUPERVISOR_C6231_GRID_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
OLDLIB=ROOT/"04_KiCad/Librerie_Simboli_V7.58_U6202_100MIL_GRID_HOLD/S3900E.kicad_sym"
NEWLIB=ROOT/"04_KiCad/Librerie_Simboli_V7.61_SUPERVISOR_U6207_HOLD/S3900E.kicad_sym"
OLDROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.60_SUPERVISOR_C6231_GRID_REVIEW_NOT_FOR_FAB"
NEWROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.61_U6207_SYMBOL_LIBRARY_REVIEW_NOT_FOR_FAB"
MASTER="S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
OUT=ROOT/"03_Verifiche/V7.61/output-ci"
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def pmap(path):
    d={}
    for n,pins in nets(path).items():
        for pin in pins:
            assert pin not in d,("duplicate",pin)
            d[pin]=n
    return d

def source_check():
    src=MCU.read_text(encoding="utf8")
    before=OLDLIB.read_text(encoding="utf8")
    actual=NEWLIB.read_text(encoding="utf8")
    start=src.index('(symbol "S3900E:TPS3840PL30_DBV5_REVIEW"')
    end=src.index('(symbol "S3900E:FB_DRAFT"',start)
    sym=src[start:end].strip()
    sym=sym.replace('(symbol "S3900E:TPS3840PL30_DBV5_REVIEW"',
                    '(symbol "TPS3840PL30_DBV5_REVIEW"',1)
    assert '(symbol "TPS3840PL30_DBV5_REVIEW"' not in before
    assert before.endswith(")\n")
    assert actual==before[:-2]+"  "+sym+"\n)\n","Any unrelated S3900E symbol changed"
    # Exact review component pins 1..5; pin5 CT and MR_N remain NC,
    # original TPS3840 manufacturer behavior is not thereby qualified.
    ids=re.findall(r'\(number "(\d+)"',sym)
    assert sorted(ids)==["1","2","3","4","5"],ids
    assert '(name "RESET_N"' in sym and '(name "CT"' in sym and '(name "MR_N"' in sym
    for fn in (MASTER,"fp-lib-table","S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_pro"):
        assert (OLDROOT/fn).read_bytes()==(NEWROOT/fn).read_bytes(),fn
    table0=(OLDROOT/"sym-lib-table").read_text(encoding="utf8")
    table1=(NEWROOT/"sym-lib-table").read_text(encoding="utf8")
    expect=table0.replace("Librerie_Simboli_V7.58_U6202_100MIL_GRID_HOLD",
                          "Librerie_Simboli_V7.61_SUPERVISOR_U6207_HOLD")
    expect=expect.replace("V7.58 U6202 pin grid correction; all other S3900E symbols preserved; NO FAB/TX",
                          "V7.61 33 unique S3900E symbols including exact embedded TPS3840 U6207; NO FAB/TX")
    assert table1==expect,"Unexpected project sym-lib-table edits"
    return sym

def check():
    s=source_check()
    a=compmap(OUT/"v761.original.net")
    b=compmap(OUT/"v761.revised.net")
    assert len(a)==len(b)==139 and a==b
    assert all(v[0] for v in b.values())
    assert len(nets(OUT/"v761.original.net"))==len(nets(OUT/"v761.revised.net"))==102
    p0=pmap(OUT/"v761.original.net");p1=pmap(OUT/"v761.revised.net")
    assert p0==p1,"Unexpected pin-net topology mutation"
    assert p1[("U200","8")]==p1[("U200","17")] and p1[("U200","8")]!=p1[("U200","9")]
    assert ("U200","7") not in p1
    e0=native_erc(OUT/"v761.original.erc.rpt")
    e1=native_erc(OUT/"v761.revised.erc.rpt")
    assert e0["errors"]==e1["errors"]==28
    assert e0["warnings"]==215 and e1["warnings"]==214,(e0["warnings"],e1["warnings"])
    assert e0["categories"]["lib_symbol_issues"]-e1["categories"].get("lib_symbol_issues",0)==1
    before=Counter(json.dumps(x,sort_keys=True,ensure_ascii=False) for x in e0["findings"])
    after=Counter(json.dumps(x,sort_keys=True,ensure_ascii=False) for x in e1["findings"])
    added=list((after-before).elements())
    removed=list((before-after).elements())
    assert not added,("new ERC findings",added[:12])
    assert len(removed)==1,("unexpected ERC removals",removed[:12])
    finding=json.loads(removed[0])
    assert finding["category"]=="lib_symbol_issues" and finding["severity"]=="warning"
    assert finding["message"]=="Symbol 'TPS3840PL30_DBV5_REVIEW' not found in symbol library 'S3900E'"
    assert "U6207" in finding["locations"][0],finding
    assert e0["categories"]["endpoint_off_grid"]==e1["categories"]["endpoint_off_grid"]
    result=dict(parts=139,nets=102,lib_issue_fixed=1,
        erc_before={"errors":28,"warnings":215},
        erc_after={"errors":28,"warnings":214},
        preserved_graph=True,supervisor_behavior_qualified=False,
        upstream_efuse_recovery_approved=False,
        crossmodule_approved=False,pcb_drc_approved=False,
        NO_FAB=True,NO_TX=True)
    OUT.mkdir(exist_ok=True,parents=True)
    (OUT/"v761.symbol_library_review.json").write_text(json.dumps(result,indent=2)+"\n")
    return result

class TestV761SupervisorLibrary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=check()
    def test_01_parts(self):self.assertEqual(self.r["parts"],139)
    def test_02_nets(self):self.assertEqual(self.r["nets"],102)
    def test_03_graph(self):self.assertTrue(self.r["preserved_graph"])
    def test_04_removed_warning(self):self.assertEqual(self.r["lib_issue_fixed"],1)
    def test_05_erc_errors(self):self.assertEqual(self.r["erc_after"]["errors"],28)
    def test_06_erc_warnings(self):self.assertEqual(self.r["erc_after"]["warnings"],214)
    def test_07_supervisor_hold(self):self.assertFalse(self.r["supervisor_behavior_qualified"])
    def test_08_efuse_hold(self):self.assertFalse(self.r["upstream_efuse_recovery_approved"])
    def test_09_crossmodule_hold(self):self.assertFalse(self.r["crossmodule_approved"])
    def test_10_pcb_hold(self):self.assertFalse(self.r["pcb_drc_approved"])
    def test_11_no_release(self):self.assertTrue(self.r["NO_FAB"] and self.r["NO_TX"])

if __name__=="__main__":
    unittest.main()
