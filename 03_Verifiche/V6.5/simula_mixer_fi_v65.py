#!/usr/bin/env python3
"""V6.5: modello ANALITICO idealizzato del preselettore e conversione RX.

Non e' SPICE / s-parameters / rete LC fisica / modello ADE-1+ vendor.
Nessuna abilitazione TX. Legge le 270 frequenze ESATTE del piano V6.4.
"""
from __future__ import annotations
import csv
import json
import math
import random
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
IF_HZ = 10_695_000
F_LOW_HZ = 25_000_000
F_HIGH_HZ = 29_000_000
POLES = 3
MIXER_TYP_LOSS_DB = 5.0  # da datasheet ADE-1+ tipico, non garanzia applicativa
LO_TARGET_DBM = 7.0
SYSTEM_Z_OHM = 50.0


def read_pll_rows(path=None):
    path = Path(path) if path else ROOT / '02_Piano_Frequenze/V6.4/PIANO_PLL_LO_270_RX_V6.4.csv'
    with path.open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 270:
        raise ValueError('Piano precedente non contiene esattamente 270 RX')
    keys = set()
    for r in rows:
        band,channel=r['banda'],r['canale']
        if (band,channel) in keys:
            raise ValueError('Collisione banda/canale')
        keys.add((band,channel))
        rf,lo,im,fi = (int(r[x]) for x in ('rf_hz','lo_hz','if_image_hz','fi1_hz'))
        if rf <= 0 or lo != rf + IF_HZ or im != rf + 2*IF_HZ or fi != IF_HZ:
            raise ValueError('FI/LO/immagine V6.4 incoerenti')
        if int(r['tx_permitted_v64']) != 0:
            raise ValueError('RX plan non deve autorizzare TX')
    return rows


def butterworth_bpf_db(f_hz, low_hz=F_LOW_HZ, high_hz=F_HIGH_HZ, order=POLES):
    """Risposta ANALITICA di un Butterworth BPF idealizzato via trasf. LP→BP.

    Il filtro analogico corrispondente ha ordine 2N (N=3 -> sei poli fisici).
    Non e' una sintesi di valori L/C o di perdite / Q / s-parameters.
    """
    if not (0 < low_hz < high_hz and isinstance(order,int) and order > 0):
        raise ValueError('Intervallo BPF non valido')
    a = np.asarray(f_hz, dtype=float)
    if not np.all(np.isfinite(a)) or np.any(a <= 0):
        raise ValueError('Frequenze f_hz devono essere positive finite')
    center_squared = low_hz*high_hz
    norm = (a*a-center_squared)/((high_hz-low_hz)*a)
    # via logaddexp per comportamento numerico stabile ad attenuazioni elevate
    x=np.log(np.maximum(np.abs(norm),np.finfo(float).tiny))*order
    y= -10/np.log(10)*np.logaddexp(0,2*x)
    return float(y) if np.ndim(y)==0 else y


def simulate_mixing_ideal(rf_hz=27_005_000, image_hz=None, fs_hz=200_000_000, n=40000):
    """FFT di due coseni REALI moltiplicati (non mixer ADE-1+), fonti separate.
    Esempi coerenti con bin di 5 kHz; controlla entrambi a 10.695 MHz.
    """
    image_hz=rf_hz+2*IF_HZ if image_hz is None else image_hz
    lo=rf_hz+IF_HZ
    if fs_hz <= 2*(image_hz+lo):
        raise ValueError('Campionamento insufficiente per il tono di somma')
    t=np.arange(n,dtype=float)/fs_hz
    lo_wave=2*np.cos(2*np.pi*lo*t)
    freq=np.fft.rfftfreq(n,1/fs_hz)
    results={}
    for name,sig in [('rx_desiderato',rf_hz),('immagine',image_hz)]:
        mixed=np.cos(2*np.pi*sig*t)*lo_wave
        ft=np.abs(np.fft.rfft(mixed))*(2/n)
        near=(freq>IF_HZ-30_000)&(freq<IF_HZ+30_000)
        index=np.argmax(ft[near]);actual=np.flatnonzero(near)[index]
        results[name]={'rf_input_hz':sig,'peak_if_hz':float(freq[actual]),'peak_amplitude_relative':round(float(ft[actual]),6)}
    results['note']='Moltiplicazione sinusoidi e FFT: nessuna non-linearita/impedenza del componente ADE-1+ simulata.'
    return results


