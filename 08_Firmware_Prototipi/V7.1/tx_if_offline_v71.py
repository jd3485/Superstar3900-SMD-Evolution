"""V7.1: model-only TX IF frequency plan and single-tone waveforms.

Never writes hardware, controls GPIO, talks to a DAC or enables RF.
All mixers, LO links and output bridges are DNI/DNP in the V7.1 candidate.
"""
from math import cos, sin, pi

IF2_HZ = 455_000
LO2_HZ = 10_240_000
IF1_HZ = LO2_HZ + IF2_HZ
RF_MIN_HZ = 25_615_000
RF_MAX_HZ = 28_305_000
MODES = ("AM", "FM", "USB", "LSB", "CW")
TX_LO_LINK_FITTED = False
TX_MIXERS_FITTED = False
TX_RF_OUTPUT_LINK_FITTED = False


def rf_tx_permission(**_diagnostic_controls):
    """Unconditionally denied; no software signal can bypass missing RF links."""
    return False


def if2_frequency_for_tone(mode, audio_hz=1000):
    """IF2 spectral component. High-side LO1 reverses RF sidebands."""
    if mode not in MODES:
        raise ValueError("unknown mode")
    if not 300 <= audio_hz <= 2700:
        raise ValueError("audio tone must be within 300..2700 Hz")
    offset = {"AM": 0, "FM": 0, "USB": -audio_hz,
              "LSB": audio_hz, "CW": -700}[mode]
    return IF2_HZ + offset


def frequency_plan(rf_hz, mode, audio_hz=1000):
    """Frequency arithmetic only. LO1 is historic RX candidate, NOT TX-ready."""
    if not RF_MIN_HZ <= rf_hz <= RF_MAX_HZ:
        raise ValueError("RF frequency outside historical 270-position span")
    if2_hz = if2_frequency_for_tone(mode, audio_hz)
    lo1_hz = rf_hz + IF1_HZ
    if1_upper_hz = LO2_HZ + if2_hz
    if1_lower_hz = LO2_HZ - if2_hz
    return {
        "rf_nominal_hz": rf_hz,
        "lo1_candidate_hz": lo1_hz,
        "if2_component_hz": if2_hz,
        "if1_wanted_hz": if1_upper_hz,
        "if1_unwanted_hz": if1_lower_hz,
        "rf_difference_hz": lo1_hz - if1_upper_hz,
        "rf_image_hz": lo1_hz + if1_upper_hz,
        "tx_permitted": False,
    }


def offline_if2_samples(mode, count, sample_rate_hz=3_640_000,
                        audio_hz=1000, am_index=0.35, deviation_hz=2000,
                        cw_key_down=False):
    """Small reference-only single-tone array, not a DAC/MCU waveform driver.

    FM sign is reversed at IF2 to produce positive RF deviation after LO1.
    SSB represents one spectral component, not a full speech/IQ implementation.
    """
    if mode not in MODES:
        raise ValueError("unknown mode")
    if count < 0 or count > 100_000:
        raise ValueError("bounded offline sample count required")
    if sample_rate_hz <= 2 * (IF2_HZ + 2700):
        raise ValueError("sampling must exceed Nyquist for this reference")
    if not 300 <= audio_hz <= 2700 or not 0 <= am_index < 1:
        raise ValueError("invalid tone or AM index")
    if deviation_hz < 0 or deviation_hz > 5000:
        raise ValueError("model FM deviation limit")
    result = []
    for n in range(count):
        t = n / sample_rate_hz
        a = 2 * pi * audio_hz * t
        c = 2 * pi * IF2_HZ * t
        if mode == "AM":
            y = (1 + am_index * cos(a)) * cos(c)
        elif mode == "FM":
            y = cos(c - deviation_hz / audio_hz * sin(a))
        elif mode == "USB":
            y = cos(2 * pi * (IF2_HZ - audio_hz) * t)
        elif mode == "LSB":
            y = cos(2 * pi * (IF2_HZ + audio_hz) * t)
        else:
            y = cos(2 * pi * (IF2_HZ - 700) * t) if cw_key_down else 0.0
        result.append(y)
    return result
