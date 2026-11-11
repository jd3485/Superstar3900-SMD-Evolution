"""V7.19: real KiCad9 loop-filter pin/net experiments on EPHEMERAL sibling clones.

Caution: experiments are NOT approvals. Vendor TI LMX2572 datasheet Fig.179
and SNAU217B EVM reference are topological constraints, not RF filter signoff.
"""
import contextlib,hashlib,json,re,shutil,subprocess,sys,tempfile,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CAD=ROOT/"04_KiCad"
POWER=CAD/"Gerarchico_Alimentazioni_V7.18_PINMODEL_NOT_FOR_FAB"
MASTER=CAD/"Assemblaggio_RX_Power_V7.18_POWER_PINMODEL_NOT_FOR_FAB"
PLL_FILE="03_PLL_LDO_TCXO.kicad_sch"
TOP="S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
OUT=ROOT/"03_Verifiche"/"V7.19"/"output-ci"
OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.17"))
from audit_full_board_native_v717 import native_erc
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.13"))
from verifica_netlist_rx_v713 import native_netlist

def exact(s,old,new):
    assert s.count(old)==1,(old,s.count(old))
    return s.replace(old,new,1)

def wire(a,b,uid):
    return "(wire (pts (xy "+a[0]+" "+a[1]+") (xy "+b[0]+" "+b[1]+")) (stroke (width 0) (type default)) (uuid "+uid+"))"
def drop(s,needle):
    return exact(s,needle+"\n","")
def add(s,elements):
    marker=' (hierarchical_label "PLL_CE"'
    assert marker in s
    return s.replace(marker,"".join(x+"\n" for x in elements)+marker,1)

W={
"trunk":"(wire (pts (xy 51 146.05) (xy 134.92 146.05)) (stroke (width 0) (type default)) (uuid a07f120a-cf4e-44fb-add0-a2d82277ae44))",
"r2_center":"(wire (pts (xy 90 146.05) (xy 90 157)) (stroke (width 0) (type default)) (uuid 87ba95ea-2452-4120-bd4c-6891bcc000ea))",
"r2_pin1_back":"(wire (pts (xy 90 157) (xy 84.92 157)) (stroke (width 0) (type default)) (uuid 65b68865-e61b-44c8-aeee-816d7dae2173))",
"r2_pin2":"(wire (pts (xy 95.08 157) (xy 113 157)) (stroke (width 0) (type default)) (uuid 8f8eb1a7-3c7c-4006-a18c-ee72d00508c5))",
"r2_to_c2":"(wire (pts (xy 113 157) (xy 113 158.92)) (stroke (width 0) (type default)) (uuid b235ea00-1c8d-49d3-9f73-981f494e4f0e))",
"r3_out":"(wire (pts (xy 145.08 146.05) (xy 183 146.05)) (stroke (width 0) (type default)) (uuid 5da5f63a-67c0-43d2-813f-1a5694993edb))",
"junction_r2":"(junction (at 90 146.05) (diameter 0) (color 0 0 0 0) (uuid 1cf0475e-783d-40a6-b8b5-61715140b083))"
}
def candidate(source,kind):
    if kind=="as_is":return source
    s=source
    if kind in ("r2_direct_pin","r2_r3_grid_reanchor","r2_direct_plus_r3_connected"):
        for label in ("r2_center","r2_pin1_back","junction_r2"):
            s=drop(s,W[label])
        x="84.92" if kind!="r2_r3_grid_reanchor" else "85.09"
        pinY="157" if kind!="r2_r3_grid_reanchor" else "157.48"
        r3_1="134.92" if kind!="r2_r3_grid_reanchor" else "134.62"
        s=drop(s,W["trunk"])
        s=add(s,[
          wire(("51","146.05"),(x,"146.05"),"a07f120a-cf4e-44fb-add0-a2d82277ae44"),
          wire((x,"146.05"),(r3_1,"146.05"),"46aa4b59-5eb0-4d47-b8d1-b086f47a56fa"),
          wire((x,"146.05"),(x,pinY),"99ae7f08-0d90-45ce-ac96-f798517c6bfd"),
          "(junction (at "+x+" 146.05) (diameter 0) (color 0 0 0 0) (uuid 52b09eea-f3cf-49a0-a668-8bd24d681c92))"
        ])
    if kind=="r2_direct_plus_r3_connected":
        # Tests whether one short, explicit legal segment is perceived when
        # touching R3 pin1; a diagnostically useful falsification only.
        s=add(s,[wire(("134.92","146.05"),("134.92","143.51"),"bd51548b-c81e-46f3-aa23-cd7dbe506079")])
    if kind=="r2_r3_grid_reanchor":
        s=exact(s,'(symbol (lib_id "S3900E:R") (at 90 157 0) (unit 1)',
                   '(symbol (lib_id "S3900E:R") (at 90.17 157.48 0) (unit 1)')
        s=exact(s,'(symbol (lib_id "S3900E:R") (at 140 146.05 0) (unit 1)',
                   '(symbol (lib_id "S3900E:R") (at 139.7 146.05 0) (unit 1)')
        s=drop(s,W["r2_pin2"])
        s=drop(s,W["r2_to_c2"])
        s=drop(s,W["r3_out"])
        s=add(s,[
          wire(("95.25","157.48"),("113","157.48"),"6c883e76-d42d-416c-ac30-6fa7d1b967cb"),
          wire(("113","157.48"),("113","158.92"),"916651ac-52fb-4ab3-b302-ae63931d2233"),
          wire(("144.78","146.05"),("183","146.05"),"773747c0-6a3b-49e3-a506-b04249387a14")
        ])
    assert s!=source
    return s

