"""V6.1 panel -> V6.0 audio bridge; functional prototype only, not hardware output pins."""
from dataclasses import dataclass
from pathlib import Path
import importlib.util,sys
HERE=Path(__file__).resolve()
def load_file(path,name):
 spec=importlib.util.spec_from_file_location(name,path)
 mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
 return mod
AUDIO=load_file(HERE.parents[1]/'V6.0'/'audio_controller_v60.py','audio_controller_v60_bridge')

def combined(panel_view,panel_inputs,*,relay_settled=True,amp_fault=False,hw_amp_arm=True):
    """Returns V6.0 logical routing. It does NOT drive amplifier SD or RF TX.
    Future V6.2 physical gate must independently check PA/TX unsafe states.
    """
    valid=panel_view.state not in ('SAFE_MUTE',)
    mode=AUDIO.RxMode(panel_view.mode) if panel_view.mode in [i.value for i in AUDIO.RxMode] else AUDIO.RxMode.AM
    a=AUDIO.Inputs(mode, pa_mode_hw=panel_inputs.pa,
         pa_ptt_pressed=panel_inputs.ptt,ch9=panel_inputs.ch9,
         tx_requested=False,power_good=panel_inputs.power_good,
         codec_ready=panel_inputs.codec_ready,relay_settled=relay_settled,
         transition=(not valid),amp_fault=amp_fault,hw_amp_arm=hw_amp_arm)
    o=AUDIO.control(a)
    assert not o.rf_tx_permission
    return o
