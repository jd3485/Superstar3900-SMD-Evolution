"""Piano numerico preliminare per un ADF4351 in Integer-N.

Questo NON e' un driver: niente registri hardware, filtro PLL, potenza LO,
spurie o rumore di fase sono ancora progettati/qualificati.

Ipotesi: iniezione alta, FI1=10.695MHz, TCXO 12.8MHz, R=20, DIVOUT=64.
La formula e' VCO=fPFD*INT; fLO=VCO/DIVOUT, fRF=fLO-FI1.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from frequency_plan import rows

IF1_HZ = 10_695_000
REF_HZ = 12_800_000
R_DIV = 20
OUT_DIV = 64
PFD_HZ = REF_HZ // R_DIV
VCO_MIN_HZ = 2_200_000_000
VCO_MAX_HZ = 4_400_000_000

@dataclass(frozen=True)
class PllPoint:
    rf_hz: int
    lo_hz: int
    vco_hz: int
    n_int: int
    frac: int = 0
    mod: int = 2
    error_hz: int = 0


def calculate(rf_hz: int) -> PllPoint:
    if type(rf_hz) is not int:
        raise TypeError('RF richiesta come Hz interi')
    lo = rf_hz + IF1_HZ
    vco = lo * OUT_DIV
    if not (VCO_MIN_HZ <= vco <= VCO_MAX_HZ):
        raise ValueError('VCO fuori intervallo dichiarato')
    if vco % PFD_HZ:
        raise ValueError('Questa frequenza non e rappresentabile esattamente in Integer-N')
    n_int = vco // PFD_HZ
    # Prescaler 8/9 dell'ADF4351: minimo N = 75 (datasheet).
    if not 75 <= n_int <= 65_535:
        raise ValueError('N non valido')
    recovered_rf = (PFD_HZ*n_int)//OUT_DIV - IF1_HZ
    if recovered_rf != rf_hz:
        raise AssertionError('Errore di sintesi non nullo')
    return PllPoint(rf_hz, lo, vco, n_int)


def all_points():
    for band, channel, alpha, rf_hz, tx_enable in rows():
        yield (band, channel, alpha, tx_enable, calculate(rf_hz))

if __name__ == '__main__':
    import csv
    out = Path(__file__).with_name('Tabella_PLL_270_Integer_N.csv')
    with out.open('w', newline='', encoding='utf-8') as f:
        w=csv.writer(f)
        w.writerow(['banda','canale','alfa','tx_software_only','rf_hz','fi1_hz','lo_hz',
                    'vco_hz','tcxo_hz','r_div','pfd_hz','output_div','int_n','frac_n','mod_n','errore_hz'])
        for band,ch,alpha,tx,p in all_points():
            w.writerow([band,ch,int(alpha),int(tx),p.rf_hz,IF1_HZ,p.lo_hz,p.vco_hz,
                        REF_HZ,R_DIV,PFD_HZ,OUT_DIV,p.n_int,p.frac,p.mod,p.error_hz])
    print(f'Creato {out} - 270 righe')
