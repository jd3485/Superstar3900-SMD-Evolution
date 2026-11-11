"""V7.33 Yageo eight MCU resistors manufacturer 0402 reflow footprint native gate."""
import json,sys,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OLDMCU=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.32_SITIME_X6201_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch";NEWMCU=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.33_YAGEO_8R_0402_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
OLDROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.32_SITIME_X6201_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch";NEWROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.33_YAGEO_8R_0402_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
OUT=ROOT/"03_Verifiche/V7.33/output-ci"
FPID="S3900E_YAGEO_0402_V733_HOLD:YAGEO_RC0402_REFLOW_VENDOR_CANDIDATE"
FPDIR=ROOT/"04_KiCad/Librerie_Footprint_V7.33_YAGEO_0402_HOLD/S3900E_Yageo_Review.pretty"
FPNAME="YAGEO_RC0402_REFLOW_VENDOR_CANDIDATE"
PARTS={
"R6201":("47k","RC0402FR-0747KL"),
"R6202":("4.7k","RC0402FR-074K7L"),
"R6203":("4.7k","RC0402FR-074K7L"),
"R6204":("4.7k","RC0402FR-074K7L"),
"R6205":("33R","RC0402FR-0733RL"),
"R6206":("4.7k","RC0402FR-074K7L"),
"R6207":("1k","RC0402FR-071KL"),
"R6208":("1k","RC0402FR-071KL"),
}
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc
def gate():
    src=OLDMCU.read_text();actual=NEWMCU.read_text()
    expected=src
    for ref,(val,mpn) in PARTS.items():
        st=expected.index('(property "Reference" "'+ref+'"')
        en=expected.index("(instances ",st)
        old=expected[st:en]
        assert '(property "Value" "'+val+'"' in old,ref
        assert '(property "Footprint" ""' in old,ref
        match=re.search(r'\(property "Footprint" "" \(at ([^)]*)\) ',old)
        assert match is not None,ref
        coords=match.group(1)
        replacement=old.replace('(property "Footprint" ""','(property "Footprint" "'+FPID+'"')
        replacement=re.sub(r'(\(property "Footprint" "[^"]+"[^\n]*\n)',
            lambda m: m.group(1)+'    (property "MPN" "'+mpn+'" (at '+coords+') (effects (font (size 1 1)) (hide yes)))\n',
            replacement,count=1)
        expected=expected[:st]+replacement+expected[en:]
    assert actual==expected,"Only 8 explicit resistor MPN+Footprint fields allowed"
    rt=NEWROOT.read_text()
    assert rt.count("Modulo_MCU_CODEC_V7.33_YAGEO_8R_0402_REVIEW_NOT_FOR_FAB")==1
    assert "Gerarchico_Alimentazioni_V7.31_AUX_CONNECTORS_ON_GRID_NOT_FOR_FAB" in rt
    table=(ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.33_YAGEO_8R_0402_REVIEW_NOT_FOR_FAB/fp-lib-table").read_text()
    assert table.count('(lib (name "S3900E_YAGEO_0402_V733_HOLD")')==1
    assert (ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.33_YAGEO_8R_0402_REVIEW_NOT_FOR_FAB/sym-lib-table").read_bytes()==(ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.32_SITIME_X6201_REVIEW_NOT_FOR_FAB/sym-lib-table").read_bytes()
    import pcbnew
    foot=pcbnew.FootprintLoad(str(FPDIR),FPNAME)
    assert foot is not None,"Native KiCad refused Yageo footprint"
    pads={p.GetNumber():(
      round(pcbnew.ToMM(p.GetPosition().x),4),
      round(pcbnew.ToMM(p.GetPosition().y),4),
      round(pcbnew.ToMM(p.GetSize().x),4),
      round(pcbnew.ToMM(p.GetSize().y),4)) for p in foot.Pads()}
    assert pads=={"1":(-0.5,0.0,0.5,0.6),"2":(0.5,0.0,0.5,0.6)},pads
    c0=compmap(OUT/"v733.original.net");c1=compmap(OUT/"v733.revised.net")
    assert len(c0)==len(c1)==132
    delta={k:(c0[k],c1[k]) for k in c0 if c0[k]!=c1[k]}
    assert set(delta)==set(PARTS),delta
    for ref,(val,mpn) in PARTS.items():
        old,new=delta[ref]
        assert old[0]=="" and new[0]==FPID and old[1]==new[1]==val,(ref,old,new)
        assert '(property "MPN" "'+mpn+'"' in actual
    oldmissing=sum(not x[0] for x in c0.values())
    newmissing=sum(not x[0] for x in c1.values())
    assert (oldmissing,newmissing)==(41,33),(oldmissing,newmissing)
    net0=nets(OUT/"v733.original.net");net1=nets(OUT/"v733.revised.net")
    assert len(net0)==100 and net0==net1,"Any net node delta BLOCKS merge"
    erc0=native_erc(OUT/"v733.original.erc.rpt")
    erc1=native_erc(OUT/"v733.revised.erc.rpt")
    assert (erc0["errors"],erc0["warnings"])==(36,218),erc0
    assert (erc1["errors"],erc1["warnings"])==(36,218),erc1
    rep0=(OUT/"v733.original.erc.rpt").read_text()
    rep1=(OUT/"v733.revised.erc.rpt").read_text()
    for rule in ("label_dangling","power_pin_not_driven","pin_not_driven","endpoint_off_grid","footprint_link_issues","lib_symbol_issues"):
        assert rep0.count("["+rule+"]")==rep1.count("["+rule+"]"),rule
    result={"revision":"V7.33","native_KiCad9":True,"R_refs":sorted(PARTS),"Mpn_mapping":{k:v[1] for k,v in PARTS.items()},
      "footprint":FPID,"pad_geometry_mm":pads,"components":132,"nets":100,"pin_net_delta":0,
      "changed_footprint_fields":8,"missing_footprints_before":41,"missing_footprints_after":33,
      "erc_before":[36,218],"erc_after":[36,218],
      "Yageo_nominal_rating_mW_at_70C":63,"R6205_fault_case_not_qualified":True,
      "15_crossdomain_OPEN_HOLD":True,"SG48_HOLD":True,"PCB_complete":False,"NO_FAB":True,"NO_TX":True}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v733.yageo_native.json").write_text(json.dumps(result,indent=2)+"\n")
    return result
class TestYageoEightResistors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.d=gate()
    def test_01_eight_mpn(self):self.assertEqual(len(self.d["R_refs"]),8)
    def test_02_four_vendor_mpns(self):self.assertEqual(len(set(self.d["Mpn_mapping"].values())),4)
    def test_03_two_native_vendor_pads(self):self.assertEqual(len(self.d["pad_geometry_mm"]),2)
    def test_04_132_components(self):self.assertEqual(self.d["components"],132)
    def test_05_100_nets_zero_delta(self):self.assertEqual((self.d["nets"],self.d["pin_net_delta"]),(100,0))
    def test_06_eight_footprints_added(self):self.assertEqual((self.d["missing_footprints_before"],self.d["missing_footprints_after"]),(41,33))
    def test_07_erc_counts_unchanged(self):self.assertEqual(self.d["erc_before"],self.d["erc_after"])
    def test_08_errors_not_waived(self):self.assertEqual(self.d["erc_after"][0],36)
    def test_09_open_hold(self):self.assertTrue(self.d["15_crossdomain_OPEN_HOLD"] and self.d["R6205_fault_case_not_qualified"])
    def test_10_no_fab_tx(self):self.assertTrue(self.d["NO_FAB"] and self.d["NO_TX"] and self.d["SG48_HOLD"] and not self.d["PCB_complete"])
if __name__=="__main__":unittest.main()
