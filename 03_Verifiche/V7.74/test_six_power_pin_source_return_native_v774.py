"""V7.74: six real TPS26600/TPS7A20 power-input/return native evidence; never waive ERC."""
from pathlib import Path
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[2]
A0=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.72_PLL_SIX_LDO_BYPASS_GRID_REVIEW_NOT_FOR_FAB"
A1=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.74_SIX_PWR_SOURCE_RETURN_PROVENANCE_HOLD"
M0=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.60_SUPERVISOR_C6231_GRID_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
M1=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.74_U6203_PWR_SOURCE_RETURN_PROVENANCE_HOLD/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
R0=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.72_PLL_SIX_LDO_BYPASS_GRID_REVIEW_NOT_FOR_FAB"
R1=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.74_SIX_PWR_SOURCE_RETURN_PROVENANCE_HOLD"
OUT=ROOT/"03_Verifiche/V7.74/output-ci"
MASTER="S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc
SHEETS=[
 (A0/"01_EFUSE_AUX.kicad_sch",A1/"01_EFUSE_AUX.kicad_sch","U200","a7740000-0000-4000-8000-000000000201"),
 (A0/"03_PLL_LDO_TCXO.kicad_sch",A1/"03_PLL_LDO_TCXO.kicad_sch","U2","a7740000-0000-4000-8000-000000000202"),
 (M0,M1,"U6203","a7740000-0000-4000-8000-000000000203")]
TARGETS=[("U6203","1","5V_DIGITAL_FILTERED"),("U6203","2","GND"),
 ("U200","1","EFUSE_VIN"),("U200","8","EFUSE_RTN"),
 ("U2","1","5V_RF_PREREGULATED"),("U2","2","GND_MAIN")]
def source_gate():
    for old,new,ref,uuid in SHEETS:
        a=old.read_text().rstrip()
        b=new.read_text().rstrip()
        assert a.endswith(")") and b.startswith(a[:-1]) and b.endswith(")"),ref
        added=b[len(a[:-1]):-1].strip()
        assert added.startswith('(text "V7.74 POWER HOLD '+ref),ref
        assert added.count('(text "')==1 and added.count(uuid)==1
        assert "NO FAB" in added and ("PWR_FLAG" in added or "Never bridge" in added)
    for n in ("02_BUCK_5V.kicad_sch","S3900E_AUX_POWER_V1_5.kicad_sch"):
        assert (A0/n).read_bytes()==(A1/n).read_bytes()
    orig=(R0/MASTER).read_text()
    changed=orig.replace("Gerarchico_Alimentazioni_V7.72_PLL_SIX_LDO_BYPASS_GRID_REVIEW_NOT_FOR_FAB",
      "Gerarchico_Alimentazioni_V7.74_SIX_PWR_SOURCE_RETURN_PROVENANCE_HOLD").replace(
      "Modulo_MCU_CODEC_V7.60_SUPERVISOR_C6231_GRID_REVIEW_NOT_FOR_FAB",
      "Modulo_MCU_CODEC_V7.74_U6203_PWR_SOURCE_RETURN_PROVENANCE_HOLD")
    assert changed==(R1/MASTER).read_text()
    for n in ("fp-lib-table","sym-lib-table","S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_pro"):
        assert (R0/n).read_bytes()==(R1/n).read_bytes()
def pinmap(path):
    out={}
    for net,nodes in nets(path).items():
        for node in nodes:
            assert node not in out,node
            out[node]=net
    return out
