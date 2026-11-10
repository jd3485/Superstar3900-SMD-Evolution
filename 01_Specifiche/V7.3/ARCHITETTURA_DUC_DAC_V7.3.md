# Superstar 3900 SMD Evolution — V7.3 sorgente IF2 causale e DAC candidato

**10 novembre 2026 · proposta documentale + software offline · NO FAB / NO TX.**
Overlay V7.2, senza toccare i sorgenti storici. `main` V7.2 era la baseline verificata alla partenza. La catena di emissione resta fisicamente assente: U7201/U7202, F7201/F7202 e R7201–R7205 V7.1 **DNP**; U7301 e R7301–R7303 V7.2 **DNP**; uscita RF del mixer TX **non instradata**. V7.3 aggiunge **solo opzioni candidate DNP**.

## 1. Blocco digitale V7.3 realmente implementato (solo modello)

`08_Firmware_Prototipi/V7.3/duc_if2_causale_v73.py` implementa `CausalIF2` con memoria di stato fra blocchi di lunghezza arbitraria (max 512 input per chiamata). Processa audio a 48k campioni/s e restituisce **array numerici** IF2 a 3,84 milioni di campioni/s tramite interpolazione 80×. Nessuna libreria HAL, SPI, DMA, accesso GPIO, DAC reale, I/O seriale, RF/antenna o alimentazione.

- Hilbert **FIR 257 tap Blackman causale**, un ramo ritardato di 128 campioni allineato alla parte in quadratura. USB RF richiede IF2 inferiore (`real − j Hilbert`); LSB RF richiede IF2 superiore (`real + j Hilbert`) a causa di LO1 alto V7.1.
- Interpolatore **FIR 32 tap per fase**, coefficienti sinc+Blackman a 80 fasi, soltanto campioni passati, ritardo di 15,5 campioni audio. Ritardo del segnale audio approssimato: **143,5 campioni a 48k = 2,99 ms**, esclusa latenza di scheduling/DAC.
- NCO 455.000 Hz con fase persistente, FM con integrazione trapezoidale persistente e deviazione IF2 **negativa**, AM portante+audio con margine da definire, CW 454.300 Hz con rampe `sin²` 2 ms e fase persistente.
- `quantize_unsigned_10bit` produce **solo codici interi 0..1023**; guadagno `headroom=0.70` candidato, **overrange produce eccezione e NON clipping silenzioso**. Non scrive bit su un bus.
- `tx_permission(**flags) -> False` sempre; costanti `DAC_MOUNTED`, `IF2_CONNECTED_TO_MIXER`, `TX_RF_ENABLED`, `PA_CONNECTED` tutte `False`. Non basta cambiare un'istanza software per creare l'uscita RF fisica.

Nota: la risposta del nuovo Hilbert non è identica alla V7.2, che usava blocchi **circolari/periodici**. Ora il flusso conserva il passato fra blocchi e non importa campioni futuri; il transitorio iniziale è reale nel modello e le prestazioni vanno misurate su campioni utili dopo il warm-up. Rimangono da definire gestione overflow numerico reale, Q-format, fixed point, tempo di calcolo e filtri d'ingresso.

## 2. DAC U7401 candidato con pin fisici **verificati sul datasheet**

**Texas Instruments DAC900E** (10 bit, TSSOP-28, parallelo CMOS, uscita differenziale *in corrente*, 2–20mA regolabili). TI indica DAC900 **ACTIVE** e dati prestazionali pubblicati a condizioni di test diverse da 3,84MSa/s: **non** assegnare tali SFDR al nostro sistema. Alimentazione nominale candidata 3,3V nei limiti 2,7–5,5V, senza rail disegnato/validato. La versione DAC900E è indicata nel datasheet SBAS093B; disponibilità in acquisto e package footprint non convalidati.

Pin `1..10`: **D9, D8, D7, D6, D5, D4, D3, D2, D1, D0** (ingressi paralleli); `11..14` NC, `15` **PD active-high**, `16` INT/EXT (0 riferimento interno), `17` REFIN, `18` FSA, `19` BW, `20` AGND, `21` IOUTB complementare, `22` IOUT, `23` BYP, `24` +VA, `25` NC, `26` DGND, `27` +VD, `28` CLK. Verificare prima della conversione a KiCad nella fonte originale, non utilizzare una libreria arbitraria. Per `PD` il produttore segnala un **pulldown interno** che NON garantisce power-down fail-closed: **R7401 10k pull-up a +VD** è una **ECO da progettare** per mantenere PD alta in futura scheda; non è un interblocco validato. Tutti i pin sono su **reti soltanto concettuali e DNP**, con `IOUT/IOUTB` esplicitamente non instradati. R7402 2k FSA (~19,84mA nominali da 1,24V/2k ×32, approssimazione da qualificare), condensatori di bypass e R7403 aperto non costituiscono circuito già realizzato.

