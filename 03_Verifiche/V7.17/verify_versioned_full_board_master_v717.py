"""V7.17 KiCad-native parity check of versioned FULL-RADIO integration index.

The versioned root is an intentional *HOLD MASTER*; updated annotations do not
constitute new wires, joined power rails or layout of the whole board.
"""
import json
import re
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche"/"V7.17"/"output-ci"
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.13"))
from verifica_netlist_rx_v713 import native_netlist
from audit_full_board_native_v717 import native_erc
BASE=ROOT/"04_KiCad"/"Assemblaggio_RX_Power_V7.14_LIB_NOT_FOR_FAB"/"S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
MASTER=ROOT/"04_KiCad"/"Assemblaggio_RX_Power_V7.17_INTEGRATION_HOLD_NOT_FOR_FAB"/BASE.name

def sheets(src):
    return re.findall(r'\(property "Sheetfile" "([^"]+)"',src)

def main():
    a=native_netlist(OUT/"root_v714.current.net")
    b=native_netlist(OUT/"root_v717.hold_master.net")
    old=native_erc(OUT/"root_v714.current.erc.rpt")
    new=native_erc(OUT/"root_v717.hold_master.erc.rpt")
    raw_before=BASE.read_text(encoding="utf-8")
    raw_after=MASTER.read_text(encoding="utf-8")
    keys=(("symbol (lib_id","(wire (pts","(pin \"","(global_label \""),)
    equality={
        "same_exact_net_names":set(a)==set(b),
        "same_every_native_ref_pin_membership":a==b,
        "same_erc_all_categories":old["categories"]==new["categories"],
        "same_erc_totals":(old["errors"],old["warnings"])==
                          (new["errors"],new["warnings"]),
        "same_child_schematic_paths":sheets(raw_before)==sheets(raw_after),
        "no_new_root_sheet_pins":raw_before.count('(pin "')==raw_after.count('(pin "'),
        "no_new_root_wires":raw_before.count("(wire (pts")==raw_after.count("(wire (pts"),
        "no_new_global_labels":raw_before.count('(global_label "')==
                               raw_after.count('(global_label "')
    }
    result={
        "revision":"V7.17",
        "scope":"native KiCad full seven-sheet hierarchy V7.14 vs versioned V7.17 HOLD master",
        "baseline_nets":len(a),"candidate_nets":len(b),
        "baseline_erc":{"errors":old["errors"],"warnings":old["warnings"]},
        "candidate_erc":{"errors":new["errors"],"warnings":new["warnings"]},
        "invariants":equality,
        "electrically_joined_modules":0,
        "new_board_fabrication_allowed":False,
        "tx_permitted":False
    }
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v717.full_board_master_native_parity.json").write_text(
        json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
    if not all(equality.values()):
        raise SystemExit("FAIL CLOSED: versioned root was unintentionally rewired or altered ERC")
    if len(a)!=99 or new["errors"]!=43 or new["warnings"]!=340:
        raise SystemExit("FAIL CLOSED: master ERC/netlist unexpected baseline")
    if not ("V7.17" in raw_after and "NO FAB / NO TX" in raw_after):
        raise SystemExit("FAIL CLOSED: master missing explicit safety intent")
    print("PASS V7.17 real KiCad seven-sheet master with all original ref-pin connectivity unchanged; NO FAB/TX")

if __name__=="__main__":
    main()
