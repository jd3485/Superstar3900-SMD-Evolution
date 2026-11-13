"""V7.62 true independent TPS26600 SHDN manual reset candidate, 7-sheet KiCad9 fail-closed."""
from pathlib import Path
from collections import Counter
import json,sys,re,unittest

ROOT=Path(__file__).resolve().parents[2]
OLD_AUX=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.57_TDK_CGA6_VENDOR_LAND_REVIEW_NOT_FOR_FAB"
NEW_AUX=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.62_EFUSE_SHDN_MANUAL_RESET_REVIEW_NOT_FOR_FAB"
OLD_ROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.61_U6207_SYMBOL_LIBRARY_REVIEW_NOT_FOR_FAB"
NEW_ROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.62_EFUSE_MANUAL_RESET_REVIEW_NOT_FOR_FAB"
OLD_LIB=ROOT/"04_KiCad/Librerie_Simboli_V7.61_SUPERVISOR_U6207_HOLD/S3900E.kicad_sym"
NEW_LIB=ROOT/"04_KiCad/Librerie_Simboli_V7.62_EFUSE_RESET_SW_HOLD/S3900E.kicad_sym"
OUT=ROOT/"03_Verifiche/V7.62/output-ci"
MASTER="S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
SYMBOL_ID="SW_EFUSE_SHDN_RESET_NO_REVIEW"

sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def pin_map(path):
    result={}
    for name,ps in nets(path).items():
        for pin in ps:
            assert pin not in result,("duplicate schematic pin",pin)
            result[pin]=name
    return result

def source_gate():
    old=(OLD_AUX/"01_EFUSE_AUX.kicad_sch").read_text(encoding="utf8")
    revised=(NEW_AUX/"01_EFUSE_AUX.kicad_sch").read_text(encoding="utf8")
    assert old.startswith("(kicad_sch") and revised.startswith("(kicad_sch")
    assert old.count('(no_connect (at 173 126)')==1
    assert revised.count('(label "EFUSE_SHDN_RESET_N" (at 173 126 0)')==1
    assert revised.count('(label "EFUSE_SHDN_RESET_N" (at 327.66 236.22 0)')==1
    assert revised.count('(label "GND_MAIN" (at 337.82 236.22 0)')==1
    assert '(label "EFUSE_RTN" (at 337.82 236.22 0)' not in revised
    assert revised.count('(property "Reference" "SW200"')==1
    assert revised.count('(property "Qualification" "V7.62 SHDN_MANUAL_RESET_SWITCH_MPN_FOOTPRINT_ACCESS_HOLD"')==1
    assert revised.count('(property "Footprint" "" (at 332.74 236.22 0)')==1
    # Extract exactly new embedded schematic switch symbol, and prove the
    # entire previous project library is byte-identical except this symbol.
    start=revised.index(f'(symbol "S3900E:{SYMBOL_ID}"')
    end=revised.index('\n (symbol "S3900E:R_EFUSE"',start)
    embedded=revised[start:end]
    a=OLD_LIB.read_text(encoding="utf8")
    b=NEW_LIB.read_text(encoding="utf8")
    assert a.endswith(")\n")
    assert b==a[:-2]+" "+embedded.replace(
        f'(symbol "S3900E:{SYMBOL_ID}"',
        f'(symbol "{SYMBOL_ID}"',1)+"\n)\n","Other project symbol lib definitions changed"
    # Prevent silent edits to baseline U200, R204 402k MODE, F200, nets.
    draft=revised.replace(f'(lib_symbols {embedded}\n (symbol "S3900E:R_EFUSE"',
                            '(lib_symbols (symbol "S3900E:R_EFUSE"',1)
    assert draft!=revised
    draft=draft.replace(
        '(label "EFUSE_SHDN_RESET_N" (at 173 126 0) (effects (font (size 1.016 1.016)) (justify left bottom)) (uuid "b7620000-0000-4000-8000-000000000001"))',
        '(no_connect (at 173 126) (uuid 4636269a-098e-4ced-858d-1c74e1fc78de))',1)
    draft=draft.replace(
        'SHDN verso SW200 momentaneo NO a GND_MAIN (NON RTN). MODE=402k latchoff, meccanica/prove HOLD; IMON/FLT NC.',
        'SHDN / IMON / FLT non collegati; MODE=R204 402k RTN -> LATCH-OFF, funzione/prove HOLD.',1)
    swstart=draft.index(f'(symbol (lib_id "S3900E:{SYMBOL_ID}")')
    swend=draft.rfind("\n)")
    assert swstart>0 and swend>swstart
    block=draft[swstart:swend]
    assert block.count("(label ")==2 and block.count("(symbol (lib_id")==1
    assert block.count('(text "V7.62 SW200 SPST-NO')==1
    assert '(at 332.74 236.22 0)' in block
    draft=draft[:swstart]+draft[swend:]
    assert draft==old,"Unexpected change to base eFuse schematic"
    for fn in ("02_BUCK_5V.kicad_sch","03_PLL_LDO_TCXO.kicad_sch","S3900E_AUX_POWER_V1_5.kicad_sch"):
        assert (OLD_AUX/fn).read_bytes()==(NEW_AUX/fn).read_bytes(),fn
    oldroot=(OLD_ROOT/MASTER).read_text(encoding="utf8")
    newroot=(NEW_ROOT/MASTER).read_text(encoding="utf8")
    assert newroot==oldroot.replace(
        "Gerarchico_Alimentazioni_V7.57_TDK_CGA6_VENDOR_LAND_REVIEW_NOT_FOR_FAB",
        "Gerarchico_Alimentazioni_V7.62_EFUSE_SHDN_MANUAL_RESET_REVIEW_NOT_FOR_FAB")
    oldtable=(OLD_ROOT/"sym-lib-table").read_text(encoding="utf8")
    newtable=(NEW_ROOT/"sym-lib-table").read_text(encoding="utf8")
    assert newtable==oldtable.replace(
        "Librerie_Simboli_V7.61_SUPERVISOR_U6207_HOLD",
        "Librerie_Simboli_V7.62_EFUSE_RESET_SW_HOLD")
    for fn in ("fp-lib-table","S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_pro"):
        assert (OLD_ROOT/fn).read_bytes()==(NEW_ROOT/fn).read_bytes()
    return embedded

