"""V7.59 real U6203-U6206 100mil KiCad geometry ECO: native ERC and pin net parity, NO FAB."""
from pathlib import Path
from collections import Counter
import json
import re
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.58_U6202_100MIL_GRID_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
NEW=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.59_FOUR_LDO_100MIL_GRID_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
OLDROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.58_U6202_100MIL_GRID_REVIEW_NOT_FOR_FAB"
NEWROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.59_FOUR_LDO_100MIL_GRID_REVIEW_NOT_FOR_FAB"
MASTER="S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
OUT=ROOT/"03_Verifiche/V7.59/output-ci"
TARGETS={"U6203":(710.0,320.0),"U6204":(810.0,415.0),
         "U6205":(870.0,415.0),"U6206":(930.0,415.0)}
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def ongrid(v):
    return abs(v/2.54-round(v/2.54))<1e-7

def pinmap(path):
    d={}
    for n,ps in nets(path).items():
        for p in ps:
            assert p not in d, ("duplicate pin",p)
            d[p]=n
    return d

def source_gate():
    old=OLD.read_text(encoding="utf8")
    actual=NEW.read_text(encoding="utf8")
    expected=old
    result={}
    for ref,(x,y) in TARGETS.items():
        nx=round(2.54*round(x/2.54),4)
        ny=round(2.54*round(y/2.54),4)
        anchor=f'(symbol (lib_id "S3900E:TPS7A2033_DBV_DRAFT") (at {x:.4f} {y:.4f} 0)'
        p=expected.index(anchor)
        q=expected.index("(symbol (lib_id",p+20)
        frag=expected[p:q]
        assert f'(property "Reference" "{ref}"' in frag
        edits=[0]
        def moved(m):
            edits[0]+=1
            return f'(at {nx:.4f} {float(m[1])+ny-y:.4f} 0)'
        frag=re.sub(r'\(at '+f'{x:.4f}'+r' (\d+\.\d+) 0\)',moved,frag)
        assert edits[0]==4,(ref,edits)
        expected=expected[:p]+frag+expected[q:]
        points={}
        for xx in (x-10.16,x+10.16):
            for yy in (y-10.16,y,y+10.16):
                pts=(f'{xx:.4f} {yy:.4f}',f'{xx+nx-x:.4f} {yy+ny-y:.4f}')
                points[pts[0]]=pts[1]
                assert ongrid(xx+nx-x) and ongrid(yy+ny-y)
                assert "(xy "+pts[0] not in old,"Unexpected real wire endpoint: "+ref
        count=[0,0,0]
        lines=[]
        for line in expected.splitlines(keepends=True):
            if line.startswith("(label ") or line.startswith("(no_connect "):
                for before,after in points.items():
                    if "(at "+before in line:
                        count[0]+=1
                        count[1 if line.startswith("(label ") else 2]+=1
                        line=line.replace("(at "+before,"(at "+after,1)
                        break
            lines.append(line)
        expected="".join(lines)
        assert count==[5,4,1],(ref,count)
        result[ref]={"center_before":[x,y],"center_after":[nx,ny],
                     "moved_attachments":count[0]}
    assert expected==actual,"Unexpected changes outside U6203-U6206 positions/attached labels/NC"
    oldroot=(OLDROOT/MASTER).read_text(encoding="utf8")
    newroot=(NEWROOT/MASTER).read_text(encoding="utf8")
    assert newroot==oldroot.replace("Modulo_MCU_CODEC_V7.58_U6202_100MIL_GRID_REVIEW_NOT_FOR_FAB",
                                    "Modulo_MCU_CODEC_V7.59_FOUR_LDO_100MIL_GRID_REVIEW_NOT_FOR_FAB")
    for fn in ("fp-lib-table","sym-lib-table","S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_pro"):
        assert (OLDROOT/fn).read_bytes()==(NEWROOT/fn).read_bytes(),fn
    return result

