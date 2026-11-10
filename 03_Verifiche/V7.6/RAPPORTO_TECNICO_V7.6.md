# Superstar 3900 SMD Evolution — RAPPORTO TECNICO V7.6

**10 novembre 2026 — REVISIONE PROGETTUALE SOFTWARE / RTL SIMULATO, NO FAB / NO TX.**
Base main V7.5 `dfa5e4274f588727cc14fca73464729a7d4c2803`. La V7.6 non abilita nessuna radio TX, non modifica alcuna interfaccia PA/antenna, e non approva un PCB.

## 1. Nuovi elaborati verificati

**RTL simulabile:** `08_Firmware_Prototipi/V7.6/rtl/clock_fifo_virtual_v76.v` aggiunge due moduli: divider di strobe 30,72MHz → pulse DAC /8 e audio /640 (rapporto 80); FIFO virtuale 10bit×16 con fault latched su underflow/overflow/mancanza flag rail/config/clock monitor/supervisore/guard PD. Le uscite `tx_rf_permission`, `dac_pd_released`, `analog_path_connected` sono `1'b0` costanti; **non sono pin elettrici**. Non crea né distribuisce clock DAC a un componente fisico; non esegue CDC, clock watchdog indipendente, power-up POR/PD né driver esterni.

**Testbench Icarus:** `03_Verifiche/V7.6/tb_clock_fifo_virtual_v76.v` prova 1280 fronti master → **160 strobi DAC + 2 audio**, ordine FIFO, perdita del dato, overflow, fault interblocco astratto, monitor clock input e persistenza del fault. Accelera la frequenza per la simulazione: la temporizzazione *fisica* del DAC900 non è verificata.

**Inventario pin FPGA:** `01_Specifiche/V7.6/SG48_PIN_PLAN_CANDIDATE_V7.6.csv` = 48 pin perimetrali + paddle massa = **49 righe DNP**, con banco e ruolo proposto; `01_Specifiche/V7.6/FPGA_PINS_PROPOSTI_V7.6.pcf` = **vincoli candidate/HOLD**, non compilati con place-route. Pinout numerico acquisito da una **copia secondaria** dello spreadsheet Lattice e incrociato con i conteggi ufficiali in Lattice FPGA-DS-02008-2.4 sezione 5.2 (39 GPIO: 17+14+8, 2 VCC, 3 VCCIO, VCCPLL, VPP, due config e **paddle GND essenziale**). **NON ESEGUITO** confronto con XLSX Lattice originale e pin symbol/package; la mappatura è esplicitamente **non approvata** per una scheda. Pins periferici RGB sono speciali open-drain; SPI config e rail non sono assegnati al bus. Nessuna pinmap dell'FPGA è stata fisicamente connessa al DAC o al circuito.

**Rischi di alimentazione:** requisiti Lattice 4.4/4.5 p.30 ordine VCC/VCCPLL → SPI_VCCIO1 → VPP_2V5 → VCCIO0/2. DAC900 PD (HIGH=OFF, pull-down interno) e oscillatore ASDMB STANDBY (LOW=OFF, aperto=ON) creano uno stato pericoloso senza supervisor indipendente. Il RTL non è una protezione fisica; tutta la catena TX resta DNP.

**Nuova simulazione DSP:** `03_Verifiche/V7.6/analizza_multitono_transienti_v76.py` esamina due toni coerenti **750Hz 0,35** + **1250Hz 0,24**, immagini numeriche 48/240/960kHz, e gradino **0→0,4→0** in FIR a tre stadi V7.5. Il picco del gradino risulta **0,4568205** contro 0,4 nominali (overshoot **14,205%**) nel solo modello; ciò richiede verificare headroom/limiter ma NON è un dato DAC/IF analogico.

**BOM/netlist:** `07_Componenti/BOM_SIMULAZIONE_RTL_V7.6.csv` contiene **5 elementi DNP** e `01_Specifiche/V7.6/NETLIST_VIRTUAL_IO_V7.6.csv` contiene **8 interfacce OPEN/DNP**. Il confine digitale è CONCETTUALE e non sostituisce 10 tracce DAC. Nessun mixer RF, PA o antenna collegati.

