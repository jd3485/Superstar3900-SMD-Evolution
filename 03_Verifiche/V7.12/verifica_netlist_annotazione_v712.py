"""Compare native KiCad9 exports, NOT textual annotation guesses.

V7.12 reannotates versioned MCU and RX schematics, preserving historical
sources, RX PCB matching references, and isolated cross-module hierarchy.
Any physical interconnect / fabrication / TX remains unqualified.
"""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche"/"V7.12"/"output-ci"
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.10"))
from analizza_netlist_kicad_v710 import analyze

def main():
    a=OUT/"integration_v710_original.net"
    b=OUT/"integration_v712_reannotated.net"
    if not a.is_file() or not b.is_file():
        raise RuntimeError("both native KiCad netlists required")
    old=analyze(a.read_text())
    new=analyze(b.read_text())
    report={
        "revision":"V7.12",
        "source":"actual KiCad9 export on original and reannotated 7-sheet roots",
        "original":old,
        "reannotated":new,
        "reference_collision_fix_confirmed":(
             old["reference_collisions"]==11
             and old["total_duplicate_excess"]==14
             and new["reference_collisions"]==0
             and new["total_duplicate_excess"]==0
        ),
        "component_count_unchanged": old["component_instances"]==new["component_instances"]==132,
        "sheets_unchanged":old["hierarchical_sheets"]==new["hierarchical_sheets"]==7,
        "nets_unchanged":old["nets_exported"]==new["nets_exported"]==99,
        "electrical_connections_qualified":False,
        "full_schema_erc_clean":False,
        "full_pcb_drc_clean":False,
        "fabrication_release":False,
        "tx_permission":False,
    }
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"native_netlist_reference_comparison_v712.json").write_text(
        json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(report,indent=2,ensure_ascii=False))
    if not all(report[k] for k in (
        "reference_collision_fix_confirmed","component_count_unchanged",
        "sheets_unchanged","nets_unchanged"
    )):
        raise SystemExit("BLOCKER: native KiCad export not collision-free / preserved")
    print("PASS native 7-sheet KiCad reference annotation consistency, NOT ERC or DRC PASS")

if __name__=="__main__":
    main()
