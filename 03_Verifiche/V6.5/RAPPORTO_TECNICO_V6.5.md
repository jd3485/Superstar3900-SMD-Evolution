# Superstar 3900 SMD Evolution — Rapporto tecnico V6.5

**9 novembre 2026 — Progetto progressivo mixer RF e prima FI; esclusivamente RX. NO FAB / NO TX.**

## Modulo sviluppato nella V6.5

Questa revisione propone il mixer passivo a doppio bilanciamento **Mini-Circuits ADE-1+** (Case CD636): porta RF **pin 3**, LO **pin 6**, FI **pin 2**, GND **pin 1/4/5** secondo datasheet. Il mixer e' progettato per porta LO +7 dBm, RF/LO 0,5–500 MHz, IF DC–500 MHz, perdita di conversione **tipica circa 5 dB** e IP3 tipico 15 dBm. Queste non sono prestazioni misurate nel progetto né garanzia per qualunque condizione; il filtro a monte e' necessario per la dinamica del front-end.

- **BOM candidata 20 righe**, di cui il solo mixer ha pinout vendor validato. Gli altri blocchi F501 (BPF), U502 (buffer LO), F503/F504 (filtri IF), SW501/SW502 (commutazione) e U503 (amplificatore IF) sono parti **TBD**, non componenti acquistabili definiti.
- **Netlist funzionale 37 collegamenti**, con distinzione fra pin U501 fisici certificati e terminali funzionali di dispositivi non ancora selezionati. Non e' netlist KiCad/ERC o PCB fisico. Sono stati corretti i nodi di ingresso/uscita LO e di accoppiamento RF per non unire due reti per errore.
- Ingresso dal front-end RX 50Ω storico V5.8 via J501; LO da J402 V6.4 via J502; uscita prima FI 10,695 MHz via J503; la FI non va mai direttamente al selettore audio V6.0 senza un demodulatore.

## Piano frequenze completo

|Parametro|Valore|Metodo|
|---|---:|---|
|RX e ALFA|270 RX, 30 ALFA|Importazione piano V6.4 immutato|
|RF|25.615–28.305 MHz|Piano A–F|
|LO|36.310–39.000 MHz|LO=RF+10,695MHz|
|Immagine alta|47.005–49.695 MHz|LO+10,695MHz|
|Distanza immagine|21.390 MHz|2×10,695MHz|
|LO livello obiettivo|7.0 dBm, 5.0119 mW|+7dBm, sinusoidale 50Ω|
|LO ampiezza ideale|0.50059 V RMS, 1.41589 Vpp|Calcolo ideale, NON uscita misurata LMX|

## Simulazione numerica preselector: risultati e limiti

