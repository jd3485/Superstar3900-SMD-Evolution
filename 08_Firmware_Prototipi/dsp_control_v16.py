"""Modello software V1.6, non firmware MCU e NON controlla hardware/RF.
Valida matematicamente il rilevamento toni CTCSS e una logica VOX / DW.
Python+numpy; il porting CMSIS-DSP/STM32 richiede profilo CPU/clock/DMA.
"""
from dataclasses import dataclass
from functools import lru_cache
import math
import numpy as np

# Set completo di frequenze dal riferimento citato in Architettura_MCU_CODEC_V1.6.md
CTCSS_50 = (67.0,69.3,71.9,74.4,77.0,79.7,82.5,85.4,88.5,91.5,
            94.8,97.4,100.0,103.5,107.2,110.9,114.8,118.8,123.0,127.3,
            131.8,136.5,141.3,146.2,151.4,156.7,159.8,162.2,165.5,167.9,
            171.3,173.8,177.3,179.9,183.5,186.2,189.9,192.8,196.6,199.5,
            203.5,206.5,210.7,218.1,225.7,229.1,233.6,241.8,250.3,254.1)

@lru_cache(maxsize=2)
def _tone_basis(fs: int, n: int):
    t = np.arange(n, dtype=np.float64) / fs
    hann = np.hanning(n)
    return np.exp(-2j*np.pi*np.asarray(CTCSS_50)[:,None]*t[None,:])*hann[None,:], float(hann.sum())

def detect_ctcss(samples, fs=8000, min_amplitude=0.025, margin_ratio=1.5):
    """Demo demod. Ingresso: segnale FM demodulato, non audio passa-alto.
    Finestra esatta 800 ms @8ksps. Ritorna tono o None, non apre squelch.
    Richiede filtri anti-alias prima della riduzione da 48 ksps.
    """
    s=np.asarray(samples, dtype=np.float64)
    if fs!=8000 or len(s)!=6400:
        raise ValueError('La demo richiede 6400 campioni @8 kHz')
    basis, norm=_tone_basis(fs,len(s))
    ampl=2*np.abs(basis @ s)/norm
    order=np.argsort(ampl)
    best=int(order[-1]); second=int(order[-2])
    if ampl[best]<min_amplitude or ampl[best]/max(ampl[second],1e-12)<margin_ratio:
        return None
    return CTCSS_50[best]

@dataclass
class VoxGate:
    attack_ms: int=30
    hang_ms: int=450
    high_dbfs: float=-30.0
    low_dbfs: float=-38.0
    frame_ms: int=10
    active: bool=False
    _attack_counter: int=0
    _hang_counter: int=0

    def update(self, microphone_rms: float, *, speaker_audio_active=False, pa_mode=False):
        """Gating logico; speaker_audio_active blocca nuovi attacchi VOX.
        L'interblocco TX reale e separato e di tipo fail-closed.
        """
        if pa_mode: # PA gestita da una catena indipendente; NO RF
            self.active=False;self._attack_counter=0;self._hang_counter=0
            return False
        db=20*math.log10(max(float(microphone_rms),1e-12))
        hi=math.ceil(self.attack_ms/self.frame_ms)
        hang=math.ceil(self.hang_ms/self.frame_ms)
        if self.active:
            if db>=self.low_dbfs:
                self._hang_counter=hang
            else:
                self._hang_counter=max(self._hang_counter-1,0)
                if self._hang_counter==0:
                    self.active=False
        elif (not speaker_audio_active) and db>=self.high_dbfs:
            self._attack_counter+=1
            if self._attack_counter>=hi:
                self.active=True; self._hang_counter=hang;self._attack_counter=0
        else:
            self._attack_counter=0
        return self.active

@dataclass
class DualWatch:
    """Sequenza A/B per un ricevitore singolo; non controlla PLL fisico.
    Questo scheduler non verifica lock time: richiede feedback hardware.
    """
    dwell_ms: int=500
    hold_ms: int=1200
    elapsed_ms: int=0
    hold_elapsed_ms: int=0
    slot: str='A'

    def update(self, dt_ms, *, enabled, signal_valid=False, tx=False, ch9=False, pa=False):
        if tx or ch9 or pa or not enabled:
            self.slot='A';self.elapsed_ms=0;self.hold_elapsed_ms=0
            return 'CH9' if ch9 else ('PA' if pa else 'A')
        if signal_valid:
            self.hold_elapsed_ms=self.hold_ms
        if self.hold_elapsed_ms>0:
            self.hold_elapsed_ms=max(0,self.hold_elapsed_ms-dt_ms)
            return self.slot
        self.elapsed_ms+=dt_ms
        if self.elapsed_ms>=self.dwell_ms:
            self.elapsed_ms%=self.dwell_ms
            self.slot='B' if self.slot=='A' else 'A'
        return self.slot
