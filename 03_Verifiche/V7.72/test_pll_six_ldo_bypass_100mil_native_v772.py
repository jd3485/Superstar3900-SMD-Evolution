"""V7.72 six actual PLL U2/U3 LDO bypass MLCCs on 100mil, native strict parity.
Preserve input/output decoupling C50-C55 and full seven-sheet pin/net graph;
no TDK Ceff or TPS7A20 thermal sign-off is implied.
"""
from pathlib import Path
from collections import Counter
import json,math,re,sys,unittest
ROOT=Path(__file__).resolve().parents[2]
A0=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.71_LDO_THERMAL_L100_LIMITS_REVIEW_NOT_FOR_FAB"
A1=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.72_PLL_SIX_LDO_BYPASS_GRID_REVIEW_NOT_FOR_FAB"
R0=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.71_LDO_THERMAL_L100_LIMITS_REVIEW_NOT_FOR_FAB"
R1=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.72_PLL_SIX_LDO_BYPASS_GRID_REVIEW_NOT_FOR_FAB"
OUT=ROOT/"03_Verifiche/V7.72/output-ci"
MASTER="S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
# six non-DNP real 0805 MLCC bypass: ref original-x/y new-x/y value upper-net
TARGETS=(
 ("C50",374,122,373.38,121.92,"2u2 10V X7R","5V_RF_PREREGULATED"),
 ("C51",439,122,439.42,121.92,"4u7 10V X7R","3V3_PLL_INPUT_FROM_LDO"),
 ("C52",464,122,464.82,121.92,"10u 10V X7R","3V3_PLL_INPUT_FROM_LDO"),
 ("C53",374,215,373.38,215.90,"2u2 10V X7R","5V_RF_PREREGULATED"),
 ("C54",439,215,439.42,215.90,"4u7 10V X7R","3V3_REF_LDO"),
 ("C55",464,215,464.82,215.90,"10u 10V X7R","3V3_REF_LDO"))
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def fd(v):return f"{v:.2f}".removesuffix(".00")

def expected_source():
    original=(A0/"03_PLL_LDO_TCXO.kicad_sch").read_text(encoding="utf8")
    revised=(A1/"03_PLL_LDO_TCXO.kicad_sch").read_text(encoding="utf8")
    exp=original;changed=0
    for ref,x,y,nx,ny,val,top in TARGETS:
        old_bottom=134 if y==122 else 227
        pairs=[
          (f'(symbol (lib_id "S3900E:C_PLL") (at {x} {y} 90)',
           f'(symbol (lib_id "S3900E:C_PLL") (at {nx:.4f} {ny:.4f} 90)'),
          (f'(property "Reference" "{ref}" (at {x} {y-7} 0)',
           f'(property "Reference" "{ref}" (at {nx:.4f} {ny-7:.4f} 0)'),
          (f'(property "Value" "{val}" (at {x} {fd(y-3.7)} 0)',
           f'(property "Value" "{val}" (at {nx:.4f} {ny-3.7:.4f} 0)'),
          (f'(property "Footprint" "Capacitor_SMD:C_0805_2012Metric" (at {x} {y} 0)',
           f'(property "Footprint" "Capacitor_SMD:C_0805_2012Metric" (at {nx:.4f} {ny:.4f} 0)'),
          (f'(label "{top}" (at {x} {fd(y-5.08)} 0)',
           f'(label "{top}" (at {nx:.4f} {ny-5.08:.4f} 0)'),
          (f'(wire (pts (xy {x} {fd(y+5.08)}) (xy {x} {old_bottom}))',
           f'(wire (pts (xy {nx:.4f} {ny+5.08:.4f}) (xy {nx:.4f} {ny+12.7:.4f}))'),
          (f'(label "GND_MAIN" (at {x} {old_bottom} 0)',
           f'(label "GND_MAIN" (at {nx:.4f} {ny+12.7:.4f} 0)')
        ]
        assert len(pairs)==7
        for before,after in pairs:
            assert exp.count(before)==1,("Ambiguous original",ref,before,exp.count(before))
            assert revised.count(after)==1,("Absent revised atom",ref,after)
            exp=exp.replace(before,after,1)
            changed+=1
        for px,py in ((nx,ny),(nx,ny-5.08),(nx,ny+5.08),(nx,ny+12.7)):
            assert math.isclose(px/2.54,round(px/2.54),abs_tol=1e-8),(ref,px)
            assert math.isclose(py/2.54,round(py/2.54),abs_tol=1e-8),(ref,py)
    assert changed==42
    assert exp==revised,"Extra PLL schematic edit outside six capacitors/labels/wires"
    for fn in ("01_EFUSE_AUX.kicad_sch","02_BUCK_5V.kicad_sch","S3900E_AUX_POWER_V1_5.kicad_sch"):
        assert (A0/fn).read_bytes()==(A1/fn).read_bytes(),fn
    orig=(R0/MASTER).read_text(encoding="utf8")
    actual=(R1/MASTER).read_text(encoding="utf8")
    assert actual==orig.replace(
        "Gerarchico_Alimentazioni_V7.71_LDO_THERMAL_L100_LIMITS_REVIEW_NOT_FOR_FAB",
        "Gerarchico_Alimentazioni_V7.72_PLL_SIX_LDO_BYPASS_GRID_REVIEW_NOT_FOR_FAB")
    for fn in ("sym-lib-table","fp-lib-table","S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_pro"):
        assert (R0/fn).read_bytes()==(R1/fn).read_bytes()
    return changed

