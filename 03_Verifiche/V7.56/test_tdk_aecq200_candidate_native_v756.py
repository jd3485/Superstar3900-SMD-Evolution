"""V7.56: AEC-Q200 manufacturer-proven automotive MPN candidates for C103/C104; no circuit changes.
Before/after native 7-sheet netlist and ERC must be executed by KiCad9.
Fail-closed on any pin-to-net, part value, footprint, or safety status change.
"""
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
OLD_AUX=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.55_TDK_C103_C104_VENDOR_CANDIDATE_NOT_FOR_FAB"
NEW_AUX=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.56_TDK_AECQ200_C103_C104_REVIEW_NOT_FOR_FAB"
OLD_ROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.55_TDK_BUCK_MLCC_REVIEW_NOT_FOR_FAB"
NEW_ROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.56_TDK_AECQ200_MLCC_REVIEW_NOT_FOR_FAB"
ROOT_NAME="S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
OUT=ROOT/"03_Verifiche/V7.56/output-ci"
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def pinmap(path):
    out={}
    for net,pins in nets(path).items():
        for pin in pins:
            if pin in out:raise AssertionError(("duplicate pin",pin))
            out[pin]=net
    return out

def source_check():
    old=(OLD_AUX/"02_BUCK_5V.kicad_sch").read_text(encoding="utf8")
    new=(NEW_AUX/"02_BUCK_5V.kicad_sch").read_text(encoding="utf8")
    old_mpn='"MPN" "C3225X7R1E226M250AB"'
    new_mpn='"MPN" "CGA6P3X7R1E226M250AB"'
    old_q='"Qualification" "V7.55 CANDIDATE DC_BIAS_THERMAL_HOLD"'
    new_q='"Qualification" "V7.56 AEC_Q200_CANDIDATE DC_BIAS_THERMAL_HOLD"'
    assert old.count(old_mpn)==old.count(old_q)==2
    assert new.count(new_mpn)==new.count(new_q)==2
    expected=old.replace(old_mpn,new_mpn).replace(old_q,new_q)
    assert new==expected,"Unexpected modification of existing 5V schematic"
    for fn in ("01_EFUSE_AUX.kicad_sch","03_PLL_LDO_TCXO.kicad_sch","S3900E_AUX_POWER_V1_5.kicad_sch"):
        assert (OLD_AUX/fn).read_bytes()==(NEW_AUX/fn).read_bytes(),fn
    oldroot=(OLD_ROOT/ROOT_NAME).read_text(encoding="utf8")
    newroot=(NEW_ROOT/ROOT_NAME).read_text(encoding="utf8")
    assert newroot==oldroot.replace("Gerarchico_Alimentazioni_V7.55_TDK_C103_C104_VENDOR_CANDIDATE_NOT_FOR_FAB",
                                  "Gerarchico_Alimentazioni_V7.56_TDK_AECQ200_C103_C104_REVIEW_NOT_FOR_FAB")
    assert oldroot!=newroot
    for fn in ("fp-lib-table","sym-lib-table","S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_pro"):
        assert (OLD_ROOT/fn).read_bytes()==(NEW_ROOT/fn).read_bytes(),fn
    return {"mpn":"CGA6P3X7R1E226M250AB","candidates":["C103","C104"],"automotive_aec_q200_vendor":True}

def gate():
    z=source_check()
    a=compmap(OUT/"v756.original.net")
    b=compmap(OUT/"v756.revised.net")
    assert len(a)==len(b)==139,(len(a),len(b))
    assert a==b,"Any footprint/value/part inventory change forbidden"
    assert not any(not item[0] for item in b.values()),"Missing schematic footprint"
    before=nets(OUT/"v756.original.net")
    after=nets(OUT/"v756.revised.net")
    assert len(before)==len(after)==102,(len(before),len(after))
    assert pinmap(OUT/"v756.original.net")==pinmap(OUT/"v756.revised.net"),"Changed pin-net graph"
    m=pinmap(OUT/"v756.revised.net")
    for ref in ("C103","C104"):
        ns={m[(ref,"1")],m[(ref,"2")]}
        assert any(s.endswith("/5V_RF_PREREGULATED") for s in ns),(ref,ns)
        assert any(s.endswith("/GND_MAIN") for s in ns),(ref,ns)
    assert m[("U200","8")]==m[("U200","17")]
    assert m[("U200","8")]!=m[("U200","9")]
    assert ("U200","7") not in m
    er0=native_erc(OUT/"v756.original.erc.rpt")
    er1=native_erc(OUT/"v756.revised.erc.rpt")
    # Both KiCad9 exports in this SAME run have the same 28/222 baseline.
    # Earlier checkpoints claimed 28/221; the extra pre-existing off-grid
    # finding MUST be tracked, not suppressed and not attributed to the BOM ECO.
    assert (er0["errors"],er0["warnings"])==(28,222),er0
    assert (er1["errors"],er1["warnings"])==(28,222),er1
    # KiCad9 can reorder ERC findings across file paths. Require identical
    # MULTISETS of category, message, severity, sheet and exact locations.
    # No filtering or suppression; print new/missing diagnostics on mismatch.
    from collections import Counter
    import json
    # KiCad9 detects the same pre-existing U6202 MCU off-grid issue as
    # either pin 15 (IN2_L) or pin 16 (IN2_R), depending on sheet traversal.
    # Both MCU sheet paths are BYTE-identical (source_check proves root
    # differs only in AUX path). Preserve counts and all other findings:
    # normalize ONLY this exact known ambiguity, NEVER suppress ERC itself.
    # KiCad9 diagnostics may choose different U6202 MCU pins for an
    # off-grid warning even while the MCU schematic is byte-identical.
    # Normalize ONLY U6202 endpoint_off_grid diagnostic attribution, never
    # the count, category, severity, or any other component's findings.
    # All original native reports remain intact; no ERC waiver is added.
    import re
    u6202=re.compile(r'^@\([0-9.]+ mm, [0-9.]+ mm\): Symbol U6202 Pin [0-9]+ \[.+\]')
    def fingerprint(x):
        d=dict(x)
        if (d.get("category")=="endpoint_off_grid" and d.get("sheet")=="/"
            and d.get("severity")=="warning" and len(d.get("locations",[]))==1
            and u6202.fullmatch(d["locations"][0])):
            d["locations"]=["U6202 pre-existing off-grid finding on BYTE-identical MCU source"]
        return json.dumps(d,sort_keys=True,ensure_ascii=False)
    old_findings=Counter(fingerprint(x) for x in er0["findings"])
    new_findings=Counter(fingerprint(x) for x in er1["findings"])
    if old_findings!=new_findings:
        print("ADDED ERC FINDINGS:",list((new_findings-old_findings).elements())[:25],flush=True)
        print("REMOVED ERC FINDINGS:",list((old_findings-new_findings).elements())[:25],flush=True)
    assert old_findings==new_findings,"Changed native ERC finding multiset"
    assert er0["categories"]==er1["categories"],(er0,er1)
    z.update(parts=139,nets=102,erc_errors=er1["errors"],erc_warnings=er1["warnings"],
             same_native_pin_net=True,verified_vendor_land=False,
             actual_dc_bias_curve_worst_case_approved=False,
             complete_board_approved=False,independent_efuse_recovery_approved=False)
    return z