## 2. Test effettivamente eseguiti (GitHub Actions)

| Categoria | Esito | Limiti |
|---|---|---|
| Icarus Verilog bench V7.6 | **PASS**: compile + simulate, messaggio "PASS V7.6 RTL" su GitHub Actions | Non è synthesis, place/route, STA, netlist gate, proof formale o hardware |
| Nuovi test Python V7.6 | **15 PASS / 0 FAIL / 0 SKIP** | Pinmap candidata, CSV HOLD, regressione dati e spettro numerico |
| Regressione V7.5 | **22 PASS / 0 FAIL / 0 SKIP** | Clock/modelli DSP V7.5 |
| Regressione V7.4 | **21 PASS / 0 FAIL / 0 SKIP** | FIFO e I/V virtuali |
| Regressione V7.3 | **15 PASS / 0 FAIL / 0 SKIP** | DSP Hilbert e analogica matematica |
| Regressione V7.2 | **11 PASS / 0 FAIL / 0 SKIP** | DUC offline |
| Regressione V7.1 | **8 PASS / 0 FAIL / 0 SKIP** | TX modellata ma fisicamente interdetta |
| **TOTALE** | **92 Python PASS + 1 bench RTL PASS, 0 FAIL, 0 SKIP** | [GitHub Actions run 42814160564](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42814160564), job 129822843348, log ispezionato |
| 270 posizioni RX / 30 ALFA storico | **PASS CSV** | Non LO/PLL/sintonia/EM su hardware |

### Limiti della validazione spettrale

Le immagini della V7.6 non vengono interpretate come reiezioni misurate in banda RF: sono **coefficenti DFT coerenti di campioni numerici a 3,84MSa/s**, con due toni e stato FIR dopo warm-up in doppia precisione. Per ogni tono, le sei immagini attorno a 48k, 240k e 960k devono essere sotto **−65dB** rispetto al tono desiderato; i dati analogici DAC sample-hold, spuria di clock, jitter, filtro F7401, saturazione, DAC 10bit, PA e antenna **NON SIMULATI / NON MISURATI**. Il gradino presenta overshoot numerico: non autorizza trasmissione né certificazione.

## 3. Gate BLOCCANTI / NON ESEGUITI

- **Verifica indipendente** dei 48 pin su XLSX Lattice primario `iCE40UP5K Pinout` document_id=51971, verifica delle connessioni di bank, global clock e top FPGA.
- Synthesis/place-route e timing closure, generazione bitstream, mapping GPIO/IO standard, DAC parallel clock waveform e setup/hold fisico, gestione di CDC e clock-stop mediante monitor esterno.
- POR e controlli PD hardware indipendenti, alimentazioni 1,2/3,3V, power sequencing Lattice, backfeed/stuck-at, guasti single-fault; **NESSUN circuito supervisor realmente montato**.
- Rete IOUT/IOUTB, filtro F7401 con MPN Q/SRF vendor, simulazione circuitale e misura analogica; KiCad ERC/DRC, layout/PCB, EMC, lavoro al banco, test RX/TX su hardware, conformità e fabbricazione.

## 4. Verdetto e seguito

**V7.6 candidata software/documentale e integrabile in `main` a condizione che la CI finale della PR mantenga PASS.** Non è una scheda RF validata. **NO FAB / NO TX**.

**Prossima V7.7:** recuperare il file XLSX vendor originale dei pin e produrre un top FPGA compilabile con constraints verificate, testare clock output e gestione reset CDC, disegnare POR/PD indipendente con componenti fisici e isolamenti DNP, integrare quantizzazione a 10bit e controlli spettrali/transitori, selezionare filtro e componenti per dati SRF/Q documentati.

**Fonti tecniche:** Lattice https://www.latticesemi.com/api/document/download?id=51968 ; vendor pin XLSX https://www.latticesemi.com/view_document?document_id=51971 ; copia secondaria https://git.threefortiethofonehamster.com/kelvin/bldc-driver/src/branch/master/pcb/ice40up5k_pinout.csv ; progetto incrocio https://github.com/ranveerlabs/morphcpu/blob/main/hardware/DESIGN.md ; TI DAC900 https://www.ti.com/lit/ds/symlink/dac900.pdf .
