"""Genuine native KiCad9 ERC comparison with unchanged RX schematic electronics.

Do not mistake an accessible symbol library for pin/footprint verification,
nor a clean diagnostic script for a clean CAD design.
"""
import sys
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche"/"V7.14"/"output-ci"
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.10"))
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.13"))
from esegui_kicad_audit_v710 import summarize
from verifica_netlist_rx_v713 import native_netlist

def main():
    old=OUT/"v713.erc.rpt"
    new=OUT/"v714.erc.rpt"
    orig=summarize(old.read_text(encoding="utf-8",errors="replace"))
    cur=summarize(new.read_text(encoding="utf-8",errors="replace"))
    a=native_netlist(OUT/"v713.net")
    b=native_netlist(OUT/"v714.net")
    status={
      "source":"Native KiCad9.0 ERC and exported netlist on RX coupon",
      "baseline":orig, "candidate":cur,
      "all_electrical_net_node_memberships_unchanged":a==b,
      "baseline_nets":len(a),"candidate_nets":len(b),
      "symbol_issues_before":orig["categories"].get("lib_symbol_issues",0),
      "symbol_issues_after":cur["categories"].get("lib_symbol_issues",0),
      "footprint_issues_before":orig["categories"].get("footprint_link_issues",0),
      "footprint_issues_after":cur["categories"].get("footprint_link_issues",0),
      "all_symbols_proven_vendor_correct":False,
      "all_footprints_proven_vendor_correct":False,
      "erc_clean":cur["erc_total"]==0,
      "root_erc_clean":False,
      "PCB_drc_clean":False,
      "board_manufacturing_permitted":False,
      "RF_TX_permitted":False
    }
    (OUT/"v714_native_erc_library_probe.json").write_text(json.dumps(status,indent=2)+"\n")
    print(json.dumps(status,indent=2))
    if not (status["all_electrical_net_node_memberships_unchanged"] 
            and status["baseline_nets"]==status["candidate_nets"]
            and cur["erc_errors"]<=orig["erc_errors"]
            and cur["erc_total"]<=orig["erc_total"]):
        raise SystemExit("BLOCKED native KiCad schematic regression")
    print("PASS native KiCad no-regression diagnostic; NOT a PCB or RF qualification")
if __name__=="__main__":
    main()
