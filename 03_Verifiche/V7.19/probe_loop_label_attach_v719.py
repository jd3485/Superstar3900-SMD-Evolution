"""V7.19 follow-up: test *direct pin labels* on disposable KiCad clones only.

A KiCad ERP count is never evidence of real PLL filter functional correctness;
native net membership must explicitly name U1/R2/R3/C1/C2/C3 terminals.
"""
import json,sys,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import probe_loop_endpoint_v719 as prior
ROOT=prior.ROOT
OUT=prior.OUT

def make_label(name,x,y):
    seed=uuid.uuid5(uuid.NAMESPACE_URL,"superstar3900-v719-label-"+name+str(x)+str(y))
    return '(label "'+name+'" (at '+str(x)+' '+str(y)+' 0) (effects (font (size 1.016 1.016)) (justify left bottom)) (uuid "'+str(seed)+'"))'

def edit(src,kind):
    if kind=="as_is":return src
    if kind not in ("label_two_resistors","label_complete_loop"):
        raise ValueError(kind)
    points=[
      ("PLL_CPOUT",84.92,157),
      ("PLL_CPOUT",134.92,146.05),
      ("PLL_VTUNE",145.08,146.05)
    ]
    if kind=="label_complete_loop":
        points += [
          ("PLL_R2_C2",95.08,157),
          ("PLL_R2_C2",113,158.92),
          ("PLL_VTUNE",174,158.92)
        ]
    marker=' (hierarchical_label "PLL_CE"'
    assert marker in src
    return src.replace(marker,"".join(make_label(*v)+"\n" for v in points)+marker,1)

def main():
    origin=prior.candidate
    prior.candidate=edit
    try:
        baseline=prior.experiment("as_is")
        res={}
        for name in ("label_two_resistors","label_complete_loop"):
            try:
                v=prior.experiment(name)
                changed={k:{"old":baseline["all_nets"].get(k),"new":v["all_nets"].get(k)}
                    for k in set(v["all_nets"])|set(baseline["all_nets"])
                    if v["all_nets"].get(k)!=baseline["all_nets"].get(k)}
                res[name]={
                    "errors":v["errors"],"warnings":v["warnings"],
                    "erc_categories":v["categories"],
                    "real_kicad_nets":len(v["all_nets"]),
                    "all_changed_net_pin_memberships":changed,
                    "actual_R2_pin_pairs":sorted((n,r,p) for n,pairs in v["all_nets"].items() for r,p in pairs if r=="R2"),
                    "actual_R3_pin_pairs":sorted((n,r,p) for n,pairs in v["all_nets"].items() for r,p in pairs if r=="R3")
                }
                print(name,"KiCad",v["errors"],v["warnings"],"R2",res[name]["actual_R2_pin_pairs"],"R3",res[name]["actual_R3_pin_pairs"],flush=True)
            except Exception as e:
                res[name]={"error":repr(e)}
                print(name,"DIAGNOSTIC ERROR",repr(e),flush=True)
        output={"version":"V7.19","status":"EPHEMERAL_PROBE_ONLY",
                "manufacturer_reference":"TI LMX2572 Fig179 external loop filter",
                "baseline_erc":[baseline["errors"],baseline["warnings"]],
                "results":res,"pcb_approved":False,"tx_permitted":False}
        (OUT/"v719.label_direct_native.json").write_text(json.dumps(output,indent=2)+"\n")
        if any("error" in v for v in res.values()):
            raise SystemExit("Native follow-up experiment failed")
        if (baseline["errors"],baseline["warnings"])!=(42,340):
            raise SystemExit("Unexpected KiCad baseline")
        print("PASS: direct-label trial evidence captured, NONE installed in versioned circuit")
    finally:prior.candidate=origin
if __name__=="__main__":main()
