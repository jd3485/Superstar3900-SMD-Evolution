# Superstar 3900 SMD Evolution — RAPPORTO TECNICO V7.7

**10 novembre 2026 · elaborazione digitale e RTL simulato/sintetizzato logicamente · NO FAB / NO TX.** Prosecuzione incrementale da V7.6 integrata su `main`. Nessun DAC900, oscillatore, FPGA, PA, mixer TX o antenna realmente alimentati/connessi. Tutte le nuove righe BOM e netlist DNP/open.

## 1. Risultati del lavoro V7.7

**Nuovo top RTL diagnostico:** `08_Firmware_Prototipi/V7.7/rtl/top_virtuale_v77.v` collega i due moduli V7.6: divisori di clock-enable /8 e /640 (nominali da 30,72MHz) e FIFO 16×10 bit con fault latched. I tre output `tx_rf_permission`, `dac_pd_released` e `analog_path_connected` sono **costanti zero**. L'uscita campioni è espressamente una **diagnostica virtuale**, non un bus fisico verso il DAC.

**Simulazione e sintesi logica:** self-checking testbench `03_Verifiche/V7.7/tb_top_virtuale_v77.v` con Icarus: FIFO diagnostica, monitor esterno rappresentato da flag, fault persistente e underflow. Verifica di `Yosys synth -top v77_offline_top; check -assert; stat` completata con successo sul checkout GitHub Actions. È una sintesi **generica**: NON è tecnologia iCE40 mapped, PNR, STA, verifica setup/hold, né un bitstream funzionante. Anche la regressione RTL Icarus V7.6 passa.

**Quantizzazione software DAC 10bit:** `08_Firmware_Prototipi/V7.7/quantizzazione_e_sicurezza_offline_v77.py` applica `quantize_unsigned_10bit` agli output del FIR multistadio V7.5: input due toni 750 e 1250Hz, ampiezze 0,35 e 0,24, finestra coerente da 8ms e headroom 70%; decodifica normalizzata e RMS errore. In questo solo modello in doppia precisione:
- **SNR numerica di quantizzazione: 51,470 dB**, RMS errore **0,0008012**;
- Codici minimo/massimo sul multitono: **300 e 723**, intervallo legale 0..1023;
- Gradino **0→0,4→0**: picco del FIR **0,456821**, overshoot **14,205%**, codice massimo **675**.
Non sono valori misurati di SFDR/SNR DAC900, PLL, filtro analogico o radiata. Il segnale è baseband numerico, **non** una forma d'onda TX RF.

**FMEA virtuale:** matrice nominale di 12 famiglie guasto incluso PD flottante/stuck-low, supervisor open/short, fermo clock, glitch, configurazione FPGA, backfeed rail, isolatore PA saldato e guasto al watchdog indipendente. Ogni famiglia richiede un **supervisore elettrico realmente indipendente e un'interruzione analogica normalmente aperta**, ma è marcata `NOT_RUN` per protezione fisica. Nessuna di queste condizioni è risolta da booleani HDL.

**Distinte:** BOM `07_Componenti/BOM_TOP_VIRTUALE_V7.7.csv` da **8 voci tutte DNP/OPEN** e netlist `01_Specifiche/V7.7/NETLIST_VIRTUAL_DIAGNOSTICA_V7.7.csv` con **10 terminali tutti DNP/OPEN**; i pin elettrici non sono documentati come verificati e nessuna uscita va a DAC/mixer/PA.

## 2. Verifiche realmente eseguite

