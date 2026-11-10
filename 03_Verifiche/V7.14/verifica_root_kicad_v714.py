"""Real KiCad9 seven-sheet V7.13/V7.14 comparison, no invented interconnects.

The new .kicad_pro + library tables are configuration, not electrical designs.
The 43 ERC errors of the isolated power/MCU/RX hierarchy remain blockers.
"""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche"/"V7.14"/"output-ci"
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.13"))
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.10"))
from verifica_netlist_rx_v713 import native_netlist
from esegui_kicad_audit_v710 import summarize

def main():
    a=native_netlist(OUT/"root_v713.net")
    b=native_netlist(OUT/"root_v714.net")
    old=summarize((OUT/"root_v713.erc.rpt").read_text())
    new=summarize((OUT/"root_v714.erc.rpt").read_text())
    data={
      "source":"native KiCad9 seven-sheet netlists and unwaived ERC reports",
      "previous_nets":len(a),"new_nets":len(b),
      "same_all_net_names":set(a)==set(b),
      "same_every_ref_pin":a==b,
      "previous_ERC":old,"new_ERC":new,
      "nonregression_erc_errors":new["erc_errors"]<=old["erc_errors"],
      "nonregression_erc_warnings":new["erc_warnings"]<=old["erc_warnings"],
      "full_root_ERC_clean":False,
      "crossmodule_rails_connected":False,
      "pcb_fabrication_authorized":False,
      "transmission_permitted":False
    }
    (OUT/"root_v714_native_library_audit.json").write_text(json.dumps(data,indent=2)+"\n")
    print(json.dumps(data,indent=2))
    if not (data["previous_nets"]==data["new_nets"]==99
            and data["same_all_net_names"] and data["same_every_ref_pin"]
            and data["nonregression_erc_errors"] 
            and data["nonregression_erc_warnings"]):
        raise SystemExit("BLOCKER: net/pin root change or native ERC regression")
    print("PASS native root KiCad library project/no electrical change, NOT ERC clean")
if __name__=="__main__":main()
