"""V7.60 native KiCad9 U6207 supervisor+C6231 bypass 100mil pin grid ECO, fail closed."""
from pathlib import Path
from collections import Counter
import json,re,sys,unittest

ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.59_FOUR_LDO_100MIL_GRID_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
NEW=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.60_SUPERVISOR_C6231_GRID_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
OLDROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.59_FOUR_LDO_100MIL_GRID_REVIEW_NOT_FOR_FAB"
NEWROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.60_SUPERVISOR_C6231_GRID_REVIEW_NOT_FOR_FAB"
MASTER="S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
OUT=ROOT/"03_Verifiche/V7.60/output-ci"
TARGETS={
 "U6207":("S3900E:TPS3840PL30_DBV5_REVIEW",1010.,415.,
          [(-10.16,10.16),(-10.16,-10.16),(10.16,0),(10.16,10.16),(10.16,-10.16)],3,2),
 "C6231":("S3900E:C_DRAFT",1050.,415.,[(0,5.08),(0,-5.08)],2,0)
}
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def ongrid(n):
    return abs(n/2.54-round(n/2.54))<1e-7

def pmap(path):
    result={}
    for net,pins in nets(path).items():
        for pin in pins:
            assert pin not in result,("duplicate pin",pin)
            result[pin]=net
    return result

def source_check():
    old=OLD.read_text(encoding="utf8")
    actual=NEW.read_text(encoding="utf8")
    expected=old
    moved_total=0
    for ref,(lib,x,y,points,labels_expected,ncs_expected) in TARGETS.items():
        nx=round(2.54*round(x/2.54),4);ny=round(2.54*round(y/2.54),4)
        anchor=f'(symbol (lib_id "{lib}") (at {x:.4f} {y:.4f} 0)'
        p=expected.index(anchor)
        q=expected.index("\n(label ",p)
        frag=expected[p:q]
        assert f'(property "Reference" "{ref}"' in frag
        edits=[0]
        def f(m):
            edits[0]+=1
            return f'(at {nx:.4f} {float(m[1])+ny-y:.4f} 0)'
        pattern=r'\(at '+f'{x:.4f}'+r' (\d+\.\d+) 0\)'
        frag=re.sub(pattern,f,frag)
        assert edits[0]==5,(ref,edits)
        expected=expected[:p]+frag+expected[q:]
        changes={}
        for dx,dy in points:
            before=f'(at {x+dx:.4f} {y-dy:.4f}'
            after=f'(at {nx+dx:.4f} {ny-dy:.4f}'
            assert before not in changes
            assert ongrid(nx+dx) and ongrid(ny-dy)
            assert f'(xy {x+dx:.4f} {y-dy:.4f}' not in old,"Wire at moved pin must be handled"
            changes[before]=after
        hits=[0,0,0]
        lines=[]
        for line in expected.splitlines(keepends=True):
            if line.startswith("(label ") or line.startswith("(no_connect "):
                matches=[(a,b) for a,b in changes.items() if a in line]
                assert len(matches)<=1
                if matches:
                    a,b=matches[0]
                    hits[0]+=1
                    hits[1 if line.startswith("(label ") else 2]+=1
                    line=line.replace(a,b,1)
            lines.append(line)
        expected="".join(lines)
        assert hits==[len(points),labels_expected,ncs_expected],(ref,hits)
        moved_total+=hits[0]
    assert actual==expected,"Changed unrelated MCU symbol/text/NC/connection"
    master0=(OLDROOT/MASTER).read_text(encoding="utf8")
    master1=(NEWROOT/MASTER).read_text(encoding="utf8")
    assert master1==master0.replace("Modulo_MCU_CODEC_V7.59_FOUR_LDO_100MIL_GRID_REVIEW_NOT_FOR_FAB",
                                    "Modulo_MCU_CODEC_V7.60_SUPERVISOR_C6231_GRID_REVIEW_NOT_FOR_FAB")
    for fn in ("fp-lib-table","sym-lib-table","S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_pro"):
        assert (OLDROOT/fn).read_bytes()==(NEWROOT/fn).read_bytes(),fn
    return moved_total

