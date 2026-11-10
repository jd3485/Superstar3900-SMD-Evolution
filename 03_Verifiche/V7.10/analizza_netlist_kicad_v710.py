"""Analyze the actual KiCad-generated hierarchical netlist for ref collisions.

This inspects KiCad 9's S-expression NETLIST, not a guessed BOM. It does not
rewrite annotations or merge boards; collisions remain a release blocker.
"""
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche"/"V7.10"/"output-ci"
NET=OUT/"integration.net"

def analyze(net_text):
    sheets=re.findall(r'\(sheet \(number "(\d+)"\) \(name "([^"]+)"\)',net_text)
    components=re.findall(
        r'\(comp \(ref "([^"]+)"\).*?\(sheetpath \(names "([^"]+)"\)',
        net_text,re.S)
    nets=re.findall(r'\(net \(code "?(\d+)"?\)',net_text)
    if len(sheets)<3 or len(components)<15 or len(nets)<8:
        raise ValueError("KiCad output unexpectedly lost its source sheets or nets")
    refs=defaultdict(list)
    for ref,sheet in components:
        refs[ref].append(sheet)
    conflicts={ref:paths for ref,paths in sorted(refs.items())
               if len(paths)>1}
    return {
       "source":"native KiCad CLI exported integration.net",
       "hierarchical_sheets":len(sheets),
       "sheets":[{"page":int(k),"path":v} for k,v in sheets],
       "component_instances":len(components),
       "distinct_reference_designators":len(refs),
       "reference_collisions":len(conflicts),
       "total_duplicate_excess":sum(len(v)-1 for v in conflicts.values()),
       "collisions":conflicts,
       "nets_exported":len(nets),
       "project_annotation_ready":not bool(conflicts),
       "electrical_interconnects_qualified":False,
       "all_hardware_for_FAB_validated":False,
       "tx_permission":False
    }

def main():
    if not NET.is_file():
        raise FileNotFoundError("Native KiCad integration.net missing")
    output=analyze(NET.read_text(encoding="utf-8",errors="replace"))
    (OUT/"integration_reference_collisions.json").write_text(
        json.dumps(output,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("KiCad:",output["hierarchical_sheets"],"sheets,",
          output["component_instances"],"component instances,",
          output["nets_exported"],"nets,",
          output["reference_collisions"],"ambiguous reference designators")
    if output["project_annotation_ready"]:
        print("WARNING: duplicate names are gone; manual annotation review is still needed")
    else:
        print("BLOCKER: repeated component refs across modules (do not fabricate)")
    return 0

if __name__=="__main__":
    sys.exit(main())
