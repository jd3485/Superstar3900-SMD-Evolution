import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from lo_filter_analysis import calculate,VALUES,s21_db
import numpy as np
r=calculate(write_files=False)
assert len(VALUES)==7
assert len(r['monte_carlo'])==2
assert -2<s21_db([39e6],inductor_q=60,cap_esr=0.07)[0]<0
assert s21_db([72.62e6],inductor_q=60,cap_esr=0.07)[0]<-25
assert abs(float(s21_db([36.31e6])[0])-(-0.2854))<0.005
assert np.all(np.isfinite(s21_db(np.linspace(20e6,120e6,101))))
print('PASS stage2 LC model S21 math: 7 elements, attenuation and 100MHz sweep finite')
