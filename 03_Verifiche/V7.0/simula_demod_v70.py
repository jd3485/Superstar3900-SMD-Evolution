#!/usr/bin/env python3
"""Numerical circuit equivalent + DSP simulations for V7.0; no manufacturer transistor model, no native KiCad/SPICE."""
import csv,json,math,sys
from pathlib import Path
import numpy as np
from scipy import signal
ROOT=Path(__file__).resolve().parents[2]; SUB=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'08_Firmware_Prototipi/V7.0'))
import dsp_rx_v70 as DSP
Z0=50.0
F0=10.24e6
L=(330e-9,1.1e-6,330e-9)
C=(360e-12,360e-12)
def network(f,li=L,ci=C,q=80.0):
    """ABCD network with inductor series ESR at 10.24MHz Q; two 50ohm ports."""
    a,b,c,d=1+0j,0j,0j,1+0j
    for stage,part in [('series',li[0]),('shunt',ci[0]),('series',li[1]),('shunt',ci[1]),('series',li[2])]:
        w=2*np.pi*f
        if stage=='series':
            z=1j*w*part + (2*np.pi*F0*part/q)
            A,B,Cc,D=1,z,0,1
        else:
            y=1j*w*part
            A,B,Cc,D=1,0,y,1
        a,b,c,d=a*A+b*Cc,a*B+b*D,c*A+d*Cc,c*B+d*D
    den=a+b/Z0+c*Z0+d
    s21=2/den
    s11=(a+b/Z0-c*Z0-d)/den
    return s21,s11
def db(x):return 20*math.log10(max(1e-18,abs(x)))
def fm_lin(t,dev=2000.0,audio=1000.0,kvo=100000.,rc=100e-6,vcc=3.3):
    """Small-signal linearized XOR phase detector + 1-pole loop RC + VCO (not 4046 silicon)."""
    kd=vcc/math.pi; kv_rad=2*math.pi*kvo
    num=[2*math.pi*kd]
    den=[rc,1.,kd*kv_rad]
    u=dev*np.sin(2*np.pi*audio*t)
    _,v,_=signal.lsim((num,den),U=u,T=t)
    return v

def spectral_metrics(x,fs,tone,discard=0.04):
    n=int(discard*fs);x=np.asarray(x)[n:];x=x-np.mean(x);N=len(x)
    freqs=np.fft.rfftfreq(N,1/fs);a=np.abs(np.fft.rfft(x*np.hanning(N)))
    k=int(np.argmin(np.abs(freqs-tone)))
    main=np.max(a[max(0,k-1):k+2]);harm=[]
    for mult in (2,3,4,5):
        j=int(np.argmin(np.abs(freqs-tone*mult)))
        harm.append(np.max(a[max(0,j-1):j+2]))
    return {'peak_hz':float(freqs[k]),'thd_ratio':float(np.linalg.norm(harm)/max(main,1e-12))}

