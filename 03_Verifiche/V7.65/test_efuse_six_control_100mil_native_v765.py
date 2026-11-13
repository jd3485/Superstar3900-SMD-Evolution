"""V7.65 6 real eFuse UVLO/OVP/ILIM/dVdT/MODE resistor/cap 100mil grid ECO, no waiver."""
from pathlib import Path
from collections import Counter
import sys,json,re,unittest

ROOT=Path(__file__).resolve().parents[2]
AUX0=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.64_C200_D200_INPUT_GRID_REVIEW_NOT_FOR_FAB"
AUX1=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.65_SIX_EFUSE_CONTROL_GRID_REVIEW_NOT_FOR_FAB"
ROOT0=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.64_C200_D200_INPUT_GRID_REVIEW_NOT_FOR_FAB"
ROOT1=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.65_SIX_EFUSE_CONTROL_GRID_REVIEW_NOT_FOR_FAB"
OUT=ROOT/"03_Verifiche/V7.65/output-ci"
MASTER="S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
# Ref, lib, old x/y, snapped x/y, component Value, footprint, terminal names.
TARGETS=[
 ("R200","R_EFUSE",50,183,50.80,182.88,"365k 1%","Resistor_SMD:R_0603_1608Metric","EFUSE_VIN","UVLO_NODE"),
 ("R201","R_EFUSE",78,183,78.74,182.88,"16k2 1%","Resistor_SMD:R_0603_1608Metric","UVLO_NODE","OVP_NODE"),
 ("R202","R_EFUSE",105,183,104.14,182.88,"30k1 1%","Resistor_SMD:R_0603_1608Metric","OVP_NODE","EFUSE_RTN"),
 ("R203","R_EFUSE",240,195,238.76,195.58,"8k2 1%","Resistor_SMD:R_0603_1608Metric","ILIM_NODE","EFUSE_RTN"),
 ("C201","C_EFUSE",272,195,271.78,195.58,"22nF 50V X7R","Capacitor_SMD:C_0603_1608Metric","DV_DT_NODE","EFUSE_RTN"),
 ("R204","R_EFUSE",333,195,332.74,195.58,"402k 1% MODE_LATCHOFF_CANDIDATE","Resistor_SMD:R_0603_1608Metric","EFUSE_MODE","EFUSE_RTN"),
]

sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def source_gate():
    expected=(AUX0/"01_EFUSE_AUX.kicad_sch").read_text(encoding="utf8")
    actual=(AUX1/"01_EFUSE_AUX.kicad_sch").read_text(encoding="utf8")
    atom_count=0
    for ref,lib,x,y,nx,ny,value,foot,left,right in TARGETS:
        # The six changes per instance are exact and individual:
        # symbol, 3 value/ref/footprint positions, two pin labels.
        pairs=[
          (f'(symbol (lib_id "S3900E:{lib}") (at {x} {y} 90)',
           f'(symbol (lib_id "S3900E:{lib}") (at {nx:.4f} {ny:.4f} 90)'),
          (f'(property "Reference" "{ref}" (at {x} {y-7} 0)',
           f'(property "Reference" "{ref}" (at {nx:.4f} {ny-7:.4f} 0)'),
          (f'(property "Value" "{value}" (at {x} {y-3.3:.1f} 0)',
           f'(property "Value" "{value}" (at {nx:.4f} {ny-3.3:.4f} 0)'),
          (f'(property "Footprint" "{foot}" (at {x} {y} 0)',
           f'(property "Footprint" "{foot}" (at {nx:.4f} {ny:.4f} 0)'),
          (f'(label "{left}" (at {x} {y-5.08:.2f} 0)',
           f'(label "{left}" (at {nx:.4f} {ny-5.08:.4f} 0)'),
          (f'(label "{right}" (at {x} {y+5.08:.2f} 0)',
           f'(label "{right}" (at {nx:.4f} {ny+5.08:.4f} 0)')
        ]
        assert len(pairs)==6
        assert all(abs(v/2.54-round(v/2.54))<1e-7
                   for v in (nx,ny,nx,ny-5.08,ny+5.08)),ref
        for before,after in pairs:
            assert expected.count(before)==1,("Missing/ambiguous old source",ref,before)
            assert actual.count(after)==1,("Missing/ambiguous new source",ref,after)
            expected=expected.replace(before,after,1)
            atom_count+=1
    assert atom_count==36
    assert expected==actual,"Changes beyond 6 symbol positions +18 properties +12 attached labels"
    for fn in ("02_BUCK_5V.kicad_sch","03_PLL_LDO_TCXO.kicad_sch","S3900E_AUX_POWER_V1_5.kicad_sch"):
        assert (AUX0/fn).read_bytes()==(AUX1/fn).read_bytes(),fn
    oldroot=(ROOT0/MASTER).read_text(encoding="utf8")
    newroot=(ROOT1/MASTER).read_text(encoding="utf8")
    assert newroot==oldroot.replace(
        "Gerarchico_Alimentazioni_V7.64_C200_D200_INPUT_GRID_REVIEW_NOT_FOR_FAB",
        "Gerarchico_Alimentazioni_V7.65_SIX_EFUSE_CONTROL_GRID_REVIEW_NOT_FOR_FAB")
    for fn in ("sym-lib-table","fp-lib-table","S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_pro"):
        assert (ROOT0/fn).read_bytes()==(ROOT1/fn).read_bytes(),fn
    return atom_count

