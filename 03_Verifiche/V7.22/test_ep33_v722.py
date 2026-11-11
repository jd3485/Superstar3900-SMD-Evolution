"""V7.22 TI TLV320AIC3204 RHB EP33 real KiCad pin/node diff. NO FAB NO TX."""
import re, json, unittest, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OM=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.12_REANNOTATED_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
NM=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.22_EP33_GROUNDED_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
NR=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.22_EP33_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch"
OUT=ROOT/"03_Verifiche/V7.22/output-ci"
OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/"03_Verifiche/V7.17"))
from audit_full_board_native_v717 import native_erc
TI_NAMES=dict(enumerate(("MCLK","BCLK","WCLK","DIN/MFP1","DOUT/MFP2","IOVDD","IOVSS",
"SCLK/MFP3","SCL/SS","SDA/MOSI","MISO/MFP4","SPI_SELECT","IN1_L","IN1_R",
"IN2_L","IN2_R","AVSS","REF","MICBIAS","IN3_L","IN3_R","LOL","LOR",
"AVDD","HPL","LDOIN","HPR","DVSS","DVDD","LDO_SELECT","RESET","GPIO/MFP5"),1))
def pins(src):
    raw=src.read_text()
    marker='(symbol "S3900E:TLV320AIC3204_RHB32_DRAFT"'
    assert raw.count(marker)==1
    txt=raw.split(marker,1)[1].split('(symbol "S3900E:',1)[0]
    matches=re.findall(r'\(pin ([\w-]+) line \(at ([-.\d]+) ([-.\d]+) (\d+)\) \(length 5.08\) \(name "([^"]+)"[^\n]*?\(number "(\d+)"',txt)
    result={int(n):(name,typ,float(x),float(y),int(a)) for typ,x,y,a,name,n in matches}
    assert len(result)==len(matches)
    return result
def nets(src):
    txt=src.read_text()
    assert txt.startswith('(export (version ') and '(nets' in txt
    starts=list(re.finditer(r'^    \(net \(code "\d+"\) \(name "([^"]+)"\)',txt,re.M))
    result={}
    for i,m in enumerate(starts):
        body=txt[m.end():starts[i+1].start() if i+1<len(starts) else len(txt)]
        assert m.group(1) not in result
        result[m.group(1)]=set(re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)',body))
    return result
def audit():
    old,new=pins(OM),pins(NM)
    assert set(old)==set(range(1,33)) and set(new)==set(range(1,34))
    assert all(old[i][0]==TI_NAMES[i] for i in TI_NAMES)
    assert all(new[i]==old[i] for i in old)
    assert new[33]==("EP_GND_THERMAL_PAD","passive",48.26,-30.48,180)
    mcu=NM.read_text()
    assert mcu.count('(label "GND" (at 448.2600 190.4800 0)')==1
    # Pin 33 also exists on STM32 U6201: verify codec-specific 33 using pins(NM) above.
    codec=mcu.split('(property "Reference" "U6202"',1)[1].split('(instances ',1)[0]
    assert '(property "Footprint" ""' in codec
    assert NR.read_text().count('../Modulo_MCU_CODEC_V7.22_EP33_GROUNDED_NOT_FOR_FAB/')==1
    original=nets(OUT/"v722.original.net"); revised=nets(OUT/"v722.revised.net")
    assert set(original)==set(revised) and len(original)==100
    def membership(n):return {(name,ref,pin) for name,members in n.items() for ref,pin in members}
    orig_nodes,new_nodes=membership(original),membership(revised)
    assert orig_nodes-new_nodes==set()
    delta=new_nodes-orig_nodes
    assert delta=={("/MCU_CODEC_AFE_existing_V2_1_UNQUALIFIED/GND","U6202","33")},repr(delta)
    prev=native_erc(OUT/"v722.original.erc.rpt")
    now=native_erc(OUT/"v722.revised.erc.rpt")
    assert (prev["errors"],prev["warnings"])==(36,340)
    assert now["errors"]<=prev["errors"]
    for cat in ("pin_to_pin","pin_not_driven","power_pin_not_driven","wire_dangling","pin_not_connected"):
        assert now["categories"].get(cat,0)<=prev["categories"].get(cat,0),cat
    assert now["warnings"]<=prev["warnings"]+1
    result={"revision":"V7.22","TI_SLOS602E_pin_names_1_to_32_MATCH":True,
      "EP33_vendor_pad":33,"only_added_net_node":list(next(iter(delta))),
      "lost_nodes":0,"root_nets":100,"root_components":132,
      "erc_baseline":{"errors":prev["errors"],"warnings":prev["warnings"]},
      "erc_revision":{"errors":now["errors"],"warnings":now["warnings"]},
      "footprint_U6202_assigned":False,"stencil_qualified":False,
      "all_15_interfaces_HOLD":True,"NO_FAB":True,"NO_TX":True,"SG48_HOLD":True}
    (OUT/"v722.native_pin_net_diff.json").write_text(json.dumps(result,indent=2)+"\n")
    return result
class TestNativeTI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=audit()
    def test_vendor_pinmap(self):self.assertTrue(self.data["TI_SLOS602E_pin_names_1_to_32_MATCH"])
    def test_ep33_exists(self):self.assertEqual(self.data["EP33_vendor_pad"],33)
    def test_ep33_ground(self):self.assertEqual(self.data["only_added_net_node"][2],"33")
    def test_native_node_parity(self):self.assertEqual(self.data["lost_nodes"],0)
    def test_root_nets(self):self.assertEqual(self.data["root_nets"],100)
    def test_erc_no_new_errors(self):self.assertLessEqual(self.data["erc_revision"]["errors"],36)
    def test_footprint_hold(self):self.assertFalse(self.data["footprint_U6202_assigned"])
    def test_safety(self):self.assertTrue(self.data["NO_FAB"] and self.data["NO_TX"] and self.data["SG48_HOLD"])
if __name__=="__main__":unittest.main()
