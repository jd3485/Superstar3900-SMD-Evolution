#!/usr/bin/env python3
"""V6.6 - analisi di rete RLC a 2 porte, 50 ohm, RX only.

Si calcolano S11/S21 con nodi RF_IN, RF_MID, RF_OUT, perdite (Q)
e capacita' parassita diretta RF_IN--RF_OUT. Non e' SPICE vendor,
non e' S-parameter misurato, NON e' validazione per fabbricazione.
Eseguire PYTHONDONTWRITEBYTECODE=1 python simula_preselettore_lc_v66.py
"""
from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass, asdict, replace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
V65_PATH = ROOT / '02_Piano_Frequenze/V6.5/MAPPATURA_270_MIXER_IMMAGINE_V6.5.csv'
HERE = Path(__file__).resolve().parent
Z0 = 50.0
F0_HZ = math.sqrt(25e6 * 29e6)

@dataclass(frozen=True)
class Parts:
    # Valori PROPOSTI e NON qualificati dal produttore.
    l1_h: float = 2.0e-6
    l2_h: float = 22e-9
    l3_h: float = 2.0e-6
    c1_f: float = 17.5e-12  # C601 + C602 = 16pF + 1.5pF (parallelo)
    c2_f: float = 1591e-12  # C603 + C604 = 1500pF + 91pF
    c3_f: float = 17.5e-12  # C605 + C606 = 16pF + 1.5pF (parallelo)
    q_l1: float = 60.0       # Q equivalente assunto a 26.9258MHz
    q_l2: float = 60.0
    q_l3: float = 60.0
    q_c: float = 400.0
    srf_l1_hz: float = 90e6 # ipotesi, NON specifica di un MPN
    srf_l2_hz: float = 350e6
    srf_l3_hz: float = 90e6
    c_feed_f: float = 0.05e-12  # ACCOPPIAMENTO PARASSITA, non BOM


def load_channels() -> list[dict]:
    with V65_PATH.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def two_port(freq_hz, p: Parts = Parts()):
    """Return (S21,S11). Nodal elimination of middle node, Y->S.

    The finite-Q inductor is (R + jwL) || Cwinding, with Cwinding
    chosen from hypothetical self-resonance. Capacitor is ESR + 1/(jwC).
    The model cannot predict distributed near-field coupling or package SRF.
    """
    f = np.asarray(freq_hz, dtype=float)
    if np.any(f <= 0):
        raise ValueError('Frequencies must be positive')
    w = 2*np.pi*f
    w0 = 2*np.pi*F0_HZ

    def zl(L, Q, SRF):
        if L <= 0 or Q <= 0 or SRF <= 0:
            raise ValueError('Invalid inductor')
        rp = w0 * L / Q
        bare = rp + 1j*w*L
        cw = 1.0 / ((2*np.pi*SRF)**2*L)
        return 1 / (1/bare + 1j*w*cw)

    def zc(C):
        if C <= 0 or p.q_c <= 0:
            raise ValueError('Invalid capacitor')
        return 1/(w0*C*p.q_c) + 1/(1j*w*C)

    z1 = zl(p.l1_h, p.q_l1, p.srf_l1_hz) + zc(p.c1_f)
    z3 = zl(p.l3_h, p.q_l3, p.srf_l3_hz) + zc(p.c3_f)
    y2 = 1/zl(p.l2_h, p.q_l2, p.srf_l2_hz) + 1/zc(p.c2_f)
    # Riduzione del nodo centrale, Y a due porte.
    a = 1/z1
    b = 1/z3
    d = a + b + y2
    y11 = a - a*a/d + 1j*w*p.c_feed_f
    y22 = b - b*b/d + 1j*w*p.c_feed_f
    y12 = -(a*b/d) - 1j*w*p.c_feed_f
    # Inversione esplicita della matrice S=(I-z0Y)(I+z0Y)^-1
    den = (1+Z0*y11)*(1+Z0*y22) - (Z0*y12)**2
    s21 = -2*Z0*y12 / den
    s11 = ((1-Z0*y11)*(1+Z0*y22)+(Z0*y12)**2)/den
    return s21,s11


def attenuation_db(s):
    return -20.0*np.log10(np.maximum(np.abs(s), 1e-300))


