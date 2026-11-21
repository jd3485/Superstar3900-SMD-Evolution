"""V7.83: place 15 *existing* RX coupon footprints on the single master PCB.

Placement-only diagnostics. NO RF route, TX, outline, plane, Gerber, or fabrication.
Do not infer physical cross-module connectivity from similarly named nets.
"""
from pathlib import Path
import importlib.util
import json
import sys
import unittest
import pcbnew

ROOT=Path(__file__).resolve().parents[2]
BASE_SCRIPT=ROOT/"03_Verifiche/V7.82/build_master_pll_stage_v782.py"
BASE_BOARD=ROOT/"04_KiCad/PCB_MASTER_V7.82_PLL_PLACEMENT_WIP/S3900E_MASTER_V782_STAGING_NO_FAB.kicad_pcb"
DEST=ROOT/"04_KiCad/PCB_MASTER_V7.83_RX_PLACEMENT_WIP/S3900E_MASTER_V783_STAGING_NO_FAB.kicad_pcb"
EVID=ROOT/"03_Verifiche/V7.83/output-ci/v783_rx_placement.json"

# A review-only RX island, deliberately separate from power/MCU/PLL islands.
# Locations are placeholders pending antenna, chassis, impedance and return-plane design.
RX_REFS=("J9101","C9101","U9101","C9102","J9102","L9101",
         "C9103","C9104","C9105","J9105","J9103",
         "R9201","R9203","R9202","J9104")
