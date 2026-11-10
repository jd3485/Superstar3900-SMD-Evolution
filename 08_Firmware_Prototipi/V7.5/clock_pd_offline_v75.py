"""V7.5 coherent clock domain and fault-latched safety specification, offline.

No programmable logic file, bitstream, MCU driver, DAC output, hardware clock,
power control, TX or antenna access. Derived output *events* exist as integers
in memory; all components are DNP and RF permission is always denied.

Clock source candidate: Abracon ASDMB-30.720MHZ-LY (30.72MHz 4-pad).
Programmable bridge candidate: Lattice iCE40UP5K-SG48I (48-QFN).
Pin assignments on FPGA and its clock/reset/power circuitry remain UNDESIGNED.
"""
from itertools import product
from math import isfinite

MASTER_HZ = 30_720_000
DAC_HZ = 3_840_000
AUDIO_HZ = 48_000
MASTER_DIV_DAC = MASTER_HZ // DAC_HZ
MASTER_DIV_AUDIO = MASTER_HZ // AUDIO_HZ
DAC_PER_AUDIO = DAC_HZ // AUDIO_HZ
OSCILLATOR_MPN = "ASDMB-30.720MHZ-LY"
FPGA_CANDIDATE_MPN = "iCE40UP5K-SG48I"
MAX_OSC_STARTUP_MS_VENDOR = 3.0
OSC_TOLERANCE_PPM_CANDIDATE = 10
TX_COMPONENTS_ALL_DNP = True
DAC_PD_HARDWIRED = False
FPGA_CONFIGURED_IN_HARDWARE = False
CLOCK_ELECTRICALLY_CONNECTED = False
RF_OUTPUT_ROUTED = False
TX_PERMISSION = False


def tx_permission(**_):
    return False


def validate_rates(master_hz=MASTER_HZ, dac_hz=DAC_HZ, audio_hz=AUDIO_HZ):
    """Reject any rate set that is not synchronous integer division."""
    if any(type(v) is not int or v <= 0 for v in (master_hz, dac_hz, audio_hz)):
        raise ValueError("integer positive sample rates required")
    if master_hz % dac_hz or master_hz % audio_hz or dac_hz % audio_hz:
        raise ValueError("one integer-divisible master domain required")
    return (master_hz // dac_hz, master_hz // audio_hz, dac_hz // audio_hz)


def clock_events(start_master_tick, count):
    """Tick numbers of hypothetical DAC rising edges and audio boundaries.

    Ticks are absolute; adjacent calls return exactly the same trace as one
    call. No physical clock or frequency divider is instantiated.
    """
    if type(start_master_tick) is not int or start_master_tick < 0:
        raise ValueError("nonnegative absolute start required")
    if type(count) is not int or not 0 <= count <= 500_000:
        raise ValueError("bounded integer tick count required")
    dac_edges = []
    audio_edges = []
    for tick in range(start_master_tick + 1, start_master_tick + count + 1):
        if tick % MASTER_DIV_DAC == 0:
            dac_edges.append(tick)
        if tick % MASTER_DIV_AUDIO == 0:
            audio_edges.append(tick)
    return {"dac":dac_edges, "audio":audio_edges, "real_hardware":False}


def period_ns(master_hz=MASTER_HZ):
    if type(master_hz) is not int or master_hz <= 0:
        raise ValueError("master frequency must be positive integer")
    return 1e9 / master_hz


def worst_case_rate_error_hz(rate_hz, common_ppm=OSC_TOLERANCE_PPM_CANDIDATE):
    """Common scale factor shifts absolute rates, NOT their exact integer ratio."""
    if not (isfinite(common_ppm) and 0 <= common_ppm <= 100):
        raise ValueError("bounded ppm required")
    if type(rate_hz) is not int or rate_hz <= 0:
        raise ValueError("positive integer output rate")
    return rate_hz * common_ppm * 1e-6


def resource_plan(block_audio=512):
    if type(block_audio) is not int or not 1 <= block_audio <= 512:
        raise ValueError("bounded integer block size")
    v = validate_rates()
    return {
        "master_hz":MASTER_HZ,
        "dac_hz":DAC_HZ,
        "audio_hz":AUDIO_HZ,
        "div_master_dac":v[0],
        "div_master_audio":v[1],
        "samples_per_audio":v[2],
        "audio_block_samples":block_audio,
        "dac_codes_per_block":block_audio * DAC_PER_AUDIO,
        "packed_16bit_bytes_per_block":block_audio * DAC_PER_AUDIO * 2,
        "streaming_packed_16bit_bytes_sec":DAC_HZ * 2,
        "bit_parallel_10bit_rate":DAC_HZ * 10,
        "oscillator_max_startup_ticks_ceiling":
            (MASTER_HZ * 3 + 999) // 1000,
        "common_clock_ratio_drift_codes":0,
        "physical_fpga_pins_mapped":False,
        "rf_permission":False,
    }


class StartupFaultPlanner:
    """FMEA-oriented virtual power/clock guard; output never leaves RAM.

    This is NOT an independent hardwired interlock. In particular the DAC900
    PD pin is ACTIVE-HIGH with an internal pulldown (would run if floating),
    while ASDMB oscillator STANDBY is ACTIVE-LOW (would run if floating).
    Both defects require physical solution; never claim that boolean flags
    in this model make a future PCB fail-safe.
    """

    def __init__(self, stable_master_ticks=92_160):
        if type(stable_master_ticks) is not int or not 8 <= stable_master_ticks <= 100_000:
            raise ValueError("bounded integer guard length required")
        self.stable_required=stable_master_ticks
        self._consecutive=0
        self._fault=None
        self._last_tick=None

    def observe(self, master_tick, *, oscillator_rail_ok, fpga_core_ok,
                fpga_io_ok, fpga_config_ok, clock_present,
                dac_rail_ok, supervisor_ok, fifo_ready):
        flags=(oscillator_rail_ok, fpga_core_ok, fpga_io_ok,
               fpga_config_ok, clock_present, dac_rail_ok,
               supervisor_ok, fifo_ready)
        if type(master_tick) is not int or master_tick < 0 or any(type(v) is not bool for v in flags):
            raise ValueError("strict tick and control type contract")
        if self._fault is not None:
            return self.snapshot()
        if self._last_tick is not None and master_tick != self._last_tick + 1:
            self._fault="MISSING_MASTER_TICKS"
        elif not all(flags):
            self._fault="MISSING_RAIL_CONFIG_CLOCK_OR_DATA"
        else:
            self._consecutive+=1
        self._last_tick=master_tick
        return self.snapshot()

    def inject_fault(self, cause):
        if cause not in ("PD_STUCK_LOW","OSC_STANDBY_OPEN",
                         "DAC_RAIL_BACKFEED","BRIDGE_CONFIG_LOSS",
                         "LOST_SYNC","PA_RELAY_SHORT","UNKNOWN"):
            raise ValueError("unrecognized hazard")
        if self._fault is None:
            self._fault=cause
        return self.snapshot()

    def snapshot(self):
        return {
            "guard_conditions_satisfied":
                self._consecutive >= self.stable_required and self._fault is None,
            "stable_ticks":self._consecutive,
            "fault":self._fault,
            "dac_pd_pin_currently_driven":False,
            "dac_pd_asserted_in_proposed_physical_circuit":None,
            "hardware_dac_rail_present":False,
            "rf_path_connected":False,
            "tx_permission":False,
        }
