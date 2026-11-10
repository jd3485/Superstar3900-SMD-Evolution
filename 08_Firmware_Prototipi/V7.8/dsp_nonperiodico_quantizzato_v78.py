"""V7.8 bounded nonperiodic DSP / 10-bit ideal quantization diagnostic.

Pure numerical software. There is no physical DAC, anti-imaging filter, IF
mixer, PA, antenna, RF path or electrical TX gate. No regulatory mask.
"""
import math
import random
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"08_Firmware_Prototipi"/"V7.5"))
sys.path.insert(0,str(ROOT/"08_Firmware_Prototipi"/"V7.3"))
from interpolatore_multistadio_offline_v75 import ThreeStageInterpolator
from duc_if2_causale_v73 import quantize_unsigned_10bit

AUDIO_FS=48_000
OUTPUT_FS=3_840_000
HEADROOM=0.70
HARDWARE_PRESENT=False
RF_PERMISSION=False
ANALOG_FILTER_MEASURED=False


def tx_permission(**_):
    return False


def bounded_nonperiodic_audio(n=384,seed=78):
    if type(n) is not int or not 64<=n<=512:
        raise ValueError("bounded audio length required")
    generator=random.Random(seed)
    return [0.28*math.sin(2*math.pi*375*i/AUDIO_FS) +
            0.18*math.sin(2*math.pi*1730*i/AUDIO_FS) +
            0.12*(2*generator.random()-1)
            for i in range(n)]


def error_stats(values, codes, headroom=HEADROOM):
    if len(values)!=len(codes) or not values:
        raise ValueError("aligned non-empty data required")
    recon=[(2*code/1023-1)/headroom for code in codes]
    errors=[a-b for a,b in zip(recon,values)]
    sig2=sum(a*a for a in values)/len(values)
    err2=sum(a*a for a in errors)/len(errors)
    return {
       "quantization_noise_rms":math.sqrt(err2),
       "signal_rms":math.sqrt(sig2),
       "numerical_signal_to_error_db":10*math.log10(max(sig2,1e-24)/max(err2,1e-24)),
       "physical_DAC_SFDR_measured":False
    }


def analyze():
    model=ThreeStageInterpolator()
    audio=bounded_nonperiodic_audio()
    # Compare the deterministic nonperiodic signal in one block to uneven
    # chunks: the sample arrays must be identical, regardless of segmentation.
    one=[z.real for z in model.process(audio)]
    state=ThreeStageInterpolator()
    parts=[audio[:3],audio[3:31],audio[31:139],audio[139:257],audio[257:]]
    split=[]
    for chunk in parts:
        split.extend(z.real for z in state.process(chunk))
    if one!=split:
        raise ArithmeticError("streaming output depends on block boundaries")
    codes=quantize_unsigned_10bit(one,headroom=HEADROOM)
    return {
       "audio_samples":len(audio),
       "if2_baseband_samples":len(one),
       "output_rate_hz":OUTPUT_FS,
       "chunk_invariance":True,
       "max_abs_float_sample":max(map(abs,one)),
       "max_code":max(codes),
       "min_code":min(codes),
       "headroom":HEADROOM,
       "ideal_quantization":error_stats(one,codes),
       "rf_permission":False,
       "hardware_implemented":False
    }


def check_loud_step_rejection(step_value=1.0):
    """Quantizer must raise for a super-unity FILTERED step, not saturate."""
    if not math.isfinite(step_value) or not 0<step_value<=1.2:
        raise ValueError("bounded step input")
    model=ThreeStageInterpolator()
    model.process([0.0]*64)
    y=[z.real for z in model.process([step_value]*96)]
    peak=max(y)
    quantization_accepted=True
    try:
        quantize_unsigned_10bit(y,headroom=HEADROOM)
    except ValueError:
        quantization_accepted=False
    return {
        "step":step_value,
        "filtered_peak":peak,
        "quantization_accepted":quantization_accepted,
        "if_overrange_fail_closed":not quantization_accepted,
        "rf_permission":False
    }


if __name__=="__main__":
    import json
    print(json.dumps({"nonperiodic":analyze(),"loud_step":check_loud_step_rejection()},
                     indent=2,sort_keys=True))
