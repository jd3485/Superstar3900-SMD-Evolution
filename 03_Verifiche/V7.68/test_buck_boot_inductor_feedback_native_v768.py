"""V7.68 native KiCad9 six BUCK bootstrap, inductor, feedback components 100mil.
Strict source change-list and all 7sheet pin-net parity. TI voltage divider
envelope is idealized and does NOT qualify physical 5V output/loop stability.
"""
from pathlib import Path
from collections import Counter
import json,math,re,sys,itertools,unittest

ROOT=Path(__file__).resolve().parents[2]
A0=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.67_BUCK_VIN_EN_GRID_REVIEW_NOT_FOR_FAB"
A1=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.68_BUCK_BOOT_L_FB_GRID_REVIEW_NOT_FOR_FAB"
R0=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.67_BUCK_VIN_EN_GRID_REVIEW_NOT_FOR_FAB"
R1=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.68_BUCK_BOOT_L_FB_GRID_REVIEW_NOT_FOR_FAB"
OUT=ROOT/"03_Verifiche/V7.68/output-ci"
MASTER="S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
# ref lib x0 y0 rotation x1 y1 value footprint top bottom
TARGETS=[
 ("C102","C_BUCK",218,67,0,218.44,66.04,"100nF 25V X7R","Capacitor_SMD:C_0603_1608Metric","BUCK_BOOT","BUCK_SW"),
 ("L100","L",250,95,0,248.92,93.98,"15uH SRP1038A-150M","S3900E_BOURNS_SRP1038A_V728_HOLD:SRP1038A_150M_BOURNS_VENDOR_CANDIDATE","BUCK_SW","5V_RF_PREREGULATED"),
 ("R100","R_BUCK",246,190,90,246.38,190.50,"49R9 1%","Resistor_SMD:R_0603_1608Metric","5V_RF_PREREGULATED","BUCK_DIV_TOP"),
 ("R101","R_BUCK",279,190,90,279.40,190.50,"100k 1%","Resistor_SMD:R_0603_1608Metric","BUCK_DIV_TOP","BUCK_FB"),
 ("C105","C_BUCK",310,190,90,309.88,190.50,"75pF 50V C0G","Capacitor_SMD:C_0603_1608Metric","BUCK_DIV_TOP","BUCK_FB"),
 ("R102","R_BUCK",279,227,90,279.40,226.06,"13k3 1%","Resistor_SMD:R_0603_1608Metric","BUCK_FB","GND_MAIN")
]
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def exact_source_gate():
    original=(A0/"02_BUCK_5V.kicad_sch").read_text(encoding="utf8")
    after=(A1/"02_BUCK_5V.kicad_sch").read_text(encoding="utf8")
    expected=original
    count=0
    for ref,lib,x,y,rot,nx,ny,value,fp,top,bottom in TARGETS:
        def fm(x):return f"{x:.2f}".removesuffix(".00")
        positions=(
           ((x-5.08,y),(nx-5.08,ny)),
           ((x+5.08,y),(nx+5.08,ny))
        ) if rot==0 else (
           ((x,y-5.08),(nx,ny-5.08)),
           ((x,y+5.08),(nx,ny+5.08))
        )
        pairs=[
           (f'(symbol (lib_id "S3900E:{lib}") (at {x} {y} {rot})',
            f'(symbol (lib_id "S3900E:{lib}") (at {nx:.4f} {ny:.4f} {rot})'),
           (f'(property "Reference" "{ref}" (at {x} {y-7} 0)',
            f'(property "Reference" "{ref}" (at {nx:.4f} {ny-7:.4f} 0)'),
           (f'(property "Value" "{value}" (at {x} {y-3.3:.1f} 0)',
            f'(property "Value" "{value}" (at {nx:.4f} {ny-3.3:.4f} 0)'),
           (f'(property "Footprint" "{fp}" (at {x} {y} 0)',
            f'(property "Footprint" "{fp}" (at {nx:.4f} {ny:.4f} 0)')
        ]
        for i,label in enumerate((top,bottom)):
            kind=(f'(hierarchical_label "{label}" (shape output)'
              if ref=="L100" and i==1 else f'(label "{label}"')
            (ox,oy),(tx,ty)=positions[i]
            pairs.append((f'{kind} (at {fm(ox)} {fm(oy)} 0)',
                          f'{kind} (at {tx:.4f} {ty:.4f} 0)'))
            for coord in (tx,ty):
                assert math.isclose(coord/2.54,round(coord/2.54),abs_tol=1e-8),ref
        assert len(pairs)==6
        for before,revised in pairs:
            assert expected.count(before)==1,("missing original",ref,before)
            assert after.count(revised)==1,("missing revised",ref,revised)
            expected=expected.replace(before,revised,1)
            count+=1
    assert count==36
    assert expected==after,"Out-of-scope source change in buck feedback/bootstrap/L"
    for filename in ("01_EFUSE_AUX.kicad_sch","03_PLL_LDO_TCXO.kicad_sch","S3900E_AUX_POWER_V1_5.kicad_sch"):
        assert (A0/filename).read_bytes()==(A1/filename).read_bytes()
    src=(R0/MASTER).read_text(encoding="utf8")
    dst=(R1/MASTER).read_text(encoding="utf8")
    assert dst==src.replace(
        "Gerarchico_Alimentazioni_V7.67_BUCK_VIN_EN_GRID_REVIEW_NOT_FOR_FAB",
        "Gerarchico_Alimentazioni_V7.68_BUCK_BOOT_L_FB_GRID_REVIEW_NOT_FOR_FAB")
    for fn in ("sym-lib-table","fp-lib-table","S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_pro"):
        assert (R0/fn).read_bytes()==(R1/fn).read_bytes()
    return count