def diagnostics(erc):
    # Keep ALL raw diagnostic counts. Remove only U6203-6 offgrid
    # from the comparison as these must disappear in the revised ERC.
    # Retain power-pin errors even if their location coordinate moves.
    off=re.compile(r'^@\([0-9.]+ mm, [0-9.]+ mm\): Symbol (U620[3-6]) Pin (\d+) \[.+\]')
    power=re.compile(r'^@\([0-9.]+ mm, [0-9.]+ mm\): Symbol (U620[3-6]) Pin (\d+) \[.+\]')
    retained,removed=[],[]
    for finding in erc["findings"]:
        d=dict(finding)
        loc=d.get("locations",[])
        hit=off.fullmatch(loc[0]) if len(loc)==1 else None
        if hit and d.get("category")=="endpoint_off_grid" and d.get("severity")=="warning" and d.get("sheet")=="/":
            removed.append((hit.group(1),hit.group(2)))
            continue
        hit=power.fullmatch(loc[0]) if len(loc)==1 else None
        if hit and d.get("category")=="power_pin_not_driven" and d.get("severity")=="error":
            d["locations"]=[f"Existing power-pin-not-driven {hit.group(1)} pin{hit.group(2)}"]
        retained.append(json.dumps(d,sort_keys=True,ensure_ascii=False))
    return Counter(retained),removed

def native_gate():
    moved=source_gate()
    a=compmap(OUT/"v759.original.net")
    b=compmap(OUT/"v759.revised.net")
    assert len(a)==len(b)==139 and a==b
    assert sum(not val[0] for val in b.values())==0
    p0=pinmap(OUT/"v759.original.net")
    p1=pinmap(OUT/"v759.revised.net")
    assert p0==p1,"Any logical pin/net change is forbidden"
    assert len(nets(OUT/"v759.original.net"))==len(nets(OUT/"v759.revised.net"))==102
    assert p1[("U200","8")]==p1[("U200","17")] and p1[("U200","8")]!=p1[("U200","9")]
    assert ("U200","7") not in p1
    old=native_erc(OUT/"v759.original.erc.rpt")
    new=native_erc(OUT/"v759.revised.erc.rpt")
    assert old["errors"]==new["errors"]==28
    before, removed_before=diagnostics(old)
    after, removed_after=diagnostics(new)
    assert before==after,("Changed non-target ERC findings",
           list((after-before).elements())[:10],list((before-after).elements())[:10])
    assert {x[0] for x in removed_before}==set(TARGETS),removed_before
    assert len(removed_before)==4 and removed_after==[],(removed_before,removed_after)
    assert old["warnings"]==221 and new["warnings"]==217,(old["warnings"],new["warnings"])
    assert old["categories"]["endpoint_off_grid"]-new["categories"]["endpoint_off_grid"]==4
    report=dict(components=139,nets=102,ldos=sorted(TARGETS),moved=moved,
        erc_before={"errors":28,"warnings":221},erc_after={"errors":28,"warnings":217},
        netlist_same=True,ldo_reflow_thermal_validated=False,
        six_ldo_real_load_verified=False,crossmodule_qualified=False,
        eFuse_reset_approved=False,full_pcb_approved=False,NO_FAB=True,NO_TX=True)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v759.geometry_review.json").write_text(json.dumps(report,indent=2)+"\n")
    return report

class TestV759FourLDOGrid(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=native_gate()
    def test_01_four_ldos(self):self.assertEqual(self.r["ldos"],sorted(TARGETS))
    def test_02_parts(self):self.assertEqual(self.r["components"],139)
    def test_03_nets(self):self.assertEqual(self.r["nets"],102)
    def test_04_graph(self):self.assertTrue(self.r["netlist_same"])
    def test_05_erc_errors(self):self.assertEqual(self.r["erc_after"]["errors"],28)
    def test_06_warning_delta(self):self.assertEqual(self.r["erc_before"]["warnings"]-self.r["erc_after"]["warnings"],4)
    def test_07_attachments(self):self.assertTrue(all(x["moved_attachments"]==5 for x in self.r["moved"].values()))
    def test_08_thermal_hold(self):self.assertFalse(self.r["ldo_reflow_thermal_validated"])
    def test_09_load_hold(self):self.assertFalse(self.r["six_ldo_real_load_verified"])
    def test_10_crossmodule_hold(self):self.assertFalse(self.r["crossmodule_qualified"])
    def test_11_efuse_hold(self):self.assertFalse(self.r["eFuse_reset_approved"])
    def test_12_pcb_hold(self):self.assertFalse(self.r["full_pcb_approved"])
    def test_13_safety(self):self.assertTrue(self.r["NO_FAB"] and self.r["NO_TX"])

if __name__=="__main__":
    unittest.main()
