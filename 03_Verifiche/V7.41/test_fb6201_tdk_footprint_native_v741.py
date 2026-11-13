"""V7.41 TDK MPZ2012 vendor land 2-pad and 7-sheet native KiCad9 parity, NO FAB/TX."""
import json,sys,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche/V7.41/output-ci"
OLDROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.40_FB6201_TDK_0805_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
NEWROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.41_FB6201_TDK_VENDOR_LAND_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
OLDMCU=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.40_FB6201_TDK_0805_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
NEWMCU=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.41_FB6201_TDK_VENDOR_LAND_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
FPNAME="TDK_MPZ2012_0805_POWER_BEAD_REFLOW_REVIEW"
FPID="S3900E_TDK_MPZ2012_V741_HOLD:"+FPNAME
FPDIR=ROOT/"04_KiCad/Librerie_Footprint_V7.41_TDK_MPZ2012_HOLD/S3900E_TDK_Mpz_Review.pretty"
BEADVAL="600R@100MHz_TDK_2A_REVIEW"
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def gate():
    old=OLDMCU.read_text(encoding="utf8")
    new=NEWMCU.read_text(encoding="utf8")
    a=old.index('(property "Reference" "FB6201"')
    e=old.index("(instances ",a)
    original=old[a:e]
    assert '(property "Value" "'+BEADVAL+'"' in original
    assert '(property "Footprint" ""' in original
    assert '(property "MPN" "MPZ2012S601ATD25"' in original
    target=old[:a]+original.replace('(property "Footprint" ""','(property "Footprint" "'+FPID+'"')+old[e:]
    assert new==target,"MCU schematic edits beyond FB6201 footprint blocked"
    root=NEWROOT.read_text(encoding="utf8")
    assert root.count("../Modulo_MCU_CODEC_V7.41_FB6201_TDK_VENDOR_LAND_REVIEW_NOT_FOR_FAB/")==1
    assert "Modulo_MCU_CODEC_V7.40_FB6201_TDK_0805_REVIEW_NOT_FOR_FAB" in OLDROOT.read_text()
    assert (NEWROOT.parent/"fp-lib-table").read_text().count('(lib (name "S3900E_TDK_MPZ2012_V741_HOLD")')==1
    import pcbnew
    fp=pcbnew.FootprintLoad(str(FPDIR),FPNAME)
    assert fp is not None,"Native KiCad failed to load TDK vendor land"
    pads={p.GetNumber():(round(pcbnew.ToMM(p.GetPosition().x),4),
        round(pcbnew.ToMM(p.GetPosition().y),4),
        round(pcbnew.ToMM(p.GetSize().x),4),
        round(pcbnew.ToMM(p.GetSize().y),4)) for p in fp.Pads()}
    assert pads=={"1":(-.9,0.,.8,1.2),"2":(.9,0.,.8,1.2)},pads
    c0=compmap(OUT/"v741.original.net")
    c1=compmap(OUT/"v741.revised.net")
    assert len(c0)==len(c1)==134
    diff={k:(c0[k],c1[k]) for k in c0 if c0[k]!=c1[k]}
    assert diff=={"FB6201":(("",BEADVAL),(FPID,BEADVAL))},diff
    assert sum(not t[0] for t in c0.values())==33
    assert sum(not t[0] for t in c1.values())==32
    n0=nets(OUT/"v741.original.net")
    n1=nets(OUT/"v741.revised.net")
    assert len(n0)==len(n1)==101 and n0==n1,"Unexpected electrical change"
    e0=native_erc(OUT/"v741.original.erc.rpt")
    e1=native_erc(OUT/"v741.revised.erc.rpt")
    assert (e0["errors"],e0["warnings"])==(36,221),e0
    assert e1["errors"]<=e0["errors"],e1
    for cat in ("pin_to_pin","pin_not_driven","power_pin_not_driven","wire_dangling","pin_not_connected"):
        assert e1["categories"].get(cat,0)<=e0["categories"].get(cat,0),(cat,e0,e1)
    assert e1["warnings"]<=e0["warnings"]+2
    result={"version":"V7.41","MPN":"MPZ2012S601ATD25","pad_geometry_mm":pads,
         "networks":101,"components":134,"pin_net_changes":0,
         "footprint_edits":["FB6201"],"missing_footprints_before":33,
         "missing_footprints_after":32,"erc_before":e0,"erc_after":e1,
         "AUX_MCU_connection_APPROVED":False,"BEAD_DC_BIAS_TESTED":False,
         "BEAD_THERMAL_VERIFIED":False,"NO_FAB":True,"NO_TX":True}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v741.native.json").write_text(json.dumps(result,indent=2,default=str)+"\n")
    return result

class TestTDKBeadFootprint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.d=gate()
    def test_01_two_numbered_native_pads(self):self.assertEqual(len(self.d["pad_geometry_mm"]),2)
    def test_02_only_one_footprint_change(self):self.assertEqual(self.d["footprint_edits"],["FB6201"])
    def test_03_zero_net_delta(self):self.assertEqual((self.d["networks"],self.d["pin_net_changes"]),(101,0))
    def test_04_134_components(self):self.assertEqual(self.d["components"],134)
    def test_05_missing_footprints_reduced(self):self.assertEqual(self.d["missing_footprints_after"],32)
    def test_06_erc_no_new_errors(self):self.assertLessEqual(self.d["erc_after"]["errors"],36)
    def test_07_ground_hold(self):self.assertFalse(self.d["AUX_MCU_connection_APPROVED"])
    def test_08_no_thermal_signoff(self):self.assertFalse(self.d["BEAD_THERMAL_VERIFIED"])
    def test_09_no_fab_or_tx(self):self.assertTrue(self.d["NO_FAB"] and self.d["NO_TX"])

if __name__=="__main__":
    unittest.main()
