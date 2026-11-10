# Superstar 3900 SMD Evolution — RAPPORTO TECNICO V7.3

**10 novembre 2026 · Sviluppo digitale / DAC candidato · NO FAB / NO TX**  
Revisione incrementale dalla V7.2; i file precedenti restano nella storia e non sono stati riscritti. Questo rapporto descrive un **modello numerico** e un progetto di interfaccia **tutto DNP**; non dichiara l'esistenza di schemi hardware montati, firmware reale o trasmissione.

## 1. Moduli sviluppati realmente

**A. Generatore IF2 offline a stato:** `08_Firmware_Prototipi/V7.3/duc_if2_causale_v73.py` mantiene storia per un Hilbert causale Blackman 257 tap e interpolazione sinc/Blackman 32 tap per fase 80×. Ingresso a 48kHz, uscita in array numerici a 3,84MSa/s, IF2=455kHz. USB/LSB con quadratura e LO alto, AM modulazione di ampiezza, FM integratore + NCO di fase continua, CW rampa 2ms. Funzionamento per blocchi di dimensioni differenti senza wrap periodico; quantizzazione solo numerica a 10 bit con overrange segnalato da eccezione. Nessun driver fisico o abilitazione TX.

**B. DAC candidato:** TI `DAC900E`, TSSOP-28, 10 bit, ingresso parallelo CMOS e uscita differenziale in corrente. Identificati da datasheet `SBAS093B` i 28 pin, inclusi D9..D0 ai pin1..10, CLK28, PD15 active-high, IOUT pin22 e complementare IOUTB pin21. `PD` dispone di pulldown interno: in un futuro circuito serve **pull-up hardware fail-closed** (R7401 10k *solo candidato DNP*) e ulteriori guasti da valutare. Alimentazioni e pin non cablati; tutta la distinta V7.3 da **12 voci DNP**, netlist concettuale da **42 righe DNP**, **nessuna uscita verso mixer o antenna**. Clock X7401 3.84MHz e bridge dati U7402 senza MPN né pinout fisico definiti.

Fonti vendor: https://www.ti.com/product/DAC900 e https://www.ti.com/lit/ds/symlink/dac900.pdf (Rev. B, p.4: pin; p.5: timing).

**C. F7401 LPF matematica:** reticolo 7 poli L-C-L-C-L-C-L Butterworth, (Z_0=50\Omega), (f_c=850\text{ kHz}); i valori, la formula S21/S11, il Q finite semplificato e i 400 scenari di tolleranza sono riproducibili in `03_Verifiche/V7.3/analizza_reconstruction_lpf_v73.py`. **Non è una LPF vendor né circuito IF realizzabile senza rete I/V/matching**; non filtrerebbe spur sotto cutoff e non sostituisce BPF selettivi.

## 2. Verifiche realmente eseguite

| Test / calcolo | RISULTATO | Significato e limite |
|---|---|---|
| V7.3 unit test GitHub Actions | **15 PASS / 0 FAIL / 0 SKIP** | DSP a stato, continuità a blocchi spezzati, inizializzazione a zeri, AM/FM/SSB/CW, overrange, DNP, formato pin e modello LC |
| Regressioni software V7.2 | **11 PASS / 0 FAIL / 0 SKIP** | Piano frequenze e modulazione offline precedentI |
| Regressioni software V7.1 | **8 PASS / 0 FAIL / 0 SKIP** | Mappatura storica TX interdetta, DNP e contratto bande |
| **Totale** | **34 PASS / 0 FAIL / 0 SKIP** | GitHub Actions run [42802528582](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42802528582), job 129783402835 (log esaminato) |
| Suddivisione dei blocchi USB/FM/AM | **PASS** | Stesso array campioni con alimentazione in segmenti diversi, in doppia precisione Python; non include DMA né clock fisico |
| USB/LSB due toni 750 e 1250Hz con IF2 reale | **PASS** | Test richiede soppressione indesiderata **migliore di 23dB** su coda coerente post-warmup, **non** misura di emissioni o garanzia su audio reale |
| Gate software | **256/256 False** | Nessuna combinazione di consensi permette un TX; in hardware non ancora verificato |
| BOM e pin | **12/12 DNP; 42/42 pin-rete DNP** | 28 pin U7401 tracciati da datasheet, 14 terminali passivi generici; nessun PCB |
| Modello ideale LPF | perdita max banda IF2 **0,001dB**, reiezione immagini DAC relativa min **84,019dB** | Solo 50Ω a componenti RLC ideali, NON misura hardware |
| Modello LPF QL=80/QC=500 | perdita max desiderata **0,174dB** | Resistenze parassite approssimate, non dati vendor |
| Monte Carlo deterministico 400 | perdita max desiderata **0,342dB**, immagine relativa min **82,494dB**, return loss min **24,353dB** | L ±5%, C ±2%, QL40..120, QC200..1000 **assunti**, nessuna SRF/accoppiamento/layout |

