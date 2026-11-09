"""Prove del contratto di sicurezza logica, non implementazione hardware."""
import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'08_Firmware_Prototipi'))
from funzioni_utente_v151 import Mode, UserSettings, Conditions, effective_control

class ContractTests(unittest.TestCase):
    def test_tx_off_default(self):
        self.assertFalse(effective_control(UserSettings(vox_enabled=True), Conditions(vox_detected=True))['rf_tx'])
    def test_tx_only_when_safe(self):
        s=UserSettings(vox_enabled=True)
        self.assertFalse(effective_control(s,Conditions(vox_detected=True,tx_permitted=True))['rf_tx'])
        self.assertTrue(effective_control(s,Conditions(vox_detected=True,tx_permitted=True,radio_safe=True))['rf_tx'])
    def test_pa_never_tx(self):
        s=UserSettings(pa=True,vox_enabled=True,dual_watch=True)
        o=effective_control(s,Conditions(ptt=True,vox_detected=True,tx_permitted=True,radio_safe=True))
        self.assertFalse(o['rf_tx']);self.assertFalse(o['dual_watch']);self.assertTrue(o['pa_audio_gate'])
    def test_ch9_override(self):
        s=UserSettings(ch9=True,dual_watch=True,echo=True,roger_beep=True,ctcss_rx=True)
        o=effective_control(s, Conditions())
        self.assertEqual(o['rx'],'CH9-27.065-AM'); self.assertFalse(o['dual_watch'])
        self.assertFalse(o['echo']); self.assertFalse(o['roger_beep']); self.assertFalse(o['ctcss'])
    def test_dw_never_tx_on_secondary(self):
        s=UserSettings(dual_watch=True,channel_primary='A',channel_secondary='B')
        o=effective_control(s,Conditions(ptt=True,tx_permitted=True,radio_safe=True,secondary_has_signal=True))
        self.assertEqual(o['target_tx'],'A');self.assertFalse(o['dual_watch'])
    def test_dw_receives_secondary(self):
        s=UserSettings(dual_watch=True,channel_primary='A',channel_secondary='B')
        o=effective_control(s,Conditions(secondary_has_signal=True))
        self.assertEqual(o['rx'],'B');self.assertTrue(o['dual_watch'])
    def test_no_fm_subtones_on_am_ssb_cw(self):
        for m in (Mode.AM,Mode.USB,Mode.LSB,Mode.CW):
            o=effective_control(UserSettings(mode=m,ctcss_rx=True,dcs_tx=True),Conditions())
            self.assertFalse(o['ctcss']);self.assertFalse(o['dcs'])
    def test_mutually_exclusive_ctcss_dcs(self):
        with self.assertRaises(ValueError):
            effective_control(UserSettings(mode=Mode.FM,ctcss_rx=True,dcs_tx=True),Conditions())
    def test_fm_code_allowed_independently(self):
        o=effective_control(UserSettings(mode=Mode.FM,ctcss_rx=True),Conditions())
        self.assertTrue(o['ctcss']);self.assertFalse(o['dcs'])
    def test_echo_off_in_cw(self):
        o=effective_control(UserSettings(mode=Mode.CW,echo=True), Conditions())
        self.assertFalse(o['echo'])
    def test_roger_beep_cannot_bypass_tx_guard(self):
        o=effective_control(UserSettings(roger_beep=True), Conditions(ptt=True))
        self.assertFalse(o['roger_beep'])

if __name__=='__main__': unittest.main(verbosity=2)
