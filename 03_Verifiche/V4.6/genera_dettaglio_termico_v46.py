#!/usr/bin/env python3
"""Technical plot from static KiCad coordinates. No manufacturer CAD, no thermal simulation."""
from pathlib import Path
import json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'03_Verifiche/V4.6'
x=json.loads((P/'AUDIT_TERMICA_SMA_V4.6.json').read_text())
r=x['paddle_rect_mm'];v=x['closest_ground_via'];fig,ax=plt.subplots(figsize=(7.5,5.3))
ax.add_patch(Rectangle((r[0],r[1]),r[2]-r[0],r[3]-r[1],facecolor='#a9c4bd',edgecolor='#316c60',lw=2,label='Rame piazzola U101 GND'))
ax.add_patch(Circle((v['x_mm'],v['y_mm']),v['diameter_mm']/2,facecolor='#d3dce8',edgecolor='#3d638a',lw=2,label='Via GND esterno'))
ax.add_patch(Circle((v['x_mm'],v['y_mm']),v['drill_mm']/2,facecolor='white',edgecolor='#3d638a',lw=1,label='Foro via'))
x0=v['x_mm']+0.7;y0=v['y_mm']+v['diameter_mm']/2;y1=r[1]
ax.annotate('',(x0,y0),(x0,y1),arrowprops=dict(arrowstyle='<->',lw=1.5))
ax.text(x0+0.12,(y0+y1)/2,'0,50 mm',va='center',fontsize=10)
ax.text(68,34.2,'Pad U101\n1,80 × 3,48 mm',ha='center',va='center',fontsize=11)
ax.text(68.3,30.55,'Via Ø0,70 / foro Ø0,30 mm',fontsize=10)
ax.set_xlim(66.1,71.4);ax.set_ylim(30.2,36.5);ax.set_aspect('equal');ax.grid(alpha=.15)
ax.set_xlabel('Coordinata PCB X (mm)');ax.set_ylabel('Coordinata PCB Y (mm)')
ax.set_title('V4.6 — Dettaglio geometrico GND ADL5535 (solo audit statico)')
ax.text(.02,-.17,'NON è una simulazione termica e NON conferma il refill dei piani di massa.',transform=ax.transAxes,fontsize=9)
fig.tight_layout();fig.savefig(P/'DETTAGLIO_PAD_TERMICO_U101_V4.6.png',dpi=180,bbox_inches='tight');plt.close(fig)
