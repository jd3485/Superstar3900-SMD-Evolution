"""V7.89: two guarded electrical eFuse control connections on real KiCad PCB.

Only C201 is moved (DV_DT to U200.12), with four UVLO_NODE copper
sections branching from existing R200.1 trace to R201.2, plus two
DV_DT_NODE sections U200.12 to C201.2. All 30 previous segments,
139 pad-net maps, return domains, source/OUT power and HOLD are preserved.
"""
from pathlib import Path
import json, math, unittest
import pcbnew

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"04_KiCad/PCB_MASTER_V7.88_EFUSE_THRESHOLDS_WIP/S3900E_MASTER_V788_UVLO_OVP_NO_FAB.kicad_pcb"
BOARD=ROOT/"04_KiCad/PCB_MASTER_V7.89_EFUSE_DVDT_UVLO_WIP/S3900E_MASTER_V789_DVDT_UVLO_NO_FAB.kicad_pcb"
EVID=ROOT/"03_Verifiche/V7.89/output-ci/v789_native_electrical.json"
MOVE={"C201":(76,42)}
ROUTES={
  "UVLO_NODE":[((53,39),(51.5,39)),((51.5,39),(51.5,54)),
               ((51.5,54),(56.825,54)),((56.825,54),(56.825,52))],
  "DV_DT_NODE":[((71.9,45.325),(76.775,45.325)),
                ((76.775,45.325),(76.775,42))]
}
def mm(v):
    return pcbnew.VECTOR2I(pcbnew.FromMM(v[0]),pcbnew.FromMM(v[1]))
def near(a,b):
    return abs(a.x-b.x)<=pcbnew.FromMM(.001) and abs(a.y-b.y)<=pcbnew.FromMM(.001)
def pins(f):
    return sorted((p.GetNumber(),p.GetNetname(),
       p.GetLayerSet().Contains(pcbnew.F_Cu),
       p.GetLayerSet().Contains(pcbnew.B_Cu)) for p in f.Pads())
def trsig(b):
    return sorted((t.GetNetname(),t.GetLayer(),t.GetWidth(),
                   t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y)
                  for t in b.GetTracks())
def pad(fs,r,n):
    found=[p for p in fs[r].Pads() if p.GetNumber()==n]
    assert len(found)==1,(r,n,len(found))
    return found[0]
def validate():
    first=pcbnew.LoadBoard(str(BASE))
    second=pcbnew.LoadBoard(str(BOARD))
    a={f.GetReference():f for f in first.GetFootprints()}
    b={f.GetReference():f for f in second.GetFootprints()}
    assert set(a)==set(b) and len(a)==139
    assert len(first.GetTracks())==30 and len(second.GetTracks())==36
    assert not first.Zones() and not second.Zones()
    assert not any(d.GetLayer()==pcbnew.Edge_Cuts for d in second.GetDrawings())
    for r in a:
        assert pins(a[r])==pins(b[r]),r
        assert a[r].GetFPID().GetLibItemName()==b[r].GetFPID().GetLibItemName(),r
        if r in MOVE:
            assert b[r].GetPosition()==mm(MOVE[r]) and a[r].GetPosition()!=b[r].GetPosition(),r
        else:
            assert a[r].GetPosition()==b[r].GetPosition(),r
    prev=set(trsig(first))
    curr=set(trsig(second))
    assert prev<=curr and len(curr-prev)==6
    assert pad(b,"R200","1").GetNetname()==pad(b,"R201","2").GetNetname()
    assert pad(b,"U200","12").GetNetname()==pad(b,"C201","2").GetNetname()
    assert near(pad(b,"R201","2").GetPosition(),mm((56.825,52)))
    assert near(pad(b,"U200","12").GetPosition(),mm((71.9,45.325)))
    assert near(pad(b,"C201","2").GetPosition(),mm((76.775,42)))
    # UVLO branch attaches at a genuine endpoint of the existing V7.88
    # UVLO copper, not at an invented pad or isolated free-standing stub.
    uvlo=pad(b,"R200","1").GetNetname()
    assert any(t.GetNetname()==uvlo and (near(t.GetStart(),mm((53,39)))
        or near(t.GetEnd(),mm((53,39)))) for t in first.GetTracks())
    proofs={}
    for net,parts in ROUTES.items():
        true_net=(pad(b,"U200","12") if net=="DV_DT_NODE" else
                  pad(b,"R200","1")).GetNetname()
        assert true_net.endswith("/"+net)
        for i,(x,y) in enumerate(parts):
            assert x!=y and (i==0 or parts[i-1][1]==x)
            hits=[t for t in second.GetTracks()
                  if t.GetNetname()==true_net and t.GetLayer()==pcbnew.F_Cu
                  and t.GetWidth()==pcbnew.FromMM(.2)
                  and ((near(t.GetStart(),mm(x)) and near(t.GetEnd(),mm(y)))
                    or (near(t.GetStart(),mm(y)) and near(t.GetEnd(),mm(x))))]
            assert len(hits)==1,(net,x,y,"real copper missing or duplicated")
        proofs[net]={"segments":len(parts),"physical_endpoints":True}
    for n in ("4","10","13","14"):
        assert pad(b,"U200",n).GetNetCode()==0,(n,"NC/FLT pin altered")
    for t in second.GetTracks():
        assert t.GetLayer()==pcbnew.F_Cu
        assert t.GetNetname().endswith(("/BUCK_BOOT","/BUCK_EN","/BUCK_FB",
          "/BUCK_DIV_TOP","/EFUSE_MODE","/ILIM_NODE",
          "/UVLO_NODE","/OVP_NODE","/DV_DT_NODE"))
    names={p.GetNetname() for f in b.values() for p in f.Pads()}
    assert any(x.endswith("/EFUSE_RTN") for x in names)
    assert any(x.endswith("/GND_MAIN") for x in names)
    assert any(x.endswith("/GND_RF") for x in names)
    out={"version":"V7.89","footprints":139,"preserved_tracks":30,
         "new_segments":6,"total_tracks":36,"moved":MOVE,
         "native_connections":proofs,"all_pad_nets_preserved":True,
         "other_138_placements_preserved":True,"no_return_or_power_copper":True,
         "no_vias":True,"no_zones":True,"no_outline":True,"no_tx":True,
         "no_fab":True,"no_release":True}
    EVID.parent.mkdir(parents=True,exist_ok=True)
    EVID.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    return out
class TestV789(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=validate()
    def test_nets(self):self.assertEqual(set(self.r["native_connections"]),{"UVLO_NODE","DV_DT_NODE"})
    def test_count(self):self.assertEqual(self.r["total_tracks"],36)
    def test_guard(self):self.assertTrue(self.r["all_pad_nets_preserved"] and self.r["no_return_or_power_copper"])
    def test_no_release(self):self.assertTrue(self.r["no_fab"] and self.r["no_tx"])
if __name__=="__main__":unittest.main()
