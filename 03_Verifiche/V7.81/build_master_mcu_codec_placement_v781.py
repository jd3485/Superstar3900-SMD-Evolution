"""V7.81 REAL KiCad9 power-chain footprint placement staged from 7sheet native netlist.

NOT a completed radio PCB, now extending power into MCU/codec: no outline, routing, zones, 13.8V source
qualification, safety release, or fabricated board.
"""
from pathlib import Path
import json,re,sys,unittest
import pcbnew
ROOT=Path(__file__).resolve().parents[2]
MASTER=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.79_SWD_JST_GH_SERVICE_CONNECTOR_HOLD"
NET=ROOT/"03_Verifiche/V7.79/output-ci/v779.revised.net"
DEST=ROOT/"04_KiCad/PCB_MASTER_V7.81_MCU_CODEC_SWD_PLACEMENT_WIP/S3900E_MASTER_V781_STAGING_NO_FAB.kicad_pcb"
EVID=ROOT/"03_Verifiche/V7.81/output-ci/v781_mcu_codec_power_placement.json"
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap

# Physical, preliminary left-to-right power flow. No enclosure/outlines or
# PCB stackup and no route; all placement coordinates are subject to DFM review.
PLACEMENT={
 "J100":(25,45),"F200":(47,45),"C200":(59,29),
 "U200":(69,45),"R200":(59,60),"R201":(65,60),"R202":(71,60),
 "R203":(77,60),"R204":(83,60),"C201":(80,29),"C202":(86,29),
 "SW200":(93,62),"C100":(101,29),"C101":(107,29),
 "U100":(113,45),"R103":(106,59),"R104":(112,59),"C102":(118,29),
 "L100":(136,45),"C103":(153,34),"C104":(153,45),
 "R100":(154,58),"R101":(160,58),"R102":(166,58),"C105":(160,51)
}

