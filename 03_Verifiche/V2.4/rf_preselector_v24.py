#!/usr/bin/env python3
"""V2.4: 50-ohm lumped ABCD model. Study only; no real device S-parameters.
Reproduce: python rf_preselector_v24.py [--output OUTPUT_DIR]
Requires numpy, matplotlib. Optional SciPy is NOT required.
Caveats: frequency-independent inductor Q, scalar capacitor tan-delta, no pad/trace parasitics.
"""
from __future__ import annotations
import numpy as np, csv, json, argparse, math
from pathlib import Path
PI = np.pi
Z0=50.0
PASS_BAND = np.linspace(25.615e6,28.305e6,81)
IMAGE_BAND = np.linspace(47.005e6,49.695e6,81)

def chebyshev_g(n:int,ripple_db:float=0.1):
    assert n%2==1 and n>=3
    beta = np.log(1/np.tanh(ripple_db/17.37))
    gamma=np.sinh(beta/(2*n))
    a=[0]+[np.sin((2*k-1)*PI/(2*n)) for k in range(1,n+1)]
    b=[0]+[gamma*gamma+np.sin(k*PI/n)**2 for k in range(1,n+1)]
    g=[1.0, 2*a[1]/gamma]
    for k in range(2,n+1):
        g.append(4*a[k-1]*a[k]/(b[k-1]*g[k-1]))
    g.append(1.0)
    return g

def lowpass(n:int=9,cutoff_hz=29.5e6,z0=Z0,ripple_db=.1):
    g=chebyshev_g(n,ripple_db)
    return [('L',g[k]*z0/(2*PI*cutoff_hz)) if k%2 else ('C',g[k]/(z0*2*PI*cutoff_hz)) for k in range(1,n+1)]

def highpass(n:int=5,cutoff_hz=18e6,z0=Z0):
    assert n%2==1
    g=[1]+[2*np.sin((2*k-1)*PI/(2*n)) for k in range(1,n+1)]
    return [('CS',1/(2*PI*cutoff_hz*z0*g[k])) if k%2 else ('LS',z0/(2*PI*cutoff_hz*g[k])) for k in range(1,n+1)]

def network(pieces,frequency_hz,q_inductor=60.,tand_cap=.001,z0=Z0):
    f=np.asarray(frequency_hz, dtype=float).reshape(-1)
    w=2*PI*f
    A=np.ones(len(f),complex);B=np.zeros(len(f),complex)
    C=np.zeros(len(f),complex);D=np.ones(len(f),complex)
    for kind, val in pieces:
        if kind=='L':
            z=1j*w*val+w*val/q_inductor; aa,bb,cc,dd=1,z,0,1
        elif kind=='CS':
            z=1/(1j*w*val)+tand_cap/(w*val);aa,bb,cc,dd=1,z,0,1
        elif kind=='C':
            y=1j*w*val+w*val*tand_cap;aa,bb,cc,dd=1,0,y,1
        elif kind=='LS':
            z=1j*w*val+w*val/q_inductor;y=1/z;aa,bb,cc,dd=1,0,y,1
        else: raise ValueError(kind)
        A,B,C,D=A*aa+B*cc,A*bb+B*dd,C*aa+D*cc,C*bb+D*dd
    den=A+B/z0+C*z0+D
    s21=2/den
    s11=(A+B/z0-C*z0-D)/den
    return s21,s11

def measures(pieces,q=60.,tand=.001):
    a,rl=network(pieces,PASS_BAND,q,tand)
    b,_=network(pieces,IMAGE_BAND,q,tand)
    return {'max_pass_loss_db':float(np.max(-20*np.log10(np.abs(a)))),
            'min_image_rejection_db':float(np.min(-20*np.log10(np.abs(b)))),
            'worst_s11_db':float(np.max(20*np.log10(np.abs(rl))))}

def plan():
    return {'LP7':lowpass(7),'LP9':lowpass(9),'LP11':lowpass(11),
            'HP5_LP7':highpass(5)+lowpass(7),
            'HP5_LP9':highpass(5)+lowpass(9),
            'HP5_LP11':highpass(5)+lowpass(11)}

