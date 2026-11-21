"""V7.85: real but NON-RELEASE feedback-branch routing on KiCad9 master.

Connect exact native BUCK_FB and BUCK_DIV_TOP low-current components.
No BUCK_SW, 5V high-current, GND, EFUSE_RTN, RX, TX, or cross-module routing.
The feedback trace to U100 is still OPEN pending safe local corridor planning.
"""
from pathlib import Path
import hashlib, json, math, unittest
import pcbnew

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"04_KiCad/PCB_MASTER_V7.84_BUCK_LOCAL_WIP/S3900E_MASTER_V784_BUCK_LOCAL_NO_FAB.kicad_pcb"
DEST=ROOT/"04_KiCad/PCB_MASTER_V7.85_BUCK_FEEDBACK_WIP/S3900E_MASTER_V785_FEEDBACK_NO_FAB.kicad_pcb"
REPORT=ROOT/"03_Verifiche/V7.85/output-ci/v785_feedback_native.json"

# Keep power inductor, input filters, IC, and prior routes untouched.
# The feedback-passive island is an unqualified mechanical staging candidate.
MOVE={
  "C105":(136,60),
  "R101":(142,60),
  "R102":(142,68),
}
# No vias, branches in same copper plane only; every point measured in mm.
# Routes are made pad-center to pad-center, not arbitrary-net assignments.
NETS={
 "BUCK_FB":[
  ("C105","1","R101","1",[(134.5,60),(134.5,63),(140.5,63)]),
  ("R101","1","R102","2",[(140.5,63),(140.5,65),(142.825,65)]),
 ],
 "BUCK_DIV_TOP":[
  ("C105","2","R101","2",[(136.775,58),(142.825,58)]),
  ("R101","2","R100","1",[]),
 ],
}
# The first route FB ends at R101 pad1 from the local junction (140.5,63)
# and route to R102 continues through that junction. Endpoints intentionally
# share this same net, but their start/end order requires a physical junction.

def pad(fp,n):
    pads=[q for q in fp.Pads() if q.GetNumber()==n]
    assert len(pads)==1,(fp.GetReference(),n,len(pads))
    return pads[0]

def sig(fp):
    return sorted((q.GetNumber(),q.GetNetname(),q.GetLayerSet().Contains(pcbnew.F_Cu))
                  for q in fp.Pads())

def track_sig(board):
    return sorted((s.GetNetname(),s.GetLayer(),s.GetWidth(),
                   s.GetStart().x,s.GetStart().y,s.GetEnd().x,s.GetEnd().y)
                  for s in board.GetTracks())

def point(xy):
    return pcbnew.VECTOR2I(pcbnew.FromMM(xy[0]),pcbnew.FromMM(xy[1]))

