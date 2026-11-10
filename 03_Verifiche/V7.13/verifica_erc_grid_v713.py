"""Native KiCad9 ERC comparison with unchanged grid rules; NO suppressions.

A successful workflow means the OFF-GRID problem is actually repaired in KiCad
without pin/net changes (checked separately). Any remaining ERC errors/warnings
are reported as NOT READY for fabrication.
"""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche"/"V7.13"/"output-ci"
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.10"))
from esegui_kicad_audit_v710 import summarize
def parse(name):
    p=OUT/name
    if not p.is_file() or p.stat().st_size<100:raise RuntimeError("native KiCad ERC report missing: "+str(p))
    return summarize(p.read_text(encoding="utf-8",errors="replace"))
def main():
    base=parse("rx_v712_erc.rpt")
    snapped=parse("rx_v713_erc.rpt")
    root=parse("root_v713_erc.rpt")
    old_off=base["categories"].get("endpoint_off_grid",0)
    new_off=snapped["categories"].get("endpoint_off_grid",0)
    report={
      "source":"native KiCad9 sch erc on same unmodified default ERC rules",
      "old":base,"grid_aligned":snapped,"hierarchical_root":root,
      "off_grid_cleared":old_off==46 and new_off==0,
      "no_new_RX_ERC_errors":snapped["erc_errors"]==0,
      "rx_erc_warning_decreased":snapped["erc_warnings"]<base["erc_warnings"],
      "hierarchical_root_erc_zero":root["erc_total"]==0,
      "rx_erc_zero":snapped["erc_total"]==0,
      "board_DRC_certified":False,
      "real_hardware_RF_TX_enabled":False,
      "NO_FAB_NO_TX":True
    }
    (OUT/"rx_v713_erc_comparison.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    if not all((report["off_grid_cleared"],report["no_new_RX_ERC_errors"],report["rx_erc_warning_decreased"])):
        raise SystemExit("BLOCKED: native RX grid ERC did not genuinely improve")
    print("PASS KiCad RX grid fix, not a full ERC/DRC pass")
if __name__=="__main__":
    main()
