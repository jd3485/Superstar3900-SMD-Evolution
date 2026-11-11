"""V7.21 preliminary manufacturer-package study against installed KiCad9 footprints.

No schematic footprint assignment is made here. The six tentative IC packages
must still pass pinout, assembly and exposed-pad thermal/copper validation.
"""
import csv,json,re
from pathlib import Path
from audit_board_foundations_v721 import ROOT,OUT,native_components,NET,schematic_values,MCU

# Manufacturer sources: ST DS12288 LQFP64 10x10mm e0.5;
# TI AIC3204 RHB0032E 5x5mm e0.5 center pad ~3.45mm;
# TI TPS7A20 SBVS338H DBV 5pin SOT23, Iout max 300mA.
CANDIDATES=[
    {"ref":"U6201","value":"STM32G474RET6 (DRAFT)",
     "kicad":"Package_QFP:LQFP-64_10x10mm_P0.5mm",
     "numbers":list(range(1,65)),"vendor_package":"ST LQFP64 10x10mm e0.5",
     "vendor_source":"https://www.st.com/resource/en/datasheet/stm32g474vb.pdf"},
    {"ref":"U6202","value":"TLV320AIC3204 (DRAFT)",
     "kicad":"Package_DFN_QFN:VQFN-32-1EP_5x5mm_P0.5mm_EP3.5x3.5mm",
     "numbers":list(range(1,34)),"vendor_package":"TI RHB0032E VQFN 5x5mm e0.5; center EP ~3.45x3.45mm",
     "vendor_source":"https://www.ti.com/lit/ds/symlink/tlv320aic3204.pdf"},
]
for ref in ("U6203","U6204","U6205","U6206"):
    CANDIDATES.append({"ref":ref,"value":"TPS7A2033PDBVR",
    "kicad":"Package_TO_SOT_SMD:SOT-23-5",
    "numbers":list(range(1,6)),"vendor_package":"TI DBV SOT23-5, 300mA",
    "vendor_source":"https://www.ti.com/lit/ds/symlink/tps7a20.pdf"})

def inspect():
    comps={c["ref"]:c for c in native_components(NET)}
    original=schematic_values(MCU)
    results=[]
    for c in CANDIDATES:
        ref=c["ref"]
        if comps[ref]["value"]!=c["value"] or original[ref]["footprint"] or comps[ref]["footprint"]:
            raise ValueError("Never replace a known or changed MCU footprint without approval "+ref)
        lib,path=c["kicad"].split(":")
        module=Path("/usr/share/kicad/footprints")/(lib+".pretty")/(path+".kicad_mod")
        if not module.is_file():
            raise ValueError("Actual installed KiCad9 standard footprint not found: "+str(module))
        body=module.read_text()
        pads={int(m) for m in re.findall(r'\(pad "?(\d+)"? (?:smd|thru_hole|connect)',body)}
        if pads!=set(c["numbers"]):
            raise ValueError(f"Actual installed KiCad9 pad list differs {ref} {sorted(pads)}")
        if ref=="U6202":
            if 33 not in pads or "3.5x3.5mm" not in path:
                raise ValueError("Codec exposed thermal pad not represented by candidate")
        results.append({
            "ref":ref,"component_value":comps[ref]["value"],
            "vendor_package":c["vendor_package"],
            "candidate_kicad_footprint":c["kicad"],
            "actual_installed_pad_numbers":sorted(pads),
            "pad_count":len(pads),
            "vendor_source":c["vendor_source"],
            "verification":"KICAD9_STANDARD_LIBRARY_PAD_NUMBERS_ONLY",
            "symbol_pin_to_pad_mapping_vendor_verified":False,
            "manufacturer_solderlandpattern_stencil_verified":False,
            "cad_schematic_footprint_assigned":False,
            "PCB_release":False
        })
    result={
      "revision":"V7.21",
      "candidate_IC_footprint_count":len(results),
      "candidate_package_check":"Installed KiCad9 library pad numbers (not physical vendor certification)",
      "codec_RHB_pad33_exposed_pad_requires_GND_and_stencil_review":True,
      "MCU_symbol_is_DRAFT_64_pin_check_required":True,
      "other_42_missing_footprints_still_HOLD":True,
      "records":results,
      "any_cad_change":False,"fabrication_release":False,"TX_release":False}
    (OUT/"v721.candidate_IC_packages_native.json").write_text(json.dumps(result,indent=2)+"\n")
    with (OUT/"v721.candidate_IC_packages.csv").open("w",newline="",encoding="utf-8") as f:
        fields=["ref","component_value","vendor_package","candidate_kicad_footprint","pad_count",
                "verification","symbol_pin_to_pad_mapping_vendor_verified","manufacturer_solderlandpattern_stencil_verified",
                "cad_schematic_footprint_assigned","vendor_source"]
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader()
        for row in results: writer.writerow({k:row[k] for k in fields})
    print(json.dumps(result,indent=2))
    print("PASS: six candidate MCU/codec/LDO package pad-number inventories match real KiCad9 library; remain HOLD/unassigned; no fab/TX")
    return result
if __name__=="__main__":inspect()
