"""V7.64 real eFuse C200/D200 input grid CAD ECO + conservative SHDN state safety, NO FAB."""
from pathlib import Path
from collections import Counter
import re,json,sys,unittest

ROOT=Path(__file__).resolve().parents[2]
AUX0=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.63_CK_KMR223NG_ULC_4PAD_REVIEW_NOT_FOR_FAB"
AUX1=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.64_C200_D200_INPUT_GRID_REVIEW_NOT_FOR_FAB"
ROOT0=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.63_CK_KMR223NG_ULC_4PAD_REVIEW_NOT_FOR_FAB"
ROOT1=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.64_C200_D200_INPUT_GRID_REVIEW_NOT_FOR_FAB"
OUT=ROOT/"03_Verifiche/V7.64/output-ci"
MASTER="S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
CASES=(
    ("C200","S3900E:C_EFUSE",83,94,83.82,93.98),
    ("D200","S3900E:D",104,94,104.14,93.98),
)
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def source_check():
    old=(AUX0/"01_EFUSE_AUX.kicad_sch").read_text(encoding="utf8")
    expected=old
    actual=(AUX1/"01_EFUSE_AUX.kicad_sch").read_text(encoding="utf8")
    for ref,lib,x,y,nx,ny in CASES:
        assert all(abs(v/2.54-round(v/2.54))<1e-7 for v in (nx,ny)),ref
        at=f'(symbol (lib_id "{lib}") (at {x} {y} 90)'
        start=expected.index(at)
        end=expected.index("\n(symbol (lib_id",start+len(at))
        part=expected[start:end]
        assert f'(property "Reference" "{ref}"' in part
        delim=part.index("\n (instances (project")
        hdr,tail=part[:delim],part[delim:]
        hdr=hdr.replace(f'(at {x} {y} 90)',f'(at {nx:.4f} {ny:.4f} 90)',1)
        edits=[0]
        def edit(m):
            edits[0]+=1
            return f'(at {nx:.4f} {float(m[1])+ny-y:.4f} 0)'
        hdr=re.sub(r'\(at '+str(x)+r' ([\d.]+) 0\)',edit,hdr)
        assert edits==[3],(ref,edits)
        expected=expected[:start]+hdr+tail+expected[end:]
        lines=expected.splitlines()
        moved=0
        for i,line in enumerate(lines):
            if not (line.startswith("(label ") or line.startswith("(hierarchical_label ")):
                continue
            old_at=re.search(r'\(at '+str(x)+r' (88\.92|99\.08) 0\)',line)
            if old_at:
                yy=float(old_at[1])
                lines[i]=line.replace(old_at[0],f'(at {nx:.4f} {yy+ny-y:.4f} 0)',1)
                moved+=1
        assert moved==2,(ref,moved)
        expected="\n".join(lines)
        for dx in (0,):
            for dy in (-5.08,5.08):
                assert abs((nx+dx)/2.54-round((nx+dx)/2.54))<1e-7
                assert abs((ny+dy)/2.54-round((ny+dy)/2.54))<1e-7
    assert expected==actual,"Unreviewed changes to AUX eFuse schematic"
    # D200 remains DNP and not an approved installed transient protection.
    assert '(property "Value" "SMBJ18CA 18V CANDIDATA / DNP"' in actual
    assert '(symbol (lib_id "S3900E:D") (at 104.1400 93.9800 90) (unit 1) (in_bom no) (on_board yes) (dnp yes)' in actual
    for fn in ("02_BUCK_5V.kicad_sch","03_PLL_LDO_TCXO.kicad_sch","S3900E_AUX_POWER_V1_5.kicad_sch"):
        assert (AUX0/fn).read_bytes()==(AUX1/fn).read_bytes(),fn
    before=(ROOT0/MASTER).read_text(encoding="utf8")
    after=(ROOT1/MASTER).read_text(encoding="utf8")
    assert after==before.replace(
      "Gerarchico_Alimentazioni_V7.63_CK_KMR223NG_ULC_4PAD_REVIEW_NOT_FOR_FAB",
      "Gerarchico_Alimentazioni_V7.64_C200_D200_INPUT_GRID_REVIEW_NOT_FOR_FAB")
    for fn in ("sym-lib-table","fp-lib-table","S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_pro"):
        assert (ROOT0/fn).read_bytes()==(ROOT1/fn).read_bytes(),fn
    return True

def pins(path):
    mp={}
    for net,ps in nets(path).items():
        for p in ps:
            assert p not in mp,p
            mp[p]=net
    return mp

def normalized_findings(erc):
    result=Counter()
    targeted=[]
    for original in erc["findings"]:
        d=dict(original)
        loc=d.get("locations",[])
        if (d.get("category")=="endpoint_off_grid" and d.get("severity")=="warning"
            and len(loc)==1 and re.match(
                r'^@\([0-9.]+ mm, [0-9.]+ mm\): Symbol (C200|D200) Pin [12] \[.+\]$',loc[0])):
            m=re.search(r'Symbol (C200|D200)',loc[0])
            targeted.append(m[1])
        else:
            result[json.dumps(d,sort_keys=True,ensure_ascii=False)]+=1
    return result,targeted