def channel_metrics(p: Parts):
    channels = load_channels()
    rxf = np.array([float(c['rf_hz']) for c in channels])
    imf = np.array([float(c['immagine_hz']) for c in channels])
    rxs,rxr = two_port(rxf,p)
    ims,_ = two_port(imf,p)
    il_rx, il_img, rl_rx = attenuation_db(rxs), attenuation_db(ims), attenuation_db(rxr)
    return channels, il_rx, il_img, rl_rx


def summary(p: Parts):
    channels,il_rx,il_img,rl = channel_metrics(p)
    return {
        'num_channels':len(channels),
        'rx_insertion_loss_db_min':float(il_rx.min()),
        'rx_insertion_loss_db_max':float(il_rx.max()),
        'image_attenuation_db_min':float(il_img.min()),
        'image_attenuation_db_max':float(il_img.max()),
        'image_rejection_relative_db_min':float(np.min(il_img - il_rx)),
        'rx_return_loss_db_min':float(rl.min()),
        'model':asdict(p),
    }


def tolerance_study(n=4000, seed=6606):
    """Stress test only; distributions illustrative, not part tolerances certified."""
    rng=np.random.default_rng(seed)
    rxf=np.array([float(c['rf_hz']) for c in load_channels()])
    imf=rxf+2*10.695e6
    results=np.empty((n,5))
    for i in range(n):
        p=Parts(
            l1_h=2e-6*rng.uniform(.95,1.05),
            l2_h=22e-9*rng.uniform(.95,1.05),
            l3_h=2e-6*rng.uniform(.95,1.05),
            c1_f=17.5e-12*rng.uniform(.98,1.02),
            c2_f=1591e-12*rng.uniform(.98,1.02),
            c3_f=17.5e-12*rng.uniform(.98,1.02),
            q_l1=rng.uniform(30,110),
            q_l2=rng.uniform(30,110),
            q_l3=rng.uniform(30,110),
            q_c=rng.uniform(300,700),
            srf_l1_hz=rng.uniform(55e6,150e6),
            srf_l2_hz=rng.uniform(250e6,750e6),
            srf_l3_hz=rng.uniform(55e6,150e6),
            c_feed_f=rng.uniform(0,0.5e-12),
        )
        sr,rr=two_port(rxf,p)
        si,_=two_port(imf,p)
        ilr=attenuation_db(sr); ili=attenuation_db(si); rl=attenuation_db(rr)
        results[i]=[ilr.max(),ili.min(),(ili-ilr).min(),rl.min(),ilr.min()]
    names=['max_rx_loss_db','min_image_atten_db','min_relative_image_rejection_db','min_rx_return_loss_db','min_rx_loss_db']
    quant={name:{str(q):float(np.quantile(results[:,k],q)) for q in (0,0.01,0.05,0.5,0.95,0.99,1)} for k,name in enumerate(names)}
    return {
        'n':n,'seed':seed,
        'distributions':{'L':'independent uniform ±5%','C':'independent uniform ±2%',
            'inductor_Q':'independent uniform [30,110] at f0','capacitor_Q':'uniform [300,700]',
            'SRF_series':'uniform [55,150] MHz','SRF_shunt':'uniform [250,750] MHz',
            'input_output_feedthrough':'uniform [0,0.5] pF'},
        'quantiles':quant,
        'fraction_rx_loss_above_6dB':float(np.mean(results[:,0]>6)),
        'fraction_relative_image_rejection_below_40dB':float(np.mean(results[:,2]<40)),
        'fraction_rx_return_loss_below_10dB':float(np.mean(results[:,3]<10)),
        'warning':'Monte Carlo illustrativo di elementi parassiti; nessuna distribuzione qualificata per MPN, nessun PCB, nessun SPICE vendor.'}


def emit_plots(f_mhz, data, path):
    # SVG in stile tecnico senza immagini di terzi.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(11,5.4),layout='constrained')
    for label,y in data.items():
        ax.plot(f_mhz,y,label=label,linewidth=1.75)
    ax.set(xlabel='Frequenza [MHz]',ylabel='Perdita inserzione simulata [dB]',
           title='F501 - risposta 50 ohm: rete LC a Q finito e bypass parassita')
    ax.axvspan(25.615,28.305,alpha=.07,color='tab:green',label='270 RX')
    ax.axvspan(47.005,49.695,alpha=.07,color='tab:red',label='immagine RX')
    ax.set_ylim(-1,100)
    ax.grid(alpha=.22)
    ax.legend(loc='upper left',fontsize=8)
    fig.savefig(path,format='svg')
    plt.close(fig)


