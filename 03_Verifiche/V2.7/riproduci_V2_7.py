#!/usr/bin/env python3
"""Run from project root: python 03_Verifiche/V2.7/riproduci_V2_7.py"""
import importlib.util,csv,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('r24',ROOT/'03_Verifiche/V2.4/rf_preselector_v24.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ref=m.plan()['HP5_LP9']
data=list(csv.DictReader((ROOT/'07_Componenti/BOM_Preselettore_Valori_Commerciali_V2.7_BOZZA.csv').open()))
record=list(csv.DictReader((ROOT/'03_Verifiche/V2.7/Confronto_Quantizzazione_V2.7.csv').open()))
for variante in ('E12_COMMERCIALE','E24_COMMERCIALE'):
    pcs=[]
    for row in sorted([r for r in data if r['variante']==variante],key=lambda r:r['designatore']):
        x=float(row['valore_nominale'])*(1e-9 if row['unita']=='nH' else 1e-12)
        pcs.append((row['topologia'],x))
    assert [k for k,v in pcs]==[k for k,v in ref]
    for q in (20,30,45,60):
        rr=next(r for r in record if r['scenario']==variante and int(r['q_ipotizzato'])==q)
        got=m.measures(pcs,q=q)
        for f,g in [('perdita_max_RX_dB','max_pass_loss_db'),('reiezione_min_IMG_dB','min_image_rejection_db'),('S11_peggiore_dB','worst_s11_db')]:
            assert abs(float(rr[f])-got[g])<1e-8,(variante,q,f)
print('PASS: 8 case (2 commercial variants x 4 Q assumptions), result files reproducible')
