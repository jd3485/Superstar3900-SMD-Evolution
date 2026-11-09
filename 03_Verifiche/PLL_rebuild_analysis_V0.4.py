#!/usr/bin/env python3
"""Rigenera i risultati V0.4 di filtro PLL: solo modello lineare ideale.
Eseguire: python PLL_rebuild_analysis_V0.4.py
Richiede Python3, numpy, scipy. Non richiede connessioni Internet.
Il report contiene il seed per la riproducibilita e non pretende misure fisiche.
"""
import csv,json,math
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
HERE=Path(__file__).resolve().parent
P={'R2':1200.,'R3':270.,'C1':6.8e-9,'C2':120e-9,'C3':4.7e-9,'Icp':.0025,'Kv_hz_v':40e6,'N':3750}
def loop(f,p):
 s=1j*2*np.pi*np.asarray(f,dtype=float)
 Y=s*p['C1'] + 1/(p['R2']+1/(s*p['C2'])) + 1/(p['R3']+1/(s*p['C3']))
 Z=(1/Y)/(1+s*p['R3']*p['C3'])
 return p['Icp']*p['Kv_hz_v']/p['N'] * Z/s
def measure(p):
 fc=brentq(lambda f:abs(loop(f,p))-1,50,70000)
 return fc, 180+np.angle(loop(fc,p),deg=True)
fc,pm=measure(P)
rng=np.random.default_rng(39004)
cases=[]
for i in range(4000):
 x=dict(P)
 for k,tol in [('R2',.01),('R3',.01),('C1',.05),('C2',.20),('C3',.05),('Icp',.05)]:
  x[k]*=rng.uniform(1-tol,1+tol)
 x['Kv_hz_v']=rng.uniform(25e6,55e6)
 x['N']=int(rng.integers(3631,3901))
 test_fc,test_pm=measure(x)
 cases.append((i,test_fc,test_pm,x['Kv_hz_v']/1e6,x['N']))
a=np.asarray(cases)
with (HERE/'PLL_MonteCarlo_V0.4.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['sample','crossover_Hz','phase_margin_deg','Kv_MHz_per_V','feedback_N']);w.writerows(cases)
f=np.logspace(2,6,1100)
L=loop(f,P)
H_vco=np.abs(1/(1+L))/64
H_ref=np.abs(L/(1+L))*(37.5e6/12.8e6)
with (HERE/'PLL_Funzioni_Trasferimento_V0.4.csv').open('w',newline='') as h:
 w=csv.writer(h);w.writerow(['offset_Hz','open_loop_gain_dB','vco_noise_shaping_dB','tcxo_phase_to_output_dB']);
 for ff,ll,vv,rr in zip(f,L,H_vco,H_ref):
  w.writerow([f'{ff:.6f}',f'{20*np.log10(abs(ll)):.6f}',f'{20*np.log10(max(vv,1e-20)):.6f}',f'{20*np.log10(max(rr,1e-20)):.6f}'])
report=json.loads((HERE/'Report_PLL_Loop_V0.4.json').read_text())
assert abs(report['nominal_crossover_Hz']-fc)<0.001
assert abs(report['nominal_phase_margin_deg']-pm)<.001
assert abs(report['montecarlo_min_phase_margin_deg']-a[:,2].min())<.001
assert abs(report['montecarlo_max_phase_margin_deg']-a[:,2].max())<.001
assert np.all(a[:,2]>=45)
# Attenuatori PI shunt/series/shunt in Z0=50ohm. Check input admittance and S21, 1e-12 relative error.
for att in [2,3,5,6,8,9,12,14,16,18]:
 k=10**(att/20)
 rp=50*(k+1)/(k-1);rs=50*(k*k-1)/(2*k)
 zin=1/(1/rp+1/(rs+1/(1/rp+1/50)))
 assert abs(zin-50)<1e-10
 # ABCD: shunt--series--shunt
 A=1+rs/rp;B=rs;C=(2+rs/rp)/rp;D=A
 s21=2/(A+B/50+C*50+D)
 assert abs(-20*np.log10(s21)-att)<1e-10
print(f'PASS: f_cross {fc:.2f} Hz; PM {pm:.2f} deg; 4000 campioni PM min {a[:,2].min():.2f}; PI attenuatori matematicamente adattati in 50 ohm')
