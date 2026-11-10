"""Optional genuine pcbnew zone fill on an ISOLATED temporary KiCad project clone.

Does not save the source board, creates NO production files, and compares real
KiCad DRC reports only if pcbnew is importable and the fill succeeds.
"""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "03_Verifiche" / "V7.15" / "output-ci"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "03_Verifiche" / "V7.11"))
from confronta_drc_rx_v711 import parse
from audit_rx_topologia_v715 import PCB, BASE, forms

def main():
    source_hash = hashlib.sha256(PCB.read_bytes()).hexdigest()
    report = {
        "revision": "V7.15", "method": "pcbnew Python ZONE_FILLER on temporary full KiCad project clone",
        "source_project_unchanged": None, "status": "NOT_RUN",
        "native_drc": None, "saved_filled_polygons_on_temporary_clone": None,
        "no_fabrication": True, "no_rf_tx": True
    }
    try:
        import pcbnew
    except ImportError as e:
        report["reason"] = "python pcbnew module not installed: " + str(e)
    else:
        try:
            with tempfile.TemporaryDirectory(prefix="v715_zone_probe_", dir=BASE.parent) as name:
                clone = Path(name)
                shutil.copytree(BASE, clone, dirs_exist_ok=True)
                temporary_pcb = clone / PCB.name
                board = pcbnew.LoadBoard(str(temporary_pcb))
                if board is None:
                    raise RuntimeError("pcbnew did not load clone")
                filler = pcbnew.ZONE_FILLER(board)
                filler.Fill(board.Zones())
                if not pcbnew.SaveBoard(str(temporary_pcb), board):
                    raise RuntimeError("pcbnew SaveBoard(clone) returned false")
                report["saved_filled_polygons_on_temporary_clone"] = len(forms(
                    temporary_pcb.read_text(encoding="utf-8"), "filled_polygon"))
                drc = OUT / "v715.rx.pcbnew_filled_cloned.drc.rpt"
                p = subprocess.run(
                    ["kicad-cli", "pcb", "drc", "-o", str(drc), str(temporary_pcb)],
                    capture_output=True, text=True, check=False
                )
                report["kicad_cli_exit_code"] = p.returncode
                if p.returncode not in (0,5):
                    raise RuntimeError("native DRC command failed: " + p.stderr[-1000:])
                report["native_drc"] = parse(drc)
                report["status"] = "EXECUTED"
                report["note"] = ("This is a real filled temporary clone; new DRC categories "
                                  "do not authorize PCB fabrication or justify blind routing.")
        except Exception as e:
            report["status"] = "FAILED"
            report["reason"] = repr(e)
    report["source_project_unchanged"] = (
        hashlib.sha256(PCB.read_bytes()).hexdigest() == source_hash)
    (OUT / "v715.pcbnew_temporary_clone_probe.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["source_project_unchanged"]:
        raise SystemExit("BLOCKED: original PCB bytes changed")
    if report["status"] == "FAILED":
        raise SystemExit("pcbnew refill attempted but failed: inspect this real error")
    print("Recorded " + report["status"] + " zone-fill probe; always NO FAB / NO TX")

if __name__ == "__main__":
    main()