def gate():
    source_gate()
    a=OUT/"v774.original.net";b=OUT/"v774.revised.net"
    assert compmap(a)==compmap(b) and len(compmap(b))==140
    assert nets(a)==nets(b) and len(nets(b))==103
    p=pinmap(b)
    assert p==pinmap(a)
    for ref,num,expected in TARGETS:
        assert p[(ref,num)].rsplit("/",1)[-1]==expected,(ref,num,p[(ref,num)])
    assert p[("U200","1")] in {p[("F200","1")],p[("F200","2")]}
    assert p[("U6203","1")] in {p[("FB6201","1")],p[("FB6201","2")]}
    assert p[("U2","1")]==p[("U3","1")]
    assert p[("U200","8")]==p[("U200","17")]!=p[("U200","9")]
    assert p[("U6203","2")]!=p[("U2","2")]
    er0=native_erc(OUT/"v774.original.erc.rpt")
    er1=native_erc(OUT/"v774.revised.erc.rpt")
    assert (er0["errors"],er0["warnings"])==(28,180)
    assert (er1["errors"],er1["warnings"])==(28,180)
    from collections import Counter
    a_findings=Counter(json.dumps(f,sort_keys=True) for f in er0["findings"])
    b_findings=Counter(json.dumps(f,sort_keys=True) for f in er1["findings"])
    if a_findings!=b_findings:
        print("V7.74 new genuine ERC",list((b_findings-a_findings).elements())[:12])
        print("V7.74 lost genuine ERC",list((a_findings-b_findings).elements())[:12])
    assert a_findings==b_findings,"Real ERC findings changed; do not waive"
    errors=[f for f in er1["findings"] if f["severity"]=="error"]
    power=[f for f in errors if f["category"]=="power_pin_not_driven"]
    assert len(errors)==28 and len(power)==6
    for ref,pin,_ in TARGETS:
        assert sum(any("Symbol "+ref+" Pin "+pin+" [" in loc for loc in f["locations"]) for f in power)==1,(ref,pin)
    result=dict(revision="V7.74",parts=140,nets=103,
      all_pinmap_equal=True,exact_source_annotations=3,
      undriven_power_pin_count=6,erc_errors=28,erc_warnings=180,
      native_erc_findings_unchanged=True,
      real_pin_nets=[dict(ref=ref,pin=pin,net=p[(ref,pin)],source_or_return_qualified=False) for ref,pin,_ in TARGETS],
      EFUSE_RTN_separate_from_GND_MAIN=True,
      MCU_GND_separate_from_PLL_GND_MAIN=True,
      external_AUX_13v8_qualified=False,crossmodule_15_qualified=False,
      actual_5V_LDO_load_profiles_known=False,pcb_drc_verified=False,
      NO_FAB=True,NO_TX=True,NO_GERBER=True,NO_PCBWAY=True)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v774_source_return_six_power_pins_native.json").write_text(json.dumps(result,indent=2)+"\n")
    return result
class TestV774PowerSourceReturn(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=gate()
    def test_01_notes(self):self.assertEqual(self.r["exact_source_annotations"],3)
    def test_02_parts(self):self.assertEqual(self.r["parts"],140)
    def test_03_nets(self):self.assertEqual(self.r["nets"],103)
    def test_04_pinmap(self):self.assertTrue(self.r["all_pinmap_equal"])
    def test_05_pins(self):self.assertEqual(len(self.r["real_pin_nets"]),6)
    def test_06_undriven(self):self.assertEqual(self.r["undriven_power_pin_count"],6)
    def test_07_erc(self):self.assertEqual(self.r["erc_errors"],28)
    def test_08_warnings(self):self.assertEqual(self.r["erc_warnings"],180)
    def test_09_findings(self):self.assertTrue(self.r["native_erc_findings_unchanged"])
    def test_10_efuse(self):self.assertTrue(self.r["EFUSE_RTN_separate_from_GND_MAIN"])
    def test_11_mcu_return(self):self.assertTrue(self.r["MCU_GND_separate_from_PLL_GND_MAIN"])
    def test_12_source_hold(self):self.assertFalse(self.r["external_AUX_13v8_qualified"])
    def test_13_crossmodule_hold(self):self.assertFalse(self.r["crossmodule_15_qualified"])
    def test_14_load_hold(self):self.assertFalse(self.r["actual_5V_LDO_load_profiles_known"])
    def test_15_fab_gate(self):self.assertTrue(self.r["NO_FAB"] and self.r["NO_TX"] and not self.r["pcb_drc_verified"])
if __name__=="__main__":unittest.main()
