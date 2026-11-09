#!/usr/bin/env python3
"""Static/ideal tests and deliberate fault injection, no native ERC or SPICE claims."""
import unittest,json,sys,copy,math,csv,itertools
from pathlib import Path
R=Path(__file__).resolve().parents[2]
D=json.loads((R/'01_Specifiche/V6.3/ALIMENTAZIONI_CANDIDATE_V6.3.json').read_text())
S=json.loads((R/'03_Verifiche/V6.3/SIMULAZIONI_NUMERICHE_V6.3.json').read_text())
sys.path.insert(0,str(R/'08_Firmware_Prototipi/V6.3'))
from power_supervisor_contract_v63 import PowerStatus,evaluate
COMP={x['ref']:x for x in D['components']}
N={(x['ref'],x['terminal']):x['net'] for x in D['functional_terminals']}

def audit(d):
    parts=d['components'];pins=d['functional_terminals']
    refs=[x['ref'] for x in parts]
    if len(refs)!=len(set(refs)):raise ValueError('duplicate ref')
    keys=[(x['ref'],x['terminal']) for x in pins]
    if len(keys)!=len(set(keys)):raise ValueError('duplicate functional terminal')
    if set(x['ref'] for x in pins)!=set(refs):raise ValueError('parts mismatch')
    nets={x['net'] for x in pins}
    if any(x['net'] in {'RF_PA_VOLTAGE','TX_ENABLE_HARD','TX_POWER_VDD'} for x in pins):raise ValueError('RF TX must remain disconnected')
    for v in ['3V3_D','3V3_UI','5V_MAIN','13V8_PROTECTED','13V8_AUD','5V_RF','3V3_A','1V8_CODEC']:
        if v not in nets:raise ValueError('missing rail '+v)
    if any(p['qualification']!='DNI' for p in parts if p['ref'] in {'J902','J907'}):raise ValueError('DNI violation')
    tr={(x['ref'],x['terminal']):x['net'] for x in pins}
    required={('S901','A'):'13V8_FILTERED',('S901','B'):'PROTECT_ENABLE',
       ('R902','B'):'PGND',('R915','A'):'13V8_PROTECTED',
       ('U902','EN_SYNC'):'BUCK_EN',('U903','EN_SYNC'):'BUCK_EN',
       ('Q901','S'):'13V8_FILTERED',('Q901','D'):'13V8_SNS_P',
       ('Q902','S'):'13V8_PROTECTED',('R901','PLUS'):'13V8_SNS_P',
       ('R901','MINUS'):'13V8_SNS_M',('J907','RF_PA_PIN'):'RF_PA_DISCONNECTED',
       ('L901','IN_N'):'PGND_RAW',('L901','OUT_N'):'PGND',
       ('U904','IN'):'5V_MAIN',('U905','IN'):'3V3_D',
       ('R916','A'):'3V3_D',('R917','A'):'3V3_D',
       ('U906','A'):'PG_5V',('U906','B'):'PG_3V3',('U906','Y'):'PWR_GOOD_HW'}
    for k,v in required.items():
        if tr.get(k)!=v:raise ValueError('wrong pin '+repr((k,tr.get(k),v)))
    edges=d['power_flow']
    by={}
    for a,b,drv in edges:
       if b in by:raise ValueError('duplicate rail sources')
       by[b]=a
    for b in by:
       reached={b};p=b
       while p in by:
         p=by[p]
         if p in reached:raise ValueError('power cyclic dependency')
         reached.add(p)
       if p!='13V8_RAW':raise ValueError('supply not rooted')
    loads=d['loads']
    if len(set(x['load'] for x in loads))!=len(loads):raise ValueError('duplicate load')
    if any(x['nominal_a']>x['envelope_a'] or x['nominal_a']<=0 for x in loads):raise ValueError('invalid current envelope')
    if any(x['rail'] not in by for x in loads):raise ValueError('unpowered load')
    if d['release']['rf_pa_power_connected'] or d['release']['rf_tx'] or d['release']['board_fabrication'] or d['release']['native_spice']:raise ValueError('unsafe release')
    return True

