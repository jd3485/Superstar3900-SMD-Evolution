#!/usr/bin/env python3
"""Generate an annotated schematic-style map from the V5.8 audit, NOT a KiCad PCB view."""
import json,html
from pathlib import Path
HERE=Path(__file__).resolve().parent
r=json.loads((HERE/'AUDIT_RITORNO_RF_V5.8.json').read_text())
ROOT=HERE.parents[1]
import sys
sys.path.insert(0,str(ROOT/'03_Verifiche/V5.5'))
from audit_rame_v55 import PCB,parse,child,children,numpair
pcb=parse(PCB.read_text())
colors={'RF_LNA_INPUT':'#007ea3','RF_LNA_IC_IN':'#289766','RF_BIAS_OUT':'#7951a6','RF_LNA_OUT':'#d06832','RF_ATTEN_IN':'#c42741','RF_ATTEN_OUT':'#b07816'}
def xy(p):return 70+(p[0]-20)*7,58+(p[1]-20)*7
out=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 930 585" role="img" aria-label="Mappa diagnostica delle vie GND e delle piste RF V5.8">',
 '<rect width="930" height="585" fill="#fcfcfc"/>',
 '<text x="70" y="31" font-family="sans-serif" font-size="17" font-weight="bold">Modulo RX 50 Ω — mappa geometrica V5.8 (NON DRC)</text>',
 '<rect x="70" y="58" width="770" height="434" rx="2" fill="#edf6f0" stroke="#557267" stroke-width="2"/>']
for v in children(pcb,'via'):
 p=numpair(child(v,'at')); x,y=xy(p)
 out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.9" fill="#687771" stroke="#26382d" stroke-width=".6"/>')
for s in r['by_segment']:
 x1,y1=xy(s['start_mm']);x2,y2=xy(s['end_mm'])
 out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{colors[s["net"]]}" stroke-width="3" stroke-linecap="round"/>')
for i,s in enumerate(r['by_net']):
 x,y=xy(s['worst_point_mm']);out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6.5" fill="none" stroke="#cc2e23" stroke-width="2"/>')
for i,(name,col) in enumerate(colors.items()):
 x=70+(i%3)*270;y=522+(i//3)*23
 out.append(f'<line x1="{x}" y1="{y-5}" x2="{x+21}" y2="{y-5}" stroke="{col}" stroke-width="3"/>')
 out.append(f'<text x="{x+27}" y="{y}" font-family="monospace" font-size="11" fill="#343434">{html.escape(name)}</text>')
out.append('<text x="70" y="577" font-family="sans-serif" font-size="11" fill="#555">Punti rossi: campioni più lontani dal centro di una via GND · GND via grigie · sole piste RF colorate · 1 unità = 1 mm</text>')
out.append('</svg>')
(HERE/'MAPPA_VIE_E_PISTE_RF_V5.8.svg').write_text('\n'.join(out)+'\n',encoding='utf-8')
print('Generated', HERE/'MAPPA_VIE_E_PISTE_RF_V5.8.svg')
