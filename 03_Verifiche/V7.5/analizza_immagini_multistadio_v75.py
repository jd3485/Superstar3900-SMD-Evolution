"""Deterministic mathematical spectrum snapshot of V7.5 baseband interpolation.

Tests 750Hz after FIR settles; coherent 8ms window, nominal floating point.
Does NOT emulate analog DAC zero-order hold, mixer, PA, antenna or EMI.
"""
import json
from math import cos, pi, log10
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"08_Firmware_Prototipi"/"V7.5"))
sys.path.insert(0,str(ROOT/"08_Firmware_Prototipi"/"V7.2"))
from interpolatore_multistadio_offline_v75 import ThreeStageInterpolator, FINAL_RATE_HZ
from duc_if2_offline_v72 import coherent_tone_amplitude


def analyze():
    src=lambda start,n:[0.4*cos(2*pi*750*(i+start)/48_000) for i in range(n)]
    m=ThreeStageInterpolator()
    m.process(src(0,512))
    samples=m.process(src(512,512))
    # 8 ms window: 384 audio input periods and 30,720 output samples.
    selected=[z.real for z in samples[-384*80:]]
    wanted=coherent_tone_amplitude(selected,750,fs_hz=FINAL_RATE_HZ)
    images={}
    for f in (47_250,48_750,239_250,240_750,959_250,960_750):
        amplitude=coherent_tone_amplitude(selected,f,fs_hz=FINAL_RATE_HZ)
        images[str(f)]={
            "amplitude":amplitude,
            "relative_to_750_hz_db":20*log10(max(amplitude,1e-15)/wanted)
        }
    return {
        "method":"coherent single sinusoid nominal 750Hz after startup; no RF or vendor spectrum",
        "sample_rate_hz":FINAL_RATE_HZ,
        "duration_s":len(selected)/FINAL_RATE_HZ,
        "wanted_750hz_amplitude":wanted,
        "nominal_digital_images":images,
        "rf_permission":False,
        "analog_reconstruction_not_modeled":True
    }


if __name__=="__main__":
    print(json.dumps(analyze(),indent=2,sort_keys=True))
