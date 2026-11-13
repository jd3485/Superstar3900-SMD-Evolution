"""V7.40 native KiCad 7-sheet FB6201 vendor-MPN and 5V power-bead gate.
No AUX-to-MCU cross-sheet wiring authorized. NO FAB/NO TX.
"""
import json,re,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche/V7.40/output-ci"
OLDROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.36_C6231_MURATA_GRM15_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
NEWROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.40_FB6201_TDK_0805_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
OLDMCU=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.36_C6231_MURATA_GRM15_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
NEWMCU=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.40_FB6201_TDK_0805_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
MPN="MPZ2012S601ATD25"
OLD_VAL="600R@100MHz_CANDIDATE"
NEW_VAL="600R@100MHz_TDK_2A_REVIEW"
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def dc_drop(current_a,dcr_max_ohms=.100):
    if current_a<0 or dcr_max_ohms<0: raise ValueError("negative current or DCR")
    return current_a*dcr_max_ohms

def dissipation(current_a,dcr_max_ohms=.100):
    if current_a<0 or dcr_max_ohms<0: raise ValueError("negative current or DCR")
    return current_a**2*dcr_max_ohms

def source_diff_gate():
    old=OLDMCU.read_text(encoding="utf-8");new=NEWMCU.read_text(encoding="utf-8")
    anchor='(property "Reference" "FB6201"'
    assert old.count(anchor)==new.count(anchor)==1
    a=old.index(anchor);e=old.index("(instances ",a)
    old_block=old[a:e]
    assert '(property "Value" "'+OLD_VAL+'"' in old_block
    assert '(property "Footprint" ""' in old_block
    m=re.search(r'(\(property "Footprint" ""[^\n]*\n)',old_block)
    assert m
    replacement=old_block.replace('(property "Value" "'+OLD_VAL+'"','(property "Value" "'+NEW_VAL+'"').replace(m.group(1),m.group(1)+'   (property "MPN" "'+MPN+'" (at 750.0000 340.0000 0) (effects (font (size 1 1)) (hide yes)))\n')
    assert old[:a]+replacement+old[e:]==new,"Unexpected MCU CAD change beyond FB6201 MPN/value"
    root=NEWROOT.read_text(encoding="utf-8")
    assert root.count("../Modulo_MCU_CODEC_V7.40_FB6201_TDK_0805_REVIEW_NOT_FOR_FAB/")==1
    assert len(re.findall(r'\(sheet \(at ',root))==3
    assert '(pin "5V_RF_PREREGULATED"' not in root,"Root inter-module links remain HOLD"
    return True

def gate():
    source_diff_gate()
    c0=compmap(OUT/"v740.original.net")
    c1=compmap(OUT/"v740.revised.net")
    assert len(c0)==len(c1)==134,(len(c0),len(c1))
    changed={ref:(c0[ref],c1[ref]) for ref in c0 if c0[ref]!=c1[ref]}
    assert changed=={"FB6201":(("",OLD_VAL),("",NEW_VAL))},changed
    assert sum(not d[0] for d in c0.values())==sum(not d[0] for d in c1.values())==33
    n0=nets(OUT/"v740.original.net")
    n1=nets(OUT/"v740.revised.net")
    assert len(n0)==len(n1)==101,(len(n0),len(n1))
    assert n0==n1,"Any changed pin/net relation fails"
    e0=native_erc(OUT/"v740.original.erc.rpt")
    e1=native_erc(OUT/"v740.revised.erc.rpt")
    assert (e0["errors"],e0["warnings"])==(36,221),e0
    assert e1["errors"]<=e0["errors"],e1
    for cat in ("pin_to_pin","pin_not_driven","power_pin_not_driven","wire_dangling","pin_not_connected"):
        assert e1["categories"].get(cat,0)<=e0["categories"].get(cat,0),(cat,e0,e1)
    assert e1["warnings"]<=e0["warnings"]+2,(e0,e1)
    result={"revision":"V7.40","part":MPN,"claimed_rated_current_A":2.0,
            "datasheet_DCRmax_ohm":.100,"Z100MHz_ohm_nominal":600,
            "component_count":134,"net_count":101,"changed_values":["FB6201"],
            "changed_pin_net_memberships":0,"missing_footprints":33,
            "erc_before":e0,"erc_after":e1,"AUX_MCU_interconnect_validated":False,
            "load_current_max_validated":False,"DC_bias_RF_impedance_validated":False,
            "selected_footprint_vendor_validated":False,"NO_FAB":True,"NO_TX":True}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v740.native.json").write_text(json.dumps(result,indent=2,default=str)+"\n")
    return result

class TestFB6201TDK(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.d=gate()
    def test_01_one_value_only(self):self.assertEqual(self.d["changed_values"],["FB6201"])
    def test_02_all_134(self):self.assertEqual(self.d["component_count"],134)
    def test_03_all_101_nets_identical(self):self.assertEqual((self.d["net_count"],self.d["changed_pin_net_memberships"]),(101,0))
    def test_04_missing_footprints_unchanged(self):self.assertEqual(self.d["missing_footprints"],33)
    def test_05_600ohm_is_not_DCR(self):self.assertAlmostEqual(dc_drop(1),.1)
    def test_06_2A_current_DCR_drop_upper_envelope(self):self.assertAlmostEqual(dc_drop(2),.2)
    def test_07_2A_dcr_power_upper_envelope(self):self.assertAlmostEqual(dissipation(2),.4)
    def test_08_four_ldo_max_1p2A_lower_bound_not_full_load(self):
        self.assertAlmostEqual(4*.300,1.2)
        self.assertAlmostEqual(dc_drop(1.2),.12)
    def test_09_buck_is_2A_not_unlimited(self):self.assertEqual(self.d["claimed_rated_current_A"],2.0)
    def test_10_no_timing_signoff(self):
        self.assertFalse(self.d["AUX_MCU_interconnect_validated"] or self.d["DC_bias_RF_impedance_validated"])
    def test_11_nonnegative(self):
        with self.assertRaises(ValueError):dc_drop(-.1)
    def test_12_no_fab_or_TX(self):self.assertTrue(self.d["NO_FAB"] and self.d["NO_TX"])

if __name__=="__main__":unittest.main()