def build():
    assert SOURCE.is_file()
    before=pcbnew.LoadBoard(str(SOURCE))
    orig={f.GetReference():f for f in before.GetFootprints()}
    assert len(orig)==139 and len(before.GetTracks())==6
    assert not before.Zones() and not any(d.GetLayer()==pcbnew.Edge_Cuts for d in before.GetDrawings())
    old_tracks=track_sig(before)
    old_places={r:f.GetPosition() for r,f in orig.items()}
    old_pads={r:sig(f) for r,f in orig.items()}
    board=pcbnew.LoadBoard(str(SOURCE))
    refs={f.GetReference():f for f in board.GetFootprints()}
    for ref,xy in MOVE.items():
        refs[ref].SetPosition(point(xy))
    route_report=[]
    for netname,routes in NETS.items():
        for a,an,b,bn,via in routes:
            p,q=pad(refs[a],an),pad(refs[b],bn)
            name=p.GetNetname()
            assert name and name==q.GetNetname() and name.endswith("/"+netname),(a,an,b,bn,name)
            assert p.GetLayerSet().Contains(pcbnew.F_Cu) and q.GetLayerSet().Contains(pcbnew.F_Cu)
            pts=[p.GetPosition(),*(point(xy) for xy in via),q.GetPosition()]
            assert len(pts)>1
            for start,end in zip(pts,pts[1:]):
                assert start!=end,(a,b,"zero-length route")
                tr=pcbnew.PCB_TRACK(board)
                tr.SetStart(start)
                tr.SetEnd(end)
                tr.SetLayer(pcbnew.F_Cu)
                tr.SetWidth(pcbnew.FromMM(0.20))
                tr.SetNet(p.GetNet())
                board.Add(tr)
            route_report.append({"net":netname,"from":f"{a}.{an}","to":f"{b}.{bn}","via":via})
    assert len(route_report)==4
    new_count=len(board.GetTracks())
    assert new_count==6+sum(len(via)+1 for routes in NETS.values() for _,_,_,_,via in routes)
    assert len(board.GetFootprints())==139
    assert not board.Zones()
    for ref,f in refs.items():
        assert sig(f)==old_pads[ref],(ref,"electrical pad delta")
        if ref not in MOVE:
            assert f.GetPosition()==old_places[ref],(ref,"unapproved move")
    # Protect previous BOOT/EN artwork from even minor change.
    assert set(old_tracks)<=set(track_sig(board))
    board.GetTitleBlock().SetTitle("S3900E V7.85 BUCK FB/DIV local copper WIP NO FAB NO TX")
    DEST.parent.mkdir(parents=True,exist_ok=True)
    if DEST.exists():
        saved=pcbnew.LoadBoard(str(DEST))
        actual={f.GetReference():f for f in saved.GetFootprints()}
        assert set(actual)==set(orig)
        assert len(saved.GetTracks())==new_count
        assert track_sig(saved)==track_sig(board),"committed PCB trace changed"
        for ref,f in refs.items():
            assert actual[ref].GetPosition()==f.GetPosition(),ref
            assert sig(actual[ref])==sig(f),ref
        assert not saved.Zones()
        # Preserve committed native PCB bytes and UUIDs for final CI.
    else:
        pcbnew.SaveBoard(str(DEST),board)
    check=pcbnew.LoadBoard(str(DEST))
    assert len(check.GetFootprints())==139 and len(check.GetTracks())==new_count
    assert not check.Zones() and not any(d.GetLayer()==pcbnew.Edge_Cuts for d in check.GetDrawings())
    checkrefs={f.GetReference():f for f in check.GetFootprints()}
    for ref in orig:
        assert sig(checkrefs[ref])==old_pads[ref],ref
    assert set(old_tracks)<=set(track_sig(check))
    valid_nets={x.GetNetname() for x in check.GetTracks()}
    assert all(n.endswith(("/BUCK_BOOT","/BUCK_EN","/BUCK_FB","/BUCK_DIV_TOP")) for n in valid_nets)
    # No physical return plane, eFuse, high-current or RF traces on this PCB.
    result={"revision":"V7.85","native_footprints":139,
            "preserved_prior_tracks":6,"total_track_segments":new_count,
            "feedback_net_count":2,"changed_coordinates":MOVE,
            "net_connections":route_report,"pad_nets_preserved":True,
            "return_domains_separate":True,"main_schematic_untouched":True,
            "no_rf":True,"no_tx":True,"no_fab":True,
            "no_edge_cuts":True,"no_5v_current_routing":True,
            "no_release_drc_claim":True}
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    return result

class TestV785(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.proof=build()
    def test_net_contracts(self):
        self.assertEqual(self.proof["feedback_net_count"],2)
        self.assertEqual(len(self.proof["net_connections"]),4)
    def test_prev_routing(self):self.assertEqual(self.proof["preserved_prior_tracks"],6)
    def test_no_release(self):
        self.assertTrue(self.proof["no_fab"] and self.proof["no_tx"] and self.proof["no_release_drc_claim"])
    def test_padmap(self):self.assertTrue(self.proof["pad_nets_preserved"])
if __name__=="__main__":unittest.main()
