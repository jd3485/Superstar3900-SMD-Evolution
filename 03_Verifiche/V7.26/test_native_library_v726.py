"""V7.26 collision-safe manufacturer symbol library gate. 15 interfaces remain HOLD."""
import json, re, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
O_AUX=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.19_PLL_PINNET_NOT_FOR_FAB"
N_AUX=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.26_UNIQUE_SYMBOLS_NOT_FOR_FAB"
O_ROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.25_SIX_FOOTPRINTS_REVIEW_NOT_FOR_FAB"
N_ROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.26_UNIFIED_SYMBOL_LIB_NOT_FOR_FAB"
LIB=ROOT/"04_KiCad/Librerie_Simboli_V7.26_UNIFIED_NOT_FOR_FAB/S3900E.kicad_sym"
OUT=ROOT/"03_Verifiche/V7.26/output-ci"
RENAMES={"01_EFUSE_AUX.kicad_sch":("EFUSE","R_EFUSE","C_EFUSE"),
         "02_BUCK_5V.kicad_sch":("BUCK","R_BUCK","C_BUCK"),
         "03_PLL_LDO_TCXO.kicad_sch":("PLL","R_PLL","C_PLL")}
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def cuts(src,start):
    depth=0;quoted=False;escape=False
    for i in range(start,len(src)):
        ch=src[i]
        if quoted:
            if escape:escape=False
            elif ch=="\\":escape=True
            elif ch=='"':quoted=False
        else:
            if ch=='"':quoted=True
            elif ch=='(':depth+=1
            elif ch==')':
                depth-=1
                if depth==0:return src[start:i+1]
    raise ValueError("unbalanced symbol")

def definitions(text,prefix):
    out={}
    for match in re.finditer(r'\(symbol "'+re.escape(prefix)+r'([^"]+)"',text):
        name=match.group(1)
        if name in out:raise AssertionError("duplicate symbol "+name)
        out[name]=cuts(text,match.start())
    return out

def read_report():
    before=OUT/"v726.original.net";after=OUT/"v726.revised.net"
    assert before.is_file() and after.is_file(),"Required real KiCad CLI exports missing"
    old_nets=nets(before);new_nets=nets(after)
    assert len(old_nets)==100 and new_nets==old_nets, "any new/lost pin-net node = STOP"
    oldc=compmap(before);newc=compmap(after)
    assert len(oldc)==132 and oldc==newc, "132 references and footprints must remain identical"
    assert sum(not fp for fp,value in newc.values())==42
    a=native_erc(OUT/"v726.original.erc.rpt")
    b=native_erc(OUT/"v726.revised.erc.rpt")
    assert (a["errors"],a["warnings"])==(36,340),a
    assert b["errors"]==36,(a,b)
    assert b["warnings"] < 340,(a,b)
    original=(OUT/"v726.original.erc.rpt").read_text()
    revised=(OUT/"v726.revised.erc.rpt").read_text()
    before_sym=original.count("[lib_symbol_issues]")
    after_sym=revised.count("[lib_symbol_issues]")
    assert before_sym==117,(before_sym,after_sym)
    assert after_sym<before_sym, "symbol library repairs must remove real KiCad warnings"
    for rule in ("label_dangling","power_pin_not_driven","pin_not_driven"):
        assert revised.count("["+rule+"]")==original.count("["+rule+"]"),"Cannot hide/change any ERC HOLD "+rule
    data={"revision":"V7.26","real_KiCad_netlist":True,"components":132,"nets":100,
          "net_node_diff":0,"missing_footprints":42,"erc_old":[36,340],
          "erc_new":[b["errors"],b["warnings"]],
          "lib_symbol_warnings_old":before_sym,"lib_symbol_warnings_new":after_sym,
          "fabrication_release":False,"TX_release":False,"assembly_qualified":False,
          "cross_module_interfaces_OpenHold":15,"SG48_HOLD":True}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v726.native_library_parity.json").write_text(json.dumps(data,indent=2)+"\n")
    return data