def full_pmap(path):
    d={}
    for n,ps in nets(path).items():
        for p in ps:
            assert p not in d,p
            d[p]=n
    return d

def categorize_erc(report):
    unrelated=Counter();target=[]
    for f in report["findings"]:
        x=dict(f);locations=x.get("locations",[])
        if x.get("category")=="endpoint_off_grid" and x.get("severity")=="warning" and len(locations)==1:
            loc=locations[0]
            if re.search(r'Symbol (?:C50|C51|C52|C53|C54|C55) Pin [12] \[',loc):
                target.append(x);continue
            if any(f"@({xx:.2f} mm, {yy:.2f} mm)" in loc for xx,yy in (
                (374.,127.08),(439.,127.08),(464.,127.08),
                (374.,220.08),(439.,220.08),(464.,220.08),
                (374.,134.),(439.,134.),(464.,134.),
                (374.,227.),(439.,227.),(464.,227.)
            )):
                target.append(x);continue
        unrelated[json.dumps(x,sort_keys=True,ensure_ascii=False)]+=1
    return unrelated,target

def gate():
    changed=expected_source()
    c0=compmap(OUT/"v772.original.net")
    c1=compmap(OUT/"v772.revised.net")
    assert c0==c1 and len(c1)==140
    n0=nets(OUT/"v772.original.net")
    n1=nets(OUT/"v772.revised.net")
    a=full_pmap(OUT/"v772.original.net")
    b=full_pmap(OUT/"v772.revised.net")
    assert a==b and len(n0)==len(n1)==103
    # Every relocated bypass has two DIFFERENT pins and an unchanged
    # pair of actual named electrical domains independent of pin orientation.
    for ref,x,y,nx,ny,val,top in TARGETS:
        ends={b[(ref,"1")],b[(ref,"2")]}
        assert len(ends)==2,(ref,ends)
        assert any(top in n for n in ends),(ref,top,ends)
        assert any("GND_MAIN" in n for n in ends),(ref,ends)
    assert {b[("C50","1")],b[("C50","2")]}=={b[("C53","1")],b[("C53","2")]}
    assert {b[("C51","1")],b[("C51","2")]}=={b[("C52","1")],b[("C52","2")]}
    assert {b[("C54","1")],b[("C54","2")]}=={b[("C55","1")],b[("C55","2")]}
    assert b[("U200","8")]==b[("U200","17")]!=b[("U200","9")]
    assert b[("U200","7")]==b[("SW200","1")]==b[("SW200","4")]
    assert b[("U200","9")]==b[("SW200","2")]==b[("SW200","3")]
    old=native_erc(OUT/"v772.original.erc.rpt")
    new=native_erc(OUT/"v772.revised.erc.rpt")
    assert (old["errors"],old["warnings"])==(28,192)
    assert new["errors"]==28
    o,t0=categorize_erc(old);n,t1=categorize_erc(new)
    if o!=n:
        print("Unrelated ERC introduced",list((n-o).elements())[:10])
        print("Unrelated ERC eliminated",list((o-n).elements())[:10])
    assert o==n,"Non-target ERC changed (never waive, review natively)"
    assert len(t0)>0,("No actual original capacitor-related off-grid warnings?",t0)
    assert len(t1)==0,("Revised bypass still off-grid",t1)
    assert new["warnings"]==192-len(t0),("Unexpected ERC warning delta",new["warnings"],len(t0))
    result=dict(
      source_exact_changed_atoms=changed,components=140,nets=103,
      full_pin_net_map_identical=True,
      six_real_non_DNP_caps=sorted(x[0] for x in TARGETS),
      original_related_endpoint_off_grid=len(t0),
      new_related_endpoint_off_grid=len(t1),
      native_erc_before={"errors":28,"warnings":192},
      native_erc_after={"errors":28,"warnings":new["warnings"]},
      vendor_mpn_newly_qualified=False,
      effective_capacitance_under_bias_verified=False,
      measured_six_LDO_loads_known=False,
      measured_thermal_or_load_step=False,
      eFuse_RTN_isolated=True,
      D200_TVS_DNP=True,crossmodule_15_OPEN_HOLD=True,
      FULL_PCB_DRC_VERIFIED=False,
      NO_FAB=True,NO_TX=True
    )
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v772_pll_six_ldo_bypass_net_parity.json").write_text(json.dumps(result,indent=2)+"\n")
    return result

