"""Riproduce il modello RC ideale per MIC/FM della revisione V2.0.

Requisiti: Python, numpy, matplotlib. Non sostituisce SPICE o misure hardware.
Esecuzione: python simula_afe_v20.py
"""
from pathlib import Path
import csv, json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

D=Path(__file__).resolve().parent
SPECS={
    'mic': (100e-9, 1000.0, 4.7e-9),
    'fm':  (1e-6,   1000.0, 10e-9),
}

def h(freq, rin, cc, r, cf):
    w=2*np.pi*np.asarray(freq)
    zs=r+1/(1j*w*cc)
    zl=1/(1/rin+1j*w*cf)
    return zl/(zs+zl)

out={}
for key,(cc,r,cf) in SPECS.items():
    out[key]={
      'rin_assumed_ohm':20000,
      'simple_highpass_Hz':1/(2*math.pi*20000*cc),
      'simple_lowpass_Hz':1/(2*math.pi*r*cf),
      'gain_db':{str(f):round(float(20*np.log10(abs(h([f],20000,cc,r,cf)[0]))),4)
                 for f in [30,67,85.4,100,250,1000,3000,6000,12000,24000]},
    }
(D/'Riproduzione_Risposta_V2.0.json').write_text(json.dumps(out,indent=2))
with (D/'Riproduzione_Risposta_V2.0.csv').open('w',newline='') as f:
    writer=csv.writer(f);writer.writerow(['path','freq_Hz','gain_dB'])
    for key,(cc,r,cf) in SPECS.items():
        for f in np.geomspace(10,96000,200):
            writer.writerow([key,round(float(f),6),round(float(20*np.log10(abs(h([f],20000,cc,r,cf)[0]))),6)])
fig,ax=plt.subplots(figsize=(9.4,4.8))
ff=np.geomspace(1,100000,1500)
for key,(cc,r,cf) in SPECS.items():
    ax.semilogx(ff,20*np.log10(abs(h(ff,20000,cc,r,cf))),label=key.upper())
ax.set(xlim=(10,100000),ylim=(-32,2),xlabel='Frequenza (Hz)',ylabel='Guadagno (dB)',title='Modello RC ideale, Rin=20k ohm')
ax.grid(True,which='both',alpha=.3);ax.legend();fig.tight_layout();fig.savefig(D/'Riproduzione_Risposta_V2.0.png',dpi=170)
print('Riprodotti grafico e tabelle RC; non e una simulazione SPICE.')
