"""Review actual KiCad9 native ERC/DRC; never call remaining violations PASS.

Compare RX standalone original V7.12 and snapped+symbol-library V7.13.
Require no new ERC errors, a meaningful off-grid reduction, exact PCB
DRC nonregression, and no root schematic error-count regression.
"""
from pathlib import Path
import sys,json

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche"/"V7.13"/"output-ci"
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.10"))
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.11"))
from esegui_kicad_audit_v710 import summarize
from confronta_drc_rx_v711 import parse

def main():
    paths={
        "erc_old_rx":OUT/"rx_v712_erc.rpt",
        "erc_new_rx":OUT/"rx_v713_erc.rpt",
        "erc_root":OUT/"root_v713_erc.rpt",
    }
    erc={k:summarize(p.read_text(encoding="utf-8",errors="replace"))
           for k,p in paths.items()}
    pcb=parse(OUT/"rx_v713_pcb_drc.rpt")
    old=erc["erc_old_rx"]
    new=erc["erc_new_rx"]
    root=erc["erc_root"]
    old_off=old["categories"].get("endpoint_off_grid",0)
    new_off=new["categories"].get("endpoint_off_grid",0)
    output={
        "revision":"V7.13",
        "sources":"KiCad9 actual native ERC/DRC .rpt outputs",
        "erc":erc,
        "pcb_drc":pcb,
        "offgrid_before":old_off,
        "offgrid_after":new_off,
        "offgrid_warnings_reduced":old_off==46 and new_off<old_off,
        "new_rx_no_erc_errors":new["erc_errors"]==0,
        "new_symbol_library_issues_nonregressed":
             new["categories"].get("lib_symbol_issues",0)<=old["categories"].get("lib_symbol_issues",0),
        "root_erc_error_count_nonregressed":root["erc_errors"]<=43,
        "pcb_geometrically_unchanged":pcb["drc_violations"]==85
          and pcb["unconnected_items"]==63
          and pcb["categories"].get("via_dangling",0)==70
          and pcb["categories"].get("drill_out_of_range",0)==0,
        "full_erc_clean":False,
        "full_drc_clean":False,
        "hardware_qualified":False,
        "pcb_fabrication_permitted":False,
        "tx_permitted":False
    }
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"native_erc_drc_comparison_v713.json").write_text(
        json.dumps(output,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(output,indent=2,ensure_ascii=False))
    for key in ("offgrid_warnings_reduced","new_rx_no_erc_errors",
                "new_symbol_library_issues_nonregressed",
                "root_erc_error_count_nonregressed","pcb_geometrically_unchanged"):
        if not output[key]:
            raise SystemExit(f"Native KiCad V7.13 quality gate failed: {key}")
    print("PASS KiCad grid improvement and unchanged RX PCB; full ERC/DRC still not clean")
if __name__=="__main__":
    main()
