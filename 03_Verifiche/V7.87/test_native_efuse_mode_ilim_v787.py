"""V7.87: native KiCad9 protect TPS26600 local MODE/ILIM copper only.

Caution: V7.86 remains baseline; add seven F.Cu segments and move only R203
and R204. U200.6 (MODE)->R204.2 and U200.11 (ILIM)->R203.2.
All return copper (EFUSE_RTN, GND_MAIN, GND_RF), VIN/OUT current, SW,
RF/TX and cross-module interfaces remain OPEN/HOLD; NO FAB.
"""
from pathlib import Path
import json,math,unittest
import pcbnew
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"04_KiCad/PCB_MASTER_V7.86_EFUSE_CAPS_WIP/S3900E_MASTER_V786_EFUSE_CAPS_NO_FAB.kicad_pcb"
TARGET=ROOT/"04_KiCad/PCB_MASTER_V7.87_EFUSE_CONTROL_WIP/S3900E_MASTER_V787_EFUSE_CONTROL_NO_FAB.kicad_pcb"
EVID=ROOT/"03_Verifiche/V7.87/output-ci/v787_native_controls.json"
MOVE={"R203":(79,50),"R204":(59,49)}
ROUTES={
 "EFUSE_MODE":[((66.1,45.975),(63,45.975)),((63,45.975),(63,49)),((63,49),(59.825,49))],
 "ILIM_NODE":[((71.9,45.975),(76,45.975)),((76,45.975),(81.5,45.975)),
              ((81.5,45.975),(81.5,50)),((81.5,50),(79.825,50))],
}
EXPECTED={"EFUSE_MODE":(("U200","6"),("R204","2")),
          "ILIM_NODE":(("U200","11"),("R203","2"))}

def pins(fp):
    return sorted((p.GetNumber(),p.GetNetname(),
      p.GetLayerSet().Contains(pcbnew.F_Cu),
      p.GetLayerSet().Contains(pcbnew.B_Cu)) for p in fp.Pads())

def tracks(board):
    return sorted((t.GetNetname(),t.GetLayerName(),t.GetWidth(),
      t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y)
      for t in board.GetTracks())

def named_pad(refs,r,p):
    items=[x for x in refs[r].Pads() if x.GetNumber()==p]
    assert len(items)==1,(r,p,len(items))
    return items[0]

def point(xy):
    return pcbnew.VECTOR2I(pcbnew.FromMM(xy[0]),pcbnew.FromMM(xy[1]))

