# Superstar 3900 SMD Evolution — Rapporto tecnico V7.2

**10 novembre 2026 — overlay DUC/IF2 software sperimentale · NO FAB / NO TX.**

## Scopo e risultati di progetto
Aggiunto modello offline *multitono* per IF2 455kHz: ingresso audio 48kHz, interpolazione 80× a 3.84Msps con sinc finestrata 32-tap per fase, Hilbert circolare Blackman 257-tap, AM/FM/USB/LSB/CW. Corrispettivo concettuale di DAC U7301, filtro IF2 F7301, connettori J7301/J7302 e ponti R7301..R7303: **8 componenti candidati tutti DNP**, **12 voci pin-to-net concettuali tutte DNP**, **nessun pin DAC/filtro inventato**. I mixer TX V7.1 restano DNP e senza uscita RF instradata.

Riferimenti: `01_Specifiche/V7.2/ARCHITETTURA_DUC_IF2_V7.2.md`, `08_Firmware_Prototipi/V7.2/duc_if2_offline_v72.py`, `03_Verifiche/V7.2/analizza_filtri_v72.py`, `07_Componenti/BOM_DUC_IF2_V7.2.csv`, `01_Specifiche/V7.2/NETLIST_DUC_IF2_V7.2.csv`, `00_Gestione_Progetto/ECO_INTEGRAZIONE_V7.2.md`.

## Verifiche effettivamente eseguite, differenziate

| Verifica | Esito / metodo | Limiti |
|---|---|---|
| Modello e test Python stdlib eseguiti sul sottoinsieme di sviluppo locale | **10 PASS / 0 FAIL**; modulazioni, Hilbert, AM/FM, CW, Nyquist, interpolazione, DNP/plan e gate 128 stati | Nel controllo locale il CSV piano 270 è stato ricreato come fixture equivalente per la verifica strutturale; il confronto autentico con il repository viene eseguito dalla CI |
| Verifica spettro con due toni periodici 750/1250 Hz a 48kHz, blocco 384 campioni, 3.84Msps | **PASS nel modello locale**: USB e LSB, banda laterale indesiderata rispetto alla desiderata **−75.29 dBc (750 Hz)** e **−93.63 dBc (1250 Hz)** | Solo toni coerenti con blocco di 8ms, Hilbert non causale/circolare e aritmetica in doppia precisione. Non garantisce gli stessi risultati su parlato, transitori, fixed-point o DAC |
| Modulazione AM multitono `μ=0.35` | **PASS**: portante ed entrambe le bande laterali al livello atteso `μ·ampiezza_tono/2` entro 0.012 (ampiezza normalizzata) | Non comprende mixer, compressore o saturazione fisici |
| Segno FM e CW | **PASS**: DC audio +0.2 con Δf 2500Hz produce spostamento IF2 −500Hz nel modello; CW disattivato interamente nullo e key-on con rampa sin² 2ms | Non prova occupazione spettrale di un keyer reale |
| Logica software TX | **PASS**: 128/128 stati di controllo producono `False`; assenza di DAC e di percorso RF codificata | Non misura affidabilità fisica di interblocchi V6.2, tuttora incompleti |
| Studio ideale filtri | **PASS calcolo locale di riferimento**: F7201 Butterworth BPF proxy ordine 2, 10.685–10.705 MHz, perdita ideale a spur 9.785MHz **79.151dB**; F7202 proxy ordine 5, 25–29MHz, perdita ideale al bordo del primo canale **0.081dB** | Curve matematiche LOSSLESS, senza Q, accoppiamenti, parassiti, tolleranze, potenza, layout o MPN |
| Scansione ideale di tutte le 270 posizioni | **PASS (CI)** sul CSV V6.4 autentico: 270/270 e 30 ALFA; reiezione relativa minima immagine RF **89.66dB**, LO1 **61.05dB**, perdita massima nominale **0.082dB** | Numeri matematici Butterworth ideali, **NON misurati** né garantiti da filtri reali |
| Test GitHub Actions su checkout integrale | **PASS V7.2 11/11 + regressione V7.1 8/8 = 19/19**, 0 skip e 0 fail; run [42794362886](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42794362886), job 129755581831, log verificato | Solo software/CSV, non KiCad, SPICE, hardware o trasmissione |
| KiCad schematico, ERC/DRC, CAD PCB, ngspice analogico, RF S-parameter, EMC, TX emissioni, firmware STM32, hardware | **NON ESEGUITI** | Nessuna qualifica fabbricazione, emissione o sicurezza |

## Rischi aperti
1. Campioni software **non** collegati a DAC/driver fisico: U7301, F7301 senza MPN, pinout, attenuazione o specifiche validate; 3.84MSa/s e relativo clock non disponibili né provati su STM32G474; FIR interpolante ingenua circa **122.88 MMAC/s** e memoria buffer per 384 campioni audio: 30.720 campioni IF2, ~60 KiB Q16 o ~120 KiB float32 per un solo canale.
2. **Hilbert circolare non causale** applica l'effetto ideale ad audio periodico; su voce occorrono Hilbert causale/stateful, protezioni overflow, filtro audio di ingresso, gestione audio a blocchi e verifica riduzione banda laterale su transitori.
3. Filtri F7301/F7201/F7202 non realizzati, né esiste prova di soppressione immagini DAC, RF sum 47–50MHz, feedthrough LO1 o emission mask; le curve Butterworth sono solamente un limite teorico.
4. I precedenti problemi V6.2 interlock, V6.4 termica/PLL, V6.7 RX immagine, V7.0 LO2 analogico/filtri e V7.1 uscita RF aperta permangono. Non usare F501 RX come filtro TX.
5. Nessuna procedura di montaggio/trasmissione abilitata: **NO FAB / NO TX**.

## Prossima V7.3 candidata
Specificare vero DAC/clock e filtro ricostruzione 455kHz con MPN e pin fisici documentati; completare modulator streaming multitonale con filtri causali e misure di spettro offline a voce/transitori; verificare la fattibilità computazionale e di alimentazione, **senza collegare TX RF o finale**.

**Verdetto: V7.2 candidato software/documentale, non una trasmittente operativa, non fabbricabile.**
