#!/usr/bin/env python3
"""Reproducible analytical/numerical IF1/IF2/VGA study, NOT device-accurate SPICE."""
from pathlib import Path
import csv,json,math,random,statistics
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
FI1=10_695_000; FI2=455_000; LO2=10_240_000
FREQ_MODES={'AM':(LO2,None,6_000),'FM':(LO2,None,12_000),
            'USB':(10_238_500,456_500,2_700),'LSB':(10_241_500,453_500,2_700),
            'CW':(LO2,455_700,500)}
C_BASE=180e-12; L0=1e-6; RLOAD=3300.; Q_UNLOADED=80.
def c_required(f0=FI1,L=L0):return 1/((2*math.pi*f0)**2*L)
def loaded_q(Q0=Q_UNLOADED, r=RLOAD, L=L0, f0=FI1):
    # Tank parallel loss Rpar = Q0*XL, resistor load additional parallel
    xl=2*math.pi*f0*L
    return 1/(1/Q0 + xl/r)
def tank_amp(f,f0=FI1,q=None):
    if q is None:q=loaded_q()
    return 1/math.sqrt(1+(q*(f/f0 - f0/f))**2)
def roofing_db(f,q1=None,q2=None,f01=FI1,f02=FI1):
    a=tank_amp(f,f01,q1)*tank_amp(f,f02,q2)
    return 20*math.log10(max(a,1e-300))
def bpf_db(delta,bw,order=4):
    # baseband-equivalent magnitude of assumed Butterworth bandpass; NOT vendor measured curves
    x=2*abs(delta)/bw
    return -10*math.log10(1+x**(2*order))
def tune_lo2(mode):return FREQ_MODES[mode][0]
def bfo(mode):return FREQ_MODES[mode][1]
def sideband_if2(mode,delta):
    assert mode in ('USB','LSB')
    sign=1 if mode=='USB' else -1
    if1=FI1-sign*delta
    return if1-tune_lo2(mode)
def agc_target_rms(vref=1.5,rtop=100e3,rbot=680e3):
    vset=vref*rbot/(rtop+rbot)
    return abs(vset-vref)
def agc_tau(c=1e-6):return 17450*(285e-12+c)
def target_gain_db(vin_rms):
    # Ideal infinite-bandwidth gain estimate, clamped to the 0..80 dB range of data sheet
    return min(80.,max(0.,20*math.log10(agc_target_rms()/vin_rms)))
def attack_response(initial_gain,final_gain,t,tau=agc_tau()):
    return final_gain+(initial_gain-final_gain)*math.exp(-t/tau)
def gain_sweep(n=2401):
    return [(round(-25_000+50_000*i/(n-1)),round(bpf_db(-25_000+50_000*i/(n-1),2700),4),
            round(bpf_db(-25_000+50_000*i/(n-1),6000),4),
            round(bpf_db(-25_000+50_000*i/(n-1),12000),4),
            round(bpf_db(-25_000+50_000*i/(n-1),500),4)) for i in range(n)]
