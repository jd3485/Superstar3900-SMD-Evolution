"""V7.2: offline/periodic-block demonstration of IF2 digital upconversion.

Pure standard-library Python. No DAC, GPIO, SPI, PA, antenna or RF output.
All physical components and jumpers remain unpopulated (DNP).
The circular Hilbert transform assumes a periodic BLOCK: not streaming firmware.
"""
from math import cos, sin, pi, isfinite

AUDIO_FS = 48_000
DUC_FACTOR = 80
IF2_FS = AUDIO_FS * DUC_FACTOR       # 3.84 Msamples/s (hypothetical)
IF2_HZ = 455_000
IF1_HZ = 10_695_000
LO2_HZ = 10_240_000
HILBERT_TAPS = 257
POLYPHASE_TAPS = 32
MODES = ("AM", "FM", "USB", "LSB", "CW")
TX_HW_ENABLED = False
TX_DAC_PRESENT = False
TX_RF_OUTPUT_ROUTED = False


def tx_permission(**_):
    """No combination of external controls makes an RF path available."""
    return False


def _validate_audio(audio):
    x = [float(s) for s in audio]
    if not 384 <= len(x) <= 1024:
        raise ValueError("offline block must have 384..1024 samples")
    if any(not isfinite(s) or abs(s) > 1 for s in x):
        raise ValueError("audio must be finite, normalized into [-1,1]")
    return x


def _blackman_at_lag(lag, half_window):
    if abs(lag) >= half_window:
        return 0.0
    v = pi * lag / half_window
    return 0.42 + 0.5 * cos(v) + 0.08 * cos(2*v)


def hilbert_periodic(audio, taps=HILBERT_TAPS):
    """Zero-phase circular Blackman Hilbert FIR, noncausal offline reference.

    Test/reference blocks must be periodic. Real streaming needs overlap-save,
    state, group-delay matching and a separately verified filter architecture.
    """
    x = _validate_audio(audio)
    if taps % 2 != 1 or not 129 <= taps <= 257:
        raise ValueError("odd Hilbert FIR length must be 129..257")
    half = (taps-1)//2
    h = [(k, 2/(pi*k)*_blackman_at_lag(k, half))
         for k in range(-half, half+1) if k % 2]
    n_total = len(x)
    return [sum(c*x[(n-k) % n_total] for k,c in h) for n in range(n_total)]


def _polyphase_coefficients():
    """32-sample Blackman-windowed sinc across 80 phases, gain-normalized."""
    radius = POLYPHASE_TAPS//2
    taps = range(-radius+1, radius+1)
    table = []
    for phase in range(DUC_FACTOR):
        u = phase/DUC_FACTOR
        weights=[]
        for k in taps:
            lag = u-k
            sinc = 1.0 if abs(lag) < 1e-12 else sin(pi*lag)/(pi*lag)
            weights.append(sinc*_blackman_at_lag(lag, radius))
        gain=sum(weights)
        if gain == 0:
            raise ArithmeticError("invalid interpolation phase")
        table.append((tuple(taps), tuple(w/gain for w in weights)))
    return table


_PHASE_TABLE = _polyphase_coefficients()


def interpolate_periodic(values):
    """Offline polyphase upsample from 48 kSa/s to nominal 3.84 MSa/s.

    Circular only; boundary stitching and analog image suppression NOT modeled.
    """
    n_audio = len(values)
    if not 384 <= n_audio <= 1024:
        raise ValueError("unsupported offline block size")
    result=[]
    for index in range(n_audio):
        for offsets,weights in _PHASE_TABLE:
            result.append(sum(values[(index+k) % n_audio]*w
                              for k,w in zip(offsets, weights)))
    return result


def filter_ideal_bpf_loss_db(f_hz, f_lo_hz, f_hi_hz, order):
    """IDEAL analog Butterworth-BPF proxy; not a physical filter or guarantee."""
    if not (f_hz > 0 and 0 < f_lo_hz < f_hi_hz and 1 <= order <= 12):
        raise ValueError("invalid normalized ideal bandpass")
    f0_sq = f_lo_hz*f_hi_hz
    bw = f_hi_hz-f_lo_hz
    omega=abs((f_hz*f_hz-f0_sq)/(bw*f_hz))
    from math import log10
    return 10.0*log10(1.0+omega**(2*order))


def if2_synthesize(mode, audio, *, am_depth=0.35, deviation_hz=2000,
                   cw_key_down=False):
    """Offline real-valued sample ARRAY, not a hardware-ready DAC stream.

    FM IF2 deviation sign is NEGATIVE (LO1 high later reverses sign).
    USB RF -> lower IF2 sideband; LSB RF -> upper IF2 sideband.
    """
    x = _validate_audio(audio)
    if mode not in MODES:
        raise ValueError("unsupported mode")
    if not (isfinite(am_depth) and 0 <= am_depth < 1):
        raise ValueError("invalid AM depth")
    if not (isfinite(deviation_hz) and 0 <= deviation_hz <= 5000):
        raise ValueError("invalid nominal FM deviation")
    if mode in ("USB", "LSB"):
        h = hilbert_periodic(x)
        complex_baseband = [complex(a, -b if mode == "USB" else b)
                            for a,b in zip(x,h)]
        up = interpolate_periodic(complex_baseband)
    elif mode == "CW":
        up = None
    else:
        up = interpolate_periodic(x)
    out=[]
    fm_integral=0.0
    fm_prev=0.0
    for n in range(len(x)*DUC_FACTOR):
        t = n/IF2_FS
        if mode == "CW":
            # Offline pulse: 2ms sin^2 rise/fall; not a proven keying envelope.
            if not cw_key_down:
                out.append(0.0)
                continue
            duration=len(x)/AUDIO_FS
            rise=min(1.0, t/0.002, (duration-t)/0.002)
            envelope=sin(pi/2*max(0.0, rise))**2
            out.append(envelope*cos(2*pi*(IF2_HZ-700)*t))
            continue
        phase=2*pi*IF2_HZ*t
        if mode=="AM":
            out.append((1.0+am_depth*up[n])*cos(phase))
        elif mode=="FM":
            value=up[n]
            fm_integral+=(fm_prev+value)/(2*IF2_FS)
            fm_prev=value
            out.append(cos(phase - 2*pi*deviation_hz*fm_integral))
        else:
            b=up[n]
            out.append(b.real*cos(phase)-b.imag*sin(phase))
    return out


def coherent_tone_amplitude(samples, freq_hz, fs_hz=IF2_FS):
    """DFT coefficient for coherent bin only (num cycles must be integer)."""
    n=len(samples)
    cycles=n*freq_hz/fs_hz
    if abs(cycles-round(cycles)) > 1e-7:
        raise ValueError("tone is not coherent with current block length")
    # Goertzel (real-valued samples), magnitude of fundamental amplitude.
    omega=2*pi*freq_hz/fs_hz
    coeff=2*cos(omega)
    s1=s2=0.0
    for val in samples:
        s0=val+coeff*s1-s2
        s2,s1=s1,s0
    real=s1-s2*cos(omega)
    imag=s2*sin(omega)
    return 2*(real*real+imag*imag)**0.5/n
