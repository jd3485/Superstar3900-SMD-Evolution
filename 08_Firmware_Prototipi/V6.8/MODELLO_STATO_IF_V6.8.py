"""Fail closed: software model of RX IF state (not a TX control)."""
from dataclasses import dataclass
VALID_MODES = {'AM','FM','USB','LSB','CW'}
LO2_HZ={'AM':10_240_000,'FM':10_240_000,'USB':10_238_500,'LSB':10_241_500,'CW':10_240_000}
BFO_HZ={'AM':None,'FM':None,'USB':456_500,'LSB':453_500,'CW':455_700}
@dataclass(frozen=True)
class IFState:
    mode:str
    power_good:bool
    pll1_lock:bool
    lo2_ready:bool
    filter_ready:bool
    pa_active:bool
    retune:bool
    hardware_fault:bool
    ptt:bool

def resolve(s:IFState):
    valid=s.mode in VALID_MODES
    rx_ok=all((valid,s.power_good,s.pll1_lock,s.lo2_ready,s.filter_ready,
               not s.pa_active,not s.retune,not s.hardware_fault,not s.ptt))
    return {'rx_audio_unmute':bool(rx_ok),'if_filter_select':s.mode if rx_ok else 'NONE',
            'lo2_hz':LO2_HZ[s.mode] if valid else None,
            'bfo_hz':BFO_HZ[s.mode] if valid else None,
            'tx_permission':False}
