"""V7.31 AUX connector J100/J101: native KiCad9 pin/net and ERC parity (NO FAB/TX)."""
import json,sys,unittest,difflib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
O_AUX=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.29_F200_LITTELFUSE_REVIEW_NOT_FOR_FAB"
N_AUX=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.31_AUX_CONNECTORS_ON_GRID_NOT_FOR_FAB"
O_ROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.29_F200_LITTELFUSE_REVIEW_NOT_FOR_FAB"
N_ROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.31_AUX_CONNECTORS_ON_GRID_NOT_FOR_FAB"
OUT=ROOT/"03_Verifiche/V7.31/output-ci"
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc
GRID=1.27
def on_grid(v):return abs(v/GRID-round(v/GRID))<1e-7
def audit():
    old=(O_AUX/"S3900E_AUX_POWER_V1_5.kicad_sch").read_text()
    new=(N_AUX/"S3900E_AUX_POWER_V1_5.kicad_sch").read_text()
    old_lines=old.splitlines();new_lines=new.splitlines()
    diff=list(difflib.ndiff(old_lines,new_lines))
    removed=[line[2:] for line in diff if line.startswith("- ")]
    added=[line[2:] for line in diff if line.startswith("+ ")]
    assert len(removed)==len(added)==16,(len(removed),len(added))
    assert all('(at ' in a and a.lstrip().startswith(('(symbol ','(property ','(label ')) for a in added)
    coordinates=[(33.02,35.56),(90.17,35.56),(27.94,33.02),(27.94,38.10)]
    coordinates.extend((85.09,y) for y in (29.21,31.75,34.29,36.83,39.37,41.91))
    assert len(coordinates)==10 and all(on_grid(x) and on_grid(y) for x,y in coordinates)
    for file in ("01_EFUSE_AUX.kicad_sch","02_BUCK_5V.kicad_sch","03_PLL_LDO_TCXO.kicad_sch"):
        assert (O_AUX/file).read_bytes()==(N_AUX/file).read_bytes()
    for f in ("sym-lib-table","fp-lib-table"):
        assert (O_ROOT/f).read_bytes()==(N_ROOT/f).read_bytes()
    a=OUT/"v731.original.net";b=OUT/"v731.revised.net"
    assert a.is_file() and b.is_file(),"Native KiCad9 netlists are mandatory"
    original=nets(a);revised=nets(b)
    assert len(original)==100 and original==revised,"Pin-to-net delta would violate HOLD"
    c0=compmap(a);c1=compmap(b)
    assert len(c0)==132 and c0==c1 and sum(not x[0] for x in c1.values())==42
    ec0=native_erc(OUT/"v731.original.erc.rpt")
    ec1=native_erc(OUT/"v731.revised.erc.rpt")
    assert (ec0["errors"],ec0["warnings"])==(36,220),ec0
    assert (ec1["errors"],ec1["warnings"])==(36,218),ec1
    rep0=(OUT/"v731.original.erc.rpt").read_text()
    rep1=(OUT/"v731.revised.erc.rpt").read_text()
    assert (rep0.count("[endpoint_off_grid]"),rep1.count("[endpoint_off_grid]"))==(219,217)
    for rule in ("label_dangling","power_pin_not_driven","pin_not_driven","footprint_link_issues","lib_symbol_issues"):
        assert rep0.count("["+rule+"]")==rep1.count("["+rule+"]"),rule
    result={"revision":"V7.31","real_native_KiCad":True,"modified_source_lines":16,
            "connectors":["J100","J101"],"grid_mm":1.27,"pin_positions_checked":coordinates,
            "components":132,"nets":100,"net_node_delta":0,"missing_footprints":42,
            "erc_before":[36,220],"erc_after":[36,218],"offgrid_before":219,"offgrid_after":217,
            "15_crossdomain_OPEN_HOLD":True,"SG48_HOLD":True,"NO_FAB":True,"NO_TX":True,
            "complete_PCB":False}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v731.native_grid.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    return result
class TestAuxConnectorGrid(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.d=audit()
    def test_01_two_connectors(self):self.assertEqual(self.d["connectors"],["J100","J101"])
    def test_02_only_16_location_changes(self):self.assertEqual(self.d["modified_source_lines"],16)
    def test_03_50mil_grid_coordinates(self):self.assertEqual(len(self.d["pin_positions_checked"]),10)
    def test_04_132_components(self):self.assertEqual(self.d["components"],132)
    def test_05_100_nets_and_no_node_changes(self):self.assertEqual((self.d["nets"],self.d["net_node_delta"]),(100,0))
    def test_06_missing_footprints_unchanged(self):self.assertEqual(self.d["missing_footprints"],42)
    def test_07_exact_two_offgrid_warnings_removed(self):self.assertEqual((self.d["offgrid_before"],self.d["offgrid_after"]),(219,217))
    def test_08_ERC_errors_not_hidden(self):self.assertEqual(self.d["erc_before"][0],self.d["erc_after"][0])
    def test_09_safety_crossdomain_hold(self):self.assertTrue(self.d["15_crossdomain_OPEN_HOLD"] and self.d["SG48_HOLD"])
    def test_10_no_fabrication_or_TX(self):self.assertTrue(self.d["NO_FAB"] and self.d["NO_TX"] and not self.d["complete_PCB"])
if __name__=="__main__":unittest.main()
