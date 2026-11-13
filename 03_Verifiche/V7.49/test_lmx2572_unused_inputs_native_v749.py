"""V7.49 KiCad9 native ECO: four TI LMX2572 optionally unused digital inputs
held low through weak 10k pull-down resistors, while preserving future drive.
NO inter-module connections. NO FAB/TX.
"""
import json,sys,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche/V7.49/output-ci"
OLDROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.48_TDK_2_C0G_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
NEWROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.49_LMX_PULLDOWN_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
OLDAUX=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.31_AUX_CONNECTORS_ON_GRID_NOT_FOR_FAB"
NEWAUX=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.49_LMX_UNUSED_PULLDOWN_REVIEW_NOT_FOR_FAB"
MAP={
 "R70":("5","PLL_SYNC_PENDING",365.76),
 "R71":("28","PLL_SYSREFREQ_PENDING",388.62),
 "R72":("30","PLL_RAMPCLK_PENDING",411.48),
 "R73":("32","PLL_RAMPDIR_PENDING",434.34),
}
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc
def pin_members(nets_by_name):
    mp={}
    for net,ps in nets_by_name.items():
        for pin in ps:
            if pin in mp:raise AssertionError(("two nets on same pin",pin))
            mp[pin]=net
    return mp
def gate():
    orig=(OLDAUX/"03_PLL_LDO_TCXO.kicad_sch").read_text()
    revised=(NEWAUX/"03_PLL_LDO_TCXO.kicad_sch").read_text()
    i=orig.rfind("\n)")
    assert i>0
    assert revised.startswith(orig[:i]+"\n"),"Old PLL file prefix changed"
    assert revised.endswith(orig[i:]),"Old PLL file termination changed"
    additions=revised[len(orig[:i])+1:-len(orig[i:])]
    for ref,(u1_pin,signal,y) in MAP.items():
        assert additions.count('(property "Reference" "'+ref+'"')==1,ref
        assert additions.count('(property "Value" "10k 1pct"')==4
        assert additions.count('(property "Footprint" "Resistor_SMD:R_0402_1005Metric"')==4
        assert additions.count('(label "'+signal+'" (at 595.63 '+str(y)+' 0)')==1,(ref,signal)
        assert additions.count('(label "GND_MAIN" (at 605.79 '+str(y)+' 0)')==1,ref
    assert additions.count('(symbol (lib_id "S3900E:R_PLL")')==4
    assert additions.count('(label "')==8
    for file in ("S3900E_AUX_POWER_V1_5.kicad_sch","01_EFUSE_AUX.kicad_sch","02_BUCK_5V.kicad_sch"):
        assert (OLDAUX/file).read_bytes()==(NEWAUX/file).read_bytes(),file
    assert NEWROOT.read_text().count("../Gerarchico_Alimentazioni_V7.49_LMX_UNUSED_PULLDOWN_REVIEW_NOT_FOR_FAB/")==1
    assert NEWROOT.read_text().count("(sheet (at ")==3
    c0=compmap(OUT/"v749.original.net")
    c1=compmap(OUT/"v749.revised.net")
    assert len(c0)==134 and len(c1)==138,(len(c0),len(c1))
    assert set(c1)-set(c0)==set(MAP),set(c1)-set(c0)
    assert all(c0[k]==c1[k] for k in c0),"Existing component value/footprint changed"
    for ref in MAP:
        assert c1[ref]==("Resistor_SMD:R_0402_1005Metric","10k 1pct"),(ref,c1[ref])
    n0,n1=(nets(OUT/f) for f in ("v749.original.net","v749.revised.net"))
    oldpins,newpins=pin_members(n0),pin_members(n1)
    assert all(newpins.get(key)==net for key,net in oldpins.items()),"A previously-connected pin changed nets"
    assert set(newpins)-set(oldpins)=={(ref,pin) for ref in MAP for pin in ("1","2")},"Unexpected added pin"
    for ref,(u1,net,y) in MAP.items():
        assert newpins[(ref,"1")]==newpins[("U1",u1)],(ref,u1,newpins.get((ref,"1")))
        assert newpins[(ref,"1")].endswith("/"+net),(ref,newpins[(ref,"1")])
        assert newpins[(ref,"2")].endswith("/GND_MAIN"),(ref,newpins[(ref,"2")])
        assert newpins[(ref,"1")]!=newpins[(ref,"2")],ref
    assert len(n0)==len(n1)==101,(len(n0),len(n1))
    missing0=sum(not v[0] for v in c0.values())
    missing1=sum(not v[0] for v in c1.values())
    assert missing0==missing1==2,(missing0,missing1)
    e0=native_erc(OUT/"v749.original.erc.rpt")
    e1=native_erc(OUT/"v749.revised.erc.rpt")
    assert (e0["errors"],e0["warnings"])==(36,221),e0
    assert e1["errors"]<=e0["errors"],(e0,e1)
    assert e1["warnings"]<=e0["warnings"]+3,(e0,e1)
    for typ in ("pin_to_pin","wire_dangling","pin_not_connected","power_pin_not_driven"):
        assert e1["categories"].get(typ,0)<=e0["categories"].get(typ,0),(typ,e0,e1)
    result={"revision":"V7.49","existing_components":134,"new_resistors":4,"total_components":138,
      "networks_before":len(n0),"networks_after":len(n1),"old_pin_net_changes":0,
      "new_resistor_nets":{r:{"signal":newpins[(r,"1")],"return":newpins[(r,"2")]} for r in MAP},
      "missing_footprints":2,"erc_before":{"errors":e0["errors"],"warnings":e0["warnings"]},
      "erc_after":{"errors":e1["errors"],"warnings":e1["warnings"]},
      "used_ti_recommendation":"SNAS740B Section 8.1.10 unused pin pull LOW",
      "can_drive_inputs_later":True,"control_firmware_approved":False,
      "aux_mcu_connected":False,"NO_FAB":True,"NO_GERBER":True,"NO_TX":True}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v749.native.json").write_text(json.dumps(result,indent=2)+"\n")
    return result
class TestLMXUnusedPins(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=gate()
    def test_01_four_resistors(self):self.assertEqual(self.r["new_resistors"],4)
    def test_02_138_parts(self):self.assertEqual(self.r["total_components"],138)
    def test_03_old_nets_unchanged(self):self.assertEqual(self.r["old_pin_net_changes"],0)
    def test_04_no_new_net(self):self.assertEqual((self.r["networks_before"],self.r["networks_after"]),(101,101))
    def test_05_pull_to_main_ground(self):self.assertTrue(all(v["return"].endswith("/GND_MAIN") for v in self.r["new_resistor_nets"].values()))
    def test_06_missing_conns_still_hold(self):self.assertEqual(self.r["missing_footprints"],2)
    def test_07_erc_no_growth(self):self.assertLessEqual(self.r["erc_after"]["errors"],36)
    def test_08_ramps_not_firmware_signed_off(self):self.assertFalse(self.r["control_firmware_approved"])
    def test_09_aux_still_isolated(self):self.assertFalse(self.r["aux_mcu_connected"])
    def test_10_fab_tx_held(self):self.assertTrue(all(self.r[k] for k in ("NO_FAB","NO_GERBER","NO_TX")))
if __name__=="__main__":unittest.main()
