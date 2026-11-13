"""V7.48 native KiCad9 strict 2 C0G MLCC footprint parity, NO FAB/TX."""
import json,re,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche/V7.48/output-ci"
OLDROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.47_TDK_16_MLCC_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
NEWROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.48_TDK_2_C0G_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
OLDMCU=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.47_TDK_16_MLCC_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
NEWMCU=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.48_TDK_2_C0G_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
FPID="S3900E_TDK_C0G_V748_HOLD:TDK_C1608_0603_C0G_REFLOW_REVIEW"
DIR=ROOT/"04_KiCad/Librerie_Footprint_V7.48_TDK_C0G_HOLD/S3900E_TDK_C0G_Review.pretty"
PARTS={"C6228":("4.7nF","C1608C0G1H472J080AA"),"C6230":("10nF","C1608C0G1H103J080AA")}
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def audit():
    old=OLDMCU.read_text(encoding="utf8")
    new=NEWMCU.read_text(encoding="utf8")
    expected=old
    for ref,(val,mpn) in PARTS.items():
        a=expected.index('(property "Reference" "'+ref+'"')
        e=expected.index("(instances ",a)
        block=expected[a:e]
        assert '(property "Value" "'+val+'"' in block
        assert '(property "Footprint" ""' in block
        m=re.search(r'(\(property "Footprint" "" \(at ([\d.]+) ([\d.]+) 0\) \(effects \(font \(size [^)]+\)\) \(hide yes\)\)\)\n)',block)
        assert m,(ref,block)
        change=m[1].replace('(property "Footprint" ""','(property "Footprint" "'+FPID+'"')
        change+='    (property "MPN" "'+mpn+'" (at '+m[2]+' '+m[3]+' 0) (effects (font (size 1 1)) (hide yes)))\n'
        expected=expected[:a]+block.replace(m[1],change)+expected[e:]
    assert new==expected,"Any change beyond two footprint+MPN properties forbidden"
    assert NEWROOT.read_text().count("../Modulo_MCU_CODEC_V7.48_TDK_2_C0G_REVIEW_NOT_FOR_FAB/")==1
    assert NEWROOT.read_text().count("(sheet (at ")==3
    assert (NEWROOT.parent/"fp-lib-table").read_text().count('(lib (name "S3900E_TDK_C0G_V748_HOLD")')==1
    import pcbnew
    fp=pcbnew.FootprintLoad(str(DIR),"TDK_C1608_0603_C0G_REFLOW_REVIEW")
    assert fp is not None
    pads={p.GetNumber():(round(pcbnew.ToMM(p.GetPosition().x),4),
        round(pcbnew.ToMM(p.GetPosition().y),4),
        round(pcbnew.ToMM(p.GetSize().x),4),
        round(pcbnew.ToMM(p.GetSize().y),4)) for p in fp.Pads()}
    assert pads=={"1":(-.7,0.,.7,.7),"2":(.7,0.,.7,.7)},pads
    c0,c1=compmap(OUT/"v748.original.net"),compmap(OUT/"v748.revised.net")
    assert len(c0)==len(c1)==134
    changed={ref:(c0[ref],c1[ref]) for ref in c0 if c0[ref]!=c1[ref]}
    assert set(changed)==set(PARTS),changed
    for ref,(val,mpn) in PARTS.items():
        assert changed[ref]==(("",val),(FPID,val)),changed[ref]
    missing=(sum(not v[0] for v in c0.values()),sum(not v[0] for v in c1.values()))
    assert missing==(4,2),missing
    n0,n1=nets(OUT/"v748.original.net"),nets(OUT/"v748.revised.net")
    assert len(n0)==len(n1)==101 and n0==n1,"Pin-net membership changed"
    e0,e1=native_erc(OUT/"v748.original.erc.rpt"),native_erc(OUT/"v748.revised.erc.rpt")
    assert (e0["errors"],e0["warnings"])==(36,221),e0
    assert e1["errors"]<=e0["errors"]
    assert e1["warnings"]<=e0["warnings"]+2
    for cat in ("pin_to_pin","pin_not_driven","power_pin_not_driven","wire_dangling","pin_not_connected"):
        assert e1["categories"].get(cat,0)<=e0["categories"].get(cat,0),cat
    result={"revision":"V7.48","parts":134,"nets":101,"changed_footprints":sorted(changed),
            "missing_before":4,"missing_after":2,"vendor_pads_mm":pads,
            "erc_before":{"errors":e0["errors"],"warnings":e0["warnings"]},
            "erc_after":{"errors":e1["errors"],"warnings":e1["warnings"]},
            "filter_response_validated":False,"circuit_electrical_validation":False,
            "NO_FAB":True,"NO_GERBER":True,"NO_TX":True}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v748.audit.json").write_text(json.dumps(result,indent=2)+"\n")
    return result
class TestC0GTwo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=audit()
    def test_01_only_two_caps(self):self.assertEqual(len(self.r["changed_footprints"]),2)
    def test_02_nets(self):self.assertEqual(self.r["nets"],101)
    def test_03_parts(self):self.assertEqual(self.r["parts"],134)
    def test_04_missing_reduced(self):self.assertEqual((self.r["missing_before"],self.r["missing_after"]),(4,2))
    def test_05_two_pads_native(self):self.assertEqual(len(self.r["vendor_pads_mm"]),2)
    def test_06_erc_no_growth(self):self.assertLessEqual(self.r["erc_after"]["errors"],36)
    def test_07_no_fake_filter_signoff(self):self.assertFalse(self.r["filter_response_validated"])
    def test_08_no_fab(self):self.assertTrue(all(self.r[v] for v in ("NO_FAB","NO_GERBER","NO_TX")))
if __name__=="__main__":unittest.main()
