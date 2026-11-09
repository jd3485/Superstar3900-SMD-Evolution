#!/usr/bin/env python3
"""V2.6 analytical replay: no extrapolation of vendor Q@250MHz to Q@27MHz."""
import sys,csv,importlib.util,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
V=ROOT/'03_Verifiche/V2.6'

def load(p,name):
 sp=importlib.util.spec_from_file_location(name,str(p));m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
b=load(ROOT/'03_Verifiche/V2.5/filter_bank_v25.py','b25_replay')
m24=load(ROOT/'03_Verifiche/V2.4/rf_preselector_v24.py','m24_replay')
bands=b.extract_bands(ROOT/'02_Piano_Frequenze/Tabella_270_canali.csv')
with (V/'Sintesi_Pari_Q_V2.6.csv').open() as f: expected=list(csv.DictReader(f))
for row in expected:
 q=int(row['Q_assumed']);base=m24.measures(m24.plan()['HP5_LP9'],q)
 metrics=[b.branch_metrics(b.branch_nominal(z['center_hz']),z['freq_hz'],q=q) for z in bands]
 assert abs(base['max_pass_loss_db']-float(row['one_filter_loss_max_dB']))<.0006
 assert abs(max(v['filter_max_loss_db'] for v in metrics)-float(row['bank_ideal_loss_max_dB']))<.0006
print('PASS: 5 Q scenarios x 6 bands, 270 frequencies; all Q values are scenario assumptions')
