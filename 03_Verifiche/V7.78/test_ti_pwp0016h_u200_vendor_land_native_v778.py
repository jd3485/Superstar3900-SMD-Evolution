"""V7.78: U200 TI TPS26600 PWP0016H documented vendor-land candidate native CAD gate.

This is a physical-footprint ECO, NOT an approval of 3D fit, reflow,
creepage, thermal vias, power-source wiring, or a complete PCB.
"""
import json
import math
import sys
import unittest
from pathlib import Path
import pcbnew

ROOT=Path(__file__).resolve().parents[2]
A0=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.74_SIX_PWR_SOURCE_RETURN_PROVENANCE_HOLD"
A1=ROOT/"04_KiCad/Gerarchico_Alimentazioni_V7.78_TI_PWP0016H_EFUSE_LAND_HOLD"
R0=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.74_SIX_PWR_SOURCE_RETURN_PROVENANCE_HOLD"
R1=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.78_TI_PWP0016H_EFUSE_LAND_HOLD"
FP=ROOT/"04_KiCad/Librerie_Footprint_V7.78_TI_PWP0016H_HOLD/S3900E_TI_PWP0016H_Review.pretty/TPS26600_PWP0016H_EXAMPLE_LAND_REVIEW.kicad_mod"
OUT=ROOT/"03_Verifiche/V7.78/output-ci"
MASTER="S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
OLD="Package_SO:TSSOP-16-1EP_4.4x5mm_P0.65mm"
NEW="S3900E_TI_PWP0016H_V778_HOLD:TPS26600_PWP0016H_EXAMPLE_LAND_REVIEW"

sys.path.insert(0,str(ROOT/"03_Verifiche/V7.22"))
from test_ep33_v722 import nets
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.25"))
from test_six_vendor_assignments_v725 import compmap
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc

def point(p):
    a=p.GetPosition()
    return round(pcbnew.ToMM(a.x),4),round(pcbnew.ToMM(a.y),4)

def size(p):
    a=p.GetSize()
    return round(pcbnew.ToMM(a.x),4),round(pcbnew.ToMM(a.y),4)

