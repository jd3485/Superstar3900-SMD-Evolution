"""V7.50 KiCad9 native vendor JST J100 power and J101 SPI host footprints.
Electrical 138 components and 101 nets unchanged, no connector wiring approved.
"""
import json,re,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"03_Verifiche/V7.50/output-ci"
OLDROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.49_LMX_PULLDOWN_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
NEWROOT=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.50_JST_CONNECTORS_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
OLDAUX=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.49_LMX_UNUSED_PULLDOWN_REVIEW_NOT_FOR_FAB"
NEWAUX=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.50_JST_CONNECTORS_REVIEW_NOT_FOR_FAB"
JST_LIB=Path("/usr/share/kicad/footprints/Connector_JST.pretty")
PARTS={
"J100":{"foot":"Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical","mpn":"B2P-VH(LF)(SN)","mate":"VHR-2N","signals":{"1":"PWR_13V8_AUX_RAW","2":"GND_MAIN"}},
"J101":{"foot":"Connector_JST:JST_GH_BM06B-GHS-TBT_1x06-1MP_P1.25mm_Vertical","mpn":"BM06B-GHS-TBT(LF)(SN)","mate":"GHR-6V-S",
        "signals":{"1":"PLL_SCK","2":"PLL_SDI","3":"PLL_CSB","4":"PLL_CE","5":"PLL_MUXOUT","6":"GND_MAIN"}}
}
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def pinmap(netlist):
    found={}
    for net, ps in nets(netlist).items():
        for refpin in ps:
            if refpin in found:raise AssertionError(("multi-net pin",refpin))
            found[refpin]=net
    return found

def source_gate():
    old=(OLDAUX/"S3900E_AUX_POWER_V1_5.kicad_sch").read_text(encoding="utf8")
    actual=(NEWAUX/"S3900E_AUX_POWER_V1_5.kicad_sch").read_text(encoding="utf8")
    expected=old
    for ref,d in PARTS.items():
        a=expected.index('(property "Reference" "'+ref+'"')
        e=expected.index('(instances ',a)
        seg=expected[a:e]
        m=re.search(r'\(property "Footprint" "" \(at ([\d.]+) ([\d.]+) 0\) \(effects \(font \(size 1.016 1.016\)\) \(hide yes\)\)\)',seg)
        assert m,(ref,seg)
        replace=m.group(0).replace('(property "Footprint" ""','(property "Footprint" "'+d["foot"]+'"')
        replace+='\n (property "MPN" "'+d["mpn"]+'" (at '+m[1]+' '+m[2]+' 0) (effects (font (size 1 1)) (hide yes)))'
        replace+='\n (property "MatingHousing" "'+d["mate"]+'" (at '+m[1]+' '+m[2]+' 0) (effects (font (size 1 1)) (hide yes)))'
        expected=expected[:a]+seg.replace(m.group(0),replace)+expected[e:]
    assert actual==expected,"Unexpected AUX modifications besides J100/J101 metadata"
    for fn in ("01_EFUSE_AUX.kicad_sch","02_BUCK_5V.kicad_sch","03_PLL_LDO_TCXO.kicad_sch"):
        assert (OLDAUX/fn).read_bytes()==(NEWAUX/fn).read_bytes(),fn
    sr=NEWROOT.read_text(encoding="utf8")
    assert sr.count("../Gerarchico_Alimentazioni_V7.50_JST_CONNECTORS_REVIEW_NOT_FOR_FAB/")==1
    assert sr.count("(sheet (at ")==3
    assert "Gerarchico_Alimentazioni_V7.49_LMX_UNUSED_PULLDOWN_REVIEW_NOT_FOR_FAB" in OLDROOT.read_text()
    for fn in ("fp-lib-table","sym-lib-table","S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_pro"):
        assert (OLDROOT.parent/fn).read_bytes()==(NEWROOT.parent/fn).read_bytes(),fn