def net_pin_map(path):
    d={}
    for net,ps in nets(path).items():
        for p in ps:
            assert p not in d,p
            d[p]=net
    return d

def split_erc(erc):
    other=Counter();target=[]
    for finding in erc["findings"]:
        d=dict(finding);loc=d.get("locations",[])
        m=(re.fullmatch(
           r'@\([0-9.]+ mm, [0-9.]+ mm\): Symbol (C102|L100|R100|R101|C105|R102) Pin [12] \[.+\]',
           loc[0]) if len(loc)==1 else None)
        if m and d.get("category")=="endpoint_off_grid" and d.get("severity")=="warning":
            target.append(m[1])
        else:other[json.dumps(d,sort_keys=True,ensure_ascii=False)]+=1
    return other,target

def theoretical_feedback():
    # TPS54202 Rev C Vfb MIN 0.581, TYP 0.596, MAX 0.611 V.
    # R100=49.9 ohm in series with R101=100k feedback upper leg,
    # R102=13.3k lower leg, 1% each. C105=75pF parallel to upper
    # 100k is NOT a DC divider element, requires dynamic loop review.
    rtop=100000+49.9
    rbot=13300
    nominal=.596*(1+rtop/rbot)
    low=.581*(1+rtop*.99/(rbot*1.01))
    high=.611*(1+rtop*1.01/(rbot*.99))
    assert 5.079<nominal<5.080
    assert 4.865<low<4.866
    assert 5.300<high<5.301
    # Actual buck 5V level, LDO performance, internal tolerance,
    # transient response and capacitor DC-bias NOT qualified.
    return dict(vfb_min_typ_max_V=[.581,.596,.611],
        nominal_ideal_5v_output_V=nominal,
        idealized_1pct_resistor_ref_range_V=[low,high],
        r100_ohm=49.9,r101_ohm=100000,r102_ohm=13300,
        compensation_C105_pF=75,inductor_L100_uH=15,
        output_voltage_measured=False,loop_stability_measured=False,
        capacitor_C103_C104_effective_C_measured=False,
        six_LDO_loads_verified=False)

