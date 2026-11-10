"""V7.6 offline multitone and step-transient study of V7.5 baseband FIR.

This is a DIGITAL, double precision study at 3.84MSa/s. It does not model:
quantization to 10-bit DAC, clock jitter, DAC ZOH, analog F7401, IF2 upconversion,
mixer, RF output, phase noise, EMC or any antenna. No physical TX operation.
"""
import json
import sys
from math import cos, pi, isfinite, log10
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"08_Firmware_Prototipi"/"V7.5"))
sys.path.insert(0,str(ROOT/"08_Firmware_Prototipi"/"V7.2"))
from interpolatore_multistadio_offline_v75 import ThreeStageInterpolator
from duc_if2_offline_v72 import coherent_tone_amplitude

OUTPUT_FS = 3_840_000
AUDIO_FS = 48_000
MULTITONE_FREQS=(750,1250)
WINDOW_AUDIO=384   # 8 ms coherent for 750/1250 (6 and 10 cycles)


def _multi(start,count):
    return [0.35*cos(2*pi*750*(start+i)/AUDIO_FS) +
            0.24*cos(2*pi*1250*(start+i)/AUDIO_FS)
            for i in range(count)]


def analyze_multitone():
    fir=ThreeStageInterpolator()
    fir.process(_multi(0,512))
    # Follow-up 512 samples, after FIFO FIR initial transient.
    samples=fir.process(_multi(512,512))
    last=[x.real for x in samples[-WINDOW_AUDIO*80:]]
    wanted={}
    for f in MULTITONE_FREQS:
        wanted[str(f)]=coherent_tone_amplitude(last,f,fs_hz=OUTPUT_FS)
    images={}
    for fundamental in MULTITONE_FREQS:
        image_values={}
        for base in (48_000,240_000,960_000):
            for sign in (-1,+1):
                frequency=base+sign*fundamental
                amp=coherent_tone_amplitude(last,frequency,fs_hz=OUTPUT_FS)
                relative=20*log10(max(amp,1e-15)/wanted[str(fundamental)])
                image_values[str(frequency)]=round(relative,3)
        images[str(fundamental)]=image_values
    return {
        "type":"two coherent 750 and 1250 Hz tones, 384-input-sample window after warmup",
        "fs_hz":OUTPUT_FS,
        "wanted":wanted,
        "images_relative_db":images,
        "nominal_hardware_or_emissions_result":False,
        "tx_rf_permission":False
    }


def analyze_step():
    fir=ThreeStageInterpolator()
    before=fir.process([0]*256)
    rise=fir.process([0.4]*512)
    fall=fir.process([0]*512)
    all_samples=before+rise+fall
    if any(not isfinite(y.real) or not isfinite(y.imag) for y in all_samples):
        raise ArithmeticError("non-finite step output")
    return {
        "type":"0->0.4->0 step, causal filter, no circular boundaries",
        "samples_before":len(before),
        "samples_rise":len(rise),
        "samples_fall":len(fall),
        "rise_peak":max(y.real for y in rise),
        "rise_min":min(y.real for y in rise),
        "end_of_rise_average":sum(y.real for y in rise[-80:])/80,
        "fall_peak_abs":max(abs(y.real) for y in fall),
        "end_of_fall_average_abs":sum(abs(y.real) for y in fall[-80:])/80,
        "rf_tx_permission":False,
        "analog_emission_mask_tested":False,
    }


if __name__=="__main__":
    print(json.dumps({"multitone":analyze_multitone(),"step":analyze_step()},sort_keys=True,indent=2))
