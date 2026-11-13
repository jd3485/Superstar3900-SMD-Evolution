"""V7.51 TI TPS26600 eFuse reverse-input-polarity safety: never short RTN-GND.
Native KiCad9 seven-sheet netlist + vendor-linked UVLO/OVP resistor corners.
No electrical circuit or intermodule ECO; one safety annotation in schematic.
"""
import itertools,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche/V7.51/output-ci"
OLDROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.50_JST_CONNECTORS_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
NEWROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.51_TPS26600_RTN_SAFETY_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
OLDAUX=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.50_JST_CONNECTORS_REVIEW_NOT_FOR_FAB"
NEWAUX=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.51_TPS26600_RTN_SAFETY_REVIEW_NOT_FOR_FAB"
WARNING='(text "TI TPS26600 SLVSDG2G sect. 10.4: MAI CORTOCIRCUITARE RTN A GND: si perde la protezione inversione polarita!" (at 196 45 0) (effects (font (size 1.2 1.2))) (uuid "b7510000-0000-4000-8000-000000000001"))'
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def mapping(filename):
    result={}
    for net,points in nets(filename).items():
        for pin in points:
            if pin in result:raise AssertionError(("duplicate net on pin",pin))
            result[pin]=net
    return result

def node(mp,ref,pin,suffix):
    n=mp[(ref,str(pin))]
    assert n.endswith("/"+suffix),(ref,pin,n,suffix)
    return n

def threshold_bounds(which,resistors,threshold_min,threshold_typ,threshold_max):
    rr=[resistors[k] for k in ("R200","R201","R202")]
    denom_index=(1,2) if which=="UVLO" else (2,)
    def f(v,x):
        return v*sum(x)/sum(x[i] for i in denom_index)
    points=[]
    for vals in itertools.product(*[(v*.99,v*1.01) for v in rr]):
        for t in (threshold_min,threshold_max):
            points.append(f(t,vals))
    return {"typ_v":f(threshold_typ,rr),"min_v":min(points),"max_v":max(points)}

def gate():
    original=(OLDAUX/"01_EFUSE_AUX.kicad_sch").read_text(encoding="utf8")
    revised=(NEWAUX/"01_EFUSE_AUX.kicad_sch").read_text(encoding="utf8")
    assert WARNING not in original and revised.count(WARNING)==1
    assert revised.replace("\n"+WARNING,"")==original,"Only one warning text may change the eFuse CAD"
    for fn in ("S3900E_AUX_POWER_V1_5.kicad_sch","02_BUCK_5V.kicad_sch","03_PLL_LDO_TCXO.kicad_sch"):
        assert (OLDAUX/fn).read_bytes()==(NEWAUX/fn).read_bytes(),fn
    s=NEWROOT.read_text(encoding="utf8")
    assert s.count("../Gerarchico_Alimentazioni_V7.51_TPS26600_RTN_SAFETY_REVIEW_NOT_FOR_FAB/")==1
    assert s.count("(sheet (at ")==3,"Top-level sheet pins must remain isolated"
    for fn in ("fp-lib-table","sym-lib-table","S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_pro"):
        assert (OLDROOT.parent/fn).read_bytes()==(NEWROOT.parent/fn).read_bytes(),fn
    c0=compmap(OUT/"v751.original.net")
    c1=compmap(OUT/"v751.revised.net")
    assert len(c0)==len(c1)==138 and c0==c1,"No components, values or footprints may change"
    assert sum(not x[0] for x in c1.values())==0
    n0=nets(OUT/"v751.original.net")
    n1=nets(OUT/"v751.revised.net")
    assert len(n0)==len(n1)==101 and n0==n1,"No pin-net changes allowed"
    m=mapping(OUT/"v751.revised.net")
    rtn=node(m,"U200","8","EFUSE_RTN")
    pp=node(m,"U200","17","EFUSE_RTN")
    gnd=node(m,"U200","9","GND_MAIN")
    assert rtn==pp and rtn!=gnd,"TI: RTN short GND defeats reverse polarity protection"
    assert gnd==node(m,"J100","2","GND_MAIN")
    assert rtn!=node(m,"J100","2","GND_MAIN")
    assert rtn!=m[("U6205","2")],"MCU ground must remain isolated"
    for ref,pin in (("R203","2"),("C201","2"),("R202","2")):
        assert node(m,ref,pin,"EFUSE_RTN")==rtn,(ref,pin)
    for ref,pin in (("R200","1"),("U200","1"),("U200","2")):
        node(m,ref,pin,"EFUSE_VIN")
    for ref,pin in (("R200","2"),("R201","1"),("U200","3")):
        node(m,ref,pin,"UVLO_NODE")
    for ref,pin in (("R201","2"),("R202","1"),("U200","5")):
        node(m,ref,pin,"OVP_NODE")
    node(m,"R203","1","ILIM_NODE")
    node(m,"U200","11","ILIM_NODE")
    node(m,"C201","1","DV_DT_NODE")
    node(m,"U200","12","DV_DT_NODE")
    assert node(m,"F200","1","PWR_13V8_AUX_RAW")==node(m,"J100","1","PWR_13V8_AUX_RAW")
    node(m,"F200","2","EFUSE_VIN")
    assert node(m,"U200","15","BUCK_VIN_PROTECTED")==node(m,"U200","16","BUCK_VIN_PROTECTED")
    assert m[("U200","15")]!=m[("U200","1")]
    assert m[("U200","9")]!=m[("U6205","2")]
    values={"R200":365000,"R201":16200,"R202":30100}
    for ref,exp in (("R200","365k 1%"),("R201","16k2 1%"),("R202","30k1 1%")):
        assert c1[ref][1]==exp,(ref,c1[ref])
    uv=threshold_bounds("UVLO",values,1.175,1.19,1.225)
    ov=threshold_bounds("OVP",values,1.17,1.19,1.225)
    assert 10.2<uv["min_v"]<uv["typ_v"]<uv["max_v"]<11.2
    assert 15.6<ov["min_v"]<ov["typ_v"]<ov["max_v"]<17.2
    assert uv["max_v"]<13.8<ov["min_v"],(uv,ov)
    e0=native_erc(OUT/"v751.original.erc.rpt")
    e1=native_erc(OUT/"v751.revised.erc.rpt")
    assert (e0["errors"],e0["warnings"])==(28,221),e0
    assert (e1["errors"],e1["warnings"])==(28,221),e1
    result={"version":"V7.51","status":"NO_FAB_EFUSE_SAFETY_REVIEW",
      "parts":138,"nets":101,"footprints_missing":0,
      "rtn_net":rtn,"gnd_net":gnd,"rtn_powerpad_same":True,"rtn_not_gnd":True,
      "uvlo_rising_static_resistor_tolerance_1pct":uv,
      "ovp_rising_static_resistor_tolerance_1pct":ov,
      "min_input_v_nominal":13.8,
      "transients_and_input_leakage_included":False,
      "thresholds_validated_on_hardware":False,"reverse_polarity_tested":False,
      "erc_original":{"errors":e0["errors"],"warnings":e0["warnings"]},
      "erc_revised":{"errors":e1["errors"],"warnings":e1["warnings"]},
      "aux_to_mcu_joined":False,"NO_FAB":True,"NO_GERBER":True,"NO_PCBWAY":True,"NO_TX":True}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v751.rtn_safety.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    return result

