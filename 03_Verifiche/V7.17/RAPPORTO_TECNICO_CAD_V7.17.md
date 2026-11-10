# Superstar 3900 SMD Evolution — Rapporto tecnico CAD V7.17

**11 novembre 2026 · avvio concreto della fase PCB COMPLETA a livello integrazione KiCad, senza collegamenti elettrici nuovi. NO FAB / NO TX.**

## 1. Obiettivo e deliverable

Questa revisione passa dal coupon RX all'integrazione **dell'intera architettura**: analizza i 7 fogli AUX/POWER (eFuse, buck, PLL/TCXO), MCU/CODEC/AFE e RX tramite `kicad-cli sch export netlist` e `kicad-cli sch erc` **reali**, non con una stima descrittiva. Crea un **master di revisione gerarchica V7.17** con schemi figli immutati; non una PCB integrata e non connessioni fisiche.

Directory: `04_KiCad/Assemblaggio_RX_Power_V7.17_INTEGRATION_HOLD_NOT_FOR_FAB/`. Il basename `S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB` è intenzionalmente mantenuto all'interno del nuovo contenitore versionato per evitare cambi di identità delle istanze KiCad. Il titolo specifica V7.17, include testo esplicito OPEN/HOLD, librerie locali e un nuovo contratto delle interfacce.

Evidenza nativa GitHub Actions [run 42923409956](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42923409956) **success**: verifica del master con KiCad9, ERC e netlist reali, 18 nuovi test +223 regressioni = **241 PASS /0 FAIL /0 SKIP**. Report KiCad e JSON nativi forniti nell'artifact `v717-real-kicad-full-board-erc-interface-NO-FAB-NO-TX`.

## 2. Integrità CAD della gerarchia e blocchi ERC

| Verifica | Root storico V7.14 | Master di revisione V7.17 | Significato |
|---|---:|---:|---|
| Reti native in netlist KiCad | **99** | **99** | Nomi e TUTTI i membri ref/pin identici |
| Errori ERC nativi | **43** | **43** | Nessun errore occultato |
| Warning ERC nativi | **340** | **340** | Nessun warning occultato |
| ERC RX standalone | **0/0** | **0/0**, invariato | Coupon RX soltanto |
| Collegamenti intermodulo approvati | **0** | **0** | Nessuna alimentazione o RF arbitraria collegata |
| Interfacce OPEN/HOLD | **15** | **15** | Tutti i gate restano attivi |

**Classificazione dei 43 errori ERC**, estratta riga per riga dal rapporto reale KiCad e con riferimenti foglio/coordinate conservati in `03_Verifiche/V7.17/output-ci/v717.root_erc_issues.json`:

| Categoria | N. | Azione richiesta |
|---|---:|---|
| `label_dangling` | 26 | Verificare etichette PLL, MCU, alimentazioni, segnali aperti; alcune sono volutamente PENDING, non marcabili automaticamente NC |
| `wire_dangling` | 3 | Ricostruire la rete e gli estremi elettrici reali, soprattutto intorno al PLL |
| `power_pin_not_driven` | 6 | Qualificare e portare sorgenti reali, riferimenti GND e regolatori; non mascherare con PWR_FLAG impropri |
| `pin_to_pin` | 1 | Verificare da datasheet eFuse U200 pin OUT 15↔16 dichiarati power-output; non separare/ritipizzare a caso |
| `pin_not_driven` | 5 | Verificare pilotaggio degli ingressi PLL (SYNC, SysRefReq, RampClk, RampDir e Vtune) |
| `pin_not_connected` | 2 | Verificare R2/R3 e filtro relativo, senza inventare piste |
| **Totale** | **43** | **17 problemi elettrici/fili oltre 26 label** |

I **340 warning** sono 219 `endpoint_off_grid` e 121 problemi librerie (`lib_symbol_issues` 117 + `footprint_link_issues` 4). Non è consentito azzerarli disattivando le categorie ERC.

## 3. Analisi delle 15 interfacce reali

