"""V7.43: six sourced TPS7A20 rail outputs + separate thermal vs buck budget gates.
No connection/PCB modifications; calculations are board-specific illustrative stress.
"""
import json,math,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/"03_Verifiche/V7.43/MATRICE_CARICHI_TERMICA_5V_V743.json"
def read():
    d=json.loads(DATA.read_text(encoding="utf8"))
    for key,part in d["source_paths"].items():
        path=ROOT/part
        if not path.is_file():
            raise AssertionError(("missing source",key,path))
    return d

def embedded_label_map(s):
    labels={}
    for net,x,y in re.findall(r'\(label "([^"]+)" \(at ([-\d.]+) ([-\d.]+)',s):
        xy=(round(float(x),4),round(float(y),4))
        if xy in labels and labels[xy]!=net:
            raise AssertionError(("conflicting labels",xy,net,labels[xy]))
        labels[xy]=net
    return labels

def ref_value(s,ref):
    hits=re.findall(r'\(property "Reference" "'+re.escape(ref)+r'"[^\n]*\n\s*\(property "Value" "([^"]+)"',s)
    if len(hits)!=1:
        raise AssertionError((ref,hits))
    return hits[0]

def actual_ldo_rail(s,ref,domain):
    regex=r'\(symbol \(lib_id "S3900E:TPS7A2033_DBV(?:_DRAFT)?"\) \(at ([-\d.]+) ([-\d.]+) 0\)[\s\S]{0,380}?\(property "Reference" "'+re.escape(ref)+r'"'
    matches=list(re.finditer(regex,s))
    if len(matches)!=1:
        raise AssertionError((ref,len(matches)))
    x,y=float(matches[0].group(1)),float(matches[0].group(2))
    labels=embedded_label_map(s)
    if domain=="mcu":
        coords=[(x-10.16,y-10.16),(x+10.16,y-10.16),(x-10.16,y+10.16)]
    elif domain=="pll":
        coords=[(x-24,y-8),(x+24,y-8),(x-24,y+8)]
    else:raise ValueError(domain)
    return [labels.get((round(a,4),round(b,4))) for a,b in coords]

def ldo_power_w(i_a,vin=5.,vout=3.3,ignd_a=0.):
    if min(i_a,vin,vout,ignd_a)<0 or vin<vout:
        raise ValueError("invalid LDO power point")
    return (vin-vout)*i_a+vin*ignd_a

def thermal_junction_c(ambient_c,i_a,theta=187.1,vin=5.,vout=3.3,ignd_a=0.):
    if theta<=0:raise ValueError("invalid thermal resistance")
    return ambient_c+theta*ldo_power_w(i_a,vin,vout,ignd_a)

def max_i_nom_by_thermal(ambient_c,tjmax_c=125.,theta=187.1,vin=5.,vout=3.3,ignd_a=0.):
    if theta<=0 or vin<=vout or ignd_a<0:raise ValueError("invalid assumptions")
    return max(0.,((tjmax_c-ambient_c)/theta-vin*ignd_a)/(vin-vout))

def budget_required_measurements(d):
    for rail in d["rail_rows"]:
        if rail["load_max_known_a"] is None or rail["transient_max_known_a"] is None:
            raise RuntimeError("HOLD: actual loads and transients missing")
    for k in ("unknown_direct_5v_and_other_load_a","ambient_design_max_c","thermal_board_theta_actual_c_per_w","allowable_junction_margin_c"):
        if d[k] is None:
            raise RuntimeError("HOLD: unknown 5V consumers or board thermal environment")
    raise RuntimeError("HOLD: measured profiles and ground-return model not qualified")