RX_AT={ref:(495+45*(i%5),95+55*(i//5)) for i,ref in enumerate(RX_REFS)}
assert len(RX_REFS)==len(set(RX_REFS))==15
assert len(set(RX_AT.values()))==15

def base_module():
    spec=importlib.util.spec_from_file_location("s3900_v782",BASE_SCRIPT)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def build():
    old=base_module()
    # Validate committed base PCB and native master pad/net parity.
    old.build()
    comps=old.compmap(old.NET)
    pins=old.pinmap(old.nets(old.NET))
    assert len(comps)==141 and len(old.nets(old.NET))==103
    missing=set(comps)-set(old.PLACEMENT)
    assert missing==set(RX_REFS)|{"Y1","D200"}, ("Unexpected schematic remainder",sorted(missing))
    assert "Y1" not in RX_REFS and "D200" not in RX_REFS
    libraries=old.lib_dirs()
    board=pcbnew.LoadBoard(str(BASE_BOARD))
    existing={f.GetReference():f for f in board.GetFootprints()}
    assert len(existing)==124 and set(existing)==set(old.PLACEMENT)
    # Existing copper must remain unmodified; no hidden electrical changes.
    assert not board.GetTracks() and not board.Zones()
    assert not any(d.GetLayer()==pcbnew.Edge_Cuts for d in board.GetDrawings())
    added={}
    for ref,(x,y) in RX_AT.items():
        fpname,value=comps[ref]
        assert ":" in fpname,(ref,fpname)
        nickname,name=fpname.split(":",1)
        lib=libraries.get(nickname,Path("/usr/share/kicad/footprints")/(nickname+".pretty"))
        assert lib.is_dir(),(ref,fpname,str(lib))
        fp=pcbnew.FootprintLoad(str(lib),name)
        assert fp is not None,(ref,fpname)
        fp.SetReference(ref)
        fp.SetValue(value)
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y)))
        field=fp.Reference()
        sz=field.GetTextSize()
        if min(sz.x,sz.y)<pcbnew.FromMM(0.8):
            field.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.9),pcbnew.FromMM(0.9)))
            field.SetTextThickness(pcbnew.FromMM(0.12))
        seen={}
        for pad in fp.Pads():
            n=pad.GetNumber()
            # No copper pad may lack a schematic pin number; paste-only is fine.
            if not n:
                assert not pad.GetLayerSet().Contains(pcbnew.F_Cu),(ref,"unnumbered copper")
                assert pad.GetLayerSet().Contains(pcbnew.F_Paste),(ref,"unnumbered non-paste pad")
                continue
            if n=="MP":
                assert (ref,n) not in pins and pad.GetNetCode()==0,(ref,n)
                continue
            assert n not in seen,(ref,n,"duplicate physical pad number")
            native=pins.get((ref,n))
            if native is not None:
                net=board.FindNet(native)
                assert net is not None,(ref,n,native)
                pad.SetNet(net)
            seen[n]=native
        assert {number for r,number in pins if r==ref} <=set(seen),(ref,"missing footprint pads")
        board.Add(fp)
        added[ref]={"footprint":fpname,"at_mm":[x,y],"pad_nets":seen}
    assert len(board.GetFootprints())==139
    assert len(board.GetTracks())==0 and len(board.Zones())==0
    board.GetTitleBlock().SetTitle("S3900E V7.83 RX placement-only WIP NO FAB NO TX")
    DEST.parent.mkdir(parents=True,exist_ok=True)
    # If the actual V7.83 board has been committed, reject unexplained changes
    # instead of overwriting a newer manual or electrically modified PCB.
    if DEST.exists():
        prev=pcbnew.LoadBoard(str(DEST))
        prevrefs={f.GetReference():f for f in prev.GetFootprints()}
        assert set(prevrefs)==set(existing)|set(RX_REFS)
        assert len(prev.GetTracks())==0 and len(prev.Zones())==0
        for fp in board.GetFootprints():
            prior=prevrefs[fp.GetReference()]
            assert prior.GetPosition()==fp.GetPosition(),fp.GetReference()
            assert prior.GetFPID().GetLibItemName()==fp.GetFPID().GetLibItemName()
            assert sorted((p.GetNumber(),p.GetNetname()) for p in prior.Pads())==sorted((p.GetNumber(),p.GetNetname()) for p in fp.Pads()),fp.GetReference()
    pcbnew.SaveBoard(str(DEST),board)
    restored=pcbnew.LoadBoard(str(DEST))
    refs={f.GetReference():f for f in restored.GetFootprints()}
    assert set(refs)==set(existing)|set(RX_REFS) and len(refs)==139
    for ref in existing:
        a,b=existing[ref],refs[ref]
        assert a.GetPosition()==b.GetPosition(),ref
        assert sorted((p.GetNumber(),p.GetNetname()) for p in a.Pads())==sorted((p.GetNumber(),p.GetNetname()) for p in b.Pads()),ref
    for ref in RX_REFS:
        assert min(refs[ref].Reference().GetTextSize().x,refs[ref].Reference().GetTextSize().y)>=pcbnew.FromMM(0.8),ref
    assert not restored.GetTracks() and not restored.Zones()
    assert not any(d.GetLayer()==pcbnew.Edge_Cuts for d in restored.GetDrawings())
    result={"revision":"V7.83","base_components":124,"rx_added":15,
            "placed":139,"schematic_components":141,"schematic_nets":103,
            "not_placed":["D200","Y1"],"rx_footprints":added,
            "all_old_pad_nets_unchanged":True,"all_rx_pads_from_native_netlist":True,
            "no_routing":True,"no_outline":True,"no_fab":True,"no_tx":True,
            "ground_domain_bridges_added":False,
            "rf_50ohm_staging_only":True,"drc_release_pass":False}
    EVID.parent.mkdir(parents=True,exist_ok=True)
    EVID.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    return result

class TestV783RX(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proof=build()
    def test_new_rx(self):
        self.assertEqual(self.proof["rx_added"],15)
        self.assertEqual(self.proof["placed"],139)
    def test_hold(self):
        self.assertEqual(self.proof["not_placed"],["D200","Y1"])
        self.assertTrue(self.proof["no_fab"] and self.proof["no_tx"])
    def test_original_pads_preserved(self):
        self.assertTrue(self.proof["all_old_pad_nets_unchanged"])
    def test_no_pretend_release(self):
        self.assertFalse(self.proof["drc_release_pass"])
if __name__=="__main__":
    unittest.main()
