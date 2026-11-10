"""Native KiCad ERC findings inventory; loading is NOT the same as clean ERC.

Proof for RX parser repair is a nonempty, KiCad-produced ERC report. Root and
RX errors are fully preserved and remain NON-FABRICATION blockers.
"""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche"/"V7.12"/"output-ci"
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.10"))
from esegui_kicad_audit_v710 import summarize

def main():
    reports={
      "integrated_v712":OUT/"v712_hierarchy_erc.rpt",
      "rx_standalone_v712":OUT/"v712_rx_standalone_erc.rpt",
    }
    results={}
    for k,p in reports.items():
        if not p.is_file() or p.stat().st_size<200:
            raise SystemExit(f"Missing genuine native KiCad report: {k}")
        result=summarize(p.read_text(encoding="utf-8",errors="replace"))
        if "erc_errors" not in result or "erc_warnings" not in result:
            raise SystemExit(f"ERC report not parseable: {k}")
        results[k]=result
    root=results["integrated_v712"]
    rx=results["rx_standalone_v712"]
    result={
       "source":"KiCad 9 CLI native ERC reports",
       "results":results,
       "standalone_rx_erc_now_loadable":rx["erc_total"]==76,
       "root_annotation_unchanged_electrically":root["erc_total"]==459,
       "erc_clean":False,
       "qualified_power_mcu_rx_links":False,
       "manufacturing_release":False,
       "tx_permission":False
    }
    (OUT/"native_erc_inventory_v712.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(result,indent=2,ensure_ascii=False))
    if not (result["standalone_rx_erc_now_loadable"]
            and result["root_annotation_unchanged_electrically"]
            and rx["erc_errors"]+rx["erc_warnings"]==76):
        raise SystemExit("Unexpected KiCad ERC regression, unsafe to claim RX fix")
    print("PASS native schematic LOAD and ERC INVENTORY, NOT electrical ERC clean")

if __name__=="__main__":
    main()
