"""V7.77: KiCad9 native 7-sheet master -> real footprint pad-number audit.

This verifies *numbering and availability* only. It never accepts physical
manufacturer lands, package thermal geometry, electrical functionality,
PCB DRC, or production readiness by counting pads.
"""
from pathlib import Path
import json
import re
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
MASTER_DIR=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.74_SIX_PWR_SOURCE_RETURN_PROVENANCE_HOLD"
NET=ROOT/"03_Verifiche/V7.74/output-ci/v774.revised.net"
OUT=ROOT/"03_Verifiche/V7.77/output-ci/v777_critical_pad_audit.json"
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets

# These are actual solder pad numbers, including mandatory CODEC EP33
# and eFuse exposed return pad17. No disconnected pin is silently discarded.
EXPECTED={
 "F200":set("12"),"U200":set(map(str,range(1,18))),
 "SW200":set("1234"),"U100":set(map(str,range(1,7))),
 "L100":set("12"),
 "U6201":set(map(str,range(1,65))),
 "U6202":set(map(str,range(1,34))),
 **{f"U620{i}":set("12345") for i in (3,4,5,6)}
}
# Critical component footprint IDs actually present in V7.74 source.
FOOTPRINT_IDS={
 "F200":"S3900E_LF451_V729_HOLD:LF451_045101_5MRL_VENDOR_CANDIDATE",
 "U200":"Package_SO:TSSOP-16-1EP_4.4x5mm_P0.65mm",
 "SW200":"S3900E_CK_KMR2_V763_HOLD:CK_KMR223NG_ULC_LFG_4PAD_VENDOR_LAND_REVIEW",
 "U100":"Package_TO_SOT_SMD:SOT-23-6",
 "L100":"S3900E_BOURNS_SRP1038A_V728_HOLD:SRP1038A_150M_BOURNS_VENDOR_CANDIDATE",
 "U6201":"S3900E_ST_LQFP_V722_HOLD:STM32G474RE_LQFP64_ST_DS12288_CANDIDATE",
 "U6202":"S3900E_TI_RHB_V722_HOLD:TLV320AIC3204_RHB0032E_VENDOR_CANDIDATE",
 **{f"U620{i}":"S3900E_TI_DBV_V722_HOLD:TPS7A20_DBV0005A_VENDOR_CANDIDATE" for i in (3,4,5,6)}
}

def library_dirs():
    s=(MASTER_DIR/"fp-lib-table").read_text(encoding="utf8")
    # One lib per line in the versioned KiCad fp-lib-table.
    lib={}
    for name,uri in re.findall(r'\(lib \(name "([^"]+)"\)\(type "KiCad"\)\(uri "([^"]+)"\)',s):
        assert name not in lib,name
        lib[name]=Path(uri.replace("${KIPRJMOD}",str(MASTER_DIR))).resolve()
    return lib

def pad_list(text):
    # KiCad includes *multiple F.Paste-only apertures* on U200 EP17.
    # Those are NOT duplicate copper pads. For every native (pad ...) node
    # extract its balanced S-expression and only retain pads with copper.
    found=[]
    for m in re.finditer(r'\\(pad "([^"]+)" (?:smd|thru_hole|connect|np_thru_hole) ',text):
        start=m.start()
        depth=0
        in_string=False
        escaped=False
        end=None
        for i in range(start,len(text)):
            c=text[i]
            if escaped:
                escaped=False
            elif in_string and c=="\\\\":
                escaped=True
            elif c=='"':
                in_string=not in_string
            elif not in_string:
                if c=="(":
                    depth+=1
                elif c==")":
                    depth-=1
                    if depth==0:
                        end=i+1
                        break
        assert end is not None,(m.group(1),"unbalanced pad")
        chunk=text[start:end]
        layer=re.search(r'\\(layers? ([^)]*)\\)',chunk)
        assert layer is not None,(m.group(1),"no layers")
        layers=layer.group(1)
        if re.search(r'(?:F|B|\\*)\\.Cu',layers):
            found.append(m.group(1))
        else:
            assert "Paste" in layers or "Mask" in layers,(m.group(1),layers)
    return found

