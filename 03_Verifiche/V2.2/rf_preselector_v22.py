#!/usr/bin/env python3
"""V2.2 first-pass 5-resonator + 7-pole LPF RF circuit model.
Theoretical ABCD transmission (matched 50-ohm ports). Not EM/PCB or parasitic simulation.
"""
from __future__ import annotations
import csv,json,math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

R0=50.; F_REF=26.9e6; W_REF=2*math.pi*F_REF
F_MIN=25.615e6; F_MAX=28.305e6; IMG_MIN=47.005e6; IMG_MAX=49.695e6
L_TANK=330e-9
F_LPF_CUTOFF=31.0e6
RIPPLE_DB=0.3
# Optimized only against a simplistic bandpass response at Q=70; not a BOM for production.
TANK_OPT_PF=(129.37280327,30.40701326,11.56764921,55.68687781,70.34284482,83.88538041)
TANK_E24_PF=(130.,30.,12.,56.,68.,82.)

def cheby_g(n,ripple_db):
    beta=math.log(1./math.tanh(ripple_db/17.37))
    ga=math.sinh(beta/(2*n))
    a=lambda i:math.sin((2*i-1)*math.pi/(2*n))
    b=lambda i:ga*ga+math.sin(i*math.pi/n)**2
    gs=[1.,2*a(1)/ga]
    for i in range(2,n+1):gs.append(4*a(i-1)*a(i)/(b(i-1)*gs[i-1]))
    gs.append(1. if n%2 else (1/math.tanh(beta/4))**2)
    return gs

def lowpass_components(n=7):
    g=cheby_g(n,RIPPLE_DB);wc=2*math.pi*F_LPF_CUTOFF
    return [('L' if i%2==1 else 'C', R0*g[i]/wc if i%2==1 else g[i]/(R0*wc)) for i in range(1,n+1)]

def s21(f,tank_pf=TANK_OPT_PF, q_tank=70.,q_lpf=60.,n_lpf=7,l_deviation=None, c_deviation=None):
    p=np.asarray(tank_pf)*1e-12
    cin,c12,c23,ce,cm,cc=p
    w=2*math.pi*f
    l_deviation=np.ones(5) if l_deviation is None else np.asarray(l_deviation)
    c_deviation=np.ones(11) if c_deviation is None else np.asarray(c_deviation)
    # c_deviation 0-5 couplings, 6-10 tuning capacitors
    caps_coupling=np.array([cin,c12,c23,c23,c12,cin])*c_deviation[:6]
    caps_tuning=np.array([ce,cm,cc,cm,ce])*c_deviation[6:]
    matrix=np.eye(2,dtype=complex)
    def series(z):return np.array([[1,z],[0,1]],dtype=complex)
    def shunt(y):return np.array([[1,0],[y,1]],dtype=complex)
    for i in range(5):
        li=L_TANK*l_deviation[i]
        matrix=matrix @ series(1/(1j*w*caps_coupling[i]))
        # Constant parallel resistance loss at reference frequency -> simplified Q model
        rloss=q_tank*W_REF*li
        yl=1/(1j*w*li)+1j*w*caps_tuning[i]+1/rloss
        matrix=matrix @ shunt(yl)
    matrix=matrix @ series(1/(1j*w*caps_coupling[5]))
    for kind,val in lowpass_components(n_lpf) if n_lpf else []:
        if kind=='L': matrix=matrix@series(1j*w*val + W_REF*val/q_lpf)
        else:matrix=matrix@shunt(1j*w*val)
    A,B,C,D=matrix.ravel()
    return 2/(A+B/R0+C*R0+D)

def db(f,*args,**kwargs):return 20*np.log10(max(1e-15,abs(s21(f,*args,**kwargs))))

def model_summary(tank_pf=TANK_OPT_PF,qt=50.,ql=50.,n_lp=7):
    pb=np.linspace(F_MIN,F_MAX,111);ib=np.linspace(IMG_MIN,IMG_MAX,111)
    p=np.array([db(f,tank_pf,qt,ql,n_lp) for f in pb]);i=np.array([db(f,tank_pf,qt,ql,n_lp) for f in ib]);
    return {'passband_min_db':float(p.min()),'passband_max_db':float(p.max()),'worst_image_db':float(i.max()), 'insertion_max_db':float(-p.min())}

