"""V7.3 pure software/CSV tests, no hardware or DAC access.

Run: python3 -B -m unittest discover -s 03_Verifiche/V7.3 -p 'test_*.py' -v
"""
import csv
import math
from itertools import product
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"08_Firmware_Prototipi"/"V7.3"))
sys.path.insert(0,str(ROOT/"08_Firmware_Prototipi"/"V7.2"))
sys.path.insert(0,str(ROOT/"03_Verifiche"/"V7.3"))
import duc_if2_causale_v73 as m
import duc_if2_offline_v72 as old
import analizza_reconstruction_lpf_v73 as lpf


def tones(n, start=0):
    return [0.45*math.cos(2*math.pi*750*(start+i)/m.AUDIO_RATE_HZ)
           +0.3*math.cos(2*math.pi*1250*(start+i)/m.AUDIO_RATE_HZ)
           for i in range(n)]


class TestV73(unittest.TestCase):
    def test_01_rates_and_latency(self):
        self.assertEqual(m.AUDIO_RATE_HZ,48000)
        self.assertEqual(m.OUTPUT_RATE_HZ,3840000)
        self.assertEqual(m.DAC_BITS,10)
        self.assertEqual(m.DAC_MPN,"DAC900E")
        self.assertGreater(m.OUTPUT_RATE_HZ,2*(m.IF2_HZ+2700))
        self.assertEqual(m.CausalIF2("USB").diagnostics()["latency_audio_samples"],143.5)

    def test_02_split_blocks_identical_usb(self):
        audio=tones(320)
        one=m.CausalIF2("USB").process(audio[:320])
        state=m.CausalIF2("USB")
        segments=[audio[:27],audio[27:128],audio[128:211],audio[211:]]
        blocks=sum((state.process(x) for x in segments),[])
        self.assertEqual(blocks,one)
        self.assertEqual(state.diagnostics()["audio_samples"],320)
        self.assertEqual(state.diagnostics()["if2_samples"],25600)

    def test_03_split_blocks_identical_fm(self):
        audio=tones(256)
        one=m.CausalIF2("FM").process(audio)
        state=m.CausalIF2("FM")
        pieces=state.process(audio[:1])+state.process(audio[1:127])+state.process([])+state.process(audio[127:])
        self.assertEqual(one,pieces)

    def test_04_split_blocks_identical_am(self):
        audio=tones(192)
        one=m.CausalIF2("AM",am_depth=0.35).process(audio)
        state=m.CausalIF2("AM",am_depth=0.35)
        self.assertEqual(one,state.process(audio[:111])+state.process(audio[111:]))

    def test_05_ssb_unwanted_sideband_steady_nonperiodic_stream(self):
        # Input stream has 128-sample startup and a 257-tap causal Hilbert.
        # Analyze only last coherent 384 samples after transient has passed.
        signal=tones(1024)
        for mode,sign in (("USB",-1),("LSB",1)):
            st=m.CausalIF2(mode)
            y=[]
            for start in range(0,len(signal),256):
                y.extend(st.process(signal[start:start+256]))
            window=y[-384*m.UPSAMPLE:]
            for freq,amplitude in ((750,0.45),(1250,0.3)):
                wanted=old.coherent_tone_amplitude(window,m.IF2_HZ+sign*freq)
                unwanted=old.coherent_tone_amplitude(window,m.IF2_HZ-sign*freq)
                suppression=20*math.log10(max(unwanted,1e-12)/wanted)
                self.assertGreater(wanted,0.6*amplitude,(mode,freq,wanted))
                self.assertLess(suppression,-23,(mode,freq,suppression))

    def test_06_no_circular_wrap_at_step(self):
        st=m.CausalIF2("USB")
        zeros=st.process([0.0]*150)
        self.assertTrue(all(z==0.0 for z in zeros))
        start=st.process([0.8]*256)
        self.assertLess(abs(start[0]),1e-10)
        self.assertGreater(max(abs(z) for z in start),0.2)

    def test_07_cw_keying_stateful_ramps(self):
        cw=m.CausalIF2("CW")
        up=cw.process([0.0]*96,cw_key_down=True)
        self.assertEqual(len(up),7680)
        self.assertLess(abs(up[0]),1e-5)
        self.assertGreater(max(up[-160:]),0.9)
        down=cw.process([0.0]*96,cw_key_down=False)
        self.assertLess(abs(down[-1]),1e-5)
        again=cw.process([0.0]*16,cw_key_down=False)
        self.assertEqual(set(again),{0.0})

    def test_08_quantization_range_and_fail_closed_overrange(self):
        codes=m.quantize_unsigned_10bit([-1,0,1])
        self.assertEqual(len(codes),3)
        self.assertTrue(0<codes[0]<codes[1]<codes[2]<1023)
        with self.assertRaises(ValueError):
            m.quantize_unsigned_10bit([1.5])
        with self.assertRaises(ValueError):
            m.quantize_unsigned_10bit([float("nan")])
        with self.assertRaises(ValueError):
            m.quantize_unsigned_10bit([0.2],headroom=0.0)

    def test_09_input_validation_and_reset(self):
        with self.assertRaises(ValueError): m.CausalIF2("TX")
        with self.assertRaises(ValueError): m.CausalIF2("AM",am_depth=1.0)
        st=m.CausalIF2("LSB")
        with self.assertRaises(ValueError): st.process([1.2])
        with self.assertRaises(ValueError): st.process([float("inf")])
        with self.assertRaises(ValueError): st.process([0.0]*513)
        _=st.process(tones(32))
        self.assertEqual(st.diagnostics()["audio_samples"],32)
        st.reset()
        self.assertEqual(st.diagnostics()["audio_samples"],0)
        self.assertEqual(st.process(tones(64)),m.CausalIF2("LSB").process(tones(64)))

    def test_10_naive_dsp_budget_no_real_time_claims(self):
        b=m.compute_budget()
        self.assertEqual(b["raw_parallel_data_bits_per_sec"],38400000)
        self.assertEqual(b["polyphase_macs_per_sec"],122880000)
        self.assertEqual(b["hilbert_nonzero_macs_per_sec"],6144000)
        self.assertEqual(b["combined_naive_macs_per_sec"],129024000)
        self.assertFalse(b["rf_tx_permitted"])
        self.assertFalse(b["analogue_lpf_present"])

    def test_11_all_controls_fail_closed(self):
        self.assertFalse(m.TX_RF_ENABLED)
        self.assertFalse(m.DAC_MOUNTED)
        self.assertFalse(m.IF2_CONNECTED_TO_MIXER)
        self.assertFalse(m.PA_CONNECTED)
        for flags in product((False,True),repeat=8):
            self.assertIs(m.tx_permission(**dict(zip(("ptt","pa","mcu","fault","bench","pll","dac","clock"),flags))),False)

    def test_12_dac900_pinout_and_all_dnp(self):
        path=ROOT/"01_Specifiche"/"V7.3"/"NETLIST_PIN_DAC900_V7.3.csv"
        bom=ROOT/"07_Componenti"/"BOM_DUC_DAC_V7.3.csv"
        with path.open(newline="",encoding="utf-8") as f: rows=list(csv.DictReader(f))
        with bom.open(newline="",encoding="utf-8") as f: comp=list(csv.DictReader(f))
        self.assertEqual(len(comp),12)
        self.assertEqual(len(rows),42)
        self.assertTrue(all(r["assembly"]=="DNP" for r in comp+rows))
        pins={int(r["pin"]):r["function"] for r in rows if r["reference"]=="U7401"}
        self.assertEqual(set(pins),set(range(1,29)))
        expected={1:"D9",10:"D0",11:"NC",14:"NC",15:"PD_ACTIVE_HIGH",
                  16:"INT_EXT",17:"REFIN",18:"FSA",19:"BW",20:"AGND",
                  21:"IOUTB",22:"IOUT",23:"BYP",24:"VA",25:"NC",
                  26:"DGND",27:"VD",28:"CLK"}
        for p,v in expected.items(): self.assertEqual(pins[p],v)
        for p in (21,22):
            net=next(row["concept_net"] for row in rows
                     if row["reference"]=="U7401" and int(row["pin"])==p)
            self.assertIn("UNROUTED",net)
        self.assertEqual(next(r["vendor_mpn"] for r in comp if r["reference"]=="U7401"),
                         "Texas Instruments DAC900E")

    def test_13_lpf_ladder_symmetric(self):
        vals=lpf.nominal_elements()
        self.assertEqual(len(vals),7)
        self.assertEqual([a for a,_ in vals],list("LCLCLCL"))
        self.assertAlmostEqual(vals[0][1],vals[-1][1],places=15)
        self.assertAlmostEqual(vals[1][1],vals[-2][1],places=15)
        self.assertLess(lpf.insertion_loss_db(455000),0.02)
        self.assertGreater(lpf.insertion_loss_db(3385000),70)
        self.assertLess(lpf.insertion_loss_db(455000,q_inductor=80,q_capacitor=500),6)

    def test_14_lpf_monte_carlo_is_reproducible(self):
        a=lpf.evaluate(n_scenarios=100,seed=73)
        b=lpf.evaluate(n_scenarios=100,seed=73)
        self.assertEqual(a,b)
        self.assertGreater(a["nominal_min_image_relative_attenuation_db"],70)
        self.assertGreater(a["mc_min_relative_image_attenuation_db"],35)
        self.assertLess(a["mc_max_wanted_loss_db"],12)
        self.assertFalse(a["hardware_verified"])
        self.assertFalse(a["tx_permitted"])

    def test_15_historic_frequency_plan_remains_rx_only(self):
        path=ROOT/"02_Piano_Frequenze"/"V6.4"/"PIANO_PLL_LO_270_RX_V6.4.csv"
        with path.open(newline="",encoding="utf-8") as f: rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),270)
        self.assertEqual(sum(int(r["alfa"]) for r in rows),30)
        for r in rows:
            self.assertEqual(int(r["tx_permitted_v64"]),0)
            self.assertEqual(int(r["lo_hz"]),int(r["rf_hz"])+10695000)


if __name__=="__main__":
    unittest.main()
