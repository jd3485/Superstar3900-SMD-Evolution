"""V7.22 TI RHB0032E codec physical 32 + EP33 land/stencil, fail closed NO FAB."""
import re, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
FP=ROOT/"04_KiCad/Librerie_Footprint_V7.22_RHB_TI_HOLD/S3900E_TI_RHB_Review.pretty/TLV320AIC3204_RHB0032E_VENDOR_CANDIDATE.kicad_mod"
LIB=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.22_EP33_NOT_FOR_FAB/fp-lib-table"
MCU=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.22_EP33_GROUNDED_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
LIBID="S3900E_TI_RHB_V722_HOLD:TLV320AIC3204_RHB0032E_VENDOR_CANDIDATE"
def parse_footprint():
    t=FP.read_text()
    electrical=re.findall(r'\(pad "(\d+)" smd (?:roundrect|rect) \(at ([-.\d]+) ([-.\d]+)\) '
        r'\(size ([-.\d]+) ([-.\d]+)\) \(layers "F.Cu" "F.Mask"(?: "F.Paste")?\)',t)
    paste=re.findall(r'\(pad "" smd roundrect \(at ([-.\d]+) ([-.\d]+)\) '
        r'\(size ([-.\d]+) ([-.\d]+)\) \(layers "F.Paste"\)',t)
    points={int(n):tuple(float(v) for v in (x,y,w,h)) for n,x,y,w,h in electrical}
    assert len(points)==len(electrical)
    return t,points,[tuple(map(float,x)) for x in paste]

def expected_pads():
    out={}
    for i in range(8):out[i+1]=(-2.4,round(-1.75+.5*i,2),.6,.25)
    for i in range(8):out[i+9]=(round(-1.75+.5*i,2),2.4,.25,.6)
    for i in range(8):out[i+17]=(2.4,round(1.75-.5*i,2),.6,.25)
    for i in range(8):out[i+25]=(round(1.75-.5*i,2),-2.4,.25,.6)
    out[33]=(0.0,0.0,3.45,3.45)
    return out

class TestTIRHBVendorPackage(unittest.TestCase):
    def test_16_all_32_pad_centers_and_pitches(self):
        _,pts,_=parse_footprint()
        self.assertEqual(pts,expected_pads())

    def test_17_exposed_pad_33_single_ground_copper_pad(self):
        text,pts,_=parse_footprint()
        self.assertEqual(pts[33],(0.,0.,3.45,3.45))
        self.assertEqual(text.count('(pad "33" smd rect '),1)
        self.assertIn('(layers "F.Cu" "F.Mask")',text)

    def test_18_ti_paste_example_4_apertures_75pct(self):
        _,_,paste=parse_footprint()
        expected={(x,y,1.49,1.49) for x in (-.845,.845) for y in (-.845,.845)}
        self.assertEqual(set(paste),expected)
        self.assertEqual(len(paste),4)
        self.assertAlmostEqual(4*1.49**2/3.45**2,0.7460953581180422)
        self.assertTrue(.74 < 4*1.49**2/3.45**2 < .76)

    def test_19_physical_33_pads_not_dummy_nc_or_vias(self):
        text,pts,paste=parse_footprint()
        self.assertEqual(len(pts),33)
        self.assertEqual(len(paste),4)
        self.assertEqual(set(pts),set(range(1,34)))
        self.assertNotIn('(via ',text)
        self.assertNotIn('(net ',text)

    def test_20_native_review_library_registered(self):
        table=LIB.read_text()
        self.assertEqual(table.count('(lib (name "S3900E_TI_RHB_V722_HOLD")'),1)
        self.assertIn("../Librerie_Footprint_V7.22_RHB_TI_HOLD/S3900E_TI_RHB_Review.pretty",table)

    def test_21_not_assigned_stencil_and_ground_still_hold(self):
        src=MCU.read_text()
        block=src.split('(property "Reference" "U6202"',1)[1].split('(instances ',1)[0]
        self.assertIn('(property "Footprint" ""',block)
        self.assertNotIn(LIBID,src)
        self.assertIn('(number "33"',src)
        self.assertIn('(label "GND" (at 448.2600 190.4800 0)',src)
        self.assertIn("NO FAB/NO ASSIGNMENT",FP.read_text())

if __name__=="__main__":
    unittest.main()
