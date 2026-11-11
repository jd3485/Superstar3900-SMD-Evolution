"""V7.19 RELEASE GATE: real KiCad9 seven-sheet netlist/Electrical Rule Check.

Versioned candidate is NOT fabricated. Exactly six fully specified label attachments
in a new PLL sheet are permitted. The native netlist, not ERC counts, proves the
TI Figure 179 series/shunt loop component pin memberships.
"""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche"/"V7.19"/"output-ci"
OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.17"))
from audit_full_board_native_v717 import native_erc
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.13"))
from verifica_netlist_rx_v713 import native_netlist
OLD_POWER=ROOT/"04_KiCad"/"Gerarchico_Alimentazioni_V7.18_PINMODEL_NOT_FOR_FAB"
NEW_POWER=ROOT/"04_KiCad"/"Gerarchico_Alimentazioni_V7.19_PLL_PINNET_NOT_FOR_FAB"
OLD_ROOT=ROOT/"04_KiCad"/"Assemblaggio_RX_Power_V7.18_POWER_PINMODEL_NOT_FOR_FAB"
NEW_ROOT=ROOT/"04_KiCad"/"Assemblaggio_RX_Power_V7.19_PLL_PINNET_NOT_FOR_FAB"
TOP="S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
PLL="03_PLL_LDO_TCXO.kicad_sch"
MARKER=' (hierarchical_label "PLL_CE"'
POINTS=[
  ("PLL_CPOUT","84.92","157","c670cc06-71f6-5d12-b12f-3925c31ef7a7"),
  ("PLL_CPOUT","134.92","146.05","2f429b74-5d2b-5fd3-90cc-9f753836a95c"),
  ("PLL_VTUNE","145.08","146.05","5e75b2d7-e18d-51ea-ba9d-270d29597e48"),
  ("PLL_R2_C2","95.08","157","a1027cec-eea5-5521-aff4-13744c253199"),
  ("PLL_R2_C2","113","158.92","8adb07b0-d8dd-566a-a03b-292bffc00382"),
  ("PLL_VTUNE","174","158.92","e80d7df8-448a-5b5b-8a74-338c36732e0f")
]
PREFIX="/AUX_POWER_existing_V1_5_UNQUALIFIED/03 PLL + LDO + TCXO/"
CONTRACT=ROOT/"01_Specifiche"/"V7.19"/"CONTRATTO_TOPOLOGIA_LOOP_PLL_TI_V7_19.json"

def expected_source():
    old=(OLD_POWER/PLL).read_text()
    addition="".join('(label "'+n+'" (at '+x+' '+y+' 0) (effects (font (size 1.016 1.016)) (justify left bottom)) (uuid "'+uid+'"))\n'
                     for n,x,y,uid in POINTS)
    if old.count(MARKER)!=1:
        raise ValueError("PLL insertion anchor unexpectedly changed")
    return old.replace(MARKER,addition+MARKER,1)

def validate_source():
    new=(NEW_POWER/PLL).read_text()
    if expected_source()!=new:
        raise ValueError("V7.19 source not exactly six reviewed additional labels")
    if len(set(x[3] for x in POINTS))!=6:
        raise ValueError("Duplicate UUID for added KiCad label")
    for name in ("01_EFUSE_AUX.kicad_sch","02_BUCK_5V.kicad_sch","S3900E_AUX_POWER_V1_5.kicad_sch"):
        if (OLD_POWER/name).read_bytes()!=(NEW_POWER/name).read_bytes():
            raise ValueError("Non-PLL AUX sheet changed "+name)
    baseline=(OLD_ROOT/TOP).read_text()
    newmaster=(NEW_ROOT/TOP).read_text()
    if "../Gerarchico_Alimentazioni_V7.19_PLL_PINNET_NOT_FOR_FAB/" not in newmaster:
        raise ValueError("V7.19 root does not reference versioned PLL ECO")
    if baseline.count('(wire (pts')!=newmaster.count('(wire (pts'):
        raise ValueError("Extra physical intermodule wires not approved")
    if baseline.count('(pin "')!=newmaster.count('(pin "'):
        raise ValueError("Extra hierarchical crossmodule pins not approved")
    for name in (TOP.replace(".kicad_sch",".kicad_pro"),"fp-lib-table","sym-lib-table"):
        if (OLD_ROOT/name).read_bytes()!=(NEW_ROOT/name).read_bytes():
            raise ValueError("Root KiCad project or libraries silently altered "+name)
    if list(NEW_ROOT.glob("*.kicad_pcb")) or list(NEW_POWER.glob("*.kicad_pcb")):
        raise ValueError("Unexpected board/fabrication data")
    return {"exactly_six_new_pin_labels":True,"no_new_wires":True,
            "old_AUX_children_byte_identical":True,"no_new_board":True}

