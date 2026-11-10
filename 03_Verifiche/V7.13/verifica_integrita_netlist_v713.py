"""Compare real KiCad9 exported netlists before/after 50mil RX graphic snap.

A KiCad ERC warning reduction must NOT hide changed electrical connections.
The comparison is by every net's exact member (reference,pin) pair, not
only by net count. It does NOT validate electrical correctness or RF hardware.
"""
from pathlib import Path
import json
import re
import sys

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche"/"V7.13"/"output-ci"
ORIG=OUT/"hierarchy_v712.net"
NEW=OUT/"hierarchy_v713.net"

def sexpr_span(s,start):
    level=0
    quote=False
    backslash=False
    for i in range(start,len(s)):
        ch=s[i]
        if backslash:
            backslash=False
        elif quote and ch=="\\":
            backslash=True
        elif ch=='"':
            quote=not quote
        elif not quote:
            if ch=="(":
                level+=1
            elif ch==")":
                level-=1
                if level==0:
                    return s[start:i+1]
    raise ValueError("Unbalanced KiCad netlist block")

def connectivity(net):
    mapping={}
    for m in re.finditer(r'\(net \(code "(\d+)"\) \(name "([^"]+)"\)',net):
        body=sexpr_span(net,m.start())
        name=m.group(2)
        if name in mapping:
            raise ValueError("Duplicate KiCad net name "+name)
        # Each node is a physical symbol terminal; component ref stable in V7.12/13.
        nodes=re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)',body)
        if not nodes:
            raise ValueError("Empty net node membership: "+name)
        mapping[name]=tuple(sorted(nodes))
    if len(mapping)==0:
        raise ValueError("No KiCad nets parsed; cannot establish connectivity")
    return mapping

def main():
    a=connectivity(ORIG.read_text(encoding="utf-8"))
    b=connectivity(NEW.read_text(encoding="utf-8"))
    print("KiCad native net counts: baseline",len(a),"candidate",len(b),flush=True)
    diff={
      name:{"before":a.get(name),"after":b.get(name)}
      for name in sorted(set(a)|set(b)) if a.get(name)!=b.get(name)
    }
    result={
       "revision":"V7.13",
       "source":"KiCad 9 actual exported hierarchical netlists",
       "baseline_nets":len(a),
       "candidate_nets":len(b),
       "different_net_memberships":len(diff),
       "differences":diff,
       "all_connection_memberships_preserved":len(a)==len(b)==99 and not diff,
       "physical_connections_added":False,
       "ERC_clean":False,"DRC_clean":False,
       "fabrication_permitted":False,"tx_permitted":False,
    }
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"hierarchy_net_pin_membership_v713.json").write_text(
         json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,ensure_ascii=False))
    if not result["all_connection_memberships_preserved"]:
        raise SystemExit("BLOCKER: 50mil snap changed KiCad electrical connectivity")
    print("PASS V7.13 native KiCad exact net-pin membership invariance; NO FAB/NO TX")

if __name__=="__main__":
    main()
