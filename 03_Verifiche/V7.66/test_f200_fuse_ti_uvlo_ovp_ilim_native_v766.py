"""V7.66 F200 fuse CAD 100mil ECO, TI TPS26600 voltage/current nominal and 1% corners.
Every safety calculation intentionally avoids claims about hardware fuse coordination.
"""
from pathlib import Path
from collections import Counter
import json,itertools,math,re,sys,unittest

ROOT=Path(__file__).resolve().parents[2]
AUX0=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.65_SIX_EFUSE_CONTROL_GRID_REVIEW_NOT_FOR_FAB"
AUX1=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.66_F200_FUSE_GRID_REVIEW_NOT_FOR_FAB"
ROOT0=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.65_SIX_EFUSE_CONTROL_GRID_REVIEW_NOT_FOR_FAB"
ROOT1=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.66_F200_FUSE_GRID_REVIEW_NOT_FOR_FAB"
OUT=ROOT/"03_Verifiche/V7.66/output-ci"
MASTER="S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
EXACT_SOURCE_ATOMS=[
 ('(symbol (lib_id "S3900E:F") (at 58 77 0)',
  '(symbol (lib_id "S3900E:F") (at 58.4200 76.2000 0)'),
 ('(property "Reference" "F200" (at 58 70 0)',
  '(property "Reference" "F200" (at 58.4200 69.2000 0)'),
 ('(property "Value" "1.5A 045101.5MRL CANDIDATO" (at 58 73.7 0)',
  '(property "Value" "1.5A 045101.5MRL CANDIDATO" (at 58.4200 72.9000 0)'),
 ('(property "Footprint" "S3900E_LF451_V729_HOLD:LF451_045101_5MRL_VENDOR_CANDIDATE" (at 58 77 0)',
  '(property "Footprint" "S3900E_LF451_V729_HOLD:LF451_045101_5MRL_VENDOR_CANDIDATE" (at 58.4200 76.2000 0)'),
 ('(hierarchical_label "PWR_13V8_AUX_RAW" (shape input) (at 52.92 77 0)',
  '(hierarchical_label "PWR_13V8_AUX_RAW" (shape input) (at 53.3400 76.2000 0)'),
 ('(label "EFUSE_VIN" (at 63.08 77 0)',
  '(label "EFUSE_VIN" (at 63.5000 76.2000 0)')
]
# TI TPS2660 Rev G p7 Electrical Characteristics, p29 equations 9-12.
R1_KOHM=365.0;R2_KOHM=16.2;R3_KOHM=30.1;RILIM_KOHM=8.2
UVLO_RISE_MIN_TYP_MAX=(1.175,1.190,1.225)
OVP_RISE_MIN_TYP_MAX=(1.170,1.190,1.225)
UVLO_FALL_MIN_TYP_MAX=(1.080,1.100,1.125)
OVP_FALL_MIN_TYP_MAX=(1.085,1.100,1.125)
TOL=0.01

sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def uvlo_input_threshold(vcomp,r1,r2,r3):
    return vcomp*(r1+r2+r3)/(r2+r3)
def ovp_input_threshold(vcomp,r1,r2,r3):
    return vcomp*(r1+r2+r3)/r3
def ilim_nominal(r_kohm):
    # TI section 10.2.2.2 / EQ 9 only nominal, no guaranteed value for 8.2k.
    return 12.0/r_kohm
def all_1pct_resistor_corners():
    for scale in itertools.product((1-TOL,1+TOL),repeat=3):
        yield tuple(a*b for a,b in zip((R1_KOHM,R2_KOHM,R3_KOHM),scale))
def limited_corner_range(fn,ref_min,ref_max):
    cases=list(all_1pct_resistor_corners())
    return (min(fn(ref_min,*p) for p in cases),
            max(fn(ref_max,*p) for p in cases))

