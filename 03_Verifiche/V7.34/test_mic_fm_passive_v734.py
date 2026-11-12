"""V7.34 MIC/FM passive filter screening; NOT full SPICE or actual codec firmware signoff.
Standard-library only. The model contains series Cc + Rs and shunt Cf || Req.
"""
import cmath
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCH = ROOT / "04_KiCad/Modulo_MCU_CODEC_V7.33_YAGEO_8R_0402_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
NETWORKS = {
    "MIC": {
        "refs": ("C6227", "R6207", "C6228"),
        "values": ("100nF", "1k", "4.7nF"),
        "labels": (("MIC_PREAMP_OUT", "MIC_AC_COUPLED"),
                   ("MIC_AC_COUPLED", "MIC_CODEC_IN"),
                   ("MIC_CODEC_IN", "GND")),
        "cc_f": 100e-9, "rs_ohm": 1000.0, "cf_f": 4.7e-9,
    },
    "FM": {
        "refs": ("C6229", "R6208", "C6230"),
        "values": ("1uF", "1k", "10nF"),
        "labels": (("FM_DISCRIM_RAW", "FM_AC_COUPLED"),
                   ("FM_AC_COUPLED", "FM_CODEC_IN"),
                   ("FM_CODEC_IN", "GND")),
        "cc_f": 1e-6, "rs_ohm": 1000.0, "cf_f": 10e-9,
    },
}

def passive_transfer(freq_hz, coupling_f, series_ohm, shunt_f, codec_input_ohm, source_ohm=0):
    """Linear small-signal V(codec node)/V(ideal source), ground-referred Req."""
    if min(freq_hz, coupling_f, series_ohm, shunt_f, codec_input_ohm) <= 0 or source_ohm < 0:
        raise ValueError("All physical parameters must be valid positive values")
    omega = 2 * math.pi * freq_hz
    zc = 1/(1j*omega*coupling_f)
    zload = 1/(1/codec_input_ohm + 1j*omega*shunt_f)
    return zload / (source_ohm + zc + series_ohm + zload)

def unloaded_shunt_pole_hz(series_ohm, shunt_f):
    """ONLY isolated Rs-Cf pole without input load/source/coupling capacitor."""
    return 1 / (2*math.pi*series_ohm*shunt_f)

def instance_data():
    text=SCH.read_text(encoding="utf-8")
    inst={}
    for m in re.finditer(r'\(symbol \(lib_id "S3900E:([CR])_DRAFT"\) \(at ([\d.]+) ([\d.]+) 0\)[\s\S]{0,360}?\(property "Reference" "([CR]62\d\d)"[\s\S]{0,150}?\(property "Value" "([^"]+)"',text):
        typ,x,y,ref,value=m.groups()
        if ref in inst:
            raise AssertionError(f"Duplicate {ref}")
        inst[ref]=(typ,float(x),float(y),value)
    labels={(round(float(x),4),round(float(y),4)):name for name,x,y
            in re.findall(r'\(label "([^"]+)" \(at ([\d.]+) ([\d.]+)',text)}
    return inst,labels

class TestPassiveNetworks(unittest.TestCase):
    def test_01_exact_three_component_networks_in_kicad(self):
        inst, labels = instance_data()
        for net in NETWORKS.values():
            for ref,val,want in zip(net["refs"],net["values"],net["labels"]):
                typ,x,y,actual_val=inst[ref]
                self.assertEqual(actual_val,val)
                self.assertEqual(typ,ref[0])
                terminals=(labels.get((round(x,4),round(y-5.08,4))),
                           labels.get((round(x,4),round(y+5.08,4))))
                self.assertEqual(terminals,want,(ref,terminals))
    def test_02_ideal_unloaded_pole(self):
        self.assertAlmostEqual(unloaded_shunt_pole_hz(1000,4.7e-9),33862.753849,places=4)
        self.assertAlmostEqual(unloaded_shunt_pole_hz(1000,10e-9),15915.494309,places=4)
    def test_03_transfer_is_passive_and_finite(self):
        for n in NETWORKS.values():
            for req in (10000.0,20000.0):
                for f in (30,100,300,1000,3000,10000,20000,50000):
                    h=passive_transfer(f,n["cc_f"],n["rs_ohm"],n["cf_f"],req)
                    self.assertTrue(math.isfinite(abs(h)))
                    self.assertLessEqual(abs(h),1.00000001)
    def test_04_source_and_codec_impedance_change_response(self):
        for n in NETWORKS.values():
            base=passive_transfer(1000,n["cc_f"],n["rs_ohm"],n["cf_f"],10000)
            changed=passive_transfer(1000,n["cc_f"],n["rs_ohm"],n["cf_f"],20000,600)
            self.assertGreater(abs(base-changed),1e-4)

if __name__=="__main__":
    unittest.main()
