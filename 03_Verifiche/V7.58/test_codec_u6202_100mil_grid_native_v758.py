"""V7.58: real U6202 100mil KiCad grid correction, all nets conserved, NO FAB."""
from pathlib import Path
from collections import Counter
import json
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
OLD_MCU = ROOT / "04_KiCad/Modulo_MCU_CODEC_V7.48_TDK_2_C0G_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
NEW_MCU = ROOT / "04_KiCad/Modulo_MCU_CODEC_V7.58_U6202_100MIL_GRID_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
OLD_ROOT = ROOT / "04_KiCad/Assemblaggio_RX_Power_V7.57_TDK_CGA6_VENDOR_LAND_REVIEW_NOT_FOR_FAB"
NEW_ROOT = ROOT / "04_KiCad/Assemblaggio_RX_Power_V7.58_U6202_100MIL_GRID_REVIEW_NOT_FOR_FAB"
NAME = "S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
OUT = ROOT / "03_Verifiche/V7.58/output-ci"

sys.path.insert(0, str(ROOT / "03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0, str(ROOT / "03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0, str(ROOT / "03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def on_grid(mm):
    return abs(mm / 2.54 - round(mm / 2.54)) < 1e-7

def pin_map(path):
    found = {}
    for net, pins in nets(path).items():
        for pin in pins:
            assert pin not in found, ("duplicate pin", pin)
            found[pin] = net
    return found

def source_gate():
    old = OLD_MCU.read_text(encoding="utf8")
    new = NEW_MCU.read_text(encoding="utf8")
    ls = old.index('(symbol "S3900E:TLV320AIC3204_RHB32_DRAFT"')
    le = old.index('(symbol "S3900E:R_DRAFT"', ls)
    block = new[new.index('(symbol "S3900E:TLV320AIC3204_RHB32_DRAFT"'):new.index('(symbol "S3900E:R_DRAFT"')]
    pins = re.findall(r'\(pin [a-z_]+ line \(at (-?48\.2600) (-?\d+\.\d+) (0|180)\).*?\(number "(\d+)"', block)
    assert len(pins) == 33 and {int(p[3]) for p in pins} == set(range(1, 34)), pins
    for x, y, angle, num in pins:
        world_x = 401.32 + float(x)
        world_y = 160.02 - float(y)
        assert on_grid(world_x) and on_grid(world_y), ("pin off grid", num, world_x, world_y)
    assert '(symbol (lib_id "S3900E:TLV320AIC3204_RHB32_DRAFT") (at 401.3200 160.0200 0)' in new
    labels = re.findall(r'^\(label "[^"]+" \(at (353\.0600|449\.5800) (\d+\.\d+) 0\)', new, re.M)
    ncs = re.findall(r'^\(no_connect \(at (353\.0600|449\.5800) (\d+\.\d+)\)', new, re.M)
    assert len(labels) == 24 and len(ncs) == 9, (len(labels), len(ncs))
    for x, y in labels + ncs:
        assert on_grid(float(x)) and on_grid(float(y)), ("attachment off-grid", x, y)
    # No wires joined to codec pin locations in baseline; labels or NC only.
    assert "(xy 351.7400 " not in old and "(xy 448.2600 " not in old
    # No changes outside codec local lib block, one instance, 33 attached labels/NC.
    prefix_old = old[:ls]
    prefix_new = new[:new.index('(symbol "S3900E:TLV320AIC3204_RHB32_DRAFT"')]
    assert prefix_old == prefix_new
    assert old[le:old.index('(symbol (lib_id "S3900E:TLV320AIC3204_RHB32_DRAFT")')] == new[
        new.index('(symbol "S3900E:R_DRAFT"'):new.index('(symbol (lib_id "S3900E:TLV320AIC3204_RHB32_DRAFT")')]
    root0 = (OLD_ROOT / NAME).read_text(encoding="utf8")
    root1 = (NEW_ROOT / NAME).read_text(encoding="utf8")
    assert root1 == root0.replace("Modulo_MCU_CODEC_V7.48_TDK_2_C0G_REVIEW_NOT_FOR_FAB", "Modulo_MCU_CODEC_V7.58_U6202_100MIL_GRID_REVIEW_NOT_FOR_FAB")
    for fn in ("fp-lib-table", "S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_pro"):
        assert (OLD_ROOT / fn).read_bytes() == (NEW_ROOT / fn).read_bytes(), fn
    before_library=(OLD_ROOT/"sym-lib-table").read_text(encoding="utf8")
    after_library=(NEW_ROOT/"sym-lib-table").read_text(encoding="utf8")
    expect=before_library.replace("Librerie_Simboli_V7.26_UNIFIED_NOT_FOR_FAB",
        "Librerie_Simboli_V7.58_U6202_100MIL_GRID_HOLD")
    expect=expect.replace("V7.26 32 unique embedded S3900E definitions, MCU/AUX/RX, NO FAB/TX",
        "V7.58 U6202 pin grid correction; all other S3900E symbols preserved; NO FAB/TX")
    assert after_library==expect,"Unexpected project library routing changes"
    old_lib=(ROOT/"04_KiCad/Librerie_Simboli_V7.26_UNIFIED_NOT_FOR_FAB/S3900E.kicad_sym").read_text()
    new_lib=(ROOT/"04_KiCad/Librerie_Simboli_V7.58_U6202_100MIL_GRID_HOLD/S3900E.kicad_sym").read_text()
    assert len(new_lib)==len(old_lib)
    # Library only changes numeric pin Y coordinates for codec; avoid silently
    # changing pin numbers/types/names or any other unified symbols.
    pstart=old_lib.index('(symbol "TLV320AIC3204_RHB32_DRAFT"')
    pend=old_lib.index('\n  (symbol "',pstart+15)
    assert old_lib[:pstart]==new_lib[:pstart] and old_lib[pend:]==new_lib[pend:]
    extblock=new_lib[pstart:pend]
    extpins=re.findall(r'\(pin [a-z_]+ line \(at (-?48\.2600) (-?\d+\.\d+) (0|180)\).*?\(number "(\d+)"',extblock)
    assert len(extpins)==33
    assert [(p[0],p[1],p[3]) for p in extpins]==[(p[0],p[1],p[3]) for p in pins]
    return len(pins)

def normalized_findings(result):
    # Native KiCad9 can attribute a pre-existing offgrid finding to one
    # of several pins on U6202. Exclude only that specific family from
    # the COMPARISON, while requiring the original and revised raw
    # warning counts to differ by exactly one.
    family = re.compile(r'^@\([0-9.]+ mm, [0-9.]+ mm\): Symbol U6202 Pin [0-9]+ \[.+\]')
    retained = []
    removed = []
    # The same 3 still-dangling codec labels retain severity, category
    # and logical identity but move with their pins. Only coordinate changes
    # for these exact pre-existing labels are normalized in the diff.
    moved={"MICBIAS","AUDIO_LINE_L","AUDIO_LINE_R"}
    label_re=re.compile(r"^@\([0-9.]+ mm, [0-9.]+ mm\): Label '([^']+)'$")
    for x in result["findings"]:
        if (x.get("category")=="endpoint_off_grid" and x.get("severity")=="warning"
            and x.get("sheet")=="/" and len(x.get("locations",[]))==1
            and family.fullmatch(x["locations"][0])):
            removed.append(x)
        else:
            d=dict(x)
            if (d.get("category")=="label_dangling" and d.get("severity")=="error"
                and d.get("sheet")=="/" and len(d.get("locations",[]))==1):
                m=label_re.fullmatch(d["locations"][0])
                if m and m.group(1) in moved:
                    d["locations"]=["Existing U6202 dangling label: "+m.group(1)]
            retained.append(json.dumps(d,sort_keys=True,ensure_ascii=False))
    return Counter(retained), removed

def gate():
    pin_count = source_gate()
    a = compmap(OUT / "v758.original.net")
    b = compmap(OUT / "v758.revised.net")
    assert len(a) == len(b) == 139
    assert a == b, "Component identity/value/footprint changed unexpectedly"
    assert sum(not x[0] for x in b.values()) == 0
    n0 = nets(OUT / "v758.original.net")
    n1 = nets(OUT / "v758.revised.net")
    assert len(n0) == len(n1) == 102
    m0 = pin_map(OUT / "v758.original.net")
    m1 = pin_map(OUT / "v758.revised.net")
    assert m0 == m1, "U6202 signal/NC pin-to-net topology changed"
    for k in range(1, 34):
        pin = ("U6202", str(k))
        if pin in m0:
            assert m0[pin] == m1[pin]
    assert m0[("U200","8")] == m0[("U200","17")] != m0[("U200","9")]
    assert ("U200","7") not in m0
    e0 = native_erc(OUT / "v758.original.erc.rpt")
    e1 = native_erc(OUT / "v758.revised.erc.rpt")
    assert e0["errors"] == e1["errors"] == 28
    before, u0 = normalized_findings(e0)
    after, u1 = normalized_findings(e1)
    assert before == after, ("New/dropped non-U6202 ERC finding", list((after-before).elements())[:10],list((before-after).elements())[:10])
    assert len(u0) == 1 and len(u1) == 0, ("U6202 off-grid still unresolved", u0, u1)
    assert e0["warnings"] == 222 and e1["warnings"] == 221, (e0["warnings"],e1["warnings"])
    assert e0["categories"]["endpoint_off_grid"] - e1["categories"]["endpoint_off_grid"] == 1
    status = dict(parts=139,nets=102,mcu_grid_pins=pin_count,
                  native_erc_before={"errors":28,"warnings":222},
                  native_erc_after={"errors":28,"warnings":221},
                  electrical_graph_unchanged=True,
                  u6202_100mil_geometry_corrected=True,
                  cross_module_interface_validated=False,
                  independent_efuse_reset_approved=False,
                  entire_pcb_approved=False,NO_FAB=True,NO_TX=True)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT / "v758.grid_ecoreview.json").write_text(json.dumps(status, indent=2)+"\n")
    return status

class TestV758CodecGrid(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=gate()
    def test_01_pins_33(self):self.assertEqual(self.r["mcu_grid_pins"],33)
    def test_02_net_parity(self):self.assertTrue(self.r["electrical_graph_unchanged"])
    def test_03_parts(self):self.assertEqual(self.r["parts"],139)
    def test_04_nets(self):self.assertEqual(self.r["nets"],102)
    def test_05_erc_errors(self):self.assertEqual(self.r["native_erc_after"]["errors"],28)
    def test_06_erc_warning_delta(self):self.assertEqual(self.r["native_erc_before"]["warnings"]-self.r["native_erc_after"]["warnings"],1)
    def test_07_codec_grid(self):self.assertTrue(self.r["u6202_100mil_geometry_corrected"])
    def test_08_15_interface_hold(self):self.assertFalse(self.r["cross_module_interface_validated"])
    def test_09_efuse_hold(self):self.assertFalse(self.r["independent_efuse_reset_approved"])
    def test_10_board_hold(self):self.assertFalse(self.r["entire_pcb_approved"])
    def test_11_safety(self):self.assertTrue(self.r["NO_FAB"] and self.r["NO_TX"])

if __name__ == "__main__":
    unittest.main()