def simulate(write_files=True):
    fs=DSP.FS; t=np.arange(0,0.2,1/fs)
    # AD8307 ideal logarithmic envelope 455k average, 25mV/dB; intentionally exposed nonlinearity
    envelope=1+0.35*np.sin(2*np.pi*1000*t)
    logv=1.4+20*0.025*np.log10(envelope)
    b,a=signal.butter(1,15915,fs=fs)
    logv_filtered=signal.lfilter(b,a,logv)
    raw=logv_filtered-1.4
    corrected=DSP.log_am_linearize(logv_filtered,1.4)-1
    mraw=spectral_metrics(raw,fs,1000)
    mcorr=spectral_metrics(corrected,fs,1000)
    fm=fm_lin(t)
    mfm=spectral_metrics(fm,fs,1000)
    fgrid=np.linspace(1e6,65e6,900)
    s21=np.asarray([network(x)[0] for x in fgrid]);s11=np.asarray([network(x)[1] for x in fgrid])
    lpf_fund=db(network(10.24e6)[0]);third=db(network(30.72e6)[0]);fifth=db(network(51.2e6)[0])
    reflection=db(network(10.24e6)[1])
    rng=np.random.default_rng(7011)
    monte=[]
    for i in range(4000):
        ls=tuple(x*rng.uniform(.95,1.05) for x in L)
        cs=tuple(x*rng.uniform(.98,1.02) for x in C)
        q=rng.uniform(45,120)
        monte.append((db(network(F0,ls,cs,q)[0]),db(network(3*F0,ls,cs,q)[0])))
    monte=np.asarray(monte)
    # 5V bias worstcase with temperature dependent device voltage assumption (NOT manufacturer-grade SPICE)
    bias=[]
    for i in range(5000):
        supply=rng.uniform(4.75,5.25);res=47*rng.uniform(.99,1.01)
        vdev=3.3+rng.uniform(-.15,.15)
        # 5mV/mA small signal slope approximate, series R adds 5ohm feedback
        current=max(0.,(supply-vdev)/(res+5))
        bias.append((current, current**2*res))
    bias=np.asarray(bias)
    # DSP responses and Q15 error
    dsp={}
    for mode in DSP.SPEC:
        taps=DSP.design(mode);q15=DSP.q15(mode).astype(float)/32768
        freqs,H=signal.freqz(q15,worN=32768,fs=fs)
        def gain(f):return db(H[np.argmin(np.abs(freqs-f))])
        dsp[mode]={'taps':len(taps),'group_delay_ms':(len(taps)-1)/(2*fs)*1000,
             'mmac_per_second':len(taps)*fs/1e6,
             'pass_gain_db':{str(x):gain(x) for x in ([600,1000,2000,2500] if mode=='SSB' else [550,700,850])},
             'stop_gain_db':{str(x):gain(x) for x in ([5500,8500] if mode=='SSB' else [1800,3300])},
             'max_coeff_error':float(np.max(np.abs(q15-taps))),'q15_energy':float(np.sum(q15*q15))}
    # LO power budget (ideal square at unloaded port, differential gain + frequency specs NOT guaranteed)
    vrms_fund=(2*3.3/math.pi)/math.sqrt(2)*50/(1500+50)
    pin_dbm=10*math.log10((vrms_fund**2/50)/.001)
    theoretical_gain_db=22.4 # manufacturer only specifies at 100 MHz, NOT 10.24
    budget_dbm=pin_dbm+theoretical_gain_db+lpf_fund-2.0
    # 50ohm power target +7 dBm : Vrms
    vtarget_rms=math.sqrt(50*.001*10**(.7))
    result={'version':'V7.0','simulation_kind':'scipy/numpy ideal behavioral equations; no native SPICE silicon model',
      'am_log_ideal':{'raw_thd_percent':100*mraw['thd_ratio'],'linearized_thd_percent':100*mcorr['thd_ratio'],'tone_hz':1000,'slope_v_per_db':.025},
      'fm_pll_linearized':{'tone_hz':1000,'deviation_peak_hz':2000,'kvo_assumed_hz_per_v':100000,'rc_sec':100e-6,
      'gain_peak_v':float((np.percentile(fm[5000:],99.5)-np.percentile(fm[5000:],.5))/2),
      'thd_percent':100*mfm['thd_ratio'],'model_only':True},
      'lo2_lpf_50ohm':{'fundamental_s21_db':lpf_fund,'3rd_harmonic_s21_db':third,'5th_harmonic_s21_db':fifth,
      's11_db_10p24mhz':reflection,'nominal_inductors_h':L,'nominal_capacitors_f':C,'assumed_q':80,
      'monte_carlo_4000':{'fund_db_range':[float(np.min(monte[:,0])),float(np.max(monte[:,0]))],
        'third_db_range':[float(np.min(monte[:,1])),float(np.max(monte[:,1]))],
        'third_above_minus_25db_count':int(np.sum(monte[:,1]>-25))}},
      'lo2_rf_driver':{'si5351_square_assumed_vpp':3.3,'output_series_ohm':1500,'theoretical_fund_pin_dbm':pin_dbm,
        'gali3_gain_db_only_at_100mhz':theoretical_gain_db,'predicted_out_dbm_using_100mhz_gain_NOT_VALIDATED':budget_dbm,
        'required_mixer_out_dbm':7,'output_50ohm_vrms_at_7dbm':vtarget_rms,
        'bias_5v_5000':{'current_range_ma':[float(np.min(bias[:,0])*1000),float(np.max(bias[:,0])*1000)],
          'r47_dissipation_mw_range':[float(np.min(bias[:,1])*1000),float(np.max(bias[:,1])*1000)]}},
      'dsp_48k':dsp,'rf_tx_enabled':False,'kicad_erc_drc_done':False,'ngspice_manufacturer_models_done':False,
      'unknowns':['FM PLL actual oscillator R1/C1 center','FM capture/THD on silicon','AM log calibration','GALI-3 gain at 10.24MHz','bias choke SRF/inductor Q','455k filter availability/matching','SSB hardware preselector blocking','codec/MCU real time benchmarks']}
    if write_files:
        (SUB/'RISULTATI_SIMULAZIONI_V7.0.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf8')
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        plt.figure(figsize=(9,5));plt.plot(fgrid/1e6,20*np.log10(np.maximum(1e-15,np.abs(s21))))
        plt.axvline(10.24,linestyle='--',color='gray');plt.axvline(30.72,linestyle='--',color='gray')
        plt.xlabel('Frequenza (MHz)');plt.ylabel('S21 (dB)');plt.title('V7.0 LO2 — rete LC 5 poli, modello 50 Ω / Q=80');plt.grid();plt.ylim(-85,5);plt.tight_layout();plt.savefig(SUB/'CURVA_LPF_LO2_V7.0.svg');plt.close()
        plt.figure(figsize=(9,4));plt.plot(t[:1200]*1000,logv_filtered[:1200]-1.4,label='AD8307 uscita log (centrata)')
        plt.plot(t[:1200]*1000,corrected[:1200]*0.15,label='ricostruzione exp scalata')
        plt.xlabel('Tempo (ms)');plt.ylabel('Ampiezza relativa (V)');plt.title('V7.0 — AM ideale: legge log + conversione inversa');plt.legend();plt.grid();plt.tight_layout();plt.savefig(SUB/'CURVA_AM_DEMOD_V7.0.svg');plt.close()
        plt.figure(figsize=(9,4));plt.plot(t[4800:6000]*1000,fm[4800:6000]*1000)
        plt.xlabel('Tempo (ms)');plt.ylabel('VCOIN demod FM (mV AC)');plt.title('V7.0 — PLL FM modello linearizzato, dev ±2 kHz');plt.grid();plt.tight_layout();plt.savefig(SUB/'CURVA_FM_PLL_V7.0.svg');plt.close()
        plt.figure(figsize=(9,4))
        for mode in DSP.SPEC:
            ff,hh=signal.freqz(DSP.q15(mode).astype(float)/32768,worN=16384,fs=fs)
            plt.plot(ff,20*np.log10(np.maximum(abs(hh),1e-7)),label=mode)
        plt.xlim(0,8000);plt.ylim(-100,6);plt.grid();plt.xlabel('Audio (Hz)');plt.ylabel('Modulo FIR Q15 (dB)');plt.title('V7.0 — SSB / CW selettività DSP 48 kHz');plt.legend();plt.tight_layout();plt.savefig(SUB/'RISPOSTE_DSP_SSB_CW_V7.0.svg');plt.close()
        for mode in DSP.SPEC:
            qd=DSP.q15(mode)
            with (ROOT/'08_Firmware_Prototipi/V7.0'/f'COEFF_{mode}_Q15_V7.0.csv').open('w',newline='',encoding='utf8') as f:
                w=csv.writer(f);w.writerow(['index','q15']);w.writerows(enumerate(qd.tolist()))
        arr={mode:DSP.q15(mode).tolist() for mode in DSP.SPEC}
        txt = "/* V7.0: 48kHz Q15 audio FIR; no STM32 HAL. */\n#ifndef SUPERSTAR3900_DSP_FIR_V70_H\n#define SUPERSTAR3900_DSP_FIR_V70_H\n#include <stdint.h>\n"
        for mode in DSP.SPEC:
            values=arr[mode]
            txt+=f"\n#define V70_{mode}_TAPS {len(values)}\nstatic const int16_t v70_{mode.lower()}_q15[{len(values)}] = {{\n"
            for i in range(0,len(values),16):
                txt+='  '+', '.join(map(str,values[i:i+16]))+',\n'
            txt+='};\n'
        txt+='\n#endif\n'
        (ROOT/'08_Firmware_Prototipi/V7.0/FIR_SSB_CW_Q15_V7.0.h').write_text(txt,encoding='utf8')
    return result
if __name__=='__main__':
    result=simulate()
    print(json.dumps({key:result[key] for key in ('am_log_ideal','fm_pll_linearized','lo2_lpf_50ohm','lo2_rf_driver','dsp_48k')},indent=2))