def generate():
    HERE.mkdir(parents=True,exist_ok=True)
    channels=load_channels()
    p=Parts()
    _,nom_rx,nom_img,nom_rl=channel_metrics(p)
    alt_rx,alt_img,alt_rl=channel_metrics(replace(p,c_feed_f=0.5e-12))[1:]
    with (HERE/'RISPOSTA_270_CANALI_LC_V6.6.csv').open('w',newline='',encoding='utf-8') as fout:
        writer=csv.writer(fout)
        writer.writerow(['banda','canale','alfa','rf_mhz','immagine_mhz','lc_q60_0p05pf_il_rx_db',
                          'lc_q60_0p05pf_il_image_db','lc_q60_0p05pf_rej_rel_db','lc_q60_0p05pf_return_loss_rx_db',
                          'lc_q60_0p50pf_il_rx_db','lc_q60_0p50pf_il_image_db','tx_enabled'])
        for i,ch in enumerate(channels):
            writer.writerow([ch['banda'],ch['canale'],ch['alfa'],f"{int(ch['rf_hz'])/1e6:.6f}",
                f"{int(ch['immagine_hz'])/1e6:.6f}",f'{nom_rx[i]:.5f}',f'{nom_img[i]:.5f}',
                f'{nom_img[i]-nom_rx[i]:.5f}',f'{nom_rl[i]:.5f}',f'{alt_rx[i]:.5f}',f'{alt_img[i]:.5f}',False])
    cvec=[0,0.02,0.05,0.1,0.2,0.5,1.0]
    feeds=[]
    for pf in cvec:
        m=summary(replace(p,c_feed_f=pf*1e-12))
        feeds.append({'c_feed_pf':pf,'max_rx_loss_db':m['rx_insertion_loss_db_max'],
                    'min_img_atten_db':m['image_attenuation_db_min'],
                    'min_relative_image_rejection_db':m['image_rejection_relative_db_min']})
    stress=tolerance_study()
    result={
       'revision':'V6.6','timestamp_assumption':'2026-11-09',
       'technology':'linear passive Y-matrix -> S-parameters at 50 ohm',
       'nominal':summary(p),
       'feedthrough_sweep':feeds,
       'monte_carlo':stress,
       'external_datasheet_candidate':{'manufacturer':'Mini-Circuits','mpn':'SXBP-27R5+',
            'passband_mhz':[24,31],'insertion_loss_typical_db':1.3,
            'insertion_loss_max_db_25C':2.5,'image_stopband_mhz':[39,900],
            'image_attenuation_min_db_25C':20,'qualified_by_vendor_only_not_board':True,
            'ground_pad_numbers':[2,3,4,5,6,7], 'input_pad':1,'output_pad':8},
       'remaining_gates':['Q/SRF vendor MPN for each inductor',
            'network PCB parasitic C_IN_OUT EM/bench extraction',
            'VNA 2-port S21/S11 270 positions and image',
            'noise figure/selectivity dynamic range system budget',
            'mixer drive and IF filters', 'native KiCad ERC/DRC not executed',
            'NO TX NO FAB']}
    (HERE/'RISULTATI_ANALISI_LC_V6.6.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    fs=np.linspace(20,70,901)
    curve={f"Q=60, Cpar={pf} pF":attenuation_db(two_port(fs*1e6,replace(p,c_feed_f=pf*1e-12))[0]) for pf in (0.0,0.05,0.5)}
    emit_plots(fs,curve,HERE/'CURVE_S21_LC_V6.6.svg')
    print(json.dumps({'nominal':{k:v for k,v in result['nominal'].items() if k!='model'},
          'worst_feedthrough':feeds[-1],
          'monte_carlo_median':{k:v['0.5'] for k,v in stress['quantiles'].items()},
          'monte_carlo_fractions':{k:v for k,v in stress.items() if k.startswith('fraction_')}},indent=2))
    return result

if __name__=='__main__':
    generate()
