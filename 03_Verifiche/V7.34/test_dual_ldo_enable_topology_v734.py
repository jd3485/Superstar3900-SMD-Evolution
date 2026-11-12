"""V7.34 fail-closed topology gate for codec IOVDD/LDOIN sequencing.
Reads KiCad source only, not the exported native netlist. No hardware timing proof.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCH = ROOT / "04_KiCad/Modulo_MCU_CODEC_V7.33_YAGEO_8R_0402_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"

# TI TPS7A20 SBVS338H, DBV: IN=1, GND=2, EN=3, NC=4, OUT=5.
DBV_PINS = {1: (-10.16,-10.16), 2: (-10.16,10.16),
            3: (-10.16,0.0), 5: (10.16,-10.16)}
REGULATORS = {
    "U6205": (870.0,415.0,"3V3_CODEC_IO"),
    "U6206": (930.0,415.0,"3V3_CODEC_LDOIN"),
}

def local_labels():
    source = SCH.read_text(encoding="utf-8")
    data = {}
    for name,x,y in re.findall(r'\(label "([^"]+)" \(at ([-\d.]+) ([-\d.]+)',source):
        coord=(round(float(x),4),round(float(y),4))
        if coord in data and data[coord] != name:
            raise ValueError("Conflicting local labels: "+str(coord))
        data[coord] = name
    return data

def regulator_pins(ref):
    if ref not in REGULATORS:
        raise ValueError("Unexpected regulator")
    x,y,expected_out=REGULATORS[ref]
    source = SCH.read_text(encoding="utf-8")
    pat = r'\(symbol \(lib_id "S3900E:TPS7A2033_DBV_DRAFT"\) \(at ([\d.]+) ([\d.]+) 0\)[\s\S]{0,360}?\(property "Reference" "'+ref+r'"'
    matches=list(re.finditer(pat,source))
    if len(matches)!=1 or (float(matches[0][1]),float(matches[0][2]))!=(x,y):
        raise AssertionError("Regulator instance changed: "+ref)
    names=local_labels()
    pins={n:names.get((round(x+dx,4),round(y+dy,4))) for n,(dx,dy) in DBV_PINS.items()}
    return pins

class TestDualLdoStartup(unittest.TestCase):
    def test_01_both_ldos_share_enable_and_input(self):
        for ref in REGULATORS:
            pins=regulator_pins(ref)
            self.assertEqual(pins[1],"5V_DIGITAL_FILTERED")
            self.assertEqual(pins[3],"5V_DIGITAL_FILTERED")
            self.assertEqual(pins[2],"GND")
    def test_02_separate_codec_supply_rails(self):
        self.assertEqual(regulator_pins("U6205")[5],"3V3_CODEC_IO")
        self.assertEqual(regulator_pins("U6206")[5],"3V3_CODEC_LDOIN")
        self.assertNotEqual(regulator_pins("U6205")[5],regulator_pins("U6206")[5])
    def test_03_topology_does_not_imply_time_order(self):
        # Explicit counterexample, NOT a claimed measured start time:
        # both EN high at t=0 does not imply IOVDD ready before LDOIN.
        plausible_ramp_us = {"IOVDD": 1200, "LDOIN": 700}
        self.assertGreater(plausible_ramp_us["IOVDD"],plausible_ramp_us["LDOIN"])
    def test_04_shared_enable_is_not_a_sequencing_controller(self):
        io = regulator_pins("U6205")
        analog = regulator_pins("U6206")
        self.assertEqual(io[3], analog[3])
        self.assertNotEqual(io[5], analog[5])

if __name__ == "__main__":
    unittest.main()
