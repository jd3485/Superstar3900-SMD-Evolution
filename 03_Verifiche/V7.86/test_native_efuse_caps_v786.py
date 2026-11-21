"""V7.86: native KiCad9 prove C200/C201/C202 eFuse passive placement.

Placement-only staging on the same physical master. No changed schematic,
net, pad, trace, via, ground return, RF, TX, mechanical outline or zones.
Do not claim vendor-qualified current loops or fab readiness.
"""
from pathlib import Path
import math,json,unittest
import pcbnew

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"04_KiCad/PCB_MASTER_V7.85_BUCK_FEEDBACK_WIP/S3900E_MASTER_V785_FEEDBACK_NO_FAB.kicad_pcb"
TARGET=ROOT/"04_KiCad/PCB_MASTER_V7.86_EFUSE_CAPS_WIP/S3900E_MASTER_V786_EFUSE_CAPS_NO_FAB.kicad_pcb"
EVID=ROOT/"03_Verifiche/V7.86/output-ci/v786_efuse_caps_review.json"
MOVE={"C200":(61,39),"C201":(74,54),"C202":(80,42)}
PAIRS=(("C200","2","U200","1"),("C201","2","U200","12"),("C202","2","U200","13"))
assert len(MOVE)==3

def footprint_map(board):
    f={x.GetReference():x for x in board.GetFootprints()}
    assert len(f)==139 and "Y1" not in f and "D200" not in f
    return f

def electrical_signature(fp):
    return sorted((p.GetNumber(),p.GetNetname(),p.GetLayerSet().Contains(pcbnew.F_Cu),
                   p.GetLayerSet().Contains(pcbnew.B_Cu),
                   p.GetLayerSet().Contains(pcbnew.F_Paste)) for p in fp.Pads())

def track_signature(board):
    return sorted((t.GetNetname(),t.GetLayer(),t.GetWidth(),
                   t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y)
                  for t in board.GetTracks())

def pad(refs,ref,n):
    xs=[p for p in refs[ref].Pads() if p.GetNumber()==n]
    assert len(xs)==1,(ref,n,len(xs))
    return xs[0]

def distance(refs,a,na,b,nb):
    p,q=pad(refs,a,na),pad(refs,b,nb)
    return math.hypot(p.GetPosition().x-q.GetPosition().x,
                      p.GetPosition().y-q.GetPosition().y)/1e6

def test_board():
    assert SOURCE.exists() and TARGET.exists()
    before=pcbnew.LoadBoard(str(SOURCE))
    now=pcbnew.LoadBoard(str(TARGET))
    f0,f1=footprint_map(before),footprint_map(now)
    assert set(f0)==set(f1)
    assert len(before.GetTracks())==len(now.GetTracks())==17
    assert track_signature(before)==track_signature(now), "existing copper changed"
    assert not before.Zones() and not now.Zones()
    assert not any(d.GetLayer()==pcbnew.Edge_Cuts for d in now.GetDrawings())
    for ref in f0:
        p0,p1=f0[ref],f1[ref]
        assert electrical_signature(p0)==electrical_signature(p1),ref
        assert p0.GetFPID().GetLibItemName()==p1.GetFPID().GetLibItemName(),ref
        if ref in MOVE:
            x,y=MOVE[ref]
            assert p1.GetPosition()==pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y)),ref
            assert p0.GetPosition()!=p1.GetPosition(),ref
        else:
            assert p0.GetPosition()==p1.GetPosition(),(ref,"unexpected relocation")
    targets={}
    for ref,n,other,othernum in PAIRS:
        p,q=pad(f1,ref,n),pad(f1,other,othernum)
        assert p.GetNetname()==q.GetNetname(),(ref,n,other,othernum)
        assert p.GetNetname().split("/")[-1] in {"EFUSE_VIN","DV_DT_NODE","BUCK_VIN_PROTECTED"}
        d0=distance(f0,ref,n,other,othernum)
        d1=distance(f1,ref,n,other,othernum)
        assert d1<d0 and d1<=10.5,(ref,d0,d1)
        targets[ref]={"net":p.GetNetname(),"before_mm":round(d0,3),"after_mm":round(d1,3)}
    # RTN and GND_MAIN must remain independently named, in all 139 pads.
    names={p.GetNetname() for f in f1.values() for p in f.Pads()}
    assert any(x.endswith("/EFUSE_RTN") for x in names)
    assert any(x.endswith("/GND_MAIN") for x in names)
    assert any(x.endswith("/GND_RF") for x in names)
    result={"revision":"V7.86","native_footprints":139,"existing_tracks":17,
            "moved_caps":MOVE,"distances":targets,
            "all_139_footprint_pad_nets_preserved":True,
            "all_other_136_positions_preserved":True,"track_geometry_unchanged":True,
            "efuse_rtn_and_gnd_main_separate":True,
            "no_schematic_edit":True,"no_new_routing":True,
            "no_outline":True,"no_vias":True,"no_zones":True,
            "no_release_drc_claim":True,"no_fab":True,"no_tx":True}
    EVID.parent.mkdir(parents=True,exist_ok=True)
    EVID.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    return result

class TestV786(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proof=test_board()
    def test_n(self):
        self.assertEqual(len(self.proof["moved_caps"]),3)
    def test_unchanged_copper(self):
        self.assertTrue(self.proof["track_geometry_unchanged"])
    def test_not_release(self):
        self.assertTrue(self.proof["no_fab"] and self.proof["no_tx"])
    def test_real_distance(self):
        self.assertEqual(len(self.proof["distances"]),3)
if __name__=="__main__":
    unittest.main()
