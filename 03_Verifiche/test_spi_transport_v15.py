"""Unit tests for LMX2572 data sheet SPI framing; do not use on hardware."""
import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'08_Firmware_Prototipi'))
from lmx2572_spi_transport_v15 import build_frame,decode_request,build_startup_register_frames
class TestFrames(unittest.TestCase):
 def test_read_write(self):
  self.assertEqual(build_frame(False,0,0),bytes.fromhex('000000'))
  self.assertEqual(build_frame(False,125,0xABCD),bytes.fromhex('7dabcd'))
  self.assertEqual(build_frame(True,17),bytes.fromhex('910000'))
  for i in range(126):
   for isread in (False,True):
    self.assertEqual(decode_request(build_frame(isread,i,0xBE01)),(isread,i,0xBE01))
 def test_inputs(self):
  for bad in (-1,126,128,3.5,True):
   with self.assertRaises((ValueError,TypeError)):build_frame(False,bad,0)
  for bad in (-1,65536,False):
   with self.assertRaises((ValueError,TypeError)):build_frame(False,0,bad)
  with self.assertRaises(TypeError):build_frame(0,1)
 def test_strict_profile_guard(self):
  fake={i:i for i in range(126)} # synthetic numbers, NOT a valid radio profile
  with self.assertRaises(ValueError):build_startup_register_frames(fake,0)
  with self.assertRaises(ValueError):build_startup_register_frames({0:0},0,explicitly_validated=True)
  frames=build_startup_register_frames(fake,0x0002,explicitly_validated=True)
  self.assertEqual(len(frames),127)
  self.assertEqual([decode_request(v)[1] for v in frames],[0]+list(range(125,-1,-1)))
if __name__=='__main__':unittest.main()
