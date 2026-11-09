"""Superstar3900 V6.1 control panel: prototype state model, NOT MCU firmware/real GPIO.
Source of truth for frequencies: relative ../../02_Piano_Frequenze/Tabella_270_canali.csv.
No software pathway enables TX; all TX gating is deferred to validated hardware.
"""
from dataclasses import dataclass
from pathlib import Path
import csv
BANDS='ABCDEF'
MODES=('AM','FM','USB','LSB','CW')
ALPHA=('3A','7A','11A','15A','19A')
CH9_FREQ_HZ=27_065_000

def load_frequency_table(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f,delimiter=';'))
    lut={}
    for r in rows:
        key=(r['Banda'],r['Canale'])
        if key in lut:raise ValueError('Frequency duplicate '+str(key))
        if r['TX_preliminarmente_consentita'] not in ('SI','NO'):raise ValueError('Unknown historic preliminary TX flag (not permission)')
        lut[key]=int(r['Frequenza_Hz'])
    for band in BANDS:
        for ch in tuple(str(n) for n in range(1,41))+ALPHA:
            if (band,ch) not in lut:raise ValueError('Frequency table incomplete: '+str((band,ch)))
    if len(lut)!=270 or lut[('D','9')]!=CH9_FREQ_HZ:
        raise ValueError('Unapproved CH9 or channel plan')
    return lut

@dataclass(frozen=True)
class Inputs:
    bands:tuple=('D',)
    modes:tuple=('AM',)
    alfa:bool=False
    ch9:bool=False
    pa:bool=False
    ptt:bool=False
    i2c_ok:bool=True
    power_good:bool=True
    codec_ready:bool=True

@dataclass(frozen=True)
class View:
    state:str
    band:str
    channel:str
    mode:str
    frequency_hz:int|None
    rx_mute:bool
    pa_speaker:bool
    pa_mic_audible:bool
    mux_code:int|None
    mux_en_n:int
    rf_tx_permission:bool=False

class DebouncedChoice:
    """For slow rotary one-hot switches sampled every 5ms, 20ms stable required."""
    def __init__(self, choices):
        self.choices=tuple(choices);self.candidate=None;self.count=0;self.stable=None
    def sample(self, active):
        if len(active)!=1 or active[0] not in self.choices:
            self.candidate=None;self.count=0;return None
        if active[0]!=self.candidate:
            self.candidate=active[0];self.count=1
        else:self.count+=1
        if self.count>=4:self.stable=self.candidate
        return self.stable if self.stable==self.candidate else None

class Quadrature:
    """One sample per ms, 2 consecutive identical samples to accept a Gray edge.
    Sequence 00→01→11→10→00 = +1 detent; reverse = -1.
    Not proven for a real encoder, must be tested with measured bounce and speed.
    """
    transitions={(0,1):1,(1,3):1,(3,2):1,(2,0):1,
                 (1,0):-1,(3,1):-1,(2,3):-1,(0,2):-1}
    def __init__(self):
        self.sample_raw=0;self.streak=0;self.filtered=0;self.quarters=0
    def feed(self,ab):
        if ab not in range(4):return 0
        if ab==self.sample_raw:self.streak+=1
        else:self.sample_raw=ab;self.streak=1
        if self.streak<2 or ab==self.filtered:return 0
        prev=self.filtered;self.filtered=ab
        delta=self.transitions.get((prev,ab),0)
        if delta==0:self.quarters=0;return 0
        # Require uninterrupted 4-step sequence of one direction.
        if self.quarters and delta*self.quarters<0:self.quarters=delta
        else:self.quarters+=delta
        if abs(self.quarters)==4:
            out=1 if self.quarters>0 else -1
            self.quarters=0
            return out
        return 0

class Controller:
    def __init__(self, table):
        self.table=table;self.band_choice=DebouncedChoice(BANDS);self.mode_choice=DebouncedChoice(MODES)
        self.normal={b:1 for b in BANDS};self.alpha={b:0 for b in BANDS}
        self.last_input=None;self.last_stable_band=None;self.last_alfa=False
    def step_channel(self, delta:int):
        x=self.last_input
        if x is None or x.pa or x.ch9 or (not x.i2c_ok) or self.last_stable_band is None:return
        b=self.last_stable_band
        if x.alfa:self.alpha[b]=(self.alpha[b]+delta)%5
        else:self.normal[b]=((self.normal[b]-1+delta)%40)+1
    def update(self,x:Inputs):
        self.last_input=x
        band=self.band_choice.sample(x.bands) if x.i2c_ok else None
        mode=self.mode_choice.sample(x.modes) if x.i2c_ok else None
        self.last_stable_band=band
        # Direct PA pole has top priority, independent of I2C readiness.
        if x.pa:
            audible=bool(x.ptt and x.codec_ready and x.power_good)
            return View('PA','—','—','PA',None,True,True,audible,None,1,False)
        # Direct CH9 overrides band/mode and I2C: user cannot lose emergency RX
        # simply because the panel expander is offline; RF TX remains disabled.
        if x.ch9:
            ready=x.power_good and x.codec_ready
            return View('CH9','D','9','AM',CH9_FREQ_HZ,not ready,False,False,0,0 if ready else 1,False)
        ready=x.power_good and x.codec_ready and x.i2c_ok
        if not ready or band is None or mode is None:
            return View('SAFE_MUTE','—','—','—',None,True,False,False,None,1,False)
        ch=ALPHA[self.alpha[band]] if x.alfa else str(self.normal[band])
        return View('RX_ALPHA' if x.alfa else 'RX_NORMAL',band,ch,mode,self.table[(band,ch)],False,False,False,MODES.index(mode),0,False)

def default_table_path():
    return Path(__file__).resolve().parents[2]/'02_Piano_Frequenze'/'Tabella_270_canali.csv'
