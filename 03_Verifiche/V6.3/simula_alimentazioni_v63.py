#!/usr/bin/env python3
"""Reproducible IDEALIZED engineering computations; NOT vendor SPICE, not hardware signoff."""
from pathlib import Path
import json,csv,math,random,statistics
R=Path(__file__).resolve().parents[2]
SPEC=json.loads((R/'01_Specifiche/V6.3/ALIMENTAZIONI_CANDIDATE_V6.3.json').read_text())
O=Path(__file__).resolve().parent
RNG=random.Random(6309)

def calc_ref(top,bottom,ref=1): return ref*(1+top/bottom)
def input_power(loads,eta5,eta3):
 I={x['load']:x['nominal_a'] for x in loads}
 rail5=sum(x['nominal_a'] for x in loads if x['rail'].startswith('5V_'))+I['SENSITIVE_A']
 rail3=sum(x['nominal_a'] for x in loads if x['rail'] in ('3V3_D','3V3_UI'))+I['CODEC_1V8']
 return 5*rail5/eta5+3.3*rail3/eta3+13.8*I['SPEAKER_AMP'],rail5,rail3

def buck_pp(vin,vout,L,fs):
 d=vout/vin
 return (vin-vout)*d/(L*fs)

def report():
 loads=SPEC['loads']
 P,rail5,rail3=input_power(loads,.90,.88)
 # LM74900-Q1 external dual MOSFET 2x5mOhm; shunt 5mOhm, ideal ohmic burden.
 Rpath=0.015
 nominal_I=(13.8-math.sqrt(13.8**2-4*Rpath*P))/(2*Rpath)
 mon=[]
 for _ in range(25000):
  chosen={x['load']:RNG.uniform(x['nominal_a']*.75,x['envelope_a']) for x in loads}
  vi=RNG.uniform(11.88,15.36)
  e5=RNG.uniform(.84,.94);e3=RNG.uniform(.80,.94)
  i5=sum(chosen[x['load']] for x in loads if x['rail'].startswith('5V_'))+chosen['SENSITIVE_A']
  i3=sum(chosen[x['load']] for x in loads if x['rail'] in ('3V3_D','3V3_UI'))+chosen['CODEC_1V8']
  pa=chosen['SPEAKER_AMP']
  pt=5*i5/e5+3.3*i3/e3+vi*pa
  I=(vi-math.sqrt(vi*vi-4*Rpath*pt))/(2*Rpath)
  mon.append((I,pt,i5,i3,(5-3.3)*chosen['SENSITIVE_A'],(3.3-1.8)*chosen['CODEC_1V8'],I*I*Rpath))
 stats={}
 for j,name in enumerate(['input_a','delivered_power_w','buck5_out_a','buck3v3_out_a','ldo3v3_loss_w','ldo1v8_loss_w','fets_and_shunt_loss_w']):
  s=sorted(row[j] for row in mon)
  stats[name]={'min':round(s[0],6),'median':round(s[len(s)//2],6),'p99':round(s[int(.99*len(s))],6),'max':round(s[-1],6)}
 # 470uF output capacitor, 47nF dV/dT cap, drive 55uA typical per TI;
 # model neglects buck startup load, MOSFET charge profile and gate driver details.
 cbulk=470e-6;cg=47e-9;ih=55e-6;islew=cbulk*ih/cg
 t_ramp=13.8*cbulk/islew
 trans=[]
 for k in range(401):
  t=k*.00005
  v=min(13.8,t*islew/cbulk)
  trans.append((t*1000,v,islew if v<13.8-1e-9 else 0))
 with (O/'TRANSITORIO_IDEALE_V6.3.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['tempo_ms','vprot_ideale_v','corrente_capacitore_a']);w.writerows([(round(a,4),round(b,5),round(c,6)) for a,b,c in trans])
 # deterministic sweep of voltage with the existing V6.2 *nominal* window; not actual TPS3700 response
 sweep=[{'vbat_v':round(v,2),'v62_window_nominal':11.88<=v<=15.36}
        for v in [9,10,11,11.5,11.88,12,13.8,15,15.36,15.5,16,18,24]]
 buck=[]
 for vin in (11.88,13.8,15.36):
  for name,voltage,L,fs,Ce in [('5V_MAIN',5,4.7e-6,400000,48e-6),('3V3_D',3.3,2.2e-6,1000000,36e-6)]:
   pp=buck_pp(vin,voltage,L,fs)
   buck.append({'rail':name,'vin_v':vin,'duty_ideal':round(voltage/vin,6),
    'inductor_deltaI_pp_ideal_a':round(pp,6),
    'ccm_min_average_load_a':round(pp/2,6),
    'capacitive_ripple_if_ccm_mv':round(1000*pp/(8*fs*Ce),4),
    'assumptions':'ideal CCM, min estimated effective MLCC cap; ignores ESR/ESL/PFM/loop/EMI'})
 v5=calc_ref(100000,24900);v3=calc_ref(100000,43200)
 z={
  'revision':'V6.3','model':'ideal electrical/math study only, not real SPICE and not native KiCad',
  'loads_nominal_5v_output_a':round(rail5,6),'loads_nominal_3v3_output_a':round(rail3,6),
  'nominal_input_total_w':round(P,6),'nominal_input_current_a':round(nominal_I,6),
  'nominal_input_ohmic_loss_w':round(nominal_I**2*Rpath,6),
  'feedback_5v_from_100k_24k9_v':round(v5,6),'feedback_3v3_from_100k_43k2_v':round(v3,6),
  'feedback_abs_error_percent':{'5v':round(100*(v5/5-1),5),'3v3':round(100*(v3/3.3-1),5)},
  'monte_carlo_samples':len(mon),
  'monte_carlo_efficiency_assumptions':{'eta5':[.84,.94],'eta3':[.80,.94],'input_voltage_v':[11.88,15.36],
  'load_distribution':'independent uniform 0.75*nominal to envelope, NOT actual probability/fault distribution'},
  'monte_carlo_stats':stats,
  'ideal_inrush':{'c_bulk_f':cbulk,'c_dvdt_f':cg,'i_gate_source_typ_a':ih,
   'current_charge_a':round(islew,6),'ramp_time_to_13v8_ms':round(t_ramp*1000,4),
   'exclusions':'real gate dynamics, MOSFET SOA, buck load and inductor/cable, UVOV logic'},
  'buck_ccm_only':buck,
  'ideal_brownout_hold_time_ms':{'13v8_bulk_470uf_13v8_to_11v88':round(1000*470e-6*(13.8-11.88)/nominal_I,5),'13v8_20pct_low_cap':round(1000*.8*470e-6*(13.8-11.88)/nominal_I,5),'5v_local_48uf_5_to_4v5':round(1000*48e-6*.5/rail5,5),'3v3_local_36uf_3v3_to_3v0':round(1000*36e-6*.3/rail3,5),'assumptions':'capacitors only; instantaneous loss of energy supply, constant load, no buck regulation/hold-up or switching behavior'},
  'ldo_nominal_dissipation':{'3v3_a_w':round((5-3.3)*.045,4),'1v8_codec_w':round((3.3-1.8)*.05,4)},
  'nominal_3v3_limiter_below_rated':True,
  'voltage_window_nominal_samples':sweep,
  'safety':{'production_release':False,'rf_pa_power_connected':False,'tx_permitted':False},
  'limitations':['efficiencies assumed, not measured','load currents unverified','TVS transients and reverse pulse waveform unknown',
   'output ripple only CCM formula, at nominal load both converters may operate in DCM/PFM',
   'current limit, MOSFET SOA, fuse and thermal not qualified','EMI at 26–28MHz not modeled']}
 (O/'SIMULAZIONI_NUMERICHE_V6.3.json').write_text(json.dumps(z,indent=2,ensure_ascii=False)+'\n')
 # static SVG, no dependency on plotting libraries; axes physically scaled.
 W,H=910,370
 xy=lambda t,v:(80+(t/20)*780,300-(v/16)*235)
 poly=' '.join(f'{xy(a,b)[0]:.1f},{xy(a,b)[1]:.1f}' for a,b,_ in trans)
 svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 910 370">',
 '<rect width="910" height="370" fill="#111b2c"/>',
 '<text x="35" y="38" fill="#f5f8ff" font-family="sans-serif" font-size="21" font-weight="bold">V6.3 • Accensione ideale del bus protetto 13,8 V</text>',
 '<text x="35" y="61" fill="#cdd8ef" font-family="sans-serif" font-size="12">Solo carica C=470µF con Cdv/dt=47nF e Igate=55µA · NON simulazione SPICE</text>',
 '<line x1="80" y1="300" x2="860" y2="300" stroke="#8290ad"/><line x1="80" y1="65" x2="80" y2="300" stroke="#8290ad"/>']
 for v in (0,4,8,12,16):
  yy=xy(0,v)[1];svg.extend([f'<line x1="80" y1="{yy:.1f}" x2="860" y2="{yy:.1f}" stroke="#26354d"/>',f'<text x="49" y="{yy+5:.1f}" fill="#cdd8ef" font-family="sans-serif" font-size="12">{v} V</text>'])
 for t in (0,5,10,15,20):
  xx=xy(t,0)[0];svg.append(f'<text x="{xx-12:.1f}" y="325" fill="#cdd8ef" font-family="sans-serif" font-size="12">{t}ms</text>')
 svg += [f'<polyline points="{poly}" fill="none" stroke="#60d4a3" stroke-width="3"/>',
 f'<text x="390" y="100" fill="#60d4a3" font-family="sans-serif" font-size="14">I cap ≈ {islew:.2f} A, tempo ≈ {t_ramp*1000:.1f} ms</text>',
 '<text x="35" y="354" fill="#cdd8ef" font-family="sans-serif" font-size="11">Esclude carico e sequenze buck, disturbi TVS, limiti MOSFET e controllore</text>','</svg>']
 (O/'AVVIO_ALIMENTAZIONE_V6.3.svg').write_text('\n'.join(svg))
 return z

if __name__=='__main__':
 d=report()
 print('SIM V6.3',d['monte_carlo_samples'],'samples','Inom=',d['nominal_input_current_a'],'A',
       'I99=',d['monte_carlo_stats']['input_a']['p99'],'A',
       'inrush=',d['ideal_inrush']['current_charge_a'],'A',
       'ramp_ms=',d['ideal_inrush']['ramp_time_to_13v8_ms'])
