"""V7.4 offline DAC900 digital-bus contract + passive current/voltage study.

Pure Python. Does NOT control a peripheral or implement STM32/FPGA firmware.
No physical DAC, GPIO, power, clock, PA, TX, mixer or antenna is connected.
The returned "words" and "edges" are mathematical annotations only.
"""
from collections import deque
from math import isfinite

SAMPLE_RATE_HZ = 3_840_000
AUDIO_RATE_HZ = 48_000
UPSAMPLE = SAMPLE_RATE_HZ // AUDIO_RATE_HZ
CLOCK_PERIOD_NS = 1e9 / SAMPLE_RATE_HZ
CLOCK_HALF_PERIOD_NS = CLOCK_PERIOD_NS / 2
DAC_BITS = 10
DAC_CODES = 1 << DAC_BITS
DEFAULT_FULL_SCALE_A = 0.020  # TI internal REF=1.24V; RSET nominal approx 2k
DEFAULT_SHUNT_OHM = 49.9
DEFAULT_TERMINATION_OHM = 49.9
# This is an ENGINEERING HYPOTHESIS, not TI's specified min across PVT.
ASSUMED_REQUIRED_SETUP_NS = 20.0
ASSUMED_REQUIRED_HOLD_NS = 20.0
# Vendor timing sheet lists typical 1.5ns setup, 1.0ns hold.
TI_DATASHEET_SETUP_TYP_NS = 1.5
TI_DATASHEET_HOLD_TYP_NS = 1.0

DAC_MOUNTED = False
PD_PHYSICALLY_RELEASED = False
BRIDGE_MOUNTED = False
CLOCK_SOURCE_MOUNTED = False
ANALOG_LINK_MOUNTED = False
TX_RF_ENABLED = False


def tx_permission(**_diagnostics):
    """RF permission is unconditionally denied; no software unlock exists."""
    return False


def _valid_code(code):
    return type(code) is int and 0 <= code < DAC_CODES


def current_output_a(code, full_scale_current_a=DEFAULT_FULL_SCALE_A):
    """Ideal DAC900 straight-binary IOUT current; datasheet uses CODE/1024.

    The complementary output is (1023-CODE)/1024; ignoring DAC errors.
    """
    if not _valid_code(code):
        raise ValueError("requires a 10-bit unsigned INTEGER DAC code")
    if not isfinite(full_scale_current_a) or not 0.002 <= full_scale_current_a <= 0.020:
        raise ValueError("full scale outside vendor nominal 2..20mA")
    return full_scale_current_a * code / DAC_CODES


def complementary_current_a(code, full_scale_current_a=DEFAULT_FULL_SCALE_A):
    current_output_a(code, full_scale_current_a)
    return full_scale_current_a * (DAC_CODES-1-code) / DAC_CODES


def effective_resistance_ohm(shunt_ohm=DEFAULT_SHUNT_OHM,
                             termination_ohm=DEFAULT_TERMINATION_OHM):
    """Two parallel resistor loads, NOT a measured high-frequency impedance."""
    if (not isfinite(shunt_ohm) or not isfinite(termination_ohm) or
            shunt_ohm <= 0 or termination_ohm <= 0):
        raise ValueError("two positive, finite loads required")
    return shunt_ohm * termination_ohm / (shunt_ohm + termination_ohm)


def ideal_terminated_voltage_v(code, full_scale_current_a=DEFAULT_FULL_SCALE_A,
                               shunt_ohm=DEFAULT_SHUNT_OHM,
                               termination_ohm=DEFAULT_TERMINATION_OHM):
    """Ideal current output -> 49.9-ohm local shunt || 49.9-ohm termination.

    This is the low-frequency equivalent of a doubly terminated nominal
    50-ohm line, BEFORE modelling a filter. DAC is DNP and links remain open.
    """
    return current_output_a(code, full_scale_current_a) * effective_resistance_ohm(
        shunt_ohm, termination_ohm)


def analog_study(code, shunt_ohm=DEFAULT_SHUNT_OHM,
                 termination_ohm=DEFAULT_TERMINATION_OHM,
                 full_scale_current_a=DEFAULT_FULL_SCALE_A):
    v=ideal_terminated_voltage_v(code, full_scale_current_a,
                                 shunt_ohm, termination_ohm)
    return {
        "iout_a": current_output_a(code, full_scale_current_a),
        "ioutb_a": complementary_current_a(code, full_scale_current_a),
        "effective_ohm": effective_resistance_ohm(shunt_ohm, termination_ohm),
        "termination_voltage_v": v,
        "shunt_power_w": v*v/shunt_ohm,
        "termination_power_w": v*v/termination_ohm,
        "output_compliance_in_vendor_range": -1.0 <= v <= 1.25,
        "hardware_implemented": False,
        "rf_tx_allowed": False,
    }


