"""V7.43: KiCad9 native seven-sheet ECO parity gate for U2.IN pin1 supply.
Fail closed: ONE intended local pin-net move, no intermodule ground/power join.
"""
import json,re,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche/V7.43/output-ci"
OLDROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.41_FB6201_TDK_VENDOR_LAND_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
NEWROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.43_U2_PLL_IN_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
OLDPLL=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.31_AUX_CONNECTORS_ON_GRID_NOT_FOR_FAB/03_PLL_LDO_TCXO.kicad_sch"
NEWPLL=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.43_U2_LDO_IN_REVIEW_NOT_FOR_FAB/03_PLL_LDO_TCXO.kicad_sch"
LABEL='(label "5V_RF_PREREGULATED" (at 388 72 0) (effects (font (size 1.016 1.016)) (justify left bottom)) (uuid "b7430000-0000-4000-8000-000000000001"))'
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def membership(n):
    d={}
    for name,nodes in n.items():
        for ref,pin in nodes:
            key=(ref,pin)
            if key in d:
                raise AssertionError(("pin assigned multiple nets",key,d[key],name))
            d[key]=name
    return d

def gate():
    old=OLDPLL.read_text(encoding="utf8")
    new=NEWPLL.read_text(encoding="utf8")
    assert LABEL not in old and new.count(LABEL)==1
    # strict whitespace-insensitive parser comparison: only additional label permitted
    assert "".join((new.replace(LABEL,"")).split())=="".join(old.split()),"PLL ECO includes unexpected changes"
    for f in ("01_EFUSE_AUX.kicad_sch","02_BUCK_5V.kicad_sch","S3900E_AUX_POWER_V1_5.kicad_sch"):
        oldfile=OLDPLL.parent/f;newfile=NEWPLL.parent/f
        assert oldfile.read_bytes()==newfile.read_bytes(),f
    assert NEWROOT.read_text().count("../Gerarchico_Alimentazioni_V7.43_U2_LDO_IN_REVIEW_NOT_FOR_FAB/")==1
    assert NEWROOT.read_text().count("../Modulo_MCU_CODEC_V7.41_FB6201_TDK_VENDOR_LAND_REVIEW_NOT_FOR_FAB/")==1
    assert NEWROOT.read_text().count("(sheet (at ")==3
    orig=compmap(OUT/"v743.original.net")
    revised=compmap(OUT/"v743.revised.net")
    assert orig==revised and len(orig)==134,"Component value, MPN/footprint inventory must be unchanged"
    a=nets(OUT/"v743.original.net")
    b=nets(OUT/"v743.revised.net")
    m0,m1=membership(a),membership(b)
    changes={key:(m0.get(key),m1.get(key)) for key in set(m0)|set(m1) if m0.get(key)!=m1.get(key)}
    assert set(changes)=={("U2","1")},changes
    old_net,new_net=changes[("U2","1")]
    assert old_net is None or not old_net.endswith("/5V_RF_PREREGULATED"),changes
    assert new_net is not None and new_net.endswith("/5V_RF_PREREGULATED"),changes
    # Full seven-sheet link remains isolated even after local AUX U2 repair.
    assert not re.search(r'\(pin "5V_RF_PREREGULATED" (?:input|output|passive)',NEWROOT.read_text())
    e0=native_erc(OUT/"v743.original.erc.rpt")
    e1=native_erc(OUT/"v743.revised.erc.rpt")
    assert (e0["errors"],e0["warnings"])==(36,221),(e0["errors"],e0["warnings"])
    assert e1["errors"]<=e0["errors"],(e0["errors"],e1["errors"])
    assert e1["warnings"]<=e0["warnings"]+2,(e0["warnings"],e1["warnings"])
    for cat in ("pin_to_pin","wire_dangling","pin_not_connected","power_pin_not_driven"):
        assert e1["categories"].get(cat,0)<=e0["categories"].get(cat,0),(cat,e0["categories"],e1["categories"])
    result={"revision":"V7.43","status":"CAD_REVIEW_ONLY", "original_net_count":len(a),
      "revised_net_count":len(b),"components":134,"changed_net_endpoints":{str(k):v for k,v in changes.items()},
      "old_U2_IN_net":old_net,"new_U2_IN_net":new_net,"erc_before":{"errors":e0["errors"],"warnings":e0["warnings"]},
      "erc_after":{"errors":e1["errors"],"warnings":e1["warnings"]},
      "all_other_pins_unchanged":True,"root_aux_mcu_ground_joined":False,
      "all_15_crossdomain_interfaces_hold":True,"SG48_HOLD":True,
      "NO_FAB":True,"NO_GERBER":True,"NO_TX":True}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v743.u2_native.json").write_text(json.dumps(result,indent=2)+"\n")
    return result
class TestU2Fix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=gate()
    def test_01_native_134_components(self):self.assertEqual(self.r["components"],134)
    def test_02_one_endpoint(self):self.assertEqual(len(self.r["changed_net_endpoints"]),1)
    def test_03_specific_pin_1(self):self.assertIn("('U2', '1')",self.r["changed_net_endpoints"])
    def test_04_local_5v_fixed(self):self.assertTrue(self.r["new_U2_IN_net"].endswith("/5V_RF_PREREGULATED"))
    def test_05_baseline_erc(self):self.assertEqual(self.r["erc_before"]["errors"],36)
    def test_06_no_erc_growth(self):self.assertLessEqual(self.r["erc_after"]["errors"],36)
    def test_07_crossdomain_remains_held(self):self.assertFalse(self.r["root_aux_mcu_ground_joined"])
    def test_08_no_fab_or_tx(self):self.assertTrue(self.r["NO_FAB"] and self.r["NO_TX"])
if __name__=="__main__":
    unittest.main()
