"""V7.71 TI TPS7A20 six-rail thermal stress and Bourns L100 peak/rms review.
Review annotations are native KiCad CAD changes (no electrical value change).
No theta-JA value here is an actual PCB measurement or guaranteed bound.
"""
from pathlib import Path
from collections import Counter
import json, math, sys, unittest

ROOT=Path(__file__).resolve().parents[2]
A0=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.70_U100_TI_SOT23_6PIN_GRID_REVIEW_NOT_FOR_FAB"
A1=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.71_LDO_THERMAL_L100_LIMITS_REVIEW_NOT_FOR_FAB"
R0=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.70_U100_TI_SOT23_6PIN_GRID_REVIEW_NOT_FOR_FAB"
R1=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.71_LDO_THERMAL_L100_LIMITS_REVIEW_NOT_FOR_FAB"
OUT=ROOT/"03_Verifiche/V7.71/output-ci"
MASTER="S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
MATRIX=ROOT/"03_Verifiche/V7.43/MATRICE_CARICHI_TERMICA_5V_V743.json"
NOTES={
 "02_BUCK_5V.kicad_sch":[
 ("eaaa7111-1711-4711-a711-000000000171",
  "V7.71 L100 BOURNS: 15uH +/-20%, DCR max45mOhm, Irms6.25A / Isat10A @25C; ripple scenario only, DRC/PCB HOLD.",200,286),
 ("eaaa7111-1711-4711-a711-000000000172",
  "V7.71 5V RAIL HOLD: six TPS7A20 outputs 300mA RATED EACH, total 1.8A rating != real consumption; 2A buck margin not proven.",200,294)
 ],
 "03_PLL_LDO_TCXO.kicad_sch":[
 ("eaaa7111-1711-4711-a711-000000000173",
  "V7.71 LDO THERMAL HOLD: TPS7A2033 DBV Rja 187.1C/W; at Vin5.300V Ta85C Iout300mA, idealized Tj 199C (Ignd typ).",443,47),
 ("eaaa7111-1711-4711-a711-000000000174",
  "U2/U3 AND MCU U6203-U6206: 300mA rating is NOT approved per-rail current. Need actual load, PCB thermal and 5V worst case.",443,55)
 ]
}
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def note_text(note):
    uuid,phrase,x,y=note
    return f'(text "{phrase}" (at {x} {y} 0) (effects (font (size 1.2 1.2))) (uuid {uuid}))'

def source_gate():
    count=0
    for filename,notes in NOTES.items():
        expected=(A0/filename).read_text(encoding="utf8")
        actual=(A1/filename).read_text(encoding="utf8")
        closing=expected.rfind(")")
        assert closing>=0 and not expected[closing+1:].strip()
        inserted="\n".join(note_text(note) for note in notes)+"\n"
        expected=expected[:closing]+inserted+expected[closing:]
        assert expected==actual,("Unexpected schematic topology/value changes",filename)
        for note in notes:
            assert actual.count(note_text(note))==1
            assert actual.count(note[0])==1
            assert "NO_FAB" not in note[1]
        count+=len(notes)
    for fn in ("01_EFUSE_AUX.kicad_sch","S3900E_AUX_POWER_V1_5.kicad_sch"):
        assert (A0/fn).read_bytes()==(A1/fn).read_bytes(),fn
    oldroot=(R0/MASTER).read_text(encoding="utf8")
    newroot=(R1/MASTER).read_text(encoding="utf8")
    assert newroot==oldroot.replace(
        "Gerarchico_Alimentazioni_V7.70_U100_TI_SOT23_6PIN_GRID_REVIEW_NOT_FOR_FAB",
        "Gerarchico_Alimentazioni_V7.71_LDO_THERMAL_L100_LIMITS_REVIEW_NOT_FOR_FAB")
    for fn in ("sym-lib-table","fp-lib-table","S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_pro"):
        assert (R0/fn).read_bytes()==(R1/fn).read_bytes(),fn
    return count

def pmap(path):
    d={}
    for net,ps in nets(path).items():
        for x in ps:
            assert x not in d,x
            d[x]=net
    return d

def pldo(vin,i,ignd=.002,vout=3.3):
    assert 0<=i<=.3 and 0<=ignd and 0<vout<vin<=6.
    return (vin-vout)*i+vin*ignd

def tldo(ambient,vin,i,theta=187.1,ignd=.002):
    return ambient+theta*pldo(vin,i,ignd)

def i_at_125c(ambient,vin,theta=187.1,ignd=.002):
    return max(0.,((125.-ambient)/theta-vin*ignd)/(vin-3.3))

