#!/usr/bin/env python3
"""70 reproducible static/numerical RX checks, NOT KiCad ERC/DRC or silicon tests."""
import sys,math,csv,json,itertools,unittest,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent

def imp(name,path):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m
M=imp('v69_planner',ROOT/'08_Firmware_Prototipi/V6.9/lo2_bfo_planner_v69.py')
S=imp('v69_sim',HERE/'simula_lo2_demod_v69.py')
def readcsv(path):
    with path.open(newline='',encoding='utf8') as f:return list(csv.DictReader(f))
PLAN=readcsv(ROOT/'02_Piano_Frequenze/V6.9/PIANO_270_X_5_SI5351C_V6.9.csv')
OLD=readcsv(ROOT/'02_Piano_Frequenze/V6.8/PIANO_270_X_5_IF2_V6.8.csv')
PINS=readcsv(ROOT/'01_Specifiche/V6.9/NETLIST_PIN_LO2_DEMOD_V6.9.csv')
BOM=readcsv(ROOT/'07_Componenti/BOM_LO2_DEMOD_V6.9.csv')
PINMCU=readcsv(ROOT/'01_Specifiche/V6.9/RISERVA_PIN_MCU_V6.9.csv')
RES=json.loads((HERE/'RISULTATI_SIMULAZIONI_V6.9.json').read_text(encoding='utf8'))

def pin(ref,n,net):return any(p['ref']==ref and p['pin_or_terminal']==str(n) and p['net']==net for p in PINS)

def good():
    return M.RxInputs(rx_switch_closed=True,pa_selected=False,ptt_active=False,supply_good=True,pll1_lock=True,
       lo2_pll_status_ok=True,lo2_config_committed=True,filter_ready=True,mode_valid=True,
       retune_in_progress=False,ref_clock_present=True,hardware_rx_consent=True)

class V69(unittest.TestCase):
    def test_01_plan_1350(self):self.assertEqual(len(PLAN),1350)
    def test_02_270_unique(self):self.assertEqual(len({(r['band'],r['channel']) for r in PLAN}),270)
    def test_03_modes(self):self.assertEqual({x['mode'] for x in PLAN},set(M.MODE_FREQS))
    def test_04_old_equiv(self):self.assertEqual([(x['band'],x['channel'],x['rf_hz'],x['lo1_hz'],x['mode']) for x in PLAN],[(x['band'],x['channel'],x['rf_hz'],x['lo1_hz'],x['mode']) for x in OLD])
    def test_05_ref_div(self):self.assertEqual(M.PLL_VCO_HZ/M.REF_HZ,62.5)
    def test_06_all_lo2_math_exact(self):self.assertTrue(all(int(r['arithmetic_error_hz'])==0 for r in PLAN))
    def test_07_all_plla(self):self.assertTrue(all(r['lo2_pll']=='PLLA' for r in PLAN))
    def test_08_all_lo2_r_one(self):self.assertTrue(all(r['lo2_r_div']=='1' for r in PLAN))
    def test_09_am_bfo_disabled(self):self.assertTrue(all(not r['bfo_hz'] and r['bfo_pll']=='DISABLED' for r in PLAN if r['mode']=='AM'))
    def test_10_fm_bfo_disabled(self):self.assertTrue(all(not r['bfo_hz'] and r['bfo_pll']=='DISABLED' for r in PLAN if r['mode']=='FM'))
    def test_11_ssb_bfo_pllb(self):self.assertTrue(all(r['bfo_pll']=='PLLB' and r['bfo_r_div']=='16' for r in PLAN if r['mode'] in ('USB','LSB','CW')))
    def test_12_bfo_700(self):self.assertEqual(M.MODE_FREQS['CW'][1]-455000,700)
    def test_13_usb_bfo(self):self.assertEqual(M.plan('USB')['bfo_hz'],456500)
    def test_14_lsb_bfo(self):self.assertEqual(M.plan('LSB')['bfo_hz'],453500)
    def test_15_pll_in_bounds(self):self.assertTrue(600e6<=M.PLL_VCO_HZ<=900e6)
    def test_16_den_lt_max(self):self.assertTrue(all(int(x['lo2_ms_c'])<=M.MAX_DEN and (not x['bfo_ms_c'] or int(x['bfo_ms_c'])<=M.MAX_DEN) for x in PLAN))
    def test_17_bom_unique(self):self.assertEqual(len(BOM),len(set(r['ref'] for r in BOM)))
    def test_18_pin_unique(self):self.assertEqual(len(PINS),len(set((r['ref'],r['pin_or_terminal']) for r in PINS)))
    def test_19_all_component_coverage(self):self.assertEqual({r['ref'] for r in BOM},{r['ref'] for r in PINS})
    def test_20_si_qfn_20(self):self.assertEqual({int(x['pin_or_terminal']) for x in PINS if x['ref']=='U971' and x['pin_or_terminal'].isdigit()},set(range(1,21)))
    def test_21_si_clk_in(self):self.assertTrue(pin('U971',6,'REF_12M8_BUFFERED'))
    def test_22_si_clk0(self):self.assertTrue(pin('U971',13,'LO2_CMOS_RAW'))
    def test_23_si_clk1(self):self.assertTrue(pin('U971',12,'BFO_CMOS_RAW'))
    def test_24_si_oeb(self):self.assertTrue(pin('U971',7,'LO2_OEB_N'))
    def test_25_oeb_pull_up(self):self.assertTrue(pin('R971',1,'3V3_LO2') and pin('R971',2,'LO2_OEB_N'))
    def test_26_gate_pull_down(self):self.assertTrue(pin('R972',2,'GND_SYNTH') and pin('Q971','G','LO2_DRIVE_GATE'))
    def test_27_20qfn_banks(self):self.assertTrue(all(pin('U971',p,'3V3_LO2') for p in (10,11,14,18,20)))
    def test_28_si_i2c(self):self.assertTrue(pin('U971',4,'CODEC_I2C_SCL') and pin('U971',5,'CODEC_I2C_SDA'))
    def test_29_switch_pinout(self):self.assertTrue(all(pin('U981',n,net) for n,net in [(1,'IF2_INV_BIASED'),(2,'AGND_IF2'),(3,'IF2_NONINV_BIASED'),(4,'SSB_SWITCHED_BIASED'),(5,'3V3_A_IF'),(6,'BFO_LOGIC_3V3')]))
    def test_30_mcu_spares(self):self.assertEqual({r['mcu_pad'] for r in PINMCU},{'PB6','PB7','PC12','PB11'})
    def test_31_tx_unwired(self):self.assertFalse(any(x['net'].startswith('TX_') or x['net'].startswith('PA_RF_') for x in PINS))
    def test_32_models_fft(self):self.assertEqual(set(RES['demod']),set(M.MODE_FREQS))
    def test_33_audio_four_1k(self):self.assertTrue(all(abs(RES['demod'][x]['peak_hz']-1000)<5 for x in ('USB','LSB','AM','FM')))
    def test_34_cw_700(self):self.assertAlmostEqual(RES['demod']['CW']['peak_hz'],700,delta=5)
    def test_35_good_and_failclosed(self):
        x=good();self.assertTrue(M.permit_audio(x));self.assertTrue(M.lo2_request(x));self.assertFalse(M.tx_authorized(x))
        self.assertFalse(M.permit_audio(M.RxInputs()))

