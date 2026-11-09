import unittest,sys,itertools,random,math,csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
S=ROOT/'01_Specifiche/V6.2'
sys.path.insert(0,str(ROOT/'08_Firmware_Prototipi/V6.2'))
from interlock_model_v62 import load_contract,evaluate,tx_permitted
D=load_contract(ROOT)
GOOD={'SUP_3V3_OK':True,'BAT_UV_OK':True,'BAT_OV_OK':True,'RX_SAFE_NC':True,
      'PA_MODE_HW':False,'FAULT_LOOP_OK':True,'TX_ARM_REQUEST':True,'PTT_N':False,
      'TX_BENCH_KEY':True,'AMP_SD_REQUEST':True,'CODEC_READY':True,'AMP_FAULT_N':True,'PA_RELAY_CMD':True}
class TestInterlock(unittest.TestCase):
    def test_structure(self):
        self.assertEqual(len(D['gates']),15)
        self.assertEqual(sum(g['type']=='AND' for g in D['gates']),13)
        self.assertEqual(sum(g['type']=='NOT' for g in D['gates']),2)
    def test_parts_unique(self):
        refs=[p['ref'] for p in D['components']];self.assertEqual(len(refs),len(set(refs)))
    def test_unique_component_pins(self):
        v=[(p['ref'],p['pin']) for p in D['pins']];self.assertEqual(len(v),len(set(v)))
    def test_pinout_tps3823(self):
        p={int(x['pin']):x['net'] for x in D['pins'] if x['ref']=='U801'}
        self.assertEqual(p,{1:'SUP_3V3_OK',2:'DGND',3:'3V3_D',4:'WDI_HEARTBEAT',5:'3V3_D'})
    def test_pinout_tps3700(self):
        p={int(x['pin']):x['net'] for x in D['pins'] if x['ref']=='U802'}
        self.assertEqual(p,{1:'BAT_UV_OK',2:'DGND',3:'BAT_UV_SENSE',4:'BAT_OV_SENSE',5:'3V3_D',6:'BAT_OV_OK'})
    def test_logical_pinouts_and_ncs(self):
        for g in D['gates']:
            p={int(x['pin']):x['net'] for x in D['pins'] if x['ref']==g['ref']}
            self.assertEqual(p[3],'DGND');self.assertEqual(p[5],'3V3_D');self.assertEqual(p[4],g['y'])
            if g['type']=='AND':self.assertEqual((p[1],p[2]),(g['a'],g['b']))
            else:self.assertEqual(p[2],g['a']);self.assertTrue(p[1].startswith('NC_'))
    def test_no_crossvoltage_on_gates(self):
        for p in D['pins']:
            if p['ref'].startswith('U8') and p['ref'] not in ['U801','U802']:
                self.assertNotIn(p['net'],['13V8_PROTECTED','BAT_UV_SENSE','BAT_OV_SENSE'])
    def test_all_controls_default_to_safety_off(self):
        s=evaluate(D,{});self.assertFalse(s['TX_ENABLE_HARD']);self.assertFalse(s['AMP_SD']);self.assertFalse(s['PA_RELAY_EN'])
    def test_reachable_true_only_for_bench_test(self):
        s=evaluate(D,GOOD);self.assertTrue(s['TX_ENABLE_HARD']);self.assertTrue(s['AMP_SD']);self.assertFalse(s['PA_RELAY_EN'])
    def test_default_jumper_dni(self):
        q=GOOD.copy();q.pop('TX_BENCH_KEY');self.assertFalse(tx_permitted(D,q))
        jp=[c for c in D['components'] if c['ref']=='J801'][0];self.assertEqual(jp['status'],'DNI')
    def test_single_faults_in_required_healthy_paths(self):
        for sig in ['SUP_3V3_OK','BAT_UV_OK','BAT_OV_OK','RX_SAFE_NC','FAULT_LOOP_OK','TX_ARM_REQUEST','TX_BENCH_KEY']:
            q=GOOD.copy();q[sig]=False
            self.assertFalse(tx_permitted(D,q),sig)
    def test_no_ptt(self):
        q=GOOD.copy();q['PTT_N']=True;self.assertFalse(tx_permitted(D,q))
    def test_PA_veto_even_NC_stuck_closed(self):
        q=GOOD.copy();q['PA_MODE_HW']=True;self.assertFalse(tx_permitted(D,q))
    def test_fault_loop_break(self):
        q=GOOD.copy();q.pop('FAULT_LOOP_OK');self.assertFalse(tx_permitted(D,q))
    def test_8192_boolean_truth_table(self):
        keys=sorted(['SUP_3V3_OK','BAT_UV_OK','BAT_OV_OK','RX_SAFE_NC','PA_MODE_HW','FAULT_LOOP_OK',
                     'TX_ARM_REQUEST','PTT_N','TX_BENCH_KEY','AMP_SD_REQUEST','CODEC_READY','AMP_FAULT_N','PA_RELAY_CMD'])
        self.assertEqual(len(keys),13)
        true_count=0
        for bitset in range(1<<len(keys)):
            q={k:bool((bitset>>i)&1) for i,k in enumerate(keys)}
            actual=evaluate(D,q)
            tx=(q['SUP_3V3_OK'] and q['BAT_UV_OK'] and q['BAT_OV_OK'] and q['RX_SAFE_NC']
                and not q['PA_MODE_HW'] and q['FAULT_LOOP_OK'] and q['TX_ARM_REQUEST'] and not q['PTT_N'] and q['TX_BENCH_KEY'])
            self.assertEqual(actual['TX_ENABLE_HARD'],bool(tx))
            self.assertEqual(actual['AMP_SD'],q['AMP_SD_REQUEST'] and q['CODEC_READY'] and q['AMP_FAULT_N'] and actual['POWER_GOOD_HW'])
            self.assertEqual(actual['PA_RELAY_EN'],q['PA_RELAY_CMD'] and q['PA_MODE_HW'] and actual['POWER_GOOD_HW'])
            true_count+=bool(tx)
        self.assertEqual(true_count,16) # 4 unrelated AMP/RELAY switches => 2^4
    def test_tx_false_when_pa_relay_energized(self):
        q=GOOD.copy();q['PA_MODE_HW']=True; self.assertFalse(evaluate(D,q)['TX_ENABLE_HARD'])
    def test_amp_mute_if_voltage_fault(self):
        for sig in ['SUP_3V3_OK','BAT_UV_OK','BAT_OV_OK']:
            q=GOOD.copy();q[sig]=False;self.assertFalse(evaluate(D,q)['AMP_SD'])
    def test_power_good_independent_of_firmware(self):
        for arm in (False,True):
            q=GOOD.copy();q['TX_ARM_REQUEST']=arm
            self.assertTrue(evaluate(D,q)['POWER_GOOD_HW'])
    def test_thresholds_analytic(self):
        self.assertAlmostEqual(D['uv_threshold_nominal_v'],11.88,places=2)
        self.assertAlmostEqual(D['ov_threshold_nominal_v'],15.36,places=2)
    def test_threshold_montecarlo_50000(self):
        rng=random.Random(6262);lo=[];hi=[]
        for i in range(50000):
            vref=0.4*rng.uniform(0.99,1.01)
            def trip(upper):
                return vref*(1+upper*rng.uniform(0.99,1.01)/(10000*rng.uniform(0.99,1.01)))
            lo.append(trip(287000));hi.append(trip(374000))
        self.assertGreater(min(lo),11.5);self.assertLess(max(lo),12.4)
        self.assertGreater(min(hi),14.85);self.assertLess(max(hi),15.9)
        self.assertGreater(min(hi)-max(lo),2.5)
    def test_fault_bridge_high_with_key_open(self):
        q=GOOD.copy();q['TX_BENCH_KEY']=False
        for sig in ['PA_MODE_HW','PTT_N','TX_ARM_REQUEST','RX_SAFE_NC','FAULT_LOOP_OK']:
            s=q.copy();s[sig]=not s[sig];self.assertFalse(tx_permitted(D,s))
    def test_power_sense_filter_approx(self):
        self.assertGreater(4700*(287000*10000/(287000+10000))*1e-12,0)
        uv_t=(287000*10000/(287000+10000))*4.7e-9
        self.assertLess(uv_t,60e-6)
    def test_pin_correspondence_with_v61(self):
        v61=json.loads((ROOT/'01_Specifiche/V6.1/CIRCUITO_PIN_MCU_PANNELLO_V6.1.json').read_text(encoding='utf8'))
        nets={x['net'] for x in v61['pins'] if x['ref']=='U201'}
        for n in ['PTT_N','AMP_SD_REQUEST','PA_RELAY_CMD','POWER_GOOD','AMP_FAULT_N']:
            self.assertIn(n,nets)
        # ECO: two firmware pins formerly reserved, no unsafe forced reuse of PA9 / SWD
        m={x['pin']:x['net'] for x in v61['pins'] if x['ref']=='U201'}
        self.assertEqual(m['33'],'PB11_RESERVE');self.assertEqual(m['57'],'PB4_RESERVE')
        self.assertEqual(m['43'],'AUDIO_WCLK');self.assertEqual(m['49'],'SWDIO')
    def test_pa_mechanical_eco_logged(self):
        self.assertIn('SPDT',D['v61_eco_required']['PA_mode_switch'])
        n={x['net'] for x in D['pins'] if x['ref']=='S801'}
        self.assertEqual(n,{'RX_SAFE_NC','PA_MODE_HW','3V3_D'})
    def test_tps3700_open_drain_pullups(self):
        pp=[x for x in D['pins'] if x['net'] in ('BAT_UV_OK','BAT_OV_OK')]
        for ref in ('R805','R806'): self.assertEqual(len([x for x in pp if x['ref']==ref]),1)
    def test_interface_conns_unique(self):
        p=[x['net'] for x in D['pins'] if x['ref']=='J803'];self.assertEqual(len(p),len(set(p)))
        for n in ['AMP_SD','PA_RELAY_EN','TX_ENABLE_HARD','POWER_GOOD_HW']:
            self.assertIn(n,p)
    def test_inverter_missing_net_detected(self):
        broken=json.loads(json.dumps(D));broken['gates'][0]['a']='ABSENT_SIGNAL'
        with self.assertRaises(AssertionError): evaluate(broken,GOOD)
    def test_gate_tamper_detected_by_expected(self):
        broken=json.loads(json.dumps(D));broken['gates'][-8]['a']='PA_MODE_HW'
        q=GOOD.copy();self.assertNotEqual(evaluate(broken,q)['TX_ENABLE_HARD'],evaluate(D,q)['TX_ENABLE_HARD'])
    def test_no_tx_enabled_in_contract(self):
        self.assertFalse(D['production_release']);self.assertFalse(D['tx_hardware_connected'])
        self.assertFalse(D['rf_transmission_permitted'])
    def test_bom_csv_counts(self):
        with (ROOT/'07_Componenti/BOM_INTERBLOCCHI_V6.2.csv').open(newline='',encoding='utf8') as f:rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),len(D['components']))
    def test_reject_undefined_input(self):
        with self.assertRaises(ValueError):evaluate(D,{'RF_TX_PERMISSION':True})
if __name__=='__main__':unittest.main(verbosity=2)
