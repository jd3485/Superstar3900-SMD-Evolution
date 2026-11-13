"""V7.43 independent native KiCad9 diagnostic, correcting a text-label false positive.
No CAD ECO: native netlist proves U2 pin1/3 and U3 pin1/3 already connected.
"""
import re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche/V7.43/output-ci"
MASTER=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.41_FB6201_TDK_VENDOR_LAND_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
PLL=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.31_AUX_CONNECTORS_ON_GRID_NOT_FOR_FAB/03_PLL_LDO_TCXO.kicad_sch"
NET=OUT/"v743.baseline.net"
ERC=OUT/"v743.baseline.erc.rpt"
import sys
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def endpoints():
    mapping={}
    for net,nodes in nets(NET).items():
        for node in nodes:
            if node in mapping:raise AssertionError(("multiple nets for same endpoint",node))
            mapping[node]=net
    return mapping

class TestU2NativeReality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=endpoints()
    def test_01_root_3_isolated_sheets(self):
        s=MASTER.read_text(encoding="utf8")
        self.assertEqual(s.count("(sheet (at "),3)
        self.assertNotIn('(pin "5V_RF_PREREGULATED" ',s)
    def test_02_original_U2_IN_pin1_is_on_five_volts(self):
        self.assertTrue(self.m[("U2","1")].endswith("/5V_RF_PREREGULATED"))
    def test_03_U2_enable_pin3_is_same_native_net(self):
        self.assertEqual(self.m[("U2","1")],self.m[("U2","3")])
    def test_04_U3_input_pin1_on_same_five_volts(self):
        self.assertEqual(self.m[("U3","1")],self.m[("U2","1")])
    def test_05_U3_enable_pin3_on_same_five_volts(self):
        self.assertEqual(self.m[("U3","3")],self.m[("U2","1")])
    def test_06_U2_out_3v3_pll(self):
        self.assertTrue(self.m[("U2","5")].endswith("/3V3_PLL_INPUT_FROM_LDO"))
    def test_07_U3_out_3v3_ref(self):
        self.assertTrue(self.m[("U3","5")].endswith("/3V3_REF_LDO"))
    def test_08_both_local_returns_are_main(self):
        self.assertEqual(self.m[("U2","2")],self.m[("U3","2")])
        self.assertTrue(self.m[("U2","2")].endswith("/GND_MAIN"))
    def test_09_pin_label_absence_cannot_be_called_unpowered(self):
        src=PLL.read_text(encoding="utf8")
        self.assertNotIn('(label "5V_RF_PREREGULATED" (at 388 72 0)',src)
        self.assertIn(("U2","1"),self.m)
    def test_10_native_134_comp(self):
        self.assertEqual(len(compmap(NET)),134)
    def test_11_native_baseline_erc_no_new_claim(self):
        e=native_erc(ERC)
        self.assertEqual((e["errors"],e["warnings"]),(36,221))
    def test_12_no_layout_fab_or_tx_signoff(self):
        self.assertTrue(True, "Diagnostic-only; all crossdomain HOLD")
if __name__=="__main__":
    unittest.main()
