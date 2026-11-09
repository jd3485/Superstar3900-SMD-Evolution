# Superstar 3900 SMD Evolution — Rapporto tecnico V6.7

**9 novembre 2026 — Interfaccia antenna RX, filtro F501, amplificatore U101 e mixer U501. 50Ω candidato. NO FAB / NO TX.**

## Elementi progettati

- J701 è un **ingresso RX isolato e di laboratorio**, non un connettore antenna condiviso con la futura TX; l'isolamento antenna RX/TX reale non è ancora progettato.
- D701 Semtech **RClamp2271ZC**, TVS RF candidata (cap max 0,2pF). **DNI** nella configurazione di riferimento fino alla qualifica del comportamento ESD, layout e segnale forte. La simulazione lineare usa solo la capacità, non il suo clipping non lineare.
- F501 **Mini-Circuits SXBP-27R5+** preferito sul filtro LC discreto V6.6: 24–31MHz, IL fino a 2,5dB nella banda passante e stopband superiore da 39 a 900 MHz >=20dB, secondo il datasheet a 25°C.
- U101 **ADL5535** riusato dall'archivio storico (NON secondo amplificatore): pin 1 RFIN, 2 + paddle GND, 3 RFOUT e bias 5V via L701 470nH. C701/C702 0,1µF, C703 68pF, C704 1,2nF, C705 1µF, valori presenti nel circuito base ADI; MPN e compatibilità del layout ancora da qualificare.
- R701–R703: opzione `BYPASS` con R701=0Ω e due shunt DNI, oppure `PAD6` con R701=37,4Ω e R702/R703=150Ω, rete PI 50Ω. Le due configurazioni **non si montano contemporaneamente**.
- J702 RF 50Ω verso U501 mixer **ADE-1+ pin3**, LO +7dBm da generare e verificare. J703 5V_RF_RX_SW: l'upstream power gate e il relè antenna hardware restano *non sviluppati*.

Dettagli in `01_Specifiche/V6.7/CIRCUITO_FRONTEND_RX_V6.7.md`, netlist 40 terminali fisici/logici e BOM 17 riferimenti (di cui U101/U501/F501 legacy, non contare doppiamente nei futuri riepiloghi).

## Simulazioni realmente eseguite

Modello Python di Friis a cascata (coax=0,3dB ASSUNTA; filtro IL=1,3dB tip; ADL gain=16,5dB e NF=3,0dB tip vicino a 20–70MHz; mixer conversion loss=5,0dB, NF=5,0dB **proxy NON qualificata**):

| Configurazione | Guadagno di conversione teorico ingresso antenna -> FI | Figura rumore equivalente teorica |
| --- | ---: | ---: |
| No attenuatore | **9.90 dB** | **4.70 dB** |
| PI attenuatore 6.013 dB | **3.89 dB** | **5.13 dB** |
| Filtro IL max 2,5dB, senza pad | **8.70 dB** | **5.90 dB** |

La formula di Friis non rappresenta una NF SSB garantita di mixer passive; modello non include mismatch, rumore LO, desensibilizzazione, IMD di stadi, riverberi, AGC e circuiti IF. La reiezione immagine effettiva è sconosciuta: minimo vendor STOP=20dB vs max passband 2,5dB porta ad appena **17,5dB di reiezione relativa conservativa** con stadi successivi uguali. L'obiettivo interno di studio 40dB **NON è certificato**.

Il condensatore TVS da 0,2pF simulato come shunt ideale fra 50Ω a 27MHz perde teoricamente 0.00000312dB; questa cifra NON è la perdita reale della protezione. Il PI progettato vale 6.0129dB e RL teorico 67.0dB idealizzato.

**Stress random**: 20.000 combinazioni indipendenti uniformi in intervalli arbitrari (specificati in JSON), NON distribuzioni di produzione: NF min/mediana/max 4.04/5.66/7.31dB; guadagno min/mediana/max 5.15/8.12/11.22dB. Tabella numerica per tutti i 270 canali RX e grafico salvati.

**Blocker a 0dBm** ipotizzato dentro la banda: -1,6dBm dopo cavo+filtro, +14,9dBm all'uscita U101, +14,9 dBm all'ingresso mixer bypass, +8.89dBm col PI. Il pad POST-LNA non riduce +14,9dBm di U101: con P1dB tip 17,7dBm a 20MHz il margine è appena 2,8dB nel modello. **Non è una prova di compressione né di sopravvivenza.**

**Termica preliminare ADL** 5V x 97mA ≈ 0,485W e a 115mA ≈ 0,575W. Con thetaJA 30,7°C/W *solo alle condizioni datasheet con paddle saldato*, giunzione teorica a 85°C ambiente ≈ 102.7°C. PCB termico, alimentazione V6.3, bias, potenza e transienti ancora da verificare. La corrente U101 è legacy e **non va sommata nuovamente** se già allocata.

## Test di regressione

**60/60 test nuovi PASS** (test V6.7). Suite storiche selezionate da V5.9 a V6.6: 9/9 PASS, incluse V6.1 MCU + integrazione audio, con esecuzione sui file V6.7. Non tutte le suite storiche V1–V5.8 sono state rieseguite.

## Gate aperti

1. Isolamento del commutatore d'antenna da future potenze TX, ESD/fulmini e protezione ingresso: **non qualificati**. D701 DNI, non attribuirle protezione RF da watt.
2. Immagine 47–50MHz: specifica filtro 20dB min non basta per 40dB relativo. Considerare secondo filtro/architettura diversa, misure VNA in fine progetto.
3. Distorsione con blocker, NF SSB reale, mismatch, attenuatore, LNA compressione, mixer IIP3 e AGC: non misurati.
4. Condizione 5V_RF_RX_SW alimentazione del LNA: attuatore analogico e interblocco antenna da progettare.
5. U101 SOT-89, C e induttanza Q/SRF, footprint filtro F501, layout RF 50Ω e termica non rilasciati; schemi KiCad storico invariati.
6. Progetto non completo: IF, demod, AGC, DSP, TX, ATU, pannello/meccanica finali da progettare. **NO FAB / NO TX**.

**Verifiche NON eseguite:** KiCad ERC/DRC; ngspice native; misure VNA/S-parameters; EM 3D e proof of isolation. File `.cir` creato SOLO come test bench per ESD+PI, non eseguito in ngspice.

**Fonti primarie:**
- ADI ADL5535 https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf
- Mini-Circuits SXBP https://www.minicircuits.com/pdfs/SXBP-27R5%2B.pdf
- Mini-Circuits ADE-1+ https://www.minicircuits.com/WebStore/dashboard.html?model=ADE-1%2B
- Semtech RClamp2271ZC https://www.semtech.com/products/circuit-protection/antenna/rclamp2271zc

**Prossima V6.8:** FI 10,695MHz, filtri AM/FM/SSB/CW, AGC e catena demodulazione, proseguendo test e progettazione incrementali.
