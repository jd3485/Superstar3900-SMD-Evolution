"""Prototipo PURAMENTE LOGICO per specifiche V1.5.1, NON firmware di trasmissione.
Non pilota PLL, audio, GPIO, rele o trasmettitore. I TX interlock sono simbolici.
"""
from dataclasses import dataclass
from enum import Enum

class Mode(str, Enum):
    AM = 'AM'
    FM = 'FM'
    USB = 'USB'
    LSB = 'LSB'
    CW = 'CW'

@dataclass(frozen=True)
class UserSettings:
    mode: Mode = Mode.FM
    channel_primary: str = 'D-20'
    channel_secondary: str = 'D-19'
    ch9: bool = False
    pa: bool = False
    dual_watch: bool = False
    vox_enabled: bool = False
    roger_beep: bool = False
    echo: bool = False
    ctcss_rx: bool = False
    ctcss_tx: bool = False
    dcs_rx: bool = False
    dcs_tx: bool = False

@dataclass(frozen=True)
class Conditions:
    ptt: bool = False
    vox_detected: bool = False
    tx_permitted: bool = False  # fail-closed; untrusted by default
    radio_safe: bool = False   # PLL lock, VSWR, temperature, etc.
    secondary_has_signal: bool = False


def effective_control(u: UserSettings, c: Conditions) -> dict:
    """Reference output for specification tests; does not actuate hardware."""
    if u.pa:
        return dict(rf_tx=False, target_tx=None, rx='PA', dual_watch=False,
                    ctcss=False, dcs=False, echo=False, roger_beep=False,
                    pa_audio_gate=bool(c.ptt or (u.vox_enabled and c.vox_detected)))
    if u.ch9:
        eligible = bool(c.tx_permitted and c.radio_safe and (c.ptt or (u.vox_enabled and c.vox_detected)))
        return dict(rf_tx=eligible, target_tx='CH9-27.065-AM' if eligible else None,
                    rx='CH9-27.065-AM', dual_watch=False,
                    ctcss=False, dcs=False, echo=False, roger_beep=False,
                    pa_audio_gate=False)
    wants_tx = bool(c.ptt or (u.vox_enabled and c.vox_detected))
    eligible = bool(wants_tx and c.tx_permitted and c.radio_safe)
    # Dual watch is a time-multiplexed receiver; while transmitting, only A is TX target.
    dw_active = bool(u.dual_watch and not eligible)
    rx = u.channel_secondary if dw_active and c.secondary_has_signal else u.channel_primary
    fm = u.mode == Mode.FM
    # CTCSS e DCS sono mutuamente esclusivi in FM per questa specifica.
    if fm and (u.ctcss_rx or u.ctcss_tx) and (u.dcs_rx or u.dcs_tx):
        raise ValueError('CTCSS e DCS non possono essere attivi simultaneamente in FM')
    return dict(rf_tx=eligible, target_tx=u.channel_primary if eligible else None,
                rx=rx, dual_watch=dw_active,
                ctcss=fm and (u.ctcss_rx or u.ctcss_tx),
                dcs=fm and (u.dcs_rx or u.dcs_tx),
                echo=bool(u.echo and u.mode in (Mode.AM, Mode.FM, Mode.USB, Mode.LSB)),
                roger_beep=bool(u.roger_beep and eligible),
                pa_audio_gate=False)
