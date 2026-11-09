"""Modello di comportamento UI/PTT da collaudare; NON e' firmware operativo.

Interlock fisico, protezioni analogiche, switch RF e temporizzazioni NON implementati.
La proprieta' hw_interlock e' una simulazione di consenso da elettronica dedicata.
"""
from dataclasses import dataclass
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'02_Piano_Frequenze'))
from frequency_plan import BAND_OFFSETS_HZ, frequency_hz, tx_allowed

MODES={'AM','FM','USB','LSB'}

@dataclass(frozen=True)
class Controls:
    band: str='D'
    channel: int=9
    alpha: bool=False
    ch9: bool=False
    mode: str='AM'
    ptt: bool=False

@dataclass(frozen=True)
class Health:
    pll_locked: bool=False
    hw_interlock: bool=False
    supply_ok: bool=False
    temperature_ok: bool=False
    swr_ok: bool=False
    antenna_relay_settled: bool=False
    atu_busy: bool=False

@dataclass(frozen=True)
class Result:
    rf_hz: int | None
    mode: str
    tx_enabled: bool
    warning: str

def evaluate(c: Controls, h: Health) -> Result:
    # Controlli invalidi: TX disattivato, anche CH9 prioritario.
    valid = c.band in BAND_OFFSETS_HZ and type(c.channel)==int and 1 <= c.channel <=40 and c.mode in MODES
    if not valid:
        return Result(None, 'AM', False, 'Comandi invalidi: TX inibita')
    rf = frequency_hz(c.band,c.channel,c.alpha,c.ch9)
    mode = 'AM' if c.ch9 else c.mode
    legal = tx_allowed(c.band,c.channel,c.alpha,c.ch9)
    ready = (h.pll_locked and h.hw_interlock and h.supply_ok and h.temperature_ok and
             h.swr_ok and h.antenna_relay_settled and not h.atu_busy)
    enabled = bool(c.ptt and legal and ready)
    if c.ptt and not enabled:
        why='Posizione TX non autorizzata' if not legal else 'Interblocco/protezione attiva'
    else:
        why=''
    return Result(rf,mode,enabled,why)