def state_of_shdn(vpin,vin_present,fault_persists):
    """Conservative logical requirements, NOT a transistor model or time-domain simulation."""
    if not vin_present:
        return "UNPOWERED"
    if vpin < 0.76:
        return "DISABLED"
    if vpin < 1.0:
        return "UNDETERMINED"
    if fault_persists:
        return "FAULT_NOT_CLEARED"
    return "ENABLE_REQUEST_ONLY"

def gate():
    source_check()
    a=compmap(OUT/"v764.original.net")
    b=compmap(OUT/"v764.revised.net")
    assert a==b and len(b)==140
    pa=pins(OUT/"v764.original.net")
    pb=pins(OUT/"v764.revised.net")
    assert pa==pb and len(nets(OUT/"v764.original.net"))==len(nets(OUT/"v764.revised.net"))==103
    assert pb[("U200","7")]==pb[("SW200","1")]==pb[("SW200","4")]
    assert pb[("U200","9")]==pb[("SW200","2")]==pb[("SW200","3")]
    assert pb[("U200","8")]==pb[("U200","17")] and pb[("U200","8")]!=pb[("U200","9")]
    assert pb[("U200","6")]==pa[("U200","6")]
    e0=native_erc(OUT/"v764.original.erc.rpt")
    e1=native_erc(OUT/"v764.revised.erc.rpt")
    assert (e0["errors"],e0["warnings"])==(28,214)
    assert e1["errors"]==28
    oldtarget,oldgrid=normalized_findings(e0)
    newtarget,newgrid=normalized_findings(e1)
    if oldtarget!=newtarget:
        print("Non-target added",list((newtarget-oldtarget).elements())[:10])
        print("Non-target removed",list((oldtarget-newtarget).elements())[:10])
    assert oldtarget==newtarget,"Other preexisting ERC errors or warnings changed"
    assert not newgrid,("C200/D200 still offgrid",newgrid)
    assert sorted(set(oldgrid))==["C200","D200"],("No verified native offgrid targets",oldgrid)
    assert len(oldgrid)==2,("Unexpected old offgrid count",oldgrid)
    assert e1["warnings"]==212,(e0["warnings"],e1["warnings"])
    assert e0["categories"]["endpoint_off_grid"]-e1["categories"]["endpoint_off_grid"]==2
    assert state_of_shdn(0.4,True,False)=="DISABLED"
    assert state_of_shdn(0.75,True,False)=="DISABLED"
    assert state_of_shdn(0.8,True,False)=="UNDETERMINED"
    assert state_of_shdn(1.0,True,False)=="ENABLE_REQUEST_ONLY"
    assert state_of_shdn(1.2,True,True)=="FAULT_NOT_CLEARED"
    assert state_of_shdn(0.0,False,False)=="UNPOWERED"
    summary={"components":140,"nets":103,"offgrid_removed":2,
      "erc_before":{"errors":28,"warnings":214},"erc_after":{"errors":28,"warnings":212},
      "same_full_pin_net_map":True,"reset_vlow_V_max_exclusive":0.76,
      "reset_venable_V_min":1.0,"button_bounce_ms_max":3,
      "timing_of_actual_reset_qualified":False,"reset_with_persistent_fault_qualified":False,
      "esd_protection_qualified":False,"exposed_manual_reset_access_qualified":False,
      "d200_tvs_installed":False,"actual_5v_load_qualified":False,
      "no_fab":True,"no_tx":True}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v764.efuse_grid_and_shdn_state.json").write_text(json.dumps(summary,indent=2)+"\n")
    return summary

class TestV764EFuse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=gate()
    def test_01_components(self):self.assertEqual(self.r["components"],140)
    def test_02_nets(self):self.assertEqual(self.r["nets"],103)
    def test_03_map(self):self.assertTrue(self.r["same_full_pin_net_map"])
    def test_04_offgrid(self):self.assertEqual(self.r["offgrid_removed"],2)
    def test_05_erc_errors(self):self.assertEqual(self.r["erc_after"]["errors"],28)
    def test_06_erc_warnings(self):self.assertEqual(self.r["erc_after"]["warnings"],212)
    def test_07_disabled(self):self.assertEqual(state_of_shdn(.4,True,False),"DISABLED")
    def test_08_bounce_undefined(self):self.assertEqual(state_of_shdn(.9,True,False),"UNDETERMINED")
    def test_09_high_not_hardware_proven(self):self.assertEqual(state_of_shdn(1.,True,False),"ENABLE_REQUEST_ONLY")
    def test_10_persistent_fault(self):self.assertEqual(state_of_shdn(1.5,True,True),"FAULT_NOT_CLEARED")
    def test_11_unpowered(self):self.assertEqual(state_of_shdn(.4,False,False),"UNPOWERED")
    def test_12_esd_hold(self):self.assertFalse(self.r["esd_protection_qualified"])
    def test_13_mech_hold(self):self.assertFalse(self.r["exposed_manual_reset_access_qualified"])
    def test_14_tvs_dnp(self):self.assertFalse(self.r["d200_tvs_installed"])
    def test_15_load_hold(self):self.assertFalse(self.r["actual_5v_load_qualified"])
    def test_16_no_release(self):self.assertTrue(self.r["no_fab"] and self.r["no_tx"])

if __name__=="__main__":
    unittest.main()
