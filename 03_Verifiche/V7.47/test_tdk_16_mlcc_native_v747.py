"""V7.47: native KiCad9 16 TDK 1uF/10uF footprint assignments, strict source parity.
Does NOT approve effective capacitance/stability or fabrication.
"""
import json,re,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche/V7.47/output-ci"
OLDROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.46_12_MURATA_GRM15_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
NEWROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.47_TDK_16_MLCC_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
OLDMCU=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.46_12_MURATA_GRM15_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
NEWMCU=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.47_TDK_16_MLCC_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
FPDIR=ROOT/"04_KiCad/Librerie_Footprint_V7.47_TDK_MLCC_HOLD/S3900E_TDK_MLCC_Review.pretty"
LIB="S3900E_TDK_MLCC_V747_HOLD"
REF_1=("C6213","C6215","C6216","C6218","C6221","C6222","C6223","C6224","C6225","C6226","C6229")
REF_10=("C6202","C6204","C6206","C6208","C6219")
CONFIG={
 "1uF":{"refs":REF_1,"name":"TDK_C1608_0603_1UF_REFLOW_REVIEW",
         "mpn":"C1608X7R1C105K080AC",
         "pads":{"1":(-.7,0.,.7,.7),"2":(.7,0.,.7,.7)},
         "vendor_land_reflow_A_B_C_mm":(.7,.7,.7),
         "voltage_v":16},
 "10uF":{"refs":REF_10,"name":"TDK_C2012_0805_10UF_REFLOW_REVIEW",
          "mpn":"C2012X7R1A106K125AC",
          "pads":{"1":(-.9,0.,.8,1.),"2":(.9,0.,.8,1.)},
          "vendor_land_reflow_A_B_C_mm":(1.,.8,1.),
          "voltage_v":10}
}
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def source_gate():
    src=OLDMCU.read_text(encoding="utf8")
    actual=NEWMCU.read_text(encoding="utf8")
    expected=src
    for val,cfg in CONFIG.items():
        for ref in cfg["refs"]:
            a=expected.index('(property "Reference" "'+ref+'"')
            e=expected.index("(instances ",a)
            block=expected[a:e]
            assert '(property "Value" "'+val+'"' in block,(ref,val)
            assert '(property "Footprint" ""' in block,ref
            m=re.search(r'(\(property "Footprint" "" \(at ([\d.]+) ([\d.]+) 0\) \(effects \(font \(size [^)]+\)\) \(hide yes\)\)\)\n)',block)
            assert m,(ref,block[:300])
            old=m[1]
            changed=old.replace('(property "Footprint" ""','(property "Footprint" "'+LIB+':'+cfg["name"]+'"')
            changed+='    (property "MPN" "'+cfg["mpn"]+'" (at '+m[2]+' '+m[3]+' 0) (effects (font (size 1 1)) (hide yes)))\n'
            expected=expected[:a]+block.replace(old,changed)+expected[e:]
    assert expected==actual,"Any CAD change beyond 16 footprint/MPN assignments forbidden"
    assert NEWROOT.read_text().count("../Modulo_MCU_CODEC_V7.47_TDK_16_MLCC_REVIEW_NOT_FOR_FAB/")==1
    assert NEWROOT.read_text().count("(sheet (at ")==3
    libtable=(NEWROOT.parent/"fp-lib-table").read_text()
    assert libtable.count('(lib (name "'+LIB+'")')==1

