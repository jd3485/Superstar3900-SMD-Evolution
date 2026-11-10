"""V7.15 READ-ONLY source audit of RX KiCad copper and SMA pads.

This audit intentionally does not infer electrical contact from mere proximity,
does not refill zones, modify board data, qualify vendor CAD, or release FAB/TX.
Native KiCad DRC remains the authority for actual connected/unconnected items.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KICAD = ROOT / "04_KiCad"
BASE = KICAD / "Modulo_RX_Test_50ohm_V7.14_LIB_DIAGNOSTIC_NOT_FOR_FAB"
PCB = BASE / "S3900E_RX_LIB_V7_14_NOT_FOR_FAB.kicad_pcb"
LIB = (KICAD / "Modulo_RX_Test_50ohm_V5.2_PARITY_LINK_STUDY_NOT_FOR_FAB"
       / "S3900E_V38_Review.pretty" / "CONSMA002_SMD_SHAPED_REVIEW.kicad_mod")
SMA_REFS = ("J9101", "J9102", "J9103", "J9104")
VENDOR = {
    "manufacturer": "TE Connectivity / Linx",
    "manufacturer_part": "CONSMA002-SMD",
    "drawing": "C-CONSMA002-SMD-X-X, revision D, sheet 2 of 3",
    "product_url": "https://www.te.com/en/product-CONSMA002-SMD.html",
    "secondary_drawing_url": "https://docs.rs-online.com/a010/A700000010108374.pdf",
    "center_pad_diameter_mm": 2.05,
    "drawing_transverse_dimension_mm": 7.76,
    "mechanical_qualification": False,
    "cad_dxf_step_imported": False,
}

def forms(src, kind):
    """Extract complete balanced S-expressions; quoted parentheses are ignored."""
    pattern = re.compile(r"\(" + re.escape(kind) + r"(?=[\s)])")
    result = []
    pos = 0
    while (match := pattern.search(src, pos)) is not None:
        start = match.start()
        depth = 0
        quoted = False
        escaped = False
        for i in range(start, len(src)):
            c = src[i]
            if escaped:
                escaped = False
                continue
            if quoted and c == "\\":
                escaped = True
                continue
            if c == '"':
                quoted = not quoted
                continue
            if not quoted:
                if c == "(":
                    depth += 1
                elif c == ")":
                    depth -= 1
                    if depth == 0:
                        result.append(src[start:i + 1])
                        pos = i + 1
                        break
        else:
            raise ValueError("Unbalanced KiCad expression: " + kind)
    return result

def footprint_refs(src):
    out = {}
    for f in forms(src, "footprint"):
        m = re.search(r'\(property "Reference" "([^"]+)"', f)
        if m:
            if m.group(1) in out:
                raise ValueError("Duplicate PCB designator " + m.group(1))
            out[m.group(1)] = f
    return out

def signature(pad):
    """Structural pad signature, excluding net assignment and KiCad UUID."""
    pad = re.sub(r'\(net\s+\d+\s+"[^"]*"\)', "", pad)
    pad = re.sub(r'\(tstamp\s+"[^"]+"\)', "", pad)
    return re.sub(r"\s+", "", pad)

def pad_signatures(fp):
    return sorted(signature(p) for p in forms(fp, "pad"))

def read_board():
    return PCB.read_text(encoding="utf-8")

def audit():
    raw = PCB.read_bytes()
    pcb = raw.decode("utf-8")
    lib = LIB.read_text(encoding="utf-8")
    footprints = footprint_refs(pcb)
    expected = pad_signatures(lib)
    footprints_have_same_pads = {
        ref: pad_signatures(footprints[ref]) == expected for ref in SMA_REFS
    }
    vias = forms(pcb, "via")
    tracks = forms(pcb, "segment")
    zones = forms(pcb, "zone")
    zone_info = []
    for z in zones:
        m = re.search(r'\(zone\s+\(net\s+(\d+)\)\s+\(net_name\s+"([^"]+)"\)\s+\(layer\s+"([^"]+)"\)', z)
        if not m:
            raise ValueError("Unexpected zone format")
        zone_info.append({"net_id": int(m[1]), "net_name": m[2], "layer": m[3]})
    via_map = []
    for v in vias:
        m = re.search(r'\(via\s+\(at\s+([\d.]+)\s+([\d.]+)\)\s+\(size\s+([\d.]+)\)\s+\(drill\s+([\d.]+)\)', v)
        n = re.search(r'\(net\s+(\d+)\)', v)
        if not m or not n:
            raise ValueError("Unexpected via format")
        via_map.append({"x_mm": float(m[1]), "y_mm": float(m[2]),
                        "diameter_mm": float(m[3]), "drill_mm": float(m[4]),
                        "net_id": int(n[1])})
    nets = dict((int(i), name) for i, name in
                re.findall(r'^\s{2}\(net\s+(\d+)\s+"([^"]*)"\)', pcb, re.M))
    sma_pads = {}
    for ref in SMA_REFS:
        pads = forms(footprints[ref], "pad")
        number = [re.match(r'\(pad\s+"([^"]+)"', p)[1] for p in pads]
        m = re.search(r'\(pad\s+"1"\s+smd\s+circle\s+\(at\s+0(?:\.0+)?\s+0(?:\.0+)?\)\s+\(size\s+([\d.]+)\s+([\d.]+)\)', footprints[ref])
        sma_pads[ref] = {
            "count": len(pads),
            "numbers": number,
            "center_pad_diameter_mm": float(m[1]) if m and m[1] == m[2] else None,
            "raw_pad_shapes_same_as_archived_library": footprints_have_same_pads[ref],
        }
    result = {
        "revision": "V7.15",
        "scope": "read-only KiCad RX source inventory + archived footprint signature comparison",
        "source_pcb": str(PCB.relative_to(ROOT)),
        "pcb_sha256": hashlib.sha256(raw).hexdigest(),
        "source_unchanged": True,
        "footprints_total": len(footprints),
        "sma": sma_pads,
        "vendor_reference": VENDOR,
        "via_count": len(via_map),
        "via_net_ids": sorted(set(v["net_id"] for v in via_map)),
        "via_coords": via_map,
        "segments_total": len(tracks),
        "zones": zone_info,
        "saved_filled_polygons": len(forms(pcb, "filled_polygon")),
        "net_names": nets,
        "native_baseline_v714": {
            "rx_drc_violations": 72,
            "via_dangling": 70,
            "sma_footprint_mismatch": ["J9102", "J9104"],
            "unconnected_items": 63,
            "root_erc_errors": 43,
            "root_erc_warnings": 340,
            "status": "previously verified; NOT remeasured by this static script"
        },
        "warning": ("Identical KiCad pad signatures do NOT resolve library mismatch, "
                    "mechanical tolerance, custom pad/rotation semantics, PCB routing, or vendor approval."),
        "read_only": True,
        "pcb_fabrication_permitted": False,
        "tx_permitted": False,
    }
    return result

def check(data):
    assert data["footprints_total"] == 15
    assert data["via_count"] == 70
    assert data["via_net_ids"] == [1]
    assert data["net_names"][1] == "GND_RF"
    assert data["segments_total"] == 44
    assert len(data["zones"]) == 4
    assert {z["layer"] for z in data["zones"]} == {"F.Cu", "B.Cu", "In1.Cu", "In2.Cu"}
    assert all(z["net_id"] == 1 for z in data["zones"])
    assert data["saved_filled_polygons"] == 0
    assert all(p["raw_pad_shapes_same_as_archived_library"] for p in data["sma"].values())
    assert all(p["center_pad_diameter_mm"] == 2.05 for p in data["sma"].values())
    assert not data["pcb_fabrication_permitted"] and not data["tx_permitted"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data = audit()
    check(data)
    payload = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(json.dumps({k: v for k, v in data.items() if k not in ("via_coords", "net_names")}, indent=2))
    print("PASS read-only V7.15 source inventory; not an ERC/DRC or vendor qualification")