def main(out_dir=None):
    out_dir=Path(out_dir or Path(__file__).resolve().parent);out_dir.mkdir(parents=True,exist_ok=True)
    cases={
       '5 tank only Q50':model_summary(qt=50,n_lp=0),
       '5 tank + 7 LPF Q30':model_summary(qt=30,ql=40),
       '5 tank + 7 LPF Q50':model_summary(qt=50,ql=50),
       '5 tank + 7 LPF Q70':model_summary(qt=70,ql=70),
       'E24 nearest 5 tank + 7 LPF Q50':model_summary(TANK_E24_PF,qt=50,ql=50),
    }
    freqs=np.linspace(20e6,58e6,450)
    fig,ax=plt.subplots(figsize=(9.8,4.4))
    for name,p,q in [('5 resonators Q50, no LPF',TANK_OPT_PF,0),('5 resonators + 7-pole LPF, Q50',TANK_OPT_PF,7),('E24 candidate + 7-pole LPF, Q50',TANK_E24_PF,7)]:
       ax.plot(freqs/1e6,[db(f,p,50,50,q) for f in freqs],label=name)
    ax.axvspan(F_MIN/1e6,F_MAX/1e6,alpha=.13);ax.axvspan(IMG_MIN/1e6,IMG_MAX/1e6,alpha=.10)
    ax.set(title='RF preselector simulation: ideal components + constant Q loss (not PCB)',xlabel='Frequency (MHz)',ylabel='S21 (dB)',ylim=(-95,5));ax.grid(True,alpha=.2);ax.legend(fontsize=8,loc='lower left');fig.tight_layout()
    fig.savefig(out_dir/'Preselettore_RF_V2.2.png',dpi=170);plt.close(fig)
    # Fixed-seed Monte Carlo: initial L ±5%, capacitors ±2%, Qres 30...70, Qlp 40...70
    rng=np.random.default_rng(390022)
    pb=np.linspace(F_MIN,F_MAX,25);ib=np.linspace(IMG_MIN,IMG_MAX,8)
    samples=[]
    for k in range(500):
        ldev=1+rng.uniform(-.05,.05,5)
        cdev=1+rng.uniform(-.02,.02,11)
        qres=float(rng.uniform(30,70));qlpf=float(rng.uniform(40,70))
        pbdb=np.array([db(f,TANK_OPT_PF,qres,qlpf,7,ldev,cdev) for f in pb]);
        ibdb=np.array([db(f,TANK_OPT_PF,qres,qlpf,7,ldev,cdev) for f in ib]);
        samples.append({'sample':k+1,'passband_min_db':float(pbdb.min()),'worst_image_db':float(ibdb.max()),'q_tanks':qres,'q_lpf':qlpf,'pass_ge_minus6':bool(np.min(pbdb)>=-6),'image_le_minus60':bool(np.max(ibdb)<=-60)})
    success=sum(x['pass_ge_minus6'] and x['image_le_minus60'] for x in samples)
    with (out_dir/'MonteCarlo_Preselector_V2.2.csv').open('w',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=samples[0].keys());w.writeheader();w.writerows(samples)
    fig,ax=plt.subplots(figsize=(8.2,3.8))
    ax.scatter([a['passband_min_db'] for a in samples],[a['worst_image_db'] for a in samples],s=7,alpha=.4)
    ax.axvline(-6,ls='--');ax.axhline(-60,ls='--');ax.set(xlabel='Worst passband S21 (dB); must be >= -6',ylabel='Worst image S21 (dB); must be <= -60',title='Tolerance experiment (500 samples, no post-assembly tuning)');ax.grid(alpha=.2);fig.tight_layout();fig.savefig(out_dir/'Tolleranze_RF_V2.2.png',dpi=160);plt.close(fig)
    summary={
      'model':'5 capacitively-coupled shunt RLC resonators + n=7 0.3dB Chebyshev LPF; ideal element response, constant Q, 50 ohm terminations',
      'rf_band_mhz':[F_MIN/1e6,F_MAX/1e6],
      'image_band_mhz':[IMG_MIN/1e6,IMG_MAX/1e6],
      'ripple_db':RIPPLE_DB,'lpf_cutoff_mhz':F_LPF_CUTOFF/1e6,'lpf_g_values':cheby_g(7,RIPPLE_DB),
      'rf_l_nh':330,'rf_capacitors_opt_pf':list(TANK_OPT_PF),'rf_capacitors_e24_pf':list(TANK_E24_PF),
      'lpf': [{'kind':k,'value':v,'unit':'H' if k=='L' else 'F'} for k,v in lowpass_components(7)],
      'comparison_cases':cases,
      'monte_carlo_samples':len(samples),'mc_seed':390022,'criteria':{'passband_s21_min_db':-6,'image_s21_max_db':-60},
      'mc_joint_passes':success,'mc_joint_pass_rate':success/len(samples),
      'limitations':['Does NOT model PCB parasitics or shielding or RF inductor SRF, stray couplings or nonlinearities', 'Q of actual coil at 27 MHz unverified; 45 quoted in Coilcraft sheet is at 100 MHz','Not an in-circuit validated 50-ohm match; only power transmission simulated','Other filter position, mixer and NF tradeoff must be optimized','No native SPICE/ADS/KiCad ERC conducted']}
    (out_dir/'Risultati_RF_V2.2.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    assert cases['5 tank + 7 LPF Q50']['worst_image_db'] < -60
    assert cases['5 tank + 7 LPF Q50']['insertion_max_db'] < 7
    assert len(samples)==500
    assert all(math.isfinite(s['passband_min_db']) and math.isfinite(s['worst_image_db']) for s in samples)
    print(json.dumps({k:v for k,v in summary.items() if k in ['comparison_cases','mc_joint_passes','mc_joint_pass_rate']},indent=2))
    return summary
if __name__=='__main__':main()
