#!/usr/bin/env python3
"""Monte Carlo resistor / reference tolerance; not SPICE nor electrical qualification."""
import random,math,json,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'03_Verifiche/V6.2'
random.seed(6206)
voltage=[]; count=50000
for _ in range(count):
    ref=0.4*random.uniform(.99,1.01)
    def trip(up):
        top=up*random.uniform(.99,1.01);bot=10000*random.uniform(.99,1.01)
        return ref*(top+bot)/bot
    voltage.append([trip(287000),trip(374000)])
uv=[x[0] for x in voltage];ov=[x[1] for x in voltage]
res={'simulator':'Monte Carlo analytic dividers, no SPICE','n':count,'assumptions':{'R_tolerance_fraction':0.01,'Vref_fraction':0.01,'other_TPS3700_errors_not_modeled':True},
  'uv_v':{'minimum':min(uv),'maximum':max(uv),'mean':sum(uv)/count,'nominal':11.88},
  'ov_v':{'minimum':min(ov),'maximum':max(ov),'mean':sum(ov)/count,'nominal':15.36},
  'at_13_8_V_ideal':sum(a<13.8<b for a,b in voltage)==count,
  'hardware_qualification':False}
(OUT/'STUDIO_SOGLIE_V6.2.json').write_text(json.dumps(res,indent=2)+'\n')
# reusable SVG plot with guardrails, no external plotting requirement
points=[]
for v in range(800,1901,10):
  V=v/100
  # normalized nominal open-drain comparators: uv high above threshold, ov high below threshold
  p=int(V>=11.88 and V<=15.36)
  points.append((V,p))
W,H=850,360
coord=lambda v:75+(v-8)*60
red=' '.join(f'{coord(v):.1f},{300-210*p}' for v,p in points)
svg=f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 360" width="850" height="360"><rect width="850" height="360" fill="white"/><text x="40" y="35" font-family="Arial" font-size="22" font-weight="bold">V6.2 — finestra alimentazione nominale (solo modello)</text><text x="40" y="57" font-family="Arial" font-size="13" fill="#666">Soglie idealizzate, senza isteresi / ritardi reali. TX resta OFF per J801 aperto.</text><line x1="75" x2="750" y1="300" y2="300" stroke="#333"/><line x1="75" x2="75" y1="78" y2="300" stroke="#333"/><polyline points="{red}" fill="none" stroke="#14532d" stroke-width="3"/>"""
for v,t in [(11.88,'UV 11,88 V'),(13.8,'13,8 V nom.'),(15.36,'OV 15,36 V')]:
 x=coord(v)
 svg+=f'<line x1="{x}" x2="{x}" y1="80" y2="300" stroke="#94a3b8" stroke-dasharray="4 5"/><text x="{x-37}" y="325" font-size="12" font-family="Arial">{t}</text>'
svg+='</svg>'
(OUT/'CURVA_FINESTRA_V6.2.svg').write_text(svg)
print(json.dumps(res,indent=2))
