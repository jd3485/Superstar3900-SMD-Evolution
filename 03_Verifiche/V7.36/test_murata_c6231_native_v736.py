"""V7.36 Murata GRM15 C6231 source-only ECO and native KiCad9 7-sheet parity gate.
The vendor land and MPN remain REVIEW/NO FAB; Ceff(3.3 V) worst case not established.
"""
import json,re,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche/V7.36/output-ci"
OLDROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.35_TPS3840_DBV5_VENDOR_LAND_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
NEWROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.36_C6231_MURATA_GRM15_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
OLDMCU=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.35_TPS3840_DBV5_VENDOR_LAND_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
NEWMCU=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.36_C6231_MURATA_GRM15_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
FPID="S3900E_MURATA_GRM15_V736_HOLD:MURATA_GRM15_0402_REFLOW_REVIEW"
MPN="GRM155R71C104KA88D"
FPDIR=ROOT/"04_KiCad/Librerie_Footprint_V7.36_MURATA_GRM15_HOLD/S3900E_Murata_Review.pretty"
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def gate():
    old=OLDMCU.read_text(encoding="utf8")
    new=NEWMCU.read_text(encoding="utf8")
    anchor='(property "Reference" "C6231"'
    assert old.count(anchor)==new.count(anchor)==1
    a=old.index(anchor);e=old.index("(instances ",a)
    orig=old[a:e]
    assert '(property "Value" "100nF"' in orig
    assert '(property "Footprint" ""' in orig
    m=re.search(r'(\(property "Footprint" ""[^\n]*\n)',orig)
    assert m
    rep=orig.replace(m.group(1),m.group(1).replace('(property "Footprint" ""','(property "Footprint" "'+FPID+'"')+'    (property "MPN" "'+MPN+'" (at 1050.0000 415.0000 0) (effects (font (size 1 1)) (hide yes)))\n',1)
    assert old[:a]+rep+old[e:]==new,"Only C6231 footprint + hidden MPN may change"
    assert NEWROOT.read_text().count("../Modulo_MCU_CODEC_V7.36_C6231_MURATA_GRM15_REVIEW_NOT_FOR_FAB/")==1
    table=(NEWROOT.parent/"fp-lib-table").read_text()
    assert table.count('(lib (name "S3900E_MURATA_GRM15_V736_HOLD")')==1
    import pcbnew
    foot=pcbnew.FootprintLoad(str(FPDIR),"MURATA_GRM15_0402_REFLOW_REVIEW")
    assert foot is not None,"native KiCad cannot load Murata land"
    pads={p.GetNumber():(round(pcbnew.ToMM(p.GetPosition().x),4),round(pcbnew.ToMM(p.GetPosition().y),4),round(pcbnew.ToMM(p.GetSize().x),4),round(pcbnew.ToMM(p.GetSize().y),4)) for p in foot.Pads()}
    assert pads=={"1":(-0.40,0.0,0.40,0.50),"2":(0.40,0.0,0.40,0.50)},pads
    c0=compmap(OUT/"v736.original.net");c1=compmap(OUT/"v736.revised.net")
    assert len(c0)==len(c1)==134
    delta={k:(c0[k],c1[k]) for k in c0 if c0[k]!=c1[k]}
    assert delta=={"C6231":(("","100nF"),(FPID,"100nF"))},delta
    missing=(sum(not z[0] for z in c0.values()),sum(not z[0] for z in c1.values()))
    assert missing==(34,33),missing
    n0=nets(OUT/"v736.original.net");n1=nets(OUT/"v736.revised.net")
    assert len(n0)==len(n1)==101 and n0==n1,"Unexpected pin-net delta"
    er0=native_erc(OUT/"v736.original.erc.rpt")
    er1=native_erc(OUT/"v736.revised.erc.rpt")
    assert (er0["errors"],er0["warnings"])==(36,221),er0
    assert er1["errors"]<=er0["errors"],er1
    for rule in ("pin_to_pin","pin_not_driven","power_pin_not_driven","wire_dangling","pin_not_connected"):
        assert er1["categories"].get(rule,0)<=er0["categories"].get(rule,0),(rule,er0,er1)
    assert er1["warnings"]<=er0["warnings"]+2,(er0,er1)
    result={"revision":"V7.36","MPN":MPN,"pads":pads,"components":134,"nets":101,"pin_net_delta":0,"changed_footprint":["C6231"],"missing_before":34,"missing_after":33,"erc_before":er0,"erc_after":er1,"actual_Ceff_at_3V3_qualified":False,"PCB_complete":False,"NO_FAB":True,"NO_TX":True}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v736.native.json").write_text(json.dumps(result,indent=2,default=str)+"\n")
    return result

class TestMurataC6231(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.d=gate()
    def test_01_two_pads_vendor(self):self.assertEqual(len(self.d["pads"]),2)
    def test_02_only_C6231(self):self.assertEqual(self.d["changed_footprint"],["C6231"])
    def test_03_netlist_same(self):self.assertEqual((self.d["nets"],self.d["pin_net_delta"]),(101,0))
    def test_04_missing_33(self):self.assertEqual((self.d["missing_before"],self.d["missing_after"]),(34,33))
    def test_05_erc_no_new_error(self):self.assertLessEqual(self.d["erc_after"]["errors"],36)
    def test_06_murata_Ceff_hold(self):self.assertFalse(self.d["actual_Ceff_at_3V3_qualified"])
    def test_07_no_fab_tx(self):self.assertTrue(self.d["NO_FAB"] and self.d["NO_TX"] and not self.d["PCB_complete"])

if __name__=="__main__":unittest.main()
