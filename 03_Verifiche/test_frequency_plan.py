"""Verifiche riproducibili del piano canali, da eseguire: python test_frequency_plan.py"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / '02_Piano_Frequenze'))
from frequency_plan import *

entries=list(rows())
assert len(entries) == 270, f"Attesi 270 canali: {len(entries)}"
assert len({e[3] for e in entries}) == 270, 'Ci sono frequenze duplicate'
assert len([e for e in entries if e[2]]) == 30
assert len([e for e in entries if not e[2]]) == 240
assert len([e for e in entries if e[4]]) == 40
assert min(e[3] for e in entries) == 25_615_000
assert max(e[3] for e in entries) == 28_305_000
for band in BAND_OFFSETS_HZ:
    assert len([e for e in entries if e[0] == band]) == 45
    assert frequency_hz(band, 3, True) - frequency_hz(band, 3) == 10_000
    assert frequency_hz(band, 19, True) - frequency_hz(band, 19) == 10_000
    assert frequency_hz(band, 9, True) == frequency_hz(band, 9)
assert frequency_hz('D',9) == 27_065_000
assert frequency_hz('D',19,True) == 27_195_000
assert frequency_hz('D',23) == 27_255_000
assert frequency_hz('D',24) == 27_235_000
assert frequency_hz('F',40) == 28_305_000
assert frequency_hz('A',1) == 25_615_000
assert frequency_hz('F',40,ch9=True) == 27_065_000
assert tx_allowed('D',9)
assert not tx_allowed('D',19,alpha=True)
assert not tx_allowed('A',9)
assert tx_allowed('A',9,ch9=True)
print('PASS: 270 frequenze uniche; 240 normali + 30 ALFA; CH9; anomalie CH23/24; 40 posizioni TX predefinite.')
