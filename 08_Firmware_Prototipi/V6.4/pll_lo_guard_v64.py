"""Supervisione PLL RX simulata, MAI controllo reale di hardware e MAI TX.

Nessun profilo LMX2572 o parola registro viene generata. I 24-bit frames
sono gia gestiti dal modulo precedente, che accetta solo profili validati esternamente.
"""
from dataclasses import dataclass
from enum import Enum


class State(str, Enum):
    OFF = 'OFF'
    SETTLING = 'SETTLING'
    WAIT_PROFILE = 'WAIT_PROFILE'
    WAIT_LOCK = 'WAIT_LOCK'
    RX_READY = 'RX_READY'
    FAULT = 'FAULT'


@dataclass(frozen=True)
class Pins:
    ce: bool
    audio_rx_unmuted: bool
    tx_enable: bool = False


class RxPllGuard:
    """Invariante: RF TX disattivata in ogni stato e dopo ogni transizione."""
    def __init__(self, settle_ms=1.0, lock_dwell_ms=3.0):
        if settle_ms < 0.5 or lock_dwell_ms < 0:
            raise ValueError('tempi non ammissibili')
        self.settle_ms = float(settle_ms)
        self.lock_dwell_ms = float(lock_dwell_ms)
        self.state = State.OFF
        self.entered_ms = 0.0
        self.lock_seen_ms = None
        self.last_ms = None

    def step(self, now_ms, *, request, power_good, ref_good, profile_loaded=False,
             lock_detect=False, pa_active=False, retune_request=False, fault=False):
        if not isinstance(now_ms,(int,float)) or not 0 <= now_ms < float('inf'):
            raise ValueError('timestamp non valido')
        if self.last_ms is not None and now_ms < self.last_ms:
            raise ValueError('timestamp regressivo')
        self.last_ms = now_ms
        if fault or (self.state != State.OFF and (not power_good or not ref_good)):
            self._goto(State.FAULT,now_ms)
        elif not request or pa_active:
            self._goto(State.OFF,now_ms)
        elif self.state == State.FAULT:
            pass  # necessaria rimozione richiesta prima di riavviare
        elif self.state == State.OFF:
            if power_good and ref_good:
                self._goto(State.SETTLING,now_ms)
        elif self.state == State.SETTLING:
            if now_ms-self.entered_ms >= self.settle_ms:
                self._goto(State.WAIT_PROFILE,now_ms)
        elif self.state == State.WAIT_PROFILE:
            if profile_loaded:
                self._goto(State.WAIT_LOCK,now_ms)
        elif self.state == State.WAIT_LOCK:
            if retune_request:
                self._goto(State.WAIT_PROFILE,now_ms)
            elif lock_detect:
                if self.lock_seen_ms is None: self.lock_seen_ms = now_ms
                if now_ms-self.lock_seen_ms>=self.lock_dwell_ms:
                    self._goto(State.RX_READY,now_ms)
            else:
                self.lock_seen_ms = None
        elif self.state == State.RX_READY:
            if retune_request:
                self._goto(State.WAIT_PROFILE,now_ms)
            elif not lock_detect:
                self._goto(State.WAIT_LOCK,now_ms)
        return self.outputs(pa_active=pa_active, lock_detect=lock_detect, power_good=power_good, ref_good=ref_good)

    def _goto(self, state, now):
        if self.state != state:
            self.state = state
            self.entered_ms = now
            self.lock_seen_ms = None

    def outputs(self, *, pa_active=False, lock_detect=False, power_good=False, ref_good=False):
        healthy = bool(power_good and ref_good and not pa_active)
        ce = self.state in (State.SETTLING,State.WAIT_PROFILE,State.WAIT_LOCK,State.RX_READY) and healthy
        audio = self.state == State.RX_READY and ce and bool(lock_detect)
        return Pins(ce=ce,audio_rx_unmuted=audio,tx_enable=False)
