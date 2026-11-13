"""V7.57 KiCad9 TDK CGA6 1210 vendor reflow land; native gate, NOT FAB approval."""
import unittest,sys,json,re
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[2]
OLD_AUX=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.56_TDK_AECQ200_C103_C104_REVIEW_NOT_FOR_FAB"
NEW_AUX=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.57_TDK_CGA6_VENDOR_LAND_REVIEW_NOT_FOR_FAB"
OLD_ROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.56_TDK_AECQ200_MLCC_REVIEW_NOT_FOR_FAB"
NEW_ROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.57_TDK_CGA6_VENDOR_LAND_REVIEW_NOT_FOR_FAB"
FP_DIR=ROOT/"04_KiCad/Librerie_Footprint_V7.57_TDK_CGA6_AECQ200_HOLD/S3900E_TDK_CGA6_Review.pretty"
FP_NAME="TDK_CGA6_1210_AECQ200_C103_C104_VENDOR_LAND_HOLD"
FPN="S3900E_TDK_CGA6_V757_HOLD:"+FP_NAME
OUT=ROOT/"03_Verifiche/V7.57/output-ci"
MASTER="S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.56"))
from test_tdk_aecq200_candidate_native_v756 import pinmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def source_gate():
    orig=(OLD_AUX/"02_BUCK_5V.kicad_sch").read_text(encoding="utf8")
    revised=(NEW_AUX/"02_BUCK_5V.kicad_sch").read_text(encoding="utf8")
    expected=orig
    for x in (277,304):
        a='(property "Footprint" "Capacitor_SMD:C_1210_3225Metric" (at '+str(x)+' 120 0)'
        b='(property "Footprint" "'+FPN+'" (at '+str(x)+' 120 0)'
        assert expected.count(a)==1
        expected=expected.replace(a,b)
    assert revised==expected,"Unexpected BUCK source modifications"
    for fn in ("01_EFUSE_AUX.kicad_sch","03_PLL_LDO_TCXO.kicad_sch","S3900E_AUX_POWER_V1_5.kicad_sch"):
        assert (OLD_AUX/fn).read_bytes()==(NEW_AUX/fn).read_bytes(),fn
    o=(OLD_ROOT/MASTER).read_text(encoding="utf8")
    n=(NEW_ROOT/MASTER).read_text(encoding="utf8")
    assert n==o.replace("Gerarchico_Alimentazioni_V7.56_TDK_AECQ200_C103_C104_REVIEW_NOT_FOR_FAB","Gerarchico_Alimentazioni_V7.57_TDK_CGA6_VENDOR_LAND_REVIEW_NOT_FOR_FAB")
    for fn in ("sym-lib-table","S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_pro"):
        assert (OLD_ROOT/fn).read_bytes()==(NEW_ROOT/fn).read_bytes()
    x=(OLD_ROOT/"fp-lib-table").read_text()
    y=(NEW_ROOT/"fp-lib-table").read_text()
    assert y.count("S3900E_TDK_CGA6_V757_HOLD")==1
    assert y.count("Librerie_Footprint_V7.57_TDK_CGA6_AECQ200_HOLD")==1
    assert y.replace(next(line for line in y.splitlines(keepends=True) if 'name "S3900E_TDK_CGA6_V757_HOLD"' in line),"")==x
    return True

def geometry():
    import pcbnew
    fp=pcbnew.FootprintLoad(str(FP_DIR),FP_NAME)
    assert fp is not None,"Vendor footprint not loadable via KiCad9"
    p={}
    for pad in fp.Pads():
        p[pad.GetNumber()]=(round(pcbnew.ToMM(pad.GetPosition().x),3),
            round(pcbnew.ToMM(pad.GetPosition().y),3),
            round(pcbnew.ToMM(pad.GetSize().x),3),
            round(pcbnew.ToMM(pad.GetSize().y),3))
    assert p=={"1":(-1.65,0.,1.1,2.2),"2":(1.65,0.,1.1,2.2)},p
    # TDK manufacturer mid-range of CGA6 reflow: A 2–2.4 mm,
    # B 1–1.2 mm, C 1.9–2.5 mm.
    a=p["2"][0]-p["1"][0]-p["1"][2]
    assert 2.0<=a<=2.4 and 1.0<=p["1"][2]<=1.2 and 1.9<=p["1"][3]<=2.5
    return p

