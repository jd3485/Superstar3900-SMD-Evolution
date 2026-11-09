# Superstar 3900 SMD Evolution — Rapporto tecnico V6.8

**9 novembre 2026 | Modulo FI1 10,695 MHz, AGC e architettura FI2 455 kHz. STUDIO RX, NO FAB / NO TX.**

## Progettazione nuova

- U801 **Analog Devices AD8338** su 3V3_A_IF_SW: VGA differenziale 0–80dB, 18MHz (datasheet, NON banda passante garantita per tutti i guadagni a 10,695MHz); pinout LFCSP16 da Rev.C documentato in `01_Specifiche/V6.8/NETLIST_PIN_FI_AGC_V6.8.csv`. **MODE pin6 massa**, GAIN pin7 unito DETO pin8, C803 1uF a massa; VREF interno pin16, R802 100kΩ + R803 680kΩ verso terra impostano VAGC pin13 ≈1.307692V, target RMS teorico 0.192308V. VREF NON pilotato dall'esterno.
- Il primo mixer U501 ADE-1+ della V6.5 alimenta terminazione R801 49,9Ω e U801 via condensatore; uscita differenziale da adattare prima di roofing e secondo mixer. Il livello in ingresso e il comportamento con blocker non sono qualificati.
- Due risonatori FI1 **1µH + 180pF + trimmer circa 41.45pF** e R=3,3kΩ sono candidati di STUDIO. A Q intrinseco 80 e buffer ideali **ancora non selezionati**, il Q caricato è 30.43 e larghezza teorica circa 351kHz. Attenuazione normalizzata FI2 immagine 9,785MHz solo **29.65 dB**; stadio aggiuntivo/ritaratura necessari se i requisiti di sistema lo impongono.
- U802 ADE-1+ candidato secondo mixer, LO2 programmabile ~10,240MHz con +7dBm richiesti non realizzati, e FI2 455kHz. F821 **Murata SFPKA455KFA4-R1** e F822 **SFPKA455KHA1-R1** (catalogo Murata novembre 2011: ±6 e ±3 kHz *minime a -6dB*, impedenze 1,5kΩ e 2kΩ, perdite massime 6dB). Disponibilità e fattibilità SMD odierna NON verificate. F823 SSB e F824 CW sono **placeholder senza MPN**. Commutatori SW821/SW822, LO2, BFO e demodulatori ancora **DA PROGETTARE**.

## Correzione d'architettura per USB e LSB

Poiché LO1 è alto, USB RF passa in FI1 come **banda laterale inferiore** e LSB come superiore. Senza ritoccare il piano PLL integer-N LO1 dei 270 canali, adottiamo come ipotesi una seconda conversione selezionabile:

| Modalità | LO2 di studio | BFO di studio | Frequenza IF2 della banda utile |
|---|---:|---:|---|
| AM | 10,2400 MHz | non necessario | 455kHz ± modulazione |
| FM | 10,2400 MHz | non necessario | 455kHz ± modulazione |
| USB | 10,2385 MHz | 456,5kHz | 453,8–456,2kHz per audio 300–2700Hz |
| LSB | 10,2415 MHz | 453,5kHz | 453,8–456,2kHz per audio 300–2700Hz |
| CW | 10,2400 MHz | 455,7kHz | 455kHz → tono 700Hz |

**La sorgente LO2 e il BFO non sono realizzati**: questi sono contratti di frequenza. `02_Piano_Frequenze/V6.8/PIANO_270_X_5_IF2_V6.8.csv`: 1.350 righe su 270 posizioni e 5 modi. Il cambio di LO2 richiede blanking, lock e validazione hardware.

## Verifiche effettuate in chat

- **60/60 nuovi test V6.8**: pinout, netlist, configurazione AGC, LO2/BFO, coerenza 270×5, formula Q e verifiche interblocco fail-closed su 1.536 stati logici (6 modalità × 2^8), TX sempre FALSE.
- **11 suite selezionate, 471 test** dalla V5.9 alla V6.8 tutte PASS. Non significa che ogni test storico V1–V5.8 sia stato rieseguito.
- **12.000 campioni** su parametri di filtro arbitrari con Q intrinseco, carico, L e residuo taratura. Attenuazione relativa FI2 immagine nella famiglia esplorata: 23.58–35.13dB. Questi estremi NON sono tolleranze garantite di produzione.
- AGC: tempo nominale datasheet con CDETO 1µF ≈17.45ms; step ideale di +40dB ingresso da 50µV a 5mV RMS, guadagno teorico 71.70→31.70dB e avvicinamento a 1dB ≈64.4ms in un modello a un polo **non la risposta reale del chip**. Attenzione a saturazione durante il transitorio.
- Modelli passa-banda **Butterworth analitici** FI2: 12k FM, 6k AM, 2,7k SSB, 500Hz CW a -3dB nominali. I modelli non sono le specifiche delle componenti Murata né filtri SSB/CW reali. Le curve sono consegnate per ispezione.

## Controlli NON eseguiti / gate aperti

**KiCad ERC/DRC NOT RUN, ngspice NOT RUN, FFT/phase noise e filtro EM NON TESTED, nessuna qualifica hardware o permesso fabbricazione.** AD8338 gain/frequency e DC bias, AGC saturazione, VREF load, componenti trimmer/Q, alimentazione, matching 50Ω a 1,5–2kΩ, switch isolation, LO2 spur, filtro BFO, filtri SSB/CW a 455, demod AM/FM/SSB/CW, immagini di entrambe le conversioni e scelta MCU pin da completare. V6.7 image rejection conservativa 17,5dB resta criticità separata. **NO FAB, NO TX.**

## Sorgenti ufficiali

- https://www.analog.com/en/products/ad8338.html
- https://www.analog.com/media/en/technical-documentation/data-sheets/ad8338.pdf
- https://www.analog.com/en/resources/app-notes/an-1192.html
- https://www.murata.com/~/media/webrenewal/support/library/catalog/products/filter/cerafil/p05e.ashx
- https://www.minicircuits.com/pdfs/ADE-1%2B.pdf

**Prossima V6.9:** generatore LO2 e BFO, filtri SSB/CW realizzabili e scelta circuiti demod AM/FM/SSB/CW, con nuovi test. Progetto radio completo ancora in corso; revisioneremo l'intero sistema e useremo KiCad quando ultimato.
