"""Test indipendenti dal chip reale: sola aritmetica dei divisori PLL."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'02_Piano_Frequenze'))
from pll_adf4351_plan import *

pts=list(all_points())
assert len(pts)==270
assert len({p.rf_hz for _,_,_,_,p in pts})==270
assert all(p.error_hz==0 and p.frac==0 for _,_,_,_,p in pts)
assert min(p.lo_hz for *_,p in pts)==36_310_000
assert max(p.lo_hz for *_,p in pts)==39_000_000
assert min(p.vco_hz for *_,p in pts)==2_323_840_000
assert max(p.vco_hz for *_,p in pts)==2_496_000_000
assert min(p.n_int for *_,p in pts)==3631
assert max(p.n_int for *_,p in pts)==3900
assert all((p.lo_hz+p.rf_hz)!=0 for *_,p in pts)
assert all((p.lo_hz+IF1_HZ) >=47_005_000 for *_,p in pts)
assert PFD_HZ==640_000
assert calculate(27_065_000).n_int==3776
assert calculate(27_195_000).n_int==3789
assert calculate(28_305_000).n_int==3900
try:
    calculate(27_065_001)
except ValueError:
    pass
else:
    assert False, 'La configurazione non deve rappresentare passi arbitrari di 1Hz'
print('PASS: 270 LO e 270 INT unici; 36.310-39.000 MHz; VCO 2323.84-2496 MHz; errore 0Hz.')
