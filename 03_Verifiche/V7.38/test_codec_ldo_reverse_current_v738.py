"""V7.38 capacitor-inventory and reverse-current *screening* (not SPICE/hardware).

Vendor basis: TI TPS7A20 SBVS338H §6.3.7 warns reverse OUT->IN current
must not exceed 5% of 300mA rating for a SHORT period.
The C*dV/dt numbers are only hypothetical stored-charge transfer rates,
NOT LDO reverse currents. A measured/simulated reverse-current path is required.
"""
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_KiCad/Modulo_MCU_CODEC_V7.36_C6231_MURATA_GRM15_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
NOMINAL_OUTPUT_V = 3.3
LDO_RATED_A = 0.300
TI_REVERSE_LIMIT_FRACTION = 0.05
TI_REVERSE_SHORT_A = LDO_RATED_A * TI_REVERSE_LIMIT_FRACTION
EXPECTED_RAIL_CAPS = {
    "3V3_CODEC_IO": {"C6201": "100nF", "C6224": "1uF", "C6231": "100nF"},
    "3V3_CODEC_LDOIN": {"C6207": "100nF", "C6208": "10uF", "C6226": "1uF"},
}
EXPECTED_LDO_INSTANCES = ("U6205", "U6206")

def farads(raw):
    m = re.fullmatch(r"(\d+(?:\.\d+)?)(nF|uF)", raw)
    if not m:
        raise ValueError("Unsupported/unqualified value: "+raw)
    return float(m[1]) * {"nF": 1e-9, "uF": 1e-6}[m[2]]

def local_capacitors():
    """Read all real schematic capacitor terminal labels; avoid inferred nets."""
    src=SRC.read_text(encoding="utf-8")
    labs={}
    for name,x,y in re.findall(r'\(label "([^"]+)" \(at ([\d.]+) ([\d.]+)',src):
        pos=(round(float(x),4),round(float(y),4))
        if pos in labs and labs[pos]!=name:
            raise AssertionError(("conflicting endpoint label",pos))
        labs[pos]=name
    caps={}
    pattern=r'\(symbol \(lib_id "S3900E:C_DRAFT"\) \(at ([\d.]+) ([\d.]+) 0\)[\s\S]{0,360}?\(property "Reference" "(C62\d\d)"[\s\S]{0,145}?\(property "Value" "([^"]+)"'
    for x,y,ref,val in re.findall(pattern,src):
        if ref in caps:
            raise AssertionError(("duplicate cap",ref))
        x,y=float(x),float(y)
        p1=labs.get((round(x,4),round(y-5.08,4)))
        p2=labs.get((round(x,4),round(y+5.08,4)))
        caps[ref]=(val,p1,p2)
    return caps

def cap_inventory():
    caps=local_capacitors()
    found={}
    for net,expected in EXPECTED_RAIL_CAPS.items():
        group={ref:actual[0] for ref,actual in caps.items()
               if actual[1]==net and actual[2]=="GND"}
        if group!=expected:
            raise AssertionError(("rail inventory changed; requires review",net,group,expected))
        found[net]=sum(farads(val) for val in group.values())
    return found

def charge_coulomb(cap_f, volts=NOMINAL_OUTPUT_V):
    if cap_f<=0 or volts<0:
        raise ValueError("Invalid storage parameters")
    return cap_f*volts

def equivalent_charge_transfer_a(cap_f, seconds, delta_v=NOMINAL_OUTPUT_V, reverse_fraction=1.0):
    """Hypothetical average C*dV/dt portion assigned to reverse path.
    reverse_fraction is unknown [0,1], NOT derived from the schematic.
    """
    if seconds<=0 or cap_f<=0 or delta_v<0 or not 0<=reverse_fraction<=1:
        raise ValueError("Invalid hypothetical transient input")
    return cap_f*delta_v*reverse_fraction/seconds

def all_charge_through_reverse_limit_time_s(cap_f, delta_v=NOMINAL_OUTPUT_V):
    """ONLY if 100% of capacitor charge crossed the LDO reverse path."""
    return cap_f*delta_v/TI_REVERSE_SHORT_A

