"""V7.84 real PCB WIP: compact buck passive placement plus two verified
low-current local F.Cu nets (BOOT, EN). 13.8V/eFuse/current loops, RF,
GND return and safety remain UNROUTED / NO FAB / NO TX.
"""
from pathlib import Path
import json, math, unittest
import pcbnew

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"04_KiCad/PCB_MASTER_V7.83_RX_PLACEMENT_WIP/S3900E_MASTER_V783_STAGING_NO_FAB.kicad_pcb"
DEST=ROOT/"04_KiCad/PCB_MASTER_V7.84_BUCK_LOCAL_WIP/S3900E_MASTER_V784_BUCK_LOCAL_NO_FAB.kicad_pcb"
EVID=ROOT/"03_Verifiche/V7.84/output-ci/v784_buck_local_placement.json"

# Positions are mechanical/thermal REVIEW candidates, NOT a released stackup.
# Preserve all 124 PLL/MCU/power-base and 15 RX electrical pin-to-net mappings.
# Keep J100, F200, U200, U100 and other critical connectors fixed; only
# preliminary buck local passives are repositioned.
RELOCATE={
 "C100":(104,43), "C101":(104,49),
 "C102":(119,40),
 "L100":(131,45),
 "C103":(145,37), "C104":(145,53),
 "C105":(138,60),
 "R100":(148,60), "R101":(154,60), "R102":(160,60),
 "R103":(117,51), "R104":(111,56),
}
assert len(RELOCATE)==12
EXPECTED={
 ("U100","6"):"BUCK_BOOT",("C102","1"):"BUCK_BOOT",
 ("U100","5"):"BUCK_EN",("R103","1"):"BUCK_EN",
}
# Routes are provisional signals, no power feed, current return, ground pour,
# switching power trace, RF or eFuse recovery connected.
ROUTES=[
 ("U100","6","C102","1",[]),
 ("U100","5","R103","1",[(118,45),(118,51)]),
]
def pad_by_number(footprint,num):
    pads=[p for p in footprint.Pads() if p.GetNumber()==num]
    assert len(pads)==1,(footprint.GetReference(),num,len(pads))
    return pads[0]

def pad_signature(fp):
    return sorted((p.GetNumber(),p.GetNetname(),tuple(p.GetLayerSet().Contains(layer) for layer in (pcbnew.F_Cu,pcbnew.B_Cu,pcbnew.F_Paste,pcbnew.F_Mask))) for p in fp.Pads())

def vertices_from_route(refs,route):
    a,an,b,bn,via=route
    p1=pad_by_number(refs[a],an)
    p2=pad_by_number(refs[b],bn)
    net1,net2=p1.GetNetname(),p2.GetNetname()
    assert net1==net2
    expected=EXPECTED[(a,an)]
    assert net1.endswith("/"+expected),(a,an,net1)
    assert EXPECTED[(b,bn)]==expected
    assert p1.GetLayerSet().Contains(pcbnew.F_Cu)
    assert p2.GetLayerSet().Contains(pcbnew.F_Cu)
    pts=[p1.GetPosition()]
    pts += [pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y)) for x,y in via]
    pts += [p2.GetPosition()]
    for i in range(len(pts)-1):
        assert pts[i]!=pts[i+1]
    return pts,p1.GetNet()

