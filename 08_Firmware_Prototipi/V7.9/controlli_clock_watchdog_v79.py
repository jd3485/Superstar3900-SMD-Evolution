"""V7.9 manufacturer-window timing / alias risk and fail-closed diagnostic.

Data-sheet grounded: 30.72MHz master candidate from V7.5, standalone
TI TPS3430 window watchdog candidate and 32.768kHz Abracon reference
candidate. All are UNPOWERED, DNP and OPEN. Calculations are OFFLINE.

TPS3430 CWD=NC, SET0=0, SET1=1: upper min 23.375ms, lower max 2.22ms
at vendor specified temp/supply. WDI falling edge on each full heartbeat
cycle. A real TPS3430 output WDO is OPEN-DRAIN ACTIVE-LOW and self-rearms:
external fault latch + guaranteed physical DAC PD high and RF isolation
would be separate requirements, NOT implemented here.
"""
from math import isfinite

MASTER_HZ=30_720_000
REF_HZ=32_768
MASTER_TICKS_PER_TOGGLE=307_200
OLD_V78_TICKS_PER_TOGGLE=8
TPS3430_VENDOR_MPN="TPS3430WDRCR"
ABRACON_REF_VENDOR_MPN="ASFLK-32.768KHZ-LJT"
LOWER_WDI_LIMIT_MAX_MS=2.22
UPPER_WDI_LIMIT_MIN_MS=23.375
DAC_PD_PHYSCAL_DRIVER_PRESENT=False
INDEPENDENT_WATCHDOG_MOUNTED=False
RF_OUTPUT_CONNECTED=False
TX_PERMISSION=False

def tx_permission(**_):
    return False

def derive_cadence(master_hz=MASTER_HZ, toggle_ticks=MASTER_TICKS_PER_TOGGLE):
    if type(master_hz) is not int or master_hz<=0 or type(toggle_ticks) is not int or toggle_ticks<=0:
        raise ValueError("positive integer rate/divisor required")
    toggles_per_second=master_hz/toggle_ticks
    falling_edges_per_second=toggles_per_second/2
    return {
      "master_hz":master_hz,
      "master_ticks_per_toggle":toggle_ticks,
      "toggle_frequency_hz":toggles_per_second,
      "falling_edges_per_second":falling_edges_per_second,
      "falling_edge_period_ms":2000*toggle_ticks/master_hz,
      "external_fpga_output_routed":False,
      "rf_permission":False
    }

def watchdog_window(master_ppm=10):
    if not isfinite(master_ppm) or master_ppm<0 or master_ppm>100:
        raise ValueError("bounded positive frequency error")
    period=derive_cadence()["falling_edge_period_ms"]
    fast=period/(1+master_ppm*1e-6)
    slow=period/(1-master_ppm*1e-6)
    return {
      "config":"CWD=NC SET0=0 SET1=1; CRST=NC candidate; WDI falling-edge",
      "vendor_lower_boundary_max_ms":LOWER_WDI_LIMIT_MAX_MS,
      "vendor_upper_boundary_min_ms":UPPER_WDI_LIMIT_MIN_MS,
      "period_fastest_ms":fast,
      "period_slowest_ms":slow,
      "lower_margin_ms":fast-LOWER_WDI_LIMIT_MAX_MS,
      "upper_margin_ms":UPPER_WDI_LIMIT_MIN_MS-slow,
      "math_window_pass":fast>LOWER_WDI_LIMIT_MAX_MS and slow<UPPER_WDI_LIMIT_MIN_MS,
      "first_edge_after_power_up_verified":False,
      "physical_watchdog_built":False,
      "external_single_fault_latch_present":False
    }

def ref_sampling_risk(reference_hz=REF_HZ):
    if type(reference_hz) is not int or reference_hz<=0:
        raise ValueError("reference rate must be positive integer")
    new=derive_cadence()
    old=derive_cadence(toggle_ticks=OLD_V78_TICKS_PER_TOGGLE)
    return {
      "reference_hz":reference_hz,
      "reference_nyquist_hz":reference_hz/2,
      "old_toggle_rate_hz":old["toggle_frequency_hz"],
      "old_exceeds_ref_nyquist":old["toggle_frequency_hz"]>=reference_hz/2,
      "new_toggle_rate_hz":new["toggle_frequency_hz"],
      "new_below_ref_nyquist":new["toggle_frequency_hz"]<reference_hz/2,
      "nominal_ref_samples_per_toggle":reference_hz/new["toggle_frequency_hz"],
      "watchdog_independence_hardware_proved":False
    }

def fault_study(cause):
    causes={
      "MASTER_STOPS","REF_CLOCK_STOPS","BOTH_CLOCKS_STOP",
      "WDO_STUCK_HIGH","WDO_STUCK_LOW","WDI_STUCK_HIGH",
      "WDI_STUCK_LOW","DISABLED_SET_CONFIG","DAC_PD_STUCK_LOW",
      "SUPERVISOR_UNPOWERED","SUPPLY_BACKFEED","RF_RELAY_WELDED"
    }
    if cause not in causes:
        raise ValueError("unrecognized single-fault candidate")
    return {
      "cause":cause,
      "unresolved_hardware_requirement":True,
      "second_independent_physical_inhibit_present":False,
      "physical_safe_state_electrically_validated":False,
      "rf_permission":False,
    }
