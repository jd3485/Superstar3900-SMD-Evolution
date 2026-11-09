"""Prototype of SSB/CW post-detector fixed-point audio FIR filters, 48ksps. NOT a STM32 HAL/SAI integration."""
from pathlib import Path
import numpy as np
from scipy import signal
FS=48000
SPEC={"SSB":((300,2700),241,7.5),"CW":((450,950),481,7.8)}
def design(mode):
    band,n,beta=SPEC[mode]
    return signal.firwin(n,band,fs=FS,pass_zero=False,window=('kaiser',beta))
def q15(mode):
    return np.clip(np.rint(design(mode)*32768),-32768,32767).astype(np.int16)
def apply_q15(x,mode):
    """Floating re-expression of 64-bit accumulated signed Q15 MAC; model, not MCU implementation."""
    b=q15(mode).astype(np.float64)/32768
    return signal.lfilter(b,[1],np.asarray(x,dtype=np.float64))
def log_am_linearize(v,dc_level=1.4,slope_v_per_db=0.025):
    """AD8307 nominal inverse logarithmic amplitude transfer. Needs real calibration and guard clipping."""
    dv=np.clip(np.asarray(v)-dc_level,-1.2,+1.2)
    return np.power(10.0,dv/(20*slope_v_per_db))
def mute_condition(mode,rx_good,pa,ptt,retune,ref_ok,hardware_consent):
    return not (mode in ('AM','FM','USB','LSB','CW') and rx_good and not pa and not ptt and not retune and ref_ok and hardware_consent)
def tx_permission(*args,**kwargs):return False
if __name__=='__main__':
    for mode in SPEC:
        print(mode,len(q15(mode)),sum(abs(q15(mode).astype(int))))
