"""V7.44 reproducible TI/ST load anchors; conditional modes != full-board loads.
No CAD edits, no current signoff. Standard-library-only 23-test matrix gate.
"""
import json,math,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=ROOT/"03_Verifiche/V7.44"
DATA=HERE/"MATRICE_CONSUMI_VENDOR_CONDIZIONALI_V744.json"
def read():
    x=json.loads(DATA.read_text(encoding="utf8"))
    upstream=json.loads((ROOT/x["upstream"]).read_text(encoding="utf8"))
    return x,upstream
def example(x,id,mode,kind):
    rows=[v for v in x["source_evidence"] if v["id"]==id]
    if len(rows)!=1:raise AssertionError((id,rows))
    m=[a for a in rows[0]["examples"] if a["mode"]==mode and a["type"]==kind]
    if len(m)!=1:raise AssertionError((id,mode,kind,m))
    return m[0]["value"]*0.001
def p_ldo(i_a,vin=5,vout=3.3,ground_current=0):
    if i_a<0 or ground_current<0 or vin<=vout:raise ValueError("invalid point")
    return (vin-vout)*i_a + vin*ground_current
def thermal(i_a,ambient_c,theta=187.1,vin=5,vout=3.3,ground_current=0):
    if theta<=0:raise ValueError("invalid thermal reference")
    return ambient_c+theta*p_ldo(i_a,vin,vout,ground_current)
def conditional_remaining_a(device_a,ambient_c,tj_limit_c=125,theta=187.1):
    if device_a<0 or theta<=0:raise ValueError("invalid input")
    return max(0,(tj_limit_c-ambient_c)/(theta*1.7)-device_a)
def signoff(x,upstream):
    if not x["approval"]["full_buck_budget_approved"]:
        raise RuntimeError("HOLD: missing all-channel maximum power budget")
    if not x["approval"]["board_thermal_budget_approved"]:
        raise RuntimeError("HOLD: PCB thermal not validated")
    raise RuntimeError("HOLD: physical reverse current and ground return")

