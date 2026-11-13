"""V7.67: KiCad9 full pin-net parity gate and plausible TPS54202/F200 input-current envelope.
The duty/efficiency examples are scenarios, not guaranteed bounds on actual hardware.
"""
from pathlib import Path
from collections import Counter
import json,re,math,sys,itertools,unittest

ROOT=Path(__file__).resolve().parents[2]
AUX0=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.66_F200_FUSE_GRID_REVIEW_NOT_FOR_FAB"
AUX1=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.67_BUCK_VIN_EN_GRID_REVIEW_NOT_FOR_FAB"
ROOT0=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.66_F200_FUSE_GRID_REVIEW_NOT_FOR_FAB"
ROOT1=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.67_BUCK_VIN_EN_GRID_REVIEW_NOT_FOR_FAB"
OUT=ROOT/"03_Verifiche/V7.67/output-ci"
MASTER="S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
# lib, reference, centre before/after, value, footprint, labels (top/bottom)
TARGETS=(
 ("C_BUCK","C100",52,85,50.80,83.82,"10uF 35V X7R","Capacitor_SMD:C_1210_3225Metric","BUCK_VIN_PROTECTED","GND_MAIN"),
 ("C_BUCK","C101",76,85,76.20,83.82,"100nF 50V X7R","Capacitor_SMD:C_0603_1608Metric","BUCK_VIN_PROTECTED","GND_MAIN"),
 ("R_BUCK","R103",52,132,50.80,132.08,"510k 5%","Resistor_SMD:R_0603_1608Metric","BUCK_VIN_PROTECTED","BUCK_EN"),
 ("R_BUCK","R104",76,132,76.20,132.08,"105k 1%","Resistor_SMD:R_0603_1608Metric","BUCK_EN","GND_MAIN")
)
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def exact_source_check():
    old=(AUX0/"02_BUCK_5V.kicad_sch").read_text(encoding="utf8")
    actual=(AUX1/"02_BUCK_5V.kicad_sch").read_text(encoding="utf8")
    expected=old
    count=0
    for lib,ref,x,y,nx,ny,value,fp,top,bottom in TARGETS:
        parts=[
          (f'(symbol (lib_id "S3900E:{lib}") (at {x} {y} 90)',
           f'(symbol (lib_id "S3900E:{lib}") (at {nx:.4f} {ny:.4f} 90)'),
          (f'(property "Reference" "{ref}" (at {x} {y-7} 0)',
           f'(property "Reference" "{ref}" (at {nx:.4f} {ny-7:.4f} 0)'),
          (f'(property "Value" "{value}" (at {x} {y-3.3:.1f} 0)',
           f'(property "Value" "{value}" (at {nx:.4f} {ny-3.3:.4f} 0)'),
          (f'(property "Footprint" "{fp}" (at {x} {y} 0)',
           f'(property "Footprint" "{fp}" (at {nx:.4f} {ny:.4f} 0)'),
          (f'(label "{top}" (at {x} {y-5.08:.2f} 0)',
           f'(label "{top}" (at {nx:.4f} {ny-5.08:.4f} 0)'),
          (f'(label "{bottom}" (at {x} {y+5.08:.2f} 0)',
           f'(label "{bottom}" (at {nx:.4f} {ny+5.08:.4f} 0)')
        ]
        for before,after in parts:
            assert expected.count(before)==1,("Ambiguous original atom",ref,before)
            assert actual.count(after)==1,("Absent or duplicated revised atom",ref,after)
            expected=expected.replace(before,after,1)
            count+=1
        assert all(math.isclose(v/2.54,round(v/2.54),abs_tol=1e-8)
          for v in (nx,ny,nx,ny-5.08,ny+5.08))
    assert count==24
    assert expected==actual,"Unexpected KiCad schematic source change outside 24 atoms"
    for filename in ("01_EFUSE_AUX.kicad_sch","03_PLL_LDO_TCXO.kicad_sch","S3900E_AUX_POWER_V1_5.kicad_sch"):
        assert (AUX0/filename).read_bytes()==(AUX1/filename).read_bytes()
    root_before=(ROOT0/MASTER).read_text(encoding="utf8")
    root_after=(ROOT1/MASTER).read_text(encoding="utf8")
    assert root_after==root_before.replace(
     "Gerarchico_Alimentazioni_V7.66_F200_FUSE_GRID_REVIEW_NOT_FOR_FAB",
     "Gerarchico_Alimentazioni_V7.67_BUCK_VIN_EN_GRID_REVIEW_NOT_FOR_FAB")
    for filename in ("sym-lib-table","fp-lib-table","S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_pro"):
        assert (ROOT0/filename).read_bytes()==(ROOT1/filename).read_bytes()
    return count

