#!/usr/bin/env python3
"""V5.9 audio route reference: logical design, no GPIO, no real TX authorization."""
from dataclasses import dataclass
from enum import Enum

class RxMode(str, Enum):
    AM = 'AM'
    FM = 'FM'
    USB = 'USB'
    LSB = 'LSB'
    CW = 'CW'

class Speaker(str, Enum):
    RADIO = 'RADIO_SPEAKER'
    PA = 'PA_EXTERNAL'
    MUTED = 'MUTED'

@dataclass(frozen=True)
class RouteInputs:
    rx_mode: RxMode
    pa_mode: bool = False
    ch9_override: bool = False
    tx_request: bool = False
    power_good: bool = True
    transition_mute: bool = False

@dataclass(frozen=True)
class AudioRoute:
    codec_adc_l: str
    codec_adc_r: str
    selected_demod: str
    codec_dac_l: str
    codec_dac_r: str
    speaker: Speaker
    rf_tx_permission: bool
    tx_modulator_muted: bool
    explanation: str


def route_audio(s: RouteInputs) -> AudioRoute:
    """Fail-closed audio router. RF TX permission is *never* generated here."""
    if not isinstance(s.rx_mode, RxMode):
        raise ValueError('Invalid RX mode')
    source = 'AM' if s.ch9_override else s.rx_mode.value
    base = dict(codec_adc_l='MIC', codec_adc_r='RX_DEMOD',
                selected_demod=source, rf_tx_permission=False,
                tx_modulator_muted=True)
    if not s.power_good or s.transition_mute:
        return AudioRoute(**base, codec_dac_l='MUTE',codec_dac_r='MUTE',
                          speaker=Speaker.MUTED,explanation='Power/transition mute')
    if s.pa_mode:
        return AudioRoute(**base, codec_dac_l='MIC_MONITOR',codec_dac_r='MUTE',
                          speaker=Speaker.PA,explanation='PA is audio-only; hardware RF inhibited')
    if s.tx_request:
        # Signal is handled by supervisor + independent hardware gate, not this module.
        return AudioRoute(**base, codec_dac_l='MUTE',codec_dac_r='MUTE',
                          speaker=Speaker.MUTED,explanation='Unqualified TX: no audio into modulator')
    return AudioRoute(**base, codec_dac_l='RX_AUDIO',codec_dac_r='MUTE',
                      speaker=Speaker.RADIO,explanation='Receive/listen')
