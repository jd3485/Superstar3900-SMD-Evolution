"""V7.52 KiCad9: TI TPS26600 MODE 402k to RTN, candidate latch-off/dVdT.
Native before/after electric graph fail closed; no fabrication or fault restart signoff.
"""
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche/V7.52/output-ci"
OLDROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.51_TPS26600_RTN_SAFETY_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
NEWROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.52_EFUSE_MODE_DVDT_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
OLDAUX=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.51_TPS26600_RTN_SAFETY_REVIEW_NOT_FOR_FAB"
NEWAUX=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.52_EFUSE_MODE_DVDT_LATCHOFF_REVIEW_NOT_FOR_FAB"
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def pinmap(path):
    result={}
    for net,pins in nets(path).items():
        for pin in pins:
            if pin in result:raise AssertionError(("multiple nets",pin))
            result[pin]=net
    return result
def on_net(mp,ref,pin,suffix):
    net=mp[(ref,str(pin))]
    assert net.endswith("/"+suffix),(ref,pin,net,suffix)
    return net
def source_check():
    old=(OLDAUX/"01_EFUSE_AUX.kicad_sch").read_text(encoding="utf8")
    new=(NEWAUX/"01_EFUSE_AUX.kicad_sch").read_text(encoding="utf8")
    nc='(no_connect (at 173 120) (uuid 0e1de3b7-f496-44eb-a825-b692d533a876))'
    pinlabel='(label "EFUSE_MODE" (at 173 120 0) (effects (font (size 1.016 1.016)) (justify left bottom)) (uuid "b7520000-0000-4000-8000-000000000005"))'
    assert old.count(nc)==1 and new.count(pinlabel)==1
    assert nc not in new
    assert new.count('(property "Reference" "R204"')==1
    assert new.count('(label "EFUSE_MODE"')==2
    assert '(property "Value" "402k 1% MODE_LATCHOFF_CANDIDATE"' in new
    assert 'MODE / SHDN / IMON / FLT non collegati in questa BOZZA: strategia fault & controllo da definire.' in old
    assert 'SHDN / IMON / FLT non collegati; MODE=R204 402k RTN -> LATCH-OFF, funzione/prove HOLD.' in new
    parts=new.split('\n(symbol (lib_id "S3900E:R_EFUSE") (at 333 195 90)')
    assert len(parts)==2
    expected_tail=parts[1].split('\n)',1)[0]
    assert 'R204' in expected_tail and 'EFUSE_MODE' in expected_tail
    # Source changes allowed: new R204 section with two local labels and notice,
    # replacement pin NC with label and replacement of only existing MODE note.
    expected=old.replace(nc,pinlabel)
    expected=expected.replace('MODE / SHDN / IMON / FLT non collegati in questa BOZZA: strategia fault & controllo da definire.',
      'SHDN / IMON / FLT non collegati; MODE=R204 402k RTN -> LATCH-OFF, funzione/prove HOLD.')
    added='\n(symbol (lib_id "S3900E:R_EFUSE") (at 333 195 90)'+expected_tail
    expected=expected.replace('\n)',added+'\n)')
    assert new.rstrip("\n")==expected.rstrip("\n"),"Unexpected schematic source edit"
    for fn in ("S3900E_AUX_POWER_V1_5.kicad_sch","02_BUCK_5V.kicad_sch","03_PLL_LDO_TCXO.kicad_sch"):
        assert (OLDAUX/fn).read_bytes()==(NEWAUX/fn).read_bytes()
    assert NEWROOT.read_text().count("../Gerarchico_Alimentazioni_V7.52_EFUSE_MODE_DVDT_LATCHOFF_REVIEW_NOT_FOR_FAB/")==1
    assert NEWROOT.read_text().count("(sheet (at ")==3
    for fn in ("fp-lib-table","sym-lib-table","S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_pro"):
        assert (OLDROOT.parent/fn).read_bytes()==(NEWROOT.parent/fn).read_bytes()