| Gruppo | Esito verificato | Ambito |
|---|---|---|
| Icarus bench V7.7 top | **PASS** | Soltanto simulazione funzionale di dati diagnostici e fault |
| Yosys generic `synth` + `check -assert` | **PASS** | Sintesi logica generica senza floorplan, PNR, STA o device bitstream |
| Icarus bench V7.6 regressione | **PASS** | Divisori, FIFO e consensi costantemente zero |
| Nuovi Python V7.7 | **14 PASS / 0 FAIL / 0 SKIP** | Quantizzatore, inventario guasti, DNP, pinout HOLD |
| Regressioni Python V7.6 | **15 PASS** | Inventario SG48 e spettro digitale |
| Regressioni Python V7.5 | **22 PASS** | Clock sincronizzato e FIR multistadio |
| Regressioni Python V7.4 | **21 PASS** | Interfaccia FIFO DAC virtuale e I/V |
| Regressioni Python V7.3 | **15 PASS** | DSP IF2 causale |
| Regressioni Python V7.2 | **11 PASS** | DUC offline |
| Regressioni Python V7.1 | **8 PASS** | IF/TX modello inibito |
| **Totale Python** | **106 PASS / 0 FAIL / 0 SKIP** | [GitHub Actions run 42819963860](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42819963860), job **129842672029**, log verificato |
| 270/30 storico | **PASS** | CSV 270 posizioni, 30 ALFA, `tx_permitted=0` |

La stessa evidenza machine-readable è in `03_Verifiche/V7.7/RISULTATI_VERIFICHE_V7.7.json`; se verranno apportati commit ulteriori alla PR, verificare nuovamente la CI sul commit finale.

## 3. Limitazione del pinout SG48 (HOLD)

È stata identificata sul sito ufficiale Lattice la voce XLSX **iCE40UP5K Pinout v1.1 (document_id=51971)**, ma il contenuto non è stato acquisito in questa sessione; pertanto non è stato possibile confrontare i 48 numeri con l'originale. La mappatura di V7.6 da fonte secondaria e il PCF restano **HOLD**. È verificato soltanto il conteggio I/O/rail e il paddle GND dal datasheet primario FPGA-DS-02008-2.4, **non** l'assegnazione precisa dei segnali. La sintesi Yosys NON dà validazione al PCF.

Fonte ufficiale indice: https://www.latticesemi.com/Products/FPGAandCPLD/iCE40UltraPlus ; link vendor spreadsheet https://www.latticesemi.com/view_document?document_id=51971 .

## 4. Rischi bloccanti e non eseguiti

- **NON ESEGUITO:** verifica dell'XLSX Lattice e full pinmap con I/O bank, PNR/STA, implementazione fisica clock 3,84MHz e DAC900 setup/hold.
- **NON ESEGUITO:** supervisore indipendente POR/PD, watchdog di clock realmente autonomo, sequenze rail, fault injection single-fault, interruttore hardware fail-open.
- **NON ESEGUITO:** DSP realtime MCU/FPGA, qualità audio complessiva, DAC quantizzato fisico, quantizzazione su segnali non coerenti/rumore, anti-imaging F7401 con Q/SRF vendor.
- **NON ESEGUITO:** KiCad/ERC/DRC, SPICE analogico, prove termiche, EMI/EMC, prove RF, fabbricazione e qualsiasi trasmissione.

Il DAC900 PD pin15 è active-HIGH con pulldown interno, quindi una linea flottante può abilitarlo: **i valori costanti zero in RTL non sono una garanzia fisica**. Gli interblocchi V6.2 e l'intera catena TX devono essere verificati fuori dal modello prima di qualunque considerazione di montaggio.

## 5. Decisione

**V7.7 è integrabile come revisione progettuale software/documentale dopo la CI finale della PR. NON è pronta a schemi TX di produzione, fabbricazione o emissioni.** Lo storico `v7.0` resta immutato e lo stato attuale su `main` va sempre verificato prima di sviluppare altro.

**Prossima V7.8:** ottenere e incrociare l'XLSX ufficiale dei pin SG48, comporre un top con pin realmente autorizzati e verificare floorplan/STA soltanto a valle della qualificazione dei segnali; studiare supervisor indipendente hardware e filtri Q/SRF con modelli/datasheet; ampliamento di simulazioni DSP, sempre **NO FAB / NO TX**.
