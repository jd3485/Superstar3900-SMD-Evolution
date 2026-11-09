#!/usr/bin/env python3
"""V3.0: bounded small-signal RX cascade study, not circuit, blocker, SPICE or VNA validation.
Reuses manufacturer-based, frequency-dependent preselector from V2.9.
ADL5535 assumed typical 20 MHz: gain 16.7 dB, NF 3.0 dB, OIP3 41.5 dBm, P1dB out 17.7 dBm.
ADE-1+ assumed (manufacturer generic): mixer conversion loss 5dB, input IP3 15dBm, LO +7 dBm.
NF_mixer=conversion_loss is an approximative assumption; matched small-signal Friis, no antenna noise.
This model intentionally does NOT inherit the V2.9 image rejection for hypothetical split filters.
"""
from __future__ import annotations
import csv, json, math, importlib.util
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
V29=HERE.parent/'V2.9'/'modello_coilcraft_v29.py'
sp=importlib.util.spec_from_file_location('rf_v29',V29)
rf=importlib.util.module_from_spec(sp)
sp.loader.exec_module(rf)

AMP={'gain_db':16.7,'nf_db':3.0,'oip3_dbm':41.5,'p1db_out_dbm':17.7,'current_mA':97.0,'supply_v':5.0}
MIX={'gain_db':-5.0,'nf_db_assumed':5.0,'iip3_dbm':15.0,'lo_dbm':7.0}
RX=rf.RX

# power-gain linear; intercept dBm to mW; IIP3 cascade uses preceding gain only.
def lin(x):return 10.0**(x/10.0)
def db(x):return 10*math.log10(x)
def stage(name,gain_db,nf_db,iip3_dbm=None):
    return {'name':name,'gain_db':float(gain_db),'nf_db':float(nf_db),'iip3_dbm':iip3_dbm}
def passive(name,loss_db):return stage(name,-loss_db,loss_db)
def cascade(stages):
    gain_pre=1.0; F=1.0; iip3_inv=0.0
    for s in stages:
        F += (lin(s['nf_db'])-1.0)/gain_pre
        if s['iip3_dbm'] is not None:
            iip3_inv += gain_pre / lin(s['iip3_dbm'])
        gain_pre *= lin(s['gain_db'])
    return {'NF_dB':db(F),'gain_dB':db(gain_pre),
            'IIP3_dBm':(-db(iip3_inv) if iip3_inv>0 else None)}

def assemble(mode,loss):
    amp=stage('ADL5535 @20MHz datasheet proxy',AMP['gain_db'],AMP['nf_db'],AMP['oip3_dbm']-AMP['gain_db'])
    mixer=stage('ADE-1+ (assumed)',MIX['gain_db'],MIX['nf_db_assumed'],MIX['iip3_dbm'])
    pre=passive('V2.9 full preselector',loss)
    if mode=='RX_NORMAL': return [pre,amp,mixer]
    if mode=='RX_PAD_POST6': return [pre,amp,passive('6 dB pad after LNA',6.),mixer]
    if mode=='RX_LNA_BYPASS': return [pre,mixer]
    if mode=='RX_PAD_PRE6': return [pre,passive('6 dB pad ahead of LNA',6.),amp,mixer]
    if mode=='RX_POST_FILTER_HYPOTHETICAL':
        # 1.0 dB pre loss, 1.0 dB post loss AS HYPOTHESIS ONLY: image rejection not modeled
        return [passive('HYP pre-filter 1dB',1.),amp,passive('HYP post-filter 1dB',1.),mixer]
    raise ValueError(mode)

def all_results():
    modes=['RX_NORMAL','RX_PAD_POST6','RX_LNA_BYPASS','RX_PAD_PRE6','RX_POST_FILTER_HYPOTHETICAL']
    ss,_=rf.twoport(rf.CORE,RX)
    loss=-20*np.log10(abs(ss))
    rows=[];points=[]
    for mode in modes:
        vals=[]
        for f,l in zip(RX,loss):
            r=cascade(assemble(mode,float(l)))
            r['frequency_MHz']=float(f/1e6)
            r['mode']=mode
            r['preselector_loss_dB']=float(l) if mode!='RX_POST_FILTER_HYPOTHETICAL' else None
            vals.append(r)
            points.append(r)
        rows.append({'mode':mode,'nf_min_dB':min(x['NF_dB'] for x in vals),
            'nf_max_dB':max(x['NF_dB'] for x in vals),
            'iip3_min_dBm':min(x['IIP3_dBm'] for x in vals),
            'iip3_max_dBm':max(x['IIP3_dBm'] for x in vals),
            'gain_min_dB':min(x['gain_dB'] for x in vals),
            'gain_max_dB':max(x['gain_dB'] for x in vals),
            'image_rejection_validated':False,
            'image_rejection_status':'full V2.9 prefilter model only; no PCB/mixer' if mode!='RX_POST_FILTER_HYPOTHETICAL' else 'UNVERIFIED SPLIT TOPOLOGY'})
    return rows,points