class TestSixLDOsAndThermal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=read()
        cls.sources={k:(ROOT/p).read_text(encoding="utf8") for k,p in cls.d["source_paths"].items() if k in ("mcu","pll","root")}
    def test_01_six_distinct_sources(self):
        self.assertEqual(len(self.d["rail_rows"]),6)
        self.assertEqual(len({p["sheet"]+p["ref"] for p in self.d["rail_rows"]}),6)
    def test_02_actual_ldo_references_and_parts(self):
        for row in self.d["rail_rows"]:
            s=self.sources[row["sheet"]]
            self.assertEqual(ref_value(s,row["ref"]),"TPS7A2033PDBVR")
    def test_03_actual_pin_to_label_net_topology(self):
        for row in self.d["rail_rows"]:
            actual=actual_ldo_rail(self.sources[row["sheet"]],row["ref"],row["sheet"])
            expected=[row["vin_net"],row["output_net"],row["return_net"]]
            self.assertEqual(actual,expected,(row["ref"],actual,expected))
    def test_04_three_domains_unchanged(self):
        self.assertEqual(self.sources["root"].count("(sheet (at "),3)
        self.assertFalse(self.d["approval"]["root_interconnect_signed_off"])
    def test_05_buck_shared_2a(self):
        self.assertEqual(self.d["buck"]["max_continuous_output_a"],2)
        self.assertEqual(self.d["vendor"]["rated_output_current_a"],.3)
    def test_06_six_times_300ma_is_1p8a_rating_not_consumption(self):
        self.assertAlmostEqual(6*.3,1.8)
        self.assertAlmostEqual(2-6*.3,.2)
        self.assertIsNone(self.d["unknown_direct_5v_and_other_load_a"])
    def test_07_4_mcu_ldos_on_bead(self):
        m=[p for p in self.d["rail_rows"] if p["sheet"]=="mcu"]
        self.assertEqual(len(m),4)
        self.assertEqual({p["vin_net"] for p in m},{"5V_DIGITAL_FILTERED"})
        self.assertAlmostEqual(4*.3,1.2)
    def test_08_2_pll_ldos_bypass_bead(self):
        p=[p for p in self.d["rail_rows"] if p["sheet"]=="pll"]
        self.assertEqual(len(p),2)
        self.assertEqual({v["vin_net"] for v in p},{"5V_RF_PREREGULATED"})
    def test_09_vendor_dbv_thermal_theta(self):
        self.assertAlmostEqual(self.d["vendor"]["r_theta_ja_c_per_w_dbv"],187.1)
    def test_10_power_at_300ma_without_ignd(self):
        self.assertAlmostEqual(ldo_power_w(.3),.51)
    def test_11_300ma_temperature_rise_example(self):
        self.assertAlmostEqual(thermal_junction_c(0,.3),.51*187.1)
    def test_12_ambient_25C_300ma_nominal_stress(self):
        self.assertAlmostEqual(thermal_junction_c(25,.3),120.421)
    def test_13_ambient_85C_300ma_exceeds_125C(self):
        self.assertGreater(thermal_junction_c(85,.3),125)
        self.assertAlmostEqual(thermal_junction_c(85,.3),180.421)
    def test_14_ambient_85C_thermal_current_limit_is_not_300ma(self):
        self.assertAlmostEqual(max_i_nom_by_thermal(85),40/(187.1*1.7))
        self.assertLess(max_i_nom_by_thermal(85),.13)
    def test_15_ambient_60C_screen(self):
        self.assertAlmostEqual(max_i_nom_by_thermal(60),65/(187.1*1.7))
    def test_16_ignd_2ma_typ_at_300ma_increases_heat(self):
        self.assertAlmostEqual(ldo_power_w(.3,ignd_a=.002),.52)
        self.assertGreater(thermal_junction_c(85,.3,ignd_a=.002),thermal_junction_c(85,.3))
    def test_17_power_supply_fuse_and_ground_not_signed_off(self):
        self.assertFalse(self.d["approval"]["ground_return_signed_off"])
        self.assertFalse(self.d["approval"]["buck_total_current_verified"])
    def test_18_individual_loads_are_unknown(self):
        for row in self.d["rail_rows"]:
            self.assertIsNone(row["load_max_known_a"])
            self.assertIsNone(row["transient_max_known_a"])
    def test_19_thermal_theta_is_reference_not_measured_on_future_board(self):
        self.assertTrue(self.d["vendor"]["thermal_model_is_board_specific"])
        self.assertFalse(self.d["approval"]["actual_board_theta_verified"])
    def test_20_fail_closed_without_current_profiles(self):
        with self.assertRaisesRegex(RuntimeError,"HOLD"):
            budget_required_measurements(self.d)
    def test_21_invalid_operating_point_rejected(self):
        with self.assertRaises(ValueError):ldo_power_w(.1,vin=3,vout=3.3)
    def test_22_invalid_theta_rejected(self):
        with self.assertRaises(ValueError):max_i_nom_by_thermal(60,theta=0)
    def test_23_zero_ambient_heat_without_load_or_iq(self):
        self.assertAlmostEqual(thermal_junction_c(85,0),85)
    def test_24_all_fab_tx_flags_fail_closed(self):
        self.assertTrue(all(self.d["approval"][k] for k in ("NO_FAB","NO_GERBER","NO_TX")))
if __name__=="__main__":
    unittest.main()