def audit():
    comps=compmap(NET)
    assert len(comps)==140,("master component regression",len(comps))
    lib=library_dirs()
    pins_by_ref={}
    for net,nodes in nets(NET).items():
        for ref,pin in nodes:
            pins_by_ref.setdefault(ref,set()).add(str(pin))
    critical={}
    for ref in sorted(EXPECTED):
        assert ref in comps,ref
        fp,value=comps[ref]
        assert fp==FOOTPRINT_IDS[ref],(ref,fp)
        nickname,name=fp.split(":",1)
        if nickname in lib:
            path=lib[nickname]/(name+".kicad_mod")
        else:
            # Installed KiCad9 public standard footprints in existing native CI.
            assert nickname in {"Package_SO","Package_TO_SOT_SMD"},nickname
            path=Path("/usr/share/kicad/footprints")/(nickname+".pretty")/(name+".kicad_mod")
        assert path.is_file(),(ref,str(path))
        pads=pad_list(path.read_text(encoding="utf8"))
        assert len(pads)==len(set(pads)),(ref,"duplicate physical pad",pads)
        assert set(pads)==EXPECTED[ref],(ref,fp,sorted(pads),sorted(EXPECTED[ref]))
        assert pins_by_ref[ref] <= set(pads),(ref,"connected pin missing physical pad",pins_by_ref[ref]-set(pads))
        critical[ref]=dict(footprint=fp,pad_count=len(pads),
          connected_native_netlist_pins=len(pins_by_ref[ref]),
          footprint_file=str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
          numbering_matches=True,manufacturer_geometry_qualified_for_fab=False)
    assert "33" in EXPECTED["U6202"] and "17" in EXPECTED["U200"]
    assert len(critical)==11
    absent=sorted(ref for ref,(fp,value) in comps.items() if not fp)
    hold=dict(version="V7.77",master="V7.74 7-sheet unchanged",
      schematic_component_count=len(comps), native_nets=len(nets(NET)),
      footprint_missing_count=len(absent), footprint_missing_refs=absent,
      critical_pad_counts_verified=len(critical),critical=critical,
      all_critical_pads_match_native_numbering=True,
      all_footprints_qualified=False,manufacturer_lands_qualified=False,
      mixed_power_ground_physical_return_verified=False,
      all_smd_pcb_routed=False,board_drc_verified=False,
      crossmodule_15_open_hold=True,sg48_hold=True,
      last_native_erc_errors=28,last_native_erc_warnings=180,
      no_fab=True,no_gerber=True,no_tx=True)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(hold,indent=2)+"\n",encoding="utf8")
    return hold

class TestV777Pads(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=audit()
    def test_01_critical(self):self.assertEqual(self.r["critical_pad_counts_verified"],11)
    def test_02_total(self):self.assertEqual(self.r["schematic_component_count"],140)
    def test_03_missing_are_explicit(self):self.assertEqual(len(self.r["footprint_missing_refs"]),self.r["footprint_missing_count"])
    def test_04_ep(self):self.assertEqual(self.r["critical"]["U6202"]["pad_count"],33)
    def test_05_efuse_ep(self):self.assertEqual(self.r["critical"]["U200"]["pad_count"],17)
    def test_06_mcu(self):self.assertEqual(self.r["critical"]["U6201"]["pad_count"],64)
    def test_07_sw200(self):self.assertEqual(self.r["critical"]["SW200"]["pad_count"],4)
    def test_08_no_release(self):self.assertFalse(self.r["all_footprints_qualified"] or self.r["board_drc_verified"])
    def test_09_safety(self):self.assertTrue(self.r["no_fab"] and self.r["no_tx"] and self.r["crossmodule_15_open_hold"])

if __name__=="__main__":unittest.main()
