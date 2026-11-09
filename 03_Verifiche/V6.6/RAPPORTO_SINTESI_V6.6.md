# V6.6 — Rapporto di verifica del preselettore

**Obiettivo:** concretizzare F501 ideale V6.5 in un circuito a 3 risonatori a 50Ω e confrontarlo con un filtro SMT 50Ω di fabbrica.

**Output del modello LC discreto** (QL=60, QC=400, SRF serie 90MHz, shunt 350MHz, C_FEED 0,05pF): perdita RX **3.307–5.593dB**; attenuazione immagine minima **52.834dB**; reiezione relativa minima **47.956dB**; return loss peggiore **6.179dB**; 270/270 RX e immagini.

**Bypass parassita**: aumentando C_FEED da 0 a 1pF, l'attenuazione immagine minima cambia da **61.73** a **30.01dB**, dimostrando forte dipendenza dal layout.

**Stress test** (4.000 scenari pseudo-casuali con distribuzioni esplorative non misurate): 46.83% perdita >6dB; 71.95% reiezione relativa <40dB; 96.85% RL <10dB. Questi non sono tassi statistici di guasto di produzione.

**Decisione preliminare**: circuito LC come artefatto di studio/ottimizzazione; **SXBP-27R5+** preferenziale a titolo di componente candidato (datasheet 24–31MHz pass, 39–900MHz stop >20dB, perdita pass max 2,5dB a 25°C), con verifica finale della soppressione immagine necessaria. Non dichiarare 53dB di reiezione PCB.

**Metodi**: soluzione matriciale Y e S-parameters 50Ω in Python, test passività/idealità, Monte Carlo esplorativo, file SPICE preparato ma **ngspice non eseguito**. Nessuna estrazione elettromagnetica, component/vendor s2p, misurazione VNA o DRC/ ERC KiCad.

**Stato**: sviluppo RX, NO FAB / NO TX. Nessuna autorizzazione TX, nessun PCB prototipo validato.
