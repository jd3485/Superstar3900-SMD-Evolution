#!/usr/bin/env python3
"""Cost policy check only. Never replaces KiCad ERC/DRC, netlist or simulation gates."""
from pathlib import Path
from collections import defaultdict
import sys
import yaml
ROOT=Path(__file__).resolve().parents[2]
WF=ROOT/".github"/"workflows"
CANCEL_PR="$"+"{{ github.event_name == 'pull_request' }}"
EXCLUDE="!03_Verifiche/**/*.md"
# These historic V7.22 libraries intentionally have complementary checks:
# complete codec EP33 net/ERC and native pcbnew footprint loading, respectively.
# Changing the underlying library requires BOTH; do not silently drop either.
ALLOWED_SHARED_TRIGGERS = {
    frozenset({"v722_codec_ep33_native.yml", "v723_kicad9_footprint_native.yml"})
}
MANDATORY_MANUAL_ONLY = {
    "kicad_native_v54.yml", "kicad_native_v55.yml",
    "kicad_native_v56.yml", "kicad_native_v57.yml",
    "v712_rx_schematic_native_probe.yml",
}
def audit():
    files=sorted(WF.glob("*.yml"))
    errors=[]
    if len(files)<35:errors.append(f"Expected >=35 workflows, got {len(files)}")
    missing_manual=MANDATORY_MANUAL_ONLY-{p.name for p in files}
    if missing_manual:errors.append(f"Mandatory safety or diagnostics workflows missing: {sorted(missing_manual)}")
    trigger_owners=defaultdict(set)
    stats={"workflows":len(files),"pull_request":0,"manual_only":0,"job_count":0}
    for f in files:
        try:d=yaml.load(f.read_text(encoding="utf-8"),Loader=yaml.BaseLoader)
        except Exception as e:errors.append(f"{f.name}: invalid YAML {e}");continue
        if not isinstance(d,dict):errors.append(f"{f.name}: invalid mapping");continue
        on=d.get("on")
        if not isinstance(on,dict):errors.append(f"{f.name}: explicit on: mapping required");continue
        invalid=set(on)-{"pull_request","workflow_dispatch"}
        if invalid:errors.append(f"{f.name}: forbidden auto events {sorted(invalid)}")
        if "workflow_dispatch" not in on:errors.append(f"{f.name}: manual recovery missing")
        jobs=d.get("jobs")
        if not isinstance(jobs,dict) or not jobs:errors.append(f"{f.name}: no job definitions")
        else:stats["job_count"]+=len(jobs)
        if f.name in MANDATORY_MANUAL_ONLY and set(on)!={"workflow_dispatch"}:
            errors.append(f"{f.name}: must be manual-only to avoid duplicated CI or automatic legacy checks")
        if "pull_request" not in on:
            stats["manual_only"]+=1
            continue
        stats["pull_request"]+=1
        pr=on["pull_request"]
        paths=pr.get("paths") if isinstance(pr,dict) else None
        if not isinstance(paths,list) or not paths:
            errors.append(f"{f.name}: missing PR paths");continue
        if "04_KiCad/**" in paths or "**" in paths:
            errors.append(f"{f.name}: excessively broad paths")
        if ".github/workflows/"+f.name in paths:
            errors.append(f"{f.name}: duplicate self-trigger")
        for pat in paths:
            if pat.startswith("!") or pat.endswith(".md"):
                continue
            trigger_owners[pat].add(f.name)
        if any(p.startswith("03_Verifiche/") and p.endswith("/**") for p in paths):
            if paths[-1]!=EXCLUDE:
                errors.append(f"{f.name}: report markdown exclusion must be final")
        con=d.get("concurrency")
        if not isinstance(con,dict) or not con.get("group") or con.get("cancel-in-progress")!=CANCEL_PR:
            errors.append(f"{f.name}: cancel only superseded PR jobs, not manual checks")
        permissions=d.get("permissions")
        if not isinstance(permissions,dict) or permissions.get("contents")!="read":
            errors.append(f"{f.name}: needs least-privilege contents:read")
        if f.name=="verifica_v70.yml":
            must={"ci/verifica_manifest.py","MANIFEST_SHA256_V7.0.csv",
                  "03_Verifiche/V6.9/**","03_Verifiche/V7.0/**"}
            if not must.issubset(set(paths)):errors.append("V7.0 source/manifest gates missing")
    # An exact PR path claimed by two workflows launches two independent runners.
    # A known pair may be complementary (EP33 electrical safety + footprint model);
    # every NEW shared trigger needs a conscious review and explicit exception.
    shared={pat:sorted(owners) for pat,owners in trigger_owners.items()
            if len(owners)>1}
    for pat,owners in sorted(shared.items()):
        if len(owners)!=2 or frozenset(owners) not in ALLOWED_SHARED_TRIGGERS:
            errors.append(f"duplicate automatic PR trigger {pat}: {owners}")
    stats["shared_pr_paths_approved"]=len(shared)
    stats["duplicate_pr_paths_unapproved"]=sum(
        len(owners)!=2 or frozenset(owners) not in ALLOWED_SHARED_TRIGGERS
        for owners in shared.values())
    print(stats)
    for err in errors:print("FAIL "+err,file=sys.stderr)
    if errors:return 1
    print("PASS cost triggers; native technical verification is a separate mandatory step")
    return 0
if __name__=="__main__":sys.exit(audit())
