#!/usr/bin/env python3
"""Original diagram of study-pad coordinates only, NOT TE CAD geometry."""
from pathlib import Path
import importlib.util
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
spec=importlib.util.spec_from_file_location('audit',Path(__file__).with_name('audit_te_sma_v47.py'))
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
pads=a.p.child(a.FP.read_text('utf8'),'pad')
fig,ax=plt.subplots(figsize=(9,6))
for x in pads:
 if a.is_ground_custom_pad(x):
  v=a.custom_bounds(x)
  poly=Polygon(v['polygon_mm'],facecolor='#93A6B8',edgecolor='#243746',lw=1.5)
  ax.add_patch(poly)
ax.add_patch(Circle((0,0),1.025,facecolor='#F2B45D',edgecolor='#5F4326',lw=1.4))
ax.plot([-5.5,5.5],[0,0],':',color='#88929A',lw=0.75)
ax.plot([0,0],[-5,5],':',color='#88929A',lw=0.75)
ax.annotate('', xy=(5.0,3.88),xytext=(5.0,-3.88),arrowprops=dict(arrowstyle='<->',color='#243746',lw=1.7))
ax.text(5.16,0,'7,76 mm  (inviluppo GND)',ha='left',va='center',rotation=90,fontsize=10)
ax.annotate('Ø 2,05 mm',xy=(0.75,0.6),xytext=(0.7,2.2),arrowprops=dict(arrowstyle='->',color='#65502B'),fontsize=10)
ax.annotate('',xy=(1.73,-4.45),xytext=(3.6,-4.45),arrowprops=dict(arrowstyle='<->',color='#243746',lw=1.3))
ax.text(2.665,-4.9,'1,87 mm (larghezza locale isola)',ha='center',va='center',fontsize=8.5)
ax.set_title('Superstar 3900 V4.7 · modello footprint SMA sperimentale',loc='left',fontsize=14)
ax.set_xlim(-5.5,6.0);ax.set_ylim(-5.6,5.4);ax.set_aspect('equal');ax.grid(alpha=.2)
ax.set_xlabel('Coordinate locali del footprint (mm)');ax.set_ylabel('Coordinate locali (mm)')
fig.text(.11,.02,'Schema originale del rame V4.3/4.5. NON è una sovrapposizione al CAD TE; mask/paste, 3D e DRC non verificati.',fontsize=9,color='#6c7481')
fig.tight_layout(rect=(0,.045,1,1))
out=Path(__file__).with_name('GEOMETRIA_SMA_STUDIO_V4.7.png')
fig.savefig(out,dpi=170)
print(out, out.stat().st_size)
