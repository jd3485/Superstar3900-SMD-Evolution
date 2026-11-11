"""V7.25 - native reviewer-only symbol-to-footprint assignments, never a fabrication release."""
import re,sys,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
M="S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
R="S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
OLDM=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.22_EP33_GROUNDED_NOT_FOR_FAB"/M
NEWM=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.25_SIX_FOOTPRINTS_REVIEW_NOT_FOR_FAB"/M
OLDR=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.22_EP33_NOT_FOR_FAB"/R
NEWR=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.25_SIX_FOOTPRINTS_REVIEW_NOT_FOR_FAB"/R
OUT=ROOT/"03_Verifiche/V7.25/output-ci"
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

FP={"U6201":"S3900E_ST_LQFP_V722_HOLD:STM32G474RE_LQFP64_ST_DS12288_CANDIDATE",
    "U6202":"S3900E_TI_RHB_V722_HOLD:TLV320AIC3204_RHB0032E_VENDOR_CANDIDATE",
    "U6203":"S3900E_TI_DBV_V722_HOLD:TPS7A20_DBV0005A_VENDOR_CANDIDATE",
    "U6204":"S3900E_TI_DBV_V722_HOLD:TPS7A20_DBV0005A_VENDOR_CANDIDATE",
    "U6205":"S3900E_TI_DBV_V722_HOLD:TPS7A20_DBV0005A_VENDOR_CANDIDATE",
    "U6206":"S3900E_TI_DBV_V722_HOLD:TPS7A20_DBV0005A_VENDOR_CANDIDATE"}
def compmap(path):
    txt=path.read_text()
    it=list(re.finditer(r'(?m)^    \(comp \(ref "([^"]+)"\)',txt))
    out={}
    for i,m in enumerate(it):
        block=txt[m.start():it[i+1].start() if i+1<len(it) else len(txt)]
        f=re.search(r'(?m)^      \(footprint "([^"]+)"\)',block)
        v=re.search(r'(?m)^      \(value "([^"]+)"\)',block)
        out[m.group(1)]=(f.group(1) if f else "",v.group(1) if v else "")
    return out
def gate():
    old=compmap(OUT/"v725.original.net");new=compmap(OUT/"v725.revised.net")
    assert set(old)==set(new) and len(old)==132
    delta={k:(old[k],new[k]) for k in old if old[k]!=new[k]}
    assert set(delta)==set(FP),repr(delta)
    for k,((oldfp,oldval),(newfp,newval)) in delta.items():
        assert oldfp=="" and newfp==FP[k],repr(delta)
        assert oldval==newval
    assert sum(not x[0] for x in old.values())==48
    assert sum(not x[0] for x in new.values())==42
    oldnet=nets(OUT/"v725.original.net");newnet=nets(OUT/"v725.revised.net")
    assert oldnet==newnet and len(oldnet)==100, "no unproven net join/loss permitted"
    a=native_erc(OUT/"v725.original.erc.rpt")
    b=native_erc(OUT/"v725.revised.erc.rpt")
    assert (a["errors"],a["warnings"])==(36,340)
    assert (b["errors"],b["warnings"])==(36,340),repr(b)
    ev={"revision":"V7.25","ref_only_footprints":sorted(FP),"net_nodes_delta":0,
        "components":132,"nets":100,"footprint_missing_original":48,
        "footprint_missing_revised":42,"erc_before":[36,340],"erc_after":[36,340],
        "physical_vendor_assembly_approved":False,"all_15_interfaces_OPEN_HOLD":True,
        "SG48_HOLD":True,"NO_FAB":True,"NO_TX":True}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v725.six_footprints.json").write_text(json.dumps(ev,indent=2)+"\n")
    return ev

class TestV725ReviewOnly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.d=gate()
    def test_01_exact_six_new_footprint_assignments(self):self.assertEqual(len(self.d["ref_only_footprints"]),6)
    def test_02_42_remaining_missing(self):self.assertEqual(self.d["footprint_missing_revised"],42)
    def test_03_no_net_node_change(self):self.assertEqual(self.d["net_nodes_delta"],0)
    def test_04_components_unchanged(self):self.assertEqual(self.d["components"],132)
    def test_05_nets_unchanged(self):self.assertEqual(self.d["nets"],100)
    def test_06_erc_unchanged(self):self.assertEqual(self.d["erc_before"],self.d["erc_after"])
    def test_07_mcu_ep33_local_gnd_retained(self):
        s=NEWM.read_text()
        self.assertIn('(label "GND" (at 448.2600 190.4800 0)',s)
        self.assertNotIn("EFUSE_RTN",s)
    def test_08_footprint_ids_registered_and_native_parsed(self):
        txt=(ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.25_SIX_FOOTPRINTS_REVIEW_NOT_FOR_FAB/fp-lib-table").read_text()
        for nick in ("S3900E_ST_LQFP_V722_HOLD","S3900E_TI_RHB_V722_HOLD","S3900E_TI_DBV_V722_HOLD"):
            self.assertEqual(txt.count('(lib (name "'+nick+'")'),1)
        p=ROOT/"03_Verifiche/V7.23/output-ci/v723.native_footprint_load.json"
        evidence=json.loads(p.read_text())
        self.assertEqual(len(evidence["footprints"]),3)
        self.assertTrue(all(f["native_loaded"] and f["land_geometry_matches_vendor_example"] for f in evidence["footprints"]))
        self.assertFalse(evidence["fabrication_release"])
    def test_09_source_only_six_instance_props_differ(self):
        old=OLDM.read_text();new=NEWM.read_text()
        for ref,lib in FP.items():
            pos=old.index('(property "Reference" "'+ref+'"')
            at=old.index('(property "Footprint" ""',pos)
            self.assertLess(at,old.index('(instances ',pos))
            old=old[:at]+old[at:].replace('(property "Footprint" ""','(property "Footprint" "'+lib+'"',1)
        old=old.replace("MCU + CODEC + AFE + ALIMENTAZIONE - V2.1 BOZZA",
            "MCU/CODEC/AFE V7.25 - SIX VENDOR FOOTPRINTS PROVISIONAL HOLD / NO FAB TX")
        old=old.replace("V7.22 CODEC EP33 GROUNDED DRAFT - NO FAB / NO TX",
            "V7.25 SIX VENDOR FOOTPRINT CANDIDATES - HOLD / NO FAB TX")
        self.assertEqual(old,new)
    def test_10_no_release(self):
        self.assertTrue(self.d["SG48_HOLD"] and self.d["NO_FAB"] and self.d["NO_TX"])
        self.assertTrue(self.d["all_15_interfaces_OPEN_HOLD"])
        self.assertFalse(self.d["physical_vendor_assembly_approved"])
if __name__=="__main__":unittest.main()