def erc_not_target(erc):
    candidates=[]
    removed=[]
    pat=re.compile(r'^@\([0-9.]+ mm, [0-9.]+ mm\): Symbol (U6207|C6231) Pin (\d+) \[.+\]')
    for finding in erc["findings"]:
        d=dict(finding)
        locations=d.get("locations",[])
        m=pat.fullmatch(locations[0]) if len(locations)==1 else None
        if (m and d.get("category")=="endpoint_off_grid" and
            d.get("severity")=="warning" and d.get("sheet")=="/"):
            removed.append((m.group(1),m.group(2)))
        else:
            # Pre-existing U6207 missing-library diagnostic retains category,
            # severity and message. Only its physical location follows ECO.
            library_location=re.compile(
                r'^@\\([0-9.]+ mm, [0-9.]+ mm\\): Symbol U6207 \\[TPS3840PL30_DBV5_REVIEW\\]
    return Counter(candidates),removed

def check():
    moved=source_check()
    a=compmap(OUT/"v760.original.net")
    b=compmap(OUT/"v760.revised.net")
    assert len(a)==len(b)==139 and a==b,"Unwanted BOM/footprint change"
    assert all(x[0] for x in b.values()),"Missing footprint assignment"
    p0=pmap(OUT/"v760.original.net");p1=pmap(OUT/"v760.revised.net")
    assert len(nets(OUT/"v760.original.net"))==len(nets(OUT/"v760.revised.net"))==102
    assert p0==p1,"Native KiCad full seven-sheet pin/net graph changed"
    assert p1[("U200","8")]==p1[("U200","17")] and p1[("U200","8")]!=p1[("U200","9")]
    assert ("U200","7") not in p1,"SHDN must remain NC"
    er0=native_erc(OUT/"v760.original.erc.rpt")
    er1=native_erc(OUT/"v760.revised.erc.rpt")
    assert er0["errors"]==er1["errors"]==28
    oldother,oldtarget=erc_not_target(er0)
    newother,newtarget=erc_not_target(er1)
    if oldother!=newother:
        print("ERC ADDED",list((newother-oldother).elements())[:12],flush=True)
        print("ERC REMOVED",list((oldother-newother).elements())[:12],flush=True)
    assert oldother==newother,"Non-target native ERC diagnostics changed"
    assert not newtarget,("Residual target offgrid",newtarget)
    assert set(ref for ref,_ in oldtarget)==set(TARGETS),(oldtarget,newtarget)
    # Each targeted symbol with off-grid pins is reported as one finding,
    # but only KiCad9 native proof determines the exact delta.
    assert len(oldtarget)==2,oldtarget
    assert er0["warnings"]==217 and er1["warnings"]==215,(er0["warnings"],er1["warnings"])
    assert er0["categories"]["endpoint_off_grid"]-er1["categories"]["endpoint_off_grid"]==2
    out=dict(parts=139,nets=102,attached_nodes=moved,offgrid_eliminated=2,
             erc_before={"errors":28,"warnings":217},
             erc_after={"errors":28,"warnings":215},identical_pin_nets=True,
             independent_efuse_reset=False,actual_5v_budget_qualified=False,
             all_intermodules_closed=False,full_board_drc_approved=False,
             no_fab=True,no_tx=True)
    OUT.mkdir(exist_ok=True,parents=True)
    (OUT/"v760.supervisor_grid.json").write_text(json.dumps(out,indent=2)+"\n")
    return out

class TestV760Grid(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=check()
    def test_01_two_references(self):self.assertEqual(set(TARGETS),{"U6207","C6231"})
    def test_02_seven_attachments(self):self.assertEqual(self.r["attached_nodes"],7)
    def test_03_parts(self):self.assertEqual(self.r["parts"],139)
    def test_04_nets(self):self.assertEqual(self.r["nets"],102)
    def test_05_no_net_change(self):self.assertTrue(self.r["identical_pin_nets"])
    def test_06_erc_errors(self):self.assertEqual(self.r["erc_after"]["errors"],28)
    def test_07_offgrid_removed(self):self.assertEqual(self.r["offgrid_eliminated"],2)
    def test_08_erc_warnings(self):self.assertEqual(self.r["erc_after"]["warnings"],215)
    def test_09_reset_hold(self):self.assertFalse(self.r["independent_efuse_reset"])
    def test_10_load_hold(self):self.assertFalse(self.r["actual_5v_budget_qualified"])
    def test_11_intermodules_hold(self):self.assertFalse(self.r["all_intermodules_closed"])
    def test_12_pcb_hold(self):self.assertFalse(self.r["full_board_drc_approved"])
    def test_13_no_fab(self):self.assertTrue(self.r["no_fab"] and self.r["no_tx"])

if __name__=="__main__":
    unittest.main()
)
            if (d.get("category")=="lib_symbol_issues"
                and d.get("severity")=="warning" and d.get("sheet")=="/"
                and d.get("message")=="Symbol 'TPS3840PL30_DBV5_REVIEW' not found in symbol library 'S3900E'"
                and len(locations)==1 and library_location.fullmatch(locations[0])):
                d["locations"]=["U6207 existing missing-library warning, coordinate only"]
            candidates.append(json.dumps(d,sort_keys=True,ensure_ascii=False))
    return Counter(candidates),removed

def check():
    moved=source_check()
    a=compmap(OUT/"v760.original.net")
    b=compmap(OUT/"v760.revised.net")
    assert len(a)==len(b)==139 and a==b,"Unwanted BOM/footprint change"
    assert all(x[0] for x in b.values()),"Missing footprint assignment"
    p0=pmap(OUT/"v760.original.net");p1=pmap(OUT/"v760.revised.net")
    assert len(nets(OUT/"v760.original.net"))==len(nets(OUT/"v760.revised.net"))==102
    assert p0==p1,"Native KiCad full seven-sheet pin/net graph changed"
    assert p1[("U200","8")]==p1[("U200","17")] and p1[("U200","8")]!=p1[("U200","9")]
    assert ("U200","7") not in p1,"SHDN must remain NC"
    er0=native_erc(OUT/"v760.original.erc.rpt")
    er1=native_erc(OUT/"v760.revised.erc.rpt")
    assert er0["errors"]==er1["errors"]==28
    oldother,oldtarget=erc_not_target(er0)
    newother,newtarget=erc_not_target(er1)
    if oldother!=newother:
        print("ERC ADDED",list((newother-oldother).elements())[:12],flush=True)
        print("ERC REMOVED",list((oldother-newother).elements())[:12],flush=True)
    assert oldother==newother,"Non-target native ERC diagnostics changed"
    assert not newtarget,("Residual target offgrid",newtarget)
    assert set(ref for ref,_ in oldtarget)==set(TARGETS),(oldtarget,newtarget)
    # Each targeted symbol with off-grid pins is reported as one finding,
    # but only KiCad9 native proof determines the exact delta.
    assert len(oldtarget)==2,oldtarget
    assert er0["warnings"]==217 and er1["warnings"]==215,(er0["warnings"],er1["warnings"])
    assert er0["categories"]["endpoint_off_grid"]-er1["categories"]["endpoint_off_grid"]==2
    out=dict(parts=139,nets=102,attached_nodes=moved,offgrid_eliminated=2,
             erc_before={"errors":28,"warnings":217},
             erc_after={"errors":28,"warnings":215},identical_pin_nets=True,
             independent_efuse_reset=False,actual_5v_budget_qualified=False,
             all_intermodules_closed=False,full_board_drc_approved=False,
             no_fab=True,no_tx=True)
    OUT.mkdir(exist_ok=True,parents=True)
    (OUT/"v760.supervisor_grid.json").write_text(json.dumps(out,indent=2)+"\n")
    return out

class TestV760Grid(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=check()
    def test_01_two_references(self):self.assertEqual(set(TARGETS),{"U6207","C6231"})
    def test_02_seven_attachments(self):self.assertEqual(self.r["attached_nodes"],7)
    def test_03_parts(self):self.assertEqual(self.r["parts"],139)
    def test_04_nets(self):self.assertEqual(self.r["nets"],102)
    def test_05_no_net_change(self):self.assertTrue(self.r["identical_pin_nets"])
    def test_06_erc_errors(self):self.assertEqual(self.r["erc_after"]["errors"],28)
    def test_07_offgrid_removed(self):self.assertEqual(self.r["offgrid_eliminated"],2)
    def test_08_erc_warnings(self):self.assertEqual(self.r["erc_after"]["warnings"],215)
    def test_09_reset_hold(self):self.assertFalse(self.r["independent_efuse_reset"])
    def test_10_load_hold(self):self.assertFalse(self.r["actual_5v_budget_qualified"])
    def test_11_intermodules_hold(self):self.assertFalse(self.r["all_intermodules_closed"])
    def test_12_pcb_hold(self):self.assertFalse(self.r["full_board_drc_approved"])
    def test_13_no_fab(self):self.assertTrue(self.r["no_fab"] and self.r["no_tx"])

if __name__=="__main__":
    unittest.main()
