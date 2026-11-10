"""V7.7 DAC 10-bit quantization and external interlock HAZARD study.

Reference-only; imports V7.5 floating-point baseband FIR. Does not touch
DAC900, FPGA, GPIO, PA, RF or antenna. No real-time firmware or analogue model.
The independent supervisor is NOT an electrical schematic or certified control.
"""
from math import cos, pi, sqrt, log10, isfinite
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"08_Firmware_Prototipi"/"V7.5"))
sys.path.insert(0,str(ROOT/"08_Firmware_Prototipi"/"V7.3"))
from interpolatore_multistadio_offline_v75 import ThreeStageInterpolator
from duc_if2_causale_v73 import quantize_unsigned_10bit

AUDIO_FS=48_000
OUTPUT_FS=3_840_000
HEADROOM=0.70
HARDWARE_PRESENT=False
RF_CONNECTION_PRESENT=False
SUPERVISOR_ELECTRICAL_SCHEMATIC_VERIFIED=False
PHYSICAL_DAC_PD_CONTROLLED=False
SINGLE_FAULT_PROTECTION_VALIDATED=False

HAZARDS=(
  "DAC_PD_FLOATS_LOW",
  "DAC_PD_STUCK_LOW",
  "SUPERVISOR_OPEN",
  "SUPERVISOR_SHORT",
  "CLOCK_STOPS",
  "CLOCK_GLITCHES",
  "FPGA_CONFIG_UNDEFINED",
  "FPGA_RAIL_BROWNOUT",
  "DAC_RAIL_BACKFEED",
  "PA_ISOLATOR_WELDED",
  "TX_RELAY_SHORT",
  "INDEPENDENT_CLOCK_WATCHDOG_FAILS"
)


def tx_permission(**_):
    return False


def study_hazard(name):
    if name not in HAZARDS:
        raise ValueError("unknown fault family")
    # Flag each one as an open design requirement rather than asserting
    # the logical model guarantees an analogue path is safe.
    return {
      "hazard":name,
      "independent_pd_assertion_required":True,
      "independent_rf_open_circuit_required":True,
      "hardware_fault_tolerant":False,
      "electrical_qualification_status":"NOT_RUN",
      "rf_permission":False
    }


def _audio_block(start,n):
    return [
      0.35*cos(2*pi*750*(start+i)/AUDIO_FS)
      +0.24*cos(2*pi*1250*(start+i)/AUDIO_FS)
      for i in range(n)
    ]


def _rms(values):
    if not values:
        raise ValueError("empty RMS input")
    return sqrt(sum(v*v for v in values)/len(values))


def decode_codes(codes, headroom=HEADROOM):
    if not isfinite(headroom) or headroom<=0 or headroom>1:
        raise ValueError("invalid normalization")
    return [(2*int(c)/1023-1)/headroom for c in codes]


def analyze_quantized_multitone():
    """Warmup then coherent 8ms analysis, 10-bit uniform numeric quantization.

    The reconstruction here is mathematical; it is NOT DAC900 SFDR, SNR or
    anti-imaging. Overshoot/headroom remains separately tested.
    """
    interp=ThreeStageInterpolator()
    interp.process(_audio_block(0,512))
    full=[z.real for z in interp.process(_audio_block(512,512))]
    samples=full[-384*80:]
    codes=quantize_unsigned_10bit(samples,headroom=HEADROOM)
    reconstructed=decode_codes(codes,headroom=HEADROOM)
    errors=[r-v for r,v in zip(reconstructed,samples)]
    ref_rms=_rms(samples)
    error_rms=_rms(errors)
    return {
      "sample_count":len(samples),
      "window_s":len(samples)/OUTPUT_FS,
      "audio_tones_hz":[750,1250],
      "headroom":HEADROOM,
      "peak_abs_input":max(abs(v) for v in samples),
      "code_min":min(codes),
      "code_max":max(codes),
      "error_rms":error_rms,
      "reference_rms":ref_rms,
      "quantization_snr_db":20*log10(ref_rms/max(error_rms,1e-15)),
      "numerical_quantization_only":True,
      "rf_permission":False
    }


def analyze_quantized_step():
    interp=ThreeStageInterpolator()
    interp.process([0.0]*256)
    rise=[z.real for z in interp.process([0.4]*512)]
    fall=[z.real for z in interp.process([0.0]*512)]
    peak=max(rise)
    codes=quantize_unsigned_10bit(rise+fall,headroom=HEADROOM)
    return {
      "step_level":0.4,
      "peak":peak,
      "overshoot_percent":100*(peak/0.4-1),
      "peak_code":max(codes),
      "min_code":min(codes),
      "headroom":HEADROOM,
      "codes_do_not_represent_real_dac_io":True,
      "rf_permission":False
    }


if __name__=="__main__":
    import json
    print(json.dumps({
      "multitone":analyze_quantized_multitone(),
      "step":analyze_quantized_step(),
      "hazards":[study_hazard(v) for v in HAZARDS]
    },indent=2,sort_keys=True))
