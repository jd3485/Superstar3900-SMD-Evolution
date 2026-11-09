#!/usr/bin/env python3
"""V2.3 - Linear receiver-cascade comparison, NOT a circuit/EM simulator.
Sources: ADL5535/ADL5536 Analog Devices 20 MHz datasheet table,
Mini-Circuits ADE-1+ generic LO +7 dBm 5 dB conversion loss/+15 dBm IIP3.
Mixer noise figure approximated as its conversion loss (simple model only).
No verification at 27 MHz, no S11, blocker spectrum, phase noise, PCB, or hardware.
Run: python 03_Verifiche/V2.3/rx_cascade_v23.py
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import json, csv, math, random
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent

def db2lin(x): return 10**(x/10)
def lin2db(x): return 10*math.log10(x)

@dataclass(frozen=True)
class Stage:
    name:str
    gain_db:float
    noise_figure_db:float
    iip3_dbm: Optional[float] = None

# Friis: Ftotal=1 + SUM_i (Fi-1) / G_before_i.
# Third-order: 1/P_IIP3(in) = SUM_i G_before_i / P_IIP3_i,
# input intercepts are dBm, G are available power gains (linear).
def cascade(stages):
    total_f=1.0;gain_before=1.0; ip3_recip=0.0
    for s in stages:
        total_f+=(db2lin(s.noise_figure_db)-1.0)/gain_before
        if s.iip3_dbm is not None:
            ip3_recip+=gain_before/db2lin(s.iip3_dbm)
        gain_before*=db2lin(s.gain_db)
    return {'NF_dB':lin2db(total_f),'gain_dB':lin2db(gain_before),
            'IIP3_dBm':-lin2db(ip3_recip) if ip3_recip>0 else None}

def passive(label,loss):return Stage(label,-loss,loss,None)

def lna(label):
    if label=='ADL5536':
        # Analog Devices datasheet @20 MHz, typical values, not guaranteed at 27 MHz
        g,nf,oip=20.2,2.5,39.5
    elif label=='ADL5535':
        g,nf,oip=16.7,3.0,41.5
    else:raise ValueError(label)
    return Stage(label,g,nf,oip-g)

def mixer(higher_lo=False):
    if higher_lo:return Stage('ADE-1H+ (LO +17dBm)',-5.3,5.3,23.0)
    return Stage('ADE-1+ (LO +7dBm)',-5.,5.,15.)

# All pre/post losses are ASSUMED. Splitting the v2.2 filter does not
# preserve its computed 69-dB image rejection by assumption.
CONFIGS={
    'A_v22_pre4p5_5536': [passive('V2.2 entire front filter',4.5),lna('ADL5536'),mixer()],
    'B_split_5536': [passive('front preselector',1.5),lna('ADL5536'),passive('post-LNA pre-mixer filter',3.0),mixer()],
    'C_split_5535': [passive('front preselector',1.5),lna('ADL5535'),passive('post-LNA pre-mixer filter',3.0),mixer()],
    'D_split_5535_pad6': [passive('front preselector',1.5),lna('ADL5535'),passive('switched pad after LNA',6.0),passive('post-LNA filter',3.0),mixer()],
    'E_split_5536_pad6': [passive('front preselector',1.5),lna('ADL5536'),passive('switched pad after LNA',6.0),passive('post-LNA filter',3.0),mixer()],
    'F_lna_bypass_v22': [passive('V2.2 passive filter',4.5),mixer()],
    'G_split_5535_ADE1H_UNAVAILABLE_LO': [passive('front preselector',1.5),lna('ADL5535'),passive('post-LNA filter',3.0),mixer(True)]
}

def sample_config(name,rng):
    orig=CONFIGS[name]; out=[]
    for s in orig:
        if s.name.startswith('ADL553'):
            dg=rng.uniform(-0.8,0.8)
            dnf=rng.uniform(-0.5,0.5)
            doip=rng.uniform(-3.0,3.0)
            iip_orig=s.iip3_dbm+s.gain_db
            out.append(Stage(s.name,s.gain_db+dg,s.noise_figure_db+dnf,
                             (iip_orig+doip)-(s.gain_db+dg)))
        elif s.name.startswith('ADE-1'):
            dloss=rng.uniform(-0.8,0.8)
            out.append(Stage(s.name,s.gain_db-dloss,s.noise_figure_db+dloss,
                             s.iip3_dbm+rng.uniform(-3,3)))
        else:
            if 'front' in s.name.lower():dv=rng.uniform(-0.5,0.5)
            elif 'post' in s.name.lower() and 'pad' not in s.name.lower():dv=rng.uniform(-0.8,0.8)
            elif 'pad' in s.name.lower():dv=rng.uniform(-0.2,0.2)
            else:dv=rng.uniform(-0.7,0.7)
            loss=max(0.,s.noise_figure_db+dv)
            out.append(passive(s.name,loss))
    return cascade(out)

def run_all():
    rows=[]
    for code, stages in CONFIGS.items():
        row={'scenario':code,**cascade(stages)}
        row['filter_image_rejection_db']='UNVERIFIED'
        row['lo_compatibility']='NO: requires +17dBm' if 'ADE1H' in code else 'candidate LO +7dBm, not measured'
        rows.append(row)
    with (HERE/'Confronto_Catene_RF_V2.3.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    rng=random.Random(390023)
    mcs=[]
    for nm in ['B_split_5536','C_split_5535','D_split_5535_pad6','E_split_5536_pad6']:
        vals=[sample_config(nm,rng) for _ in range(2000)]
        for metric in ['NF_dB','IIP3_dBm','gain_dB']:
            z=np.array([v[metric] for v in vals]);p=np.percentile(z,[5,50,95]);
            mcs.append({'scenario':nm,'metric':metric,'P05':round(float(p[0]),3),
                        'median':round(float(p[1]),3),'P95':round(float(p[2]),3),
                        'N':len(vals),'comment':'ILLUSTRATIVE UNIFORM INPUT UNCERTAINTY, NOT YIELD'})
    with (HERE/'Studio_Sensibilita_Parametri_V2.3.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=mcs[0].keys());w.writeheader();w.writerows(mcs)
    # Illustrative Pareto map: lower NF (left) + higher IIP3 (up) desirable.
    fig,ax=plt.subplots(figsize=(9.2,5.4))
    for j,row in enumerate(rows):
        if row['IIP3_dBm'] is not None:
            ax.scatter(row['NF_dB'],row['IIP3_dBm'],s=65)
            label=row['scenario'].split('_')[0]
            ax.annotate(label,(row['NF_dB'],row['IIP3_dBm']),xytext=(5,5),textcoords='offset points',fontsize=10)
    ax.axvline(6,ls='--',lw=1,label='Target NF <=6 dB (preliminary)')
    ax.axhline(0,ls=':',lw=1,label='Illustrative IIP3 >=0 dBm')
    ax.set_xlabel('System noise figure (dB, lower is better)')
    ax.set_ylabel('Input intercept IIP3 (dBm, higher is better)')
    ax.set_title('V2.3 - Nominal RF architecture comparison (model only)')
    ax.grid(alpha=.25);ax.legend(loc='upper right',fontsize=8)
    fig.tight_layout();fig.savefig(HERE/'Compromesso_Rumore_Linearita_V2.3.png',dpi=175);plt.close(fig)
    report={
      'revision':'V2.3','model':'Friis RF noise budget and approximate cascaded IIP3; no physical circuit simulation',
      'data_basis':{'ADL5535_20MHz':{'gain_dB':16.7,'noise_figure_dB':3.0,'OIP3_dBm':41.5},
                    'ADL5536_20MHz':{'gain_dB':20.2,'noise_figure_dB':2.5,'OIP3_dBm':39.5},
                    'ADE_1_plus':{'conversion_loss_dB':5.,'IIP3_dBm':15,'LO_dBm':7},
                    'ADE_1H_plus':{'conversion_loss_dB':5.3,'IIP3_dBm':23,'LO_dBm':17}},
      'assumptions':['50-ohm available power gains, lossless match not verified',
                     'passive stage noise figure equals insertion loss at reference temperature',
                     'mixer SSB NF approximated by its conversion loss (not guaranteed)',
                     'IIP3 computed assuming equal-tone weak-signal third-order model',
                     'ADL amplifier typical characteristics from datasheet AT 20 MHz, not 27 MHz',
                     'preselector loss split 1.5+3.0 dB is hypothetical, not a redesigned filter',
                     'V2.2 image rejection ~69 dB CANNOT be carried over to split architecture',
                     'not a close-in blocker/spur/reciprocal-mixing/compression analysis'],
      'results':rows,'illustrative_sensitivity':mcs,
      'next_gates':['redesign matching RF preselector, measure/simulate S11/S21 image and insertion loss',
                    'verify LNA values at 27 MHz including close-spaced IM3',
                    'establish actual LO level and phase noise into ADE-1+',
                    'complete KiCad schematic and ERC, PCB EMI model',
                    'bench NF, two-tone IMD and overload with calibrated sources']}
    (HERE/'Risultati_Catena_RX_V2.3.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return rows

if __name__=='__main__':
    for v in run_all():print(v['scenario'], 'NF=',round(v['NF_dB'],3),
      'IIP3=',round(v['IIP3_dBm'],3),'Gain=',round(v['gain_dB'],3))
