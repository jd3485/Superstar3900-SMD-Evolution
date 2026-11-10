# Superstar 3900 SMD Evolution — ARCHITETTURA V7.8

**10 novembre 2026. Evoluzione da main V7.7 `607dd957`. SOLO MODELLI, NO FAB / NO TX.** La radio non possiede un percorso TX popolato o alimentato: mixer U7201/U7202, DAC900E U7401, FPGA U7601, clock, interruttori, PA e antenna restano DNP/OPEN. Non sono stati realizzati PCB, KiCad ERC/DRC, oscillatori fisici o trasmissioni.

## 1. Problema di sicurezza risolto solo in SIMULAZIONE

In V7.7 il master clock 30,72MHz era controllato da logica sincrona **alimentata da quel medesimo master**; quindi un arresto del clock impedisce la rilevazione. In V7.8 `08_Firmware_Prototipi/V7.8/rtl/clock_watchdog_indipendente_v78.v` presenta **due domini di clock simulati**:
- `v78_master_heartbeat` emette un bit di heartbeat alternando ogni 8 fronti master;
- `v78_independent_ref_monitor` campiona il bit su un secondo clock, con sincronizzatore a 3 FF etichettato `async_reg`, attende almeno due transizioni e registra un **fault latched** se mancano fronti per 40 tick del riferimento nel modello;
- `v78_offline_dual_domain_top` collega i due blocchi ma mantiene **`dac_pd_released=0`, `tx_rf_permission=0`, `analog_path_connected=0`** in tutte le circostanze.

La simulazione (testbench `03_Verifiche/V7.8/tb_clock_watchdog_v78.v`) contiene due generatori di clock virtuali separati. Arrestando **solo** il master, il riferimento indipendente continua a commutare e deve rilevare l'assenza di heartbeat; un recupero del clock master non deve cancellare il fault senza reset. **I parametri di simulazione non sono frequenze/tempi della futura scheda**: master e riferimento sono accelerati; nessun clock elettrico è stato selezionato per il riferimento indipendente. La verifica di metastabilità e MTBF, CDC, guasti alla seconda sorgente e reset domain crossing rimane **NON ESEGUITA**.

**Condizioni bloccanti per un qualunque circuito fisico:** un watchdog che usa lo stesso rail/master, un riferimento bloccato, reset comune che cancella fault e linee PD senza bias non garantiscono sicurezza. Necessario un interblocco fisico indipendente con definizione dello stato su perdita di una o di entrambe le alimentazioni, *brownout*, backfeed e guasti singoli; la logica RTL non guida pin reali e non realizza quell'interblocco.

## 2. Analisi vendor SG48: qualificazione HOLD automatizzata

Il file Lattice originale `iCE40UP5K Pinout` v1.1 (8 luglio 2017), **document_id=51971**, è indicato dal produttore in https://www.latticesemi.com/Products/FPGAandCPLD/iCE40UltraPlus . Download diretto provato da `view_document?document_id=51971` e API document 51971: il file XLSX **non era acquisibile in questa sessione**. Di conseguenza, la tabella V7.6 `SG48_PIN_PLAN_CANDIDATE_V7.6.csv` e `FPGA_PINS_PROPOSTI_V7.6.pcf` restano **HOLD**. Il datasheet ufficiale Lattice FPGA-DS-02008 Rev2.4 conferma i 39 I/O e il pad di massa esposto, **non** i 48 numeri della nostra candidata.

È stato scritto `03_Verifiche/V7.8/audit_pinout_vendor_v78.py`:
1. Richiede **un XLSX fornito dall'esterno**, un hash SHA-256 registrato indipendentemente, il percorso esplicito del worksheet XML, le lettere colonne pin/segnale e la prima riga dati. Nessuna scelta automatica di foglio o collegamento esterno implicito.
2. Con Python standard-library ZIP/XML legge testi `sharedStrings` e celle inline, raccoglie pin 1..48, segnala **mancanti, duplicati e mismatch** contro V7.6.
3. Anche un confronto perfetto restituisce sempre **`qualification=HOLD` e `physical_pinout_approved=False`**, perché l'autenticità del documento, il nome della variante/package, l'orientamento e i domini elettrici richiedono comunque una revisione umana/seconda fonte.
4. I test automatici generano soltanto XLSX **SINTETICI DI TEST** e verificano checksum, lettura e rilevazione errori: **non sono il foglio Lattice**, e non possono declassare l'HOLD.

