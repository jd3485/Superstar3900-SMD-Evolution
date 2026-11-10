"""V7.17 native *whole-radio hierarchy* ERC and interface audit.

Read actual KiCad 9 ERC and netlist; don't invent or hook up module pins.
Fulfills the design-readiness gate WITHOUT changing the 7-sheet circuit.
"""
import csv
import difflib
import json
import re
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche"/"V7.17"/"output-ci"
OUT.mkdir(parents=True,exist_ok=True)
HISTORIC_MATRIX=ROOT/"04_KiCad"/"Assemblaggio_RX_Power_V7.10_NOT_FOR_FAB"/"MATRICE_INTERFACCE_DA_QUALIFICARE_V7_10.csv"
MATRIX=ROOT/"04_KiCad"/"Assemblaggio_RX_Power_V7.17_INTEGRATION_HOLD_NOT_FOR_FAB"/"MATRICE_INTERFACCE_PROPOSTE_V7_17_OPEN_HOLD.csv"
MAPPING={
    "AUX_V1.5":"/AUX_POWER_existing_V1_5_UNQUALIFIED/",
    "MCU_CODEC_V2.1":"/MCU_CODEC_AFE_existing_V2_1_UNQUALIFIED/",
    "RX_V5.2":"/RX_50OHM_coupon_existing_V5_2_UNQUALIFIED/"
}
EXPECTED={
    "label_dangling":26,
    "wire_dangling":3,
    "power_pin_not_driven":6,
    "pin_to_pin":1,
    "pin_not_driven":5,
    "pin_not_connected":2,
    "endpoint_off_grid":219,
    "lib_symbol_issues":117,
    "footprint_link_issues":4
}
DANGER={"power_pin_not_driven","pin_to_pin","pin_not_driven","pin_not_connected","wire_dangling"}
ROOT_PREFIXES=tuple(MAPPING.values())

def native_erc(src):
    text=Path(src).read_text(encoding="utf-8",errors="replace")
    if not text.startswith("ERC report ("):
        raise ValueError("Not a native KiCad ERC report")
    totals=re.search(r"\*\* ERC messages: (\d+)\s+Errors (\d+)\s+Warnings (\d+)",text)
    if not totals:
        raise ValueError("Missing KiCad native ERC totals")
    issues=[]
    sheet=None
    current=None
    for line in text.splitlines():
        if line.startswith("***** Sheet "):
            sheet=line[len("***** Sheet "):].strip()
        elif line.startswith("[") and "]:" in line:
            if current is not None:
                issues.append(current)
            typ,description=line[1:].split("]:",1)
            current={"category":typ,"message":description.strip(),"sheet":sheet,
                     "severity":None,"locations":[]}
        elif current is not None:
            if line.strip() in ("; error","; warning"):
                current["severity"]=line.strip().split()[1]
            if line.strip().startswith("@("):
                current["locations"].append(line.strip())
    if current is not None:
        issues.append(current)
    counts=Counter(x["category"] for x in issues)
    severities=Counter(x["severity"] for x in issues)
    if severities["error"]!=int(totals[2]) or severities["warning"]!=int(totals[3]):
        raise ValueError("Per-item severity/count mismatch in native ERC")
    if len(issues)!=int(totals[1]):
        raise ValueError("Per-item number mismatch with native ERC header")
    by_sheet=defaultdict(lambda:{"errors":0,"warnings":0,"categories":Counter()})
    for x in issues:
        h=by_sheet[x["sheet"]]
        h[x["severity"]+"s"]+=1
        h["categories"][x["category"]]+=1
    return {
        "total":int(totals[1]),"errors":int(totals[2]),
        "warnings":int(totals[3]),"categories":dict(sorted(counts.items())),
        "by_sheet":{s:{"errors":v["errors"],"warnings":v["warnings"],
                       "categories":dict(v["categories"])} for s,v in sorted(by_sheet.items())},
        "findings":issues
    }

def native_nets(path):
    text=Path(path).read_text(encoding="utf-8",errors="replace")
    if not text.startswith("(export (version ") or "(nets" not in text:
        raise ValueError("Not KiCad native netlist")
    matches=re.findall(r'^    \(net \(code "\d+"\) \(name "([^"]+)"\)',text,re.M)
    if len(matches)!=len(set(matches)) or len(matches)<50:
        raise ValueError("Unexpected root KiCad netlist")
    return matches

def port_candidates(net_names,module,requested):
    if module not in MAPPING:
        return {"status":"EXTERNAL_NOT_IN_CAD","requested_net":requested,
                "exact_matches":[],"similar":[]}
    prefix=MAPPING[module]
    module_nets=[x for x in net_names if x.startswith(prefix)]
    exact=sorted(x for x in module_nets if x.rsplit("/",1)[-1]==requested)
    alternatives=sorted(set(x.rsplit("/",1)[-1] for x in module_nets))
    near=difflib.get_close_matches(requested,alternatives,n=3,cutoff=0.63)
    return {"status":"EXACT_NATIVE_NET_NAME" if exact else "NOT_FOUND_NATIVE_NETLIST",
            "requested_net":requested,"exact_matches":exact,"similar":near if not exact else []}