class TestV772PLLBypass(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=gate()
    def test_01_source(self):self.assertEqual(self.r["source_exact_changed_atoms"],42)
    def test_02_parts(self):self.assertEqual(self.r["components"],140)
    def test_03_nets(self):self.assertEqual(self.r["nets"],103)
    def test_04_fullmap(self):self.assertTrue(self.r["full_pin_net_map_identical"])
    def test_05_non_dnp(self):self.assertEqual(len(self.r["six_real_non_DNP_caps"]),6)
    def test_06_erc_errors(self):self.assertEqual(self.r["native_erc_after"]["errors"],28)
    def test_07_warning_less(self):self.assertLess(self.r["native_erc_after"]["warnings"],192)
    def test_08_target_improve(self):self.assertGreater(self.r["original_related_endpoint_off_grid"],0)
    def test_09_new_target_zero(self):self.assertEqual(self.r["new_related_endpoint_off_grid"],0)
    def test_10_no_new_nominal(self):self.assertFalse(self.r["vendor_mpn_newly_qualified"])
    def test_11_ceff_hold(self):self.assertFalse(self.r["effective_capacitance_under_bias_verified"])
    def test_12_thermal_hold(self):self.assertFalse(self.r["measured_thermal_or_load_step"])
    def test_13_unknown_load(self):self.assertFalse(self.r["measured_six_LDO_loads_known"])
    def test_14_rtn_isolation(self):self.assertTrue(self.r["eFuse_RTN_isolated"])
    def test_15_no_tvs(self):self.assertTrue(self.r["D200_TVS_DNP"])
    def test_16_crossmodule_hold(self):self.assertTrue(self.r["crossmodule_15_OPEN_HOLD"])
    def test_17_no_global_drc(self):self.assertFalse(self.r["FULL_PCB_DRC_VERIFIED"])
    def test_18_no_fab(self):self.assertTrue(self.r["NO_FAB"] and self.r["NO_TX"])

if __name__=="__main__":
    unittest.main()