def main():
    with (ROOT/'02_Piano_Frequenze/V6.4/PIANO_PLL_LO_270_RX_V6.4.csv').open(encoding='utf8') as f: rows=list(csv.DictReader(f))
    assert len(rows)==270
    rr=[]
    for x in rows:
        rf=int(x['rf_hz']);lo1=int(x['lo_hz']);assert lo1-rf==FI1
        for mode,(lo2,b,bw) in FREQ_MODES.items():
            if mode=='USB':fif2_center=sideband_if2(mode,1500)
            elif mode=='LSB':fif2_center=sideband_if2(mode,1500)
            else:fif2_center=FI1-lo2
            rr.append([x['banda'],x['canale'],rf,mode,lo1,FI1,lo2,lo1-rf-lo2,fif2_center,b if b is not None else '',bw,'MODELLO_CONVERSIONE_NON_HARDWARE'])
    (ROOT/'02_Piano_Frequenze/V6.8').mkdir(parents=True,exist_ok=True)
    with (ROOT/'02_Piano_Frequenze/V6.8/PIANO_270_X_5_IF2_V6.8.csv').open('w',encoding='utf8',newline='') as f:
        w=csv.writer(f);w.writerow(['band','channel','rf_hz','mode','lo1_hz','if1_carrier_hz','lo2_hz','if2_carrier_hz','if2_selected_center_hz','bfo_hz','ideal_filter_bw_3db_hz','status']);w.writerows(rr)
    with (HERE/'CURVE_455_IDEALI_V6.8.csv').open('w',encoding='utf8',newline='') as f:
        w=csv.writer(f);w.writerow(['offset_hz','ssb_ideal_db','am_ideal_db','fm_ideal_db','cw_ideal_db']);w.writerows(gain_sweep())
    mc=[];rnd=random.Random(680112)
    for i in range(12_000):
        # toy sensitivity scenarios: component Q and loaded resistance arbitrary and independent
        q0a=rnd.uniform(45,100);q0b=rnd.uniform(45,100);ra=rnd.uniform(2500,5000);rb=rnd.uniform(2500,5000)
        la=1e-6*rnd.uniform(.95,1.05);lb=1e-6*rnd.uniform(.95,1.05)
        f01=FI1+rnd.uniform(-1800,1800);f02=FI1+rnd.uniform(-1800,1800)
        qa=loaded_q(q0a,ra,la,f01);qb=loaded_q(q0b,rb,lb,f02)
        inband_min=min(roofing_db(f,q1=qa,q2=qb,f01=f01,f02=f02) for f in (FI1-12000,FI1,FI1+12000))
        image_db=roofing_db(9_785_000,q1=qa,q2=qb,f01=f01,f02=f02)
        rel=image_db-roofing_db(FI1,q1=qa,q2=qb,f01=f01,f02=f02)
        mc.append((inband_min,rel,qa,qb))
    c=c_required();tau=agc_tau();vset=1.5*680/(100+680);vtarget=agc_target_rms()
    model={
      'revision':'V6.8','status':'NUMERIC_STUDY_NOT_SPICE_NOT_HARDWARE','rx_channels':270,'modes':5,'channel_mode_rows':len(rr),
      'if1_hz':FI1,'if2_hz':FI2,'sideband_inversion_first_high_side_lo':True,
      'lo2_mode_hz':{m:a[0] for m,a in FREQ_MODES.items()},'bfo_mode_hz':{m:a[1] for m,a in FREQ_MODES.items()},
      'usb_if2_edges_hz':[sideband_if2('USB',2700),sideband_if2('USB',300)],
      'lsb_if2_edges_hz':[sideband_if2('LSB',300),sideband_if2('LSB',2700)],
      'roofing_lc':{'L_h':L0,'C_total_f':c,'C_fixed_f':C_BASE,'Ctrim_needed_pf':(c-C_BASE)*1e12,
         'loaded_Q_assumed':loaded_q(),'nominal_bandwidth_hz':FI1/loaded_q(),
         'pass_at_if1_plus_12khz_db':roofing_db(FI1+12000),
         'stop_if2_image_9p785mhz_db_ideal':roofing_db(9_785_000),
         'approximate_assumptions':'two independent isolated unloaded-Q=80 parallel tanks; buffer and leakage ignored'},
      'agc':{'vref_v':1.5,'r_top_ohm':100000,'r_bot_ohm':680000,'setpoint_v':vset,'target_diff_rms_v':vtarget,
         'c_deto_f':1e-6,'tau_nominal_s':tau,'tau_0p1uF_s':agc_tau(0.1e-6),
         'gain_50uVrms_db':target_gain_db(50e-6),'gain_5mVrms_db':target_gain_db(5e-3),
         'step_40db_settle_1db_s':tau*math.log(40),
         'estimated_sr_differential_v_per_us':2*math.pi*FI1*(vtarget*math.sqrt(2))/1e6,
         'nominal_output_vpp_differential':2*math.sqrt(2)*vtarget,
         'note':'first-order gain response and datasheet timing only; no real AGC envelope waveform simulation'},
      'ideal_455_filter':{'order':4,'am_bw3_hz':6000,'fm_bw3_hz':12000,'ssb_bw3_hz':2700,'cw_bw3_hz':500,
          'usb_edge_1200hz_att_db':bpf_db(1200,2700),
          'lsb_edge_1200hz_att_db':bpf_db(1200,2700),
          'am_adjacent_10khz_att_db':bpf_db(10000,6000),
          'fm_adjacent_10khz_att_db':bpf_db(10000,12000),
          'note':'Butterworth envelopes NOT Murata or real SSB/CW response'},
      'mc_12000':{'random_seed':680112,'sample_count':len(mc),
          'worst_inband_12000_db_min':min(x[0] for x in mc),
          'if2_image_rejection_db_range':[min(-x[1] for x in mc),max(-x[1] for x in mc)],
          'q_loaded_range':[min(min(x[2],x[3]) for x in mc),max(max(x[2],x[3]) for x in mc)],
          'note':'arbitrary independent uniforms on Q0/Rload/L/trimming offset; no correlated production or EM parasitics'},
      'corrections_or_open':[
         'No LO2 generator nor BFO built, no MCU pin allocated','Murata catalog from 2011; procurement not verified',
         'F823/F824 no manufacturer part, SW821/SW822 unselected','B811/B812 buffers unselected and impedance transformation not solved',
         '3V3_A_IF_SW current and real hardware gating not yet allocated','bandwidth/linearity/saturation at 10.695 not validated',
         'passband/image attenuation theoretical only','No connection to TX; no release to fab'],
      'native_ngspice':'NOT_RUN','native_KiCad':'NOT_RUN','hardware':'NOT_TESTED','tx_permission':False,'fab_permission':False}
    (HERE/'RISULTATI_SIMULAZIONI_FI_AGC_V6.8.json').write_text(json.dumps(model,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    # Plots using vector SVG files
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    freq=np.linspace(9.2e6,11.8e6,3201)
    vals=[roofing_db(float(f)) for f in freq]
    fig,ax=plt.subplots(figsize=(9,4.5));ax.plot(freq/1e6,vals,label='2 risonatori LC (ipotesi Q/carico)');ax.axvline(10.695,linestyle='--',alpha=.6,label='FI1 10.695MHz');ax.axvline(9.785,linestyle=':',alpha=.7,label='immagine 2a conversione 9.785MHz');ax.set(xlabel='Frequenza [MHz]',ylabel='Ampiezza normalizzata [dB]',title='Roofing 10.695MHz — solo modello a buffer ideali');ax.grid(alpha=.3);ax.legend();fig.tight_layout();fig.savefig(HERE/'RISPOSTA_ROOFING_FI1_V6.8.svg');plt.close(fig)
    delta=np.linspace(-25000,25000,2001)
    fig,ax=plt.subplots(figsize=(9,4.5))
    for mode,bw in [('FM',12000),('AM',6000),('USB/LSB',2700),('CW',500)]:
        ax.plot(delta/1000,[bpf_db(float(d),bw) for d in delta],label=f'{mode} ideale {bw/1000:g}kHz')
    ax.set(xlim=(-20,20),ylim=(-100,2),xlabel='Scostamento da 455 kHz [kHz]',ylabel='Ampiezza normale [dB]',title='FI2 a 455 kHz — maschere ANALITICHE, NON specifiche filtri');ax.grid(alpha=.3);ax.legend();fig.tight_layout();fig.savefig(HERE/'CURVE_FILTRI_455_IDEALI_V6.8.svg');plt.close(fig)
    times=np.linspace(0,.1,1200)
    initial=target_gain_db(50e-6);final=target_gain_db(5e-3)
    gains=[attack_response(initial,final,float(t)) for t in times]
    fig,ax=plt.subplots(figsize=(9,4.5));ax.plot(times*1000,gains,label='guadagno ideale, passo ingresso +40dB');ax.axhline(final,color='black',linestyle='--',alpha=.5,label='equilibrio ideale');ax.set(xlabel='Tempo dopo salto [ms]',ylabel='Guadagno equivalente [dB]',title='AGC AD8338 — solo costante nominale e sistema lineare semplificato');ax.grid(alpha=.3);ax.legend();fig.tight_layout();fig.savefig(HERE/'TRANSITORIO_AGC_IDEALE_V6.8.svg');plt.close(fig)
    print(json.dumps({'rows':len(rr),'q':loaded_q(),'image_db':model['roofing_lc']['stop_if2_image_9p785mhz_db_ideal'],
       'agc_tau_ms':tau*1000,'ssb_edges_usb':model['usb_if2_edges_hz'],
       'monte_carlo':len(mc)},indent=2))
if __name__=='__main__':main()
