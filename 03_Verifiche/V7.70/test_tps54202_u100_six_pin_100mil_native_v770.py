"""V7.70: TI TPS54202DDCR U100 six real terminal positions on 100mil.
Vendor pin numbers are GND1 SW2 VIN3 FB4 EN5 BOOT6, NOT switched.
Full seven-sheet KiCad9 before/after net/ERC is mandatory and fail-closed.
"""
from pathlib import Path
from collections import Counter
import json,math,re,sys,unittest

ROOT=Path(__file__).resolve().parents[2]
A0=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.69_TDK_OUTPUT_CEFF_GRID_REVIEW_NOT_FOR_FAB"
A1=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.70_U100_TI_SOT23_6PIN_GRID_REVIEW_NOT_FOR_FAB"
R0=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.69_TDK_OUTPUT_CEFF_GRID_REVIEW_NOT_FOR_FAB"
R1=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.70_U100_TI_SOT23_6PIN_GRID_REVIEW_NOT_FOR_FAB"
LIB0=ROOT/"04_KiCad/Librerie_Simboli_V7.63_CK_KMR223NG_ULC_4PAD_HOLD/S3900E.kicad_sym"
LIB1=ROOT/"04_KiCad/Librerie_Simboli_V7.70_TPS54202_U100_PIN_GRID_HOLD/S3900E.kicad_sym"
OUT=ROOT/"03_Verifiche/V7.70/output-ci"
MASTER="S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
# TI TPS54202 Rev C §4 SOT23 DDC package top-view, symbol numbers and functions.
PINS=[
  ("GND","power_in",1,-20,-12,-20.32,-12.70,0,
    "GND_MAIN","hierarchical_label","passive",128,111,127,111.76),
  ("SW","output",2,20,2,20.32,2.54,180,
    "BUCK_SW","label",None,168,97,167.64,96.52),
  ("VIN","power_in",3,-20,10,-20.32,10.16,0,
    "BUCK_VIN_PROTECTED","hierarchical_label","input",128,89,127,88.90),
  ("FB","input",4,20,-10,20.32,-10.16,180,
    "BUCK_FB","label",None,168,109,167.64,109.22),
  ("EN","input",5,-20,-2,-20.32,-2.54,0,
    "BUCK_EN","label",None,128,101,127,101.60),
  ("BOOT","output",6,20,12,20.32,12.70,180,
    "BUCK_BOOT","label",None,168,87,167.64,86.36),
]
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def source_gate():
    s0=(A0/"02_BUCK_5V.kicad_sch").read_text(encoding="utf8")
    s1=(A1/"02_BUCK_5V.kicad_sch").read_text(encoding="utf8")
    l0=LIB0.read_text(encoding="utf8")
    l1=LIB1.read_text(encoding="utf8")
    count=0
    for name,ptype,num,x0,y0,x1,y1,angle,label,kind,shape,lx0,ly0,lx1,ly1 in PINS:
        orig=f'(pin {ptype} line (at {x0} {y0} {angle}) (length 5.08) (name "{name}"'
        new=f'(pin {ptype} line (at {x1:.4f} {y1:.4f} {angle}) (length 5.08) (name "{name}"'
        assert s0.count(orig)==1 and s1.count(new)==1,("embedded pin",num)
        assert l0.count(orig)==1 and l1.count(new)==1,("library pin",num)
        s0=s0.replace(orig,new,1)
        l0=l0.replace(orig,new,1)
        head=f'({kind} "{label}"'
        if shape:
            head+=f' (shape {shape})'
        orig=f'{head} (at {lx0} {ly0} 0)'
        new=f'{head} (at {lx1:.4f} {ly1:.4f} 0)'
        assert s0.count(orig)==1 and s1.count(new)==1,("label",name)
        s0=s0.replace(orig,new,1)
        count+=2
        for val in (x1,y1,lx1,ly1):
            assert math.isclose(val/2.54,round(val/2.54),abs_tol=1e-8),(name,val)
        # The schematic target pin coordinates must be actual symbol origin
        # plus the KiCad local mirror Y transform.
        assert math.isclose(lx1,147.32+x1,abs_tol=1e-7)
        assert math.isclose(ly1,99.06-y1,abs_tol=1e-7)
    instance_edits=[
      ('(symbol (lib_id "S3900E:TPS54202_DDC") (at 148 99 0)',
       '(symbol (lib_id "S3900E:TPS54202_DDC") (at 147.3200 99.0600 0)'),
      ('(property "Reference" "U100" (at 148 77 0)',
       '(property "Reference" "U100" (at 147.3200 77.0600 0)'),
      ('(property "Value" "TPS54202DDCR" (at 148 74 0)',
       '(property "Value" "TPS54202DDCR" (at 147.3200 74.0600 0)'),
      ('(property "Footprint" "Package_TO_SOT_SMD:SOT-23-6" (at 148 99 0)',
       '(property "Footprint" "Package_TO_SOT_SMD:SOT-23-6" (at 147.3200 99.0600 0)')
    ]
    for orig,new in instance_edits:
        assert s0.count(orig)==1 and s1.count(new)==1,orig
        s0=s0.replace(orig,new,1)
        count+=1
    assert count==16 and s0==s1,"Unexpected U100 schematic source changes"
    assert l0==l1,"Unexpected project symbol library change beyond 6 pin coords"
    for fn in ("01_EFUSE_AUX.kicad_sch","03_PLL_LDO_TCXO.kicad_sch","S3900E_AUX_POWER_V1_5.kicad_sch"):
        assert (A0/fn).read_bytes()==(A1/fn).read_bytes(),fn
    oldroot=(R0/MASTER).read_text(encoding="utf8")
    newroot=(R1/MASTER).read_text(encoding="utf8")
    assert newroot==oldroot.replace(
      "Gerarchico_Alimentazioni_V7.69_TDK_OUTPUT_CEFF_GRID_REVIEW_NOT_FOR_FAB",
      "Gerarchico_Alimentazioni_V7.70_U100_TI_SOT23_6PIN_GRID_REVIEW_NOT_FOR_FAB")
    for fn in ("fp-lib-table","S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_pro"):
        assert (R0/fn).read_bytes()==(R1/fn).read_bytes()
    sym0=(R0/"sym-lib-table").read_text(encoding="utf8")
    sym1=(R1/"sym-lib-table").read_text(encoding="utf8")
    assert sym1==sym0.replace(
      "Librerie_Simboli_V7.63_CK_KMR223NG_ULC_4PAD_HOLD",
      "Librerie_Simboli_V7.70_TPS54202_U100_PIN_GRID_HOLD")
    return count

