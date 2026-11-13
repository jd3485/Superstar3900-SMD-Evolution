"""V7.69 genuine TDK C103/C104 100mil CAD ECO; TI 2-clock Cout sensitivity.
No manufacturer curve digitization or PCB/hardware signoff is claimed.
"""
from pathlib import Path
from collections import Counter
import json,math,re,sys,itertools,unittest

ROOT=Path(__file__).resolve().parents[2]
A0=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.68_BUCK_BOOT_L_FB_GRID_REVIEW_NOT_FOR_FAB"
A1=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.69_TDK_OUTPUT_CEFF_GRID_REVIEW_NOT_FOR_FAB"
R0=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.68_BUCK_BOOT_L_FB_GRID_REVIEW_NOT_FOR_FAB"
R1=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.69_TDK_OUTPUT_CEFF_GRID_REVIEW_NOT_FOR_FAB"
OUT=ROOT/"03_Verifiche/V7.69/output-ci"
MASTER="S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
TARGETS=(("C103",277,120,276.86,119.38),("C104",304,120,304.80,119.38))
MPN="CGA6P3X7R1E226M250AB"
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def exact_source_gate():
    expected=(A0/"02_BUCK_5V.kicad_sch").read_text(encoding="utf8")
    revised=(A1/"02_BUCK_5V.kicad_sch").read_text(encoding="utf8")
    edits=0
    for ref,x,y,nx,ny in TARGETS:
        anchor=f'(symbol (lib_id "S3900E:C_BUCK") (at {x} {y} 90)'
        start=expected.index(anchor)
        end=expected.index("\n(symbol (lib_id",start+len(anchor))
        chunk=expected[start:end]
        assert f'(property "Reference" "{ref}"' in chunk
        split=chunk.index("\n (instances (project")
        head=chunk[:split];tail=chunk[split:]
        assert head.count(anchor)==1
        head=head.replace(anchor,f'(symbol (lib_id "S3900E:C_BUCK") (at {nx:.4f} {ny:.4f} 90)',1)
        edited=[0]
        def property_move(m):
            edited[0]+=1
            return f'(at {nx:.4f} {float(m[1])+ny-y:.4f} 0)'
        head=re.sub(r'\(at '+str(x)+r' ([\d.]+) 0\)',property_move,head)
        assert edited==[6],(ref,edited)
        edits+=1+edited[0]
        expected=expected[:start]+head+tail+expected[end:]
        for label,dy in (("5V_RF_PREREGULATED",-5.08),("GND_MAIN",5.08)):
            before=f'(label "{label}" (at {x} {y+dy:.2f} 0)'
            after=f'(label "{label}" (at {nx:.4f} {ny+dy:.4f} 0)'
            assert expected.count(before)==1,(ref,before)
            expected=expected.replace(before,after,1)
            edits+=1
        for vx,vy in ((nx,ny),(nx,ny-5.08),(nx,ny+5.08)):
            assert math.isclose(vx/2.54,round(vx/2.54),abs_tol=1e-8),ref
            assert math.isclose(vy/2.54,round(vy/2.54),abs_tol=1e-8),ref
    assert edits==18
    assert expected==revised,"Unapproved BUCK schematic source edit"
    for ref,_,_,nx,ny in TARGETS:
        assert f'(property "Reference" "{ref}"' in revised
        assert f'(property "MPN" "{MPN}" (at {nx:.4f} {ny-11:.4f} 0)' in revised
        assert f'(property "Qualification" "V7.56 AEC_Q200_CANDIDATE DC_BIAS_THERMAL_HOLD" (at {nx:.4f} {ny-10:.4f} 0)' in revised
    for filename in ("01_EFUSE_AUX.kicad_sch","03_PLL_LDO_TCXO.kicad_sch","S3900E_AUX_POWER_V1_5.kicad_sch"):
        assert (A0/filename).read_bytes()==(A1/filename).read_bytes()
    orig=(R0/MASTER).read_text(encoding="utf8")
    after=(R1/MASTER).read_text(encoding="utf8")
    assert after==orig.replace(
       "Gerarchico_Alimentazioni_V7.68_BUCK_BOOT_L_FB_GRID_REVIEW_NOT_FOR_FAB",
       "Gerarchico_Alimentazioni_V7.69_TDK_OUTPUT_CEFF_GRID_REVIEW_NOT_FOR_FAB")
    for filename in ("sym-lib-table","fp-lib-table","S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_pro"):
        assert (R0/filename).read_bytes()==(R1/filename).read_bytes()
    return edits