class TestNativeUnifiedLibrary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=read_report()

    def test_01_no_pin_net_joins(self):self.assertEqual(self.data["net_node_diff"],0)
    def test_02_132_component_100_nets_42_unassigned(self):
        self.assertEqual((self.data["components"],self.data["nets"],self.data["missing_footprints"]),(132,100,42))
    def test_03_old_known_erc_errors_preserved(self):
        self.assertEqual(self.data["erc_old"],[36,340])
        self.assertEqual(self.data["erc_new"][0],36)
    def test_04_library_warnings_strict_decrease_native(self):
        self.assertLess(self.data["lib_symbol_warnings_new"],117)
        self.assertLess(self.data["erc_new"][1],340)
    def test_05_no_electrical_source_pin_or_transmission_released(self):
        self.assertEqual(self.data["cross_module_interfaces_OpenHold"],15)
        self.assertTrue(self.data["SG48_HOLD"])
        self.assertFalse(self.data["TX_release"] or self.data["fabrication_release"])
    def test_06_six_unique_sheet_scoped_rc_symbols(self):
        for filename,(suffix,r,c) in RENAMES.items():
            src=(N_AUX/filename).read_text()
            for old,new in (("R",r),("C",c)):
                self.assertIn('(symbol "S3900E:'+new+'"',src)
                self.assertIn('(lib_id "S3900E:'+new+'"',src)
                self.assertNotIn('(lib_id "S3900E:'+old+'"',src)
                for suffix in ("_0_1","_1_1"):
                    self.assertIn('(symbol "'+new+suffix+'"',src)
    def test_07_rest_of_each_legacy_aux_sheet_byte_identical(self):
        for file,(_,r,c) in RENAMES.items():
            old=(O_AUX/file).read_text()
            for former,target in (("R",r),("C",c)):
                old=old.replace('(symbol "S3900E:'+former+'"','(symbol "S3900E:'+target+'"')
                old=old.replace('(lib_id "S3900E:'+former+'"','(lib_id "S3900E:'+target+'"')
                for suffix in ("_0_1","_1_1"):
                    old=old.replace('(symbol "'+former+suffix+'"','(symbol "'+target+suffix+'"')
            self.assertEqual(old,(N_AUX/file).read_text())
    def test_08_aux_parent_identical(self):
        self.assertEqual((O_AUX/"S3900E_AUX_POWER_V1_5.kicad_sch").read_bytes(),
                         (N_AUX/"S3900E_AUX_POWER_V1_5.kicad_sch").read_bytes())
    def test_09_library_has_32_unambiguous_unique_main_symbols(self):
        lib=LIB.read_text()
        names=re.findall(r'\(symbol "([^"]+)"',lib)
        main=[x for x in names if not re.search(r'_[01]_1$',x)]
        self.assertEqual(len(main),32)
        self.assertEqual(len(main),len(set(main)))
        self.assertTrue(set(("R_EFUSE","R_BUCK","R_PLL","C_EFUSE","C_BUCK","C_PLL")).issubset(main))
        self.assertFalse("S3900E:R" in main or "S3900E:C" in main)
        self.assertIn("TLV320AIC3204_RHB32_DRAFT",main)
        self.assertIn("TPS26600_PWP",main)
        self.assertIn("COAX_L",main)
    def test_10_new_root_retargets_only_aux_sheet_and_symbol_library(self):
        old=(O_ROOT/"S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch").read_text()
        new=(N_ROOT/"S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch").read_text()
        self.assertIn("../Gerarchico_Alimentazioni_V7.26_UNIQUE_SYMBOLS_NOT_FOR_FAB",new)
        self.assertIn("NO FAB TX",new)
        self.assertIn("../Modulo_MCU_CODEC_V7.25_SIX_FOOTPRINTS_REVIEW_NOT_FOR_FAB",new)
        self.assertIn("../Modulo_RX_Test_50ohm_V7.14_LIB_DIAGNOSTIC_NOT_FOR_FAB",new)
        self.assertNotIn("V7.26_UNIQUE_SYMBOLS",old)
        self.assertEqual((O_ROOT/"fp-lib-table").read_bytes(),(N_ROOT/"fp-lib-table").read_bytes())
    def test_11_full_symbols_on_disk_registered(self):
        table=(N_ROOT/"sym-lib-table").read_text()
        self.assertEqual(table.count('(lib (name "S3900E")'),1)
        self.assertIn("../Librerie_Simboli_V7.26_UNIFIED_NOT_FOR_FAB/S3900E.kicad_sym",table)
    def test_12_no_EFUSE_GND_short_or_PwrFlag(self):
        lib=LIB.read_text()
        self.assertNotIn("PWR_FLAG",lib)
        self.assertFalse(self.data["assembly_qualified"])
        for path in (N_AUX/"01_EFUSE_AUX.kicad_sch",N_AUX/"02_BUCK_5V.kicad_sch",
                     N_AUX/"03_PLL_LDO_TCXO.kicad_sch"):
            self.assertNotIn("PWR_FLAG",path.read_text())
if __name__=="__main__":unittest.main()