def native_gate():
    source_gate()
    import pcbnew
    pads={}
    for val,cfg in CONFIG.items():
        fp=pcbnew.FootprintLoad(str(FPDIR),cfg["name"])
        assert fp is not None,(val,cfg["name"])
        p={a.GetNumber():(round(pcbnew.ToMM(a.GetPosition().x),4),
                           round(pcbnew.ToMM(a.GetPosition().y),4),
                           round(pcbnew.ToMM(a.GetSize().x),4),
                           round(pcbnew.ToMM(a.GetSize().y),4)) for a in fp.Pads()}
        assert p==cfg["pads"],(val,p)
        gap=round(p["2"][0]-p["2"][2]/2 -(p["1"][0]+p["1"][2]/2),4)
        assert abs(gap-cfg["vendor_land_reflow_A_B_C_mm"][0])<1e-5,(val,gap)
        pads[val]=p
    c0=compmap(OUT/"v747.original.net")
    c1=compmap(OUT/"v747.revised.net")
    assert len(c0)==len(c1)==134,(len(c0),len(c1))
    delta={ref:(c0[ref],c1[ref]) for ref in c0 if c0[ref]!=c1[ref]}
    assert set(delta)==set(REF_1)|set(REF_10),(len(delta),delta)
    for val,cfg in CONFIG.items():
        for ref in cfg["refs"]:
            assert delta[ref]==(("",val),(LIB+":"+cfg["name"],val)),(ref,delta[ref])
    missing=(sum(not v[0] for v in c0.values()),sum(not v[0] for v in c1.values()))
    assert missing==(20,4),missing
    n0=nets(OUT/"v747.original.net")
    n1=nets(OUT/"v747.revised.net")
    assert len(n0)==len(n1)==101 and n0==n1,"Any pin/net change forbidden"
    e0=native_erc(OUT/"v747.original.erc.rpt")
    e1=native_erc(OUT/"v747.revised.erc.rpt")
    assert (e0["errors"],e0["warnings"])==(36,221),e0
    assert e1["errors"]<=e0["errors"],e1
    for cat in ("pin_to_pin","pin_not_driven","power_pin_not_driven","wire_dangling","pin_not_connected"):
        assert e1["categories"].get(cat,0)<=e0["categories"].get(cat,0),(cat,e0,e1)
    assert e1["warnings"]<=e0["warnings"]+2,(e0,e1)
    result={"revision":"V7.47","parts":134,"nets":101,"changed_nets":0,
        "changed_footprints":sorted(delta),"missing_before":20,"missing_after":4,
        "erc_before":{"errors":e0["errors"],"warnings":e0["warnings"]},
        "erc_after":{"errors":e1["errors"],"warnings":e1["warnings"]},
        "native_pad_geometry":pads,"effective_capacitance_worst_case_validated":False,
        "tps7a20_stability_validated":False,"codec_rail_loads_validated":False,
        "NO_FAB":True,"NO_GERBER":True,"NO_TX":True}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v747.audit.json").write_text(json.dumps(result,indent=2)+"\n")
    return result

class TestTDK16Caps(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.d=native_gate()
    def test_01_exact_16(self):self.assertEqual(len(self.d["changed_footprints"]),16)
    def test_02_11_and_5(self):self.assertEqual((len(REF_1),len(REF_10)),(11,5))
    def test_03_parts_unchanged(self):self.assertEqual(self.d["parts"],134)
    def test_04_nets_unchanged(self):self.assertEqual((self.d["nets"],self.d["changed_nets"]),(101,0))
    def test_05_missing_drop_to_four(self):self.assertEqual((self.d["missing_before"],self.d["missing_after"]),(20,4))
    def test_06_2_pad_vendor_size_0603(self):self.assertEqual(len(self.d["native_pad_geometry"]["1uF"]),2)
    def test_07_2_pad_vendor_size_0805(self):self.assertEqual(len(self.d["native_pad_geometry"]["10uF"]),2)
    def test_08_erc_no_increase(self):self.assertLessEqual(self.d["erc_after"]["errors"],36)
    def test_09_effective_capacitance_not_signed_off(self):self.assertFalse(self.d["effective_capacitance_worst_case_validated"])
    def test_10_LDO_stability_not_signed_off(self):self.assertFalse(self.d["tps7a20_stability_validated"])
    def test_11_codec_load_not_signed_off(self):self.assertFalse(self.d["codec_rail_loads_validated"])
    def test_12_fab_gerber_tx_hold(self):self.assertTrue(self.d["NO_FAB"] and self.d["NO_GERBER"] and self.d["NO_TX"])
if __name__=="__main__":unittest.main()