Gli stessi numeri dei test sono registrati in `03_Verifiche/V7.3/RISULTATI_VERIFICHE_V7.3.json`. Nessun risultato di simulazione software deve essere espresso come prova RF fisica.

## 3. Budget e criticità di progetto

- Passo campione IF2 **260,4167ns** nominali a 3,84MHz; dati grezzi di 10 bit equivalenti a **38,4Mbit/s** su bus parallelo, **non** implica che STM32G474 possa pilotarlo autonomamente. Servono bridge digitale/clock/DMA ancora da scegliere.
- DSP naïve: **122,88 MMAC/s** FIR interpolatore + **6,144 MMAC/s** Hilbert = **129,024 MMAC/s** senza NCO, controllo, overhead e I/O. Nessun benchmark realtime STM32; 512 audio campioni producono 40.960 numeri IF2, ~160KiB buffer float32 se interamente memorizzato.
- Ritardo FIR di progetto **143,5 campioni audio = 2,99ms**, oltre ad altre latenze non modellate. La quantizzazione 10 bit con 70% headroom è solo studio del range, non una prova di SFDR.
- Il TI DAC900E ha output **in corrente**, non tensione 50Ω: necessaria una nuova architettura I/V o rete balun, terminazioni, riferimento analogico, alimentazione e PD fail-closed testati. `F7401` non è collegata all'uscita DAC.
- Filtri L da ~16,87µH a frequenze MHz impongono verifica SRF/Q, MPN e layout. F7201/F7202 (V7.1), F7301 (V7.2), F7401 e clock X7401 restano **non selezionati per fabbricazione**.
- PLL termica V6.4, immagini RX V6.7, IF/AGC V6.8, LO2 V7.0, interblocchi V6.2 e isolamento RX/TX persistono. Il sistema completo **non è progettato né verificato integralmente**.

## 4. NON ESEGUITO (esplicitamente)

- Schema KiCad nativo di V7.3, ERC/DRC, PCB e stackup RF; CAD dei MPN e verifica DFM.
- Clock reale 3,84MHz, temporizzazione Setup/Hold, fattibilità MCU/FPGA, benchmark, uscita analogica DAC, noise/jitter, dati IBIS e modelli SPICE, taratura realistica, EMC e misure su prototipo.
- Qualifica indipendente fail-safe fisica, autorizzazione normativa, fabbricazione di PCB o **qualsiasi trasmissione RF**.

## 5. Decisione e prossima V7.4

**V7.3 è pronta come REVISIONE PROGETTUALE CANDIDATA, NON per uso in RF né per ordinare PCB.** Dopo merge in `main`, successiva **V7.4**: interfaccia digitale/clock reale in specifiche, stadio corrente→tensione filtrato a componenti candidati con pin verificati, studio alimentazioni/termica e soluzioni DUC più efficienti; continuare a preservare storico e verifiche incrementali, con **NO FAB / NO TX**.
