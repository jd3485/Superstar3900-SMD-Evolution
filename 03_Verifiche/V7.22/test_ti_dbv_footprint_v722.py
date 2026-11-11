"""V7.22 TI DBV0005A real KiCad footprint candidate CAD land map (not production qualified)."""
import re, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
FP=ROOT/"04_KiCad/Librerie_Footprint_V7.22_DBV_TI_HOLD/S3900E_TI_DBV_Review.pretty/TPS7A20_DBV0005A_VENDOR_CANDIDATE.kicad_mod"
FP_TABLE=ROOT/"04_KiCad/Assemblaggio_RX_Power_V7.22_EP33_NOT_FOR_FAB/fp-lib-table"
MCU=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.22_EP33_GROUNDED_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"

# TI SBVS338H Rev.H p57 (PDF zero-index 56) LAND PATTERN EXAMPLE DBV0005A:
# pad 1.10 x 0.60 mm, centers x +/-1.30 mm and y -0.95/0/+0.95 mm.
# TI SBVS338H p4 Fig 4-4: top view 1=IN 2=GND 3=EN 4=N/C 5=OUT.
PADS={
    1:(-1.30,-0.95,1.10,0.60),
    2:(-1.30, 0.00,1.10,0.60),
    3:(-1.30, 0.95,1.10,0.60),
    4:( 1.30, 0.95,1.10,0.60),
    5:( 1.30,-0.95,1.10,0.60),
}
LIBID="S3900E_TI_DBV_V722_HOLD:TPS7A20_DBV0005A_VENDOR_CANDIDATE"

def native_pad_centers_and_sizes(src):
    rows=re.findall(
        r'\(pad "([1-5])" smd roundrect \(at ([-.0-9]+) ([-.0-9]+)\) '
        r'\(size ([-.0-9]+) ([-.0-9]+)\) '
        r'\(layers "F.Cu" "F.Mask" "F.Paste"\)',
        src)
    result={int(n):tuple(float(x) for x in (a,b,c,d)) for n,a,b,c,d in rows}
    assert len(rows)==len(result),"duplicate physical pad numbers"
    return result

class TestTIVendorDBVFootprint(unittest.TestCase):
    def test_11_exact_manufacturer_land_geometry(self):
        self.assertEqual(native_pad_centers_and_sizes(FP.read_text()),PADS)
        self.assertEqual(len(PADS),5)

    def test_12_spacing_widths_and_nc_pin4(self):
        p=native_pad_centers_and_sizes(FP.read_text())
        self.assertAlmostEqual(p[5][0]-p[1][0],2.60)
        self.assertAlmostEqual(p[3][1]-p[1][1],1.90)
        self.assertEqual(p[4][2:],(1.1,0.6))
        self.assertEqual(set(p),set(range(1,6)))
        self.assertEqual(p[4][0],p[5][0])  # NC pad exists physically

    def test_13_local_review_library_link(self):
        src=FP_TABLE.read_text()
        self.assertEqual(src.count('(lib (name "S3900E_TI_DBV_V722_HOLD")'),1)
        self.assertIn("../Librerie_Footprint_V7.22_DBV_TI_HOLD/S3900E_TI_DBV_Review.pretty",src)
        self.assertTrue(FP.is_file())
        self.assertIn('(footprint "TPS7A20_DBV0005A_VENDOR_CANDIDATE"',FP.read_text())

    def test_14_four_ldo_symbols_still_no_footprint_and_holds(self):
        src=MCU.read_text()
        for ref in ("U6203","U6204","U6205","U6206"):
            self.assertEqual(src.count('(property "Reference" "'+ref+'"'),1)
            body=src.split('(property "Reference" "'+ref+'"',1)[1].split('(instances ',1)[0]
            self.assertIn('(property "Footprint" ""',body)
            self.assertNotIn(LIBID,body)
        self.assertNotIn(LIBID,src)
        self.assertIn("NO FAB",src)

    def test_15_no_embedded_tx_fab_or_waiver(self):
        src=FP.read_text()
        self.assertIn("NO FAB/NO ASSIGNMENT",src)
        self.assertNotIn("(zone ",src)
        self.assertNotIn("PWR_FLAG",src)
        self.assertNotIn("(net ",src)

if __name__=="__main__":
    unittest.main()
