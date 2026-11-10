# Superstar 3900 SMD Evolution — V7.6 RTL, pin-plan e protezioni (SOLO STUDIO)

**10 novembre 2026. Baseline: V7.5 su main, commit dfa5e427. NO FAB / NO TX.** Nessuna trasmissione, nessun PA/antenna, DAC900E, oscillatore o FPGA realmente montati. Tutti i ponti V7.1–V7.5 restano DNP/aperti. La V7.6 aggiunge **RTL simulabile, mappatura candidata e misure numeriche**; non è una PCB pronta.

## 1. Primo modulo RTL realmente compilabile (senza pin elettrici)

Sorgente: `08_Firmware_Prototipi/V7.6/rtl/clock_fifo_virtual_v76.v`.
- `v76_clock_ce`: dominio clock **matematico da 30,72MHz**; pulsi `dac_sample_ce` ogni 8 fronti e `audio_ce` ogni 640 fronti, **80 eventi DAC per evento audio**. Sono *clock-enable*, **NON un'onda DAC di 3,84MHz**, né fronti DAC con dati stabilizzati. Uscita TX forzata a 0.
- `v76_virtual_fifo_guard`: FIFO **simulata** 16 parole ×10bit, con contatori read/write e flag. Riceve input astratti `rail_ok, config_ok, external_clock_monitor_ok, independent_supervisor_ok, independent_pd_guard_ok`. L'errore di underflow/overflow o di consenso blocca `fault_latched` e svuota la coda; non viene ripristinato senza reset di simulazione. `dac_pd_released=0` e `analog_path_connected=0` sono OUTPUT COSTANTI di simulazione, **non pin fisici**.
- L'interfaccia RTL **NON** invia bit a un DAC900 né contiene un TOP sintetizzabile per FPGA con pad/constrains. Non comprende un vero generatore d'onda DAC, setup/hold a livello fisico, metastabilità, CDC asincrono, jitter, POR né un sistema fault monitor se l'oscillatore master cessa di commutare (una logica tutta sincrona non vede l'arresto del proprio clock). L'ingresso `external_clock_monitor_ok` presume un supervisore ESTERNO che non è stato progettato.
- La FIFO da 16 parole dura **4,167 µs** a 3,84Msps e **non** è sufficiente come memoria di streaming per blocchi da 512 campioni audio. Dimostra solo la logica di controllo, non la RAM/throughput dell'FPGA.
- Testbench `03_Verifiche/V7.6/tb_clock_fifo_virtual_v76.v`, compilato con `iverilog -g2012`, eseguito da `vvp`, verifica 1280 tick master = 160 strobi DAC e 2 audio, allineamento, ordine FIFO e fault latched su underflow, overflow, disabilitazione guard e clock-monitor astratto. La simulazione accelera il clock: conta fronti, **non misura timing reale 30,72MHz**.

## 2. Inventario SG48 e vincoli PCF PROPOSTI — HOLD

I due file `01_Specifiche/V7.6/SG48_PIN_PLAN_CANDIDATE_V7.6.csv` (48 pin perimetrali **DNP** + paddle massa **DNP**) e `FPGA_PINS_PROPOSTI_V7.6.pcf` (vincoli di un *futuro* modulo di interfaccia, NON del TOP RTL corrente) documentano una possibile distribuzione delle risorse del candidato Lattice `iCE40UP5K-SG48I`. I numeri di pin derivano da una **riproduzione secondaria pubblica del file pinout Lattice**:
https://git.threefortiethofonehamster.com/kelvin/bldc-driver/src/branch/master/pcb/ice40up5k_pinout.csv
incrociata con lo schema `ICE40UP5K-SG48ITR` in un progetto pubblico https://github.com/ranveerlabs/morphcpu/blob/main/hardware/DESIGN.md. **La verifica diretta contro il foglio ufficiale iCE40UP5K Pinout XLSX di Lattice (document_id=51971) NON È STATA ESEGUITA. Ogni assegnazione PCF è quindi HOLD, non approvata per PCB o programmazione.**

La fonte PRIMARIA Lattice `FPGA-DS-02008-2.4`, sezione 5.2 p.42, https://www.latticesemi.com/api/document/download?id=51968, conferma il **conteggio** SG48: **39 I/O generali (17 banca 0, 14 banca 1, 8 banca 2)**, 2 VCC, 3 VCCIO, VCCPLL e VPP_2V5 separati, due dedicated config pin, e **nessun pin GND dedicato**: è obbligatorio collegare a massa il **paddle esposto**, che non è uno dei 48 pin perimetrali. Gli RGB0/RGB1/RGB2 (39–41 nella riproduzione secondaria) sono open-drain speciali e NON trattati come GPIO push-pull; SPI config pin14–17 non vengono usati come dati.
- Proposta MASTER_CLK ingresso globale **pin35 IOT_46b_G0**.
- Proposta DAC_WORD virtuale a 10 bit: pin **23,25,26,27,28,31,32,34,36,38**, OUTPUT *non cablati*, più futuro DAC_CLOCK virtuale pin42.
- Proposta INPUT FIFO 10 bit: pin **6,9,10,11,12,13,18,19,20,21**; sorgente valida pin2. Nessuna definizione del protocollo tra STM32G474 e FPGA, carico, setup/hold o timing closure.
- Porti di debug/condizioni proposti sui pin 3,4,43,44. Nessun pin analogico, PD, PTT o RF è assegnato.
- Il file PCF è una **bozza di vincoli con nomi di porta futuri**, NON un file validato con nextpnr, Yosys, Radiant o iCEcube2; il suo semplice parsing non prova che le risorse siano compatibili o che l'FPGA possa funzionare.
- U7601 e tutte le nuove connessioni V7.6 restano **DNP**, non progettare power pad e reti sul PCB basandosi su questa mappa.

