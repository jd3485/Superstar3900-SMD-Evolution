#!/usr/bin/env python3
"""Superstar 3900 SMD Evolution V2.5 -- 6-band *RX ONLY* RF filter-bank study.

Run: python filter_bank_v25.py --root /path/to/Superstar3900_SMD_Evolution_V2.5
Dependencies: numpy, matplotlib. Uses prior V2.3 and V2.4 modules for consistency.

IMPORTANT: DESIGN MODEL ONLY: C/L values are non-stock ideals, Q is frequency-independent,
RF switch losses are hypothetical example scenarios, no PCB parasitics, pad capacitance,
loading/matching between active stages, relay leakage/coupling, or calibrated RF measurements.
"""
from __future__ import annotations
import argparse, csv, json, math, importlib.util
from pathlib import Path
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

Z0=50.; PI=np.pi; F_REF=26.960e6
# The 5-parameter seed was optimized numerically as a **broad** 3-shunt-tank BPF;
# it is not an E-series BOM and notably does not provide sharp six-band selectivity.
# [input series cap, intertank series cap, outer tank shunt C, middle tank shunt C, tank L]
BASE_SEED=[71.44e-12,35.00e-12,103.137e-12,133.692e-12,200e-9]


def load_module(path, name):
    spec=importlib.util.spec_from_file_location(name,str(path));mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod);return mod


def extract_bands(plan_csv:Path):
    out=defaultdict(list)
    with plan_csv.open(encoding='utf-8-sig',newline='') as f:
        for r in csv.DictReader(f,delimiter=';'):
            out[r['Banda']].append(int(r['Frequenza_Hz']))
    bands=[]
    for band in 'ABCDEF':
        f=np.array(sorted(set(out[band])),dtype=float)
        assert len(f)==45 and len(out[band])==45, f'Expected 45 channel positions in {band}'
        bands.append({'band':band,'lo_hz':int(min(f)),'hi_hz':int(max(f)),
                      'center_hz':(min(f)+max(f))/2,'freq_hz':f})
    assert sum(len(b['freq_hz']) for b in bands)==270
    return bands


def branch_nominal(center_hz):
    # preserve normalized impedance response of each LC when the center frequency changes
    x=np.array(BASE_SEED)*F_REF/center_hz
    ce,cc,cte,ctm,L=x
    return [('CS',ce),('LPAR',L),('CPAR',cte),('CS',cc),
            ('LPAR',L),('CPAR',ctm),('CS',cc),
            ('LPAR',L),('CPAR',cte),('CS',ce)]


def response(elements,f_hz,q=90.,tan_delta=.001,z0=Z0):
    f=np.atleast_1d(np.asarray(f_hz,float));w=2*PI*f
    A=np.ones_like(f,dtype=complex);B=np.zeros_like(f,dtype=complex)
    C=np.zeros_like(f,dtype=complex);D=np.ones_like(f,dtype=complex)
    for typ,val in elements:
        if typ=='CS':
            z=1/(1j*w*val)+tan_delta/(w*val)
            aa,bb,cc,dd=1,z,0,1
        elif typ=='LPAR':
            z=1j*w*val +w*val/q
            aa,bb,cc,dd=1,0,1/z,1
        elif typ=='CPAR':
            y=1j*w*val+w*val*tan_delta
            aa,bb,cc,dd=1,0,y,1
        else: raise ValueError(typ)
        A,B,C,D=A*aa+B*cc,A*bb+B*dd,C*aa+D*cc,C*bb+D*dd
    den=A+B/z0+C*z0+D
    s21=2/den;s11=(A+B/z0-C*z0-D)/den
    return -20*np.log10(np.maximum(np.abs(s21),1e-50)),20*np.log10(np.maximum(np.abs(s11),1e-50))


def branch_metrics(elements, freqs, q=90., switches_db=0.):
    loss,return_db=response(elements,freqs,q=q)
    rej,_=response(elements,freqs+21.390e6,q=q)
    return {'filter_max_loss_db':float(np.max(loss)),
            'front_max_loss_db':float(np.max(loss)+switches_db),
            'min_image_rej_db':float(np.min(rej)),
            'worst_s11_db':float(np.max(return_db))}


def mc_elements(elems,rng,tol=.02):
    # all 10 passives varied independently; not actual supplier/component distribution
    return [(typ,val*(1+rng.uniform(-tol,tol))) for typ,val in elems]