def gate():
    # TI 4223630/A, 04/2017 PWP0016H example board pattern:
    # 16x1.50 x .45mm / row center distance 5.8mm / 0.65mm pitch
    # and 2.66 x 2.46mm exposed center land. 9 optional vias
    # and stencil design require separate thermal/DFM approval.
    f=pcbnew.FootprintLoad(str(FP.parent),FP.stem)
    assert f is not None, "PWP native KiCad9 footprint not loaded"
    pads={}
    for p in f.Pads():
        number=p.GetNumber()
        assert number not in pads,(number,"unintended duplicated copper pad")
        assert p.GetLayerSet().Contains(pcbnew.F_Cu)
        assert p.GetLayerSet().Contains(pcbnew.F_Mask)
        assert p.GetLayerSet().Contains(pcbnew.F_Paste)
        pads[number]=(point(p),size(p))
    assert set(pads)==set(map(str,range(1,18))),sorted(pads)
    for n in range(1,17):
        left=n<=8
        x=-2.9 if left else 2.9
        y=-2.275+(n-1)*.65 if left else -2.275+(16-n)*.65
        p,s=pads[str(n)]
        assert p==(round(x,4),round(y,4)),(n,p)
        assert s==(1.5,.45),(n,s)
    assert pads["17"]==((0.0,0.0),(2.66,2.46)),pads["17"]
    assert math.isclose(pads["16"][0][0]-pads["1"][0][0],5.8)
    assert math.isclose(pads["8"][0][1]-pads["1"][0][1],4.55)

    old=(A0/"01_EFUSE_AUX.kicad_sch").read_text()
    new=(A1/"01_EFUSE_AUX.kicad_sch").read_text()
    start=old.index('(property "Reference" "U200"')
    loc=old.index('(property "Footprint" "'+OLD+'"',start)
    assert loc<old.index('(instances ',start)
    expected=old[:loc]+old[loc:].replace('(property "Footprint" "'+OLD+'"','(property "Footprint" "'+NEW+'"',1)
    assert new==expected,"Only real U200 footprint property may change"
    for name in ("02_BUCK_5V.kicad_sch","03_PLL_LDO_TCXO.kicad_sch","S3900E_AUX_POWER_V1_5.kicad_sch"):
        assert (A0/name).read_bytes()==(A1/name).read_bytes()
    target=(R0/MASTER).read_text().replace(
       "Gerarchico_Alimentazioni_V7.74_SIX_PWR_SOURCE_RETURN_PROVENANCE_HOLD",
       "Gerarchico_Alimentazioni_V7.78_TI_PWP0016H_EFUSE_LAND_HOLD")
    assert target==(R1/MASTER).read_text()
    for name in ("S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_pro","sym-lib-table"):
        assert (R0/name).read_bytes()==(R1/name).read_bytes()
    table=(R1/"fp-lib-table").read_text()
    assert table.count('(lib (name "S3900E_TI_PWP0016H_V778_HOLD")')==1

    c0=compmap(OUT/"v778.original.net")
    c1=compmap(OUT/"v778.revised.net")
    assert len(c0)==len(c1)==140
    assert {ref for ref in c0 if c0[ref]!=c1[ref]}=={"U200"}
    assert c0["U200"]==(OLD,"TPS26600PWPT")
    assert c1["U200"]==(NEW,"TPS26600PWPT")
    n0=nets(OUT/"v778.original.net")
    n1=nets(OUT/"v778.revised.net")
    assert n0==n1 and len(n0)==103
    pinmap={}
    for net,nodes in n1.items():
        for node in nodes:
            assert node not in pinmap
            pinmap[node]=net
    assert pinmap[("U200","8")]==pinmap[("U200","17")]!=pinmap[("U200","9")]
    assert pinmap[("U200","1")]==pinmap[("U200","2")]
    assert pinmap[("U200","15")]==pinmap[("U200","16")]==pinmap[("U100","3")]
    er0=native_erc(OUT/"v778.original.erc.rpt")
    er1=native_erc(OUT/"v778.revised.erc.rpt")
    from collections import Counter
    assert (er0["errors"],er0["warnings"])==(28,180)
    assert (er1["errors"],er1["warnings"])==(28,180),(er0["errors"],er0["warnings"],er1["errors"],er1["warnings"])
    def findings(a):
        return Counter(json.dumps(f,sort_keys=True) for f in a["findings"])
    assert findings(er0)==findings(er1),"Actual ERC findings cannot change without real electrical ECO"
    result=dict(revision="V7.78",tested_with="KiCad9",manufacturer="Texas Instruments",
        mpn="TPS26600PWPT",package="PWP0016H",source_drawing="TI 4223630/A 04/2017",
        pads={ref:{"position_mm":p,"size_mm":s} for ref,(p,s) in pads.items()},
        ep17_connected_to_efuse_rtn_not_gnd_main=True,
        different_only_u200_footprint=True,all_pin_to_net_same=True,
        components=140,nets=103,erc_errors=28,erc_warnings=180,
        footprint_source_is_vendor_example_not_manufacturing_signoff=True,
        thermal_copper_vias_qualified=False,creepage_qualified=False,
        stencil_qualification=False,thermal_qualified=False,board_drc_verified=False,
        crossmodule_15_open=True,sg48_hold=True,no_fab=True,no_tx=True)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"v778_ti_pwp0016h_17pad_native.json").write_text(json.dumps(result,indent=2)+"\n")
    return result

class TestV778VendorLand(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=gate()
    def test_01_pad_count(self):self.assertEqual(len(self.r["pads"]),17)
    def test_02_vendor(self):self.assertEqual(self.r["package"],"PWP0016H")
    def test_03_rtn(self):self.assertTrue(self.r["ep17_connected_to_efuse_rtn_not_gnd_main"])
    def test_04_pinmap(self):self.assertTrue(self.r["all_pin_to_net_same"])
    def test_05_only_u200(self):self.assertTrue(self.r["different_only_u200_footprint"])
    def test_06_parts(self):self.assertEqual(self.r["components"],140)
    def test_07_nets(self):self.assertEqual(self.r["nets"],103)
    def test_08_erc(self):self.assertEqual((self.r["erc_errors"],self.r["erc_warnings"]),(28,180))
    def test_09_stencil_hold(self):self.assertFalse(self.r["stencil_qualification"])
    def test_10_thermal_hold(self):self.assertFalse(self.r["thermal_qualified"])
    def test_11_creepage_hold(self):self.assertFalse(self.r["creepage_qualified"])
    def test_12_no_fab(self):self.assertTrue(self.r["no_fab"] and self.r["no_tx"] and not self.r["board_drc_verified"])

if __name__=="__main__":
    unittest.main()
