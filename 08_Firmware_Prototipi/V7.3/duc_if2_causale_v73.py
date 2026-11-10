"""V7.3 causal, stateful *offline* IF2 waveform research model.

Independent of hardware. No physical DAC, clock, GPIO, PLL, PA, PTT or antenna.
48 kSa/s input -> 80x/3.84 MSa/s mathematical output only.
Hilbert FIR and interpolation retain history across arbitrary block boundaries.
This is NOT real-time STM32 firmware. All TX interfaces are DNP/open.
"""
from math import cos, sin, pi, isfinite
from collections import deque

AUDIO_RATE_HZ = 48_000
UPSAMPLE = 80
OUTPUT_RATE_HZ = AUDIO_RATE_HZ * UPSAMPLE
IF2_HZ = 455_000
HILBERT_LENGTH = 257
INTERPOLATOR_LENGTH = 32
DAC_BITS = 10
DAC_MPN = "DAC900E"  # TI TSSOP-28 candidate, not mounted or connected
TX_RF_ENABLED = False
DAC_MOUNTED = False
IF2_CONNECTED_TO_MIXER = False
PA_CONNECTED = False
MODES = ("AM", "FM", "USB", "LSB", "CW")


def tx_permission(**_controls):
    """No software control has authority to permit a real TX signal."""
    return False


def _blackman(index, length):
    return 0.42 - 0.5*cos(2*pi*index/(length-1)) + 0.08*cos(4*pi*index/(length-1))


def _design_hilbert():
    middle = (HILBERT_LENGTH-1)//2
    taps = []
    for i in range(HILBERT_LENGTH):
        lag = i-middle
        taps.append(2.0/(pi*lag)*_blackman(i,HILBERT_LENGTH) if lag and lag % 2 else 0.0)
    return tuple(taps)


def _design_interpolator():
    """32-tap causal, delay 15.5 AUDIO samples, fractional shift per phase."""
    d = (INTERPOLATOR_LENGTH-1)/2
    phases=[]
    for p in range(UPSAMPLE):
        weights=[]
        for j in range(INTERPOLATOR_LENGTH):
            v = j - d + p/UPSAMPLE
            sinc = 1.0 if abs(v)<1e-12 else sin(pi*v)/(pi*v)
            weights.append(sinc*_blackman(j,INTERPOLATOR_LENGTH))
        total=sum(weights)
        if abs(total)<1e-12:
            raise ArithmeticError("invalid polyphase normalization")
        phases.append(tuple(w/total for w in weights))
    return tuple(phases)


_H = _design_hilbert()
_POLYPHASE = _design_interpolator()