class TestEfuSafety(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.result=gate()
    def test_01_rtn_not_gnd(self):self.assertTrue(self.result["rtn_not_gnd"])
    def test_02_powerpad_in_rtn(self):self.assertTrue(self.result["rtn_powerpad_same"])
    def test_03_components_preserved(self):self.assertEqual(self.result["parts"],138)
    def test_04_all_pads_assigned(self):self.assertEqual(self.result["footprints_missing"],0)
    def test_05_nets_unchanged(self):self.assertEqual(self.result["nets"],101)
    def test_06_uvlo_nominal(self):self.assertAlmostEqual(self.result["uvlo_rising_static_resistor_tolerance_1pct"]["typ_v"],10.571209503239741)
    def test_07_ovp_nominal(self):self.assertAlmostEqual(self.result["ovp_rising_static_resistor_tolerance_1pct"]["typ_v"],16.260697674418605)
    def test_08_uvlo_upper_below_nominal_supply(self):self.assertLess(self.result["uvlo_rising_static_resistor_tolerance_1pct"]["max_v"],13.8)
    def test_09_ovp_lower_above_nominal_supply(self):self.assertGreater(self.result["ovp_rising_static_resistor_tolerance_1pct"]["min_v"],13.8)
    def test_10_static_corner_no_transient_claim(self):self.assertFalse(self.result["transients_and_input_leakage_included"])
    def test_11_no_hw_signoff(self):self.assertFalse(self.result["thresholds_validated_on_hardware"])
    def test_12_reverse_test_hold(self):self.assertFalse(self.result["reverse_polarity_tested"])
    def test_13_erc_identical(self):self.assertEqual(self.result["erc_original"],self.result["erc_revised"])
    def test_14_grounds_no_crossmodule(self):self.assertFalse(self.result["aux_to_mcu_joined"])
    def test_15_no_fab_or_tx(self):self.assertTrue(all(self.result[k] for k in ("NO_FAB","NO_GERBER","NO_PCBWAY","NO_TX")))
if __name__=="__main__":unittest.main()
