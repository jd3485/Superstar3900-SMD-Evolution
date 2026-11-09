"""Mock di interblocco RX V6.5. NO scheda hardware / NO TX.

Non e' firmware macchina definitiva; si combina al supervisore PLL V6.4.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class FrontEndRxPins:
    receiver_path_enabled: bool
    if_audio_unmuted: bool
    tx_enabled: bool = False


def frontend_guard(*, power_good: bool, pll_locked_and_ready: bool,
                   requested_rx: bool, pa_active: bool, retuning: bool,
                   fault: bool, if_filter_selected: bool) -> FrontEndRxPins:
    valid = bool(power_good and pll_locked_and_ready and requested_rx
                 and not pa_active and not retuning and not fault and if_filter_selected)
    return FrontEndRxPins(receiver_path_enabled=valid,
                          if_audio_unmuted=valid,tx_enabled=False)