def mandatory_source_gate():
    expected=(AUX0/"01_EFUSE_AUX.kicad_sch").read_text(encoding="utf8")
    actual=(AUX1/"01_EFUSE_AUX.kicad_sch").read_text(encoding="utf8")
    for before,after in EXACT_SOURCE_ATOMS:
        assert expected.count(before)==1,("F200 original source missing/ambiguous",before)
        assert actual.count(after)==1,("F200 revised source missing/ambiguous",after)
        expected=expected.replace(before,after,1)
    assert expected==actual,"Unreviewed electrical/AUX schematic change"
    # F200 position including both 5.08mm horizontal pin ends on grid:
    for x,y in ((58.42,76.2),(53.34,76.2),(63.5,76.2)):
        assert math.isclose(x/2.54,round(x/2.54),abs_tol=1e-8)
        assert math.isclose(y/2.54,round(y/2.54),abs_tol=1e-8)
    for fn in ("02_BUCK_5V.kicad_sch","03_PLL_LDO_TCXO.kicad_sch","S3900E_AUX_POWER_V1_5.kicad_sch"):
        assert (AUX0/fn).read_bytes()==(AUX1/fn).read_bytes(),fn
    aroot=(ROOT0/MASTER).read_text(encoding="utf8")
    broot=(ROOT1/MASTER).read_text(encoding="utf8")
    assert broot==aroot.replace(
      "Gerarchico_Alimentazioni_V7.65_SIX_EFUSE_CONTROL_GRID_REVIEW_NOT_FOR_FAB",
      "Gerarchico_Alimentazioni_V7.66_F200_FUSE_GRID_REVIEW_NOT_FOR_FAB")
    for fn in ("sym-lib-table","fp-lib-table","S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_pro"):
        assert (ROOT0/fn).read_bytes()==(ROOT1/fn).read_bytes(),fn
    for target,expected in (("R200",'"365k 1%"'),("R201",'"16k2 1%"'),
       ("R202",'"30k1 1%"'),("R203",'"8k2 1%"'),
       ("R204",'"402k 1% MODE_LATCHOFF_CANDIDATE"')):
        assert f'(property "Reference" "{target}"' in actual
        assert f'(property "Value" {expected}' in actual
    return True

def net_pin_map(path):
    result={}
    for net,ps in nets(path).items():
        for p in ps:
            assert p not in result,("duplicate physical pin",p)
            result[p]=net
    return result

def split_erc(e):
    findings=Counter();old_target=[]
    for x in e["findings"]:
        d=dict(x);loc=d.get("locations",[])
        m=re.fullmatch(
          r'@\([0-9.]+ mm, [0-9.]+ mm\): Symbol F200 Pin [12] \[.+\]',
          loc[0]) if len(loc)==1 else None
        if m and d.get("category")=="endpoint_off_grid" and d.get("severity")=="warning":
            old_target.append(d)
        else:
            findings[json.dumps(d,sort_keys=True,ensure_ascii=False)]+=1
    return findings,old_target

def compute_engineering_audit():
    uv_nom=uvlo_input_threshold(1.19,R1_KOHM,R2_KOHM,R3_KOHM)
    ov_nom=ovp_input_threshold(1.19,R1_KOHM,R2_KOHM,R3_KOHM)
    uv_rng=limited_corner_range(uvlo_input_threshold,UVLO_RISE_MIN_TYP_MAX[0],UVLO_RISE_MIN_TYP_MAX[2])
    ov_rng=limited_corner_range(ovp_input_threshold,OVP_RISE_MIN_TYP_MAX[0],OVP_RISE_MIN_TYP_MAX[2])
    ilim=ilim_nominal(RILIM_KOHM)
    string_uA=13.8/(R1_KOHM+R2_KOHM+R3_KOHM)*1000
    continuous_fuse_candidate=1.5*.75
    assert 10.57<uv_nom<10.58 and 16.26<ov_nom<16.27
    assert 10.25<uv_rng[0]<10.26 and 11.07<uv_rng[1]<11.08
    assert 15.69<ov_rng[0]<15.70 and 17.05<ov_rng[1]<17.06
    assert 1.46<ilim<1.47
    assert 33.5<string_uA<33.6
    assert continuous_fuse_candidate==1.125
    assert ilim>continuous_fuse_candidate
    # TI specified input leakage 100nA per pin: 20× single pin
    # rule yes, but dual opposing pin leakage + temperature/aging not
    # represented in this simple resistor tolerance only corner.
    assert string_uA>20*.1
    # TI SHDN falling threshold is 0.55-0.94V, TYPICAL 0.76.
    # 0.76V is NOT a guaranteed disable level, historical V7.64 caveat.
    guaranteed_low_exclusive=0.55
    typ_low=0.76
    max_falling=.94
    assert guaranteed_low_exclusive<typ_low<max_falling
    return dict(uvlo_rising_nominal_V=uv_nom,uvlo_rising_res1pct_ti_ref_range_V=uv_rng,
       ovp_rising_nominal_V=ov_nom,ovp_rising_res1pct_ti_ref_range_V=ov_rng,
       divider_13p8V_current_uA=string_uA,
       ilim_from_ti_eq9_nominal_A=ilim,
       nominal_fuse_rating_A=1.5,
       fuse_recommended_continuous_at25C_A=continuous_fuse_candidate,
       fuse_thermal_derating_qualified=False,
       eFuse_limit_fuse_trip_coordination_qualified=False,
       shdn_low_falling_min_typ_max_V=(.55,.76,.94),
       shdn_v0p76_guaranteed_off=False,
       actual_shdn_pulse_measured=False,
       tvs_d200_is_DNP=True, actual_reverse_input_tested=False,
       load_5v_and_startup_qualified=False,
       eFuse_rtn_gnd_isolation_required=True)

