"""V7.63: C&K KMR223NG ULC LFG vendor 4-pad SW200, KiCad9 full electrical safety gate, NO FAB."""
from pathlib import Path
from collections import Counter
import json,re,sys,unittest

ROOT=Path(__file__).resolve().parents[2]
OLD_AUX=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.62_EFUSE_SHDN_MANUAL_RESET_REVIEW_NOT_FOR_FAB/01_EFUSE_AUX.kicad_sch"
NEW_AUX=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.63_CK_KMR223NG_ULC_4PAD_REVIEW_NOT_FOR_FAB/01_EFUSE_AUX.kicad_sch"
OLD_ROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.62_EFUSE_MANUAL_RESET_REVIEW_NOT_FOR_FAB"
NEW_ROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.63_CK_KMR223NG_ULC_4PAD_REVIEW_NOT_FOR_FAB"
OLD_LIB=ROOT/"04_KiCad/Librerie_Simboli_V7.62_EFUSE_RESET_SW_HOLD/S3900E.kicad_sym"
NEW_LIB=ROOT/"04_KiCad/Librerie_Simboli_V7.63_CK_KMR223NG_ULC_4PAD_HOLD/S3900E.kicad_sym"
MOD=ROOT/"04_KiCad/Librerie_Footprint_V7.63_CK_KMR223NG_ULC_HOLD/S3900E_CK_KMR2_Review.pretty/CK_KMR223NG_ULC_LFG_4PAD_VENDOR_LAND_REVIEW.kicad_mod"
OUT=ROOT/"03_Verifiche/V7.63/output-ci"
MASTER="S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
FP="S3900E_CK_KMR2_V763_HOLD:CK_KMR223NG_ULC_LFG_4PAD_VENDOR_LAND_REVIEW"
MPN="KMR223NG ULC LFG"

sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def pinmap(path):
    d={}
    for net, pins in nets(path).items():
        for p in pins:
            assert p not in d,("repeated pin",p)
            d[p]=net
    return d

def sexpr_source_gate():
    before=OLD_AUX.read_text(encoding="utf8")
    after=NEW_AUX.read_text(encoding="utf8")
    # All 139 existing non-SW200 components remain; added only two SW200
    # pads and two net labels, C&K MPN/footprint/qualification value metadata.
    for ref in ('U200','R204','R203','F200'):
        assert after.count(f'(property "Reference" "{ref}"')==before.count(f'(property "Reference" "{ref}"')==1
    assert after.count('(property "Reference" "SW200"')==1
    assert after.count('(property "MPN" "'+MPN+'"')==1
    assert after.count('(property "Footprint" "'+FP+'"')==1
    assert after.count('(label "EFUSE_SHDN_RESET_N" (at 327.66 241.30 0)')==1
    assert after.count('(label "GND_MAIN" (at 337.82 241.30 0)')==1
    oldprefix='(symbol "S3900E:SW_EFUSE_SHDN_RESET_NO_REVIEW"'
    a=after.index(oldprefix)
    b=after.index(' (symbol "S3900E:R_EFUSE"',a)
    em=after[a:b]
    nums=re.findall(r'\(number "(\d+)"',em)
    assert nums==["1","2","4","3"],nums
    original=OLD_LIB.read_text(encoding="utf8")
    newlib=NEW_LIB.read_text(encoding="utf8")
    start=original.index(' (symbol "SW_EFUSE_SHDN_RESET_NO_REVIEW"')
    assert newlib==original[:start]+" "+em.replace(
        oldprefix,'(symbol "SW_EFUSE_SHDN_RESET_NO_REVIEW"',1).strip()+"\n)\n"
    # Match physical manufacturer top view: 4 1 / 3 2. NG only, no G pin.
    import pcbnew
    fp=pcbnew.FootprintLoad(str(MOD.parent),MOD.stem)
    assert fp is not None,"KiCad9 pcbnew vendor switch footprint load failed"
    pads={}
    for pad in fp.Pads():
        num=pad.GetNumber()
        assert num not in pads,("physical terminal duplicates",num)
        p=pad.GetPosition()
        sz=pad.GetSize()
        pads[num]=(
            round(p.x/1e6,3),round(p.y/1e6,3),
            round(sz.x/1e6,3),round(sz.y/1e6,3))
    assert pads=={
        "4":(-2.05,-0.8,0.9,1.0),"1":(2.05,-0.8,0.9,1.0),
        "3":(-2.05,0.8,0.9,1.0),"2":(2.05,0.8,0.9,1.0)
    },pads
    # This footprint is NOT mechanically approved; 5x2.6 mm land envelope
    # and 0.9x1.0mm pads derive from KMR2 2026 datasheet NG layout.
    aroot=(OLD_ROOT/MASTER).read_text()
    broot=(NEW_ROOT/MASTER).read_text()
    assert broot==aroot.replace(
        "Gerarchico_Alimentazioni_V7.62_EFUSE_SHDN_MANUAL_RESET_REVIEW_NOT_FOR_FAB",
        "Gerarchico_Alimentazioni_V7.63_CK_KMR223NG_ULC_4PAD_REVIEW_NOT_FOR_FAB")
    for name in ("S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_pro",):
        assert (OLD_ROOT/name).read_bytes()==(NEW_ROOT/name).read_bytes()
    return pads