def run(root:Path,mc_count=500,seed=390025):
    ver=root/'03_Verifiche'/'V2.5';ver.mkdir(parents=True,exist_ok=True)
    m24=load_module(root/'03_Verifiche'/'V2.4'/'rf_preselector_v24.py','rf_prior_v24')
    m23=load_module(root/'03_Verifiche'/'V2.3'/'rx_cascade_v23.py','rx_prior_v23')
    bands=extract_bands(root/'02_Piano_Frequenze'/'Tabella_270_canali.csv')
    results=[];comp=[]; rng=np.random.default_rng(seed);stresses=[]
    post_lo=m24.lowpass(7)
    for band in bands:
        key=band['band'];freq=band['freq_hz'];f0=band['center_hz'];e=branch_nominal(f0)
        metrics=branch_metrics(e,freq,90.,0.)
        post_rej=float(np.min(-20*np.log10(np.abs(m24.network(post_lo,freq+21.39e6,60.)[0]))))
        # Two 6-way selection switches per branch, one before and one after bank.
        # 0.2dB and 0.7dB per switch are *scenario assumptions*, not 27MHz guarantees.
        relay_db=0.4;soi_db=1.4
        for scenario,sw_loss in [('SMT_RF_RELAY_ASSUMED',relay_db),('SOI_SP6T_ASSUMED',soi_db)]:
            frontend=metrics['filter_max_loss_db']+sw_loss
            chain=m23.cascade([m23.passive('switch+bank BPF pre LNA',frontend),
                     m23.lna('ADL5535'),m23.passive('post-LNA LP7',float(m24.measures(post_lo,60)['max_pass_loss_db'])),
                     m23.mixer()])
            row={'band':key,'scenario':scenario,'start_mhz':band['lo_hz']/1e6,'end_mhz':band['hi_hz']/1e6,
                 'center_mhz':f0/1e6,'filter_max_loss_db':metrics['filter_max_loss_db'],
                 'switch_pair_assumed_loss_db':sw_loss,'front_max_loss_db':frontend,
                 'pre_lna_image_rej_min_db':metrics['min_image_rej_db'],
                 'post_lna_LP7_image_min_db':post_rej,
                 'image_rej_optimistic_sum_db':metrics['min_image_rej_db']+post_rej,
                 'worst_s11_db_filter_only':metrics['worst_s11_db'],
                 'cascade_NF_db_illustrative':chain['NF_dB'],
                 'cascade_IIP3_dbm_illustrative':chain['IIP3_dBm']}
            comp.append(row)
        results.append({'band':key,'start_hz':band['lo_hz'],'end_hz':band['hi_hz'],'center_hz':f0,
                        **metrics,'components': [{'kind':kind,'value_SI':float(value)} for kind,value in e]})
        for j in range(mc_count):
            q=float(rng.uniform(45,120));perturb=mc_elements(e,rng)
            met=branch_metrics(perturb,freq,q,0.)
            # combine only in ideal isolated, 50-ohm terminated cascade; caveat in report
            ok_relay=(met['filter_max_loss_db']+.4<=1.5 and met['min_image_rej_db']+post_rej>=60)
            ok_soi=(met['filter_max_loss_db']+1.4<=1.5 and met['min_image_rej_db']+post_rej>=60)
            stresses.append({'band':key,'case':j,'Q_inductor_assumed':q,
                             'filter_max_loss_db':met['filter_max_loss_db'],
                             'min_image_rej_db':met['min_image_rej_db'],
                             'relay_front_loss_db':met['filter_max_loss_db']+.4,
                             'soi_front_loss_db':met['filter_max_loss_db']+1.4,
                             'relay_pass_illustrative':int(ok_relay),
                             'soi_pass_illustrative':int(ok_soi)})
    # standalone baseline from V2.4
    base=m24.measures(m24.plan()['HP5_LP9'],60.)
    for name,data in [('Confronto_Sei_Bande_V2.5.csv',comp),('Stress_Test_V2.5.csv',stresses)]:
        with (ver/name).open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=data[0].keys());w.writeheader();w.writerows(data)
    with (ver/'Valori_Ideali_Sei_Filtri_V2.5.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(['Banda','Rif_non_PCB','Tipo','Valore_ideale','Unita','Stato'])
        for r in results:
            for ix,e in enumerate(r['components'],1):
                is_l=e['kind']=='LPAR'
                w.writerow([r['band'],f'B{r["band"]}-{ix:02d}',e['kind'],
                    round(e['value_SI']*(1e9 if is_l else 1e12),4),'nH' if is_l else 'pF',
                    'MODELLO - non valore E-series / BOM approvata'])
    counts={s:sum(int(r[s+'_pass_illustrative']) for r in stresses) for s in ['relay','soi']}
    summary={'release':'V2.5',
             'study_type':'Six branches of wide-ish three-shunt-resonator LC BPF (10 passives each); not six narrow high-selectivity filters',
             'frequency_plan_positions_total':sum(len(b['freq_hz']) for b in bands),
             'model':'ABCD 50ohm, 10 ideal series/shunt C/L elements, L series R=omega L/Q; no PCB parasitics',
             'series_switches_count':2,'switch_loss_scenarios_dB_each':{'SMT_RF_RELAY_ASSUMED':.2,'SOI_SP6T_ASSUMED':.7},
             'post_LNA_common_filter':'LP7 from V2.4; calculated as separately matched/isolated stage',
             'baseline_unbanked_HP5_LP9_Q60':base,
             'nominal_filter_Q':90.,'mc_Q_uniform_range':[45,120],
             'mc_each_element_tolerance_percent_uniform':2,
             'mc_cases_per_band':mc_count,'mc_total':len(stresses),'seed':seed,
             'nominal_bank_results':comp,
             'mc_pass_fraction_relay_assumptions':counts['relay']/len(stresses),
             'mc_pass_fraction_soi_assumptions':counts['soi']/len(stresses),
             'test_gates':{'max_pre_LNA_loss_db':1.5,'min_image_summed_db':60},
             'decision':'NO-GO FOR PCB: front-end filter and especially switch + layout losses and 6-band benefit not validated; evaluate SMT relay vs CMOS with real 27MHz S params, tuned filters, leakage/isolation and layout',
             'warning':'Image suppression is the sum of isolated matched stages, not the true assembled bank S21; this is an optimistic systems-level bound',
             'component_source_caveat':'Relay nominal 0.2dB is max at 1GHz in Omron data, NOT specified 27MHz. pSemi PE42462 0.7dB typical is whole-band marketing figure, NOT 27MHz measured.',
             'other_blockers':['actual 27MHz Q and SRF of 190-210nH inductors','S parameters of input/output switches and PCB','six disconnected filters may couple/leak','MC ±2% component variations not a manufacturing yield model','receiver mixer + LO with image spur suppression, LNA real intercept','KiCad ERC/DRC and bench VNA + NF test','TX path must bypass or isolate RX-only filter bank']}
    (ver/'Risultati_V2.5.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
    # figures
    fig,ax=plt.subplots(figsize=(9.4,4.6))
    xx=np.linspace(25.3e6,28.6e6,400)
    for res in results:
        y,_=response(branch_nominal(res['center_hz']),xx,q=90)
        ax.plot(xx/1e6,y,lw=1.3,label=f"{res['band']} ({res['center_hz']/1e6:.3f})")
    ax.axvspan(25.615,28.305,alpha=.07)
    ax.set(xlabel='Frequenza (MHz)',ylabel='Perdita S21 del solo BPF (dB)',title='V2.5 – sei percorsi RX; Q ipotetico = 90',ylim=(0,6))
    ax.grid(alpha=.2);ax.legend(ncol=3,fontsize=8);fig.tight_layout();fig.savefig(ver/'Bande_BPF_V2.5.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9.4,4.5))
    ks=np.arange(6);sw_relay=np.array([r['front_max_loss_db'] for r in comp if r['scenario']=='SMT_RF_RELAY_ASSUMED']);sw_soi=np.array([r['front_max_loss_db'] for r in comp if r['scenario']=='SOI_SP6T_ASSUMED'])
    ax.bar(ks-.19,sw_relay,width=.37,label='2× 0,2 dB (relè SMT, ipotesi)')
    ax.bar(ks+.19,sw_soi,width=.37,label='2× 0,7 dB (SOI, ipotesi)')
    ax.axhline(base['max_pass_loss_db'],ls=':',label=f"V2.4 filtro unico (Q60): {base['max_pass_loss_db']:.2f} dB")
    ax.axhline(1.5,ls='--',label='Target ingresso RX 1,5 dB')
    ax.set(xlabel='Banda',ylabel='Perdita max prima dell’LNA (dB)',title='V2.5 – i due commutatori possono annullare il vantaggio',xticks=ks,xticklabels=list('ABCDEF'))
    ax.grid(axis='y',alpha=.2);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(ver/'Perdite_Switch_V2.5.png',dpi=160);plt.close(fig)
    return summary

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);ap.add_argument('--mc',type=int,default=500)
    args=ap.parse_args();s=run(Path(args.root),args.mc)
    print(json.dumps({k:s[k] for k in ['release','frequency_plan_positions_total','mc_total','mc_pass_fraction_relay_assumptions','mc_pass_fraction_soi_assumptions','baseline_unbanked_HP5_LP9_Q60','decision']},indent=2,ensure_ascii=False))