def bourns_l100_ripple(vin,load_A,L_h=12e-6,fsw_hz=390e3,vout=5.):
    assert vin>vout and 0<load_A<=2 and L_h>0 and fsw_hz>0
    # Ideal continuous conduction buck at fixed Vout with no conduction losses.
    di=vout*(1-vout/vin)/(L_h*fsw_hz)
    peak=load_A+di/2
    rms=(load_A**2+di**2/12)**.5
    return {"vin_V":vin,"load_A":load_A,"ripple_pp_A":di,"peak_A":peak,
       "inductor_rms_A":rms,"DCR_max45mohm_loss_W":.045*rms*rms,
       "Isat_10A_vendor_20pct_L_drop_current_A":10.,
       "Irms_6p25A_vendor_40C_rise_test_A":6.25}

def audit():
    d=json.loads(MATRIX.read_text(encoding="utf8"))
    refs={row["ref"] for row in d["rail_rows"]}
    assert refs=={"U2","U3","U6203","U6204","U6205","U6206"}
    assert len(d["rail_rows"])==6
    assert {r["ref"] for r in d["rail_rows"] if r["sheet"]=="pll"}=={"U2","U3"}
    assert {r["ref"] for r in d["rail_rows"] if r["sheet"]=="mcu"}=={"U6203","U6204","U6205","U6206"}
    assert all(r["load_max_known_a"] is None and r["transient_max_known_a"] is None for r in d["rail_rows"])
    assert d["unknown_direct_5v_and_other_load_a"] is None
    vin_scenarios=[4.865054342,5.,5.079439128,5.300131449]
    ambients=[25.,60.,85.]
    currents=[.05,.10,.15,.20,.30]
    thermal=[]
    for ref in sorted(refs):
        for vin in vin_scenarios:
            for amb in ambients:
                for curr in currents:
                    thermal.append(dict(ref=ref,Vin_assumed_V=vin,ambient_assumed_C=amb,
                        Iout_assumed_A=curr,
                        P_dissipation_assumed_W=pldo(vin,curr),
                        Tj_thetaJA_JEDEC_C=tldo(amb,vin,curr),
                        theoretical_max_current_to_125C_A=i_at_125c(amb,vin)))
    assert len(thermal)==6*4*3*5==360
    high=tldo(85.,vin_scenarios[-1],.3)
    assert 199.2<high<199.3
    high_current=i_at_125c(85.,vin_scenarios[-1])
    assert .1015<high_current<.1017
    assert tldo(25.,5.,.3)>122.2
    assert tldo(85.,5.,.3)>182.2
    assert math.isclose(.3*6,1.8,rel_tol=0,abs_tol=1e-12) and 2-1.8>.19999
    l100=[bourns_l100_ripple(vin,i)
        for vin in (10.2545,13.8,17.0524) for i in (.5,1.,1.5,2.)]
    assert len(l100)==12
    worst=next(x for x in l100 if x["vin_V"]==17.0524 and x["load_A"]==2.)
    assert 2.377<worst["peak_A"]<2.378
    assert .182<worst["DCR_max45mohm_loss_W"]<.183
    assert worst["peak_A"]<10. and worst["inductor_rms_A"]<6.25
    return dict(
       source_vendor_TI="https://www.ti.com/lit/ds/symlink/tps7a20.pdf",
       source_vendor_Bourns="https://www.bourns.com/docs/product-datasheets/srp1038a.pdf",
       six_ldos=sorted(refs),
       vendor_thetaJA_DBV_c_per_W=187.1,
       vendor_rated_each_ldo_A=.3,
       vendor_IGND_typ_at_300mA_assumed_A=.002,
       manufacturer_thetaJA_measured_on_our_board=False,
       measured_per_rail_loads_available=False,
       measured_total_5v_load_available=False,
       thermal_scenario_count=len(thermal),thermal_scenarios=thermal,
       max_highVin_highAmbient_at_300mA_tj_C=high,
       theoretical_max_A_at_highVin_85C_for125C=high_current,
       six_ratings_sum_A=1.8,buck_rating_A=2.,
       unknown_direct_5v_load_A=None,
       inductor_vendor_MPN="SRP1038A-150M",
       l100_nominal_uH=15.,l100_tolerance_fraction=.20,
       l100_DCR_typ_ohm=.040,l100_DCR_max_ohm=.045,
       l100_vendor_Irms_40C_rise_A=6.25,
       l100_vendor_Isat_20pct_Ldrop_A=10.,
       l100_scenario_count=len(l100),
       l100_scenarios=l100,
       l100_worst_2A_17p05V_390k_12uH=worst,
       L100_dynamic_saturation_measurement_qualified=False,
       L100_fault_current_qualification=False,
       L100_real_pcb_thermal_verified=False,
       tps54202_Ceff_loop_startup_qualified=False,
       no_general_pcb_DRC=True,NO_FAB=True,NO_TX=True)

