import unittest,importlib.util,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def imp(path,name):
 spec=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);return m
p=imp(ROOT/'08_Firmware_Prototipi/V6.1/panel_controller_v61.py','p61')
b=imp(ROOT/'08_Firmware_Prototipi/V6.1/integration_audio_v61.py','b61')
F=p.load_frequency_table(ROOT/'02_Piano_Frequenze/Tabella_270_canali.csv')
class TestBridge(unittest.TestCase):
 def test_01_all_modes_bridge_equal_mux(self):
  for mode in p.MODES:
   c=p.Controller(F);x=p.Inputs(modes=(mode,))
   for _ in range(4):view=c.update(x)
   o=b.combined(view,x)
   self.assertEqual(o.mux_code,view.mux_code);self.assertEqual(o.mux_enable_n,0);self.assertFalse(o.rf_tx_permission)
 def test_02_invalid_panel_forces_audio_mute(self):
  c=p.Controller(F);x=p.Inputs(bands=())
  v=c.update(x);o=b.combined(v,x)
  self.assertEqual(o.mode,'FAULT_OR_SETTLE');self.assertEqual(o.mux_enable_n,1);self.assertEqual(o.amp_sd,0)
 def test_03_pa_audio_mic_only(self):
  for ptt in [False,True]:
   c=p.Controller(F);x=p.Inputs(pa=True,ptt=ptt)
   o=b.combined(c.update(x),x)
   self.assertEqual(o.mode,'PA');self.assertEqual(o.pa_audio_audible,ptt);self.assertFalse(o.rf_tx_permission)
 def test_04_ch9_am(self):
  c=p.Controller(F);x=p.Inputs(ch9=True,modes=('CW',))
  v=c.update(x);o=b.combined(v,x)
  self.assertEqual(v.mode,'AM');self.assertEqual(o.mux_code,0);self.assertFalse(o.rf_tx_permission)
 def test_05_codec_fail_amp_off(self):
  c=p.Controller(F);x=p.Inputs(codec_ready=False)
  v=c.update(x);o=b.combined(v,x)
  self.assertTrue(v.rx_mute);self.assertEqual(o.amp_sd,0);self.assertEqual(o.mux_enable_n,1)
if __name__=='__main__':unittest.main()