La matrice V7.10 è preservata; la nuova `MATRICE_INTERFACCE_PROPOSTE_V7_17_OPEN_HOLD.csv` mantiene **tutte le 15 righe OPEN/HOLD e `tx_permission=0`**.

Unico aggiornamento proposto: per l'interfaccia `rx_fm_audio`, la sorgente esterna prevista `FM_DISCR_RAW` resta sconosciuta nel CAD; il **solo nome** della rete di destinazione MCU viene allineato a **`FM_DISCRIM_RAW`**, confermato dalla vera netlist MCU. La correzione non collega i segnali, non specifica livello di ingresso o filtro ed è verificata da un guardrail che impedisce modifiche nascoste alle altre 14 righe.

Sulla matrice V7.17 rimangono **2 riferimenti di rete non presenti** nella destinazione CAD:
1. `I11 rx_after_atten`: `RF_ATTEN_OUT` esiste nel coupon RX, ma `RX_IF_STAGE` **non esiste nel foglio MCU**; la catena di conversione RF→IF è da progettare, non si può chiudere con una net label.
2. `I15 interlock`: `RF_TX_UNROUTED` non esiste, intenzionalmente, nella sezione AUX. **È giusto mantenere TX non realizzato.**

Restano qualifiche pendenti per 5V RF vs `+5V_BENCH`, 5V/3V3 codec, GND_MAIN vs GND_RF, CE/CSB reset e MUXOUT, preamplificatore microfonico e segnale FM. Un nome uguale nelle netlist isolate **NON è** una connessione fisica.

## 4. Cosa è stato realmente aggiunto

- `04_KiCad/Assemblaggio_RX_Power_V7.17_INTEGRATION_HOLD_NOT_FOR_FAB/`: vero KiCad schematic master a 7 pagine + project, tabelle librerie e CSV di contratto.
- `03_Verifiche/V7.17/audit_full_board_native_v717.py`: parser nativo ERC con tutte le coordinate, file JSON per categoria/foglio, analisi di 15 interfacce su nomi delle reti nativi KiCad.
- `03_Verifiche/V7.17/verify_versioned_full_board_master_v717.py`: impone **identità esatta di ogni net/ref/pin** vecchio↔nuovo e nessuna variazione ERC, pin di foglio o wires.
- `03_Verifiche/V7.17/test_full_board_gate_v717.py`: **18 nuovi test** includendo FM nomenclature, 5V≠3V3 e TX bloccato; più **223 regressioni V7.1–V7.16**.
- `.github/workflows/v717_full_board_erc.yml`: esecuzione automatica nativa e archiviazione prove.

**Nessun** layout della radio completa (`.kicad_pcb`) viene creato, nessuno schema figlio/PCB coupon o firmware alterato, nessun ERC hard risolto arbitrariamente. **La stima della PCB completa rimane circa 10%, senza accredito percentuale di layout per la diagnostica.**

## 5. Prossime azioni tecniche, in ordine di sicurezza

1. **V7.18: eliminazione controllata degli ERC elettrici nel ramo POWER/PLL**, iniziando dai 17 errori reali pin/wire. Richiede verifica pinout e datasheet eFuse, regolatori e LMX2572, mantenendo test di parità o tracciando esplicitamente ogni ECO autorizzato.
2. Qualificare 5V/3V3 e punto stella GND con budget di corrente, filtro, thermal, ritorno RF ed ESD. NO rail short per equivalenza di nome.
3. Collegare SPI MCU→PLL soltanto dopo verifica GPIO, reset, CE fail-safe e logica TX hard-inhibit.
4. Definire e simulare la vera catena RX fino a IF (stadio mancante `RX_IF_STAGE`), determinare requisiti RF e analogici prima della netlist globale.
5. Solo con schematico integrato, annotazione, pinmap e BOM reali: **creare la prima PCB unica versionata** con placement/stack-up; DRC nativo e approvazione fornitore footprint SMA prima di Gerber e prototipo.

**NO FAB, NO GERBER, NO PCBWAY, NO TX, nessun PA o antenna attivata.**
