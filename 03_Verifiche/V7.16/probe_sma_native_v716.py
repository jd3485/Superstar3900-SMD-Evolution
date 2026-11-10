"""V7.16: native KiCad diagnosis of 180-degree SMA library mismatch.

Each variant exists only in an isolated disposable full-project clone.
Never reinterpret a diagnostic reduction of lib_footprint_mismatch as
vendor authorization, stable RF layout, or successful copper routing.
"""
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"04_KiCad"/"Modulo_RX_Test_50ohm_V7.14_LIB_DIAGNOSTIC_NOT_FOR_FAB"
PCB=SRC/"S3900E_RX_LIB_V7_14_NOT_FOR_FAB.kicad_pcb"
OUT=ROOT/"03_Verifiche"/"V7.16"/"output-ci"
OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.11"))
from confronta_drc_rx_v711 import parse
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.15"))
from audit_rx_topologia_v715 import forms,footprint_refs,pad_signatures,LIB

TARGETS=("J9102","J9104")

def variant_board(original,experiment):
    if experiment=="as_saved":
        return original
    fps=footprint_refs(original)
    out=original
    for ref in TARGETS:
        f=fps[ref]
        pos="36" if ref=="J9102" else "65"
        if f"(at 122 {pos} 180)" not in f:
            raise ValueError("Missing target SMA 180deg footprint coordinate "+ref)
        if experiment=="orientation_0_diagnostic":
            edited=f.replace(f"(at 122 {pos} 180)",f"(at 122 {pos})",1)
        elif experiment=="reference_value_text_180_diagnostic":
            edited=f.replace('(property "Reference" "'+ref+'" (at 0 -6.100 0)',
                             '(property "Reference" "'+ref+'" (at 0 -6.100 180)',1)
            edited=edited.replace('(at 0 5.900 0)','(at 0 5.900 180)',1)
        elif experiment=="pad_rotation_180_diagnostic":
            edited=re.sub(
                r'(\(pad "2" smd custom \(at [-\d.]+ [-\d.]+)\)',
                r'\1 180)',f)
            if edited.count(" 180)")==f.count(" 180)"):
                raise ValueError("Pad rotation test did not change custom pad angles")
        else:
            raise ValueError("Unknown variant "+experiment)
        if edited==f:
            raise ValueError("Variant did not change target "+ref)
        out=out.replace(f,edited,1)
    if pad_signatures(LIB.read_text()) != pad_signatures(fps["J9101"]):
        raise ValueError("Unexpected original SMA library pad mismatch")
    if experiment=="reference_value_text_180_diagnostic":
        for ref in TARGETS:
            if pad_signatures(footprint_refs(out)[ref])!=pad_signatures(fps[ref]):
                raise ValueError("Text-only experiment altered pads")
    return out

def run_one(experiment,root,original):
    import pcbnew
    clone=root
    # Must be a direct sibling of the original KiCad project: fp-lib-table
    # uses historical relative paths resolved from the project directory.
    shutil.copytree(SRC,clone,dirs_exist_ok=True)
    path=clone/PCB.name
    modified=variant_board(original,experiment)
    path.write_text(modified,encoding="utf-8")
    board=pcbnew.LoadBoard(str(path))
    if board is None:
        raise RuntimeError("Native pcbnew did not load "+experiment)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    if not pcbnew.SaveBoard(str(path),board):
        raise RuntimeError("Cannot save temporary clone")
    drc=OUT/("v716."+experiment+".native.drc.rpt")
    proc=subprocess.run(["kicad-cli","pcb","drc","-o",str(drc),str(path)],
                        capture_output=True,text=True)
    if proc.returncode not in (0,5):
        raise RuntimeError("Native KiCad DRC failed: "+proc.stderr[-1200:])
    report=parse(drc)
    return {"experiment":experiment,"native_drc":report,
            "notes":"Temporary geometry manipulation is a CAUSAL PROBE only; never a PCB correction"}

def main():
    import pcbnew
    raw=PCB.read_bytes()
    checksum=hashlib.sha256(raw).hexdigest()
    original=raw.decode("utf-8")
    result={"revision":"V7.16","pcbnew":pcbnew.Version(),
            "source_pcb_sha256":checksum, "source_pcb_unchanged":None,
            "source_pad_geometry_preserved":True,
            "vendor_2d_3d_CAD_imported":False,
            "experiments":{}, "no_fab":True,"no_tx":True}
    for experiment in ("as_saved","reference_value_text_180_diagnostic",
                       "orientation_0_diagnostic","pad_rotation_180_diagnostic"):
        try:
            with tempfile.TemporaryDirectory(prefix="v716_sma_"+experiment+"_",dir=SRC.parent) as td:
                data=run_one(experiment,Path(td),original)
            result["experiments"][experiment]=data
            print(experiment,json.dumps(data["native_drc"]))
        except Exception as e:
            result["experiments"][experiment]={"status":"FAILED","reason":repr(e)}
            print(experiment,"FAILED",repr(e))
    result["source_pcb_unchanged"]=hashlib.sha256(PCB.read_bytes()).hexdigest()==checksum
    (OUT/"v716.sma_native_forensics.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    baseline=result["experiments"]["as_saved"].get("native_drc")
    if not result["source_pcb_unchanged"]:
        raise SystemExit("Original PCB changed")
    if not baseline or baseline["drc_violations"]!=2 or baseline["unconnected_items"]!=0:
        raise SystemExit("Native V7.15 filled-board baseline regression")
    if baseline["categories"].get("lib_footprint_mismatch",0)!=2:
        raise SystemExit("Expected exactly two SMA mismatches")
    if any(a.get("status")=="FAILED" for a in result["experiments"].values()):
        raise SystemExit("One or more causal native KiCad experiments FAILED")
    print("PASS: native original and three cloned SMA geometry experiments; NO FAB/TX")

if __name__=="__main__":main()
