"""Test di consistenza V0.6 - indipendente da laboratorio; NON testi RF reali."""
import csv, json
from pathlib import Path
P=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((P/'02_Piano_Frequenze/Mappa_VCO_core_e_PLL_V0.6.csv').open()))
assert len(rows)==270
assert len(set(int(z['f_rx_hz']) for z in rows))==270
assert min(int(z['pll_n']) for z in rows)==3631
assert max(int(z['pll_n']) for z in rows)==3900
assert sum(z['vco_core_teorico']=='VCO3' for z in rows)==2
assert all(int(z['f_vco_hz'])==128*int(z['f_lo_hz']) for z in rows)
assert all(int(z['pll_n'])*1_280_000==int(z['f_vco_hz']) for z in rows)
report=json.loads((P/'03_Verifiche/Report_PLL_LMX2572_V0.6.json').read_text())
assert report['loop']['C3_nF']>=1.5
assert 3000<report['nominal']['crossover_Hz']<5500
assert report['nominal']['phase_margin_deg']>50
pinrows=list(csv.DictReader((P/'04_KiCad/Bozze_pre_KiCad/LMX2572_RHA_Pinmap_V0.6.csv').open()))
assert len(pinrows)==41
assert sorted(int(p['pin']) for p in pinrows if p['pin']!='DAP')==list(range(1,41))
assert {int(z['pin']):z['ti_name'] for z in pinrows if z['pin']!='DAP'}[35]=='Vtune'
print('PASS V0.6: piano frequenze, 270 setpoint, 2 core VCO3, 40pin+DAP, rapporto modello')