def gate():
    source_check()
    a=compmap(OUT/"v752.original.net")
    b=compmap(OUT/"v752.revised.net")
    assert len(a)==138 and len(b)==139,(len(a),len(b))
    assert set(b)-set(a)=={"R204"} and all(b[k]==v for k,v in a.items())
    assert b["R204"]==("Resistor_SMD:R_0603_1608Metric","402k 1% MODE_LATCHOFF_CANDIDATE"),b["R204"]
    assert sum(not p[0] for p in b.values())==0
    before=nets(OUT/"v752.original.net")
    after=nets(OUT/"v752.revised.net")
    assert len(before)==101 and len(after)==102,(len(before),len(after))
    origpins=pinmap(OUT/"v752.original.net")
    revpins=pinmap(OUT/"v752.revised.net")
    assert all(revpins[k]==v for k,v in origpins.items()),"Existing pin-net changed"
    assert ("U200","6") not in origpins,"MODE previously expected no-connect"
    assert set(revpins)-set(origpins)=={("U200","6"),("R204","1"),("R204","2")},set(revpins)-set(origpins)
    mode=on_net(revpins,"U200",6,"EFUSE_MODE")
    rtn=on_net(revpins,"U200",8,"EFUSE_RTN")
    gnd=on_net(revpins,"U200",9,"GND_MAIN")
    assert rtn==on_net(revpins,"U200",17,"EFUSE_RTN")
    assert gnd==on_net(revpins,"J100",2,"GND_MAIN")
    assert len({mode,rtn,gnd})==3,"MODE must not directly short RTN/GND"
    assert {revpins[("R204","1")],revpins[("R204","2")]}=={mode,rtn},"R204 only between MODE and RTN"
    assert revpins[("U200","12")]==revpins[("C201","1")] or revpins[("U200","12")]==revpins[("C201","2")]
    assert rtn in {revpins[("C201","1")],revpins[("C201","2")]}
    assert ("U200","7") not in revpins,"SHDN internal pullup must not be accidentally forced"
    assert ("U200","10") not in revpins and ("U200","14") not in revpins
    er0=native_erc(OUT/"v752.original.erc.rpt")
    er1=native_erc(OUT/"v752.revised.erc.rpt")
    assert (er0["errors"],er0["warnings"])==(28,221),er0
    assert er1["errors"]<=28 and er1["warnings"]<=222,(er0,er1)
    for cat in ("pin_to_pin","pin_not_driven","power_pin_not_driven","wire_dangling","pin_not_connected"):
        assert er1["categories"].get(cat,0)<=er0["categories"].get(cat,0),(cat,er0,er1)
    # Texas Instruments SLVSDG2G Table 2: MODE=402k to RTN -> latch-off on overload,
    # dVdT controls inrush; it is NOT auto-retry, and physical validation remains open.
    vin=13.8
    cdvdt_f=22e-9
    tv=8000*vin*cdvdt_f
    assert abs(tv-0.0024288)<1e-12
    result={"revision":"V7.52","part_count":139,"net_count":102,
      "old_erc":{"errors":er0["errors"],"warnings":er0["warnings"]},
      "new_erc":{"errors":er1["errors"],"warnings":er1["warnings"]},
      "old_part_count":138,"new_resistor":"R204","mode_net":mode,
      "mode_connected_only_to_rtn_through_R204":True,"rtn_gnd_still_separate":True,
      "mode_selection":"LATCH_OFF_CANDIDATE_WITH_DVDT_STARTUP",
      "theoretical_dvdt_s_at_13p8_v_from_ti_ideal_formula":tv,
      "true_input_surge_and_buck_startup_validated":False,
      "fault_recovery_behavior_approved":False,
      "PCB_footprint_thermal_approved":False,
      "intermodule_5v_ground_connected":False,
      "NO_FAB":True,"NO_GERBER":True,"NO_PCBWAY":True,"NO_TX":True}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v752.mode_latchoff_review.json").write_text(json.dumps(result,indent=2)+"\n")
    return result

class TestModeChoice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.z=gate()
    def test_01_parts(self):self.assertEqual((self.z["old_part_count"],self.z["part_count"]),(138,139))
    def test_02_nets(self):self.assertEqual(self.z["net_count"],102)
    def test_03_402k(self):self.assertEqual(self.z["new_resistor"],"R204")
    def test_04_gnd_isolation(self):self.assertTrue(self.z["rtn_gnd_still_separate"])
    def test_05_series_mode_rtn(self):self.assertTrue(self.z["mode_connected_only_to_rtn_through_R204"])
    def test_06_mode_latchoff(self):self.assertIn("LATCH_OFF",self.z["mode_selection"])
    def test_07_dvdt_22nF(self):self.assertAlmostEqual(self.z["theoretical_dvdt_s_at_13p8_v_from_ti_ideal_formula"],.0024288)
    def test_08_no_approved_fault_recovery(self):self.assertFalse(self.z["fault_recovery_behavior_approved"])
    def test_09_no_input_buck_transient_signoff(self):self.assertFalse(self.z["true_input_surge_and_buck_startup_validated"])
    def test_10_erc_not_worsened(self):self.assertLessEqual(self.z["new_erc"]["errors"],self.z["old_erc"]["errors"])
    def test_11_no_crossmodule_join(self):self.assertFalse(self.z["intermodule_5v_ground_connected"])
    def test_12_no_fab(self):self.assertTrue(all(self.z[k] for k in ("NO_FAB","NO_GERBER","NO_PCBWAY","NO_TX")))
if __name__=="__main__":unittest.main()