def audit_interfaces(net_names):
    with MATRIX.open(encoding="utf-8",newline="") as fh:
        records=list(csv.DictReader(fh))
    if len(records)!=15:
        raise ValueError("Expected all 15 historical OPEN/HOLD interfaces")
    with HISTORIC_MATRIX.open(encoding="utf-8",newline="") as fh:
        original=list(csv.DictReader(fh))
    if len(original)!=15:
        raise ValueError("History contract unexpectedly changed")
    for i,(old,new) in enumerate(zip(original,records),1):
        expected=dict(old)
        if old["domain"]=="rx_fm_audio":
            expected["candidate_destination_net"]="FM_DISCRIM_RAW"
            expected["blocker"]=new["blocker"]
            if "Canonical label" not in new["blocker"]:
                raise ValueError("FM signal label correction has no qualification warning")
        if expected!=new:
            raise ValueError("Unapproved interface contract change at row "+str(i))
    out=[]
    for idx,r in enumerate(records,1):
        if any(r[k]!=v for k,v in (
            ("physical_connection","OPEN"),("qualification","HOLD"),("tx_permission","0"))):
            raise ValueError("Interface unexpectedly released: "+r["domain"])
        src=port_candidates(net_names,r["source_module"],r["source_net"])
        dst=port_candidates(net_names,r["candidate_destination_module"],r["candidate_destination_net"])
        out.append({
            "id":f"I{idx:02d}","domain":r["domain"],
            "source_module":r["source_module"],"source":src,
            "candidate_destination_module":r["candidate_destination_module"],
            "candidate_destination":dst,
            "source_net":r["source_net"],"candidate_destination_net":r["candidate_destination_net"],
            "physical_connection":"OPEN","qualification":"HOLD",
            "tx_permission":0,"existing_blocker":r["blocker"],
            "name_match_does_not_qualify_electrical_connection":True
        })
    return out

def main():
    root=native_erc(OUT/"root_v714.current.erc.rpt")
    rx=native_erc(OUT/"rx_v714.current.erc.rpt")
    nets=native_nets(OUT/"root_v714.current.net")
    matrix=audit_interfaces(nets)
    bad=[x for x in nets if not x.startswith(ROOT_PREFIXES)]
    hard=[x for x in root["findings"] if x["category"] in DANGER]
    if root["categories"]!=EXPECTED:
        raise SystemExit("Unexpected root categories: inspect native KiCad ERC")
    if root["errors"]!=43 or root["warnings"]!=340:
        raise SystemExit("Root KiCad ERC baseline changed; do not silently claim progress")
    if rx["errors"]!=0 or rx["warnings"]!=0:
        raise SystemExit("RX standalone native ERC regression")
    if len(nets)!=99 or bad:
        raise SystemExit("Cross-sheet nets changed/merged without interface approval: "+repr(bad))
    if len(hard)!=17:
        raise SystemExit("Unexpected count in electrical-hard blockers")
    missing=[x for x in matrix if x["source"]["status"]=="NOT_FOUND_NATIVE_NETLIST"
             or x["candidate_destination"]["status"]=="NOT_FOUND_NATIVE_NETLIST"]
    if len(missing)!=2 or set(x["domain"] for x in missing)!={"rx_after_atten","interlock"}:
        raise SystemExit("Unexpected unmatched ports; FM destination should now be native-net name only")
    result={
        "revision":"V7.17",
        "method":"real native KiCad9 root and RX ERC plus native exported 7-sheet netlist",
        "root_erc":{
            k:v for k,v in root.items() if k!="findings"
        },
        "root_erc_full_issue_ledger":"v717.root_erc_issues.json",
        "errors_prioritization":{
            "dangling_labels_errors":root["categories"]["label_dangling"],
            "electrical_hard_errors_needing_engineering":len(hard),
            "hard_error_refs":[{"category":x["category"],"sheet":x["sheet"],
                                 "locations":x["locations"]} for x in hard],
            "off_grid_warnings":root["categories"]["endpoint_off_grid"],
            "library_warnings":root["categories"]["lib_symbol_issues"]+
                               root["categories"]["footprint_link_issues"]
        },
        "rx_erc":{"errors":rx["errors"],"warnings":rx["warnings"]},
        "native_net_count":len(nets),
        "native_net_names_scoped_within_original_modules":True,
        "module_interconnects_electrically_approved":0,
        "interface_matrix_count":len(matrix),"interfaces_open_hold":15,
        "matrix_approved_change":"FM discriminator destination label canonicalized, OPEN/HOLD unchanged",
        "interfaces_with_missing_net_name":len(missing),
        "interface_name_mismatches":[{"id":x["id"],"domain":x["domain"],
           "source":x["source"],"candidate_destination":x["candidate_destination"]}
           for x in missing],
        "report_net_name_presence_only_not_pin_level_qualification":True,
        "no_new_full_radio_pcb":True,
        "no_fabrication":True,"no_tx":True
    }
    (OUT/"v717.root_erc_issues.json").write_text(json.dumps(root["findings"],indent=2,ensure_ascii=False)+"\n")
    (OUT/"v717.interface_evidence.json").write_text(json.dumps(matrix,indent=2,ensure_ascii=False)+"\n")
    (OUT/"v717.full_board_readiness.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(result,indent=2,ensure_ascii=False))
    print("PASS: real KiCad whole-hierarchy/ERC inventory, all 15 OPEN/HOLD, 0 connection claims. NO FAB/TX.")

if __name__=="__main__":
    main()
