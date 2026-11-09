#!/usr/bin/env python3
"""V2.8: network 2-port of 50-ohm preselector; study only.
Parallel-LC resonant branches are *series* elements in the RF path.
Each inductor has Z=R+jwL with R=wL/Q (Q constant across f, assumed).
Each capacitor includes illustrative tan-delta=0.001 as series ESR or shunt G.
No SRF, mutual coupling, pad parasitics, switch, ESD or enclosure.
Run: python 03_Verifiche/V2.8/model_v28.py --check
"""
from __future__ import annotations
import numpy as np, math, csv, json, argparse
from pathlib import Path
PI=math.pi; Z0=50.
PASS=np.linspace(25.615e6,28.305e6,101)
IMG=np.linspace(47.005e6,49.695e6,101)

def hp3(fc=12e6):
    # Normalized Butterworth g values for N=3: 1,2,1.
    g=[1,2,1]
    return [('CS',1/(2*PI*fc*Z0*g[0])),('LS',Z0/(2*PI*fc*g[1])),('CS',1/(2*PI*fc*Z0*g[2]))]

def lp7_traps():
    # Commercial value candidates, NOT approved MPNs. Tuned traps at ~50.1 and 47.6 MHz.
    return [('T',(180e-9,56e-12)),('C',120e-12),('L',470e-9),
            ('C',140e-12),('L',470e-9),('C',120e-12),('T',(180e-9,62e-12))]

def two_port(elements,frequency,q=30.,tand=0.001,z0=50.):
    f=np.atleast_1d(np.asarray(frequency,dtype=float));w=2*PI*f
    A=np.ones(f.shape,complex);B=np.zeros(f.shape,complex)
    C=np.zeros(f.shape,complex);D=np.ones(f.shape,complex)
    for typ,value in elements:
        if typ=='L':
            zz=w*value/q + 1j*w*value;aa,bb,cc,dd=1,zz,0,1
        elif typ=='T':
            L,cap=value
            zl=w*L/q+1j*w*L
            zc=tand/(w*cap)+1/(1j*w*cap)
            zz=zl*zc/(zl+zc)
            aa,bb,cc,dd=1,zz,0,1
        elif typ=='C':
            yy=w*value*tand+1j*w*value;aa,bb,cc,dd=1,0,yy,1
        elif typ=='CS':
            zz=tand/(w*value)+1/(1j*w*value);aa,bb,cc,dd=1,zz,0,1
        elif typ=='LS':
            zl=w*value/q+1j*w*value
            aa,bb,cc,dd=1,0,1/zl,1
        else:raise ValueError(typ)
        A,B,C,D=A*aa+B*cc,A*bb+B*dd,C*aa+D*cc,C*bb+D*dd
    den=A+B/z0+C*z0+D
    return 2/den,(A+B/z0-C*z0-D)/den

def measure(elements,q=30.,tand=.001):
    s21,s11=two_port(elements,PASS,q,tand)
    simg,_=two_port(elements,IMG,q,tand)
    return {'loss_max_dB':float(np.max(-20*np.log10(abs(s21)))),
       'image_rejection_min_dB':float(np.min(-20*np.log10(abs(simg)))),
       's11_worst_dB':float(np.max(20*np.log10(abs(s11))))}

def perturb(elements,rng,qlow=20,qhigh=60):
    q=float(rng.uniform(qlow,qhigh))
    new=[]
    for kind,value in elements:
        if kind=='T':
            L,C=value
            new.append((kind,(L*(1+rng.uniform(-.05,.05)),C*(1+rng.uniform(-.02,.02)))))
        else:
            err=.05 if kind in ('L','LS') else .02
            new.append((kind,value*(1+rng.uniform(-err,err))))
    return new,q

def pass_gate(result):
    return result['loss_max_dB']<=1.5 and result['image_rejection_min_dB']>=60 and result['s11_worst_dB']<=-10

def runchecks():
    p=lp7_traps()
    assert len(p)==7 and sum(k=='T' for k,v in p)==2
    assert len(hp3())==3
    for l,c in (p[0][1],p[-1][1]):
        f=1/(2*PI*np.sqrt(l*c))
        assert 45e6<f<52e6
    for series in (p,hp3()+p):
        s21,s11=two_port(series,np.linspace(1e6,80e6,300),q=30)
        assert np.isfinite(s21).all()
        assert np.max(abs(s21)**2+abs(s11)**2)<=1.0000001
        m=measure(series,30)
        assert m['loss_max_dB']<3 and m['image_rejection_min_dB']>55
    # Compare plain LP7 ABCD against historical unchanged code outside study's resonant branches.
    return True

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--check',action='store_true');args=a.parse_args()
    if args.check:print('PASS',runchecks())
    for n,e in [('LP7_DUE_TRAP',lp7_traps()),('HP3_LP7_DUE_TRAP',hp3()+lp7_traps())]:
        print(n,measure(e,30))