def gate():
    mandatory_source_gate()
    a=compmap(OUT/"v766.original.net");b=compmap(OUT/"v766.revised.net")
    assert a==b and len(a)==140
    np0=net_pin_map(OUT/"v766.original.net")
    np1=net_pin_map(OUT/"v766.revised.net")
    assert np0==np1 and len(nets(OUT/"v766.original.net"))==len(nets(OUT/"v766.revised.net"))==103
    assert np1[("F200","1")]!=np1[("F200","2")]
    assert np1[("U200","8")]==np1[("U200","17")]!=np1[("U200","9")]
    assert np1[("U200","7")]==np1[("SW200","1")]==np1[("SW200","4")]
    assert np1[("U200","9")]==np1[("SW200","2")]==np1[("SW200","3")]
    e0=native_erc(OUT/"v766.original.erc.rpt")
    e1=native_erc(OUT/"v766.revised.erc.rpt")
    assert (e0["errors"],e0["warnings"])==(28,206)
    assert e1["errors"]==28
    o,t0=split_erc(e0);n,t1=split_erc(e1)
    if o!=n:
        print("Unexpected OTHER ERC ADDED",list((n-o).elements())[:5])
        print("Unexpected OTHER ERC REMOVED",list((o-n).elements())[:5])
    assert o==n,"Changed unapproved old ERC findings, no waivers allowed"
    assert not t1,("F200 still offgrid",t1)
    assert len(t0)==1,("Expected one F200 native off-grid warning",t0)
    assert e1["warnings"]==205,("Wrong new ERC warnings",e1["warnings"])
    ret=compute_engineering_audit()
    ret.update(components=140,nets=103,full_pin_to_net_map_equal=True,
        f200_native_offgrid_removed=len(t0),erc_before={"errors":28,"warnings":206},
        erc_after={"errors":e1["errors"],"warnings":e1["warnings"]},
        NO_FAB=True,NO_TX=True,pcb_drc_validated=False)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v766.tps2660_f200_threshold_corner_review.json").write_text(json.dumps(ret,indent=2)+"\n")
    return ret

class TestV766FuseInputAndTI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=gate()
    def test_01_parts(self):self.assertEqual(self.r["components"],140)
    def test_02_nets(self):self.assertEqual(self.r["nets"],103)
    def test_03_full_map(self):self.assertTrue(self.r["full_pin_to_net_map_equal"])
    def test_04_f200_grid(self):self.assertEqual(self.r["f200_native_offgrid_removed"],1)
    def test_05_error_same(self):self.assertEqual(self.r["erc_after"]["errors"],28)
    def test_06_warning(self):self.assertEqual(self.r["erc_after"]["warnings"],205)
    def test_07_uvlo_nominal(self):self.assertAlmostEqual(self.r["uvlo_rising_nominal_V"],10.5712095,places=5)
    def test_08_ovp_nominal(self):self.assertAlmostEqual(self.r["ovp_rising_nominal_V"],16.2606977,places=5)
    def test_09_uvlo_corners(self):self.assertLess(self.r["uvlo_rising_res1pct_ti_ref_range_V"][0],10.26)
    def test_10_ovp_corners(self):self.assertGreater(self.r["ovp_rising_res1pct_ti_ref_range_V"][1],17.05)
    def test_11_ilim_nominal(self):self.assertAlmostEqual(self.r["ilim_from_ti_eq9_nominal_A"],12/8.2)
    def test_12_divider_current(self):self.assertAlmostEqual(self.r["divider_13p8V_current_uA"],33.552151714,places=5)
    def test_13_fuse_derating(self):self.assertEqual(self.r["fuse_recommended_continuous_at25C_A"],1.125)
    def test_14_coord_hold(self):self.assertFalse(self.r["eFuse_limit_fuse_trip_coordination_qualified"])
    def test_15_shdn_typical_not_guaranteed(self):self.assertFalse(self.r["shdn_v0p76_guaranteed_off"])
    def test_16_shdn_min(self):self.assertEqual(self.r["shdn_low_falling_min_typ_max_V"][0],.55)
    def test_17_tvs_dnp(self):self.assertTrue(self.r["tvs_d200_is_DNP"])
    def test_18_shdn_hw_hold(self):self.assertFalse(self.r["actual_shdn_pulse_measured"])
    def test_19_load_hold(self):self.assertFalse(self.r["load_5v_and_startup_qualified"])
    def test_20_no_fab(self):self.assertTrue(self.r["NO_FAB"] and self.r["NO_TX"])

if __name__=="__main__":
    unittest.main()
