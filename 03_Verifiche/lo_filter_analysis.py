"""Low-pass LO 7th order: reproducible 2-port ABCD frequency sweep.
A lumped idealized network, NOT an EM simulation, KiCad ERC or ngspice.
Usage: python 03_Verifiche/lo_filter_analysis.py
"""
import csv,json, math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
BASE=Path(__file__).resolve().parent
Z0=50.0; FC_HZ=44_000_000; ORDER=7
VALUES=[]
for k in range(1, ORDER+1):
    g=2*math.sin((2*k-1)*math.pi/(2*ORDER))
    VALUES.append(('L' if k%2 else 'C',g*Z0/(2*math.pi*FC_HZ) if k%2 else g/(Z0*2*math.pi*FC_HZ)))

def s21_db(freq_hz,components=VALUES,inductor_q=None,cap_esr=0.0):
    f=np.atleast_1d(np.asarray(freq_hz,dtype=float))
    omega=2*math.pi*f
    M=np.broadcast_to(np.eye(2,dtype=np.complex128),(len(f),2,2)).copy()
    for kind,val in components:
        T=np.zeros_like(M)
        T[:,0,0]=T[:,1,1]=1
        if kind=='L':
            T[:,0,1]=1j*omega*val + (omega*val/inductor_q if inductor_q is not None else 0)
        else:
            T[:,1,0]=1/(cap_esr+1/(1j*omega*val))
        M=M@T
    denom=M[:,0,0]+M[:,0,1]/Z0+M[:,1,0]*Z0+M[:,1,1]
    return 20*np.log10(np.abs(2/denom))

def calculate(write_files=True):
    f=np.linspace(15e6,140e6,2501)
    ideal=s21_db(f)
    approximated=s21_db(f,inductor_q=60,cap_esr=0.07)
    results={'version':'V0.3','status':'RLC lumped idealized numerical model, not measured',
       'fc_hz':FC_HZ,'order':ORDER,'z0_ohm':Z0,
       'elements':[{'kind':k,'value_si':v} for k,v in VALUES],
       'frequencies':{},'monte_carlo':{}}
    for hz in [36_310_000,39_000_000,72_620_000,78_000_000]:
        results['frequencies'][str(hz)]={'ideal_s21_db':float(s21_db([hz])[0]),'q60_s21_db':float(s21_db([hz],inductor_q=60,cap_esr=0.07)[0])}
    rng=np.random.default_rng(3900)
    samples=[]
    for _ in range(1000):
        pert=[(kind,val*rng.normal(1,0.05 if kind=='L' else 0.02)) for kind,val in VALUES]
        samples.append(s21_db([39e6,72.62e6],pert,inductor_q=60,cap_esr=0.07))
    a=np.asarray(samples)
    for i,hz in enumerate([39_000_000,72_620_000]):
        results['monte_carlo'][str(hz)]={'p05_db':float(np.quantile(a[:,i],0.05)),'p50_db':float(np.quantile(a[:,i],0.5)),'p95_db':float(np.quantile(a[:,i],0.95))}
    if write_files:
        with (BASE/'LO_LPF_7p_Risposta_V0.3.csv').open('w',newline='') as h:
            w=csv.writer(h);w.writerow(['frequency_hz','s21_ideal_db','s21_q60_esr0p07_db'])
            w.writerows(zip(f.astype(int),np.round(ideal,8),np.round(approximated,8)))
        (BASE/'Risultati_LO_LPF_V0.3.json').write_text(json.dumps(results,indent=2),encoding='utf8')
        fig,ax=plt.subplots(figsize=(9.5,4.4))
        ax.plot(f/1e6,ideal,label='LC ideali')
        ax.plot(f/1e6,approximated,label='Q induttori = 60; ESR C = 0.07 ohm')
        ax.axvspan(36.31,39,alpha=.15,label='Gamma LO')
        ax.set(xlabel='Frequenza (MHz)',ylabel='|S21| (dB)',title='Filtro LO Butterworth 7 poli - simulazione analitica, non EM',ylim=(-85,3),xlim=(20,140))
        ax.grid(alpha=.2);ax.legend(loc='upper right',fontsize=8);fig.tight_layout()
        fig.savefig(BASE/'Grafico_LO_LPF_V0.3.png',dpi=170)
        plt.close(fig)
    return results
if __name__=='__main__':
    r=calculate()
    print('Stage2 filter calculations, 50ohm, idealized:')
    for f,v in r['frequencies'].items():print(f, v)
