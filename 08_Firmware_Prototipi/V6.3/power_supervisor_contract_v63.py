"""Host-testable logical contract (not executable STM32 firmware, not electrical hardware verification)."""
from dataclasses import dataclass

@dataclass(frozen=True)
class PowerStatus:
    protected_path_valid: bool=False
    buck5_good: bool=False
    buck3v3_good: bool=False
    v62_3v3_supervisor_ok: bool=False
    uv_in_window: bool=False
    ov_in_window: bool=False
    audio_enable_request: bool=False
    pa_mode: bool=False
    tx_arm_request: bool=False

def evaluate(status:PowerStatus):
    pg = status.protected_path_valid and status.buck5_good and status.buck3v3_good
    rx_ready=pg and status.v62_3v3_supervisor_ok and status.uv_in_window and status.ov_in_window
    return {'power_good_hw':pg,
            'audio_power_request_gated':rx_ready and status.audio_enable_request,
            'rf_pa_power_enabled':False,
            'tx_rf_permitted':False}
