"""Budget di rumore TEORICO con Friis. NON e' simulazione circuitale o misura.

Input ipotizzati di stadi da confermare con parti, adattamenti, PCB e filtri reali.
"""
from dataclasses import dataclass
from math import log10, sqrt

@dataclass(frozen=True)
class Stage:
    name: str
    gain_db: float
    noise_figure_db: float

# Il primo stadio e' un passivo: NF=perdita passiva in ambiente a 290K.
HYPOTHETICAL_STAGES = (
    Stage('Preselettore RF',-1.2,1.2),
    Stage('LNA commutabile',12.0,2.0),
    Stage('Mixer passivo',-5.0,5.0),
    Stage('Amplificatore FI',20.0,6.0),
)

def cascaded_nf_db(stages=HYPOTHETICAL_STAGES):
    f_total=0.0
    gain_before=1.0
    for idx, stage in enumerate(stages):
        nf_lin=10**(stage.noise_figure_db/10)
        gain_lin=10**(stage.gain_db/10)
        f_total += (nf_lin if idx==0 else (nf_lin-1)/gain_before)
        gain_before *= gain_lin
    return 10*log10(f_total)

def thermal_sensitivity_dbm(bw_hz=2400, snr_db=10.0):
    # -174dBm/Hz: densita' termica di riferimento approssimata a 290K.
    return -174.0 + 10*log10(bw_hz) + cascaded_nf_db() + snr_db

def dbm_to_uv_rms(dbm, ohms=50):
    watts=10**((dbm-30)/10)
    return 1e6*sqrt(watts*ohms)

if __name__=='__main__':
    nf=cascaded_nf_db()
    p=thermal_sensitivity_dbm()
    print(f'Ipotesi RF: NF cascata={nf:.3f} dB, 10dB SNR/2.4kHz => {p:.3f} dBm, {dbm_to_uv_rms(p):.3f} uV RMS/50ohm')
    print('Solo modello analitico; NON equiparare direttamente a SINAD o (S+N)/N normato.')
