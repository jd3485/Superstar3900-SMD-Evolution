#!/usr/bin/env python3
"""Ideal matched 50-ohm pi pad test. No physical circuit model."""
import math, random
Z0=50

def calc(r1,rs,r2):
 y1,y2=1/r1,1/r2
 A,B,C,D=1+rs*y2,rs,y1+y2+y1*rs*y2,1+y1*rs
 den=A+B/Z0+C*Z0+D
 s11=(A+B/Z0-C*Z0-D)/den
 s21=2/den
 return -20*math.log10(abs(s21)),-20*math.log10(abs(s11))

if __name__=='__main__':
 K=10**(6/20)
 assert abs(50*(K+1)/(K-1)-150.476)<.1
 il,rl=calc(150,37.4,150)
 assert 5.95<il<6.05,(il,rl)
 assert rl>40,(il,rl)
 random.seed(390031)
 out=[]
 for _ in range(10000):
  vals=[v*(1+random.uniform(-.01,.01)) for v in (150,37.4,150)]
  out.append(calc(*vals))
 assert all(5.7<v[0]<6.3 for v in out)
 assert all(v[1]>30 for v in out)
 print('PASS nominal IL/RL = %.4f / %.2f dB; 10000 independent resistor tolerance samples' % (il,rl))
