"""V7.45: actual seven-sheet KiCad9 pin-net graph for PLL/TCXO supply paths.
USES EXISTING V7.43 native export: no new workflow, no CAD/physical signoff.
"""
import json, re, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"03_Verifiche/V7.45/MAPPA_PLL_TCXO_CARICHI_NATIVE_V745.json"
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def read_source_parts(path):
    text=path.read_text(encoding="utf8")
    matches=re.findall(r'\(property "Reference" "([^"]+)"[^\n]*\n\s*\(property "Value" "([^"]+)"',text)
    d={}
    for ref,value in matches:
        if ref in d:raise AssertionError(("duplicate symbol",ref))
        d[ref]=value
    return d

def graph(filename):
    bynet=nets(filename)
    pin_to_net={}
    for net,pins in bynet.items():
        for endpoint in pins:
            if endpoint in pin_to_net:
                raise AssertionError(("pin in multiple nets",endpoint,net,pin_to_net[endpoint]))
            pin_to_net[endpoint]=net
    return bynet,pin_to_net

class TestV745NativePLLTcxo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=json.loads(MODEL.read_text(encoding="utf8"))
        cls.s=read_source_parts(ROOT/cls.d["pll_source"])
        cls.master=(ROOT/cls.d["native_master"]).read_text(encoding="utf8")
        cls.bynet,cls.pin=graph(ROOT/cls.d["netlist_generated_by_existing_workflow"])
        cls.pll=cls.d["pll_rails"]["pll_input_3v3"]
        cls.ref=cls.d["pll_rails"]["reference_3v3"]
        cls.pll_supply=cls.pin[("U2","5")]
        cls.ref_supply=cls.pin[("U3","5")]
    def test_01_exact_master_3_sheet_gate(self):
        self.assertEqual(self.master.count("(sheet (at "),3)
        self.assertNotIn('(pin "5V_RF_PREREGULATED"',self.master)
    def test_02_existing_native_baseline_101_nets(self):
        self.assertEqual(len(self.bynet),101)
    def test_03_separate_three_volt_domains(self):
        self.assertTrue(self.pll_supply.endswith("/3V3_PLL_INPUT_FROM_LDO"))
        self.assertTrue(self.ref_supply.endswith("/3V3_REF_LDO"))
        self.assertNotEqual(self.pll_supply,self.ref_supply)
    def test_04_pll_ic_and_bead_mpn(self):
        self.assertEqual(self.s["U1"],"LMX2572RHA")
        self.assertEqual(self.s["U2"],"TPS7A2033PDBVR")
        self.assertEqual(self.s["U3"],"TPS7A2033PDBVR")
    def test_05_six_resistors_in_pll_supplier_rail(self):
        for res in self.pll["series_0ohm"]:
            self.assertEqual(self.s[res],"0R")
            self.assertEqual(self.pin[(res,"2")],self.pll_supply,res)
    def test_06_each_resistor_feeds_matching_lmx_pin(self):
        for res,expected in self.pll["series_0ohm"].items():
            supply=self.pin[(res,"1")]
            self.assertEqual(supply,self.pin[("U1",expected["device_pin"])],res)
            self.assertTrue(supply.endswith("/"+expected["device_domain"]),(res,supply))
            self.assertNotEqual(supply,self.pll_supply)
    def test_07_distinct_lmx_supply_domain_nodes(self):
        self.assertEqual(len({self.pin[(r,"1")] for r in self.pll["series_0ohm"]}),6)
    def test_08_do_not_multiply_full_chip_current_by_six(self):
        self.assertEqual(self.pll["datasheet_current_mA_typ_at_25C"],[75,79,82,86])
        self.assertEqual(len(self.pll["series_0ohm"]),6)
        self.assertIsNone(self.pll["max_all_operating_modes_mA"])
    def test_09_lmx_supply_not_directly_same_net_as_3v3_after_r0(self):
        for pin in ("7","11","15","21","26","37"):
            self.assertNotEqual(self.pin[("U1",pin)],self.pll_supply)
    def test_10_reference_y1_matches_real_mpn(self):
        self.assertEqual(self.s["Y1"],self.ref["tcxo_part"])
        self.assertEqual(self.ref["tcxo_part"],"7N-12.800MBP-T")
    def test_11_y1_vcc_pin9_from_u3_out5(self):
        self.assertEqual(self.pin[("Y1",self.ref["tcxo_vcc_pin"])],self.ref_supply)
    def test_12_reference_pullup_r60_at_ldo_out(self):
        self.assertEqual(self.s["R60"],self.ref["pullup_value"])
        self.assertEqual(self.pin[("R60","2")],self.ref_supply)
    def test_13_r60_goes_to_y1_control(self):
        self.assertEqual(self.pin[("R60","1")],self.pin[("Y1",self.ref["tcxo_ctrl_pin"])])
        self.assertNotEqual(self.pin[("R60","1")],self.ref_supply)
    def test_14_tcxo_max_is_device_figure_not_rail_sum(self):
        self.assertEqual(self.ref["tcxo_supply_max_mA_per_referenced_distributor"],10)
        self.assertIsNone(self.ref["other_load_max_mA"])
    def test_15_pin10_remains_hold(self):
        self.assertTrue(self.ref["tcxo_aFC_pin10_ground_or_AFC_unresolved"])
        self.assertFalse(self.d["signoff"]["tcxo_pin10_qualified"])
    def test_16_original_aux_5v_does_not_supply_mcu_bead_by_top_level(self):
        self.assertTrue(self.pin[("U2","1")].endswith("/5V_RF_PREREGULATED"))
        self.assertNotEqual(self.pin[("U2","1")],self.pin[("FB6201","1")])
    def test_17_ground_return_not_automatically_joined(self):
        self.assertNotEqual(self.pin[("U2","2")],self.pin[("U6205","2")])
        self.assertFalse(self.d["signoff"]["root_aux_mcu_power_connected"])
    def test_18_native_erc_observed_not_zero(self):
        erc=native_erc(ROOT/self.d["erc_generated_by_existing_workflow"])
        self.assertEqual((erc["errors"],erc["warnings"]),(36,221))
    def test_19_none_of_6_output_ratings_imply_total_current(self):
        self.assertFalse(self.d["signoff"]["six_ldo_total_worstcase_current"])
        self.assertFalse(self.d["signoff"]["reference_rail_total_current"])
        self.assertFalse(self.d["signoff"]["pll_rail_total_current"])
    def test_20_no_fabrication_gerber_pcbway_or_tx(self):
        self.assertTrue(all(self.d["signoff"][key] for key in ("NO_FAB","NO_GERBER","NO_PCBWAY","NO_TX")))
if __name__=="__main__":
    unittest.main()
