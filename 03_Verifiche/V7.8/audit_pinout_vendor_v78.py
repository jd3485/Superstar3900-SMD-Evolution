"""V7.8 fail-closed SG48 original-vendor workbook comparison tool.

The manufacturer spreadsheet (Lattice iCE40UP5K Pinout v1.1, document 51971)
could NOT be downloaded in this run. All reported comparisons to a synthetic
fixture are parser tests ONLY, never evidence of vendor pin certification.

When the original manufacturer XLSX is provided with independently verified
SHA-256 and human-inspected worksheet/column layout, invoke
audit_sheet_against_candidate(...). Without it, approval remains HOLD.
Uses Python standard library ZIP/XML only; does not rewrite the workbook.
"""
from pathlib import Path
import csv
import hashlib
import re
from zipfile import ZipFile, BadZipFile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
CANDIDATE=ROOT/"01_Specifiche"/"V7.6"/"SG48_PIN_PLAN_CANDIDATE_V7.6.csv"
OFFICIAL_URL="https://www.latticesemi.com/view_document?document_id=51971"
ORIGINAL_XLSX_ACQUIRED=False
VENDOR_BYTES_HASH_AUTHENTICATED=False
PHYSICAL_PINOUT_APPROVED=False
NS="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def vendor_status():
    return {"vendor_url":OFFICIAL_URL,
            "original_binary_acquired":ORIGINAL_XLSX_ACQUIRED,
            "vendor_hash_authenticated":VENDOR_BYTES_HASH_AUTHENTICATED,
            "pinout_approved_for_pcb":PHYSICAL_PINOUT_APPROVED,
            "qualification":"HOLD"}


def candidate_48():
    with CANDIDATE.open(encoding="utf-8",newline="") as f:
        rows=list(csv.DictReader(f))
    result={int(row["pin"]):row["source_signal"].strip() for row in rows
            if row["pin"].isdigit()}
    if set(result)!=set(range(1,49)):
        raise ValueError("candidate must have precisely pins 1-48")
    if any(row["assembly"]!="DNP" for row in rows):
        raise ValueError("pin plan is not DNP")
    return result


def _cells_from_sheet(raw, strings):
    tree=ET.fromstring(raw)
    rows=[]
    for row in tree.findall(f".//{NS}sheetData/{NS}row"):
        cells={}
        for cell in row.findall(f"{NS}c"):
            label=cell.attrib.get("r","")
            col=re.match(r"^[A-Z]+",label)
            if not col:
                continue
            typecode=cell.attrib.get("t","")
            v=cell.find(f"{NS}v")
            if typecode=="inlineStr":
                inline=cell.find(f"{NS}is")
                value="".join(t.text or "" for t in inline.iter(f"{NS}t")) if inline is not None else ""
            elif v is None:
                value=""
            elif typecode=="s":
                value=strings[int(v.text)]
            else:
                value=v.text or ""
            cells[col.group(0)]=str(value).strip()
        rows.append((int(row.attrib.get("r","0")),cells))
    return rows


def _shared_strings(archive):
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    tree=ET.fromstring(archive.read("xl/sharedStrings.xml"))
    return ["".join(n.text or "" for n in si.iter(f"{NS}t"))
            for si in tree.findall(f"{NS}si")]


def audit_sheet_against_candidate(vendor_xlsx, expected_sha256,
                                  *, worksheet_path, pin_column,
                                  signal_column, first_data_row):
    """Explicit column/sheet mapping required; no filename/URL trust fallback.

    Returns precise mismatch list and STILL qualifies only as HOLD; supplier
    authenticity, package variant and electrical mapping need human QA.
    """
    filepath=Path(vendor_xlsx)
    if not filepath.is_file():
        raise FileNotFoundError("official workbook not supplied")
    if not re.fullmatch("[a-f0-9]{64}",expected_sha256 or ""):
        raise ValueError("independently recorded vendor SHA-256 is mandatory")
    binary=filepath.read_bytes()
    actual=hashlib.sha256(binary).hexdigest()
    if actual!=expected_sha256:
        raise ValueError("vendor spreadsheet SHA-256 mismatch")
    if not re.fullmatch("xl/worksheets/sheet[0-9]+\\.xml",worksheet_path):
        raise ValueError("explicit XLSX sheet xml path required")
    for col in (pin_column,signal_column):
        if not re.fullmatch("[A-Z]{1,3}",col):
            raise ValueError("explicit Excel column required")
    if type(first_data_row) is not int or first_data_row < 1:
        raise ValueError("first_data_row invalid")
    try:
        with ZipFile(filepath) as workbook:
            if worksheet_path not in workbook.namelist():
                raise ValueError("selected vendor XLSX worksheet absent")
            strings=_shared_strings(workbook)
            rows=_cells_from_sheet(workbook.read(worksheet_path),strings)
    except BadZipFile as error:
        raise ValueError("not an OOXML workbook") from error
    parsed={}
    duplicate_pins=[]
    for row_idx,cells in rows:
        if row_idx<first_data_row:
            continue
        raw_pin=cells.get(pin_column,"").strip()
        if not raw_pin:
            continue
        try:
            pin=int(float(raw_pin))
        except ValueError:
            continue
        if not 1<=pin<=48:
            continue
        name=cells.get(signal_column,"").strip()
        if pin in parsed:
            duplicate_pins.append(pin)
        parsed[pin]=name
    expected=candidate_48()
    missing=sorted(set(expected)-set(parsed))
    mismatches=[{"pin":pin,"candidate":expected[pin],"vendor_sheet":parsed[pin]}
                for pin in sorted(set(expected)&set(parsed))
                if expected[pin].upper()!=parsed[pin].upper()]
    return {
        "vendor_file_sha256":actual,
        "parsed_pins":len(parsed),
        "missing_pins":missing,
        "duplicate_pins":sorted(set(duplicate_pins)),
        "mismatches":mismatches,
        "candidate_equal_to_selected_sheet":not(missing or mismatches or duplicate_pins),
        "sheet_layout_validated_by_manufacturer":False,
        "actual_original_xlsx_authenticated":False,
        "physical_pinout_approved":False,
        "qualification":"HOLD"
    }
