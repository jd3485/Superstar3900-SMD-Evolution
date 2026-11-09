#!/usr/bin/env python3
"""RF S3900E V2.9, 50-ohm AC model with Coilcraft 0805CS typical lumped elements.
Source: https://www.coilcraft.com/getmedia/c86a99da-e310-4932-bb03-09af08346f8a/spice_0805cs.pdf
NOT full ngspice run, NOT measured S-parameters, NOT PCB EM simulation.
Rvar=k*sqrt(f_Hz). Cp is intrinsic inductor parasitic; capacitors: assumed tanδ=0.001.
"""
from __future__ import annotations
import numpy as np
from math import pi
Z0=50.0
COILS={180:(18.,.64,.090,178.,2.75e-4),330:(31.,1.40,.096,320.,4.74e-4),470:(66.,1.8,.132,470.,6.14e-4)}
RX=np.linspace(25.615e6,28.305e6,101)
IMG=np.linspace(47.005e6,49.695e6,101)
# Trap T = Coilcraft L in parallel with C0G capacitor in the series RF path.
# Shunt C nodes refer to RF ground and are represented in ABCD as a parallel admittance.
CORE=[('T',(180,56.)),('C',120.),('L',470),('C',150.),('L',470),('C',120.),('T',(180,62.))]
HP3=[('CS',270.),('LS',330),('CS',270.)] # optional high-pass candidate

def zcoil(n,f,lv=1.,rv=1.,cv=1.):
    r1,r2,cp,l,k=COILS[n]
    f=np.asarray(f,dtype=float);w=2*pi*f
    a=rv*k*np.sqrt(f)+1j*w*(l*lv*1e-9)
    b=r1*rv+1/(1j*w*(cp*cv*1e-12))
    return r2*rv + a*b/(a+b)

def twoport(elements,f,tand=.001,lv=1.,rv=1.,cv=1.):
    f=np.atleast_1d(np.asarray(f,dtype=float));w=2*pi*f
    A=np.ones_like(w,dtype=complex);B=np.zeros_like(A);C=np.zeros_like(A);D=np.ones_like(A)
    for kind,val in elements:
        if kind=='L':
            z=zcoil(val,f,lv,rv,cv);a,b,c,d=1,z,0,1
        elif kind=='T':
            n,cp=val
            zl=zcoil(n,f,lv,rv,cv);zc=tand/(w*cp*1e-12)+1/(1j*w*cp*1e-12)
            z=zl*zc/(zl+zc);a,b,c,d=1,z,0,1
        elif kind=='C':
            y=1j*w*val*1e-12+tand*w*val*1e-12;a,b,c,d=1,0,y,1
        elif kind=='CS':
            z=tand/(w*val*1e-12)+1/(1j*w*val*1e-12);a,b,c,d=1,z,0,1
        elif kind=='LS':
            z=zcoil(val,f,lv,rv,cv);a,b,c,d=1,0,1/z,1
        else:raise ValueError(kind)
        A,B,C,D=A*a+B*c,A*b+B*d,C*a+D*c,C*b+D*d
    den=A+B/Z0+C*Z0+D
    return 2/den,(A+B/Z0-C*Z0-D)/den

def metrics(elements,lv=1.,rv=1.,cv=1.):
    s21,s11=twoport(elements,RX,lv=lv,rv=rv,cv=cv)
    s21img,_=twoport(elements,IMG,lv=lv,rv=rv,cv=cv)
    return {'loss_max_dB':float(np.max(-20*np.log10(np.abs(s21)))),
            'image_rejection_min_dB':float(np.min(-20*np.log10(np.abs(s21img)))),
            's11_worst_dB':float(np.max(20*np.log10(np.abs(s11))))}

def perturb(elements,rng):
    out=[]
    for kind,v in elements:
        if kind=='T':out.append((kind,(v[0],v[1]*rng.uniform(.98,1.02))))
        elif kind in ('C','CS'):out.append((kind,v*rng.uniform(.98,1.02)))
        else:out.append((kind,v))
    return out

def check():
    assert len(CORE)==7 and len(HP3+CORE)==10
    for n in COILS:
        z=zcoil(n,np.array([27e6]))[0]
        assert z.real>0 and z.imag>0
    for es in (CORE,HP3+CORE):
        s21,s11=twoport(es,np.linspace(1e6,80e6,300))
        assert np.all(np.isfinite(s21))
        assert np.max(abs(s21)**2+abs(s11)**2)<=1.00001
        assert metrics(es)['image_rejection_min_dB']>50
    return True

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--results',action='store_true');args=p.parse_args()
    if args.check:print('PASS' if check() else 'FAIL')
    if args.results:
        print('CORE:',metrics(CORE));print('HP3 + CORE:',metrics(HP3+CORE))