def build():
    assert SOURCE.is_file()
    original=pcbnew.LoadBoard(str(SOURCE))
    before={f.GetReference():f for f in original.GetFootprints()}
    assert len(before)==139 and "Y1" not in before and "D200" not in before
    assert len(original.GetTracks())==0 and len(original.Zones())==0
    assert not any(d.GetLayer()==pcbnew.Edge_Cuts for d in original.GetDrawings())
    # Compare real electrically relevant footprint and pad connectivity
    # BEFORE placing/routing, never generate or alias new schematic nets.
    before_sig={ref:pad_signature(fp) for ref,fp in before.items()}
    original_pos={ref:fp.GetPosition() for ref,fp in before.items()}
    board=pcbnew.LoadBoard(str(SOURCE))
    refs={f.GetReference():f for f in board.GetFootprints()}
    for ref,(x,y) in RELOCATE.items():
        assert ref in refs
        refs[ref].SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y)))
    for route in ROUTES:
        pts,net=vertices_from_route(refs,route)
        for start,end in zip(pts,pts[1:]):
            t=pcbnew.PCB_TRACK(board)
            t.SetStart(start)
            t.SetEnd(end)
            t.SetLayer(pcbnew.F_Cu)
            t.SetWidth(pcbnew.FromMM(0.25))
            t.SetNet(net)
            board.Add(t)
    board.GetTitleBlock().SetTitle("S3900E V7.84 BUCK local BOOT EN routing WIP NO FAB")
    assert len(board.GetFootprints())==139
    assert len(board.GetTracks())==4 and len(board.Zones())==0
    for ref,fp in refs.items():
        assert pad_signature(fp)==before_sig[ref],ref
        if ref not in RELOCATE:
            assert fp.GetPosition()==original_pos[ref],ref
    DEST.parent.mkdir(parents=True,exist_ok=True)
    if DEST.exists():
        saved=pcbnew.LoadBoard(str(DEST))
        existing={f.GetReference():f for f in saved.GetFootprints()}
        assert set(existing)==set(before)
        assert len(saved.GetTracks())==len(board.GetTracks())==4
        assert not saved.Zones()
        for ref,fp in refs.items():
            q=existing[ref]
            assert q.GetPosition()==fp.GetPosition(),(ref,"unexpected placement")
            assert pad_signature(q)==pad_signature(fp),(ref,"pad net delta")
        def track_sig(b):
            return sorted((t.GetLayerName(),t.GetNetname(),t.GetWidth(),
                           t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y)
                          for t in b.GetTracks())
        assert track_sig(saved)==track_sig(board),"committed trace geometry/net differs"
        # Do not regenerate committed UUIDs or replace reviewed board bytes.
    else:
        pcbnew.SaveBoard(str(DEST),board)
    assert DEST.is_file()
    final=pcbnew.LoadBoard(str(DEST))
    assert len(final.GetFootprints())==139 and len(final.GetTracks())==4
    assert not final.Zones()
    assert not any(d.GetLayer()==pcbnew.Edge_Cuts for d in final.GetDrawings())
    fref={f.GetReference():f for f in final.GetFootprints()}
    for ref in before_sig:
        assert pad_signature(fref[ref])==before_sig[ref],ref
    for t in final.GetTracks():
        assert t.GetLayer()==pcbnew.F_Cu
        assert t.GetWidth()==pcbnew.FromMM(0.25)
        assert any(t.GetNetname().endswith("/"+n) for n in ("BUCK_BOOT","BUCK_EN"))
    def pad_distance(boardrefs,a,an,b,bn):
        pa,pb=pad_by_number(boardrefs[a],an),pad_by_number(boardrefs[b],bn)
        av,bv=pa.GetPosition(),pb.GetPosition()
        return math.hypot(av.x-bv.x,av.y-bv.y)/1e6
    improvement={
      "bootstrap_before_mm":pad_distance(before,"U100","6","C102","1"),
      "bootstrap_after_mm":pad_distance(fref,"U100","6","C102","1"),
      "enable_before_mm":pad_distance(before,"U100","5","R103","1"),
      "enable_after_mm":pad_distance(fref,"U100","5","R103","1"),
    }
    assert improvement["bootstrap_after_mm"]<improvement["bootstrap_before_mm"]
    assert improvement["enable_after_mm"]<improvement["enable_before_mm"]
    result={"revision":"V7.84","physical_footprints":139,"relocated":RELOCATE,
      "new_copper_segments":4,"new_track_nets":["BUCK_BOOT","BUCK_EN"],
      "all_139_pad_nets_conserved":True,"all_unmodified_positions_conserved":True,
      "distance":improvement,"no_power_tracks":True,"no_rf_tracks":True,
      "no_outline":True,"no_ground_zones":True,"source_13v8_unqualified":True,
      "buck_compensation_output_current_loop_unqualified":True,
      "no_drc_release_claim":True,"no_fab":True,"no_tx":True}
    EVID.parent.mkdir(parents=True,exist_ok=True)
    EVID.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    return result

class TestV784(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=build()
    def test_real_tracks(self):self.assertEqual(self.data["new_copper_segments"],4)
    def test_relocation(self):self.assertEqual(len(self.data["relocated"]),12)
    def test_no_power_or_rf(self):self.assertTrue(self.data["no_power_tracks"] and self.data["no_rf_tracks"])
    def test_pin_net_parity(self):self.assertTrue(self.data["all_139_pad_nets_conserved"])
    def test_no_release(self):self.assertTrue(self.data["no_drc_release_claim"] and self.data["no_fab"] and self.data["no_tx"])
if __name__=="__main__":unittest.main()
