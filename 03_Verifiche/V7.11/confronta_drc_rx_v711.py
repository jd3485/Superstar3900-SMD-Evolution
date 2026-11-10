"""Compare native KiCad 9 DRC reports for V5.2 vs versioned V7.11 board.

This is a REAL native DRC regression gate; it does NOT waive outstanding
unconnected, dangling-via, footprint or board fabrication blockers.
"""
import json
import re
import sys
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche"/"V7.11"/"output-ci"

def parse(report):
    text=Path(report).read_text(encoding="utf-8",errors="replace")
    if not text.startswith("** Drc report"):
        raise ValueError("missing KiCad-native DRC header")
    types=Counter(re.findall(r"^\[([^\]]+)\]:",text,re.M))
    total=re.search(r"Found\s+(\d+)\s+DRC violations",text)
    disconnected=re.search(r"Found\s+(\d+)\s+unconnected",text)
    if not total or not disconnected:
        raise ValueError("native DRC counts absent: do not infer PASS")
    return {
        "drc_violations":int(total.group(1)),
        "unconnected_items":int(disconnected.group(1)),
        "categories":dict(types)
    }

def main():
    old=parse(OUT/"rx_v52_legacy_drc.rpt")
    new=parse(OUT/"rx_v711_repaired_drc.rpt")
    changed_drill=new["categories"].get("drill_out_of_range",0)
    old_drill=old["categories"].get("drill_out_of_range",0)
    changed_foot=new["categories"].get("lib_footprint_issues",0)
    old_foot=old["categories"].get("lib_footprint_issues",0)
    result={
      "revision":"V7.11",
      "scope":"Native KiCad DRC of original RX V5.2 and edited V7.11 copy",
      "baseline":old,"candidate":new,
      "drill_errors_baseline":old_drill,
      "drill_errors_candidate":changed_drill,
      "library_warnings_baseline":old_foot,
      "library_warnings_candidate":changed_foot,
      "unconnected_not_waived":new["unconnected_items"],
      "drc_total_zero":new["drc_violations"]==0,
      "board_fabrication_authorized":False,
      "tx_physically_connected":False,
      "NO_FAB_NO_TX":True
    }
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"comparison_v711.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    if old_drill!=6 or changed_drill!=0:
        print("REGRESSION: expected six actual legacy drill faults fixed",file=sys.stderr)
        return 2
    if new["drc_violations"]>=old["drc_violations"]:
        print("REGRESSION: candidate DRC not strictly improved",file=sys.stderr)
        return 3
    if new["unconnected_items"]>old["unconnected_items"]:
        print("REGRESSION: new unconnected item count increased",file=sys.stderr)
        return 4
    # Footprint errors MUST remain visible if local table fix does not resolve.
    print("PASS V7.11 native KiCad DRC IMPROVEMENT, NOT BOARD DRC PASS")
    return 0

if __name__=="__main__":
    sys.exit(main())
