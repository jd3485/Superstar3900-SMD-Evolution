"""Post-CAD-audit meta-check; green means defects were measured, NOT PCB clean."""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
p=ROOT/"03_Verifiche"/"V7.10"/"output-ci"/"cad_audit_summary.json"

def main():
    if not p.is_file():
        raise RuntimeError("No native KiCad result JSON")
    data=json.loads(p.read_text(encoding="utf-8"))
    checks=data["checks"]
    expected={"integration_erc","aux_power_v15_erc","mcu_codec_v21_erc",
              "rx_v52_erc","rx_v52_pcb_drc"}
    if set(checks)!=expected:
        raise AssertionError("incomplete native check inventory")
    if data["unexpected_native_command_failures"]:
        raise AssertionError("unknown KiCad CLI execution failures")
    if data["known_legacy_root_erc_load_failures"]!=["rx_v52_erc"]:
        raise AssertionError("legacy RX standalone issue changed - review explicitly")
    for n in expected-{"rx_v52_erc"}:
        x=checks[n]
        if x["returncode"]!=0 or not x["report_generated"]:
            raise AssertionError("native KiCad did not produce "+n)
    root=checks["integration_erc"]["native_kicad_findings"]
    pcb=checks["rx_v52_pcb_drc"]["native_kicad_findings"]
    if not root.get("erc_errors",0)>0 or not pcb.get("drc_violations",0)>0:
        raise AssertionError("legacy draft defects disappeared; inspect for dropped sheets")
    if not pcb.get("drc_unconnected",0)>0:
        raise AssertionError("KiCad report did not contain expected unconnected RX nets")
    if data["full_native_erc_drc_pass"] or data["integration_electrically_complete"]:
        raise AssertionError("fake CAD release flag")
    if not data["NO_FAB_NO_TX"] or data["TX_RF_enabled"]:
        raise AssertionError("unsafe CAD status flag")
    print("NATIVE KIcad 9 AUDIT OK: violations CONFIRMED, not waived")
    print("Integration ERC",root["erc_errors"],"errors /",
          root["erc_warnings"],"warnings")
    print("Legacy RX PCB DRC",pcb["drc_violations"],"violations and",
          pcb["drc_unconnected"],"unconnected items")
    print("Original RX standalone schematic load remains BLOCKED.")
    print("NO FAB / NO TX; the integrated PCB is NOT COMPLETE.")
    return 0

if __name__=="__main__":
    sys.exit(main())