def monte_carlo_bpf(rows,n=12000,seed=6505):
    """Scenari di scostamento filtro ideale: f_c ±0.5%, bandwidth ±5%.
    Questo NON modella tolleranze individuali di L/C o Q fisici.
    """
    if n<1: raise ValueError('n non valido')
    rng=random.Random(seed)
    rf=np.array([int(r['rf_hz']) for r in rows],dtype=float)
    im=np.array([int(r['if_image_hz']) for r in rows],dtype=float)
    centers=[];rejects=[];passworst=[]
    mid= (F_LOW_HZ+F_HIGH_HZ)/2
    width=F_HIGH_HZ-F_LOW_HZ
    for _ in range(n):
        shift=rng.uniform(-0.005,0.005)
        spread=rng.uniform(-0.05,0.05)
        c=mid*(1+shift); w=width*(1+spread)
        fl=c-w/2;fh=c+w/2
        rx_gain=butterworth_bpf_db(rf,fl,fh)
        image_gain=butterworth_bpf_db(im,fl,fh)
        passworst.append(float(np.min(rx_gain)))
        rejects.append(float(-np.max(image_gain)))
        centers.append(c)
    rejects.sort();passworst.sort()
    return {'samples':n,'seed':seed,'scenario_center_error_fraction':[-0.005,0.005],
        'scenario_width_error_fraction':[-0.05,0.05],
        'min_image_rejection_db_sample':round(rejects[0],4),
        'p05_image_rejection_db_sample':round(rejects[int((n-1)*.05)],4),
        'worst_passband_gain_db_sample':round(passworst[0],4),
        'warning':'Solo spostamento globale f_c e BW del trasferimento ideale. Non include ESR/Q, accoppiamenti, mismatch, layout o effetti termici reali.'}


