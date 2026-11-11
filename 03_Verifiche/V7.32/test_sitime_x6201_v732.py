"""V7.32 X6201 SiTime vendor land and real KiCad9 before/after proof (NO FAB/TX)."""
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OLDMCU=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.25_SIX_FOOTPRINTS_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
NEWMCU=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.32_SITIME_X6201_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
OLDROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.31_AUX_CONNECTORS_ON_GRID_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
NEWROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.32_SITIME_X6201_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
FPDIR=ROOT/"04_KiCad/Librerie_Footprint_V7.32_SITIME_X6201_HOLD/S3900E_SiTime_Review.pretty"
FPNAME="SiT8008AI_3225_VENDOR_CANDIDATE"
FPID="S3900E_SITIME_3225_V732_HOLD:SiT8008AI_3225_VENDOR_CANDIDATE"
OUT=ROOT/"03_Verifiche/V7.32/output-ci"
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def gate():
    oldsrc=OLDMCU.read_text()
    newsrc=NEWMCU.read_text()
    x0=oldsrc.index('(property "Reference" "X6201"')
    x1=oldsrc.index("(instances ",x0)
    assert oldsrc[x0:x1].count('(property "Footprint" ""')==1
    expected=oldsrc[:x0]+oldsrc[x0:x1].replace('(property "Footprint" ""','(property "Footprint" "'+FPID+'"')+oldsrc[x1:]
    assert newsrc==expected,"Only X6201 field may differ in MCU schematic"
    rt=NEWROOT.read_text()
    assert rt.count("Modulo_MCU_CODEC_V7.32_SITIME_X6201_REVIEW_NOT_FOR_FAB")==1
    assert "Gerarchico_Alimentazioni_V7.31_AUX_CONNECTORS_ON_GRID_NOT_FOR_FAB" in rt
    tbl=(ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.32_SITIME_X6201_REVIEW_NOT_FOR_FAB/fp-lib-table").read_text()
    assert tbl.count('(lib (name "S3900E_SITIME_3225_V732_HOLD")')==1
    assert (ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.32_SITIME_X6201_REVIEW_NOT_FOR_FAB/sym-lib-table").read_bytes()==(ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.31_AUX_CONNECTORS_ON_GRID_NOT_FOR_FAB/sym-lib-table").read_bytes()
    import pcbnew
    ft=pcbnew.FootprintLoad(str(FPDIR),FPNAME)
    assert ft is not None,"KiCad native footprint parser refused X6201"
    pads={p.GetNumber():(
        round(pcbnew.ToMM(p.GetPosition().x),4),
        round(pcbnew.ToMM(p.GetPosition().y),4),
        round(pcbnew.ToMM(p.GetSize().x),4),
        round(pcbnew.ToMM(p.GetSize().y),4)
    ) for p in ft.Pads()}
    required={"1":(-1.1,0.95,1.4,1.2),"2":(1.1,0.95,1.4,1.2),
              "3":(1.1,-0.95,1.4,1.2),"4":(-1.1,-0.95,1.4,1.2)}
    assert pads==required,pads
    symbol=oldsrc[oldsrc.index('(symbol "S3900E:SIT8008_12M288_OE_DRAFT"'):oldsrc.index('(symbol "S3900E:TPS7A2033_DBV_DRAFT"')]
    for no,name in (("1","OE"),("2","GND"),("3","OUT"),("4","VDD")):
        assert '(name "'+name+'"' in symbol and '(number "'+no+'"' in symbol
    c0=compmap(OUT/"v732.original.net");c1=compmap(OUT/"v732.revised.net")
    assert len(c0)==len(c1)==132
    delta={k:(c0[k],c1[k]) for k in c0 if c0[k]!=c1[k]}
    assert list(delta)==["X6201"],delta
    assert delta["X6201"][0][0]=="" and delta["X6201"][1][0]==FPID
    assert delta["X6201"][0][1]==delta["X6201"][1][1]=="SiT8008AI-22-33E-12.288000"
    missing0=sum(not x[0] for x in c0.values())
    missing1=sum(not x[0] for x in c1.values())
    assert (missing0,missing1)==(42,41),(missing0,missing1)
    net0=nets(OUT/"v732.original.net");net1=nets(OUT/"v732.revised.net")
    assert len(net0)==100 and net0==net1,"Pin-net delta not permitted"
    erc0=native_erc(OUT/"v732.original.erc.rpt")
    erc1=native_erc(OUT/"v732.revised.erc.rpt")
    assert (erc0["errors"],erc0["warnings"])==(36,218),erc0
    assert (erc1["errors"],erc1["warnings"])==(36,218),erc1
    rept0=(OUT/"v732.original.erc.rpt").read_text()
    rept1=(OUT/"v732.revised.erc.rpt").read_text()
    for rule in ("label_dangling","power_pin_not_driven","pin_not_driven","endpoint_off_grid","footprint_link_issues","lib_symbol_issues"):
        assert rept0.count("["+rule+"]")==rept1.count("["+rule+"]"),rule
    assert rept0.count("[endpoint_off_grid]")==217
    result={"revision":"V7.32","component":"X6201","mpn":"SiT8008AI-22-33E-12.288000",
        "vendor_review_only":True,"native_KiCad9":True,"footprint":FPID,
        "pads_mm":pads,"components":132,"nets":100,"pin_net_delta":0,
        "footprint_delta":["X6201"],"missing_footprints_before":42,"missing_footprints_after":41,
        "erc_before":[36,218],"erc_after":[36,218],"crossdomain_OPEN_HOLD":15,
        "SG48_HOLD":True,"PCB_complete":False,"NO_FAB":True,"NO_TX":True}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v732.sitime_native.json").write_text(json.dumps(result,indent=2)+"\n")
    return result

class TestSiTimeX6201(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=gate()
    def test_01_vendor_pads(self):self.assertEqual(len(self.data["pads_mm"]),4)
    def test_02_correct_mpn(self):self.assertEqual(self.data["mpn"],"SiT8008AI-22-33E-12.288000")
    def test_03_only_x6201_changed(self):self.assertEqual(self.data["footprint_delta"],["X6201"])
    def test_04_components(self):self.assertEqual(self.data["components"],132)
    def test_05_nets(self):self.assertEqual((self.data["nets"],self.data["pin_net_delta"]),(100,0))
    def test_06_one_footprint_more(self):self.assertEqual((self.data["missing_footprints_before"],self.data["missing_footprints_after"]),(42,41))
    def test_07_erc_counts(self):self.assertEqual(self.data["erc_before"],self.data["erc_after"])
    def test_08_no_error_waiver(self):self.assertEqual(self.data["erc_after"][0],36)
    def test_09_crossdomain_HOLD(self):self.assertEqual(self.data["crossdomain_OPEN_HOLD"],15)
    def test_10_no_fab_tx(self):self.assertTrue(self.data["NO_FAB"] and self.data["NO_TX"] and not self.data["PCB_complete"] and self.data["SG48_HOLD"])
if __name__=="__main__":unittest.main()