class TestVendorConditionalLoads(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.x,cls.u=read()
        cls.r={row["ref"]:row for row in cls.u["rail_rows"]}
        cls.s={i["id"]:i for i in cls.x["source_evidence"]}
    def test_01_all_upstream_six_rails_preserved(self):
        self.assertEqual(len(self.r),6)
        self.assertEqual({k for k in self.r},{"U6203","U6204","U6205","U6206","U2","U3"})
    def test_02_validated_crossmodule_remains_unconnected(self):
        self.assertFalse(self.u["approval"]["root_interconnect_signed_off"])
        self.assertFalse(self.x["approval"]["cross_domain_connection_approved"])
    def test_03_pll_vendor_source_and_supply_rail(self):
        a=self.s["LMX2572"]
        self.assertEqual((a["ldo"],a["rail"]),( "U2",self.r["U2"]["output_net"]))
        self.assertIn("lmx2572.pdf",a["pdf"])
    def test_04_pll_all_4_active_typ_modes(self):
        vals=[v["value"] for v in self.s["LMX2572"]["examples"] if v["mode"]!="power_down"]
        self.assertEqual(vals,[75,79,82,86])
        self.assertTrue(all(v["type"]=="typ" for v in self.s["LMX2572"]["examples"]))
    def test_05_pll_powerdown_is_typ_not_guaranteed(self):
        self.assertAlmostEqual(example(self.x,"LMX2572","power_down","typ"),.0025)
    def test_06_pll_86ma_vcc_current_example(self):
        self.assertAlmostEqual(example(self.x,"LMX2572","rf_divided_fpd100MHz_icp2p5mA","typ"),.086)
    def test_07_pll_86ma_dissipation_5to3p3(self):
        self.assertAlmostEqual(p_ldo(.086),.1462)
    def test_08_pll_86ma_85C_hypothetical_theta(self):
        self.assertAlmostEqual(thermal(.086,85),112.35402)
        self.assertGreater(thermal(.086,85),85)
    def test_09_pll_86ma_is_not_worst_case_at_85c(self):
        self.assertIsNone(self.s["LMX2572"]["datasheet_max_for_these_examples_mA"])
        self.assertEqual(self.s["LMX2572"]["temp_data_c"],25)
        self.assertIsNone(self.r["U2"]["load_max_known_a"])
    def test_10_conditional_pll_85C_headroom_no_other_load(self):
        self.assertAlmostEqual(conditional_remaining_a(.086,85), (125-85)/(187.1*1.7)-.086)
        self.assertLess(conditional_remaining_a(.086,85),.04)
    def test_11_st_170mhz_85C_max_peripherals_off(self):
        self.assertAlmostEqual(example(self.x,"STM32G474","run_170MHz_85C","max"),.042)
    def test_12_st_170mhz_25C_typ(self):
        self.assertAlmostEqual(example(self.x,"STM32G474","run_170MHz_25C","typ"),.0295)
    def test_13_st_170mhz_max_25C_vs_85C(self):
        self.assertLess(example(self.x,"STM32G474","run_170MHz_25C","max"),
                        example(self.x,"STM32G474","run_170MHz_85C","max"))
    def test_14_st_85C_42ma_only_if_peripherals_off(self):
        a=self.s["STM32G474"]
        self.assertTrue(a["peripherals_gpio_adc_dac_dma_usb_unknown"])
        self.assertIn("ALL_PERIPHERALS_DISABLED",a["scope"])
        self.assertEqual((a["ldo"],a["rail"]),("U6204",self.r["U6204"]["output_net"]))
        self.assertIsNone(self.r["U6204"]["load_max_known_a"])
    def test_15_st_42ma_conditional_thermal_85C(self):
        self.assertAlmostEqual(p_ldo(.042),.0714)
        self.assertAlmostEqual(thermal(.042,85),98.35894)
    def test_16_st_example_not_upper_bound_on_total_rail(self):
        self.assertFalse(self.x["approval"]["board_thermal_budget_approved"])
        self.assertIsNone(self.r["U6204"]["transient_max_known_a"])
    def test_17_codec_two_rails_not_collapsed(self):
        a=self.s["TLV320AIC3204"]
        self.assertEqual(a["rail_io"],self.r["U6205"]["output_net"])
        self.assertEqual(a["rail_ldoin"],self.r["U6206"]["output_net"])
        self.assertIsNone(a["available_io_rail_current_max_mA"])
        self.assertIsNone(a["available_ldoin_rail_current_max_mA"])
    def test_18_codec_150ma_source_capability_not_load(self):
        a=self.s["TLV320AIC3204"]
        self.assertTrue(a["source_capability_is_not_current_draw"])
        self.assertEqual(a["source_capability_recommendation_mA"],150)
    def test_19_codec_dvdd_peak_not_ldoin_current(self):
        self.assertTrue(self.s["TLV320AIC3204"]["dvdd_processing_peak_not_ldoin_input_current"])
        self.assertIsNone(self.r["U6206"]["load_max_known_a"])
    def test_20_audio_clock_and_ref_loads_unknown(self):
        for ref in ("U6203","U3"):
            self.assertIsNone(self.r[ref]["load_max_known_a"])
    def test_21_three_firmware_modes_unconfigured(self):
        self.assertEqual({p["name"] for p in self.x["profiles"]},{"RX_ACTIVE","RX_SCAN","STANDBY"})
        for p in self.x["profiles"]:
            self.assertIsNone(p["codec_register_image"])
            self.assertIsNone(p["all_other_loads_a"])
            self.assertIsNone(p["ambient_max_c"])
    def test_22_worst_case_signoff_refused(self):
        with self.assertRaisesRegex(RuntimeError,"HOLD"):
            signoff(self.x,self.u)
    def test_23_no_fab_gerber_tx(self):
        for n in ("NO_FAB","NO_GERBER","NO_TX"):
            self.assertTrue(self.x["approval"][n])
    def test_24_no_fake_static_thermal_with_negative_power(self):
        with self.assertRaises(ValueError):
            p_ldo(-.001)
    def test_25_actual_board_theta_not_claimed(self):
        self.assertFalse(self.x["nominal_operating_point"]["board_theta_measured"])
        self.assertIsNone(self.x["nominal_operating_point"]["ignd_a_unbounded"])
if __name__=="__main__":
    unittest.main()