class CausalIF2:
    """Continuously evaluated offline prototype: processing chunk size invariant.

    Constructor selects a single operating mode; use reset for mode change.
    CW uses a 2ms sin-squared transition. NCO and FM phase persist across blocks.
    """

    def __init__(self, mode, am_depth=0.35, fm_deviation_hz=2000.0):
        if mode not in MODES:
            raise ValueError("unsupported mode")
        if not isfinite(am_depth) or not (0 <= am_depth < 1):
            raise ValueError("invalid AM depth")
        if not isfinite(fm_deviation_hz) or not (0 <= fm_deviation_hz <= 5000):
            raise ValueError("invalid FM deviation")
        self.mode = mode
        self.am_depth = am_depth
        self.fm_deviation_hz = fm_deviation_hz
        self.reset()

    def reset(self):
        self._hist = deque([0.0]*HILBERT_LENGTH, maxlen=HILBERT_LENGTH)
        self._iq_hist = deque([0j]*INTERPOLATOR_LENGTH, maxlen=INTERPOLATOR_LENGTH)
        self._phase = 0.0
        self._fm_phase = 0.0
        self._fm_prev = 0.0
        self._cw_env = 0.0
        self.audio_samples = 0
        self.if2_samples = 0

    def process(self, audio, *, cw_key_down=False):
        """Return float array, never send samples or control to a physical device."""
        x = [float(v) for v in audio]
        if len(x)>512 or any(not isfinite(v) or abs(v)>1 for v in x):
            raise ValueError("bounded, finite normalized audio required")
        out=[]
        hcoeff=_H
        phases=_POLYPHASE
        mode=self.mode
        base_step=2*pi*(IF2_HZ-(700 if mode=="CW" else 0))/OUTPUT_RATE_HZ
        fm_scale=2*pi*self.fm_deviation_hz/(2*OUTPUT_RATE_HZ)
        env_step=1/(0.002*OUTPUT_RATE_HZ)
        for value in x:
            self._hist.appendleft(value)
            if mode in ("USB", "LSB"):
                hilbert=sum(hcoeff[j]*self._hist[j] for j in range(HILBERT_LENGTH) if hcoeff[j])
                real=self._hist[(HILBERT_LENGTH-1)//2]
                bb=complex(real, -hilbert if mode=="USB" else hilbert)
            elif mode=="CW":
                bb=0j
            else:
                # Delay audio paths consistently with Hilbert real branch.
                bb=complex(self._hist[(HILBERT_LENGTH-1)//2],0.0)
            self._iq_hist.appendleft(bb)
            iq=self._iq_hist
            for taps in phases:
                if mode=="CW":
                    if cw_key_down:
                        self._cw_env=min(1.0,self._cw_env+env_step)
                    else:
                        self._cw_env=max(0.0,self._cw_env-env_step)
                    envelope=sin((pi/2)*self._cw_env)**2
                    sample=envelope*cos(self._phase)
                else:
                    z=sum(w*iq[j] for j,w in enumerate(taps))
                    if mode=="AM":
                        sample=(1+self.am_depth*z.real)*cos(self._phase)
                    elif mode=="FM":
                        self._fm_phase=(self._fm_phase+fm_scale*(self._fm_prev+z.real))%(2*pi)
                        self._fm_prev=z.real
                        sample=cos(self._phase-self._fm_phase)
                    else:
                        sample=z.real*cos(self._phase)-z.imag*sin(self._phase)
                out.append(sample)
                self._phase=(self._phase+base_step)%(2*pi)
                self.if2_samples+=1
            self.audio_samples+=1
        return out

    def diagnostics(self):
        return {
            "mode":self.mode,
            "audio_samples":self.audio_samples,
            "if2_samples":self.if2_samples,
            "latency_audio_samples":(HILBERT_LENGTH-1)//2+(INTERPOLATOR_LENGTH-1)/2,
            "rf_tx_permitted":False,
            "dac_present":False,
        }


def quantize_unsigned_10bit(samples, *, headroom=0.70):
    """Return only integer codes; NOT a DAC driver, hardware frames or GPIO.

    Guard overflow rather than silently clipping, since AM peaks > 1 are possible.
    """
    if not isfinite(headroom) or not (0<headroom<=1):
        raise ValueError("invalid headroom")
    out=[]
    for v in samples:
        val=float(v)*headroom
        if not isfinite(val) or abs(val)>1:
            raise ValueError("normalized analog-domain overrange: refusing quantization")
        out.append(min(1023,max(0,round((val+1)*1023/2))))
    return out


def compute_budget():
    """Upper bound for naïve direct form; not an MCU timing benchmark."""
    return {
        "audio_samples_per_sec":AUDIO_RATE_HZ,
        "if2_samples_per_sec":OUTPUT_RATE_HZ,
        "parallel_bits":DAC_BITS,
        "raw_parallel_data_bits_per_sec":OUTPUT_RATE_HZ*DAC_BITS,
        "polyphase_macs_per_sec":OUTPUT_RATE_HZ*INTERPOLATOR_LENGTH,
        "hilbert_nonzero_macs_per_sec":AUDIO_RATE_HZ*(HILBERT_LENGTH-1)//2,
        "combined_naive_macs_per_sec":OUTPUT_RATE_HZ*INTERPOLATOR_LENGTH+
                                      AUDIO_RATE_HZ*(HILBERT_LENGTH-1)//2,
        "analogue_lpf_present":False,
        "rf_tx_permitted":False,
    }
