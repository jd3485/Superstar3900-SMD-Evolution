# V5.9 — Architettura completa del Superstar 3900 SMD Evolution

**Fase di lavoro:** PROGETTAZIONE ITERATIVA DELLA RADIO COMPLETA. Non è un rilascio fabbricabile e non afferma che tutti i moduli siano già disegnati. Data: 9 novembre 2026.

## Metodo richiesto
La radio si costruisce progressivamente in molte revisioni cumulative: in ogni revisione si aggiungono *elementi funzionali e circuitali nuovi*, con schemi e componenti sempre più definiti. Si completa **prima** la progettazione generale, poi si eseguono una **revisione tecnica globale**, **simulazioni dei sottosistemi**, **KiCad ERC/DRC**, e infine **prototipi e misure**. Gli unit test software di ogni revisione garantiscono la coerenza interna dei documenti, **non simulano né convalidano** il comportamento RF.

## Separazione fisica dei sottosistemi
- RF RX: antenna -> relè antenna -> preselettori per A–F -> attenuatore / ADL5535 bypass -> ADE-1+ -> FI 10,695 MHz -> demodulatori AM/FM/USB/LSB/CW.
- FI e BFO: USB/LSB con filtro selettivo, FM/AM con eventuale FI 455 kHz **ancora da definire**. Un unico audio analogico selezionato alimenta ADC R del CODEC.
- Radio digitale: MCU STM32G474RE, PLL LMX2572 con riferimento RF dedicato, codec TLV320AIC3204, clock audio 12,288 MHz indipendente ma coerente all'interno dell'interfaccia codec/SAI.
- TX: ramo riservato MIC/ADC L -> DSP -> DAC R -> modulazione FI -> conversione -> driver -> PA -> passa-basso -> ATU/potenza/ROS -> commutazione antenna. Architettura da concretizzare prima di dimensionare la catena. **Tutti gli ingressi di enable hardware TX restano bloccati**.
- Audio: ADC L microfono sempre distinto da ADC R ricezione; DAC L programma / PA esterna, DAC R modulatore TX con mute hardware. PA è solo audio e inibisce tutta la RF.
- Servizi: rail 13,8 V protetta, 5 V, 3,3 V analogica/digitale/RF da dimensionare; misure, display, ATU, pannello vintage, sicurezza HW indipendente.

## Specifiche radio confermate
Bande A–F, 40 canali normali e 5 ALFA per banda, 270 RX; selettore ALFA fisico; CH9 = 27,065 MHz AM prioritario; AM/FM/USB/LSB e CW solo in ricezione di default; PA senza RF; VOX/Dual Watch/Roger Beep/Echo/CTCSS-DCS/DSP e strumenti ROS/PEP. Regole TX legate a normativa e omologazione, non dedotte dalla sola tabella frequenze.

## Progetto audio: scelta di sistema V5.9
Si preserva il contratto V2.1: MIC su ADC sinistro e audio RX su ADC destro, evitando il conflitto di allocazione FM/MIC dell'antico V2.0. Si aggiunge un **selettore analogico 5:1 candidato**, preferibilmente con buffer/antialias e gestione di offset, fra le cinque funzioni di demodulazione e ADC_R. Non è ancora scelto un integrato mux o il suo pinout. La richiesta di 5 sorgenti può essere implementata mediante mux 8:1 o struttura equivalente, da definire nella progettazione elettrica.

Il TLV320AIC3204 dispone di due ADC e due DAC; la struttura stereo è coerente col contratto audio, ma ogni assegnazione dei pin reali, dei registri e dell'analog front end richiede futuro schema dettagliato. Il suo DAC L alimenterà la catena speaker RX o PA attraverso commutazione e muting; il DAC R sarà dedicato alla modulazione *solo se* si superano tutte le future condizioni TX; default MUTE. Audio sampling candidato 48 kHz / 2 × 32 bit / 3,072 MHz BCLK, codec master BCLK/WCLK, STM32 slave. Questo non è firmware MCU funzionante.

**CH9** prevale sulla sorgente audio ricezione, salvo PA prioritaria; **Dual Watch** è commutazione RX temporizzata sullo stesso ricevitore, **non doppia ricezione simultanea**. Squelch/AGC e filtri CW/SSB sono ancora da progettare. **PA** deve avere selezione dell'altoparlante esterno, isolamento dall'uscita radio, anti-pop e protezione termica; in ogni condizione PA l'RF rimane disabilitata da controllo hardware indipendente.

## Contratto fra blocchi
`CONTRATTO_MODULI_V5.9.json` definisce 26 blocchi e 54 connessioni LOGICHE tipizzate, con direzione, modalità d'uso, segnali, ruolo e criticità di sicurezza. **NON è un pinout PCB, non è una netlist KiCad e non autorizza a fabbricare cablaggi.** Nelle revisioni successive ogni blocco deve avere circuito dettagliato, distinta, limiti elettrici e connettori fisici espliciti.

## Cose importanti ancora da progettare
- TX reale: modulazione AM/FM/SSB a FI, driver, finale, polarizzazioni, filtri armoniche, selezione potenza, misura PEP/ROS, sequenza sicura TX/RX.
- PLL: interfacce fisiche, filtro d'anello, spurie, alimentazione e riferimenti.
- RX FI/demodulazione: schema componenti reale, filtri disponibili, AGC/ANL/NB, lettura CTCSS/DCS.
- Audio: circuito mux, mute anti-pop, power amp, prese e polarizzazioni.
- MCU: matrice pin reali LQFP64, risorse DMA, I2C, SAI, GPIO, ADC e firmware embedded.
- Meccanica: posizioni e diametri manopole, dimensioni del contenitore, schermature, connettori.
- PCB: layout complessivo a moduli, ingombri, masse/crosstalk, dimensionamenti di corrente e fabbricabilità.

## Norme di conservazione e rilascio
Tutti gli originali V5.8 e precedenti restano conservati con SHA-256. Prototipi hardware validati: zero. ERC/DRC nativi: NON ESEGUITI. Nove gate di produzione V5.0: OPEN. Nessun gerber o via libera a TX/PCBWay. Il 37% è una stima storica documentale e non un avanzamento fisico misurato.

## Fonti ufficiali per i candidati
- TI LMX2572: https://www.ti.com/product/LMX2572
- TI TLV320AIC3204: https://www.ti.com/product/TLV320AIC3204
- ST STM32G474RE: https://www.st.com/en/microcontrollers-microprocessors/stm32g474re.html
- STM32G4 RM0440 SAI: https://www.st.com/resource/en/reference_manual/dm00355726.pdf