def run(outdir:Path,number_mc=1200,seed=390024):
    outdir.mkdir(parents=True,exist_ok=True)
    cases=plan(); rows=[]
    for name,elems in cases.items():
        for q in [25.,35.,60.,90.]:
            rows.append({'scenario':name,'q_inductor':q,**measures(elems,q)})
    with (outdir/'Confronto_Nominale_V2.4.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    candidate=cases['HP5_LP9'];rng=np.random.default_rng(seed)
    mc=[]
    for i in range(number_mc):
        # Explicit uniform independent component tolerances; Q range is NOT a probability model of a product batch.
        q=rng.uniform(25,75)
        e=[(typ,val*(1+rng.uniform(-.02,.02))) for typ,val in candidate]
        met=measures(e,q)
        mc.append({'case':i,'q':float(q),**met,
                   'pass_2db_image_55db':int(met['max_pass_loss_db']<=2 and met['min_image_rejection_db']>=55)})
    with (outdir/'MonteCarlo_RF_V2.4.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(mc[0]));w.writeheader();w.writerows(mc)
    nom=measures(candidate,60);stress=measures(candidate,35)
    stats={'release':'V2.4','model':'ABCD cascaded LC in 50 Ohm; series L R=omega*L/Q; shunt C G=omega*C*tan_delta; series C ESR=tand/(omega*C)',
       'topology_candidate':'HP5 Butterworth fc=18MHz + LP9 Chebyshev ripple .1dB fc=29.5MHz',
       'f_pass_hz':[25.615e6,28.305e6], 'f_image_hz':[47.005e6,49.695e6],
       'q_nominal_illustrative':60, 'q_stress':35,'capacitor_tan_delta':.001,
       'nominal_q60':nom,'stress_q35':stress, 'mc_samples':number_mc, 'mc_seed':seed,
       'mc_ranges':'all values uniform +/-2%; common Q uniformly between 25 and 75; these distributions are test inputs, not sourced manufacturing tolerances',
       'mc_percentile95_loss_db':float(np.percentile([r['max_pass_loss_db'] for r in mc],95)),
       'mc_percentile5_rejection_db':float(np.percentile([r['min_image_rejection_db'] for r in mc],5)),
       'mc_success_fraction':float(np.mean([r['pass_2db_image_55db'] for r in mc])),
       'gates':{'objective_pass_loss_db':1.5,'objective_image_rejection_db':60,
                'status':'NOT APPROVED - nominal loss and conservative Q/tolerance require further optimization'},
       'limitations':['No PCB and package parasitics','Q at 27 MHz not confirmed by individual vendor S-parameters',
       'No EM coupling or trace effects','No real filter coupling to LNA and mixer','No frequency-dependent L/C parameters','No real KiCad ERC or bench validation']}
    (outdir/'Risultati_V2.4.json').write_text(json.dumps(stats,indent=2,ensure_ascii=False)+'\n')
    fig,ax=__import__('matplotlib.pyplot',fromlist=['subplots']).subplots(figsize=(9.2,4.5))
    f=np.linspace(5e6,65e6,900)
    for name in ['HP5_LP7','HP5_LP9','HP5_LP11']:
        s21,_=network(cases[name],f,60)
        ax.plot(f/1e6,-20*np.log10(np.abs(s21)),label=name.replace('_',' + '),lw=1.6)
    ax.axvspan(25.615,28.305,alpha=.10,label='RX 25.615-28.305 MHz')
    ax.axvspan(47.005,49.695,alpha=.10,label='Immagine 47.005-49.695 MHz')
    ax.set(xlim=(5,60),ylim=(0,100),xlabel='Frequenza (MHz)',ylabel='Perdita/attenuazione (dB)',title='Preselettori di studio | modello ABCD, Q(L)=60')
    ax.grid(True,alpha=.22);ax.legend(loc='upper left',fontsize=8);fig.tight_layout()
    fig.savefig(outdir/'Confronto_Preselector_V2.4.png',dpi=160);__import__('matplotlib.pyplot',fromlist=['close']).close(fig)
    fig,axs=__import__('matplotlib.pyplot',fromlist=['subplots']).subplots(figsize=(9.2,4.3),ncols=2)
    axs[0].hist([r['max_pass_loss_db'] for r in mc],bins=28);axs[0].axvline(2,linestyle='--',lw=1.5);axs[0].set(title='Perdita massima in RX',xlabel='dB',ylabel='Casi');axs[0].grid(alpha=.2)
    axs[1].hist([r['min_image_rejection_db'] for r in mc],bins=28);axs[1].axvline(55,linestyle='--',lw=1.5);axs[1].set(title='Reiezione minima immagine',xlabel='dB',ylabel='Casi');axs[1].grid(alpha=.2)
    fig.suptitle('Monte Carlo V2.4: 1200 casi, componenti +/-2%, Q comune 25..75');fig.tight_layout();fig.savefig(outdir/'Distribuzioni_Tolleranze_V2.4.png',dpi=160);__import__('matplotlib.pyplot',fromlist=['close']).close(fig)
    with (outdir/'Componenti_Ideali_V2.4.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['ref_studio','tipo','valore_ideale','unita','valore_SI','stato'])
        for i,(typ,val) in enumerate(candidate,1):
            is_l=typ in ('L','LS');w.writerow([f'RF{i:02}',typ,round(val*(1e9 if is_l else 1e12),3),'nH' if is_l else 'pF',f'{val:.12g}','OBIETTIVO TEORICO, NON CODICE APPROVATO'])
    return stats

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default='.');p.add_argument('--mc',type=int,default=1200); a=p.parse_args()
    print(json.dumps(run(Path(a.output),a.mc),indent=2))