def main():
    src=validate_source()
    a=native_netlist(OUT/"v719.root_v718.net")
    b=native_netlist(OUT/"v719.root_v719.net")
    ea=native_erc(OUT/"v719.root_v718.erc.rpt")
    eb=native_erc(OUT/"v719.root_v719.erc.rpt")
    contract=json.loads(CONTRACT.read_text())
    expected=contract["expected_future_pin_nets"]
    targets={(("/AUX_POWER_existing_V1_5_UNQUALIFIED/GND_MAIN") if k=="GND_MAIN" else PREFIX+k):sorted((r,p) for r,p in v)
             for k,v in expected.items()}
    for name,want in targets.items():
        got=b.get(name,[])
        if name.endswith("/GND_MAIN"):
            if not set(want).issubset(set(got)):
                raise SystemExit("FAIL CLOSED: missing PLL GND shunts "+name)
        elif got!=want:
            raise SystemExit("FAIL CLOSED: TI loop pin net "+name+": expected "+repr(want)+" actual "+repr(got))
    diffs={k:{"old":a.get(k,[]),"new":b.get(k,[])}
          for k in sorted(set(a)|set(b)) if a.get(k,[])!=b.get(k,[])}
    allowed={PREFIX+"PLL_CPOUT",PREFIX+"PLL_VTUNE",PREFIX+"PLL_R2_C2"}
    # Native netlist often has prefix inheritance on standalone grounds; require
    # ALL changed memberships confined strictly to the three TI intended nodes.
    if set(diffs)!=allowed:
        raise SystemExit("FAIL CLOSED: unrelated net/pin topology changed "+repr(sorted(set(diffs)-allowed)))
    report={
      "revision":"V7.19","evidence":"real KiCad9 netlist and complete ERC, 7-sheet original and versioned master",
      "baseline":{"erc_errors":ea["errors"],"erc_warnings":ea["warnings"],"net_count":len(a),
                  "categories":ea["categories"]},
      "candidate":{"erc_errors":eb["errors"],"erc_warnings":eb["warnings"],"net_count":len(b),
                   "categories":eb["categories"]},
      "exact_ERC_category_delta":{k:eb["categories"].get(k,0)-ea["categories"].get(k,0)
                         for k in sorted(set(ea["categories"])|set(eb["categories"]))
                         if eb["categories"].get(k,0)!=ea["categories"].get(k,0)},
      "changed_native_ref_pin_net_memberships":diffs,
      "exact_manufacturer_figure179_pin_nets_verified":True,
      "source_constraints":src,
      "interface_crossmodule_approved":0,
      "all_existing_15_interfaces_open_hold":True,
      "vendor_values_and_RF_stability_approved":False,
      "full_radio_board_layout_created":False,
      "fab_authorized":False,
      "TX_permitted":False
    }
    (OUT/"v719.real_full_master_erc_netlist_gate.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    if (ea["errors"],ea["warnings"],len(a))!=(42,340,99):
        raise SystemExit("FAIL CLOSED: changed historical baseline")
    if (eb["errors"],eb["warnings"],len(b))!=(36,340,100):
        raise SystemExit("FAIL CLOSED: versioned KiCad PLL native result not 36/340 and 100 nets")
    if report["exact_ERC_category_delta"]!={"pin_not_connected":-2,"pin_not_driven":-1,"wire_dangling":-3}:
        raise SystemExit("FAIL CLOSED: unexpected ERC category change")
    print("PASS native TI 3-pole PLL topology pin-to-net qualified at CAD connectivity level; 36 ERC errors remain, NO FAB/TX")

if __name__=="__main__":
    main()
