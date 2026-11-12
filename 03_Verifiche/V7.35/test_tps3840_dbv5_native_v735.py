"""V7.35 TI DBV0005A land geometry and seven-sheet native KiCad9 gate.
Vendor footprint is a REVIEW candidate; no assembly/DRC/hardware signoff.
"""
import json,re,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche/V7.35/output-ci"
OLDROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.34_TPS3840_IOVDD_SEQUENCE_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
NEWROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.35_TPS3840_DBV5_VENDOR_LAND_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
OLDMCU=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.34_TPS3840_IOVDD_SEQUENCE_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
NEWMCU=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.35_TPS3840_DBV5_VENDOR_LAND_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
FPID="S3900E_TPS3840_DBV5_V735_HOLD:TI_DBV0005A_5PAD_REFLOW_REVIEW"
FPDIR=ROOT/"04_KiCad/Librerie_Footprint_V7.35_TI_TPS3840_DBV5_HOLD/S3900E_TPS3840_Review.pretty"
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

EXPECTED_PADS={
 "1":(-1.30,-0.95,1.10,0.60),
 "2":(-1.30,0.00,1.10,0.60),
 "3":(-1.30,0.95,1.10,0.60),
 "4":(1.30,0.95,1.10,0.60),
 "5":(1.30,-0.95,1.10,0.60),
}

def gate():
    old=OLDMCU.read_text(encoding="utf-8")
    new=NEWMCU.read_text(encoding="utf-8")
    assert old.count('(property "Reference" "U6207"')==1
    a=old.index('(property "Reference" "U6207"')
    e=old.index('(instances ',a)
    orig=old[a:e]
    assert '(property "Value" "TPS3840PL30DBVR"' in orig
    assert '(property "Footprint" ""' in orig
    desired=old[:a]+orig.replace('(property "Footprint" ""','(property "Footprint" "'+FPID+'"')+old[e:]
    assert desired==new,"Only U6207 footprint property may change in MCU schematic"
    assert NEWROOT.read_text().count("Modulo_MCU_CODEC_V7.35_TPS3840_DBV5_VENDOR_LAND_REVIEW_NOT_FOR_FAB")==1
    assert "Modulo_MCU_CODEC_V7.34_TPS3840_IOVDD_SEQUENCE_REVIEW_NOT_FOR_FAB" in OLDROOT.read_text()
    fp_table=(NEWROOT.parent/"fp-lib-table").read_text()
    assert fp_table.count('(lib (name "S3900E_TPS3840_DBV5_V735_HOLD")')==1
    import pcbnew
    foot=pcbnew.FootprintLoad(str(FPDIR),"TI_DBV0005A_5PAD_REFLOW_REVIEW")
    assert foot is not None,"Native PCBNEW refused package"
    pads={p.GetNumber():(
        round(pcbnew.ToMM(p.GetPosition().x),4),
        round(pcbnew.ToMM(p.GetPosition().y),4),
        round(pcbnew.ToMM(p.GetSize().x),4),
        round(pcbnew.ToMM(p.GetSize().y),4)) for p in foot.Pads()}
    assert pads==EXPECTED_PADS,pads
    oldc=compmap(OUT/"v735.original.net")
    newc=compmap(OUT/"v735.revised.net")
    assert len(oldc)==len(newc)==134
    delta={r:(oldc[r],newc[r]) for r in oldc if oldc[r]!=newc[r]}
    assert set(delta)=={"U6207"},delta
    assert delta["U6207"]==(("","TPS3840PL30DBVR"),(FPID,"TPS3840PL30DBVR")),delta
    assert sum(not x[0] for x in oldc.values())==35
    assert sum(not x[0] for x in newc.values())==34
    n0=nets(OUT/"v735.original.net");n1=nets(OUT/"v735.revised.net")
    assert len(n0)==len(n1)==101 and n0==n1,"Any altered node blocks approval"
    er0=native_erc(OUT/"v735.original.erc.rpt")
    er1=native_erc(OUT/"v735.revised.erc.rpt")
    assert (er0["errors"],er0["warnings"])==(36,221),er0
    assert er1["errors"]<=er0["errors"],er1
    for cat in ("pin_to_pin","pin_not_driven","power_pin_not_driven","wire_dangling","pin_not_connected"):
        assert er1["categories"].get(cat,0)<=er0["categories"].get(cat,0),(cat,er0,er1)
    assert er1["warnings"]<=er0["warnings"]+2,(er0,er1)
    evidence={"revision":"V7.35","approval":"REVIEW_HOLD_NO_FAB","TI_part":"TPS3840PL30DBVR",
        "package":"DBV0005A_SOT23-5","TI_4214839_K_2024":True,
        "pads_mm":pads,"components":134,"nets":101,"pin_net_delta":0,
        "footprint_changes":["U6207"],"missing_before":35,"missing_after":34,
        "erc_before":er0,"erc_after":er1,
        "board_exists":False,"SG48_HOLD":True,"crossdomain_15_HOLD":True,
        "NO_FAB":True,"NO_TX":True}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v735.native.json").write_text(json.dumps(evidence,indent=2,default=str)+"\n")
    return evidence

class TestTPS3840VendorLand(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=gate()
    def test_01_native_five_pads(self):self.assertEqual(len(self.data["pads_mm"]),5)
    def test_02_one_footprint_only(self):self.assertEqual(self.data["footprint_changes"],["U6207"])
    def test_03_no_net_change(self):self.assertEqual((self.data["nets"],self.data["pin_net_delta"]),(101,0))
    def test_04_missing_footprint_reduced(self):self.assertEqual((self.data["missing_before"],self.data["missing_after"]),(35,34))
    def test_05_erc_no_new_error(self):self.assertLessEqual(self.data["erc_after"]["errors"],36)
    def test_06_no_fab_tx(self):self.assertTrue(self.data["NO_FAB"] and self.data["NO_TX"] and self.data["SG48_HOLD"])

if __name__=="__main__":unittest.main()
