#!/usr/bin/env python3
"""Numerical IF2 AM/SSB/CW/FM illustrations (not SPICE or PCB measurement)."""
from __future__ import annotations
from pathlib import Path
import json,math,csv
import numpy as np
from scipy import signal

HERE=Path(__file__).resolve().parent
FS=3_640_000                 # exactly 8 samples per nominal 455 kHz period
DURATION=.040
T=np.arange(round(FS*DURATION),dtype=float)/FS
SAMPLE_SLICE=slice(int(.010*FS),None)


def lowpass(a, fc=4000):
    return signal.sosfilt(signal.butter(5,fc,fs=FS,output='sos'),a)

def peak(y):
    a=np.asarray(y[SAMPLE_SLICE]); a=a-np.mean(a)
    w=np.hanning(len(a));ft=np.fft.rfft(a*w)
    fr=np.fft.rfftfreq(len(a),1/FS)
    sub=(fr>100)&(fr<4000)
    return {'peak_hz':float(fr[sub][np.argmax(np.abs(ft[sub]))]),'rms':float(np.sqrt(np.mean(a*a)))}

def ssc(mode):
    bfo={'USB':456_500,'LSB':453_500,'CW':455_700}[mode]
    carrier={'USB':455_500,'LSB':454_500,'CW':455_000}[mode]
    x=np.cos(2*np.pi*carrier*T)
    # An ideal balanced square-wave commutator; *not* actual bias-switch or hardware response.
    gate=np.where(np.cos(2*np.pi*bfo*T)>=0,1.,-1.)
    y=lowpass(x*gate)
    return peak(y)

def am():
    x=(1+.5*np.cos(2*np.pi*1000*T))*np.cos(2*np.pi*455_000*T)
    env=np.maximum(0.,x) # ideal rectification, no Schottky knee/drop/noise
    return peak(lowpass(env))

def fm():
    # FM instantaneous phase; ideal two-sample (quarter carrier period) delay for 455kHz.
    phi=2*np.pi*455_000*T+2.5*np.sin(2*np.pi*1000*T)
    x=np.cos(phi)
    q=np.zeros_like(x);q[2:]=x[:-2]*x[2:]
    # This ideal phase discriminator is deliberately not a realizable B992 circuit.
    return peak(lowpass(q))

def ref_error_rf_hz(rf_hz,ppm=2.5):
    # Common 12.8 MHz reference shifts PLL1, LO2 and BFO together:
    # effective SSB difference tracks RF channel to first order, not cancellation.
    return rf_hz*ppm*1e-6


def produce():
    # Exploratory analog-output filtering: abstract 5th-order LP at 14.2 MHz.
    # No physical lumped-element network or driver isolation model.
    rng=np.random.default_rng(6901)
    fc=14_200_000
    harmonic_hz=3*10_240_000
    def lp_loss_db(f,cutoff,order=5):return -10*np.log10(1+(f/cutoff)**(2*order))
    fc_samples=fc*(1+rng.uniform(-.07,.07,size=4000))
    loss3=lp_loss_db(harmonic_hz,fc_samples)
    # 5,000 exploratory FM phase errors ±5% of quarter-cycle, not component limits.
    phase_errors=rng.uniform(-.05,.05,size=5000)*np.pi/2
    fm_gain=np.cos(phase_errors)
    result={'fs_hz':FS,'duration_s':DURATION,'model_class':'NUMERICAL_IDEAL_ONLY',
        'demod':{'USB':ssc('USB'),'LSB':ssc('LSB'),'CW':ssc('CW'),'AM':am(),'FM':fm()},
        'exploratory_lo2_lpf':{'type':'IDEAL_BUTTERWORTH_5TH_ORDER_ONLY', 'corner_hz':fc,'harmonic_hz':harmonic_hz,
          'nominal_at_3rd_harmonic_db':float(lp_loss_db(harmonic_hz,fc)),
          'corner_variations':4000,'3rd_harmonic_db_range':[float(loss3.min()),float(loss3.max())]},
        'exploratory_fm_quadrature':{'phase_error_cases':5000,'quarter_cycle_tolerance_hypothetical':0.05,
          'relative_gain_range':[float(fm_gain.min()),float(fm_gain.max())]},
        'clock_error':{'reference_ppm_range':[-2.5,2.5],
          'rf_low_hz':25_615_000,'rf_high_hz':28_305_000,
          'residual_low_hz':ref_error_rf_hz(25_615_000),
          'residual_high_hz':ref_error_rf_hz(28_305_000),
          'note':'First-order common-reference correlation; SSB net RF frequency still drifts.'},
        'limitations':['IF2 filter shapes and phase are IDEAL', 'FM discriminator uses ideal sampling delay',
          'AM diode modeled ideal', 'SSB commutator inputs generated mathematically not by B981',
          'No Si5351C register programming, jitter, phase noise, spur or clock output measurement',
          'No RF transmission tested or connected']}
    (HERE/'RISULTATI_SIMULAZIONI_V6.9.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf8')
    # Compact curve output: downsample after lowpass to 100 kSa/s, drawing audio sample only.
    dec=91;sample_count=400
    arr=np.cos(2*np.pi*455_500*T)*np.where(np.cos(2*np.pi*456_500*T)>=0,1.,-1.)
    y=lowpass(arr)
    with (HERE/'CAMPIONI_USB_DEMOD_V6.9.csv').open('w',newline='',encoding='utf8') as f:
      w=csv.writer(f);w.writerow(['t_s','demod_ideal_v_normalized'])
      i0=int(.012*FS)
      for k in range(sample_count):
          i=i0+k*dec
          w.writerow([f'{T[i]:.8f}',f'{y[i]:.9f}'])
    # SVG curve with readable axes, no external image dependency
    vals=y[i0:i0+sample_count*dec:dec];
    points=[]
    for i,v in enumerate(vals):
        xx=80+i*1000/(len(vals)-1); yy=180-v*130
        points.append(f'{xx:.1f},{yy:.1f}')
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 330" width="1200" height="330">
    <rect width="1200" height="330" fill="#111827"/><text x="55" y="37" font-size="23" fill="white" font-family="Arial">V6.9 • USB 1 kHz — demodulazione sincrona NUMERICA IDEALE</text>
    <line x1="70" y1="180" x2="1100" y2="180" stroke="#64748b"/><line x1="80" y1="60" x2="80" y2="282" stroke="#64748b"/>
    <polyline fill="none" stroke="#38bdf8" stroke-width="2.3" points="{' '.join(points)}" />
    <text x="70" y="306" font-size="15" fill="#d1d5db" font-family="Arial">t = 12 ms → ~22 ms; ampiezza normalizzata. Non è una misura su Si5351/TS5A3157.</text></svg>'''
    (HERE/'CURVA_USB_1KHZ_V6.9.svg').write_text(svg,encoding='utf8')
    return result

if __name__=='__main__':
  res=produce()
  print(json.dumps({'demod':res['demod'],'clock_error':res['clock_error']},indent=2))
