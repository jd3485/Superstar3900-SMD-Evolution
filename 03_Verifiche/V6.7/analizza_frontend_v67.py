#!/usr/bin/env python3
"""Reproducible RF front end Friis/pad/shunt-C/model, NOT a vendor RF simulator."""
import csv, json, math, random, statistics
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SRC=ROOT/'02_Piano_Frequenze/V6.4/PIANO_PLL_LO_270_RX_V6.4.csv'
Z0=50.0

def db2lin(x): return 10**(x/10)
def lin2db(x): return 10*math.log10(x)
def f_nf(stages):
    """Friis noise for [(gain_db,nf_db)] referenced to RF input; NF mixer ONLY proxy assumption."""
    f=1.; preceding=1.; net=1.
    for gain_db,nf_db in stages:
        f+=(db2lin(nf_db)-1)/preceding
        preceding*=db2lin(gain_db)
        net*=db2lin(gain_db)
    return lin2db(f),lin2db(net)

def front_metrics(filter_loss=1.3,lna_gain=16.5,lna_nf=3.,mixer_loss=5.,coax_loss=.3,pad=0.,mixer_nf_extra=0.):
    return f_nf([(-coax_loss,coax_loss),(-filter_loss,filter_loss),(lna_gain,lna_nf),(-pad,pad),(-mixer_loss,mixer_loss+mixer_nf_extra)])

def esd_s21_loss(f_hz,c_farads):
    """Ideal shunt capacitor between 2 matched 50ohm ports (no nonlinear ESD behavior)."""
    y=1j*2*math.pi*f_hz*c_farads
    return -20*math.log10(abs(2/(2+y*Z0)))

def pi_attenuator(r_series=37.4,r_shunt=150.,z0=50.):
    # ABCD of shunt Y, series Z, shunt Y
    Y=1/r_shunt; Z=r_series
    a=1+Z*Y; b=Z; c=2*Y+Y*Y*Z; d=a
    den=a+b/z0+c*z0+d
    s21=2/den
    s11=(a+b/z0-c*z0-d)/den
    return -20*math.log10(abs(s21)),-20*math.log10(max(abs(s11),1e-30))

