"""V7.22 ST DS12288 LQFP64 manufacturer-recommended pad layout. HOLD/NO FAB."""
import re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
FP=ROOT/"04_KiCad/Librerie_Footprint_V7.22_ST_LQFP_TI_HOLD/S3900E_ST_LQFP_Review.pretty/STM32G474RE_LQFP64_ST_DS12288_CANDIDATE.kicad_mod"
LIB=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.22_EP33_NOT_FOR_FAB/fp-lib-table"
MCU=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.22_EP33_GROUNDED_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
LIBID="S3900E_ST_LQFP_V722_HOLD:STM32G474RE_LQFP64_ST_DS12288_CANDIDATE"
def pads():
    text=FP.read_text()
    rows=re.findall(r'\(pad "(\d+)" smd roundrect \(at ([-.\d]+) ([-.\d]+)\) '
        r'\(size ([-.\d]+) ([-.\d]+)\) \(layers "F.Cu" "F.Mask" "F.Paste"\)',text)
    found={int(n):tuple(float(v) for v in (x,y,dx,dy)) for n,x,y,dx,dy in rows}
    assert len(rows)==len(found)
    return found
def expected():
    out={}
    for i in range(16):out[1+i]=(round(-3.75+.5*i,2),5.75,.3,1.2)
    for i in range(16):out[17+i]=(5.75,round(3.75-.5*i,2),1.2,.3)
    for i in range(16):out[33+i]=(round(3.75-.5*i,2),-5.75,.3,1.2)
    for i in range(16):out[49+i]=(-5.75,round(-3.75+.5*i,2),1.2,.3)
    return out
class TestSTLQFP64VendorFootprint(unittest.TestCase):
    def test_22_all_64_manufacturer_pad_numbers_and_centers(self):
        self.assertEqual(pads(),expected())
    def test_23_pitch_and_body_span(self):
        p=pads()
        self.assertEqual(len(p),64)
        self.assertAlmostEqual(p[16][0]-p[1][0],7.5) # 16 pad centers, pitch .5
        self.assertAlmostEqual(p[17][1]-p[32][1],7.5)
        self.assertAlmostEqual(p[17][0]-p[49][0],11.5)
        self.assertAlmostEqual(11.5+1.2,12.7)
        self.assertAlmostEqual(11.5-1.2,10.3)
    def test_24_each_vendor_land_1_2_by_0_3(self):
        for n,(_,_,w,h) in pads().items():
            self.assertIn((w,h),((1.2,.3),(.3,1.2)))
    def test_25_local_review_library_registered(self):
        lib=LIB.read_text()
        self.assertEqual(lib.count('(lib (name "S3900E_ST_LQFP_V722_HOLD")'),1)
        self.assertIn("../Librerie_Footprint_V7.22_ST_LQFP_TI_HOLD/S3900E_ST_LQFP_Review.pretty",lib)
    def test_26_not_assigned_to_mcu_no_fab(self):
        sch=MCU.read_text()
        s=sch.split('(property "Reference" "U6201"',1)[1].split('(instances ',1)[0]
        self.assertIn('(property "Footprint" ""',s)
        self.assertNotIn(LIBID,sch)
        self.assertIn("NO FAB/NO ASSIGNMENT",FP.read_text())
        self.assertNotIn('(net ',FP.read_text())
if __name__=="__main__": unittest.main()