def native_gate():
    source_gate()
    import pcbnew
    footprints={}
    for ref,d in PARTS.items():
        fp=pcbnew.FootprintLoad(str(JST_LIB),d["foot"].split(":")[1])
        assert fp is not None,("KiCad 9 standard JST footprint unavailable",ref,d["foot"])
        items={}
        for p in fp.Pads():
            num=p.GetNumber()
            items.setdefault(num,[]).append({
              "x":round(pcbnew.ToMM(p.GetPosition().x),4),
              "y":round(pcbnew.ToMM(p.GetPosition().y),4),
              "w":round(pcbnew.ToMM(p.GetSize().x),4),
              "h":round(pcbnew.ToMM(p.GetSize().y),4)})
        assert set(d["signals"]).issubset(items),(ref,items)
        footprints[ref]=items
    assert set(footprints["J100"])=={"1","2"} and len(footprints["J100"]["1"])==1
    a,b=footprints["J100"]["1"][0],footprints["J100"]["2"][0]
    assert round(b["x"]-a["x"],2)==3.96,(a,b)
    assert len(footprints["J101"]["MP"])==2,"JST GH mechanical solder pads missing"
    assert all(len(footprints["J101"][str(x)])==1 for x in range(1,7))
    xs=[footprints["J101"][str(x)][0]["x"] for x in range(1,7)]
    assert all(round(xs[i+1]-xs[i],2)==1.25 for i in range(5)),xs
    c0,c1=(compmap(OUT/f) for f in ("v750.original.net","v750.revised.net"))
    assert len(c0)==len(c1)==138,(len(c0),len(c1))
    delta={ref:(c0[ref],c1[ref]) for ref in c0 if c0[ref]!=c1[ref]}
    assert set(delta)==set(PARTS),delta
    for ref,d in PARTS.items():
        assert delta[ref][0][0]=="" and delta[ref][1][0]==d["foot"] and delta[ref][0][1]==delta[ref][1][1],delta[ref]
    missing=(sum(not v[0] for v in c0.values()),sum(not v[0] for v in c1.values()))
    assert missing==(2,0),missing
    n0,n1=nets(OUT/"v750.original.net"),nets(OUT/"v750.revised.net")
    assert len(n0)==len(n1)==101 and n0==n1,"Schematic netlist changed unexpectedly"
    pins=pinmap(OUT/"v750.revised.net")
    for ref,d in PARTS.items():
        for pin,net in d["signals"].items():
            assert pins[(ref,pin)].endswith("/"+net),(ref,pin,pins[(ref,pin)])
    assert pins[("J100","2")]!=pins[("J101","6")],"GND_MAIN local names do not bridge root sheets"
    assert pins[("FB6201","1")]!=pins[("U2","1")],"AUX 5V and MCU supply not physically joined"
    e0,e1=native_erc(OUT/"v750.original.erc.rpt"),native_erc(OUT/"v750.revised.erc.rpt")
    assert (e0["errors"],e0["warnings"])==(28,221),e0
    assert (e1["errors"],e1["warnings"])==(28,221),e1
    result={"revision":"V7.50","components":138,"nets":101,"electrical_pin_net_deltas":0,
        "changed_footprints":sorted(delta),"missing_before":2,"missing_after":0,
        "native_pad_maps":footprints,"erc_before":{"errors":e0["errors"],"warnings":e0["warnings"]},
        "erc_after":{"errors":e1["errors"],"warnings":e1["warnings"]},
        "mating_and_harness_physical_validated":False,"shield_ground_return_validated":False,
        "J101_MP_anchors_ground_decided":False,"reverse_polarity_protection_tested":False,
        "crossdomain_joined":False,"NO_FAB":True,"NO_GERBER":True,"NO_TX":True}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v750.native.json").write_text(json.dumps(result,indent=2)+"\n")
    return result
class TestJSTTwo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.d=native_gate()
    def test_01_two_changed_refs(self):self.assertEqual(self.d["changed_footprints"],["J100","J101"])
    def test_02_zero_missing_footprints(self):self.assertEqual(self.d["missing_after"],0)
    def test_03_138_parts(self):self.assertEqual(self.d["components"],138)
    def test_04_101_nets(self):self.assertEqual((self.d["nets"],self.d["electrical_pin_net_deltas"]),(101,0))
    def test_05_j100_two_holes(self):self.assertEqual(set(self.d["native_pad_maps"]["J100"]),{"1","2"})
    def test_06_j101_six_signal_pads(self):self.assertTrue(all(str(x) in self.d["native_pad_maps"]["J101"] for x in range(1,7)))
    def test_07_j101_two_mp_anchors(self):self.assertEqual(len(self.d["native_pad_maps"]["J101"]["MP"]),2)
    def test_08_erc_no_change(self):self.assertEqual(self.d["erc_before"],self.d["erc_after"])
    def test_09_harness_not_signed_off(self):self.assertFalse(self.d["mating_and_harness_physical_validated"])
    def test_10_mechanical_mp_ground_not_approved(self):self.assertFalse(self.d["J101_MP_anchors_ground_decided"])
    def test_11_crossmodule_ground_untouched(self):self.assertFalse(self.d["crossdomain_joined"])
    def test_12_fab_tx_not_approved(self):self.assertTrue(self.d["NO_FAB"] and self.d["NO_GERBER"] and self.d["NO_TX"])
if __name__=="__main__":unittest.main()
