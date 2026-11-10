"""Native KiCad9 DRC gate on reannotated RX PCB: no hidden copper changes.

The standalone RX schematic and integrated 7-sheet ERC have separate gates.
Never infer fabrication approval from retaining the V7.11 defect inventory.
"""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.11"))
from confronta_drc_rx_v711 import parse
OUT=ROOT/"03_Verifiche"/"V7.12"/"output-ci"

def main():
    p=OUT/"v712_rx_reannotated_pcb_drc.rpt"
    d=parse(p)
    status={
        "source":"native KiCad 9 pcb drc on reannotated V7.12 coupon",
        "drc":d,
        "original_v711_nonregression":d["drc_violations"]==85
            and d["unconnected_items"]==63
            and d["categories"].get("via_dangling",0)==70
            and d["categories"].get("lib_footprint_issues",0)==15
            and d["categories"].get("drill_out_of_range",0)==0,
        "pcb_drc_clean":False,
        "electrical_connections_qualified":False,
        "pcb_fabrication_release":False,
        "RF_transmission":False
    }
    (OUT/"v712_native_pcb_drc_status.json").write_text(json.dumps(status,indent=2)+"\n")
    print(json.dumps(status,indent=2))
    if not status["original_v711_nonregression"]:
        raise SystemExit("Unexpected geometry/copper DRC change following reannotation")
    print("PASS native PCB DRC NONREGRESSION; board still 85 violations and 63 unconnected")

if __name__=="__main__":
    main()