Il modello BPF ideale Butterworth ha **ordine prototipo N=3, ordine analogico 6** (non e' una rete disegnata di tre bobine), con frequenze di −3,0103 dB a 25 e 29 MHz. In **270/270** canali:

- Guadagno ideale minimo nella banda desiderata: **-0.3852 dB** (nessun ESR, Q finito, mismatch o perdita);
- Guadagno ideale massimo in banda immagine: **-53.8421 dB**;
- Reiezione immagine **relativa** minima matematica: **53.4589 dB**, NON una specifica ottenuta dal circuito.

Una FFT su sinusoidi a 27,005 MHz e 48,395 MHz, ciascuna moltiplicata separatamente per LO a 37,700 MHz, produce **10,695 MHz** in entrambe le prove: il mixer non può distinguere le immagini. È **simulazione di moltiplicazione ideale**, senza equivalente transistor/diode ring, spur, isolamenti o non linearità di ADE-1+.

Eseguiti **12,000 campioni** riproducibili (seme 6505) variando *la funzione di trasferimento ideale* con f_c ±0,5% e banda ±5%:

- Reiezione immagine assoluta minima nel campione: **52.455 dB**.
- Peggiore trasferimento desiderato nel campione: **-0.920 dB**.

**NON è un'analisi statistica di tolleranze fisiche L/C.** La rete discreta F501 non è stata sintetizzata e gli stadi reali, incluso layout PCB, non sono modellati. Il numero 53 dB non equivale a garanzia di reiezione; con un blocker immagine a 0 dBm e spur massimo richiesto di −110 dBm, per esempio, servirebbero 110 dB di rigetto (ancora da specificare). La portata dinamica del LNA/mixer e il blocker reale sono criticità aperte.

## Filtri a 10,695 MHz per ogni modo: solo requisiti

|Modalità|Larghezza candidata di −3dB|Q caricato approssimato f/BW|
|---|---:|---:|
|CW|500 Hz|21390.0|
|USB|2700 Hz|3961.1|
|LSB|2700 Hz|3961.1|
|AM|6000 Hz|1782.5|
|FM|12000 Hz|891.2|

Per SSB/CW sono richiesti filtri molto selettivi; le bande AM/FM devono essere coerenti con spaziatura canale, deviazione, risposta audio, emissioni interferenti e demodulatori, tutti da definire. Nessun filtro commerciale, quarzo, ceramico o DSP e' stato qualificato o simulato come componente fisico; il Q=10,695MHz/BW è **solo una cifra indicativa**, non Q di una singola bobina.

## Test di coerenza, regressioni e sicurezza

- **50/50 test nuovi V6.5** (unittest) PASS: verifica integrale dei 270 canali, frequenze immagini LO/FI, pin 6 del mixer, mutazioni di CSV/permesso TX, matematica Butterworth (estremi −3,0103 dB), FFT su desiderato e immagine, target LO 50Ω, assenza approvazione FAB, integrazione con `RxPllGuard` V6.4, **128 combinazioni logiche** esaustive e 10.000 combinazioni pseudo-casuali con **TX sempre FALSE**.
- **8/8 suite di regressione selezionate PASS**: V5.9, V6.0, due suite V6.1, V6.2, V6.3, V6.4, V6.5. **Non** equivale a riesecuzione totale della cronologia V4.0–V5.8.
- I file KiCad precedenti restano invariati. KiCad CLI assente nell'ambiente, quindi ERC/DRC **NOT_RUN**; ngspice assente, SPICE vendor **NOT_RUN**. Non dichiarare il modulo fisicamente valido.

## Problemi aperti prima di uno schema KiCad/PCB affidabile

1. Disegnare la rete F501 come filtro passivo/attivo reale 50Ω, con adattamento, componenti, Q, analisi S-parametri / simulazione SPICE e tolleranze fisiche; verificare LO spuri, 10kHz adiacenti e selettività rispetto a tutte le 270 posizioni.
2. Dimensionare il driver LO U502, misurare +7dBm *alla porta* U501, armoniche/isolamento e il 3V3_PLL termico già aperto in V6.4.
3. Selezionare FI 10,695 MHz realmente disponibile, commutazioni per AM/FM/USB/LSB/CW, eventuale seconda conversione/DSP e BFO, amplificatore IF e AGC, intervalli di segnale e rumore.
4. Verificare attenuatore e ADL5535 RX storico, front-end a valle dell'antenna e intermodulazione; reiezione reale RF immagine con LNA e protezioni incluse.
5. Assegnare pin MCU per selettore FI con audit dei pin V6.1 e supervisione PLL V6.4, mantenendo PA e TX disabilitata.
6. Integrare futuro schema nativo KiCad e validare ERC/DRC, package ADE, Gerber, EMI, filtri e test RF dopo completamento generale e controlli incrementali.

**Prossima revisione proposta V6.6: architettura seconda FI/demod AM/FM/SSB/CW oppure sintesi fisica del preselettore, scegliendo il passo che chiude più vincoli.** Nessun permesso TX, nessuna produzione PCBWay, nessun prototipo fisico.

### Fonti dei valori componente

- [Mini-Circuits ADE-1+ datasheet ufficiale](https://www.minicircuits.com/pdfs/ADE-1%2B.pdf), pin 1–6, specifiche LO e conversione; [product page](https://www.minicircuits.com/WebStore/dashboard.html?model=ADE-1%2B).
- [Texas Instruments LMX2572](https://www.ti.com/product/LMX2572) relativo a V6.4.

### Elaborati inclusi

- `01_Specifiche/V6.5/`: schema funzionale, ECO, diagramma, netlist funzionale, pinout vendor 6 pin.
- `02_Piano_Frequenze/V6.5/MAPPATURA_270_MIXER_IMMAGINE_V6.5.csv`.
- `03_Verifiche/V6.5/`: simulatore, test, Monte Carlo, CSV, grafico, regressioni e rapporto.
- `08_Firmware_Prototipi/V6.5/rx_frontend_guard_v65.py` mock RX, e `07_Componenti/BOM_MIXER_FI_V6.5.csv`.