def pinmap(p):
    result={}
    for name,ps in nets(p).items():
        for v in ps:
            assert v not in result,("repeat physical pin",v)
            result[v]=name
    return result

def normalize_erc(report):
    unrelated=Counter()
    targets=[]
    for original in report["findings"]:
        d=dict(original);loc=d.get("locations",[])
        m=(re.fullmatch(
          r'@\([0-9.]+ mm, [0-9.]+ mm\): Symbol (C100|C101|R103|R104) Pin [12] \[.+\]',
          loc[0]) if len(loc)==1 else None)
        if m and d.get("category")=="endpoint_off_grid" and d.get("severity")=="warning":
            targets.append(m[1])
        else:unrelated[json.dumps(d,sort_keys=True,ensure_ascii=False)]+=1
    return unrelated,targets

def average_buck_input_current_A(vin,efficiency,iout_A):
    assert vin>0 and 0<efficiency<=1 and 0<=iout_A<=2
    return 5*iout_A/(vin*efficiency)

def fuse_nominal_design_current_A():
    return 1.5*(1-0.25) # no temperature derating applied, not a trip threshold

def electrical_envelope():
    # TI TPS54202 2A out and 5ms softstart are specified. 75-95% efficiency
    # and input voltage scenarios are DESIGNED SCENARIOS not guaranteed for board.
    vin=(10.2545,13.8,17.0524)
    eta=(0.75,0.85,0.90,0.95)
    outs=(0.25,0.5,1.0,1.5,2.0)
    rows=[{"vin_V":v,"efficiency_assumed":e,"output_5v_A":i,
      "idealized_steady_input_A":average_buck_input_current_A(v,e,i),
      "exceeds_fuse_1p125A_design_continuous":average_buck_input_current_A(v,e,i)>1.125}
      for v,e,i in itertools.product(vin,eta,outs)]
    assert len(rows)==60
    nominal=average_buck_input_current_A(13.8,0.85,2)
    low=average_buck_input_current_A(10.2545,0.75,2)
    assert 0.852<nominal<0.853 and 1.30<low<1.301
    assert nominal<1.125 and low>1.125
    design_lim_5v_A=1.125*10.2545*0.75/5
    assert 1.73<design_lim_5v_A<1.731
    # Important: 1.46A eFuse current LIMIT vs 1.125A fuse continuous guideline
    # are NOT equivalent operating quantities and are not contradictory by themselves.
    # No measured board load, no inrush, no time-current coordination proof.
    assert (12.0/8.2)>1.125
    return {
      "scenarios_count":len(rows),
      "scenario_points":rows,
      "nominal_input_13p8V_85pct_2A_A":nominal,
      "lowvin_10p2545V_75pct_2A_A":low,
      "buck_5v_current_limit_design_10p2545_75pct_A":design_lim_5v_A,
      "f200_fuse_continuous_guide_25C_A":1.125,
      "f200_nominal_cold_ohm":0.063,
      "f200_nominal_melting_I2t_A2s":0.853,
      "f200_200pct_3A_open_time_max_s":5.0,
      "f200_100pct_1p5A_min_s":4*3600,
      "tps54202_nominal_softstart_ms":5,
      "buck_2A_max_5v_output_A":2,
      "output_current_2A_qualified":False,
      "real_efficiency_verified":False,
      "real_fuse_inrush_I2t_verified":False,
      "real_fuse_and_eFuse_coordination_verified":False,
      "real_thermal_derating_verified":False,
      "real_5v_downstream_load_verified":False
    }