def experiment(kind):
    old=(POWER/PLL_FILE).read_text(encoding="utf-8")
    with contextlib.ExitStack() as stack:
        aux=Path(stack.enter_context(tempfile.TemporaryDirectory(prefix="Gerarchico_Alimentazioni_V719_probe_",dir=CAD)))
        master=Path(stack.enter_context(tempfile.TemporaryDirectory(prefix="Assemblaggio_RX_Power_V719_probe_",dir=CAD)))
        shutil.copytree(POWER,aux,dirs_exist_ok=True)
        shutil.copytree(MASTER,master,dirs_exist_ok=True)
        (aux/PLL_FILE).write_text(candidate(old,kind),encoding="utf-8")
        fp=master/TOP
        fp.write_text(exact(fp.read_text(),"../"+POWER.name+"/","../"+aux.name+"/"),encoding="utf-8")
        name="v719."+kind
        rr=OUT/(name+".erc.rpt")
        nn=OUT/(name+".net")
        for args in (["kicad-cli","sch","erc","-o",str(rr),str(fp)],
                     ["kicad-cli","sch","export","netlist","-o",str(nn),str(fp)]):
            p=subprocess.run(args,capture_output=True,text=True,timeout=90)
            if p.returncode: raise RuntimeError(name+" "+repr(args)+" "+(p.stderr+p.stdout)[-2000:])
        erc=native_erc(rr)
        nets=native_netlist(nn)
        names=lambda target: {name: [(ref,pin) for ref,pin in pins if ref in target]
             for name,pins in nets.items() if any(ref in target for ref,pin in pins)}
        pll_refs={"R2","R3","C1","C2","C3","U1"}
        return {
           "errors":erc["errors"],"warnings":erc["warnings"],
           "categories":erc["categories"],
           "net_count":len(nets),
           "net_memberships_R2_R3_C1_C2_C3_U1":names(pll_refs),
           "all_nets":nets
        }
def main():
    src=POWER/PLL_FILE
    original=src.read_bytes()
    trials=("as_is","r2_direct_pin","r2_direct_plus_r3_connected","r2_r3_grid_reanchor")
    outcome={}
    for name in trials:
        try:
            v=experiment(name)
            outcome[name]=v
            print(name,"real ERC",v["errors"],v["warnings"],"R2/R3 captured",
                  [(n,x) for n,x in v["net_memberships_R2_R3_C1_C2_C3_U1"].items()
                   if any(r in ("R2","R3") for r,p in x)],flush=True)
        except Exception as exc:
            outcome[name]={"failure":str(exc)}
            print(name,"EXPERIMENT FAILED",exc,flush=True)
    baseline=outcome["as_is"]
    report={"revision":"V7.19","source":"TI LMX2572 datasheet Fig179 p75 and TI EVM SNAU217B Fig19 p13",
            "source_pll_unchanged":src.read_bytes()==original,
            "native_ki9":True,"probes_not_approved_for_power_on_or_fab":True,
            "variants":{}}
    for name,entry in outcome.items():
        if "failure" in entry:
            report["variants"][name]=entry
            continue
        diff=[n for n in sorted(set(entry["all_nets"])|set(baseline["all_nets"]))
              if entry["all_nets"].get(n)!=baseline["all_nets"].get(n)]
        report["variants"][name]={k:v for k,v in entry.items() if k!="all_nets"}
        report["variants"][name]["changed_pin_net_names"]=diff
        report["variants"][name]["changed_pin_net_memberships"]={
            n:{"before":baseline["all_nets"].get(n),
               "candidate":entry["all_nets"].get(n)} for n in diff
        }
    (OUT/"v719.pll_pin_forensics.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    if not report["source_pll_unchanged"] or any("failure" in x for x in outcome.values()):
        raise SystemExit("FAIL CLOSED: KiCad experiment incomplete")
    if (baseline["errors"],baseline["warnings"],baseline["net_count"])!=(42,340,99):
        raise SystemExit("FAIL CLOSED: PLL baseline changed")
    print("PASS: native KiCad PLL diagnosis completed on disposable sibling clones only, no production circuit changed")
if __name__=="__main__": main()