class Tests(unittest.TestCase):
 def test_metadata(self):self.assertEqual(D['revision'],'V6.3');self.assertFalse(D['release']['native_kicad'])
 def test_contract(self):self.assertTrue(audit(D))
 def test_counts(self):self.assertEqual(len(COMP),79);self.assertEqual(len(N),219)
 def test_unique_refs(self):self.assertEqual(len(COMP),len(D['components']))
 def test_unique_terminal_refs(self):self.assertEqual(len(N),len(D['functional_terminals']))
 def test_input_paths(self):self.assertEqual(N['J901','GND'],'PGND_RAW');self.assertEqual(N['D901','A'],'13V8_FUSED')
 def test_cm_filter_not_bypassed_by_same_net(self):self.assertNotEqual(N['L901','IN_N'],N['L901','OUT_N'])
 def test_power_switch_not_dependency(self):self.assertEqual(N['S901','A'],'13V8_FILTERED');self.assertNotEqual(N['J902','B'],'3V3_D')
 def test_enable_buck_is_from_protected(self):self.assertEqual(N['R915','A'],'13V8_PROTECTED')
 def test_mosfet_common_drains(self):self.assertEqual(N['Q901','D'],'13V8_SNS_P');self.assertEqual(N['Q902','D'],'13V8_SNS_M')
 def test_fet_shunt_series(self):self.assertEqual(N['R901','PLUS'],N['Q901','D']);self.assertEqual(N['R901','MINUS'],N['Q902','D'])
 def test_bridge_unpopulated(self):self.assertEqual(COMP['J907']['qualification'],'DNI')
 def test_no_rf_pa_feed(self):self.assertNotIn('RF_PA_DISCONNECTED',[e[1] for e in D['power_flow']])
 def test_protection_controller(self):self.assertEqual(COMP['U901']['mpn'],'LM74900-Q1')
 def test_regulators(self):self.assertEqual(COMP['U902']['mpn'],COMP['U903']['mpn']);self.assertEqual(COMP['U902']['mpn'],'LM61460')
 def test_rail_names(self):self.assertIn('13V8_AUD',[p[1] for p in D['power_flow']])
 def test_audio_btl_separate(self):self.assertEqual(N['Q903','OUT'],'13V8_AUD');self.assertNotIn('13V8_AUD',[x['net'] for x in D['functional_terminals'] if x['ref'].startswith('U90') and x['ref'] not in ['U901']])
 def test_ldo_limit(self):
  self.assertLessEqual(D['branches']['3V3_A']['max_a'],.3);self.assertLessEqual(D['branches']['1V8_CODEC']['max_a'],.3)
 def test_5v_load_margin(self):self.assertLess(S['monte_carlo_stats']['buck5_out_a']['max'],2.0)
 def test_3v3_load_margin(self):self.assertLess(S['monte_carlo_stats']['buck3v3_out_a']['max'],1.2)
 def test_vref_feedback_5v(self):self.assertAlmostEqual(S['feedback_5v_from_100k_24k9_v'],5.016064,places=4)
 def test_vref_feedback_3v3(self):self.assertAlmostEqual(S['feedback_3v3_from_100k_43k2_v'],3.314815,places=4)
 def test_softstart_math(self):
  ss=S['ideal_inrush'];self.assertAlmostEqual(ss['current_charge_a'],.55,places=3);self.assertAlmostEqual(ss['ramp_time_to_13v8_ms'],11.79,delta=.3)
 def test_ccm_caveat(self):self.assertTrue(all('CCM' in x['assumptions'] for x in S['buck_ccm_only']))
 def test_voltage_below_uv(self):self.assertFalse([x for x in S['voltage_window_nominal_samples'] if x['vbat_v']==11][0]['v62_window_nominal'])
 def test_voltage_above_ov(self):self.assertFalse([x for x in S['voltage_window_nominal_samples'] if x['vbat_v']==16][0]['v62_window_nominal'])
 def test_normal_window(self):self.assertTrue([x for x in S['voltage_window_nominal_samples'] if x['vbat_v']==13.8][0]['v62_window_nominal'])
 def test_fail_default(self):
  o=evaluate(PowerStatus());self.assertFalse(any(o.values()))
 def test_good_power_no_tx(self):
  o=evaluate(PowerStatus(True,True,True,True,True,True,True,False,True));self.assertTrue(o['power_good_hw']);self.assertTrue(o['audio_power_request_gated']);self.assertFalse(o['tx_rf_permitted'])
 def test_every_fault_blocks_audio(self):
  good=PowerStatus(True,True,True,True,True,True,True,False,True).__dict__
  for item in ['protected_path_valid','buck5_good','buck3v3_good','v62_3v3_supervisor_ok','uv_in_window','ov_in_window']:
   v=good.copy();v[item]=False;self.assertFalse(evaluate(PowerStatus(**v))['audio_power_request_gated'],item)
 def test_tx_never_software_enabled(self):
  # 2^9 all combinations of boolean model inputs
  from dataclasses import fields
  fs=[x.name for x in fields(PowerStatus)]
  for bits in itertools.product([False,True],repeat=len(fs)):
   o=evaluate(PowerStatus(*bits));self.assertFalse(o['tx_rf_permitted']);self.assertFalse(o['rf_pa_power_enabled'])
 def test_csv_parts(self):
  with (R/'07_Componenti/BOM_ALIMENTAZIONI_V6.3.csv').open() as f:rows=list(csv.DictReader(f))
  self.assertEqual(len(rows),len(D['components']))
 def test_csv_terminal(self):
  with (R/'01_Specifiche/V6.3/NETLIST_FUNZIONALE_ALIMENTAZIONE_V6.3.csv').open() as f:rows=list(csv.DictReader(f))
  self.assertEqual(len(rows),len(N));self.assertTrue(all(x['Pin_fisico_verificato']=='NO' for x in rows))
 def test_fault_mutation_pin(self):
  c=copy.deepcopy(D);next(x for x in c['functional_terminals'] if x['ref']=='S901' and x['terminal']=='A')['net']='3V3_D'
  with self.assertRaises(ValueError):audit(c)
 def test_fault_mutation_rf_tx(self):
  c=copy.deepcopy(D);c['release']['rf_tx']=True
  with self.assertRaises(ValueError):audit(c)
 def test_fault_mutation_power_cycle(self):
  c=copy.deepcopy(D);c['power_flow'].append(['5V_RF','13V8_RAW','INVALID'])
  with self.assertRaises(ValueError):audit(c)
 def test_fault_mutation_duplicate(self):
  c=copy.deepcopy(D);c['components'].append(copy.deepcopy(c['components'][0]))
  with self.assertRaises(ValueError):audit(c)
 def test_fault_mutation_dni(self):
  c=copy.deepcopy(D);next(x for x in c['components'] if x['ref']=='J907')['qualification']='CANDIDATE'
  with self.assertRaises(ValueError):audit(c)
 def test_fault_mutation_5v_unrooted(self):
  c=copy.deepcopy(D);next(x for x in c['power_flow'] if x[1]=='5V_MAIN')[0]='UNPOWERED'
  with self.assertRaises(ValueError):audit(c)
 def test_fault_mutation_open_shunt(self):
  c=copy.deepcopy(D);next(x for x in c['functional_terminals'] if x['ref']=='R901' and x['terminal']=='MINUS')['net']='OPEN'
  with self.assertRaises(ValueError):audit(c)
 def test_load_sampling(self):self.assertEqual(S['monte_carlo_samples'],25000);self.assertLess(S['monte_carlo_stats']['input_a']['max'],5.0)
 def test_buck_peak_inductor(self):
  for row in S['buck_ccm_only']:
   ioutmax=2.0 if row['rail']=='5V_MAIN' else 1.2
   self.assertLess(ioutmax+row['inductor_deltaI_pp_ideal_a']/2,7.0)
 def test_thermal_ldo(self):self.assertLessEqual(S['monte_carlo_stats']['ldo3v3_loss_w']['max'],.15)
 def test_holdup_conservative(self):
  h=S['ideal_brownout_hold_time_ms'];self.assertGreater(h['13v8_bulk_470uf_13v8_to_11v88'],1.0);self.assertLess(h['5v_local_48uf_5_to_4v5'],0.1)
 def test_total_files_cited(self):self.assertTrue((R/'01_Specifiche/V6.3/SCHEMA_A_COMPONENTI_ALIMENTAZIONI_V6.3.md').exists())

if __name__=='__main__':unittest.main(verbosity=1)
