"""V7.5 three-stage causal/polyphase audio-baseband interpolation study.

Original V7.3 IF2 numerical model uses one 80x 32-tap/phase interpolator,
whose direct cost is ~122.88 million coefficients/s (excluding Hilbert).
This NEW independent baseband model interpolates 5x, then 4x, then 4x
using 16 taps per phase. It is not firmware, and output is not DAC/IF2/RF.

Quality and actual execution time must be independently validated. A lower
MAC count does NOT establish output filter attenuation or MCU compatibility.
"""
from collections import deque
from math import cos, pi, sin, isfinite

INPUT_RATE_HZ = 48_000
STAGE_FACTORS = (5,4,4)
TAPS_PER_PHASE = 16
FINAL_RATE_HZ = INPUT_RATE_HZ*5*4*4
HILBERT_NONZERO_TAPS = 128
RF_PERMISSION = False
HARDWARE_ATTACHED = False


def tx_permission(**_):
    return False


def _blackman(i, count):
    return 0.42-0.5*cos(2*pi*i/(count-1))+0.08*cos(4*pi*i/(count-1))


def _sinc(x):
    return 1.0 if abs(x)<1e-12 else sin(pi*x)/(pi*x)


def phase_coefficients(factor, taps=TAPS_PER_PHASE):
    if type(factor) is not int or not 2<=factor<=16:
        raise ValueError("factor outside study range")
    if type(taps) is not int or not 8<=taps<=64 or taps%2:
        raise ValueError("even tap count required")
    center=(taps-1)/2
    phases=[]
    for phase in range(factor):
        coeff=[_sinc(j-center+phase/factor)*_blackman(j,taps)
               for j in range(taps)]
        total=sum(coeff)
        if abs(total)<1e-12:
            raise ValueError("invalid phase normalization")
        phases.append(tuple(w/total for w in coeff))
    return tuple(phases)


class PolyphaseStage:
    """Direct-form bounded offline reference with history across chunks."""
    def __init__(self, factor, taps=TAPS_PER_PHASE):
        self.factor=factor
        self.taps=taps
        self.coefficients=phase_coefficients(factor,taps)
        self.reset()

    def reset(self):
        self._history=deque([0j]*self.taps,maxlen=self.taps)
        self.received=0
        self.emitted=0

    def process(self, data):
        values=list(data)
        if len(values)>50_000:
            raise ValueError("bounded study chunk")
        output=[]
        for s in values:
            z=complex(s)
            if not isfinite(z.real) or not isfinite(z.imag) or abs(z)>1.5:
                raise ValueError("non-finite or over-range baseband")
            self._history.appendleft(z)
            for coeff in self.coefficients:
                out=sum(w*self._history[j] for j,w in enumerate(coeff))
                output.append(out)
                self.emitted+=1
            self.received+=1
        return output


class ThreeStageInterpolator:
    """Reference: no wrapping, shared 48k input and 3.84M output ratio."""
    def __init__(self):
        self.stages=tuple(PolyphaseStage(v) for v in STAGE_FACTORS)

    def reset(self):
        for stage in self.stages:
            stage.reset()

    def process(self, audio_baseband):
        values=list(audio_baseband)
        if len(values)>512:
            raise ValueError("max 512 samples per call")
        for stage in self.stages:
            values=stage.process(values)
        return values

    def stats(self):
        return {
            "input_samples":self.stages[0].received,
            "output_samples":self.stages[-1].emitted,
            "stages":[(s.received,s.emitted) for s in self.stages],
            "rf_permission":False,
            "physical_dac_connected":False,
        }


def numerical_mac_budget():
    """Nominal scalar coefficient-products only, NOT CPU cycles/time."""
    rates=[]
    current=INPUT_RATE_HZ
    for factor in STAGE_FACTORS:
        current*=factor
        rates.append(current)
    budget=sum(rate*TAPS_PER_PHASE for rate in rates)
    hilbert=INPUT_RATE_HZ*HILBERT_NONZERO_TAPS
    old=3_840_000*32+hilbert
    new=budget+hilbert
    return {
        "stage_rates_hz":rates,
        "stage_interpolation_coefficient_products_sec":[r*TAPS_PER_PHASE for r in rates],
        "interpolation_total_sec":budget,
        "hilbert_reference_products_sec":hilbert,
        "combined_candidate_products_sec":new,
        "combined_previous_direct_products_sec":old,
        "estimated_products_reduction_percent":100*(old-new)/old,
        "same_filter_as_v73":False,
        "spectrum_or_realtime_certified":False,
        "hardware_implemented":False,
        "rf_permission":False,
    }