def pmap(p):
    result={}
    for net,ps in nets(p).items():
        for pin in ps:
            assert pin not in result,pin
            result[pin]=net
    return result

def split_erc(report):
    unrelated=Counter();target=[]
    for v in report["findings"]:
        d=dict(v);loc=d.get("locations",[])
        m=re.fullmatch(
          r'@\([0-9.]+ mm, [0-9.]+ mm\): Symbol U100 Pin [1-6] \[.+\]',
          loc[0]) if len(loc)==1 else None
        if m and d.get("category")=="endpoint_off_grid" and d.get("severity")=="warning":
            target.append(d)
        else:
            unrelated[json.dumps(d,sort_keys=True,ensure_ascii=False)]+=1
    return unrelated,target

def gate():
    atoms=source_gate()
    c0=compmap(OUT/"v770.original.net")
    c1=compmap(OUT/"v770.revised.net")
    assert c0==c1 and len(c1)==140
    p0=pmap(OUT/"v770.original.net")
    p1=pmap(OUT/"v770.revised.net")
    assert p0==p1 and len(nets(OUT/"v770.original.net"))==len(nets(OUT/"v770.revised.net"))==103
    signal_pin=dict((num,name) for name,typ,num,*_ in PINS)
    # Preserve vendor pin-number-to-function mapping and genuine expected nets.
    vendor_nets={
      1:"GND_MAIN",2:"BUCK_SW",3:"BUCK_VIN_PROTECTED",
      4:"BUCK_FB",5:"BUCK_EN",6:"BUCK_BOOT"
    }
    for pin,name in signal_pin.items():
        assert name==PINS[pin-1][0]
        assert vendor_nets[pin] in p1[("U100",str(pin))],(pin,p1[("U100",str(pin))])
    assert p1[("U100","2")]==p1[("C102","2")] or p1[("U100","2")]==p1[("C102","1")]
    assert p1[("U200","8")]==p1[("U200","17")]!=p1[("U200","9")]
    assert p1[("U200","7")]==p1[("SW200","1")]==p1[("SW200","4")]
    assert p1[("U200","9")]==p1[("SW200","2")]==p1[("SW200","3")]
    erc0=native_erc(OUT/"v770.original.erc.rpt")
    erc1=native_erc(OUT/"v770.revised.erc.rpt")
    assert (erc0["errors"],erc0["warnings"])==(28,193)
    assert erc1["errors"]==28
    oldother,offgrid0=split_erc(erc0)
    newother,offgrid1=split_erc(erc1)
    if oldother!=newother:
        print("Other ERC added",list((newother-oldother).elements())[:10])
        print("Other ERC removed",list((oldother-newother).elements())[:10])
    assert oldother==newother,"Unrelated ERC finding changed"
    assert len(offgrid0)==1,("KiCad should flag exactly U100 VIN pin 3 as offgrid",offgrid0)
    assert "Pin 3 [VIN," in offgrid0[0]["locations"][0],offgrid0
    assert not offgrid1,"U100 pin still offgrid"
    assert erc1["warnings"]==192
    out=dict(source_atoms=atoms,components=140,nets=103,
      same_full_pin_net_graph=True,pin_numbers_TI_vendor=vendor_nets,
      corrected_u100_native_pin_offgrid=len(offgrid0),
      erc_before={"errors":28,"warnings":193},
      erc_after={"errors":28,"warnings":192},
      symbol_library_only_six_pin_coords_changed=True,
      full_board_drc_unavailable=True,real_buck_5v_loop_not_validated=True,
      c103_c104_effective_C_HOLD=True,
      F200_eFuse_fault_coordination_HOLD=True,
      no_5v_LDO_bench_load_data=True,
      D200_TVS_DNP=True,crossmodule_15_OPEN_HOLD=True,
      NO_FAB=True,NO_TX=True)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v770_tps54202_u100_six_pin_native_vendor_audit.json").write_text(json.dumps(out,indent=2)+"\n")
    return out