def require_actual_current_waveform_for_signoff(current_waveform=None):
    if current_waveform is None:
        raise RuntimeError("NO BROWNOUT SIGNOFF: reverse-current waveform is unknown")
    raise RuntimeError("Measurement/model validation not implemented; no signoff")

class TestV738PowerDown(unittest.TestCase):
    def test_01_two_regulators_present_real_vendor(self):
        txt=SRC.read_text(encoding="utf8")
        for ref in EXPECTED_LDO_INSTANCES:
            assert txt.count('(property "Reference" "'+ref+'"')==1
            idx=txt.index('(property "Reference" "'+ref+'"')
            self.assertIn('(property "Value" "TPS7A2033PDBVR"',txt[idx:idx+200])
    def test_02_all_three_rail_coupling_caps_exact(self):
        caps=local_capacitors()
        for net,expected in EXPECTED_RAIL_CAPS.items():
            for ref,val in expected.items():
                self.assertEqual(caps[ref],(val,net,"GND"))
    def test_03_rail_io_total(self):
        self.assertAlmostEqual(cap_inventory()["3V3_CODEC_IO"],1.2e-6)
    def test_04_rail_ldoin_total(self):
        self.assertAlmostEqual(cap_inventory()["3V3_CODEC_LDOIN"],11.1e-6)
    def test_05_total_ratio(self):
        inv=cap_inventory()
        self.assertAlmostEqual(inv["3V3_CODEC_LDOIN"]/inv["3V3_CODEC_IO"],9.25)
    def test_06_vendor_reversed_5percent_is_15ma(self):
        self.assertAlmostEqual(TI_REVERSE_SHORT_A,0.015)
    def test_07_io_stored_charge_at_nominal_v(self):
        self.assertAlmostEqual(charge_coulomb(cap_inventory()["3V3_CODEC_IO"]),3.96e-6)
    def test_08_ldoin_stored_charge_at_nominal_v(self):
        self.assertAlmostEqual(charge_coulomb(cap_inventory()["3V3_CODEC_LDOIN"]),36.63e-6)
    def test_09_illustrative_one_ms_io(self):
        self.assertAlmostEqual(equivalent_charge_transfer_a(1.2e-6,.001),.00396)
    def test_10_illustrative_one_ms_ldoin(self):
        self.assertAlmostEqual(equivalent_charge_transfer_a(11.1e-6,.001),.03663)
    def test_11_illustrative_five_ms_ldoin(self):
        self.assertAlmostEqual(equivalent_charge_transfer_a(11.1e-6,.005),.007326)
    def test_12_one_ms_ldoin_if_only_quarter_reverse(self):
        self.assertAlmostEqual(equivalent_charge_transfer_a(11.1e-6,.001,reverse_fraction=.25),.0091575)
    def test_13_conditional_reverse_limit_time_io(self):
        self.assertAlmostEqual(all_charge_through_reverse_limit_time_s(1.2e-6),.000264)
    def test_14_conditional_reverse_limit_time_ldoin(self):
        self.assertAlmostEqual(all_charge_through_reverse_limit_time_s(11.1e-6),.002442)
    def test_15_reverse_fraction_zero_is_zero(self):
        self.assertEqual(equivalent_charge_transfer_a(11.1e-6,.001,reverse_fraction=0),0)
    def test_16_invalid_reverse_fraction_fails_closed(self):
        for fraction in (-.01,1.01):
            with self.assertRaises(ValueError):
                equivalent_charge_transfer_a(1e-6,.001,reverse_fraction=fraction)
    def test_17_invalid_period_fails_closed(self):
        with self.assertRaises(ValueError):
            equivalent_charge_transfer_a(1e-6,0)
    def test_18_invalid_units_fail_closed(self):
        with self.assertRaises(ValueError):
            farads("100pF")
    def test_19_no_current_waveform_signoff(self):
        with self.assertRaisesRegex(RuntimeError,"NO BROWNOUT SIGNOFF"):
            require_actual_current_waveform_for_signoff()
    def test_20_no_signoff_from_fictional_current_trace(self):
        with self.assertRaisesRegex(RuntimeError,"no signoff"):
            require_actual_current_waveform_for_signoff([(0,0),(.001,.01)])

if __name__=="__main__":
    unittest.main()
