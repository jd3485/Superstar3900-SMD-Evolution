"""Native KiCad RX standalone root-load diagnostic, NOT a library rewrite.

Experiment with copies in CI and report which S-expression classes trigger
KiCad CLI exit 3. Never use these reduced diagnostic variants for CAD release.
"""
import json
import re
import subprocess
import tempfile
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RX=ROOT/"04_KiCad"/"Modulo_RX_Test_50ohm_V7.12_SCHEMATIC_REPAIR_NOT_FOR_FAB"/"S3900E_RX_STANDALONE_V7_12_NOT_FOR_FAB.kicad_sch"
OUT=ROOT/"03_Verifiche"/"V7.12"/"output-ci"

def children(src):
    """Parse only balanced form boundaries, respecting escaped/quoted strings."""
    start=src.find("(")
    if start<0: raise ValueError("missing opening paren")
    depth=0
    quote=False
    esc=False
    child_start=None
    result=[]
    for i,ch in enumerate(src[start:],start):
        if esc:
            esc=False
        elif quote and ch=="\\":
            esc=True
        elif ch=='"':
            quote=not quote
        elif not quote and ch=="(":
            depth+=1
            if depth==2: child_start=i
        elif not quote and ch==")":
            if depth==2:
                part=src[child_start:i+1]
                m=re.match(r"\(\s*([A-Za-z_0-9]+)",part)
                result.append((m.group(1) if m else "",part))
                child_start=None
            depth-=1
    if depth or quote: raise ValueError("invalid parenthesis structure")
    return result

def run():
    source=RX.read_text(encoding="utf-8")
    nodes=children(source)
    count=Counter(k for k,v in nodes)
    original={k:[v for kind,v in nodes if kind==k] for k in count}
    print("RX FORM COUNTS",dict(count),flush=True)
    # Synthetic trial variants strictly for parsing diagnosis, not schematic design.
    mandatory=["version","generator","uuid","paper"]
    header=" ".join(sum((original.get(k,[]) for k in mandatory),[]))
    libs=original["lib_symbols"][0]
    placements=original.get("symbol",[])
    wires=original.get("wire",[])
    labels=original.get("label",[])
    text=original.get("text",[])
    footer='(sheet_instances (path "/" (page "1"))) (embedded_fonts no)'
    variants={
      "minimal": "(kicad_sch "+header+" (lib_symbols) "+footer+")",
      "libraries_only": "(kicad_sch "+header+" "+libs+" "+footer+")",
      "libraries_and_symbols": "(kicad_sch "+header+" "+libs+" "+" ".join(placements)+" "+footer+")",
      "without_text": "(kicad_sch "+header+" "+libs+" "+" ".join(placements+wires+labels)+" "+footer+")",
      "with_text": "(kicad_sch "+header+" "+libs+" "+" ".join(placements+wires+labels+text)+" "+footer+")",
      "original": source
    }
    OUT.mkdir(parents=True,exist_ok=True)
    report={}
    with tempfile.TemporaryDirectory(prefix="s3900_rx_parser_") as folder:
        dir=Path(folder)
        for name,value in variants.items():
            path=dir/(name+".kicad_sch")
            # synchronize project instance refs with diagnostic file basename
            value=value.replace("S3900E_RX_STANDALONE_V7_12_NOT_FOR_FAB",name)
            path.write_text(value,encoding="utf-8")
            result=subprocess.run(["kicad-cli","sch","export","netlist","-o",str(dir/(name+".net")),str(path)],
                                  text=True,capture_output=True,timeout=45)
            report[name]={"native_exit":result.returncode,
                          "native_stderr":result.stderr.strip(),
                          "actual_netlist_exported":(dir/(name+".net")).exists()}
            print("RX PARSER PROBE",name,report[name],flush=True)
    (OUT/"rx_standalone_parser_probe_v712.json").write_text(
      json.dumps({"source_root":"RX V7.12 experimental only","form_counts":dict(count),
                  "variants":report,"all_manufacturing_gates":False,"NO_FAB_NO_TX":True},indent=2)+"\n")
    # Always diagnostic; manual repair must be proved by native export+ERC.
if __name__=="__main__":
    run()
