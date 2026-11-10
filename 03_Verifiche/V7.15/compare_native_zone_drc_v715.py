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
    probe=json.loads((OUT/"v715.pcbnew_temporary_clone_probe.json").read_text())
    clone=probe["native_drc"] if probe["status"]=="EXECUTED" else None
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
        "pcbnew_temporary_clone_refill_executed":clone is not None,
        "pcbnew_temporary_clone_native_drc":clone,
        "pcbnew_saved_filled_polygons":probe["saved_filled_polygons_on_temporary_clone"],
        "pcbnew_original_sha256_unchanged":probe["source_project_unchanged"],
        "pcbnew_delta_violations":clone["drc_violations"]-base["drc_violations"] if clone else None,
        "pcbnew_delta_unconnected":clone["unconnected_items"]-base["unconnected_items"] if clone else None,
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
    if not probe["source_project_unchanged"]:
        raise SystemExit("Source PCB SHA drift during pcbnew clone probe")
    if clone is not None:
        if not (clone["drc_violations"]==2 and clone["unconnected_items"]==0
                and clone["categories"].get("lib_footprint_mismatch",0)==2
                and clone["categories"].get("via_dangling",0)==0
                and probe["saved_filled_polygons_on_temporary_clone"]==4):
            raise SystemExit("New KiCad pcbnew filled-clone DRC baseline changed; inspect without waivers")
        print("PASS: genuine cloned zone-fill native DRC 72->2, unconnected 63->0; NOT RF/vendor qualification")
    else:
        print("NOT RUN: pcbnew filled-clone DRC unavailable; retain RX DRC blockers")
    print("PASS: native KiCad DRC diagnostic and immutable PCB, NOT fabrication or TX release")

if __name__=="__main__":
    main()