def gate():
    pads=sexpr_source_gate()
    a=compmap(OUT/"v763.original.net")
    b=compmap(OUT/"v763.revised.net")
    assert len(a)==len(b)==140
    for ref in a:
        if ref!="SW200":
            assert a[ref]==b[ref],("Changed original component",ref,a[ref],b[ref])
    assert b["SW200"][0]==FP,b["SW200"]
    assert b["SW200"][1]=="KMR223NG ULC LFG (CANDIDATE)",b["SW200"]
    n0=nets(OUT/"v763.original.net")
    n1=nets(OUT/"v763.revised.net")
    assert len(n0)==len(n1)==103
    original=pinmap(OUT/"v763.original.net")
    revised=pinmap(OUT/"v763.revised.net")
    assert {p:revised[p] for p in original}==original,"Changed old physical pin->net"
    assert set(revised)-set(original)=={("SW200","3"),("SW200","4")}
    assert revised[("SW200","1")]==revised[("SW200","4")]==revised[("U200","7")]
    assert revised[("SW200","2")]==revised[("SW200","3")]==revised[("U200","9")]
    assert revised[("U200","9")]!=revised[("U200","8")]
    assert revised[("U200","8")]==revised[("U200","17")]
    assert revised[("U200","6")]==original[("U200","6")]
    e0=native_erc(OUT/"v763.original.erc.rpt")
    e1=native_erc(OUT/"v763.revised.erc.rpt")
    assert e0["errors"]==28 and e0["warnings"]==214,(e0["errors"],e0["warnings"])
    assert e1["errors"]==28,"New/missing ERC error"
    old_error=Counter(json.dumps(x,sort_keys=True) for x in e0["findings"] if x["severity"]=="error")
    new_error=Counter(json.dumps(x,sort_keys=True) for x in e1["findings"] if x["severity"]=="error")
    assert old_error==new_error,("New/dropped ERC errors",list((new_error-old_error).elements())[:5])
    assert e1["warnings"]<=214,("New warnings after fully-vendor footprint",e1["warnings"])
    # Existing offgrid and all other violations are not waived.
    result=dict(components=140,nets=103,vendor_pads=4,
        original_pin_map_preserved=True,
        ck_gold_ulc_minimum_current_uA_at_1p8V=1,
        ck_ng_4pad_native_library_review=True,
        footprint_present=True,physical_package_candidate=True,
        footprint_vendor_geometry_review=True,
        internal_reset_verified_without_mcu=True,
        erc_before={"errors":28,"warnings":214},
        erc_after={"errors":e1["errors"],"warnings":e1["warnings"]},
        panel_mounting_approved=False,
        environmental_ip40_sealed=False,
        esd_emc_approved=False,
        actual_fault_recovery_measured=False,
        complete_pcb_drc_approved=False,NO_FAB=True,NO_TX=True)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v763.kmr223ng_native_review.json").write_text(json.dumps(result,indent=2)+"\n")
    return result

class TestV763FourPadVendor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=gate()
    def test_01_parts(self):self.assertEqual(self.r["components"],140)
    def test_02_nets(self):self.assertEqual(self.r["nets"],103)
    def test_03_4pad(self):self.assertEqual(self.r["vendor_pads"],4)
    def test_04_pinmap(self):self.assertTrue(self.r["original_pin_map_preserved"])
    def test_05_vendor_footprint(self):self.assertTrue(self.r["footprint_present"])
    def test_06_gold_ulc(self):self.assertEqual(self.r["ck_gold_ulc_minimum_current_uA_at_1p8V"],1)
    def test_07_erc_errors(self):self.assertEqual(self.r["erc_after"]["errors"],28)
    def test_08_erc_no_new_warnings(self):self.assertLessEqual(self.r["erc_after"]["warnings"],214)
    def test_09_panel_hold(self):self.assertFalse(self.r["panel_mounting_approved"])
    def test_10_ip40_hold(self):self.assertFalse(self.r["environmental_ip40_sealed"])
    def test_11_esd_hold(self):self.assertFalse(self.r["esd_emc_approved"])
    def test_12_hw_hold(self):self.assertFalse(self.r["actual_fault_recovery_measured"])
    def test_13_board_hold(self):self.assertFalse(self.r["complete_pcb_drc_approved"])
    def test_14_safety(self):self.assertTrue(self.r["NO_FAB"] and self.r["NO_TX"])

if __name__=="__main__":
    unittest.main()
