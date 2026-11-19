"""V7.79 actual STM32G474 SWD JST-GH 5pin debug interface native fail-closed.

A real physical access connector, NOT a PWR_FLAG or substitute power source.
No cross-module nets, TX or external 3V3 power injection approved.
"""
import unittest, json, sys, re
from pathlib import Path
from collections import Counter
import pcbnew

ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.78_TI_PWP0016H_EFUSE_LAND_HOLD"
NEW=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.79_SWD_JST_GH_SERVICE_CONNECTOR_HOLD"
MCU=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.79_SWD_JST_GH_SERVICE_CONNECTOR_HOLD/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
ORIG_MCU=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.74_U6203_PWR_SOURCE_RETURN_PROVENANCE_HOLD/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
OUT=ROOT/"03_Verifiche/V7.79/output-ci"
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc
FP="Connector_JST:JST_GH_BM05B-GHS-TBT_1x05-1MP_P1.25mm_Vertical"
PORT={
 "1":"3V3_MCU", "2":"MCU_SWDIO", "3":"MCU_SWCLK",
 "4":"MCU_NRST", "5":"GND"
}
def gate():
    a=compmap(OUT/"v779.original.net")
    z=compmap(OUT/"v779.revised.net")
    if (len(a),len(z))!=(140,141):
        raw=(OUT/"v779.revised.net").read_text()
        print("DIAG missing refs",sorted(set(a)-set(z)),"new refs",sorted(set(z)-set(a)))
        print("DIAG raw J6201",raw.count("J6201"),"old",len(a),"new",len(z))
        print("DIAG revised netlist tail",raw[-1300:])
        er=(OUT/"v779.revised.erc.rpt").read_text()
        print("DIAG ERC context", "\\n".join(line for line in er.splitlines() if "J6201" in line or "SWD" in line or "library" in line.lower())[:3800])
    assert len(a)==140 and len(z)==141,(len(a),len(z))
    assert set(z)-set(a)=={"J6201"}
    assert all(a[k]==z[k] for k in a),"existing component / footprint altered"
    assert z["J6201"]==(FP,"BM05B-GHS-TBT(LF)(SN)"),z["J6201"]
    old=nets(OUT/"v779.original.net")
    new=nets(OUT/"v779.revised.net")
    def pinmap(n):
        p={}
        for net,nodes in n.items():
            for node in nodes:
                assert node not in p,node
                p[node]=net
        return p
    p0=pinmap(old)
    p1=pinmap(new)
    for key,net in p0.items():
        assert p1.get(key)==net,(key,net,p1.get(key))
    assert set(p1)-set(p0)=={("J6201",n) for n in PORT}
    for number,name in PORT.items():
        assert p1["J6201",number].rsplit("/",1)[-1]==name,(number,name,p1["J6201",number])
    assert p1["J6201","1"]!=p1["J6201","5"]
    assert p1["J6201","2"]!=p1["J6201","3"]
    # STM32G474RE LQFP64 physical pins: PA13=49 SWDIO, PA14=50 SWCLK,
    # PG10-NRST=7; VDD16 and VSS15 stay in MCU power domain.
    assert p1["J6201","2"]==p1["U6201","49"]
    assert p1["J6201","3"]==p1["U6201","50"]
    assert p1["J6201","4"]==p1["U6201","7"]
    assert p1["J6201","1"]==p1["U6201","16"]
    assert p1["J6201","5"]==p1["U6201","15"]
    assert p1["U200","8"]==p1["U200","17"]!=p1["U200","9"]
    assert p1["U6203","2"]!=p1["U2","2"]
    assert len(new)==len(old)==103,("unexpected lost/added net",len(old),len(new))
    m=MCU.read_text()
    assert m.count('(property "Reference" "J6201"')==1
    # KiCad schematic stores the footprint both in embedded lib symbol and instance.
    assert m.count('(property "Footprint" "'+FP+'"')==2
    assert m.count('(property "MPN" "BM05B-GHS-TBT(LF)(SN)"')==1
    assert m.count('(property "MatingHousing" "GHR-05V-S"')==1
    assert len(re.findall(r'\(label "(3V3_MCU|MCU_SWDIO|MCU_SWCLK|MCU_NRST|GND)" \(at 998\.22 (?:543\.56|546\.10|548\.64|551\.18|553\.72)',m))==5
    assert "No external 3V3 injection" in m
    assert "PWR_FLAG" not in m[len(ORIG_MCU.read_text()):]
    s0=(OLD/"S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch").read_text()
    s1=(NEW/"S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch").read_text()
    assert s1==s0.replace("Modulo_MCU_CODEC_V7.74_U6203_PWR_SOURCE_RETURN_PROVENANCE_HOLD","Modulo_MCU_CODEC_V7.79_SWD_JST_GH_SERVICE_CONNECTOR_HOLD")
    for file in ("fp-lib-table","S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_pro"):
        assert (OLD/file).read_bytes()==(NEW/file).read_bytes()
    assert (NEW/"sym-lib-table").read_text()==(OLD/"sym-lib-table").read_text().replace(
        "Librerie_Simboli_V7.70_TPS54202_U100_PIN_GRID_HOLD",
        "Librerie_Simboli_V7.79_SWD_SERVICE_JST_GH_HOLD")
    # Physical SMD connector must have pads 1..5 and mechanical solder anchor
    fp=pcbnew.FootprintLoad("/usr/share/kicad/footprints/Connector_JST.pretty",
        "JST_GH_BM05B-GHS-TBT_1x05-1MP_P1.25mm_Vertical")
    assert fp is not None,"KiCad9 JST GH official footprint absent"
    numbered=[p.GetNumber() for p in fp.Pads() if p.GetNumber() in {"1","2","3","4","5"}]
    mechanical=[p for p in fp.Pads() if p.GetNumber()=="MP"]
    assert Counter(numbered)==Counter(["1","2","3","4","5"]),(numbered,"signal pad mapping error")
    assert len(mechanical)==2,"JST GH must have two soldered SMD mounting pads MP"
    assert len(list(fp.Pads()))==7,"Unexpected JST GH pads"
    assert all(p.GetLayerSet().Contains(pcbnew.F_Cu) for p in fp.Pads())
    er0=native_erc(OUT/"v779.original.erc.rpt")
    er1=native_erc(OUT/"v779.revised.erc.rpt")
    assert er0["errors"]==28 and er0["warnings"]==180
    # Do not hide any other ERC error: only original dangling debug nets may clear.
    orig=Counter(json.dumps(f,sort_keys=True) for f in er0["findings"] if f["severity"]=="error")
    after=Counter(json.dumps(f,sort_keys=True) for f in er1["findings"] if f["severity"]=="error")
    extra=list((after-orig).elements())
    removed=list((orig-after).elements())
    assert not extra,("new genuine ERC errors",extra)
    for item in removed:
        f=json.loads(item)
        assert f["category"]=="label_dangling" and any(
            token in json.dumps(f) for token in ("MCU_NRST","MCU_SWCLK","MCU_SWDIO")
        ),("unjustified ERC disappearance",f)
    assert er1["errors"]==25,("physical debug interface must remove exactly three genuine dangling label errors",er1["errors"])
    assert er1["warnings"]==180,("no additional warnings allowed",er1["warnings"])
    assert len(removed)==3,("only three proven labels may clear",removed)
    new_warnings=Counter(json.dumps(f,sort_keys=True) for f in er1["findings"] if f["severity"]=="warning")-Counter(
        json.dumps(f,sort_keys=True) for f in er0["findings"] if f["severity"]=="warning")
    assert not new_warnings,("new KiCad warnings",list(new_warnings.elements())[:8])
    data=dict(revision="V7.79",feature="MCU SWD physical service interface",
      original_components=140,updated_components=141,original_nets=103,updated_nets=103,
      port_pinmap=PORT, connector_mpn="BM05B-GHS-TBT(LF)(SN)",mating_housing="GHR-05V-S",
      native_erc_before=[er0["errors"],er0["warnings"]],
      native_erc_after=[er1["errors"],er1["warnings"]],
      genuinely_resolved_debug_label_erc_errors=len(removed),
      old_electrical_pins_preserved=True,
      source_domain_mcu_3v3_gnd_only=True,
      debug_vtref_sense_only_external_power_injection_qualified=False,
      debug_3v3_load_and_esd_qualified=False,
      cable_pin1_orientation_and_mating_verified=False,
      no_external_power_or_tx=False,
      crossmodule_15_hold=True,no_fab=True,no_tx=True,global_pcb_drc=False)
    OUT.mkdir(exist_ok=True,parents=True)
    (OUT/"v779_swd_native_jst5.json").write_text(json.dumps(data,indent=2)+"\n")
    return data
class TestV779SWD(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.d=gate()
    def test_01_component_real(self):self.assertEqual(cls_v(self.d,"updated_components"),141)
    def test_02_pinmap(self):self.assertEqual(len(self.d["port_pinmap"]),5)
    def test_03_erc(self):self.assertLessEqual(self.d["native_erc_after"][0],28)
    def test_04_domains(self):self.assertTrue(self.d["source_domain_mcu_3v3_gnd_only"])
    def test_05_power_hold(self):self.assertFalse(self.d["debug_vtref_sense_only_external_power_injection_qualified"])
    def test_06_cable_hold(self):self.assertFalse(self.d["cable_pin1_orientation_and_mating_verified"])
    def test_07_fab_hold(self):self.assertTrue(self.d["no_fab"] and self.d["no_tx"])
def cls_v(data,key):return data[key]
if __name__=="__main__":unittest.main()