# MCU, codec, SWD/debug, local regulator, clock and all physically
# instantiated MCU page decouplers / passives. No power-domain nets are
# artificially joined; all copper pads copy their native schematic net IDs.
MCU_MAJOR={
 "J6201":(206,102),
 "U6201":(246,103), "U6202":(288,103),
 "X6201":(311,117),
 "FB6201":(205,148),
 "U6203":(228,148), "U6204":(249,148),
 "U6205":(270,148), "U6206":(291,148),
 "U6207":(312,148)
}
MCU_CAPS={f"C{n}":(205+10*((n-6201)%8),176+10*((n-6201)//8))
          for n in range(6201,6232)}
MCU_RES={f"R{n}":(215+13*(n-6201),230) for n in range(6201,6209)}
MCU_PLACEMENT={**MCU_MAJOR,**MCU_CAPS,**MCU_RES}
assert len(MCU_PLACEMENT)==49
POWER_PLACEMENT=dict(PLACEMENT)
PLACEMENT.update(MCU_PLACEMENT)
assert len(PLACEMENT)==74
OLDER_BOARD=ROOT/"04_KiCad/PCB_MASTER_V7.80_POWER_PLACEMENT_WIP/S3900E_MASTER_V780_STAGING_NO_FAB.kicad_pcb"
assert OLDER_BOARD.is_file()

def lib_dirs():
    t=(MASTER/"fp-lib-table").read_text()
    ret={}
    for name,uri in re.findall(r'\(lib \(name "([^"]+)"\)\(type "KiCad"\)\(uri "([^"]+)"\)',t):
        path=Path(uri.replace(chr(36)+"{KIPRJMOD}",str(MASTER))).resolve()
        assert path.is_dir(),(name,path)
        ret[name]=path
    return ret

def pinmap(n):
    d={}
    for net,pairs in n.items():
        for pair in pairs:
            assert pair not in d,pair
            d[pair]=net
    return d

def build():
    comps=compmap(NET)
    ni=nets(NET)
    pins=pinmap(ni)
    assert len(comps)==141 and len(ni)==103,(len(comps),len(ni))
    assert set(PLACEMENT)<=set(comps)
    assert "D200" not in PLACEMENT and "J6201" in PLACEMENT
    assert all(ref in comps for ref in MCU_PLACEMENT)
    assert set(PLACEMENT)==set(POWER_PLACEMENT)|set(MCU_PLACEMENT)
    board=pcbnew.BOARD()
    board.GetTitleBlock().SetTitle("S3900E MASTER power + MCU CODEC SWD placement V7.81 WIP NO FAB")
    netobjs={}
    for n in sorted(ni):
        o=pcbnew.NETINFO_ITEM(board,n)
        board.Add(o)
        netobjs[n]=o
    libraries=lib_dirs()
    shown={}
    for ref,(x,y) in PLACEMENT.items():
        fpname,value=comps[ref]
        assert ":" in fpname,(ref,fpname)
        nickname,name=fpname.split(":",1)
        path=libraries.get(nickname,Path("/usr/share/kicad/footprints")/(nickname+".pretty"))
        assert path.is_dir(),(ref,str(path))
        f=pcbnew.FootprintLoad(str(path),name)
        assert f is not None,(ref,fpname)
        f.SetReference(ref)
        f.SetValue(value)
        f.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y)))
        # KiCad9 native nonrelease DRC identified U100 own reference
        # overlap against U100 silkscreen at (113,42.6). Move only the
        # footprint reference to a clear provisional field location.
        if ref=="U100":
            f.Reference().SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(113),pcbnew.FromMM(36)))
        board.Add(f)
        seen=set()
        assigned={}
        for pad in f.Pads():
            n=pad.GetNumber()
            if n=="MP":
                assert (ref,n) not in pins and pad.GetNetCode()==0
                continue
            assert n and n not in seen,(ref,n,"duplicate solder pad")
            seen.add(n)
            net=pins.get((ref,n))
            if net:
                pad.SetNet(netobjs[net])
                assert pad.GetNetname()==net,(ref,n,net)
            assigned[n]=net
        assert {n for rr,n in pins if rr==ref}<=seen,(ref,"electrical pin without land")
        shown[ref]=dict(footprint=fpname,value=value,at_mm=[x,y],pad_nets=assigned)
    assert pins[("U200","8")]==pins[("U200","17")]!=pins[("U200","9")]
    assert pins[("U200","15")]==pins[("U200","16")]==pins[("U100","3")]
    assert pins[("F200","1")]!=pins[("F200","2")]
    assert pins[("J100","1")]!=pins[("J100","2")]
    assert len(board.GetTracks())==0 and len(board.Zones())==0
    # The genuine V7.80 board is immutable: every original 25 reference,
    # pad/net, and placement is conserved on the expanded 74-part PCB.
    old_board=pcbnew.LoadBoard(str(OLDER_BOARD))
    oldrefs={x.GetReference():x for x in old_board.GetFootprints()}
    assert set(oldrefs)==set(POWER_PLACEMENT)
    for ref,prev in oldrefs.items():
        current=next(x for x in board.GetFootprints() if x.GetReference()==ref)
        assert current.GetFPID().GetLibItemName()==prev.GetFPID().GetLibItemName(),ref
        po=prev.GetPosition()
        pn=current.GetPosition()
        assert (po.x,po.y)==(pn.x,pn.y),(ref,"V7.80 placement unexpectedly changed")
        oldpads={p.GetNumber():p for p in prev.Pads()}
        newpads={p.GetNumber():p for p in current.Pads()}
        assert set(oldpads)==set(newpads),(ref,"V7.80 pad changed")
        for n,pp in oldpads.items():
            assert pp.GetNetname()==newpads[n].GetNetname(),(ref,n,"native net regression")
    # Physical MCU and audio remain LOCAL isolated electrical domains:
    # previous 13.8V power, eFuse RTN and MCU GND are never tied as a shortcut.
    assert pins[("J6201","1")]==pins[("U6201","16")]
    assert pins[("J6201","2")]==pins[("U6201","49")]
    assert pins[("J6201","3")]==pins[("U6201","50")]
    assert pins[("J6201","4")]==pins[("U6201","7")]
    assert pins[("J6201","5")]==pins[("U6201","15")]
    assert pins[("U6203","2")]!=pins[("U2","2")]
    assert pins[("U6202","33")]!=pins[("U200","17")]
    # The first actual .kicad_pcb must be retained, not silently replaced by
    # an unrelated generated example in subsequent CI runs. Validate every
    # saved electrical pad against the current native master netlist BEFORE
    # re-emitting it; an unexpected old pad or net is a blocking regression.
    if DEST.exists():
        previous=pcbnew.LoadBoard(str(DEST))
        fp_by_ref={q.GetReference():q for q in previous.GetFootprints()}
        assert set(fp_by_ref)==set(PLACEMENT),("committed PCB reference delta",set(fp_by_ref)^set(PLACEMENT))
        for ref,(px,py) in PLACEMENT.items():
            fp=fp_by_ref[ref]
            pos=fp.GetPosition()
            assert (round(pcbnew.ToMM(pos.x),3),round(pcbnew.ToMM(pos.y),3))==(px,py),(ref,"old placement moved unexpectedly")
            for pad in fp.Pads():
                num=pad.GetNumber()
                native=pins.get((ref,num))
                if native:
                    assert pad.GetNetname()==native,(ref,num,"committed PCB pad net differs from schematic",pad.GetNetname(),native)
                else:
                    assert pad.GetNetCode()==0,(ref,num,"unspecified net assigned to PCB pad")
        assert len(previous.GetTracks())==0 and len(previous.Zones())==0
        assert not any(d.GetLayer()==pcbnew.Edge_Cuts for d in previous.GetDrawings())
    DEST.parent.mkdir(parents=True,exist_ok=True)
    pcbnew.SaveBoard(str(DEST),board)
    assert DEST.is_file() and DEST.stat().st_size>2000
    reload=pcbnew.LoadBoard(str(DEST))
    assert len(reload.GetFootprints())==len(PLACEMENT)
    assert len(reload.GetFootprints())==74
    assert {"J6201","U6201","U6202","U6203","U6204","U6205","U6206","U6207","X6201","FB6201"}<=set(f.GetReference() for f in reload.GetFootprints())
    assert len(reload.GetTracks())==0 and len(reload.Zones())==0
    u100=next(f for f in reload.GetFootprints() if f.GetReference()=="U100")
    pos=u100.Reference().GetPosition()
    assert (round(pcbnew.ToMM(pos.x),3),round(pcbnew.ToMM(pos.y),3))==(113,36),"U100 silk overlap recurrence"
    assert not any(d.GetLayer()==pcbnew.Edge_Cuts for d in reload.GetDrawings())
    result=dict(revision="V7.81",schematic_components=141,schematic_nets=103,
      placed_count=len(PLACEMENT),master_board=DEST.relative_to(ROOT).as_posix(),
      footprints=shown,physical_board_reload_success=True,no_tracks=True,
      no_zones=True,no_outline=True,no_copper_routing=True,
      source_13v8_not_qualified=True,efuse_rtn_separate_from_gnd_main=True,
      d200_dnp_not_placed=True,mcu_interface_placement_not_yet_assigned=False,
      mcu_codec_power_components_placed=len(MCU_PLACEMENT),
      previous_power_footprints_preserved=len(POWER_PLACEMENT),
      no_mechanical_enclosure_dimensions=True,no_stackup_qualified=True,
      no_drc_pass_claim=True,no_fab=True,no_tx=True)
    EVID.parent.mkdir(parents=True,exist_ok=True)
    EVID.write_text(json.dumps(result,indent=2)+"\n")
    return result

class TestV780Placement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=build()
    def test_01_real_file(self):self.assertTrue((ROOT/self.r["master_board"]).is_file())
    def test_02_placed(self):self.assertEqual(self.r["placed_count"],74)
    def test_02b_mcu_sheet_placement(self):self.assertEqual(self.r["mcu_codec_power_components_placed"],49)
    def test_02c_power_placement_preserved(self):self.assertEqual(self.r["previous_power_footprints_preserved"],25)
    def test_03_isolation(self):self.assertTrue(self.r["efuse_rtn_separate_from_gnd_main"])
    def test_04_no_routing(self):self.assertTrue(self.r["no_tracks"] and self.r["no_zones"])
    def test_05_no_enclosure(self):self.assertTrue(self.r["no_outline"])
    def test_06_kicad_reload(self):self.assertTrue(self.r["physical_board_reload_success"])
    def test_07_no_drc_claim(self):self.assertTrue(self.r["no_drc_pass_claim"])
    def test_08_no_fab(self):self.assertTrue(self.r["no_fab"] and self.r["no_tx"])
if __name__=="__main__":unittest.main()