def check():
    assert BASE.exists() and TARGET.exists()
    old=pcbnew.LoadBoard(str(BASE))
    new=pcbnew.LoadBoard(str(TARGET))
    a={f.GetReference():f for f in old.GetFootprints()}
    b={f.GetReference():f for f in new.GetFootprints()}
    assert len(a)==len(b)==139 and set(a)==set(b)
    assert len(old.GetTracks())==17 and len(new.GetTracks())==24
    assert not old.Zones() and not new.Zones()
    assert not any(g.GetLayer()==pcbnew.Edge_Cuts for g in new.GetDrawings())
    for ref in a:
        assert pins(a[ref])==pins(b[ref]),(ref,"pad/net delta")
        assert a[ref].GetFPID().GetLibItemName()==b[ref].GetFPID().GetLibItemName(),ref
        if ref in MOVE:
            assert b[ref].GetPosition()==point(MOVE[ref]),ref
            assert a[ref].GetPosition()!=b[ref].GetPosition(),ref
        else:
            assert a[ref].GetPosition()==b[ref].GetPosition(),ref
    past=set(tracks(old))
    now=set(tracks(new))
    assert past<=now,"preexisting copper changed"
    assert len(now-past)==7
    route_evidence={}
    for net,segments in ROUTES.items():
        assert len(segments) in (3,4)
        endpoint_specs=EXPECTED[net]
        starts=[named_pad(b,*spec) for spec in endpoint_specs]
        native=starts[0].GetNetname()
        assert native==starts[1].GetNetname() and native.endswith("/"+net),net
        assert starts[0].GetLayerSet().Contains(pcbnew.F_Cu)
        assert starts[1].GetLayerSet().Contains(pcbnew.F_Cu)
        # Native pcbnew stores positions on integer-nanometre coordinates,
        # while floating FromMM(66.1) may differ by a handful of nm.
        # Tolerance is 1 micrometre, far below copper DRC clearance.
        for actual,proposed,label in (
            (starts[0].GetPosition(),point(segments[0][0]),endpoint_specs[0]),
            (starts[1].GetPosition(),point(segments[-1][1]),endpoint_specs[1])):
            assert abs(actual.x-proposed.x)<=pcbnew.FromMM(0.001) and abs(actual.y-proposed.y)<=pcbnew.FromMM(0.001), (
                "real physical pad endpoint mismatch",net,label,
                (actual.x,actual.y),(proposed.x,proposed.y))
        for i,(p,q) in enumerate(segments):
            assert p!=q and (i==0 or segments[i-1][1]==p)
            # pcbnew may canonicalize a track's start/end direction
            # or floating decimal mm -> integer-nm by a few nanometres.
            # Match undirected geometry within 1 um, with exact native NET,
            # F.Cu and 0.20 mm copper width. Never ignore unmatched tracks.
            def close(a,b):
                return abs(a.x-b.x)<=pcbnew.FromMM(0.001) and abs(a.y-b.y)<=pcbnew.FromMM(0.001)
            expected_start,expected_end=point(p),point(q)
            matches=[t for t in new.GetTracks()
               if t.GetNetname()==native and t.GetLayer()==pcbnew.F_Cu
               and t.GetWidth()==pcbnew.FromMM(0.2)
               and ((close(t.GetStart(),expected_start) and close(t.GetEnd(),expected_end))
                 or (close(t.GetStart(),expected_end) and close(t.GetEnd(),expected_start)))]
            assert len(matches)==1,("native route segment missing/duplicated",net,p,q,
                [(t.GetNetname(),t.GetStart().x,t.GetStart().y,
                  t.GetEnd().x,t.GetEnd().y) for t in new.GetTracks()
                 if t.GetNetname()==native][:10])
        first,last=starts
        dx=(first.GetPosition().x-last.GetPosition().x)/1e6
        dy=(first.GetPosition().y-last.GetPosition().y)/1e6
        route_evidence[net]={"pin1":endpoint_specs[0],"pin2":endpoint_specs[1],
             "direct_distance_mm":round(math.hypot(dx,dy),3),"copper_segments":len(segments)}
    # Physical TPS26600 U200 PWP NC13, FLT14 and NC10 explicitly unconnected;
    # never repurpose them to silence DRC.
    for p in ("10","13","14"):
        assert named_pad(b,"U200",p).GetNetCode()==0,("U200 unused pin unexpectedly connected",p)
    names={q.GetNetname() for f in b.values() for q in f.Pads()}
    assert any(n.endswith("/EFUSE_RTN") for n in names)
    assert any(n.endswith("/GND_MAIN") for n in names)
    assert any(n.endswith("/GND_RF") for n in names)
    for t in new.GetTracks():
        assert t.GetLayer()==pcbnew.F_Cu
        assert t.GetNetname().endswith(("/BUCK_BOOT","/BUCK_EN","/BUCK_FB",
           "/BUCK_DIV_TOP","/EFUSE_MODE","/ILIM_NODE"))
    result={"revision":"V7.87","footprints":139,"existing_segments_preserved":17,
         "added_segments":7,"total_segments":24,"moved":MOVE,
         "verified_routes":route_evidence,
         "all_139_pad_net_maps_unchanged":True,
         "efuse_rtn_gnd_main_gnd_rf_unbridged":True,
         "no_power_current_routing":True,"no_return_routing":True,
         "no_outline":True,"no_zones":True,"no_vias":True,"no_tx":True,
         "no_fab":True,"no_release_drc_claim":True}
    EVID.parent.mkdir(parents=True,exist_ok=True)
    EVID.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    return result

class TestV787(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=check()
    def test_continuity(self):self.assertEqual(len(clsdata:=self.data["verified_routes"]),2)
    def test_tracks(self):self.assertEqual(self.data["total_segments"],24)
    def test_returns(self):self.assertTrue(self.data["efuse_rtn_gnd_main_gnd_rf_unbridged"])
    def test_no_fab(self):self.assertTrue(self.data["no_fab"] and self.data["no_tx"])
if __name__=="__main__":
    unittest.main()
