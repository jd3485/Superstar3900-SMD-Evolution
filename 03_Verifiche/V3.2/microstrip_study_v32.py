#!/usr/bin/env python3
"""STUDIO ESPLORATIVO microstrip, NON calcolo RF approvato per produzione.
Modello quasi-statico senza spessore rame, solder mask, coplanar gaps, via o edge launch.
"""
from math import sqrt, log, pi
from pathlib import Path
import csv

def microstrip_z0(w_mm, h_mm, er):
    u=w_mm/h_mm
    e_eff=(er+1)/2+(er-1)/2*(1/sqrt(1+12/u)+(0.04*(1-u)**2 if u<1 else 0))
    if u<=1:
        return 60/sqrt(e_eff)*log(8/u+u/4)
    return 120*pi/(sqrt(e_eff)*(u+1.393+0.667*log(u+1.444)))

def solve_width(h,er,target=50):
    a=0.05; b=1.50
    for _ in range(100):
        m=(a+b)/2
        if microstrip_z0(m,h,er)>target:a=m
        else:b=m
    return (a+b)/2

if __name__=='__main__':
    out=Path(__file__).with_name('Analisi_Microstrip_V3.2.csv')
    rows=[]
    for h in (0.17,0.1855,0.21):
        for er in (4.2,4.74,5.0):
            rows.append([h,er,round(solve_width(h,er),4),round(microstrip_z0(0.34,h,er),3)])
    with out.open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['h_mm','er','w_stimata_50ohm_mm','Z0_a_w034_ohm']);w.writerows(rows)
    print('Nominale (h=0.1855, er=4.74) larghezza per 50Ω:',round(solve_width(0.1855,4.74),4),'mm')
    print('Nominale con w=0.34mm:',round(microstrip_z0(.34,.1855,4.74),2),'ohm')
    print('Scenari salvati:',len(rows),out)