def gate():
    atoms=exact_source_check()
    m0=compmap(OUT/"v767.original.net")
    m1=compmap(OUT/"v767.revised.net")
    assert m0==m1 and len(m1)==140
    pins0=pinmap(OUT/"v767.original.net")
    pins1=pinmap(OUT/"v767.revised.net")
    assert pins0==pins1
    assert len(nets(OUT/"v767.original.net"))==len(nets(OUT/"v767.revised.net"))==103
    assert pins1[("C100","1")]==pins1[("C101","1")]==pins1[("R103","1")]
    assert pins1[("R103","2")]==pins1[("R104","1")]
    assert pins1[("C100","2")]==pins1[("C101","2")]==pins1[("R104","2")]
    assert pins1[("U200","8")]==pins1[("U200","17")]!=pins1[("U200","9")]
    assert pins1[("U200","7")]==pins1[("SW200","1")]==pins1[("SW200","4")]
    assert pins1[("U200","9")]==pins1[("SW200","2")]==pins1[("SW200","3")]
    e0=native_erc(OUT/"v767.original.erc.rpt")
    e1=native_erc(OUT/"v767.revised.erc.rpt")
    assert (e0["errors"],e0["warnings"])==(28,205)
    assert e1["errors"]==28
    unrelated0,fixed0=normalize_erc(e0)
    unrelated1,fixed1=normalize_erc(e1)
    if unrelated0!=unrelated1:
        print("ERC added",list((unrelated1-unrelated0).elements())[:10])
        print("ERC removed",list((unrelated0-unrelated1).elements())[:10])
    assert unrelated0==unrelated1,"Unrelated ERC finding changed"
    assert not fixed1,("still off-grid",fixed1)
    assert len(fixed0)==4 and set(fixed0)=={"C100","C101","R103","R104"},fixed0
    assert e1["warnings"]==201,("Unexpected ERC count",e1["warnings"])
    e=electrical_envelope()
    e.update(source_atoms=atoms,components=140,nets=103,full_pin_net_map_identical=True,
      erc_before={"errors":28,"warnings":205},
      erc_after={"errors":e1["errors"],"warnings":e1["warnings"]},
      reduced_offgrid_warnings=4,
      tps26600_RTN_ground_isolated=True,
      all_crossmodule_HOLD=True,NO_FAB=True,NO_TX=True,pcb_global_drc_available=False)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v767_buck_f200_scenario_envelope.json").write_text(json.dumps(e,indent=2)+"\n")
    return e

class TestV767BuckFuse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=gate()
    def test_01_source(self):self.assertEqual(self.r["source_atoms"],24)
    def test_02_components(self):self.assertEqual(self.r["components"],140)
    def test_03_nets(self):self.assertEqual(self.r["nets"],103)
    def test_04_pinmap(self):self.assertTrue(self.r["full_pin_net_map_identical"])
    def test_05_four_offgrid(self):self.assertEqual(self.r["reduced_offgrid_warnings"],4)
    def test_06_erc_errors(self):self.assertEqual(self.r["erc_after"]["errors"],28)
    def test_07_erc_warnings(self):self.assertEqual(self.r["erc_after"]["warnings"],201)
    def test_08_nominal(self):self.assertAlmostEqual(self.r["nominal_input_13p8V_85pct_2A_A"],10/(13.8*.85))
    def test_09_low_voltage(self):self.assertGreater(self.r["lowvin_10p2545V_75pct_2A_A"],1.3)
    def test_10_fuse_continuous(self):self.assertEqual(self.r["f200_fuse_continuous_guide_25C_A"],1.125)
    def test_11_fuse_200pct(self):self.assertEqual(self.r["f200_200pct_3A_open_time_max_s"],5)
    def test_12_fuse_nominal_I2t_not_limit(self):self.assertAlmostEqual(self.r["f200_nominal_melting_I2t_A2s"],.853)
    def test_13_60_scenarios(self):self.assertEqual(self.r["scenarios_count"],60)
    def test_14_buck_softstart(self):self.assertEqual(self.r["tps54202_nominal_softstart_ms"],5)
    def test_15_real_efficiency_HOLD(self):self.assertFalse(self.r["real_efficiency_verified"])
    def test_16_inrush_HOLD(self):self.assertFalse(self.r["real_fuse_inrush_I2t_verified"])
    def test_17_coord_HOLD(self):self.assertFalse(self.r["real_fuse_and_eFuse_coordination_verified"])
    def test_18_5vload_HOLD(self):self.assertFalse(self.r["real_5v_downstream_load_verified"])
    def test_19_domains(self):self.assertTrue(self.r["tps26600_RTN_ground_isolated"])
    def test_20_no_fab(self):self.assertTrue(self.r["NO_FAB"] and self.r["NO_TX"])

if __name__=="__main__":
    unittest.main()
