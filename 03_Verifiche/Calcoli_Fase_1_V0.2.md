# Calcoli e interpretazione delle verifiche - V0.2

## A. Calcolo della sintesi Integer-N
IF = 10.695.000 Hz; f_REF=12.800.000 Hz; R=20; f_PFD=640.000 Hz; divisore uscita=64.

- **CH9 banda D** f_RF =27.065.000 Hz -> f_LO =37.760.000 Hz -> f_VCO=2.416.640.000 Hz -> INT=3776.
- **CH19 ALFA banda D** f_RF =27.195.000 Hz -> f_LO =37.890.000 Hz -> f_VCO=2.424.960.000 Hz -> INT=3789.
- **Banda F, CH40** f_RF=28.305.000 Hz -> f_LO=39.000.000 Hz -> f_VCO=2.496.000.000 Hz -> INT=3900.

Verificato via `test_pll_plan.py` su tutta la tabella: ogni f_LO e divisibile per 10.000 Hz, N intero 3631..3900, VCO nel range del costruttore. **Errore di quantizzazione nominale 0Hz**, che non rappresenta l'errore reale di TCXO, offset BFO, modulazione o rumore PLL.

**Modalita configurazione essenziale:** feedback dal VCO fondamentale (non dall'uscita /64); abilitare mute-until-lock; band-select clock 80 kHz come ipotesi con divisore 8. Da confermare operativamente su registro e prototipo.

## B. Budget rumore ricezione (solo stima Friis, valori ipotizzati)
| Blocco | Gain (dB) | NF (dB) | Stato |
|---|---:|---:|---|
| Preselettore | -1,2 | 1,2 | Ipotesi |
| LNA commutabile | +12 | 2,0 | Ipotesi |
| Mixer passivo | -5 | 5,0 | Dato tipico componente come stima |
| IF | +20 | 6,0 | Ipotesi |

Formula Friis: `F_tot = F1 + (F2-1)/G1 + (F3-1)/(G1 G2) + ...` con F e G lineari. Calcolo `rx_noise_budget.py`: **NF cascata circa 4,85dB**. Per 2,4kHz e 10dB SNR teorico, termica assunta -174dBm/Hz, si ottiene -125,35dBm, circa **0,121 uV RMS/50ohm**. Non e una sensibilita misurata; non equivale automaticamente alle prove SINAD o (S+N)/N, e ignora degradazioni extra, DSP, filtri reali, spurie e temperatura.

**Rischio di compromesso:** +12dB LNA davanti al mixer puo amplificare segnali forti e peggiorare la dinamica. Necessari RF Gain effettivo, attenuatore commutabile e bypass LNA; la selettivita dipendera da perdite, Q e filtri reali.

## C. Potenza e tensioni: dimensionamento futuro dell'ATU
Su carico ideale 50 ohm e onda sinusoidale:
- A 4W: Vrms=sqrt(4*50)=14,14V; Vpicco circa 20V; Irms=sqrt(4/50)=0,283A.
- A 12W: Vrms=sqrt(12*50)=24,49V; Vpicco circa 34,64V; Irms=sqrt(12/50)=0,490A.

L'ATU reale con alto ROS puo avere tensioni, correnti e dissipazioni interne ben maggiori di questi numeri; i componenti non vanno selezionati per il solo caso 50ohm adattato. I test saranno su carico fittizio e su carichi reattivi controllati.

## D. Limiti delle prove
Questi script verificano soltanto aritmetica e invarianti della logica; **nessun programma SPICE, simulazione PLL, EM, ERC/DRC, misura RF o test PCB e stato eseguito in V0.2**. L'assenza di KiCad/ngspice nell'ambiente corrente e indicata nello stato progetto; quando saranno disponibili i file circuitali e strumenti compatibili eseguiremo controlli riproducibili.
