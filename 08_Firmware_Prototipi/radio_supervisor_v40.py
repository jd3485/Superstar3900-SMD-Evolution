#!/usr/bin/env python3
"""Superstar 3900 SMD Evolution V4.0 - supervisore LOGICO puro, non firmware.

Questo esempio NON controlla la RF, non configura PLL/PA e non deve essere
collegato a un apparato TX. I segnali hardware simulati non conferiscono
alcuna conformita'. Output tx_request=True e' una sola richiesta logica,
mai un consenso definitivo di trasmissione.
"""
from dataclasses import dataclass
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "02_Piano_Frequenze"))
from frequency_plan import BAND_OFFSETS_HZ, ALPHA_CHANNELS, frequency_hz

VOICE_MODES = frozenset(("AM", "FM", "USB", "LSB"))
RX_MODES = VOICE_MODES | frozenset(("CW",))

@dataclass(frozen=True)
class Tune:
    band: str = "D"
    channel: int = 9
    alpha: bool = False
    mode: str = "AM"

@dataclass(frozen=True)
class Settings:
    primary: Tune = Tune()
    secondary: Tune = Tune(band="D", channel=19, mode="FM")
    ch9: bool = False
    pa: bool = False
    dual_watch: bool = False
    dw_slot: str = "A" # simulazione scheduler: A oppure B
    vox_enabled: bool = False
    vox_gate: bool = False # gate gia' filtrato, non audio grezzo
    ptt: bool = False
    roger_beep: bool = False
    echo: bool = False
    ctcss_rx: bool = False
    ctcss_tx: bool = False
    dcs_rx: bool = False
    dcs_tx: bool = False

@dataclass(frozen=True)
class Guards:
    # Tutto OFF per default: fail closed, anche con PTT.
    country_tx_profile_validated: bool = False
    pll_locked: bool = False
    rf_hw_interlock: bool = False
    supply_ok: bool = False
    thermal_ok: bool = False
    swr_ok: bool = False
    antenna_relay_ready: bool = False
    atu_idle: bool = False

@dataclass(frozen=True)
class Outputs:
    rx_hz: int | None
    rx_mode: str
    tx_target_hz: int | None
    tx_mode: str | None
    tx_request: bool
    pa_audio_requested: bool
    dw_effective: bool
    echo_effective: bool
    roger_beep_armed: bool
    subtones_rx_effective: bool
    subtones_tx_effective: bool
    status: str

def _valid(t: Tune) -> bool:
    return (isinstance(t, Tune) and type(t.band) is str and t.band in BAND_OFFSETS_HZ
        and type(t.channel) is int and 1 <= t.channel <= 40
        and type(t.alpha) is bool and t.mode in RX_MODES)

def _frequency(t: Tune) -> int:
    return frequency_hz(t.band, t.channel, t.alpha, False)

def _band_d_tx_position(t: Tune) -> bool:
    return t.band == "D" and not (t.alpha and t.channel in ALPHA_CHANNELS)

def supervise(s: Settings, g: Guards) -> Outputs:
    # Invalid input wins even over CH9. All RF-relevant booleans must be
    # actual bools: strings like "False" and integer 1 are NOT acceptable.
    flags = ("ch9", "pa", "dual_watch", "vox_enabled", "vox_gate", "ptt",
             "roger_beep", "echo", "ctcss_rx", "ctcss_tx", "dcs_rx", "dcs_tx")
    if (not isinstance(s, Settings) or not isinstance(g, Guards)
        or any(type(getattr(s, f)) is not bool for f in flags)
        or any(type(getattr(g, f)) is not bool for f in Guards.__dataclass_fields__)
        or not _valid(s.primary) or not _valid(s.secondary)
        or s.dw_slot not in ("A", "B")):

        return Outputs(None,"INVALID",None,None,False,False,False,False,False,False,False,"CONTROLLI NON VALIDI")
    if s.pa:
        # PA excludes RF and scan; activation of PA amplifier is a separate concept.
        return Outputs(None,"PA",None,None,False,bool(s.ptt or (s.vox_enabled and s.vox_gate)),False,False,False,False,False,"PA - RF INIBITA")
    primary_rf = 27_065_000 if s.ch9 else _frequency(s.primary)
    primary_mode = "AM" if s.ch9 else s.primary.mode
    # In CH9 subtoni bypassati: un conflitto di configurazione FM memorizzato
    # non deve alterare la frequenza forzata ne' le priorita' CH9.
    if not s.ch9 and ((s.ctcss_rx and s.dcs_rx) or (s.ctcss_tx and s.dcs_tx)):
        return Outputs(primary_rf, primary_mode, None, None, False, False, False, False, False, False, False,"CTCSS/DCS IN CONFLITTO")
    dw = bool(s.dual_watch and not s.ch9)
    use_secondary = bool(dw and s.dw_slot == "B" and not (s.ptt or (s.vox_enabled and s.vox_gate)))
    rx_rf = _frequency(s.secondary) if use_secondary else primary_rf
    rx_mode = s.secondary.mode if use_secondary else primary_mode
    request = bool(s.ptt or (s.vox_enabled and s.vox_gate))
    tx_position_ok = bool(s.ch9 or _band_d_tx_position(s.primary))
    tx_mode_ok = primary_mode in VOICE_MODES
    all_guards = all((g.country_tx_profile_validated,g.pll_locked,g.rf_hw_interlock,
       g.supply_ok,g.thermal_ok,g.swr_ok,g.antenna_relay_ready,g.atu_idle))
    tx = bool(request and tx_position_ok and tx_mode_ok and all_guards)
    if request and not tx:
        reason = "TX BLOCCATA: PROFILO/MODO/POSIZIONE/PROTEZIONI"
    else:
        reason = "SIMULAZIONE: RICHIESTA TX" if tx else "RX"
    # CH9 bypasses extras; FM subtones only and mutually exclusive checked above.
    sub_rx = bool(not s.ch9 and rx_mode == "FM" and (s.ctcss_rx or s.dcs_rx))
    sub_tx = bool(tx and not s.ch9 and primary_mode == "FM" and (s.ctcss_tx or s.dcs_tx))
    return Outputs(rx_rf,rx_mode,primary_rf if tx else None,primary_mode if tx else None,
       tx,False,dw, bool(s.echo and not s.ch9 and primary_mode in VOICE_MODES),
       bool(s.roger_beep and tx and not s.ch9),sub_rx,sub_tx,reason)
