# Superstar 3900 SMD Evolution — RAPPORTO TECNICO V7.8

**10 novembre 2026 — V7.8 MODELLO NUMERICO E RTL, NO FAB / NO TX.** Evoluzione incrementale da main V7.7 (`607dd957`), storico immutato, tutti i componenti e ponti TX DNP e segnali analogici fisicamente assenti.

## 1. Sviluppo

**Monitor watchdog a due clock simulati** `08_Firmware_Prototipi/V7.8/rtl/clock_watchdog_indipendente_v78.v`: tre moduli con heartbeat dal master virtuale e watchdog in dominio di riferimento virtuale separato. Sincronizzazione a tre flip-flop, due transizioni richieste, timeout di 40 tick riferimento **di simulazione**, fault bloccato finché reset. **Arrestando il master e mantenendo il secondo clock virtuale**, il bench Icarus rileva il fault e lo mantiene anche dopo ripresa del master. Le tre uscite `tx_rf_permission`, `dac_pd_released` e `analog_path_connected` sono costanti zero. Nessuna generazione o misura elettrica dei clock, nessun circuito supervisor o RF.

**Audit pinout Lattice** `03_Verifiche/V7.8/audit_pinout_vendor_v78.py`: comparatore OOXML usando solo ZIP/XML standard library, richiede XLSX esterno, SHA256 noto indipendentemente, percorso sheet e colonne espliciti. Testa duplicati/mancanti/mismatch dei 48 pin V7.6. L'**originale XLSX Lattice** documento 51971 non è stato acquisito (download pubblico fallito), perciò **pinout V7.6/PCF resta HOLD**. I test su file XLSX sintetici **NON** provano il contenuto del produttore e non possono approvare un PCB, neppure con confronto perfetto. Fonte vendor catalogo: https://www.latticesemi.com/Products/FPGAandCPLD/iCE40UltraPlus .

**Supervisor rail solo candidato:** Texas Instruments **TPS3840PH30DBVR**, push-pull reset active-HIGH, soglia 3,0V, SOT23-5, ACTIVE secondo pagina TI https://www.ti.com/product/TPS3840/part-details/TPS3840PH30DBVR ; non è un watchdog di clock, non sono stati verificati/assegnati pin fisici e **NON è connesso** al DAC900 PD. PD pin15 è active-HIGH e ha pull-down interno; uno stato flottante può abilitare il DAC. In assenza del rail anche il supervisor può essere incapace di imporre il proprio livello: **NON è stata dimostrata una protezione single-fault fail-safe**. Oscillatore indipendente e blocco di isolamento RF con MPN ancora TBD.

**DSP non periodico + pre-guard rigorosa:** `08_Firmware_Prototipi/V7.8/dsp_nonperiodico_quantizzato_v78.py`, 384 campioni audio 48kHz di due toni non coerenti 375/1730Hz + rumore deterministico → FIR ×80 stateful → 30.720 campioni digitali baseband a 3,84MSa/s → codici ideali 10bit. Nessun wrap tra blocchi. Nel modello numerico **SNR segnale/errore di quantizzazione = 49,3918 dB** con headroom 0,70; **NON** SNR/SFDR del DAC900 reale, maschera di emissione o risultato RF. Introdotta la funzione `quantize_with_peak_guard`, che rifiuta campioni **normalizzati con |x|>1 o non finiti PRIMA della scalatura**: il quantizzatore precedente può codificare segnali >1 dopo 70% headroom, ma ciò è meno severo del contratto V7.8. Gradino normalizzato 1,0 produce nel FIR picco **1,142051**, quindi viene rifiutato in modo esplicito; è una eccezione software, NON un interblocco hardware.

**ECO e distinta:** BOM `07_Componenti/BOM_WATCHDOG_PIN_AUDIT_V7.8.csv` **8 righe tutte DNP/OPEN**, netlist `01_Specifiche/V7.8/NETLIST_PUNTI_APERTI_V7.8.csv` **10 terminali tutti DNP/OPEN**, senza assegnazione fisica di pin o nuova connessione al DAC, mixer o antenna. `01_Specifiche/V7.8/ARCHITETTURA_WATCHDOG_PINOUT_DSP_V7.8.md` documenta l'architettura e i gate.

## 2. Esecuzioni realmente verificate (GitHub Actions)

| Verifica | Esito | Limite |
|---|---|---|
| Icarus testbench V7.8 dual-clock | **PASS** | Clock e fault soltanto simulati |
| Icarus regressione V7.7 top | **PASS** | Diagnostica RTL, non DAC reale |
| Icarus regressione V7.6 clock/FIFO | **PASS** | Clock-enable /8 e /640, non output DAC |
| Yosys sintesi logica generica V7.8 | **PASS**, circa 206 celle logiche nel modello | Non PNR/STA iCE40, non area/timing fisici |
| Yosys regressione generica V7.7 | **PASS** | Non bitstream FPGA |
| Nuovi test Python V7.8 | **20 PASS, 0 FAIL, 0 SKIP** | Audit sintetico XLSX, dati DSP e DNP |
| Regressioni Python V7.7 | **14 PASS** | Modelli RTL/quantizzazione |
| Regressioni V7.6 / V7.5 / V7.4 | **15 + 22 + 21 PASS** | Pinplan HOLD, clock e DAC virtuale |
| Regressioni V7.3 / V7.2 / V7.1 | **15 + 11 + 8 PASS** | IF2, DUC, 270 canali |
| **Totale Python** | **126 PASS / 0 FAIL / 0 SKIP** | <https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42842592233>, job 129921434758, **log letto** |
| Test hardware, pin Lattice originali e fabbricazione | **NON ESEGUITI** | Nessun risultato fisico né conformità RF |

La prima CI V7.8 (run `42842166804`) ha individuato che il quantizzatore V7.3 accettava il gradino >1 dopo l'attenuazione di headroom. Il controllo è stato **corretto**, sono stati aggiunti test sui limiti ±1 e sugli input non finiti, e la CI successiva `42842592233` ha confermato tutto **PASS**. Non si è nascosto o reinterpretato il FAIL iniziale.

Machine-readable: `03_Verifiche/V7.8/RISULTATI_VERIFICHE_V7.8.json`.

## 3. Blocchi progettuali NON ESEGUITI

- XLSX Lattice originale verificato sul package SG48; pin-out/PCF V7.6 **HOLD**; nessun Yosys `synth_ice40` + nextpnr/PnR o timing fisico.
- MPN, pinout e alimentazione di riferimento indipendente, supervisor hardware funzionante, uscita PD con stato garantito a rail=0, analog/RF fail-open, proof single-fault, test di guasti a massa o stuck-at.
- CDC/MTBF, reset-domain-crossing, fault su reference clock stesso, power sequencing reale del dispositivo Lattice e del DAC.
- KiCad ERC/DRC, simulazioni SPICE vendor del filtro F7401 con SRF/Q realistici, misure RF e audio, DAC 10bit fisico, analisi EMC, DFM, schede fabbricate, emissioni o autorizzazioni normative.

**Decisione:** V7.8 è soltanto un incremento riproducibile dei **modelli digitali** e della disciplina di qualificazione vendor. È candidabile per `main` dopo CI finale della PR, ma NON per ordinare PCB, collegare RF o trasmettere.

**Prossima V7.9:** ottenere il file pinout originale Lattice per risolvere HOLD, definire MPN del clock indipendente e fail-open fisico con pin e caratteristiche verificate, affinare il controllo di power sequencing e CDC, simulare filtro analogico con Q/SRF vendor, ripetere la regressione globale. **NO FAB / NO TX.**
