# Superstar 3900 SMD Evolution — V7.7: top RTL, Yosys e DAC 10 bit (SOLO OFFLINE)

**10 novembre 2026.** La V7.7 è una continuazione incrementale della V7.6 integrata in main. **NO FAB / NO TX.** FPGA Lattice iCE40UP5K-SG48I, DAC900E, oscillatore Abracon, ponti IF/RF, mixer TX, PA e antenna restano **DNP, non alimentati e non collegati**.

## 1. Vincolo pinout Lattice non risolto

Il produttore Lattice pubblica il foglio **iCE40UP5K Pinout v1.1 del 8 luglio 2017**, documento 51971, alla pagina https://www.latticesemi.com/Products/FPGAandCPLD/iCE40UltraPlus . È stato tentato il recupero dell'XLSX originale, ma in questa sessione il contenuto binario non era acquisibile (accesso non disponibile). **NON È STATO ESEGUITO** il confronto riga-per-riga con il file originale. Pertanto il file V7.6 `SG48_PIN_PLAN_CANDIDATE_V7.6.csv` e `FPGA_PINS_PROPOSTI_V7.6.pcf` rimangono **HOLD**; nessun pin FPGA viene certificato o trasferito a uno schema fisico. I soli conteggi confermati dal datasheet Lattice FPGA-DS-02008 Rev2.4 sono 39 I/O generici e massa sul paddle esposto, non la numerazione dei segnali.

Una verifica completa in V7.8 dovrà includere la copia vendor XLSX autenticata, i domini di banco e power sequencing, clock globale, pin di configurazione, PAD/paddle, DRC PCB, collegamenti a tutti i 10 bit DAC900 e vincoli I/O. La compilazione RTL senza pinmap **non** costituisce questa verifica.

## 2. Top RTL diagnostico e sintesi logica

File `08_Firmware_Prototipi/V7.7/rtl/top_virtuale_v77.v`, connettendo `v76_clock_ce` e `v76_virtual_fifo_guard`. Porte in ingresso: clock e reset **virtuali**, controlli simbolici di alimentazione/configurazione, watchdog clock **esterno ma non implementato**, supervisor indipendente **solamente ipotizzato**, guard PD **solamente ipotizzato**, dato FIFO 10bit e valid. Porte in uscita: codici campione diagnostici, sample strobe diagnostico, stato fault/FIFO, e tre permessi hardware **costanti zero**: `tx_rf_permission`, `dac_pd_released`, `analog_path_connected`. Nessuna uscita clock fisica, DAC seriale/parallelo, GPIO PA, PTT, mixer o antenna.

`03_Verifiche/V7.7/tb_top_virtuale_v77.v` è un testbench Icarus self-checking: dati FIFO diagnostici, perdita di consenso watchdog (espressa come bit di input), fault permanente, reset e underflow. La suite V7.6 su 1280 tick master verifica già i divisori /8 (3.84 MHz nominali) e /640 (48kHz nominali). I tempi del testbench sono accelerati: **non** misurano jitter, timing a 30.72MHz o setup/hold del DAC900.

`Yosys synth -top v77_offline_top; check -assert; stat` viene eseguito solo come **sintesi RTL logica generica, senza mapping specifico iCE40, pinout, PNR, STA, bitstream o oscillatore**. Non dimostra che l'implementazione stia nell'FPGA. Il top mantiene segnali di diagnostica in modo che i contatori/FIFO non siano tutti ottimizzati via hardware permission costante zero.

Il clock master fermo impedisce alla logica sincrona di rilevare l'arresto: il watchdog deve essere **un circuito indipendente con altro riferimento di tempo**, non un flag interno autogenerato dall'FPGA. Nessuna protezione esistente può abilitare TX.

## 3. Catena DSP / DAC a 10 bit NUMERICA

