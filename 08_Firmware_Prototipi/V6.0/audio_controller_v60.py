#!/usr/bin/env python3
"""V6.0 AUDIO/PA functional controller, no hardware GPIO, no RF enable generation."""
from dataclasses import dataclass
from enum import Enum

class RxMode(str, Enum):
    AM='AM'; FM='FM'; USB='USB'; LSB='LSB'; CW='CW'

MUX_CODES = {RxMode.AM:0, RxMode.FM:1, RxMode.USB:2, RxMode.LSB:3, RxMode.CW:4}

@dataclass(frozen=True)
class Inputs:
    rx_mode: RxMode
    pa_mode_hw: bool=False
    pa_ptt_pressed: bool=False
    ch9: bool=False
    tx_requested: bool=False
    power_good: bool=True
    codec_ready: bool=True
    relay_settled: bool=True
    transition: bool=False
    amp_fault: bool=False
    hw_amp_arm: bool=True

@dataclass(frozen=True)
class Outputs:
    mode: str
    mux_code: int
    mux_enable_n: int
    adc_left: str
    adc_right: str
    dac_left: str
    dac_right: str
    relay_pa: bool
    amp_sd: int
    pa_audio_audible: bool
    rf_tx_permission: bool
    reason: str


def control(x: Inputs) -> Outputs:
    if not isinstance(x.rx_mode, RxMode): raise ValueError('Unknown mode')
    source = RxMode.AM if x.ch9 else x.rx_mode
    base=dict(adc_left='MIC',adc_right='RX',dac_right='MUTE',rf_tx_permission=False)
    safe = x.power_good and x.codec_ready and x.relay_settled and (not x.transition) and (not x.amp_fault) and x.hw_amp_arm
    if not safe:
        return Outputs(mode='FAULT_OR_SETTLE',mux_code=MUX_CODES[source],mux_enable_n=1,
            dac_left='MUTE',relay_pa=x.pa_mode_hw,amp_sd=0,pa_audio_audible=False,
            reason='Fail closed on power/codec/relay/fault/transition/arm',**base)
    if x.pa_mode_hw:
        # Physical PA switch must *also* inhibit RF through independent hardware.
        return Outputs(mode='PA',mux_code=MUX_CODES[source],mux_enable_n=1,
            dac_left='MIC' if x.pa_ptt_pressed else 'MUTE',relay_pa=True,
            amp_sd=1 if x.pa_ptt_pressed else 0,pa_audio_audible=x.pa_ptt_pressed,
            reason='PA mode; PTT is audio-only; RF never permitted',**base)
    if x.tx_requested:
        return Outputs(mode='UNQUALIFIED_TX',mux_code=MUX_CODES[source],mux_enable_n=1,
            dac_left='MUTE',relay_pa=False,amp_sd=0,pa_audio_audible=False,
            reason='TX certification and hardware gate absent',**base)
    return Outputs(mode='RX',mux_code=MUX_CODES[source],mux_enable_n=0,
        dac_left='RX',relay_pa=False,amp_sd=1,pa_audio_audible=False,
        reason='Receive audio',**base)
