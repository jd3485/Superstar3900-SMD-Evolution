"""Controlla consistenza dei calcoli d'ordine di grandezza, NON le prestazioni hardware."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from rx_noise_budget import *
f=cascaded_nf_db(); p=thermal_sensitivity_dbm(); u=dbm_to_uv_rms(p)
assert 4.0 < f < 6.0
assert -127.0 < p < -123.0
assert 0.10 < u < 0.16
assert dbm_to_uv_rms(-113.01029995663981) > 0.49
print(f'PASS: modello Friis NF={f:.2f}dB; soglia termica stimata {u:.3f}uV RMS (ipotesi).')
