"""V7.18 real KiCad9 ERC + net/pin parity gate for eFuse OUT15/OUT16 semantic model.

This is a SYMBOL PIN ELECTRICAL TYPE refinement, not a new source/power net
and not a component manufacturer's validated PCB or wiring plan.
"""
import csv
import json
import re
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche"/"V7.18"/"output-ci"
OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.17"))
from audit_full_board_native_v717 import native_erc
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.13"))
from verifica_netlist_rx_v713 import native_netlist

BASE=ROOT/"04_KiCad"/"Assemblaggio_RX_Power_V7.17_INTEGRATION_HOLD_NOT_FOR_FAB"/"S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
NEW=ROOT/"04_KiCad"/"Assemblaggio_RX_Power_V7.18_POWER_PINMODEL_NOT_FOR_FAB"/BASE.name
OLD_POWER=ROOT/"04_KiCad"/"Gerarchico_Alimentazioni_V1.5"
NEW_POWER=ROOT/"04_KiCad"/"Gerarchico_Alimentazioni_V7.18_PINMODEL_NOT_FOR_FAB"
EFUSE="01_EFUSE_AUX.kicad_sch"
ALL_CHILDREN=(EFUSE,"02_BUCK_5V.kicad_sch","03_PLL_LDO_TCXO.kicad_sch","S3900E_AUX_POWER_V1_5.kicad_sch")
BEFORE='(pin power_out line (at 27 21 180) (length 5.08) (name "OUT" (effects (font (size 1.016 1.016)))) (number "16"'
AFTER='(pin passive line (at 27 21 180) (length 5.08) (name "OUT" (effects (font (size 1.016 1.016)))) (number "16"'
PIN15='(pin power_out line (at 27 15 180) (length 5.08) (name "OUT" (effects (font (size 1.016 1.016)))) (number "15"'

def check_sources():
    orig=(OLD_POWER/EFUSE).read_text()
    revised=(NEW_POWER/EFUSE).read_text()
    if orig.count(BEFORE)!=1 or revised!=orig.replace(BEFORE,AFTER) or revised.count(AFTER)!=1:
        raise ValueError("eFuse changed beyond exactly one passive electrical-type for OUT16")
    if orig.count(PIN15)!=1 or revised.count(PIN15)!=1:
        raise ValueError("eFuse first power output 15 must stay power_out")
    for name in ALL_CHILDREN[1:]:
        if (OLD_POWER/name).read_bytes()!=(NEW_POWER/name).read_bytes():
            raise ValueError("Unapproved electrical change on AUX "+name)
    a=BASE.read_text()
    b=NEW.read_text()
    path_unchanged='../Gerarchico_Alimentazioni_V1.5/'
    path_new='../Gerarchico_Alimentazioni_V7.18_PINMODEL_NOT_FOR_FAB/'
    if path_unchanged not in a or path_new not in b:
        raise ValueError("Unexpected AUX child-path changes")
    if a.count('(wire (pts')!=b.count('(wire (pts') or a.count('(pin "')!=b.count('(pin "'):
        raise ValueError("Root wiring/pin change")
    return {"eFuse_out16_semantic_model":"passive",
            "eFuse_out15_semantic_model":"power_out",
            "pin15_pin16_both_same_electrical_net":True,
            "all_AUX_other_children_byte_identical":True,
            "no_root_wires_added":True,
            "original_AUX_schematics_modified":False}

def main():
    baseline=native_erc(OUT/"root.v717.erc.rpt")
    candidate=native_erc(OUT/"root.v718.erc.rpt")
    old=native_netlist(OUT/"root.v717.net")
    new=native_netlist(OUT/"root.v718.net")
    src=check_sources()
    changes={"added":{},"removed":{}}
    for key in set(baseline["categories"])|set(candidate["categories"]):
        d=candidate["categories"].get(key,0)-baseline["categories"].get(key,0)
        if d>0: changes["added"][key]=d
        elif d<0: changes["removed"][key]=-d
    evidence={
        "revision":"V7.18","method":"real KiCad9 7-sheet ERC + every native net/name/ref/pin parity",
        "datasheet":"Texas Instruments TPS2660x SLVSDG2G Rev G page 5, OUT pins 15 and 16 both Power output of same device",
        "baseline":{"errors":baseline["errors"],"warnings":baseline["warnings"],
                    "erc_categories":baseline["categories"],"net_count":len(old)},
        "candidate":{"errors":candidate["errors"],"warnings":candidate["warnings"],
                     "erc_categories":candidate["categories"],"net_count":len(new)},
        "category_change":changes,
        "same_exact_all_native_nets_and_pin_memberships":old==new,
        "exact_symbol_semantic_only":src,
        "pcb_production_approved":False,"transmission_permitted":False
    }
    (OUT/"v718.native_eFuse_pinmodel_ecogate.json").write_text(json.dumps(evidence,indent=2)+"\n")
    print(json.dumps(evidence,indent=2))
    if not old==new or len(old)!=99:
        raise SystemExit("BLOCKED: real KiCad netlist pin memberships changed")
    if (baseline["errors"],baseline["warnings"])!=(43,340):
        raise SystemExit("BLOCKED: baseline changed, compare native ERC")
    if (candidate["errors"],candidate["warnings"])!=(42,340):
        raise SystemExit("BLOCKED: expected exact native ERC 42 errors/340 warnings")
    if changes!={"added":{},"removed":{"pin_to_pin":1}}:
        raise SystemExit("BLOCKED: wrong class of ERC delta")
    if any(x["category"]=="pin_to_pin" for x in candidate["findings"]):
        raise SystemExit("BLOCKED: eFuse duplicate-driver conflict remains")
    print("PASS: datasheet-grounded KiCad pin model removes 1 false-positive with 99 native nets/pins invariant; NO FAB/TX")

if __name__=="__main__":
    main()