def gate():
    embedded=source_gate()
    old=compmap(OUT/"v762.original.net")
    new=compmap(OUT/"v762.revised.net")
    assert len(old)==139,("baseline component count",len(old))
    assert len(new)==140,("revised component count",len(new))
    assert set(new)-set(old)=={"SW200"},("unexpected components",set(new)-set(old))
    assert {k:new[k] for k in old}==old,"Changed original component BOM/value/footprint"
    assert new["SW200"][1]=="MANUAL_RESET_NO_HOLD",new["SW200"]
    assert not new["SW200"][0],"Unqualified physical switch footprint must stay on HOLD"
    a=pin_map(OUT/"v762.original.net")
    b=pin_map(OUT/"v762.revised.net")
    assert all(b.get(k)==v for k,v in a.items()),"Original 139 component pins/net changed"
    assert ("U200","7") not in a,"SHDN originally NC"
    assert set(b)-set(a)=={("U200","7"),("SW200","1"),("SW200","2")},("unexpected new physical pins",set(b)-set(a))
    assert b[("U200","7")]==b[("SW200","1")]
    assert "SHDN" in b[("U200","7")].upper(),b[("U200","7")]
    assert b[("SW200","2")]==b[("U200","9")],"Reset must be referenced to U200 GND pin9"
    assert b[("SW200","2")]!=b[("U200","8")],"NEVER SHORT efuse RTN to system GND"
    assert b[("U200","8")]==b[("U200","17")]
    assert "EFUSE_RTN" in b[("U200","8")].upper()
    assert b[("U200","6")]==a[("U200","6")],"R204 MODE 402k latchoff must remain"
    assert len(nets(OUT/"v762.original.net"))==102
    assert len(nets(OUT/"v762.revised.net"))==103,"SHDN control net should be sole new rail"
    er0=native_erc(OUT/"v762.original.erc.rpt")
    er1=native_erc(OUT/"v762.revised.erc.rpt")
    assert er0["errors"]==28 and er0["warnings"]==214
    assert er1["errors"]<=28,("NEW electrical error not allowed",er1["errors"],er0["errors"])
    existing=Counter(json.dumps(x,sort_keys=True,ensure_ascii=False) for x in er0["findings"])
    revised=Counter(json.dumps(x,sort_keys=True,ensure_ascii=False) for x in er1["findings"])
    # New physical component is a candidate: do not obscure any new
    # library, power_pin_not_driven, or connection errors.
    errors_added=[]
    for serialized in (revised-existing).elements():
        d=json.loads(serialized)
        if d["severity"]=="error":
            errors_added.append(d)
    assert not errors_added,("New ERC errors",errors_added)
    report=dict(original_parts=139,new_parts=140,old_nets=102,new_nets=103,
       reset_to_gnd_pin9=True,return_isolated=True,manual_switch_in_bom=True,
       no_downstream_5v_or_mcu_requirement=True,
       erc_before={"errors":er0["errors"],"warnings":er0["warnings"]},
       erc_after={"errors":er1["errors"],"warnings":er1["warnings"]},
       physical_switch_mpn_qualified=False,footprint_qualified=False,
       accessible_switch_mechanics_approved=False,
       fault_recovery_hardware_validated=False,production_ready=False,
       NO_FAB=True,NO_TX=True)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v762.efuse_manual_reset_candidate.json").write_text(json.dumps(report,indent=2)+"\n")
    return report

class TestV762ManualRecovery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=gate()
    def test_01_parts(self):self.assertEqual(self.r["new_parts"],140)
    def test_02_nets(self):self.assertEqual(self.r["new_nets"],103)
    def test_03_gnd_reference(self):self.assertTrue(self.r["reset_to_gnd_pin9"])
    def test_04_rtn_isolated(self):self.assertTrue(self.r["return_isolated"])
    def test_05_physical_part(self):self.assertTrue(self.r["manual_switch_in_bom"])
    def test_06_no_downstream_supply(self):self.assertTrue(self.r["no_downstream_5v_or_mcu_requirement"])
    def test_07_erc_no_new_error(self):self.assertLessEqual(self.r["erc_after"]["errors"],28)
    def test_08_mpn_hold(self):self.assertFalse(self.r["physical_switch_mpn_qualified"])
    def test_09_footprint_hold(self):self.assertFalse(self.r["footprint_qualified"])
    def test_10_access_hold(self):self.assertFalse(self.r["accessible_switch_mechanics_approved"])
    def test_11_hardware_hold(self):self.assertFalse(self.r["fault_recovery_hardware_validated"])
    def test_12_pcb_hold(self):self.assertFalse(self.r["production_ready"])
    def test_13_no_fab(self):self.assertTrue(self.r["NO_FAB"] and self.r["NO_TX"])

if __name__=="__main__":
    unittest.main()
