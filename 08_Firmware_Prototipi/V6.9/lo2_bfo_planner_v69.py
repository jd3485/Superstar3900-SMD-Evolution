#!/usr/bin/env python3
"""RX-only reference-frequency arithmetic and fail-closed state.

NOT silicon-register programming, production firmware, or clock-quality proof.
"""
from dataclasses import dataclass
from fractions import Fraction

REF_HZ=12_800_000
PLL_VCO_HZ=800_000_000
MODE_FREQS={
  'AM': (10_240_000, None),
  'FM': (10_240_000, None),
  'USB':(10_238_500, 456_500),
  'LSB':(10_241_500, 453_500),
  'CW': (10_240_000, 455_700),
}
IF1_HZ=10_695_000
IF2_HZ=455_000
MAX_DEN=1_048_575

@dataclass(frozen=True)
class Ratio:
    freq_hz:int
    vco_hz:int
    r_div:int
    n_int:int
    n_num:int
    n_den:int
    actual_hz:Fraction
    @property
    def error_hz(self):return self.actual_hz-self.freq_hz


def ratio(freq_hz:int, r_div:int=1, vco_hz:int=PLL_VCO_HZ)->Ratio:
    """Exact rational fit of nominal divider, not guaranteed silicon/register behavior."""
    if not (8_000<=freq_hz<=200_000_000 and 600_000_000<=vco_hz<=900_000_000):
        raise ValueError('out-of-range study request')
    if r_div not in (1,2,4,8,16,32,64,128):raise ValueError('invalid R div')
    div=Fraction(vco_hz, freq_hz*r_div)
    if not (6<=div<=1800): raise ValueError('MultiSynth ratio out of study range')
    fitted=div.limit_denominator(MAX_DEN)
    n_int=fitted.numerator//fitted.denominator
    n_num=fitted.numerator % fitted.denominator
    actual=Fraction(vco_hz*fitted.denominator,(n_int*fitted.denominator+n_num)*r_div)
    return Ratio(freq_hz,vco_hz,r_div,n_int,n_num,fitted.denominator,actual)


def plan(mode:str):
    if mode not in MODE_FREQS: raise ValueError('unknown mode: fail closed')
    lo2,bfo=MODE_FREQS[mode]
    lo2_ratio=ratio(lo2)
    bfo_ratio=ratio(bfo,16) if bfo is not None else None
    return {'mode':mode,'lo2_hz':lo2,'bfo_hz':bfo,'lo2_ratio':lo2_ratio,'bfo_ratio':bfo_ratio}

@dataclass(frozen=True)
class RxInputs:
    rx_switch_closed:bool=False
    pa_selected:bool=True
    ptt_active:bool=False
    supply_good:bool=False
    pll1_lock:bool=False
    lo2_pll_status_ok:bool=False
    lo2_config_committed:bool=False
    filter_ready:bool=False
    mode_valid:bool=False
    retune_in_progress:bool=True
    ref_clock_present:bool=False
    hardware_rx_consent:bool=False


def permit_audio(x:RxInputs)->bool:
    return (x.rx_switch_closed and not x.pa_selected and not x.ptt_active
      and x.supply_good and x.pll1_lock and x.lo2_pll_status_ok
      and x.lo2_config_committed and x.filter_ready and x.mode_valid
      and not x.retune_in_progress and x.ref_clock_present
      and x.hardware_rx_consent)


def lo2_request(x:RxInputs)->bool:
    """Requested CLOCK enable, with independent hardware gating to design later."""
    return permit_audio(x)


def tx_authorized(_x:RxInputs)->bool:
    """No RF transmission possible in this RX-only reference model."""
    return False

if __name__=='__main__':
    for m in MODE_FREQS:
        p=plan(m);print(m,p['lo2_ratio'],p['bfo_ratio'])