def pmap(path):
    out={}
    for name,ps in nets(path).items():
        for p in ps:
            assert p not in out,p
            out[p]=name
    return out

def normalize_erc(d):
    other=Counter();target=[]
    for raw in d["findings"]:
        x=dict(raw);loc=x.get("locations",[])
        m=re.fullmatch(
          r'@\([0-9.]+ mm, [0-9.]+ mm\): Symbol (C103|C104) Pin [12] \[.+\]',
          loc[0]) if len(loc)==1 else None
        if m and x.get("severity")=="warning" and x.get("category")=="endpoint_off_grid":
            target.append(m[1])
        else:other[json.dumps(x,sort_keys=True,ensure_ascii=False)]+=1
    return other,target

def ti_cout_2_cycles_min_uF(di_A,f_khz,delta_V):
    # TI TPS54202 Rev C §7.2.3.5.2 Eq11; no ESR, loop, parasitics,
    # actual load waveform, or capacitors' effective MLCC C included.
    assert di_A>0 and f_khz>0 and delta_V>0
    return 2*di_A/(f_khz*1000*delta_V)*1e6

def parametric_cout():
    assert ti_cout_2_cycles_min_uF(1.5,500,.25)==24.0
    at390=ti_cout_2_cycles_min_uF(1.5,390,.25)
    assert 30.769<at390<30.770
    # Multiplicative hypothetical sensitivity factors, *not* a guaranteed
    # bound or digitization of TDK char sheet. They can correlate in practice.
    scenarios=[]
    for tolerance,thermal,bias in itertools.product((1.,.8),(1.,.85),(1.,.95)):
        capacity=2*22.*tolerance*thermal*bias
        dv=2*1.5/(390000*(capacity*1e-6))
        scenarios.append(dict(tolerance_factor=tolerance,
          temperature_factor_assumed=thermal,bias_factor_assumed=bias,
          two_cap_total_uF=capacity,
          idealized_two_cycle_390khz_loadstep_droop_V=dv,
          meets_0p25V_at_390k_ideal_eq11=capacity>=at390))
    assert len(scenarios)==8
    adverse=2*22*.8*.85*.95
    assert math.isclose(adverse,28.424,abs_tol=1e-9)
    assert adverse<at390
    assert any(not x["meets_0p25V_at_390k_ideal_eq11"] for x in scenarios)
    # At 500k 24uF ideal; at 390k 30.769uF; even rated ±20%
    # nominal 44uF may satisfy simple eq11 but proves no actual qualification.
    return dict(
      manufacturer="TDK",mpn=MPN,
      rated_each_uF=22,rated_total_uF=44,rated_voltage_V=25,
      nominal_tolerance_fraction=.20,
      X7R_temperature_coeff_bound_fraction=.15,
      tdk_DC_bias_curve_per_part_5V_guaranteed=False,
      tdk_ageing_degradation_bound_known=False,
      assumed_test_step_A=1.5,
      assumed_allowed_droop_V=.25,
      ti_minimum_frequency_khz=390,ti_typical_frequency_khz=500,
      ti_eq11_min_cout_500khz_uF=24.0,
      ti_eq11_min_cout_390khz_uF=at390,
      scenario_count=len(scenarios),
      sensitivity_scenarios=scenarios,
      adverse_assumed_two_cap_total_uF=adverse,
      adverse_assumed_below_390k_target=True,
      real_dc_bias_thermal_aging_worst_case_qualified=False,
      real_load_step_droop_measured=False,
      real_loop_stability_verified=False,
      real_esr_and_layout_parasitics_qualified=False,
      F200_fuse_eFuse_coordination_qualified=False)

