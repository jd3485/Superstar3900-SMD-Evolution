"""V7.39 TI TPS7A20 input/output power-down voltage-envelope SCREEN.

Source: SBVS338H §5.1 VOUT(max) = min(6.5V, VIN + 0.3V).
Hypothetical exponentials are independent input waveforms, NOT simulated LDO
models; their violation windows are only a demand for real transient evidence.
"""
import math,re,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SCHEMATIC=ROOT/"04_KiCad/Modulo_MCU_CODEC_V7.36_C6231_MURATA_GRM15_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch"
VOUT_OVER_VIN_ABSMAX=0.3
REVERSE_CURRENT_SHORT_A=0.015
RAILS={
 "5V_DIGITAL_FILTERED":{"C6215":"1uF","C6219":"10uF","C6220":"100nF","C6221":"1uF","C6223":"1uF","C6225":"1uF"},
 "3V3_CODEC_IO":{"C6201":"100nF","C6224":"1uF","C6231":"100nF"},
 "3V3_CODEC_LDOIN":{"C6207":"100nF","C6208":"10uF","C6226":"1uF"},
}
REGULATORS={"U6205":("5V_DIGITAL_FILTERED","5V_DIGITAL_FILTERED","3V3_CODEC_IO"),
            "U6206":("5V_DIGITAL_FILTERED","CODEC_LDOIN_EN_SUPERVISED","3V3_CODEC_LDOIN")}

def capacitance_f(s):
    m=re.fullmatch(r"(\d+(?:\.\d+)?)(nF|uF)",s)
    if not m: raise ValueError(s)
    return float(m[1])*{"nF":1e-9,"uF":1e-6}[m[2]]

def source_capacitor_inventory():
    source=SCHEMATIC.read_text(encoding="utf-8")
    labels={}
    for name,x,y in re.findall(r'\(label "([^"]+)" \(at ([\d.]+) ([\d.]+)',source):
        p=(round(float(x),4),round(float(y),4))
        if p in labels and labels[p]!=name:raise AssertionError(("conflicting labels",p))
        labels[p]=name
    caps={}
    rx=r'\(symbol \(lib_id "S3900E:C_DRAFT"\) \(at ([\d.]+) ([\d.]+) 0\)[\s\S]{0,360}?\(property "Reference" "(C62\d\d)"[\s\S]{0,145}?\(property "Value" "([^"]+)"'
    for x,y,ref,value in re.findall(rx,source):
        x,y=float(x),float(y)
        p1=labels.get((round(x,4),round(y-5.08,4)))
        p2=labels.get((round(x,4),round(y+5.08,4)))
        if ref in caps:raise AssertionError(("duplicate capacitor",ref))
        caps[ref]=(value,p1,p2)
    sums={}
    for rail,expected in RAILS.items():
        actual={ref:v for ref,(v,up,down) in caps.items() if up==rail and down=="GND"}
        if actual!=expected:raise AssertionError(("rail inventory modified",rail,actual))
        sums[rail]=sum(capacitance_f(v) for v in actual.values())
    reg_pattern=r'\(symbol \(lib_id "S3900E:TPS7A2033_DBV_DRAFT"\) \(at ([\d.]+) ([\d.]+) 0\)[\s\S]{0,340}?\(property "Reference" "(U620[56])"'
    found={}
    for x,y,ref in re.findall(reg_pattern,source):
        x,y=float(x),float(y)
        found[ref]=(labels.get((round(x-10.16,4),round(y-10.16,4))),
                    labels.get((round(x-10.16,4),round(y,4))),
                    labels.get((round(x+10.16,4),round(y-10.16,4))))
    if found!=REGULATORS:raise AssertionError(("regulator pin nets changed",found))
    return sums

def v_cap_exp(initial_volts,tau_seconds,t_seconds):
    """Independent *hypothetical* rail trajectory, not physical LDO model."""
    if initial_volts<0 or tau_seconds<=0 or t_seconds<0:raise ValueError("invalid waveform")
    return initial_volts*math.exp(-t_seconds/tau_seconds)

def out_minus_in(t,tau_in,tau_out):
    return v_cap_exp(3.3,tau_out,t)-v_cap_exp(5.0,tau_in,t)