def gate():
    atoms=exact_source_gate()
    c0=compmap(OUT/"v768.original.net")
    c1=compmap(OUT/"v768.revised.net")
    assert c0==c1 and len(c1)==140
    pin0=net_pin_map(OUT/"v768.original.net")
    pin1=net_pin_map(OUT/"v768.revised.net")
    assert pin0==pin1 and len(nets(OUT/"v768.original.net"))==len(nets(OUT/"v768.revised.net"))==103
    sets=lambda ref:{pin1[(ref,"1")],pin1[(ref,"2")]}
    c102,l100,r100,r101,c105,r102=(sets(r) for r in ("C102","L100","R100","R101","C105","R102"))
    assert all(len(x)==2 for x in (c102,l100,r100,r101,c105,r102))
    assert len(c102&l100)==1,("Bootstrap SW not connected to inductor",c102,l100)
    assert len(l100&r100)==1,"Buck output missing feedback top R100"
    assert len(r100&r101)==1,"R100 and R101 missing junction"
    assert r101==c105,"75pF C105 not across R101"
    assert len(r101&r102)==1,"R101 and R102 missing FB node"
    assert len(c102&r102)==0,"Buck SW and feedback ground short"
    assert pin1[("U200","8")]==pin1[("U200","17")]!=pin1[("U200","9")]
    assert pin1[("U200","7")]==pin1[("SW200","1")]==pin1[("SW200","4")]
    assert pin1[("U200","9")]==pin1[("SW200","2")]==pin1[("SW200","3")]
    e0=native_erc(OUT/"v768.original.erc.rpt")
    e1=native_erc(OUT/"v768.revised.erc.rpt")
    assert (e0["errors"],e0["warnings"])==(28,201)
    assert e1["errors"]==28
    unrelated0,oldtargets=split_erc(e0)
    unrelated1,newtargets=split_erc(e1)
    if unrelated0!=unrelated1:
        print("Non-target ERC introduced",list((unrelated1-unrelated0).elements())[:10])
        print("Non-target ERC removed",list((unrelated0-unrelated1).elements())[:10])
    assert unrelated0==unrelated1,"Other ERC findings changed"
    assert not newtargets,("still offgrid",newtargets)
    assert len(oldtargets)==6 and set(oldtargets)=={t[0] for t in TARGETS},oldtargets
    assert e1["warnings"]==195,("ERC count",e1["warnings"])
    x=theoretical_feedback()
    x.update(source_atoms=atoms,components=140,nets=103,all_pin_nets_identical=True,
       erc_before={"errors":28,"warnings":201},erc_after={"errors":28,"warnings":195},
       eliminated_native_offgrid=6,R204_latchoff_unchanged=True,
       d200_TVS_still_DNP=True,actual_f200_thermal_qualified=False,
       physical_5v_board_drc_complete=False,NO_FAB=True,NO_TX=True)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v768_buck_idealized_feedback_review.json").write_text(json.dumps(x,indent=2)+"\n")
    return x

class TestV768NativeFeedback(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=gate()
    def test_01_atoms(self):self.assertEqual(self.r["source_atoms"],36)
    def test_02_parts(self):self.assertEqual(self.r["components"],140)
    def test_03_nets(self):self.assertEqual(self.r["nets"],103)
    def test_04_pinmap(self):self.assertTrue(self.r["all_pin_nets_identical"])
    def test_05_offgrid(self):self.assertEqual(self.r["eliminated_native_offgrid"],6)
    def test_06_erc_errors(self):self.assertEqual(self.r["erc_after"]["errors"],28)
    def test_07_erc_warnings(self):self.assertEqual(self.r["erc_after"]["warnings"],195)
    def test_08_vfb(self):self.assertEqual(self.r["vfb_min_typ_max_V"],[.581,.596,.611])
    def test_09_nominal(self):self.assertAlmostEqual(self.r["nominal_ideal_5v_output_V"],5.07943912782)
    def test_10_low_corner(self):self.assertLess(self.r["idealized_1pct_resistor_ref_range_V"][0],4.866)
    def test_11_high_corner(self):self.assertGreater(self.r["idealized_1pct_resistor_ref_range_V"][1],5.300)
    def test_12_compensation(self):self.assertEqual(self.r["compensation_C105_pF"],75)
    def test_13_inductor(self):self.assertEqual(self.r["inductor_L100_uH"],15)
    def test_14_no_hw_measure(self):self.assertFalse(self.r["output_voltage_measured"])
    def test_15_loop_hold(self):self.assertFalse(self.r["loop_stability_measured"])
    def test_16_cap_hold(self):self.assertFalse(self.r["capacitor_C103_C104_effective_C_measured"])
    def test_17_lod_hold(self):self.assertFalse(self.r["six_LDO_loads_verified"])
    def test_18_fuse_hold(self):self.assertFalse(self.r["actual_f200_thermal_qualified"])
    def test_19_tvs_hold(self):self.assertTrue(self.r["d200_TVS_still_DNP"])
    def test_20_no_fab(self):self.assertTrue(self.r["NO_FAB"] and self.r["NO_TX"])

if __name__=="__main__":
    unittest.main()
