from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'02_Piano_Frequenze'))
from pll_adf4351_plan import all_points, IF1_HZ, R_DIV, REF_HZ, PFD_HZ, OUT_DIV
from frequency_plan import frequency_hz
assert 1 <= R_DIV <= 1023
assert PFD_HZ == 640_000
xs=list(all_points())
assert len(xs)==270
assert all(p.frac==0 and p.vco_hz == PFD_HZ*p.n_int and p.lo_hz*OUT_DIV==p.vco_hz and p.error_hz==0 for _,_,_,_,p in xs)
assert min(p.n_int for _,_,_,_,p in xs)==3631
assert max(p.n_int for _,_,_,_,p in xs)==3900
assert all(2_200_000_000 <= p.vco_hz<=4_400_000_000 for _,_,_,_,p in xs)
assert frequency_hz('D',9)==27_065_000
assert 36_310_000 == min(p.lo_hz for _,_,_,_,p in xs)
assert 39_000_000 == max(p.lo_hz for _,_,_,_,p in xs)
assert (frequency_hz('D',9)+IF1_HZ)*OUT_DIV//PFD_HZ == 3776
print('PASS stage2: 270 PLL points, R/prescaler range, LO endpoints, CH9 and INT')
