"""KiCad9 native SMA footprint forensics on *disposable* RX board clones.

No changes to archived source .kicad_pcb or to the historic .pretty library.
A replacement loaded from the archived library is DIAGNOSTIC ONLY until
independent vendor CAD, mechanical tolerances and RF return-path validation.
"""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SRC=(ROOT/"04_KiCad"/"Modulo_RX_Test_50ohm_V7.14_LIB_DIAGNOSTIC_NOT_FOR_FAB")
BOARD=SRC/"S3900E_RX_LIB_V7_14_NOT_FOR_FAB.kicad_pcb"
LIB=(ROOT/"04_KiCad"/"Modulo_RX_Test_50ohm_V5.2_PARITY_LINK_STUDY_NOT_FOR_FAB"
     /"S3900E_V38_Review.pretty")
OUT=ROOT/"03_Verifiche"/"V7.16"/"output-ci"
TARGETS=("J9102","J9104")
OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.11"))
from confronta_drc_rx_v711 import parse

def smm(v):
    import pcbnew
    return round(pcbnew.ToMM(v),6)

def pose(p):
    """World pad centres and shapes, not a complete electrical/mechanical validation."""
    try:
        position=p.GetPosition()
        ang=p.GetOrientationDegrees()
        size=p.GetSize()
        return {"number":p.GetNumber(), "x_mm":smm(position.x),
                "y_mm":smm(position.y), "width_mm":smm(size.x),
                "height_mm":smm(size.y), "orientation_degrees":round(float(ang),5),
                "shape_code":int(p.GetShape()),"net_name":p.GetNetname()}
    except Exception as e:
        raise RuntimeError("Failed to inspect native KiCad pad: "+str(e))

def fp_by_ref(board):
    return {f.GetReference():f for f in board.GetFootprints()}

def fill_and_drc(board,path,outname):
    import pcbnew
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    if not pcbnew.SaveBoard(str(path),board):
        raise RuntimeError("Cannot save temporary KiCad PCB")
    report=OUT/outname
    cp=subprocess.run(["kicad-cli","pcb","drc","-o",str(report),str(path)],
                      capture_output=True,text=True)
    if cp.returncode not in (0,5):
        raise RuntimeError("Native KiCad DRC failed: "+cp.stderr[-2000:])
    return parse(report)

def candidate_replace(board,old_ref):
    """Replace exact two SMA instances by native FootprintLoad on disposable clone."""
    import pcbnew
    old=fp_by_ref(board)[old_ref]
    old_pos=old.GetPosition()
    old_orient=old.GetOrientation()
    old_refname=old.GetReference()
    old_val=old.GetValue()
    old_pads=sorted([pose(p) for p in old.Pads()],key=lambda x:(x["number"],x["x_mm"],x["y_mm"]))
    nets={}
    for p in old.Pads():
        n=p.GetNumber()
        if n in nets and nets[n]!=p.GetNetCode():
            raise ValueError("Old pad number has conflicting net codes")
        nets[n]=p.GetNetCode()
    replacement=pcbnew.FootprintLoad(str(LIB),"CONSMA002_SMD_SHAPED_REVIEW")
    if replacement is None:
        raise RuntimeError("pcbnew.FootprintLoad not available")
    replacement.SetPosition(old_pos)
    replacement.SetOrientation(old_orient)
    replacement.SetReference(old_refname)
    replacement.SetValue(old_val)
    if hasattr(replacement,"SetFPID") and hasattr(old,"GetFPID"):
        replacement.SetFPID(old.GetFPID())
    if hasattr(replacement,"SetPath") and hasattr(old,"GetPath"):
        replacement.SetPath(old.GetPath())
    board.Remove(old)
    board.Add(replacement)
    for pad in replacement.Pads():
        key=pad.GetNumber()
        if key not in nets:
            raise ValueError("Unexpected pad in library "+key)
        pad.SetNetCode(nets[key])
    new_pads=sorted([pose(p) for p in replacement.Pads()],key=lambda x:(x["number"],x["x_mm"],x["y_mm"]))
    return {
        "reference":old_refname,
        "before":old_pads,
        "candidate":new_pads,
        "pad_centres_sizes_shapes_and_nets_equal": old_pads==new_pads,
        "schematic_path_restored_if_supported":hasattr(replacement,"SetPath")
    }

def main():
    import pcbnew
    sha=hashlib.sha256(BOARD.read_bytes()).hexdigest()
    result={
      "revision":"V7.16",
      "pcbnew_version":pcbnew.Version(),
      "scope":"native KiCad vendor-libray-versus-placed footprint diagnostic; source unchanged",
      "source_sha256":sha,
      "source_modified":False,
      "baseline":None,
      "library_reload_probe":None,
      "vendor_cad_verified":False,
      "physical_rf_qualified":False,
      "pcb_manufacturing_permitted":False,
      "tx_permitted":False
    }
    with tempfile.TemporaryDirectory(prefix="v716_sma_probe_",dir=SRC.parent) as td:
        base=Path(td)
        for label in ("baseline","library_reload"):
            copy=base/label
            shutil.copytree(SRC,copy,dirs_exist_ok=True)
            path=copy/BOARD.name
            brd=pcbnew.LoadBoard(str(path))
            if brd is None:
                raise RuntimeError("Cannot load "+str(path))
            if label=="baseline":
                result["baseline"]=fill_and_drc(brd,path,"v716.sma.before_clone.drc.rpt")
            else:
                rec=[candidate_replace(brd,x) for x in TARGETS]
                result["library_reload_probe"]={
                    "pad_comparisons":rec,
                    "native_drc":fill_and_drc(brd,path,"v716.sma.after_library_reload.drc.rpt"),
                    "all_pad_world_geometry_equal":all(z["pad_centres_sizes_shapes_and_nets_equal"] for z in rec)
                }
    result["source_modified"]=hashlib.sha256(BOARD.read_bytes()).hexdigest()!=sha
    (OUT/"v716.sma_native_forensics.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="library_reload_probe"},indent=2))
    print("RELOAD",json.dumps({
        "all_pad_world_geometry_equal":result["library_reload_probe"]["all_pad_world_geometry_equal"],
        "native_drc":result["library_reload_probe"]["native_drc"],
        "comparison": [{k:v for k,v in row.items() if k not in ("before","candidate")}
                       for row in result["library_reload_probe"]["pad_comparisons"]]
    },indent=2))
    if result["source_modified"]:
        raise SystemExit("BLOCKED: original PCB changed")
    if result["baseline"]["drc_violations"]!=2 or result["baseline"]["unconnected_items"]!=0:
        raise SystemExit("Baseline V7.15 native filled-clone DRC regression")
    if result["baseline"]["categories"].get("lib_footprint_mismatch",0)!=2:
        raise SystemExit("Expected exactly 2 original SMA mismatches")
    print("PASS: baseline and experimental footprint reload measured; NO FAB/NO TX")

if __name__=="__main__":main()