**Fonte primaria:** https://www.ti.com/product/DAC900 — datasheet Rev.B `SBAS093B` https://www.ti.com/lit/ds/symlink/dac900.pdf, tabella pin p.4 (indice PDF 3), timing p.5 (indice PDF 4). Latch CLK con setup **1,5ns minimo** e hold **1ns minimo** da verificare elettricamente. Potenza DAC tipica 170mW riferita ai test del fornitore a 5V, **non** budget 3,3V verificato. Nessun layout/IBIS/EMC eseguito.

**Dipendenze BLOCCANTI:** `U7402` bridge/FPGA per 10 bit paralleli a 3,84MHz (flusso dati grezzo **38,4Mbit/s**, senza overhead), `X7401` clock di 3,840000MHz con jitter e sincronizzazione audio da selezionare; pin di STM32G474 **non assegnati**. L'oscillatore non può essere presunto derivato dal TCXO 12,8MHz V6.4: rapporto 3/10 matematico non equivale a profilo PLL o clock implementato. Il DAC900 corrente-output richiede **rete I/V o trasformatore/terminazione** da selezionare: vietato connettere direttamente una LPF modello 50Ω a IOUT.

## 3. F7401 filtro ricostruzione — LC 7 poli ***solo matematico***

Nuovo candidato **passabasso di ricostruzione**, *non* BPF stretto 455kHz. Reticolo 50Ω ideale Butterworth a `f_c=850 kHz`:

| Elemento (serie/shunt alternato) | Valore nominale matematico |
|---|---:|
| L1 e L7 serie | 4,1665 µH |
| C2 e C6 shunt | 4,6697 nF |
| L3 e L5 serie | 16,8698 µH |
| C4 shunt | 7,4896 nF |

`03_Verifiche/V7.3/analizza_reconstruction_lpf_v73.py` costruisce la matrice ABCD con generator/load 50Ω e induttori Q finite, capacità con ESR, poi valuta 400 scenari deterministici con L ±5%, C ±2%, QL 40–120, QC 200–1000. **Risultati dal modello GitHub Actions**: perdita massima nominale desiderata a 455±2,7kHz **0,001dB**, attenuazione relativa nominale delle immagini DAC 3,385/4,295MHz **84,019dB**; QL80/QC500 perdita max **0,174dB**. Negli scenari stocastici: perdita peggiore **0,342dB**, attenuazione relativa minima delle immagini **82,494dB**, return loss minimo **24,353dB**. Tutti numeri **ipotetici da RLC nominale**: non includono capacità parassite, self-resonance, ESR frequency-dependent, vicinanza induttori, ground return, intermodulazioni o prova di fabbricabilità. Induttori ~16,87µH a MHz impongono **controllo obbligatorio SRF e Q dei componenti MPN**; nessun componente F7401 pronto per PCB.

**IMPORTANTE:** il reticolo è calcolato fra due porte **50Ω** che attualmente NON esistono. IOUT del DAC900 non è una sorgente a tensione 50Ω; mancando I/V, adattamento e protezioni analogiche, **non si può dedurre la soppressione delle immagini DAC fisiche da questi risultati**. La LPF non blocca spur basse e non sostituisce il selettore IF e il F7201 a 10,695 MHz.

## 4. Risorse / gate / rapporto

Budget aritmetico diretto non ottimizzato: FIR interpolatore `3,84M×32 = 122,88 milioni MAC/s`; Hilbert `48k×128 = 6,144 milioni MAC/s`; totale **129,024 milioni MAC/s**, esclusi NCO, FM, memoria e interfaccia. **NON** verificata esecuzione realtime STM32G474; serve algoritmo più efficiente (ad es. DUC multi-stadio / NCO FPGA) e tempo massimo misurato. Output 512 campioni audio produce 40.960 campioni numerici IF2, con buffer float32 di ~160KiB *per una sola forma d'onda*.

Verifiche nuove: 15 test V7.3 + regressioni 11 V7.2 + 8 V7.1 in CI, 270 canali storici e 256 combinazioni fail-closed. Vedi `03_Verifiche/V7.3/RAPPORTO_TECNICO_V7.3.md`.

**NON ESEGUITO:** clock hardware, verifica jitter, GPIO/DMA timing, alimentazione DAC, protezione reset/PD indipendente, filtri analogici con MPN, SPICE/IBIS, KiCad ERC/DRC, EM/DFM, VNA/spettro fisico, hardware e conformità normativa. **NO FAB / NO TX**.

## 5. Prossima revisione proposta V7.4

Sviluppare realmente architettura di controllo dati/clock e I/V con MPN candidati, riconciliare alimentazioni e GPIO con V6.1/V6.3, e migliorare efficienza DSP / prove di blocchi audio non periodici. Tenere isolato e non popolato l'intero TX RF.
