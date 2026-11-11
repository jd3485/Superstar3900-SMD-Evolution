"""V7.20 native full-radio ERC power-source ledger: no made-up power flags.

Counts six KiCad9 power_pin_not_driven and maps EACH to its exact native
net and node types; refuses any release if status is changed under our feet.
PCB and source design are never edited. This is engineering classification,
NOT a way to suppress ERC.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche"/"V7.20"/"output-ci"
OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.17"))
from audit_full_board_native_v717 import native_erc

ERC=OUT/"v720.root_v719.erc.rpt"
NET=OUT/"v720.root_v719.net"
SOURCE_MASTER=ROOT/"04_KiCad"/"Assemblaggio_RX_Power_V7.19_PLL_PINNET_NOT_FOR_FAB"/"S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"

EXPECTED={
 ("U200","1"):{"name":"EFUSE_VIN","reason":"Unqualified external 13.8-V source and input protection/connector/return","gate":"INPUT_13V8_POWER_REVERSE_AND_TRANSIENT_HOLD"},
 ("U200","8"):{"name":"EFUSE_RTN","reason":"eFuse reverse-polarity return separate from GND_MAIN; cannot automatically short","gate":"EFUSE_RTN_REVERSE_PROTECTION_HOLD"},
 ("U2","1"):{"name":"5V_RF_PREREGULATED","reason":"5-V buck rail through passive filter; source, DC/thermal and current budget not signed off","gate":"BUCK_LDO_SOURCE_5V_HOLD"},
 ("U2","2"):{"name":"GND_MAIN","reason":"Ground return has no EDA power driver; current return, reference partition and EMC not qualified","gate":"PLL_LDO_GROUND_RETURN_HOLD"},
 ("U6203","1"):{"name":"5V_DIGITAL_FILTERED","reason":"MCU digital input power source/connector and filter are not cross-module qualified","gate":"MCU_LDO_5V_DIGITAL_HOLD"},
 ("U6203","2"):{"name":"GND","reason":"MCU ground net is isolated from AUX GND_MAIN pending review, cannot merge blindly","gate":"MCU_GND_PARTITION_HOLD"},
}

def export_net_nodes(path):
    raw=path.read_text()
    if not raw.startswith("(export (version ") or "(nets" not in raw:
        raise ValueError("not native KiCad netlist")
    starts=list(re.finditer(r'^    \(net \(code "(\d+)"\) \(name "([^"]+)"\) \(class "Default"\)',raw,re.M))
    if len(starts)!=100 or len({x.group(2) for x in starts})!=100:
        raise ValueError("Expected real KiCad V7.19 100 nets")
    nodes_by_net={}
    for i,m in enumerate(starts):
        section=raw[m.end():starts[i+1].start()] if i+1<len(starts) else raw[m.end():]
        nodes=[{"ref":r,"pin":pin,"pin_type":kind}
            for r,pin,kind in re.findall(
                r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)(?: \(pinfunction "[^"]*"\))? \(pintype "([^"]+)"\)\)',section)]
        if not nodes:
            raise ValueError("Failed to parse native KiCad nodes "+m.group(2))
        nodes_by_net[m.group(2)]=nodes
    return nodes_by_net

def main():
    if not SOURCE_MASTER.exists():
        raise SystemExit("Versioned V7.19 main not found")
    erc=native_erc(ERC)
    nets=export_net_nodes(NET)
    if (erc["errors"],erc["warnings"])!=(36,340):
        raise SystemExit("Root ERC changed, don't classify stale baseline")
    if erc["categories"].get("power_pin_not_driven")!=6:
        raise SystemExit("Power issue count unexpected")
    refs={}
    for item in erc["findings"]:
        if item["category"]!="power_pin_not_driven":continue
        pins=set()
        for loc in item["locations"]:
            k=re.search(r"Symbol (U\d+) Pin (\d+) \[",loc)
            if k:pins.add((k.group(1),k.group(2)))
        if len(pins)!=1 or next(iter(pins)) in refs:
            raise SystemExit("Unexpected native ERC power pin finding "+repr(item))
        key=next(iter(pins))
        refs[key]={"sheet":item["sheet"],"locations":item["locations"]}
    if set(refs)!=set(EXPECTED):
        raise SystemExit("Native ERC changed physical power-pin set: "+repr(set(refs)^set(EXPECTED)))
    evidence=[]
    for (ref,pin),rule in sorted(EXPECTED.items()):
        matches=[(name,nodes) for name,nodes in nets.items()
                 if any(node["ref"]==ref and node["pin"]==pin for node in nodes)]
        if len(matches)!=1 or matches[0][0].split("/")[-1]!=rule["name"]:
            raise SystemExit(f"Unexpected native net for {ref} pin {pin}: {matches}")
        name,nodes=matches[0]
        if any(node["pin_type"]=="power_out" for node in nodes):
            raise SystemExit(f"ERC input power wrongly listed undriven despite same-net power output: {name}")
        evidence.append({
           "reference":ref,"pin":pin,"exact_kicad_native_net":name,
           "native_node_count":len(nodes),
           "native_pin_type_counts":dict(sorted(Counter(n["pin_type"] for n in nodes).items())),
           "same_net_power_out_count":0,"issue_locations":refs[(ref,pin)]["locations"],
           "electrical_qualification":"HOLD",
           "review_gate":rule["gate"],"engineering_reason":rule["reason"]
        })
    result={"revision":"V7.20","method":"actual native KiCad9 seven-sheet ERC+exported netlist, all node pin types",
        "root_erc_errors":erc["errors"],"root_erc_warnings":erc["warnings"],"root_nets":len(nets),
        "undriven_power_pins":evidence,"count":len(evidence),
        "power_source_waivers_added":0,"artificial_pwr_flags_added":0,
        "voltage_domains_joined_without_qualification":0,
        "gnd_main_to_efuse_rtn_short_added":False,
        "all_15_crossmodule_contracts_open_hold":True,
        "no_fab":True,"no_tx":True}
    (OUT/"v720.native_undriven_power_ledger.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    print("PASS: all 6 undriven power input pins mapped to actual nets and classified HOLD; no artificial ERC closures")
if __name__=="__main__":main()
