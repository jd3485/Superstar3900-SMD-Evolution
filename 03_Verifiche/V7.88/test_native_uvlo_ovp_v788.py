"""V7.88: enforce real two-net eFuse UVLO and OVP local PCB routing.

Derived from committed V7.87 master; only R200/R201 positions change.
Native schematic pad/net names and all preexisting 24 F.Cu tracks stay fixed.
Route ONLY U200.3 ↔ R200.1 (UVLO_NODE) and U200.5 ↔ R201.1
(OVP_NODE) on F.Cu 0.20 mm, no via. Divider lower branches,
EFUSE_RTN/GND_MAIN/GND_RF, VIN/OUT and all RF remain OPEN.
No fabrication, battery/vehicle supply, or TX authorized.
"""
from pathlib import Path
import json,math,unittest
import pcbnew

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"04_KiCad/PCB_MASTER_V7.87_EFUSE_CONTROL_WIP/S3900E_MASTER_V787_EFUSE_CONTROL_NO_FAB.kicad_pcb"
TARGET=ROOT/"04_KiCad/PCB_MASTER_V7.88_EFUSE_THRESHOLDS_WIP/S3900E_MASTER_V788_UVLO_OVP_NO_FAB.kicad_pcb"
EVID=ROOT/"03_Verifiche/V7.88/output-ci/v788_uvlo_ovp_native.json"
MOVE={"R200":(55,39),"R201":(56,52)}
ROUTES={
 "UVLO_NODE":[((66.1,44.025),(53,44.025)),((53,44.025),(53,39)),((53,39),(54.175,39))],
 "OVP_NODE":[((66.1,45.325),(52.5,45.325)),((52.5,45.325),(52.5,52)),((52.5,52),(55.175,52))]
}
PINS={"UVLO_NODE":(("U200","3"),("R200","1")),
      "OVP_NODE":(("U200","5"),("R201","1"))}
def pt(coordinates):
    return pcbnew.VECTOR2I(pcbnew.FromMM(coordinates[0]),pcbnew.FromMM(coordinates[1]))
def close(a,b):
    return abs(a.x-b.x)<=pcbnew.FromMM(0.001) and abs(a.y-b.y)<=pcbnew.FromMM(0.001)
def padsig(fp):
    return sorted((p.GetNumber(),p.GetNetname(),
                   p.GetLayerSet().Contains(pcbnew.F_Cu),
                   p.GetLayerSet().Contains(pcbnew.B_Cu),
                   p.GetLayerSet().Contains(pcbnew.F_Paste))
                  for p in fp.Pads())
def track_sig(board):
    return sorted((t.GetNetname(),t.GetLayer(),t.GetWidth(),
                   t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y)
                  for t in board.GetTracks())
def pad(refs,ref,n):
    found=[p for p in refs[ref].Pads() if p.GetNumber()==n]
    assert len(found)==1,(ref,n,len(found))
    return found[0]
def check():
    before=pcbnew.LoadBoard(str(SOURCE))
    after=pcbnew.LoadBoard(str(TARGET))
    a={fp.GetReference():fp for fp in before.GetFootprints()}
    b={fp.GetReference():fp for fp in after.GetFootprints()}
    assert set(a)==set(b) and len(a)==139
    assert len(before.GetTracks())==24 and len(after.GetTracks())==30
    assert not before.Zones() and not after.Zones()
    assert not any(d.GetLayer()==pcbnew.Edge_Cuts for d in after.GetDrawings())
    for ref in a:
        assert padsig(a[ref])==padsig(b[ref]),ref
        assert a[ref].GetFPID().GetLibItemName()==b[ref].GetFPID().GetLibItemName(),ref
        if ref in MOVE:
            assert b[ref].GetPosition()==pt(MOVE[ref]),ref
            assert a[ref].GetPosition()!=b[ref].GetPosition(),ref
        else:
            assert a[ref].GetPosition()==b[ref].GetPosition(),ref
    prior=set(track_sig(before))
    observed=set(track_sig(after))
    assert prior<=observed and len(observed-prior)==6,"old copper or new count mismatch"
    results={}
    for net,sections in ROUTES.items():
        p,q=[pad(b,*spec) for spec in PINS[net]]
        assert p.GetNetname()==q.GetNetname() and p.GetNetname().endswith("/"+net),net
        assert close(p.GetPosition(),pt(sections[0][0])),("first pin",net)
        assert close(q.GetPosition(),pt(sections[-1][1])),("last pin",net)
        assert len(sections)==3
        for i,(x,y) in enumerate(sections):
            assert x!=y and (i==0 or sections[i-1][1]==x)
            matching=[s for s in after.GetTracks() if s.GetNetname()==p.GetNetname()
             and s.GetLayer()==pcbnew.F_Cu and s.GetWidth()==pcbnew.FromMM(0.2)
             and ((close(s.GetStart(),pt(x)) and close(s.GetEnd(),pt(y)))
                 or (close(s.GetStart(),pt(y)) and close(s.GetEnd(),pt(x))))]
            assert len(matching)==1,(net,x,y,"missing/duplicate native track")
        results[net]={"from":PINS[net][0],"to":PINS[net][1],"segments":len(sections)}
    unused=[pad(b,"U200",n) for n in ("4","10","13","14")]
    assert all(p.GetNetCode()==0 for p in unused),"TI NC/FLT pins must stay isolated"
    for track in after.GetTracks():
        assert track.GetLayer()==pcbnew.F_Cu
        assert track.GetNetname().endswith(("/BUCK_BOOT","/BUCK_EN","/BUCK_FB",
            "/BUCK_DIV_TOP","/EFUSE_MODE","/ILIM_NODE","/UVLO_NODE","/OVP_NODE"))
    nets={p.GetNetname() for f in b.values() for p in f.Pads()}
    assert any(n.endswith("/EFUSE_RTN") for n in nets)
    assert any(n.endswith("/GND_MAIN") for n in nets)
    assert any(n.endswith("/GND_RF") for n in nets)
    out={"version":"V7.88","footprints":139,"old_segments":24,
         "new_segments":6,"total_segments":30,"relocated":MOVE,
         "confirmed_connections":results,"all_pad_nets_unchanged":True,
         "all_other_137_positions_unchanged":True,"existing_copper_unchanged":True,
         "no_new_return_copper":True,"no_power_current_copper":True,
         "no_via":True,"no_zone":True,"no_edge_cuts":True,
         "no_schematic_edit":True,"no_fab":True,"no_tx":True,"no_release":True}
    EVID.parent.mkdir(parents=True,exist_ok=True)
    EVID.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    return out
class TestV788(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.result=check()
    def test_nodes(self):self.assertEqual(set(self.result["confirmed_connections"]),{"UVLO_NODE","OVP_NODE"})
    def test_tracks(self):self.assertEqual(self.result["total_segments"],30)
    def test_netparity(self):self.assertTrue(self.result["all_pad_nets_unchanged"])
    def test_protection(self):self.assertTrue(self.result["no_new_return_copper"] and self.result["no_fab"] and self.result["no_tx"])
if __name__=="__main__":
    unittest.main()
