#!/usr/bin/env python3
"""PLL loop model, independent from original project script; third-order passive ladder."""
import numpy as np
from scipy.optimize import brentq
P={'R2':1200.,'R3':270.,'C1':6.8e-9,'C2':120e-9,'C3':4.7e-9,'Icp':.0025,'Kv':40e6,'N':3750}
def transfer(f,p=P):
 s=1j*2*np.pi*f
 y=s*p['C1']+1/(p['R2']+1/(s*p['C2']))+1/(p['R3']+1/(s*p['C3']))
 return (p['Icp']*p['Kv']/p['N'])*(1/y)/(1+s*p['R3']*p['C3'])/s
fc=brentq(lambda f:abs(transfer(f))-1,50,70000)
pm=180+np.angle(transfer(fc),deg=True)
print(f'Crossover={fc:.3f} Hz; phase margin={pm:.3f} deg')
assert 4000 < fc < 5000 and 50 < pm < 60
# genuine closed-loop shaping only; no absolute RF phase-noise dBc/Hz computed
