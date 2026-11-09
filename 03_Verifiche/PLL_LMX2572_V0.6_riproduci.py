"""S3900 V0.6: modello lineare PLL; non e' una simulazione TI / simulazione IC accurata."""
import json
from pathlib import Path
import numpy as np
F=np.geomspace(50,1e6,1600)
W=1j*2*np.pi*F
X=np.array([220e-12,120e-9,2.2e-9,620.,22.])
def open_loop(x, kv=55e6, n=3750, icp=2.5e-3):
    c1,c2,c3,r2,r3=map(float,x)
    g=1/r3
    ya=W*c1+1/(r2+1/(W*c2))+g
    yb=W*c3+g
    z=g/(ya*yb-g*g)
    return (icp*kv/n)*(z/W)
def measure(x,kv=55e6,n=3750,icp=2.5e-3):
    a=open_loop(x,kv,n,icp)
    idx=np.where((abs(a[:-1])>=1)&(abs(a[1:])<1))[0]
    if len(idx)!=1: raise RuntimeError('Nessun attraversamento univoco')
    i=idx[0]
    fc=10**np.interp(0,np.log10(abs(a[i:i+2]))[::-1],np.log10(F[i:i+2])[::-1])
    phase=np.unwrap(np.angle(a))*180/np.pi
    pm=180+np.interp(np.log10(fc),np.log10(F),phase)
    return float(fc),float(pm),float(max(abs(a/(1+a))))

def run():
    rng=np.random.default_rng(390006)
    out=[]
    for _ in range(4000):
        x=X*rng.normal(1,[.05,.1,.05,.01,.01]);kv=rng.uniform(39e6,85e6); n=rng.uniform(3631,3900);icp=2.5e-3*rng.normal(1,.08)
        out.append(measure(x,kv,n,icp))
    out=np.array(out)
    return {'nominal':measure(X),'min':out.min(axis=0).tolist(),'percentile5':np.percentile(out,5,axis=0).tolist(),'percentile95':np.percentile(out,95,axis=0).tolist(),'pm_below_45_count':int((out[:,1]<45).sum())}
if __name__=='__main__':
    print(json.dumps(run(),indent=2))