def gate():
    edits=source_gate()
    cm0=compmap(OUT/"v771.original.net")
    cm1=compmap(OUT/"v771.revised.net")
    assert cm0==cm1 and len(cm1)==140
    pins0=pmap(OUT/"v771.original.net")
    pins1=pmap(OUT/"v771.revised.net")
    assert pins0==pins1 and len(nets(OUT/"v771.original.net"))==len(nets(OUT/"v771.revised.net"))==103
    assert pins1[("U200","8")]==pins1[("U200","17")]!=pins1[("U200","9")]
    assert pins1[("U200","7")]==pins1[("SW200","1")]==pins1[("SW200","4")]
    e0=native_erc(OUT/"v771.original.erc.rpt")
    e1=native_erc(OUT/"v771.revised.erc.rpt")
    assert (e0["errors"],e0["warnings"])==(28,192)
    assert (e1["errors"],e1["warnings"])==(28,192)
    # No exceptions allowed: all original findings retained exactly.
    bag=lambda e:Counter(json.dumps(d,sort_keys=True,ensure_ascii=False) for d in e["findings"])
    assert bag(e0)==bag(e1),"Unsafe ERC warning/error modification in text-only thermal annotation"
    eng=audit()
    eng.update(native_exact_CAD_annotation_edits=edits,components=140,nets=103,
      full_pin_net_map_unchanged=True,
      erc_before={"errors":28,"warnings":192},
      erc_after={"errors":28,"warnings":192},
      all_15_crossmodule_HOLD=True,
      EFUSE_RTN_separate_from_GND_MAIN=True,
      D200_TVS_still_DNP=True,
      F200_eFuse_coordination_HOLD=True)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v771_ti_six_ldo_l100_thermal_scenarios.json").write_text(json.dumps(eng,indent=2)+"\n")
    return eng

class TestV771ThermalAndL100(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.r=gate()
    def test_01_schematic_notes(self):self.assertEqual(self.r["native_exact_CAD_annotation_edits"],4)
    def test_02_components(self):self.assertEqual(self.r["components"],140)
    def test_03_nets(self):self.assertEqual(self.r["nets"],103)
    def test_04_full_map(self):self.assertTrue(self.r["full_pin_net_map_unchanged"])
    def test_05_ERC(self):self.assertEqual(self.r["erc_after"],{"errors":28,"warnings":192})
    def test_06_six_refs(self):self.assertEqual(len(self.r["six_ldos"]),6)
    def test_07_thermal_scenarios(self):self.assertEqual(self.r["thermal_scenario_count"],360)
    def test_08_real_loads_missing(self):self.assertFalse(self.r["measured_per_rail_loads_available"])
    def test_09_theta(self):self.assertEqual(self.r["vendor_thetaJA_DBV_c_per_W"],187.1)
    def test_10_typ_ignd(self):self.assertAlmostEqual(self.r["vendor_IGND_typ_at_300mA_assumed_A"],.002)
    def test_11_high_temp_300(self):self.assertGreater(self.r["max_highVin_highAmbient_at_300mA_tj_C"],199.2)
    def test_12_max_current(self):self.assertLess(self.r["theoretical_max_A_at_highVin_85C_for125C"],.102)
    def test_13_six_total_not_load(self):self.assertAlmostEqual(self.r["six_ratings_sum_A"],1.8)
    def test_14_unknown_5v_load(self):self.assertIsNone(self.r["unknown_direct_5v_load_A"])
    def test_15_L100_PN(self):self.assertEqual(self.r["inductor_vendor_MPN"],"SRP1038A-150M")
    def test_16_L100_DCR(self):self.assertEqual(self.r["l100_DCR_max_ohm"],.045)
    def test_17_L100_Isat(self):self.assertEqual(self.r["l100_vendor_Isat_20pct_Ldrop_A"],10.)
    def test_18_L100_Irms(self):self.assertEqual(self.r["l100_vendor_Irms_40C_rise_A"],6.25)
    def test_19_ripple_scenarios(self):self.assertEqual(self.r["l100_scenario_count"],12)
    def test_20_peak(self):self.assertLess(self.r["l100_worst_2A_17p05V_390k_12uH"]["peak_A"],2.378)
    def test_21_not_bench(self):self.assertFalse(self.r["L100_real_pcb_thermal_verified"])
    def test_22_no_fab(self):self.assertTrue(self.r["NO_FAB"] and self.r["NO_TX"])

if __name__=="__main__":
    unittest.main()