`08_Firmware_Prototipi/V7.7/quantizzazione_e_sicurezza_offline_v77.py` riutilizza l'interpolatore causale a 3 stadi V7.5 e il quantizzatore intero a 10bit V7.3. Per blocchi coerenti audio 48kHz e output matematico 3.84MSa/s:
- Due toni **750Hz 0.35** e **1250Hz 0.24** dopo warm-up; applicazione headroom **0.70** a un codice 0..1023, poi ricostruzione *matematica* e calcolo RMS errore e rapporto SNR di sola quantizzazione rispetto al segnale software. Il valore numerico non costituisce la SNR/SFDR del DAC900 elettrico.
- Gradino causale **0→0.4→0**, misurato sul FIR; controllo del picco e codici limitati 0..1023 senza silent clipping. I transienti nella V7.6 avevano overshoot 14.2%; il modello V7.7 conserva questa informazione ai fini dell'headroom.
- Non sono presenti **sample-and-hold**, analog IOUT/IOUTB, rumore di clock, BPF/LPF F7401, immagini DAC analogiche, modulazioni AM/FM/SSB RF complete, termica, emission mask o misure di laboratorio.

I test del modello verificano anche il mantenimento del piano 270 canali/30 ALFA e l'assenza di permessi TX.

## 4. FMEA: interblocchi necessari ma non realizzati

Il modello enumera guasti tra cui `DAC_PD_FLOATS_LOW`, `DAC_PD_STUCK_LOW`, `SUPERVISOR_OPEN`, `SUPERVISOR_SHORT`, `CLOCK_STOPS`, `FPGA_CONFIG_UNDEFINED`, `DAC_RAIL_BACKFEED`, `PA_ISOLATOR_WELDED` e `INDEPENDENT_CLOCK_WATCHDOG_FAILS`. Per ognuno è registrato **NOT_RUN** per qualifica hardware; la richiesta di un gate PD indipendente e **interruzione analogica normalmente aperta** è un requisito, non una realizzazione.

Il DAC900 PD pin15 è active-high con pulldown interno: floating implica stato di possibile attività. Oscillatore ASDMB STANDBY active-low è anch'esso sensibile a floating. I tre zeri costanti RTL **non** sostituiscono una protezione fisica sul bus alimentazioni, PA o antenna.

## 5. Distinta / netlist V7.7

`07_Componenti/BOM_TOP_VIRTUALE_V7.7.csv`: **8 elementi DNP e OPEN** (top FPGA virtuale, watchdog esterno non selezionato, supervisor non selezionato, RF isolator normalmente aperto solo requisito, header diagnostico virtuale, due ponti zero ohm aperti e un bypass placeholder).
`01_Specifiche/V7.7/NETLIST_VIRTUAL_DIAGNOSTICA_V7.7.csv`: **10 terminali**, tutti **DNP/OPEN**, nessun pin elettrico verificato; nessun componente MCU/DAC/FPGA montato. Non usare questo contratto per compilare una distinta acquisti o un CAD PCB.

## 6. Verifiche / blocchi

Workflow: `.github/workflows/v77_virtual_synthesis_quantization.yml`, con testbench Icarus V7.7 e V7.6, sintesi Yosys generica, test Python V7.7 e regressioni V7.1–V7.6. Esiti da estrarre dal log finale prima di unire PR.

**NON ESEGUITI:** verifica XLSX vendor primario Lattice, place-and-route nextpnr, STA, pin mapping fisico completo, fonte clock autonoma, fault injection power/PD, PCB KiCad/ERC/DRC, circuit simulation SPICE/IBIS, filtro Q/SRF con MPN qualificati, bench, EMC e radio TX. **NO FAB / NO TX**.

**Prossima V7.8:** verificare il foglio Lattice originale, fare un mapping di I/O con TOP compatibile e PNR/STA solo dopo validazione dei pin, studiare un vero supervisor indipendente hardware DNP con datasheet e risoluzione fault singoli, completare quantizzazione/spettro multitonale e filtri analogici con parametri realistici, senza alcuna connessione RF.
