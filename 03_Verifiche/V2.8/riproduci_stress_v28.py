#!/usr/bin/env python3
"""Riproduce i 2.400 stress numerici V2.8.
Run from project root: python 03_Verifiche/V2.8/riproduci_stress_v28.py
Optional --rebuild writes a new CSV in current directory, not in historical source.
"""
import argparse, csv, importlib.util, json, numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v28model',str(HERE/'model_v28.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
parser=argparse.ArgumentParser();parser.add_argument('--rebuild',action='store_true');args=parser.parse_args()
rng=np.random.default_rng(390028)
scenarios=[('LP7_2TRAP_9C',m.lp7_traps()),('HP3_LP7_2TRAP_12C',m.hp3()+m.lp7_traps())]
rows=[]
for i in range(1200):
 for name,elems in scenarios:
  modified,q=m.perturb(elems,rng)
  d=m.measure(modified,q)
  rows.append({'scenario':name,'case':i,'q_hypothesis':q,**d,'gate_pass':int(m.pass_gate(d))})
ref=list(csv.DictReader((HERE/'Stress_Tolleranze_V2.8.csv').open(encoding='utf8')))
assert len(rows)==len(ref)==2400
cols=list(rows[0].keys())
for i,(a,b) in enumerate(zip(rows,ref)):
 assert a['scenario']==b['scenario'] and int(a['case'])==int(b['case']),f'row {i}'
 assert int(a['gate_pass'])==int(b['gate_pass']),f'gate {i}'
 for k in ('q_hypothesis','loss_max_dB','image_rejection_min_dB','s11_worst_dB'):
  assert abs(a[k]-float(b[k]))<1e-9,(i,k)
summary=json.loads((HERE/'Risultati_V2.8.json').read_text(encoding='utf8'))
for name,ele in scenarios:
 a=[r for r in rows if r['scenario']==name]
 actual=sum(r['gate_pass'] for r in a)/len(a)
 target=summary['designs'][name]['stress']['pass_rate_exploratory']
 assert abs(actual-target)<1e-12
 print(f'PASS {name}: {len(a)} test, soglie simultanee {100*actual:.1f}%')
if args.rebuild:
 out=Path.cwd()/'Stress_Tolleranze_V2.8_RIPRODOTTO.csv'
 with out.open('w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,cols);w.writeheader();w.writerows(rows)
 print('Created:',out)
print('PASS all 2,400 numerical stress samples match saved V2.8 CSV')
