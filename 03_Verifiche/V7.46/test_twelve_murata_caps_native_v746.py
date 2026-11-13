"""V7.46: native KiCad9 parity: 12 Murata 100nF 0402 bypass footprints only.
No net or symbol value changes. Review footprints do NOT qualify Ceff or DFM.
"""
import json,re,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche/V7.46/output-ci"
OLDROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.41_FB6201_TDK_VENDOR_LAND_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
NEWROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.46_12_MURATA_GRM15_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
OLDMCU=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.41_FB6201_TDK_VENDOR_LAND_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
NEWMCU=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.46_12_MURATA_GRM15_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
FPID="S3900E_MURATA_GRM15_V736_HOLD:MURATA_GRM15_0402_REFLOW_REVIEW"
MPN="GRM155R71C104KA88D"
FPDIR=ROOT/"04_KiCad/Librerie_Footprint_V7.36_MURATA_GRM15_HOLD/S3900E_Murata_Review.pretty"
REFS=("C6201","C6203","C6205","C6207","C6209","C6210","C6211","C6212","C6214","C6217","C6220","C6227")
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def expected_source():
    old=OLDMCU.read_text(encoding="utf8")
    new=NEWMCU.read_text(encoding="utf8")
    expected=old
    for ref in REFS:
        a=expected.index('(property "Reference" "'+ref+'"')
        e=expected.index("(instances ",a)
        block=expected[a:e]
        assert '(property "Value" "100nF"' in block
        assert '(property "Footprint" ""' in block
        match=re.search(r'(\(property "Footprint" "" \(at ([\d.]+) ([\d.]+) 0\) \(effects \(font \(size [^)]+\)\) \(hide yes\)\)\)\n)',block)
        assert match,(ref,block)
        previous=match[1]
        replacement=previous.replace('(property "Footprint" ""','(property "Footprint" "'+FPID+'"')
        replacement+='    (property "MPN" "'+MPN+'" (at '+match[2]+' '+match[3]+' 0) (effects (font (size 1 1)) (hide yes)))\n'
        expected=expected[:a]+block.replace(previous,replacement)+expected[e:]
    assert new==expected,"Only 12 Murata footprints and hidden MPN properties allowed"
    root=NEWROOT.read_text(encoding="utf8")
    assert root.count("../Modulo_MCU_CODEC_V7.46_12_MURATA_GRM15_REVIEW_NOT_FOR_FAB/")==1
    assert root.count("(sheet (at ")==3
    table=(NEWROOT.parent/"fp-lib-table").read_text(encoding="utf8")
    assert table.count('(lib (name "S3900E_MURATA_GRM15_V736_HOLD")')==1

def audit():
    expected_source()
    import pcbnew
    foot=pcbnew.FootprintLoad(str(FPDIR),"MURATA_GRM15_0402_REFLOW_REVIEW")
    assert foot is not None
    pads={p.GetNumber():(round(pcbnew.ToMM(p.GetPosition().x),4),
          round(pcbnew.ToMM(p.GetPosition().y),4),
          round(pcbnew.ToMM(p.GetSize().x),4),
          round(pcbnew.ToMM(p.GetSize().y),4)) for p in foot.Pads()}
    assert pads=={"1":(-.4,0.,.4,.5),"2":(.4,0.,.4,.5)},pads
    c0,c1=(compmap(OUT/f) for f in ("v746.original.net","v746.revised.net"))
    assert len(c0)==len(c1)==134
    delta={ref:(c0[ref],c1[ref]) for ref in c0 if c0[ref]!=c1[ref]}
    assert set(delta)==set(REFS),delta
    for ref in REFS:
        assert delta[ref]==(("", "100nF"),(FPID,"100nF")),(ref,delta[ref])
    missing=(sum(not v[0] for v in c0.values()),sum(not v[0] for v in c1.values()))
    assert missing==(32,20),missing
    n0=nets(OUT/"v746.original.net")
    n1=nets(OUT/"v746.revised.net")
    assert len(n0)==len(n1)==101 and n0==n1,"Unexpected electrical pin/net change"
    e0=native_erc(OUT/"v746.original.erc.rpt")
    e1=native_erc(OUT/"v746.revised.erc.rpt")
    assert (e0["errors"],e0["warnings"])==(36,221),e0
    assert e1["errors"]<=e0["errors"],(e0,e1)
    for cat in ("pin_to_pin","pin_not_driven","power_pin_not_driven","wire_dangling","pin_not_connected"):
        assert e1["categories"].get(cat,0)<=e0["categories"].get(cat,0),(cat,e0,e1)
    assert e1["warnings"]<=e0["warnings"]+2,(e0,e1)
    result={"revision":"V7.46","parts":134,"nets":101,"changed_nets":0,
            "changed_footprints":sorted(delta),"missing_before":32,"missing_after":20,
            "erc_before":{"errors":e0["errors"],"warnings":e0["warnings"]},
            "erc_after":{"errors":e1["errors"],"warnings":e1["warnings"]},
            "murata_pads_mm":pads,"effective_capacitance_qualified":False,
            "layout_drc_qualified":False,"NO_FAB":True,"NO_GERBER":True,"NO_TX":True}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v746.audit.json").write_text(json.dumps(result,indent=2)+"\n")
    return result
class TestMurataTwelve(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=audit()
    def test_01_exact_twelve_caps(self):self.assertEqual(len(cls_refs:=self.r["changed_footprints"]),12)
    def test_02_nets_intact(self):self.assertEqual((self.r["nets"],self.r["changed_nets"]),(101,0))
    def test_03_parts_intact(self):self.assertEqual(self.r["parts"],134)
    def test_04_footprint_missing_reduced(self):self.assertEqual((self.r["missing_before"],self.r["missing_after"]),(32,20))
    def test_05_kicad_vendor_pads_two(self):self.assertEqual(len(self.r["murata_pads_mm"]),2)
    def test_06_erc_no_new_errors(self):self.assertLessEqual(self.r["erc_after"]["errors"],36)
    def test_07_effective_c_not_qualified(self):self.assertFalse(self.r["effective_capacitance_qualified"])
    def test_08_no_fab_gerber_tx(self):self.assertTrue(all(self.r[k] for k in ("NO_FAB","NO_GERBER","NO_TX")))
if __name__=="__main__":unittest.main()