def load_tolerance_sweep(code=1023, resistor_nominal_ohm=49.9,
                         tolerance_fraction=0.01,
                         full_scale_current_a=DEFAULT_FULL_SCALE_A):
    """4 extreme-corner values; not an RF/PCB tolerance Monte Carlo."""
    if not isfinite(tolerance_fraction) or not 0 <= tolerance_fraction <= 0.05:
        raise ValueError("invalid resistor tolerance")
    points=[]
    for a in (-1,1):
        for b in (-1,1):
            rs=resistor_nominal_ohm*(1+a*tolerance_fraction)
            rt=resistor_nominal_ohm*(1+b*tolerance_fraction)
            points.append(ideal_terminated_voltage_v(code,full_scale_current_a,rs,rt))
    return min(points),max(points)


def clock_data_budget():
    """A mathematical sample-clock resource plan, no verified FPGA/MCU profile."""
    return {
        "audio_rate_hz": AUDIO_RATE_HZ,
        "if2_rate_hz": SAMPLE_RATE_HZ,
        "required_ratio": UPSAMPLE,
        "clock_period_ns": CLOCK_PERIOD_NS,
        "clock_high_low_each_ns_at_50pct": CLOCK_HALF_PERIOD_NS,
        "parallel_width": DAC_BITS,
        "data_pins": DAC_BITS,
        "data_toggle_rate_upper_bits_per_second": SAMPLE_RATE_HZ*DAC_BITS,
        "packed_word_bytes": 2,
        "packed_bus_bytes_per_second": SAMPLE_RATE_HZ*2,
        "buffer_bytes_for_512_audio_samples": 512*UPSAMPLE*2,
        "physical_clock_source": False,
        "physical_parallel_bridge": False,
        "rf_tx_permission": False,
    }


def fifo_skew_samples(delta_clock_ppm, seconds):
    """Abstract independent-clock FIFO skew: sign means prod-cons direction.

    For synchronized clocks this drift is zero. No hardware PLL clock model.
    """
    if not isfinite(delta_clock_ppm) or not isfinite(seconds) or seconds < 0:
        raise ValueError("finite nonnegative time and finite ppm required")
    return SAMPLE_RATE_HZ * delta_clock_ppm * 1e-6 * seconds


class OfflineParallelBridge:
    """A bounded *virtual* FIFO and two-edge timing/audit state machine.

    Rising clock edge latches the stable data; falling edge updates the
    *hypothetical* current-output sample. Missing data/clock, power fault,
    timing or capacity error latches FAULT; no reset in this class can emit
    RF. The physical PD pin is assumed ASSERTED for every virtual cycle.
    """

    CAPACITY = 1024

    def __init__(self):
        self._fifo = deque()
        self._fault = None
        self._cycles = 0
        self._last_word = None

    @property
    def fault(self):
        return self._fault

    @property
    def queued(self):
        return len(self._fifo)

    def enqueue(self, codes):
        words=list(codes)
        if self._fault is not None:
            raise RuntimeError("fault latched")
        if any(not _valid_code(x) for x in words):
            self._fault = "INVALID_CODE"
            self._fifo.clear()
            raise ValueError("invalid bus word")
        if len(words) + self.queued > self.CAPACITY:
            self._fault = "FIFO_OVERFLOW"
            self._fifo.clear()
            raise OverflowError("offline FIFO capacity exceeded")
        self._fifo.extend(words)

    def cycle(self, *, clock_present=True, supply_good=True,
              valid_before_rising_ns=40.0, valid_after_rising_ns=40.0):
        if self._fault is not None:
            return self.diagnostics()
        if not clock_present:
            self._fault = "CLOCK_MISSING"
        elif not supply_good:
            self._fault = "POWER_NOT_GOOD"
        elif (not isfinite(valid_before_rising_ns) or
              not isfinite(valid_after_rising_ns) or
              valid_before_rising_ns < ASSUMED_REQUIRED_SETUP_NS or
              valid_after_rising_ns < ASSUMED_REQUIRED_HOLD_NS or
              valid_before_rising_ns > CLOCK_HALF_PERIOD_NS or
              valid_after_rising_ns > CLOCK_HALF_PERIOD_NS):
            self._fault = "DATA_TIMING_NOT_MET"
        elif not self._fifo:
            self._fault = "FIFO_UNDERFLOW"
        if self._fault is not None:
            self._fifo.clear()
            return self.diagnostics()
        word=self._fifo.popleft()
        self._last_word=word
        self._cycles+=1
        return {
            **self.diagnostics(),
            "hypothetical_word": word,
            "rising_edge_ns": (self._cycles-1)*CLOCK_PERIOD_NS,
            "following_falling_edge_ns": (self._cycles-1)*CLOCK_PERIOD_NS + CLOCK_HALF_PERIOD_NS,
        }

    def diagnostics(self):
        return {
            "virtual_cycles": self._cycles,
            "queued": self.queued,
            "fault": self._fault,
            "pd_asserted_in_model": True,
            "hardware_clock_present": False,
            "hardware_data_bus_present": False,
            "analog_link_mounted": False,
            "rf_tx_allowed": False,
        }