class TestV770VendorTI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=gate()
    def test_01_atoms(self):self.assertEqual(self.r["source_atoms"],16)
    def test_02_parts(self):self.assertEqual(self.r["components"],140)
    def test_03_nets(self):self.assertEqual(self.r["nets"],103)
    def test_04_fullmap(self):self.assertTrue(self.r["same_full_pin_net_graph"])
    def test_05_offgrid(self):self.assertEqual(self.r["corrected_u100_native_pin_offgrid"],1)
    def test_06_errors(self):self.assertEqual(self.r["erc_after"]["errors"],28)
    def test_07_warnings(self):self.assertEqual(self.r["erc_after"]["warnings"],192)
    def test_08_vendor_gnd(self):self.assertEqual(self.r["pin_numbers_TI_vendor"][1],"GND_MAIN")
    def test_09_vendor_sw(self):self.assertEqual(self.r["pin_numbers_TI_vendor"][2],"BUCK_SW")
    def test_10_vendor_vin(self):self.assertEqual(self.r["pin_numbers_TI_vendor"][3],"BUCK_VIN_PROTECTED")
    def test_11_vendor_fb(self):self.assertEqual(self.r["pin_numbers_TI_vendor"][4],"BUCK_FB")
    def test_12_vendor_en(self):self.assertEqual(self.r["pin_numbers_TI_vendor"][5],"BUCK_EN")
    def test_13_vendor_boot(self):self.assertEqual(self.r["pin_numbers_TI_vendor"][6],"BUCK_BOOT")
    def test_14_lib_six_only(self):self.assertTrue(self.r["symbol_library_only_six_pin_coords_changed"])
    def test_15_loop_hold(self):self.assertTrue(self.r["real_buck_5v_loop_not_validated"])
    def test_16_caps_hold(self):self.assertTrue(self.r["c103_c104_effective_C_HOLD"])
    def test_17_fuse_hold(self):self.assertTrue(self.r["F200_eFuse_fault_coordination_HOLD"])
    def test_18_load_hold(self):self.assertTrue(self.r["no_5v_LDO_bench_load_data"])
    def test_19_tvs_hold(self):self.assertTrue(self.r["D200_TVS_DNP"])
    def test_20_no_fab(self):self.assertTrue(self.r["NO_FAB"] and self.r["NO_TX"])

if __name__=="__main__":
    unittest.main()