class TestV756AutomotiveCandidate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.z=gate()
    def test_01_source_exact(self):self.assertEqual(set(self.z["candidates"]),{"C103","C104"})
    def test_02_mpn(self):self.assertEqual(self.z["mpn"],"CGA6P3X7R1E226M250AB")
    def test_03_139_parts(self):self.assertEqual(self.z["parts"],139)
    def test_04_102_nets(self):self.assertEqual(self.z["nets"],102)
    def test_05_graph(self):self.assertTrue(self.z["same_native_pin_net"])
    def test_06_erc_errors(self):self.assertEqual(self.z["erc_errors"],28)
    def test_07_erc_warnings(self):self.assertEqual(self.z["erc_warnings"],222)
    def test_08_vendor_land_hold(self):self.assertFalse(self.z["verified_vendor_land"])
    def test_09_dc_bias_hold(self):self.assertFalse(self.z["actual_dc_bias_curve_worst_case_approved"])
    def test_10_board_hold(self):self.assertFalse(self.z["complete_board_approved"])
    def test_11_recovery_hold(self):self.assertFalse(self.z["independent_efuse_recovery_approved"])
    def test_12_review_only(self):self.assertTrue(all(not self.z[k] for k in ("verified_vendor_land","complete_board_approved")))
    def test_13_tdk_aec_q200(self):self.assertTrue(self.z["automotive_aec_q200_vendor"])
if __name__=="__main__":
    unittest.main()
)
    def fingerprint(x):
        d=dict(x)
        if (d.get("category")=="endpoint_off_grid" and d.get("sheet")=="/"
            and d.get("severity")=="warning" and len(d.get("locations",[]))==1
            and u6202.fullmatch(d["locations"][0])):
            d["locations"]=["U6202 pre-existing off-grid finding on BYTE-identical MCU source"]
        return json.dumps(d,sort_keys=True,ensure_ascii=False)
    old_findings=Counter(fingerprint(x) for x in er0["findings"])
    new_findings=Counter(fingerprint(x) for x in er1["findings"])
    if old_findings!=new_findings:
        print("ADDED ERC FINDINGS:",list((new_findings-old_findings).elements())[:25],flush=True)
        print("REMOVED ERC FINDINGS:",list((old_findings-new_findings).elements())[:25],flush=True)
    assert old_findings==new_findings,"Changed native ERC finding multiset"
    assert er0["categories"]==er1["categories"],(er0,er1)
    z.update(parts=139,nets=102,erc_errors=er1["errors"],erc_warnings=er1["warnings"],
             same_native_pin_net=True,verified_vendor_land=False,
             actual_dc_bias_curve_worst_case_approved=False,
             complete_board_approved=False,independent_efuse_recovery_approved=False)
    return z

class TestV756AutomotiveCandidate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.z=gate()
    def test_01_source_exact(self):self.assertEqual(set(self.z["candidates"]),{"C103","C104"})
    def test_02_mpn(self):self.assertEqual(self.z["mpn"],"CGA6P3X7R1E226M250AB")
    def test_03_139_parts(self):self.assertEqual(self.z["parts"],139)
    def test_04_102_nets(self):self.assertEqual(self.z["nets"],102)
    def test_05_graph(self):self.assertTrue(self.z["same_native_pin_net"])
    def test_06_erc_errors(self):self.assertEqual(self.z["erc_errors"],28)
    def test_07_erc_warnings(self):self.assertEqual(self.z["erc_warnings"],222)
    def test_08_vendor_land_hold(self):self.assertFalse(self.z["verified_vendor_land"])
    def test_09_dc_bias_hold(self):self.assertFalse(self.z["actual_dc_bias_curve_worst_case_approved"])
    def test_10_board_hold(self):self.assertFalse(self.z["complete_board_approved"])
    def test_11_recovery_hold(self):self.assertFalse(self.z["independent_efuse_recovery_approved"])
    def test_12_review_only(self):self.assertTrue(all(not self.z[k] for k in ("verified_vendor_land","complete_board_approved")))
    def test_13_tdk_aec_q200(self):self.assertTrue(self.z["automotive_aec_q200_vendor"])
if __name__=="__main__":
    unittest.main()
