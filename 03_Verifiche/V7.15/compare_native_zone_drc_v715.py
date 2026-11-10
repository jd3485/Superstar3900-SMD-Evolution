"""Compare genuine KiCad9 DRC before/after temporary zone refill, if supported.

No --save-board, no Gerbers, no connectivity repair asserted.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche"/"V7.15"/"output-ci"
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.11"))
from confronta_drc_rx_v711 import parse
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.15"))
from audit_rx_topologia_v715 import PCB, audit, check

def main():
    base=parse(OUT/"v715.rx.asis.drc.rpt")
    marker=(OUT/"zone_refill_support.txt").read_text().strip()
    refill=None
    if marker=="SUPPORTED_EXECUTED":
        refill=parse(OUT/"v715.rx.refilled_volatile.drc.rpt")
    elif marker!="UNSUPPORTED_NOT_RUN":
        raise ValueError("Refill mode unknown; cannot claim it ran")
    source=audit()
    check(source)
    disk_hash=hashlib.sha256(PCB.read_bytes()).hexdigest()
    if disk_hash!=source["pcb_sha256"]:
        raise ValueError("Source PCB changed during read-only DRC")
    data={
        "revision":"V7.15",
        "method":"native kicad-cli pcb drc without refill vs --refill-zones without --save-board",
        "source_board_sha256_unchanged":True,
        "baseline_native_drc":base,
        "volatile_zone_refill_supported":refill is not None,
        "volatile_zone_refill_native_drc":refill,
        "delta_drc_violations":(refill["drc_violations"]-base["drc_violations"]) if refill else None,
        "delta_unconnected_items":(refill["unconnected_items"]-base["unconnected_items"]) if refill else None,
        "baseline_drc_clean":base["drc_violations"]==0 and base["unconnected_items"]==0,
        "refilled_drc_clean":bool(refill and refill["drc_violations"]==0 and refill["unconnected_items"]==0),
        "sma_vendor_qualified":False,
        "root_erc_clean":False,
        "gerbers_created":False,
        "pcb_fabrication_permitted":False,
        "rf_tx_permitted":False
    }
    (OUT/"v715.native_zone_refill_compare.json").write_text(json.dumps(data,indent=2)+"\n")
    print(json.dumps(data,indent=2))
    if base["drc_violations"]!=72 or base["unconnected_items"]!=63:
        raise SystemExit("V7.14 native PCB as-is baseline drift: explicit failure")
    if base["categories"].get("via_dangling",0)!=70:
        raise SystemExit("70 via dangling native baseline drift")
    if base["categories"].get("lib_footprint_mismatch",0)!=2:
        raise SystemExit("2 SMA library mismatch native baseline drift")
    print("PASS: native KiCad DRC diagnostic and immutable PCB, NOT fabrication or TX release")

if __name__=="__main__":
    main()
