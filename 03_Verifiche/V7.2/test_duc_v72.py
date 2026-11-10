"""Model-only V7.2 tests; no TX access or hardware side effects."""
import csv
from itertools import product
from math import cos, pi, log10
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'08_Firmware_Prototipi'/'V7.2'))
import duc_if2_offline_v72 as d

N=384
FS=d.AUDIO_FS
AUDIO=[0.45*cos(2*pi*750*i/FS)+0.3*cos(2*pi*1250*i/FS) for i in range(N)]

class V72(unittest.TestCase):
    def test_sample_rates_and_nyquist(self):
        self.assertEqual(d.IF2_FS,3840000)
        self.assertEqual(d.IF2_FS//d.AUDIO_FS,80)
        self.assertGreater(d.IF2_FS,2*(d.IF2_HZ+5000))
        self.assertEqual(d.LO2_HZ+d.IF2_HZ,d.IF1_HZ)

    def test_circular_interpolation(self):
        up=d.interpolate_periodic(AUDIO)
        self.assertEqual(len(up),N*80)
        for i in range(N):
            self.assertAlmostEqual(up[i*80],AUDIO[i],places=8)
        flat=d.interpolate_periodic([0.27]*N)
        self.assertTrue(all(abs(v-0.27)<1e-9 for v in flat))

    def test_ssb_two_tones_and_unwanted_sidebands(self):
        for mode,sign in (("USB",-1),("LSB",1)):
            y=d.if2_synthesize(mode,AUDIO)
            for f in (750,1250):
                wanted=d.coherent_tone_amplitude(y,d.IF2_HZ+sign*f)
                unwanted=d.coherent_tone_amplitude(y,d.IF2_HZ-sign*f)
                db=20*log10(max(unwanted,1e-12)/wanted)
                self.assertGreater(wanted,0.2)
                self.assertLess(db,-30,(mode,f,db))
            self.assertLess(d.coherent_tone_amplitude(y,d.IF2_HZ),0.02)

    def test_am_multitone_sidebands_and_carrier(self):
        y=d.if2_synthesize('AM',AUDIO,am_depth=0.35)
        carrier=d.coherent_tone_amplitude(y,d.IF2_HZ)
        self.assertAlmostEqual(carrier,1,delta=0.015)
        for freq,mag in ((750,0.45),(1250,0.30)):
            for sign in (-1,1):
                side=d.coherent_tone_amplitude(y,d.IF2_HZ+sign*freq)
                self.assertAlmostEqual(side,0.35*mag/2,delta=0.012)

    def test_fm_frequency_inversion_and_multitone(self):
        # DC test is coherent with 8ms: modulation +0.20 -> -500Hz IF2.
        dc=[0.20]*N
        y=d.if2_synthesize('FM',dc,deviation_hz=2500)
        wanted=d.coherent_tone_amplitude(y,d.IF2_HZ-500)
        unwanted=d.coherent_tone_amplitude(y,d.IF2_HZ+500)
        self.assertGreater(wanted,0.98)
        self.assertLess(unwanted,0.015)
        multi=d.if2_synthesize('FM',AUDIO)
        self.assertEqual(len(multi),N*80)
        self.assertGreater(max(multi)-min(multi),1.9)

    def test_cw_key_off_and_raised_envelope(self):
        off=d.if2_synthesize('CW',AUDIO)
        self.assertEqual(set(off),{0.0})
        on=d.if2_synthesize('CW',AUDIO,cw_key_down=True)
        self.assertAlmostEqual(on[0],0,places=10)
        self.assertGreater(max(on),0.95)
        self.assertLess(abs(on[-1]),0.01)

    def test_input_rejections(self):
        bad=[float('nan')]*N
        with self.assertRaises(ValueError): d.if2_synthesize('AM',bad)
        with self.assertRaises(ValueError): d.if2_synthesize('AM',[1.2]*N)
        with self.assertRaises(ValueError): d.if2_synthesize('AM',[0.1]*80)
        with self.assertRaises(ValueError): d.if2_synthesize('TX',AUDIO)
        with self.assertRaises(ValueError): d.if2_synthesize('FM',AUDIO,deviation_hz=9000)
        with self.assertRaises(ValueError): d.coherent_tone_amplitude([0.0]*320,455001)

    def test_hardware_disabled_for_128_logic_states(self):
        self.assertFalse(d.TX_HW_ENABLED)
        self.assertFalse(d.TX_DAC_PRESENT)
        self.assertFalse(d.TX_RF_OUTPUT_ROUTED)
        for states in product((False,True),repeat=7):
            self.assertIs(d.tx_permission(**dict(zip(('ptt','pa','fault','pll','watchdog','bench','mcu'),states))),False)

    def test_ideal_bpf_study_is_math_not_vendor(self):
        if_center=d.filter_ideal_bpf_loss_db(10695000,10685000,10705000,2)
        if_spur=d.filter_ideal_bpf_loss_db(9785000,10685000,10705000,2)
        rf_image=d.filter_ideal_bpf_loss_db(47005000,25000000,29000000,5)
        rf_edge=d.filter_ideal_bpf_loss_db(25615000,25000000,29000000,5)
        self.assertAlmostEqual(if_center,0,places=5)
        self.assertGreater(if_spur,70)
        self.assertGreater(rf_image,70)
        self.assertLess(rf_edge,1)

    def test_full_270_channel_ideal_filter_sweep(self):
        sys.path.insert(0, str(ROOT/'03_Verifiche'/'V7.2'))
        import analizza_filtri_v72 as survey
        stats=survey.evaluate()
        self.assertEqual(stats['channels'],270)
        self.assertEqual(stats['alpha_count'],30)
        self.assertGreater(stats['if1_lower_spur_9785_loss_db'],79)
        self.assertLess(stats['rf_wanted_max_ideal_loss_db'],0.09)
        self.assertGreater(stats['rf_image_min_relative_ideal_loss_db'],89)
        self.assertGreater(stats['rf_lo_leak_min_relative_ideal_loss_db'],60)
        self.assertIs(stats['rf_tx_permitted'],False)

    def test_repository_dnp_and_v71_regression(self):
        bom=ROOT/'07_Componenti'/'BOM_DUC_IF2_V7.2.csv'
        net=ROOT/'01_Specifiche'/'V7.2'/'NETLIST_DUC_IF2_V7.2.csv'
        plan=ROOT/'02_Piano_Frequenze'/'V6.4'/'PIANO_PLL_LO_270_RX_V6.4.csv'
        for path in (bom,net,plan):
            self.assertTrue(path.is_file(),f'missing required {path}')
        with bom.open(newline='',encoding='utf-8') as f: rows=list(csv.DictReader(f))
        with net.open(newline='',encoding='utf-8') as f: pins=list(csv.DictReader(f))
        with plan.open(newline='',encoding='utf-8') as f: channels=list(csv.DictReader(f))
        self.assertEqual(len(rows),8)
        self.assertEqual(len(pins),12)
        self.assertTrue(all(r['assembly']=='DNP' for r in rows))
        self.assertTrue(all(r['assembly']=='DNP' for r in pins))
        self.assertEqual(len(channels),270)
        self.assertEqual(sum(r['alfa']=='1' for r in channels),30)
        for r in channels:
            self.assertEqual(int(r['lo_hz']),int(r['rf_hz'])+d.IF1_HZ)
            self.assertEqual(int(r['tx_permitted_v64']),0)

if __name__ == '__main__': unittest.main()
