"""V7.13 rigorous native KiCad connectivity gate for 1.27mm RX coordinate snap.

Compare actual KiCad-exported net name and each pin membership; zero tolerated
changes, even when the total count of nets stays fixed. No DSP/firmware/FAB/TX.
"""
import json
import re
import sys
from pathlib import Path
from collections import Counter
OUT=Path(__file__).resolve().parent/"output-ci"

def native_netlist(path):
    src=Path(path).read_text(encoding="utf-8")
    if not src.startswith("(export ") or "(nets" not in src:
        raise ValueError("not an actual KiCad export")
    nets={}
    current=None
    for line in src.splitlines():
        m=re.match(r'^    \(net \(code "\d+"\) \(name "([^"]+)"\)',line)
        if m:
            name=m.group(1)
            if name in nets:
                raise ValueError("duplicate net name: "+name)
            nets[name]=[]
            current=name
        elif current is not None:
            n=re.search(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)',line)
            if n:
                nets[current].append((n.group(1),n.group(2)))
    if len(nets)<8:
        raise ValueError("unexpectedly small RX netlist")
    if any(len(v)==0 for v in nets.values()):
        raise ValueError("empty native net")
    return {k:sorted(v) for k,v in sorted(nets.items())}

def main():
    old=native_netlist(OUT/"rx_v712_baseline.net")
    new=native_netlist(OUT/"rx_v713_snapped.net")
    before_pairs=Counter((name,ref,pin) for name,nodes in old.items() for ref,pin in nodes)
    after_pairs=Counter((name,ref,pin) for name,nodes in new.items() for ref,pin in nodes)
    delta_removed=list((before_pairs-after_pairs).elements())
    delta_added=list((after_pairs-before_pairs).elements())
    result={
        "source":"real KiCad9 sch export netlist from both standalone RX .kicad_sch files",
        "baseline_net_count":len(old),
        "new_net_count":len(new),
        "pin_memberships_before":sum(map(len,old.values())),
        "pin_memberships_after":sum(map(len,new.values())),
        "same_net_names":set(old)==set(new),
        "same_all_pin_memberships":before_pairs==after_pairs,
        "removed":delta_removed,"added":delta_added,
        "approved_physical_interconnects":False,
        "pcb_fabrication_approved":False,"TX_permission":False
    }
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"rx_v713_netlist_pin_parity.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(result,indent=2,ensure_ascii=False))
    if not result["same_net_names"] or not result["same_all_pin_memberships"]:
        raise SystemExit("CRITICAL: KiCad RX connectivity changed on snap-to-grid; fail closed")
    print("PASS RX 1.27mm grid alignment has IDENTICAL native KiCad net-pin memberships")

if __name__=="__main__":
    main()