def calculate():
    rows=read_pll_rows()
    out=[]
    for r in rows:
        rf=int(r['rf_hz']);lo=int(r['lo_hz']);im=int(r['if_image_hz'])
        gain=float(butterworth_bpf_db(rf))
        image_gain=float(butterworth_bpf_db(im))
        out.append({'banda':r['banda'],'canale':r['canale'],'alfa':int(r['alfa']),
            'rf_hz':rf,'lo_hz':lo,'fi1_hz':IF_HZ,'immagine_hz':im,
            'preselettore_db_ideale_rx':round(gain,5),
            'preselettore_db_ideale_immagine':round(image_gain,5),
            'reiezione_ideale_relativa_db':round(gain-image_gain,5),'tx_enabled':False})
    # in banda un'immagine con identica ampiezza all'RX e' convertita nella stessa FI
    ifband={'CW':500,'USB':2700,'LSB':2700,'AM':6000,'FM':12000}
    demands=[{'modalita':mode,'bw_3db_hz_ipotizzata':bw,
        'q_caricato_ideale_approssimato':round(IF_HZ/bw,1),
        'nota':'Non implica filtro acquistabile o rispondenza alle adiacenti'} for mode,bw in ifband.items()]
    power_w=10**(LO_TARGET_DBM/10)*1e-3
    lo={'target_dbm':LO_TARGET_DBM,'power_mw':round(power_w*1000,5),
        'z_ohm_assumed':SYSTEM_Z_OHM,'vrms':round(math.sqrt(power_w*SYSTEM_Z_OHM),6),
        'vpp_sinusoid':round(2*math.sqrt(2*power_w*SYSTEM_Z_OHM),6),
        'requires_output_stage_measurement':True}
    sim={'revisione':'V6.5','metodo':'Butterworth BPF ideale n=3 (ordine analogico 6); FFT prodotto coseni; Monte Carlo su centro e larghezza',
      'channels':len(out),'alpha':sum(r['alfa'] for r in out),
      'rf_min_hz':min(r['rf_hz'] for r in out),'rf_max_hz':max(r['rf_hz'] for r in out),
      'lo_min_hz':min(r['lo_hz'] for r in out),'lo_max_hz':max(r['lo_hz'] for r in out),
      'image_min_hz':min(r['immagine_hz'] for r in out),'image_max_hz':max(r['immagine_hz'] for r in out),
      'image_separation_hz':2*IF_HZ,
      'bpf_3db_low_hz':F_LOW_HZ,'bpf_3db_high_hz':F_HIGH_HZ,
      'bpf_lowpass_prototype_order':POLES,'bpf_analog_pole_order':2*POLES,
      'min_desired_gain_db_ideal':round(min(r['preselettore_db_ideale_rx'] for r in out),5),
      'max_image_gain_db_ideal':round(max(r['preselettore_db_ideale_immagine'] for r in out),5),
      'min_relative_image_rejection_db_ideal':round(min(r['reiezione_ideale_relativa_db'] for r in out),5),
      'image_rejection_db_for_0dbm_blocker_and_minus110dbm_spurious_target':110.,
      'lo_drive':lo,'mixer_ade1_typical_conversion_loss_db_datasheet':MIXER_TYP_LOSS_DB,
      'filter_modes_theoretical_requirements':demands,
      'lo_and_rf_mixing_fft':simulate_mixing_ideal(),
      'monte_carlo':monte_carlo_bpf(rows),
      'native_kicad_erc_drc':'NOT_RUN_KICAD_MISSING',
      'spice':'NOT_RUN_SPICE_MODEL_MISSING',
      'actual_filter_component_network':'NOT_SYNTHESIZED',
      'physical_filter_characterization':'NOT_MEASURED',
      'conversion_loss_actual':'NOT_MEASURED',
      'rf_transmit_enabled':False,'production_approved':False}
    out_dir=ROOT/'03_Verifiche/V6.5'
    freq_dir=ROOT/'02_Piano_Frequenze/V6.5'
    out_dir.mkdir(parents=True,exist_ok=True);freq_dir.mkdir(parents=True,exist_ok=True)
    (out_dir/'RISULTATI_SIMULAZIONI_MIXER_V6.5.json').write_text(json.dumps(sim,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with (freq_dir/'MAPPATURA_270_MIXER_IMMAGINE_V6.5.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    with (out_dir/'FILTRO_FI_MODALITA_V6.5.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(demands[0]));w.writeheader();w.writerows(demands)
    freqs=np.linspace(18e6,55e6,1301)
    with (out_dir/'RISPOSTA_BPF_IDEALE_V6.5.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['freq_hz','gain_db_ideal_no_parasitics'])
        w.writerows((int(freq),round(float(gain),5)) for freq,gain in zip(freqs,butterworth_bpf_db(freqs)))
    return sim,out


def graphic(sim):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fr=np.linspace(20e6,55e6,2201)
    fig,ax=plt.subplots(figsize=(11,5.2))
    ax.plot(fr/1e6,butterworth_bpf_db(fr),linewidth=2,label='Preselettore BPF ideale 3° Butterworth')
    ax.axvspan(sim['rf_min_hz']/1e6,sim['rf_max_hz']/1e6,alpha=.12,label='270 frequenze RX')
    ax.axvspan(sim['image_min_hz']/1e6,sim['image_max_hz']/1e6,alpha=.12,label='Banda immagine')
    ax.axhline(-3,linestyle=':',linewidth=1)
    ax.set(xlabel='Frequenza (MHz)',ylabel='Trasferimento ideale (dB)',title='V6.5 — Selettività teorica, NON filtro fisico / NO FAB',ylim=(-105,3),xlim=(20,55))
    ax.grid(True,alpha=.25);ax.legend(loc='upper right',fontsize=9)
    fig.tight_layout()
    path=ROOT/'03_Verifiche/V6.5/RISPOSTA_PRESELETTORE_V6.5.svg';fig.savefig(path,format='svg');plt.close(fig)
    return path


if __name__=='__main__':
    sim,_=calculate();graphic(sim)
    print(json.dumps({k:sim[k] for k in ['channels','min_desired_gain_db_ideal','max_image_gain_db_ideal','min_relative_image_rejection_db_ideal','lo_drive','monte_carlo']},indent=2,ensure_ascii=False))