def analyze():
    with SRC.open(encoding='utf-8',newline='') as f: channels=list(csv.DictReader(f))
    assert len(channels)==270
    nominal_nf,nominal_gain=front_metrics()
    pad_loss,pad_rl=pi_attenuator()
    pad_nf,pad_gain=front_metrics(pad=pad_loss)
    max_nf,max_gain=front_metrics(filter_loss=2.5)
    out=[]
    for r in channels:
        rf=int(r['rf_hz']); img=int(r['if_image_hz']); lo=int(r['lo_hz'])
        assert img == lo+10695000 and lo==rf+10695000
        # Assumed ADI typical gain linear interpolation 20->70MHz, explicitly not a rated limit.
        interp_gain=16.7+(16.5-16.7)*(rf/1e6-20)/50
        nf,gain=front_metrics(lna_gain=interp_gain)
        out.append([r['banda'],r['canale'],rf,lo,img,round(interp_gain,4),round(gain,4),round(nf,4),round(esd_s21_loss(rf,0.2e-12),8),20,round(20-2.5,3),'MODELLO_E_IPOTESI_NON_DATI_MISURATI'])
    with (HERE/'BILANCIO_270_RX_V6.7.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(['banda','canale','rf_hz','lo_hz','image_hz','adl_gain_interp_db_assunto','front_net_gain_db_assunto','front_nf_db_friis_assunto','esd_ideal_il_0p2pf_db','stopband_min_vendor_db','conservative_relative_image_db','status']);w.writerows(out)

    # Stress test: chosen ranges for exploration. NOT statistical manufacturing yield.
    rng=random.Random(390067); trials=[]
    for i in range(20000):
        il=rng.uniform(1,2.5); g=rng.uniform(15.0,17.0); n=rng.uniform(2.7,4.0); mix=rng.uniform(4.5,7.0)
        coax=rng.uniform(.1,.6); ext_nf=rng.uniform(0,2.)
        nf,gn=front_metrics(il,g,n,mix,coax,mixer_nf_extra=ext_nf)
        trials.append((nf,gn))
    nfs=[v[0] for v in trials]; gains=[v[1] for v in trials]
    res={
      'rev':'V6.7', 'status':'NUMERICAL_SIMULATION_NOT_EM_OR_SPICE',
      'frequency_positions':len(channels),
      'default_assumptions':{'coax_loss_db':.3,'sxbp_filter_loss_typ_db':1.3,'sxbp_filter_loss_max_db_at_25C':2.5,'adl_gain_typ_27MHz_proxy_db':16.5,'adl_nf_typ_27MHz_proxy_db':3.,'ade1_mixer_conversion_loss_typ_db':5.,'ade1_mixer_nf_proxy_db':5.,'esd_cap_max_pf':.2},
      'default_no_pad':{'nf_db':round(nominal_nf,5),'net_conversion_gain_db':round(nominal_gain,5)},
      'default_pad6':{'nominal_pi_loss_db':round(pad_loss,5),'pi_return_loss_db':round(pad_rl,5),'nf_db':round(pad_nf,5),'net_conversion_gain_db':round(pad_gain,5)},
      'filter_max_il_case_no_pad':{'nf_db':round(max_nf,5),'net_conversion_gain_db':round(max_gain,5)},
      'esd_ideal_shunt_loss_27mhz_db':esd_s21_loss(27e6,.2e-12),
      'image_rejection':{'vendor_stopband_min_db':20.,'passband_max_db':2.5,'relative_worst_case_lower_bound_db_if_equal_other_gain':17.5,'desired_internal_target_db':40.,'target_certified':False},
      'blocker_example':{'input_antenna_dbm':0.,'post_filter_dbm':-1.6,'adl_out_dbm':14.9,'mixer_in_no_pad_dbm':14.9,'mixer_in_pad6_dbm':round(14.9-pad_loss,5),'adl_input_p1db_ant_proxy_dbm':round(17.7-(16.5-1.6),3),'caution':'LNA output P1dB is a TYPICAL 20MHz spec, proxy for 27MHz, not safe operating threshold'},
      'adl_thermal_approx':{'dc_power_typ_w':5*.097,'dc_power_115ma_w':5*.115,'estimated_tj_at_85c_115ma_and_30p7K_W_c':85+5*.115*30.7,'datasheet_pad_soldered_thetaJA_c_w':30.7,'measured':False},
      'monte_carlo':{'samples':20000,'seed':390067,'model':'independent uniform ranges chosen for exploratory stress, NOT manufacturing probability',
       'ranges':{'filter_loss_db':[1,2.5],'coax_loss_db':[.1,.6],'lna_gain_db':[15,17],'lna_nf_db':[2.7,4.0],'mixer_conversion_loss_db':[4.5,7.0],'mixer_nf_extra_db':[0,2]},
       'nf_min_db':min(nfs),'nf_median_db':statistics.median(nfs),'nf_max_db':max(nfs),'gain_min_db':min(gains),'gain_median_db':statistics.median(gains),'gain_max_db':max(gains)},
      'not_run':['native_KiCad_ERC','native_KiCad_DRC','ngspice_native','VNA_Sparams','EM_layout','hardware_ESD_or_TX_isolation','RF_blocker_nonlinear_measurement'],
      'tx_enabled':False,'fab_released':False,
    }
    (HERE/'RISULTATI_ANALISI_FRONTEND_V6.7.json').write_text(json.dumps(res,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig,ax=plt.subplots(figsize=(9,4.4))
        ax.scatter(gains[::16],nfs[::16],s=4,alpha=.3)
        ax.scatter([nominal_gain],[nominal_nf],s=80,marker='x',label='Modello nominale')
        ax.set(xlabel='Guadagno di conversione totale (dB)',ylabel='Figura di rumore equivalente (dB)',title='V6.7 | 20.000 casi esplorativi (1/16 visualizzati)')
        ax.grid(True,alpha=.3); ax.legend();fig.tight_layout()
        fig.savefig(HERE/'STRESS_GAIN_NF_V6.7.svg');plt.close(fig)
    except ImportError:
        pass
    return res

if __name__=='__main__':
    r=analyze()
    print('SIM_V67_PASS',r['frequency_positions'],r['default_no_pad'],r['default_pad6'],r['monte_carlo']['samples'])
