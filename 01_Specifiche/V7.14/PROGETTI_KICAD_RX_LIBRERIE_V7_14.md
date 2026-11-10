# V7.14 — progetti KiCad RX e gerarchia con librerie di progetto

**10 novembre 2026. Stato progettuale NO FAB / NO TX.** V7.14 segue V7.13 `main` e conserva completamente lo storico, i test DSP, firmware, PLL e la baseline RX.

## 1. Causa diagnosticata con KiCad 9, NON desunta dal nome dei file

Il vero report ERC del coupon RX V7.13 aveva **15 `lib_symbol_issues`** e **15 `footprint_link_issues`**, tutti con motivo: **“The current configuration does not include the [symbol/footprint] library”**. I file di tabella esistevano già, ma **senza un progetto `.kicad_pro` riconosciuto** il CLI non caricava le librerie project-local. La semplice copia del file simboli nella cartella RX ha prodotto ancora **30 warning** nel primo test nativo, dunque era insufficiente.

La V7.14 aggiunge un `S3900E_RX_LIB_V7_14_NOT_FOR_FAB.kicad_pro` con `meta.filename` corrispondente allo schematic e PCB, una copia letterale dell'archivio simboli `S3900E.kicad_sym`, `sym-lib-table` in directory di progetto e `fp-lib-table` con le tre librerie footprint storiche (collegamenti relativi ai `.pretty`). Con tale file di progetto presente KiCad 9 **ha letto effettivamente i riferimenti delle librerie**: **30 warning ERC → zero**, senza cambiare nessun controllo di severità.

Tutti i file sono nella directory `04_KiCad/Modulo_RX_Test_50ohm_V7.14_LIB_DIAGNOSTIC_NOT_FOR_FAB/`:
- `S3900E_RX_LIB_V7_14_NOT_FOR_FAB.kicad_pro` — contenitore progetto minimo, con header JSON verificato dal CLI;
- `S3900E_RX_LIB_V7_14_NOT_FOR_FAB.kicad_sch` — copia con stesse 15 refs, net, label, pins e UUID del RX V7.13;
- `S3900E_RX_LIB_V7_14_NOT_FOR_FAB.kicad_pcb` — **bytes del file PCB uguali** alla V7.12; nessuna nuova pista né modifica di rame o foratura;
- `S3900E.kicad_sym`, `sym-lib-table`, `fp-lib-table` — riferimenti locali; i tre `.pretty` e gli originali V5.2 restano invariati e storicamente conservati.

**Non è stata aperta una GUI KiCad e non sono stati effettuati collaudi meccanici o RF**. `kicad-cli` è stato eseguito realmente; i dati CAD non sono stati trasformati in Gerber.

## 2. Confronti e risultato nativo RX

La comparazione utilizza `kicad-cli sch export netlist` sul RX V7.13 e sul RX V7.14 e confronta esattamente nomi di rete e coppie (reference, pin): **identici, nessun pin spostato elettricamente**, nessun collegamento inventato. Lo schema V7.14 genera `kicad-cli sch erc` **0 errori e 0 warning**; il risultato è validazione ERC del solo *coupon* e **non equivale alla qualifica vendor dei piedini/pad**.

Il `kicad-cli pcb drc` viene eseguito sul PCB RX nella directory progetto V7.14: **85→72 violazioni DRC** per effetto della configurazione librerie; la distinta reale è:
- **70 `via_dangling`** di GND_RF, cioè via sconnesse o con connessione su un solo lato (non nascoste);
- **2 `lib_footprint_mismatch`** sui connettori SMA **J9102 e J9104**: footprint nel PCB non uguale a quello disponibile nella libreria; **NON sovrascrivere footprint o tracce prima del confronto con disegno vendor**;
- **63 `unconnected_items`** riportati separatamente dalle 72 violazioni: piste e piani non ultimati; nessuna traccia arbitraria aggiunta;
- **0 `drill_out_of_range`**: correzioni della V7.11 conservate.

**DRC del PCB resta NON SUPERATO**, non è possibile autorizzare produzione. Il passaggio 85→72 **non significa routing o geometria più sicuri**: il rame è rimasto identico.

## 3. Progetto gerarchico reale, ma fili intermodulo assenti

Nuovo progetto `04_KiCad/Assemblaggio_RX_Power_V7.14_LIB_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_pro` con relativo `.kicad_sch`, `sym-lib-table`, `fp-lib-table`. Contiene gli stessi **7 fogli**, con AUX V1.5 e MCU V7.12 intatti, ma foglio RX sostituito dalla V7.14 con librerie accessibili. **Le 15 interfacce tra moduli restano OPEN/HOLD**.

Due esportazioni vere `kicad-cli sch export netlist` della gerarchia V7.13 e V7.14 producono **99 reti identiche**, con corrispondenza completa di ciascun (reference, pin). ERC gerarchico native:
- V7.13: **43 errori + 370 warning = 413**;
- V7.14: **43 errori + 340 warning = 383**;
- **30 warning spariti** perché le 15 posizioni RX ora sono risolte attraverso librerie di progetto; rimangono **117 lib symbol issues, 4 footprint link issues, 219 endpoint off-grid** e altri errori power, pin e label nei moduli AUX/MCU. Non dichiarare ERC gerarchico superato.

Tutti i componenti e interfacce verso TX/DAC900/FPGA/mixer/PA/antenna sono DNP/OPEN, non alimentati né instradati; pinout originale Lattice SG48 ancora HOLD.

## 4. Limiti e prossime azioni

**Non eseguiti:** qualificazione meccanica SMA/ADL5535, prova via-in-pad e ritorni GND_RF, routing delle 63 connessioni, power rails e alimentazione RX verificata, MCU/PLL/IF2 connessi, disegno PCB complessivo, RF/EMC e laboratorio. I test software DSP e firmware continuano in parallelo.

**V7.15:** recuperare datasheet manufacturer dei connettori SMA e comparare footprint in libreria vs copie PCB J9102/J9104, valutare modello reale di ritorno massa per 70 via e risolvere le 63 connessioni con netlist pad a pad; ridurre 43 errori ERC root qualificando i moduli AUX/MCU. Nessun Gerber e nessun TX finché i blocchi non sono qualificati. **NO FAB / NO TX.**