def gate():
    atoms=exact_source_gate()
    cm0=compmap(OUT/"v769.original.net")
    cm1=compmap(OUT/"v769.revised.net")
    assert cm0==cm1 and len(cm1)==140
    a=pmap(OUT/"v769.original.net")
    b=pmap(OUT/"v769.revised.net")
    assert a==b and len(nets(OUT/"v769.original.net"))==len(nets(OUT/"v769.revised.net"))==103
    for ref in ("C103","C104"):
        assert {b[(ref,"1")],b[(ref,"2")]}=={b[("C103","1")],b[("C103","2")]}
        assert b[(ref,"1")]!=b[(ref,"2")]
    assert b[("U200","8")]==b[("U200","17")]!=b[("U200","9")]
    assert b[("U200","7")]==b[("SW200","1")]==b[("SW200","4")]
    assert b[("U200","9")]==b[("SW200","2")]==b[("SW200","3")]
    old=native_erc(OUT/"v769.original.erc.rpt")
    new=native_erc(OUT/"v769.revised.erc.rpt")
    assert (old["errors"],old["warnings"])==(28,195)
    assert new["errors"]==28
    other0,removed=normalize_erc(old);other1,persist=normalize_erc(new)
    if other0!=other1:
        print("Non-target added",list((other1-other0).elements())[:5])
        print("Non-target removed",list((other0-other1).elements())[:5])
    assert other0==other1,"Unrelated real ERC finding changed"
    assert sorted(removed)==["C103","C104"],removed
    assert not persist,("Still off-grid target",persist)
    assert new["warnings"]==193
    risk=parametric_cout()
    risk.update(components=140,nets=103,complete_pin_net_map_unchanged=True,
        exact_source_edits=atoms,offgrid_removed=2,
        erc_before={"errors":28,"warnings":195},
        erc_after={"errors":28,"warnings":193},
        d200_TVS_still_DNP=True,
        crossmodule_15_HOLD=True,NO_FAB=True,NO_TX=True,
        full_board_pcb_drc_available=False)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v769_tdk_C103_C104_5v_ceff_sensitivity.json").write_text(json.dumps(risk,indent=2)+"\n")
    return risk

class TestV769TDK(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=gate()
    def test_01_source(self):self.assertEqual(self.r["exact_source_edits"],18)
    def test_02_components(self):self.assertEqual(self.r["components"],140)
    def test_03_nets(self):self.assertEqual(self.r["nets"],103)
    def test_04_pinmap(self):self.assertTrue(self.r["complete_pin_net_map_unchanged"])
    def test_05_offgrid(self):self.assertEqual(self.r["offgrid_removed"],2)
    def test_06_erc_errors(self):self.assertEqual(self.r["erc_after"]["errors"],28)
    def test_07_erc_warn(self):self.assertEqual(self.r["erc_after"]["warnings"],193)
    def test_08_tdk_mpn(self):self.assertEqual(self.r["mpn"],MPN)
    def test_09_nominal_pair(self):self.assertEqual(self.r["rated_total_uF"],44)
    def test_10_TI_500k(self):self.assertEqual(self.r["ti_eq11_min_cout_500khz_uF"],24)
    def test_11_TI_390k(self):self.assertAlmostEqual(self.r["ti_eq11_min_cout_390khz_uF"],30.7692307692)
    def test_12_scenarios(self):self.assertEqual(self.r["scenario_count"],8)
    def test_13_adverse(self):self.assertAlmostEqual(self.r["adverse_assumed_two_cap_total_uF"],28.424)
    def test_14_adverse_fail_ideal(self):self.assertTrue(self.r["adverse_assumed_below_390k_target"])
    def test_15_curve_not_guaranteed(self):self.assertFalse(self.r["tdk_DC_bias_curve_per_part_5V_guaranteed"])
    def test_16_aging_hold(self):self.assertFalse(self.r["tdk_ageing_degradation_bound_known"])
    def test_17_step_hw_hold(self):self.assertFalse(self.r["real_load_step_droop_measured"])
    def test_18_loop_hold(self):self.assertFalse(self.r["real_loop_stability_verified"])
    def test_19_fuse_hold(self):self.assertFalse(self.r["F200_fuse_eFuse_coordination_qualified"])
    def test_20_safety(self):self.assertTrue(self.r["NO_FAB"] and self.r["NO_TX"])

if __name__=="__main__":
    unittest.main()