def findings(er):
    # No suppression. Normalize only KiCad9's U6202 MCU off-grid
    # attribution on byte-identical MCU; preserve exact warning counts.
    r=re.compile(r'^@\([0-9.]+ mm, [0-9.]+ mm\): Symbol U6202 Pin [0-9]+ \[.+\]')
    def fp(x):
        d=dict(x)
        if (d.get("category")=="endpoint_off_grid" and d.get("sheet")=="/"
          and d.get("severity")=="warning" and len(d.get("locations",[]))==1
          and r.fullmatch(d["locations"][0])):
            d["locations"]=["U6202 unchanged source off-grid attribution"]
        return json.dumps(d,sort_keys=True,ensure_ascii=False)
    return Counter(fp(x) for x in er["findings"])

def gate():
    source_gate()
    pads=geometry()
    a=compmap(OUT/"v757.original.net")
    b=compmap(OUT/"v757.revised.net")
    assert len(a)==len(b)==139
    delta={ref:(a[ref],b[ref]) for ref in a if a[ref]!=b[ref]}
    assert set(delta)=={"C103","C104"},delta
    for ref,(old,new) in delta.items():
        assert old[0]=="Capacitor_SMD:C_1210_3225Metric" and new[0]==FPN
        assert old[1]==new[1]=="22uF 25V X7R"
    assert sum(not v[0] for v in b.values())==0
    n0,n1=nets(OUT/"v757.original.net"),nets(OUT/"v757.revised.net")
    assert len(n0)==len(n1)==102
    before=pinmap(OUT/"v757.original.net")
    after=pinmap(OUT/"v757.revised.net")
    assert before==after,"Electrical graph changed"
    for ref in ("C103","C104"):
        assert {after[(ref,"1")],after[(ref,"2")]}=={
            next(v for v in after.values() if v.endswith("/5V_RF_PREREGULATED")),
            next(v for v in after.values() if v.endswith("/GND_MAIN"))}
    assert after[("U200","8")]==after[("U200","17")]
    assert after[("U200","8")]!=after[("U200","9")]
    assert ("U200","7") not in after
    er0=native_erc(OUT/"v757.original.erc.rpt")
    er1=native_erc(OUT/"v757.revised.erc.rpt")
    assert (er0["errors"],er0["warnings"])==(28,222)
    assert (er1["errors"],er1["warnings"])==(28,222)
    assert er0["categories"]==er1["categories"] and findings(er0)==findings(er1),"Unexpected ERC change"
    report=dict(parts=139,nets=102,footprint_pads=pads,changed=["C103","C104"],
        land_reflow_vendor_ranges_valid=True,physical_land_proven=False,
        DC_bias_capacity_signoff=False,whole_PCB_signed_off=False,
        independent_efuse_recovery=False,NO_FAB=True,NO_TX=True)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v757.land_review.json").write_text(json.dumps(report,indent=2)+"\n")
    return report

class TestV757VendorLand(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=gate()
    def test_01_changed(self):self.assertEqual(self.r["changed"],["C103","C104"])
    def test_02_pad_numbers(self):self.assertEqual(set(self.r["footprint_pads"]),{"1","2"})
    def test_03_pad_spacing(self):self.assertAlmostEqual(self.r["footprint_pads"]["2"][0]-self.r["footprint_pads"]["1"][0],3.3)
    def test_04_pad_width(self):self.assertEqual(self.r["footprint_pads"]["1"][2],1.1)
    def test_05_pad_height(self):self.assertEqual(self.r["footprint_pads"]["1"][3],2.2)
    def test_06_parts(self):self.assertEqual(self.r["parts"],139)
    def test_07_nets(self):self.assertEqual(self.r["nets"],102)
    def test_08_vendor_range(self):self.assertTrue(self.r["land_reflow_vendor_ranges_valid"])
    def test_09_physical_hold(self):self.assertFalse(self.r["physical_land_proven"])
    def test_10_dcbias_hold(self):self.assertFalse(self.r["DC_bias_capacity_signoff"])
    def test_11_board_hold(self):self.assertFalse(self.r["whole_PCB_signed_off"])
    def test_12_recovery_hold(self):self.assertFalse(self.r["independent_efuse_recovery"])
    def test_13_no_fab(self):self.assertTrue(self.r["NO_FAB"] and self.r["NO_TX"])

if __name__=="__main__":
    unittest.main()