Un reale sblocco richiederà il file originale autenticato, confronto riga-per-riga, fonte del package e del revision ID, e verifica dei limiti I/O, rail, clock globali e bitstream. **Non** usare la PCF candidata per PCB.

## 3. Supervisor tensione: candidato di catalogo, NON pin-to-net

**TI TPS3840PH30DBVR**: variante di catalogo ACTIVE, **SOT-23 5 pin**, reset **push-pull active-HIGH**, soglia codificata di 3,0V. Fonte primaria prodotto https://www.ti.com/product/TPS3840/part-details/TPS3840PH30DBVR e datasheet TPS3840 SNVSB03E https://www.ti.com/lit/ds/symlink/tps3840.pdf .

- Il dispositivo può costituire un elemento di una futura **supervisione di rail** ma non è automaticamente un watchdog di clock; non integra funzione WDI su questa variante.
- **Non** collegarlo direttamente a DAC900 PD pin15: il DAC900 ha **PD active-HIGH con pulldown interno** e può essere attivo se PD è lasciato flottante. Il supervisor push-pull potrebbe essere non alimentato durante perdita del rail e non avere livello garantito prima della propria soglia POR; serve una topologia a bias e isolamento **indipendente** da verificare con guasti single-point e alimentazioni separate.
- **Nessuna piedinatura TPS3840 e nessuna rete fisica sono inventate** nella V7.8. Soglie, tempi CT, reset output loading, power sequencing, temperatura e ESD NON calcolati/qualificati. Il watchdog di clock fisico `U7902` e riferimento `X7901` rimangono **TBD/DNP**; non confondere supervisor rail e clock-stop monitor.
- L'isolatore RF futuro `Q7901` resta un requisito DNP; il confine verso DAC/PA/antenna è fisicamente **aperto**.

## 4. DSP numerico non periodico + quantizzazione 10bit

`08_Firmware_Prototipi/V7.8/dsp_nonperiodico_quantizzato_v78.py` usa il FIR causale a 3 stadi della V7.5 con audio 48kHz:
- Stimolo deterministico **non periodico** con due sinusoidi 375/1730Hz e rumore pseudo-random a seed fisso. Confronto del risultato unico con blocchi di dimensione diversa, sempre **30.720 campioni di uscita** da 384 campioni ingresso, e quantizzazione uniforme a 10bit con headroom 0,70.
- Misura soltanto RMS segnale/errore quantizzazione **numerico**, non DAC900 SFDR/SNR, immagini analogiche, jitter, adattamento I/V o emissioni RF.
- Applica un gradino di input unitario per osservare l'overshoot del FIR; il quantizzatore deve **lanciare eccezione**, non saturare silenziosamente né produrre codici per il DAC. È un test di **rejection** software e non un'interruzione fisica di trasmissione.

Il rapporto `03_Verifiche/V7.8/RAPPORTO_TECNICO_V7.8.md` riporta solo i test effettivamente eseguiti e relativi valori rilevati dai log GitHub Actions.

## 5. DNP e sicurezza

- BOM `07_Componenti/BOM_WATCHDOG_PIN_AUDIT_V7.8.csv`: **8 voci TUTTE DNP/OPEN**.
- Netlist `01_Specifiche/V7.8/NETLIST_PUNTI_APERTI_V7.8.csv`: **10 terminali concettuali TUTTI DNP/OPEN** senza pin fisici verificati per i nuovi dispositivi.
- Nessun pin DAC900 fisico, nessun filo clock, mixer IF, PA, antenna o alimentazione aggiunti; lo storico RX a 270 posizioni e 30 ALFA rimane preservato.

**NON ESEGUITI:** XLSX Lattice originale, verifica vendor completa, FPGA synthesis device-specific / PNR / STA, watchdog e supervisor su PCB, POR/PD elettrici, fault injection, KiCad ERC/DRC, simulazione analogica vendor, EMC, misure RF, fabbricazione e qualsiasi trasmissione.

**Prossima V7.9:** autenticare pinout originale, completare simulazione multi-clock/CDC e fault in hardware virtuale, selezionare MPN reali per oscillatore indipendente e interruttore fail-open con datasheet e pin verificati, convalidare componenti LPF SRF/Q reali e spettro dopo DAC model, mantenendo **NO FAB / NO TX**.