def pinmap(path):
    result={}
    for net,ps in nets(path).items():
        for pin in ps:
            assert pin not in result,("duplicate pin",pin)
            result[pin]=net
    return result

def diff_erc(erc):
    other=Counter()
    offgrid=[]
    for orig in erc["findings"]:
        d=dict(orig)
        locations=d.get("locations",[])
        m=re.fullmatch(
           r'@\([0-9.]+ mm, [0-9.]+ mm\): Symbol (R200|R201|R202|R203|C201|R204) Pin [12] \[.+\]',
           locations[0]) if len(locations)==1 else None
        if m and d.get("category")=="endpoint_off_grid" and d.get("severity")=="warning":
            offgrid.append(m[1])
        else:
            other[json.dumps(d,sort_keys=True,ensure_ascii=False)]+=1
    return other,offgrid

def gate():
    edits=source_gate()
    before=compmap(OUT/"v765.original.net")
    after=compmap(OUT/"v765.revised.net")
    assert before==after and len(before)==140
    a=pinmap(OUT/"v765.original.net")
    b=pinmap(OUT/"v765.revised.net")
    assert a==b and len(nets(OUT/"v765.original.net"))==len(nets(OUT/"v765.revised.net"))==103
    assert b[("U200","7")]==b[("SW200","1")]==b[("SW200","4")]
    assert b[("U200","9")]==b[("SW200","2")]==b[("SW200","3")]
    assert b[("U200","8")]==b[("U200","17")] and b[("U200","8")]!=b[("U200","9")]
    assert b[("U200","6")]==b[("R204","1")] or b[("U200","6")]==b[("R204","2")]
    old=native_erc(OUT/"v765.original.erc.rpt")
    new=native_erc(OUT/"v765.revised.erc.rpt")
    assert (old["errors"],old["warnings"])==(28,212)
    assert new["errors"]==28
    x,removed=diff_erc(old);y,still=diff_erc(new)
    if x!=y:
        print("Unwanted ERC ADDED",list((y-x).elements())[:10])
        print("Unwanted ERC REMOVED",list((x-y).elements())[:10])
    assert x==y,"Non-target ERC finding changed"
    assert not still,("Still target off-grid",still)
    assert len(removed)==6 and set(removed)=={t[0] for t in TARGETS},removed
    assert new["warnings"]==206,(new["warnings"],new["errors"])
    assert old["categories"]["endpoint_off_grid"]-new["categories"]["endpoint_off_grid"]==6
    result=dict(components=140,nets=103,exact_source_atoms=edits,
       fixed_offgrid=6,full_pin_net_map_identical=True,
       erc_before={"errors":28,"warnings":212},erc_after={"errors":28,"warnings":206},
       MODE_latchoff_retained=True,RTN_GND_isolated=True,
       actual_current_limit_measured=False,UVLO_OVP_transient_qualified=False,
       SHDN_fault_reset_hardware_qualified=False,pcb_global_drc_qualified=False,
       NO_FAB=True,NO_TX=True)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v765.efuse_six_control_grid.json").write_text(json.dumps(result,indent=2)+"\n")
    return result

class TestV765SixControl(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=gate()
    def test_01_all_changes_scoped(self):self.assertEqual(self.r["exact_source_atoms"],36)
    def test_02_all_six(self):self.assertEqual(self.r["fixed_offgrid"],6)
    def test_03_parts(self):self.assertEqual(self.r["components"],140)
    def test_04_nets(self):self.assertEqual(self.r["nets"],103)
    def test_05_all_edges(self):self.assertTrue(self.r["full_pin_net_map_identical"])
    def test_06_erc_error(self):self.assertEqual(self.r["erc_after"]["errors"],28)
    def test_07_erc_warn(self):self.assertEqual(self.r["erc_after"]["warnings"],206)
    def test_08_mode_hold(self):self.assertTrue(self.r["MODE_latchoff_retained"])
    def test_09_rtn_hold(self):self.assertTrue(self.r["RTN_GND_isolated"])
    def test_10_current_hold(self):self.assertFalse(self.r["actual_current_limit_measured"])
    def test_11_uvlo_hold(self):self.assertFalse(self.r["UVLO_OVP_transient_qualified"])
    def test_12_shdn_hold(self):self.assertFalse(self.r["SHDN_fault_reset_hardware_qualified"])
    def test_13_board_hold(self):self.assertFalse(self.r["pcb_global_drc_qualified"])
    def test_14_no_fab(self):self.assertTrue(self.r["NO_FAB"] and self.r["NO_TX"])

if __name__=="__main__":
    unittest.main()