def violation(t,tau_in,tau_out):
    return out_minus_in(t,tau_in,tau_out)>VOUT_OVER_VIN_ABSMAX

def hypothetical_violation_window(tau_in,tau_out,step_s=0.000005,end_s=0.05):
    """Sample-only window; NOT precision timing, I_reverse or pass/fail hardware."""
    if min(tau_in,tau_out,step_s,end_s)<=0:raise ValueError("invalid time")
    n=math.ceil(end_s/step_s)
    samples=[i*step_s for i in range(n+1) if violation(i*step_s,tau_in,tau_out)]
    if not samples:return None
    return (samples[0],samples[-1])

def required_protection_signoff(input_trace=None,output_trace=None,reverse_current_trace=None):
    if any(x is None for x in (input_trace,output_trace,reverse_current_trace)):
        raise RuntimeError("HOLD: missing measured or validated coupled power-down traces")
    raise RuntimeError("HOLD: no validated model/certified protections in this test")

class TestV739OutputInputSafety(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.caps=source_capacitor_inventory()
    def test_01_input_reservoir(self):self.assertAlmostEqual(self.caps["5V_DIGITAL_FILTERED"],14.1e-6)
    def test_02_io_reservoir(self):self.assertAlmostEqual(self.caps["3V3_CODEC_IO"],1.2e-6)
    def test_03_ldoin_reservoir(self):self.assertAlmostEqual(self.caps["3V3_CODEC_LDOIN"],11.1e-6)
    def test_04_all_12_capacitors_inventory(self):self.assertEqual(sum(map(len,RAILS.values())),12)
    def test_05_tps7a20_absmax_limit(self):self.assertEqual(VOUT_OVER_VIN_ABSMAX,0.3)
    def test_06_reversed_limit(self):self.assertEqual(REVERSE_CURRENT_SHORT_A,0.015)
    def test_07_initial_rails_valid(self):self.assertAlmostEqual(out_minus_in(0,.0002,.005),-1.7)
    def test_08_fast_input_slow_output_has_hypothetical_violation(self):
        w=hypothetical_violation_window(.0002,.005)
        self.assertIsNotNone(w)
        self.assertLess(w[0],.002)
        self.assertGreater(w[1],.005)
    def test_09_identical_time_constants_never_violate(self):
        self.assertIsNone(hypothetical_violation_window(.005,.005))
    def test_10_faster_output_than_input_never_violate(self):
        self.assertIsNone(hypothetical_violation_window(.005,.0002))
    def test_11_at_1ms_large_hypothetical_overshoot(self):
        self.assertGreater(out_minus_in(.001,.0002,.005),2.5)
    def test_12_model_not_limited_to_nominal_rail_cap(self):
        self.assertGreater(self.caps["5V_DIGITAL_FILTERED"],self.caps["3V3_CODEC_LDOIN"])
    def test_13_waveform_time_positive(self):
        with self.assertRaises(ValueError):v_cap_exp(5,0,.1)
    def test_14_negative_time_fails(self):
        with self.assertRaises(ValueError):v_cap_exp(5,.01,-.01)
    def test_15_bad_sample_step_fails(self):
        with self.assertRaises(ValueError):hypothetical_violation_window(.001,.01,step_s=0)
    def test_16_no_output_violation_at_time0(self):
        self.assertFalse(violation(0,.0002,.005))
    def test_17_exponential_always_decreases(self):
        self.assertGreater(v_cap_exp(5,.001,.001),v_cap_exp(5,.001,.002))
    def test_18_signoff_refused_without_current_trace(self):
        with self.assertRaisesRegex(RuntimeError,"HOLD"):required_protection_signoff()
    def test_19_even_synthetic_traces_not_signoff(self):
        with self.assertRaisesRegex(RuntimeError,"HOLD"):required_protection_signoff([5,0],[3.3,2],[0,.01])
    def test_20_no_inference_of_reverse_current_from_vout_difference(self):
        self.assertNotEqual(out_minus_in(.001,.0002,.005),REVERSE_CURRENT_SHORT_A)

if __name__=="__main__":unittest.main()
