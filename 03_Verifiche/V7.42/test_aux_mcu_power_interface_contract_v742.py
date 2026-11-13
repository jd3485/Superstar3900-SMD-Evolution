"""V7.42: fail-closed source-backed contract for AUX-to-MCU 5V power.
No CAD edits, so no new netlist/ERC run is claimed. This gate DOES NOT authorize a bridge.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT/"03_Verifiche/V7.42/CONTRATTO_INTERFACCIA_AUX_MCU_POWER_V742.json"

def load():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))

def source(c, key):
    location = c[key]["schematic"] if isinstance(c[key],dict) else c[key]
    p = ROOT / location
    if not p.is_file():
        raise FileNotFoundError(p)
    return p.read_text(encoding="utf-8")

def ref_value(s, reference):
    # Fail closed on missing/duplicate instantiation, not library template references.
    pattern = r'\(property "Reference" "'+re.escape(reference)+r'"[^\n]*\n\s*\(property "Value" "([^"]+)"'
    matches = re.findall(pattern,s)
    if len(matches)!=1:
        raise AssertionError((reference,matches))
    return matches[0]

def cap_at(s, ref):
    return ref_value(s,ref).split()[0]

def actual_power_pin_labels(s):
    lab = {}
    for name,x,y in re.findall(r'\(label "([^"]+)" \(at ([-\d.]+) ([-\d.]+)',s):
        coord=(round(float(x),4),round(float(y),4))
        if coord in lab and lab[coord]!=name:
            raise AssertionError(("contradictory label", coord))
        lab[coord]=name
    return lab

def internal_power_bead_pins(s):
    labels=actual_power_pin_labels(s)
    # FB6201 origin is 750,340; embedded FB_DRAFT pin1 is +5.08 upward,
    # pin2 -5.08 downward, rotation 0. Check actual native source instance.
    assert '(symbol (lib_id "S3900E:FB_DRAFT") (at 750.0000 340.0000 0)' in s
    assert ref_value(s,"FB6201")=="600R@100MHz_TDK_2A_REVIEW"
    i=s.index('(property "Reference" "FB6201"')
    inst=s[i:s.index("(instances ",i)]
    assert '(property "MPN" "MPZ2012S601ATD25"' in inst
    assert 'S3900E_TDK_MPZ2012_V741_HOLD:TDK_MPZ2012_0805_POWER_BEAD_REFLOW_REVIEW' in inst
    return [labels.get((750.0,334.92)),labels.get((750.0,345.08))]

class TestAuxMCUPowerContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=load()
        cls.root=source(cls.c,"master")
        cls.aux=source(cls.c,"aux")
        cls.buck=source(cls.c,"buck")
        cls.efuse=source(cls.c,"efuse")
        cls.pll=source(cls.c,"pll")
        cls.mcu=source(cls.c,"mcu")
    def test_01_contract_is_hold(self):
        self.assertEqual(self.c["status"],"INTERFACE_PROPOSED_HOLD_NO_NET_CONNECTION")
        self.assertFalse(self.c["power_link"]["approved"])
        self.assertFalse(self.c["return_link"]["approved"])
    def test_02_master_has_three_isolated_sheets(self):
        self.assertEqual(self.root.count("(sheet (at "),3)
        self.assertEqual(len(re.findall(r'\(property "Sheetfile" "',self.root)),3)
        self.assertEqual(len(re.findall(r'\(pin "[^"]+" (?:input|output|passive|bidirectional)',self.root)),0)
    def test_03_mcu_not_exposed_as_hierarchical_global_power(self):
        self.assertNotIn("(hierarchical_label ",self.mcu)
        self.assertNotIn("(global_label ",self.mcu)
        self.assertNotIn("(pin \"5V_RF_PREREGULATED\"",self.root)
    def test_04_aux_hierarchy_is_not_root_interface(self):
        self.assertIn('(pin "5V_RF_PREREGULATED" output',self.aux)
        self.assertIn('(pin "GND_MAIN" passive',self.aux)
        self.assertIn('(hierarchical_label "5V_RF_PREREGULATED" (shape output)',self.buck)
    def test_05_buck_and_efuse_are_real_references(self):
        self.assertEqual(ref_value(self.buck,"U100"),"TPS54202DDCR")
        self.assertEqual(ref_value(self.efuse,"U200"),"TPS26600PWPT")
        self.assertIn("1.5A",ref_value(self.efuse,"F200"))
        self.assertTrue(self.c["efuse"]["fuse_input_is_not_5v_output_current_rating"])
    def test_06_buck_local_output_capacitance(self):
        self.assertEqual(cap_at(self.buck,"C103"),"22uF")
        self.assertEqual(cap_at(self.buck,"C104"),"22uF")
        self.assertEqual(sum(self.c["buck"]["output_caps_nominal_uF"].values()),44)
    def test_07_mcublock_bead_nets_at_physical_endpoints(self):
        actual=internal_power_bead_pins(self.mcu)
        self.assertEqual(actual,["5V_RF_PREREGULATED","5V_DIGITAL_FILTERED"])
        self.assertEqual(self.c["power_link"]["sink_pin"],"1")
        self.assertEqual(self.c["power_link"]["sink_output_pin"],"2")
    def test_08_no_implicit_ground_join(self):
        self.assertIn('GND_MAIN',self.aux)
        self.assertIn('(label "GND"',self.mcu)
        self.assertFalse(self.c["return_link"]["approved"])
    def test_09_six_independent_ldos_in_source(self):
        for ref in self.c["ldo_rails"]["MCU"]:
            self.assertEqual(ref_value(self.mcu,ref),"TPS7A2033PDBVR")
        for ref in self.c["ldo_rails"]["AUX_PLL"]:
            self.assertEqual(ref_value(self.pll,ref),"TPS7A2033PDBVR")
        self.assertEqual(len(self.c["ldo_rails"]["MCU"])+len(self.c["ldo_rails"]["AUX_PLL"]),6)
    def test_10_nominal_worst_case_consumes_1p8_of_2A(self):
        v=self.c["limits"]
        self.assertAlmostEqual(6*self.c["ldo_rails"]["max_nominal_output_per_ldo_a"],1.8)
        self.assertAlmostEqual(v["buck_rated_output_a"]-v["sum_six_ldo_ratings_a"],0.2)
        self.assertTrue(v["headroom_is_not_guaranteed"])
    def test_11_bead_vendor_current_is_not_buck_sizing(self):
        f=self.c["filters"]["FB6201"]
        self.assertEqual((f["z_100mhz_nom_ohm"],f["rated_current_a"],f["dcr_max_ohm"]),(600,2,0.1))
        self.assertTrue(f["footprint_review_only"])
    def test_12_required_unknowns_remain_fail_closed(self):
        required={"steady_state_load_current_per_rail_and_other_5v_consumers",
                  "all_5v_return_paths_and_ground_joins",
                  "power_down_reverse_current_and_prebias",
                  "buck_stability_44uF_out_plus_isolated_14p1uF"}
        self.assertTrue(required.issubset(set(self.c["unknowns"])))
        self.assertGreaterEqual(len(self.c["unknowns"]),8)
    def test_13_never_claim_cad_approved(self):
        approval=self.c["approval"]
        for k in ("physical_crossmodule_net_exists","power_budget_signed_off",
                  "ground_return_signed_off","layout_drc_signed_off","simulation_signed_off"):
            self.assertFalse(approval[k], k)
    def test_14_no_fabrication_or_transmission(self):
        self.assertTrue(all(self.c["approval"][k] for k in ("NO_FAB","NO_GERBER","NO_TX")))
    def test_15_no_power_flag_artifact(self):
        self.assertNotIn('PWR_FLAG',self.root)
    def test_16_dont_confuse_input_fuse_with_buck_output(self):
        self.assertIn("1.5A",self.c["efuse"]["fuse_input_rating_label"])
        self.assertEqual(self.c["buck"]["rated_output_current_a"],2.0)
        self.assertNotEqual(1.5,2.0)

if __name__ == "__main__":
    unittest.main()
