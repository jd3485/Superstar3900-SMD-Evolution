"""Non-committing experiment: native KiCad9 comparison of R2/R3 loop-filter wires.

All variants are on throw-away *complete KiCad project* sibling clones. Never
apply a variant to an actual schematic merely because the ERC total improves:
the RF loop topology and component pin-to-net membership must be validated.
"""
import contextlib
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import uuid
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CAD=ROOT/"04_KiCad"
POWER=CAD/"Gerarchico_Alimentazioni_V7.18_PINMODEL_NOT_FOR_FAB"
MASTER=CAD/"Assemblaggio_RX_Power_V7.18_POWER_PINMODEL_NOT_FOR_FAB"
TOP_FILE="S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
PLL_FILE="03_PLL_LDO_TCXO.kicad_sch"
OUT=ROOT/"03_Verifiche"/"V7.18"/"output-ci"
OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.17"))
from audit_full_board_native_v717 import native_erc
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.13"))
from verifica_netlist_rx_v713 import native_netlist

def replace_one(text,old,new):
    if text.count(old)!=1:
        raise ValueError(f"Expected exact one source element for variant: {old}")
    return text.replace(old,new,1)

def edit_pll(original,variant):
    s=original
    if variant in ("r2_outside_body_lead","r2_outside_plus_R3_pin_rotation"):
        s=replace_one(s,
            '(wire (pts (xy 90 146.05) (xy 90 157)) (stroke (width 0) (type default)) (uuid 87ba95ea-2452-4120-bd4c-6891bcc000ea))\n','')
        s=replace_one(s,
            '(wire (pts (xy 90 157) (xy 84.92 157)) (stroke (width 0) (type default)) (uuid 65b68865-e61b-44c8-aeee-816d7dae2173))\n','')
        s=replace_one(s,
            '(wire (pts (xy 51 146.05) (xy 134.92 146.05)) (stroke (width 0) (type default)) (uuid a07f120a-cf4e-44fb-add0-a2d82277ae44))\n',
            '(wire (pts (xy 51 146.05) (xy 78 146.05)) (stroke (width 0) (type default)) (uuid a07f120a-cf4e-44fb-add0-a2d82277ae44))\n'
            '(wire (pts (xy 78 146.05) (xy 134.92 146.05)) (stroke (width 0) (type default)) (uuid d8d1885a-e3d0-4798-b95b-ac5c49839b08))\n'
            '(wire (pts (xy 78 146.05) (xy 78 157)) (stroke (width 0) (type default)) (uuid fa2e3f0f-4d5c-48e8-8f76-b23b82a2a2ca))\n'
            '(wire (pts (xy 78 157) (xy 84.92 157)) (stroke (width 0) (type default)) (uuid 56d77508-3b8a-4a2a-9cc9-34b12576afaa))\n'
            '(junction (at 78 146.05) (diameter 0) (color 0 0 0 0) (uuid 3ead4626-fcfb-4b0a-b897-8d0dcfd019d6))\n')
    if variant in ("r3_pin180_only","r2_outside_plus_R3_pin_rotation"):
        s=replace_one(s,
            '(symbol (lib_id "S3900E:R") (at 140 146.05 0) (unit 1)',
            '(symbol (lib_id "S3900E:R") (at 140 146.05 180) (unit 1)')
    if variant=="as_is":
        if s!=original:
            raise ValueError("Baseline altered")
    elif s==original:
        raise ValueError("Experiment did not change source")
    return s

def run_variant(variant,original):
    with contextlib.ExitStack() as stack:
        aux=Path(stack.enter_context(tempfile.TemporaryDirectory(prefix="Gerarchico_Alimentazioni_V718__test_",dir=CAD)))
        master=Path(stack.enter_context(tempfile.TemporaryDirectory(prefix="Assemblaggio_RX_Power_V718__test_",dir=CAD)))
        shutil.copytree(POWER,aux,dirs_exist_ok=True)
        shutil.copytree(MASTER,master,dirs_exist_ok=True)
        (aux/PLL_FILE).write_text(edit_pll(original,variant),encoding="utf-8")
        candidate=master/TOP_FILE
        before=candidate.read_text(encoding="utf-8")
        old="../"+POWER.name+"/"
        candidate.write_text(replace_one(before,old,"../"+aux.name+"/"),encoding="utf-8")
        drc_path=OUT/("v718."+variant+".root.erc.rpt")
        net_path=OUT/("v718."+variant+".root.net")
        for cmd in (
            ["kicad-cli","sch","erc","-o",str(drc_path),str(candidate)],
            ["kicad-cli","sch","export","netlist","-o",str(net_path),str(candidate)]
        ):
            p=subprocess.run(cmd,capture_output=True,text=True)
            if p.returncode:
                raise RuntimeError("Real KiCad command failed for "+variant+": "+(p.stderr+p.stdout)[-1200:])
        erc=native_erc(drc_path)
        net=native_netlist(net_path)
        return {"name":variant,"erc_errors":erc["errors"],"erc_warnings":erc["warnings"],
                "categories":erc["categories"],"native_nets":net}

def main():
    original=(POWER/PLL_FILE).read_text(encoding="utf-8")
    original_hash=hashlib.sha256((POWER/PLL_FILE).read_bytes()).hexdigest()
    plans=("as_is","r2_outside_body_lead","r3_pin180_only","r2_outside_plus_R3_pin_rotation")
    results={}
    for plan in plans:
        try:
            results[plan]=run_variant(plan,original)
            print(plan,"ERC errors/warnings",results[plan]["erc_errors"],
                  results[plan]["erc_warnings"],flush=True)
        except Exception as ex:
            results[plan]={"status":"FAILED","reason":repr(ex)}
            print(plan,"FAILED",repr(ex),flush=True)
    for plan,value in results.items():
        if value.get("status")=="FAILED":
            raise SystemExit("Native PLL candidate probe failure "+plan)
    baseline=results["as_is"]
    report={
        "revision":"V7.18",
        "provenance":"native KiCad 9 disposable sibling full KiCad project clone",
        "source_unchanged":hashlib.sha256((POWER/PLL_FILE).read_bytes()).hexdigest()==original_hash,
        "original_native_errors":baseline["erc_errors"],
        "experiments":{},
        "no_PLL_candidate_auto_approved":True,
        "full_board_layout_created":False,
        "no_fab":True,"no_tx":True
    }
    for plan,value in results.items():
        old=baseline["native_nets"]
        new=value["native_nets"]
        affected={name:{"old":old.get(name,[]),"candidate":new.get(name,[])}
             for name in sorted(set(old)|set(new)) if old.get(name)!=new.get(name)}
        report["experiments"][plan]={
            "erc_errors":value["erc_errors"],"erc_warnings":value["erc_warnings"],
            "categories":value["categories"],"native_net_count":len(new),
            "changed_exact_native_ref_pin_net_memberships":affected
        }
    (OUT/"v718.pll_loop_candidates_native.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:{"ERC":x["erc_errors"],"nets":len(x["native_nets"])}
                      for k,x in results.items()},indent=2))
    if not report["source_unchanged"] or baseline["erc_errors"]!=42 or baseline["erc_warnings"]!=340:
        raise SystemExit("Native baseline changed or V7.18 source was modified")
    print("PASS: four genuine KiCad loop-filter clone experiments; NO auto wiring or FAB/TX")

if __name__=="__main__":
    main()