# 35 channel/mode checks as separate unittest cases, cross-compared with the inherited IF2 table.
for ci,channel_key in enumerate(sorted({(r['band'],r['channel']) for r in PLAN})[::39][:7]):
    for mi,mode in enumerate(('AM','FM','USB','LSB','CW')):
        def check(self,ch=channel_key,m=mode):
            candidates=[r for r in PLAN if (r['band'],r['channel'],r['mode'])==(ch[0],ch[1],m)]
            self.assertEqual(len(candidates),1)
            r=candidates[0];p=M.plan(m)
            self.assertEqual(int(r['lo2_hz']),p['lo2_hz'])
            self.assertEqual(int(r['lo2_ms_a']),p['lo2_ratio'].n_int)
            self.assertEqual(int(r['lo2_ms_b']),p['lo2_ratio'].n_num)
            self.assertEqual(int(r['lo2_ms_c']),p['lo2_ratio'].n_den)
            self.assertEqual(int(r['bfo_hz']) if r['bfo_hz'] else None,p['bfo_hz'])
            if p['bfo_ratio']:
                self.assertEqual(int(r['bfo_ms_c']),p['bfo_ratio'].n_den)
        setattr(V69,f'test_{36+ci*5+mi:02d}_channel_{ci}_{mode}',check)

# Extra explicitly separate safety state enumeration (4,096 inputs) and all previous modes, no test count inflation.
def exhaustive_safety():
    from dataclasses import fields
    names=[f.name for f in fields(M.RxInputs)]
    count=0; valid_count=0
    for bits in itertools.product((False,True),repeat=len(names)):
        state=M.RxInputs(**dict(zip(names,bits)))
        want=(state.rx_switch_closed and not state.pa_selected and not state.ptt_active
           and state.supply_good and state.pll1_lock and state.lo2_pll_status_ok
           and state.lo2_config_committed and state.filter_ready and state.mode_valid
           and not state.retune_in_progress and state.ref_clock_present
           and state.hardware_rx_consent)
        assert M.permit_audio(state)==want
        assert M.lo2_request(state)==want
        assert M.tx_authorized(state) is False
        count+=1;valid_count+=int(want)
    assert count==4096 and valid_count==1
    return count

if __name__=='__main__':
    print('FAIL-CLOSED state combinations',exhaustive_safety())
    unittest.main(verbosity=1)