## 3. Sequenza alimentazioni FPGA e protezione DAC

Fonte primaria Lattice `FPGA-DS-02008-2.4`, sezioni 4.4–4.6 p.30, ordina il power-up:
**VCC/VCCPLL (core ~1,2V) → SPI_VCCIO1 → VPP_2V5 → VCCIO0/VCCIO2** (al raggiungimento di soglie intermedie specificate); tutte le alimentazioni restano da definire e non c'è POR indipendente validato. Durante configurazione i pin user sono tri-state e richiedono analisi di pull-up/-down e feedthrough. CRESET_B e CDONE non sono sostituti di un supervisore analogico indipendente del DAC.

**Pericolo concreto:** TI DAC900 PD pin15 è active-HIGH con pull-down interno, quindi *floating* equivale a possibile uscita attiva; l'oscillatore Abracon ASDMB STANDBY pin1 è active-LOW, floating equivale a possibile oscillazione abilitata. Non c'è circuito fisico che garantisca DAC spento in assenza di alimentazioni o durante configurazione FPGA. La V7.6 rappresenta `independent_pd_guard_ok` come un **input ideale**, non una protezione. Gli eventuali guasti `PD_STUCK_LOW`, `SUPERVISOR_OUTPUT_OPEN`, `CLOCK_STOPPED`, `DAC_IOUT_SHORT`, `PA_RELAY_SHORT` richiedono gate fisici indipendenti e analisi single-fault, non soltanto logica Verilog.

La scheda futura deve mantenere un **punto di interruzione hardware fisico normalmente aperto** verso qualsiasi mixer RF/PA/antenna e impedire alimentazione DAC non qualificata. Nessun criterio di fabbricazione è stato raggiunto. BOM V7.6 5 elementi virtuali DNP, netlist 8 terminali tutti **OPEN/DNP**, R7701 link clock e R7702 confine digitale soltanto concettuale (NON 10 connessioni vere).

## 4. Spettro numerico più realistico (non performance RF)

`03_Verifiche/V7.6/analizza_multitono_transienti_v76.py` valuta la FIR V7.5 con **due toni coerenti 750Hz/1250Hz** (0,35 + 0,24 di ampiezza) e un **gradino 0 → 0,4 → 0** usando stati causali; risultati dal solo Python a 3,84Msps:
- Tono desiderato 750Hz e 1250Hz verificato entro ±0,01 di ampiezza; le immagini digitali 48k/240k/960k sono testate soltanto contro una soglia numerica generica di −65dB rispetto ai propri toni, **non una emission mask**.
- Gradino 0→0,4: picco **~0,45682** (overshoot **~14,2% rispetto a 0,4**), assestamento a ~0,4; dopo transitorio di discesa torna a zero nel modello. Il picco evidenzia la necessità di dimensionare l'headroom e gestire transitori prima di ogni DAC.
- **Non comprende** DAC quantizzato 10-bit, filtro F7401, tempo di clock/jitter, mixer IF2, SSB/AМ/FM reale, PA, PCB o radiazione.

È possibile che la V7.5 produca images molto basse con toni coerenti, ma su voce reale/rumore/transitori non è ancora fatta una verifica di mask o di distorsione. Non presentare i valori come livelli garantiti in dBc sull'antenna.

## 5. Stato verifiche e prossima revisione

Verifiche: Icarus Verilog **simulazione RTL funzionale** e test Python su mappa pin/PCF e spettro, più regressioni V7.1–V7.5. Il rapporto `03_Verifiche/V7.6/RAPPORTO_TECNICO_V7.6.md` deve riportare i log/risultati reali.

**NON ESEGUITI:** verifica contro XLSX vendor originale, top-level sintetizzato, Yosys/nextpnr placement/timing, pin I/O electrical bank/ramp, data source STM32, POR/PD hardwired, KiCad/ERC/DRC, SPICE vendor/EMI/EMC, VNA, misure RF/audio, fabbricazione e trasmissione.

**Prossima V7.7:** completare verifica della mappa con il foglio vendor originale, integrare top FPGA simulabile con clock DAC effettivo e timing closure, CDC/guard su clock esterno indipendente, progetto supervisor PD fail-closed a componenti fisici, reiezione multitonale/transitorio dopo DAC quantizzato e filtro analogico con dati SRF/Q verificati. **NO FAB / NO TX.**