def sanity_tests():
    rows, points=all_results();d={r['mode']:r for r in rows}
    assert rf.check()
    assert len(rows)==5 and len(points)==5*len(RX)
    for r in rows:
        assert np.isfinite(r['nf_max_dB']) and np.isfinite(r['iip3_min_dBm'])
        assert r['nf_min_dB']<=r['nf_max_dB']
        assert not r['image_rejection_validated']
    assert 5.0<d['RX_NORMAL']['nf_max_dB']<6.5
    assert d['RX_PAD_POST6']['iip3_min_dBm']>d['RX_NORMAL']['iip3_min_dBm']+5
    assert d['RX_PAD_POST6']['nf_max_dB']>d['RX_NORMAL']['nf_max_dB']
    assert d['RX_LNA_BYPASS']['iip3_min_dBm']>d['RX_PAD_POST6']['iip3_min_dBm']
    assert d['RX_LNA_BYPASS']['nf_max_dB']>d['RX_NORMAL']['nf_max_dB']
    assert d['RX_PAD_PRE6']['nf_max_dB']>d['RX_PAD_POST6']['nf_max_dB']+4
    assert abs(AMP['current_mA']*AMP['supply_v']/1000-0.485)<1e-9
    assert all(x['NF_dB']>0 for x in points)
    # Thermal noise reference: at 290K in 2.4kHz, -174 dBm/Hz approximation.
    assert -141<(-174+10*math.log10(2400))<-139
    return True

def generate():
    assert sanity_tests()
    rows,points=all_results()
    with (HERE/'Risultati_Catena_RF_V3.0.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    with (HERE/'Sweep_Frequenze_Catena_V3.0.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(points[0]));w.writeheader();w.writerows(points)
    limits={'revision':'V3.0','model':'linear small-signal Friis + approximate IIP3 cascade + Coilcraft V2.9 S21, 50ohm',
      'RF_filter_vendor_model':'0805CS fitted R(f), Cpar, L; NOT coupon or EM measurement',
      'amp_20MHz_proxy':AMP,'mixer_assumptions':MIX,
      'modes':rows,'limitations':[
        'ADL5535 20 MHz typ values are not RF measurements at 27 MHz or guaranteed mins/maxes.',
        'Mixer NF approximated as 5dB conversion loss. SSB vs DSB figure and port match remain unverified.',
        'S21 50ohm transducer-loss mapped to matched passive NF; mismatch and noise correlation neglected.',
        'LNA post-pad and bypass routing are idealized, no insertion loss / return-loss for switches.',
        'Image rejection of preselector alone from V2.9 may not equal assembled front-end image rejection.',
        'Hypothetical split filter is not the V2.9 circuit; no image-rejection claim allowed.',
        'IM3 cascade only weak-signal, two-tone, frequency-independent ideal model. No P1dB or reciprocal-mixing limit.',
        'No PCB, RF protection, LO phase-noise, IF load, EM, or KiCad ERC/DRC simulation.',
      ],'decision':'keep full prefilter ahead of LNA for first test coupon; add selectable post-LNA pad and LNA bypass pending design; do not approve PCB',
      'progress_percent_estimated':35}
    (HERE/'Risultati_Assunzioni_Limiti_V3.0.json').write_text(json.dumps(limits,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    pal={'RX_NORMAL':'#176D83','RX_PAD_POST6':'#D97706','RX_LNA_BYPASS':'#A855F7','RX_PAD_PRE6':'#DC2626','RX_POST_FILTER_HYPOTHETICAL':'#6B7280'}
    pretty={'RX_NORMAL':'LNA inserito','RX_PAD_POST6':'LNA + pad 6dB dopo','RX_LNA_BYPASS':'LNA escluso','RX_PAD_PRE6':'Pad 6dB prima LNA','RX_POST_FILTER_HYPOTHETICAL':'Filtri divisi (non verificati)'}
    fig,ax=plt.subplots(figsize=(8.8,5))
    for r in rows:
        x=r['nf_max_dB'];y=r['iip3_min_dBm']
        ax.scatter(x,y,marker='o',s=80,color=pal[r['mode']]);offset=(6,-15) if r['mode']=='RX_NORMAL' else ((-1,13) if r['mode']=='RX_POST_FILTER_HYPOTHETICAL' else (7,5));ax.annotate(pretty[r['mode']],(x,y),xytext=offset,textcoords='offset points',fontsize=9)
    ax.axvline(6,color='#888',ls='--',lw=1,label='Obiettivo esplorativo NF <= 6dB')
    ax.set(xlabel='NF massimo nella gamma (dB, meno e meglio)',ylabel='IIP3 minimo (dBm, più e meglio)',title='Superstar 3900 V3.0 | Compromesso rumore / linearità')
    ax.grid(alpha=.2);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(HERE/'Grafico_Friis_IIP3_V3.0.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.8,4.3))
    f=RX/1e6;s21,_=rf.twoport(rf.CORE,RX)
    ax.plot(f,-20*np.log10(abs(s21)),color='#176D83',lw=2)
    ax.set(xlabel='Frequenza RX (MHz)',ylabel='Perdita preselettore (dB)',title='V3.0 | Perdita del filtro V2.9 in banda, modello produttore')
    ax.grid(alpha=.2);fig.tight_layout();fig.savefig(HERE/'Perdita_Preselettore_RX_V3.0.png',dpi=175);plt.close(fig)
    tests={'model_self_check':'PASS','scenario_count':len(rows),'frequency_samples':len(points),
        'friis_and_iip3_modes':'PASS','post_pad_tradeoff':'PASS','front_pad_penalty':'PASS',
        'vendor_filter_reuse':'PASS','power_budget_mW':485,'erc_native':'NOT RUN',
        'ngspice_native':'NOT RUN','hardware_rx_and_vna':'NOT RUN'}
    (HERE/'Report_Test_V3.0.json').write_text(json.dumps(tests,indent=2)+'\n',encoding='utf-8')
    print('V3.0 PASS',json.dumps(rows,indent=2))
    return rows

if __name__=='__main__':generate()
