#!/usr/bin/env python3
"""Verifica riproducibile del confronto fase-noise V0.5 (standard library only).
Rumore calcolato = SOLO normalized in-band flat floor e flicker; non emissioni reali.
"""
from pathlib import Path
import csv,json,math
root=Path(__file__).resolve().parents[1]
p=root/'02_Piano_Frequenze'/'Tabella_LMX2572_270_Integer_N_V0.5.csv'
r=list(csv.DictReader(p.open(newline='',encoding='utf-8')))
assert len(r)==270 and len({x['rf_hz'] for x in r})==270
for x in r:
    lo=int(x['lo_hz']);vco=int(x['vco_hz']);N=int(x['pll_n_integer']);PFD=int(x['pfd_hz'])
    assert lo==int(x['rf_hz'])+int(x['fi1_hz'])
    assert lo*128==vco==N*PFD
    assert 3_200_000_000<=vco<=6_400_000_000 and N>=24
    assert x['pll_num']=='0' and x['freq_error_hz']=='0'

def normalized(fom,ref_hz,r_div,f_out_hz):
    pfd=ref_hz/r_div
    return fom+10*math.log10(pfd)+20*math.log10(f_out_hz/pfd)
adf=normalized(-220,12_800_000,20,37_500_000)
lmx=normalized(-232,12_800_000,10,37_500_000)
assert abs(adf-(-126.5811743852845))<1e-9
assert abs(lmx-(-141.5914743419243))<1e-9
assert abs((adf-lmx)-15.0102999566)<1e-6
j=json.loads((root/'03_Verifiche'/'Report_Confronto_PLL_V0.5.json').read_text())
assert j['channel_count']==270
assert abs(j['difference_in_white_floor_db']-(adf-lmx))<.001
print('PASS V0.5: 270 frequenze Integer-N, 0 Hz errore matematico; PN-floor comparata (NON misurata).')
print(f'ADF4351 {adf:.2f}, LMX2572 {lmx:.2f} dBc/Hz; delta {adf-lmx:.2f} dB')
