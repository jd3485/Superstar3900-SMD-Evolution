# SUPERSTAR 3900 SMD EVOLUTION — RAPPORTO TECNICO CAD V7.13

**10 novembre 2026 | Versione sperimentale KiCad del modulo RX 50Ω, NO FAB / NO TX.**

## 1. Lavoro effettivamente realizzato

Sviluppo incrementale su copie versionate della V7.12, senza sostituire gli originali. Nuovi sorgenti nativi:

- `04_KiCad/Modulo_RX_Test_50ohm_V7.13_GRID_NOT_FOR_FAB/S3900E_RX_GRID_V7_13_NOT_FOR_FAB.kicad_sch`: stesso schema e stessa rete di componenti RX della V7.12, 15 origini di simboli, 31 coppie di estremi wire, 31 ancore label portate su **griglia connessione 1,27mm / 50mil**. Offset locali di 19 pin cached già conformi, invariati. Nessun numero di pin, reference, valore, UUID elettrico o net name cambiato.
- `04_KiCad/Assemblaggio_RX_Power_V7.13_GRID_NOT_FOR_FAB/S3900E_RX_POWER_V7_13_GRID_NOT_FOR_FAB.kicad_sch`: root KiCad a 7 fogli che punta alla nuova RX e preserva AUX/MCU V7.12. **Nessuna connessione elettrica intermodulo**: tutti i 15 contratti ancora OPEN/HOLD.
- `sym-lib-table` e `fp-lib-table` nella cartella RX V7.13: puntano a librerie archiviate esistenti, non rappresentano una qualifica fisica dei footprint o una prova della loro corretta risoluzione su altre installazioni.

## 2. Verifiche native KiCad, non simulazioni ipotetiche

CI GitHub Actions [run 42869838167](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42869838167), job **130017817769**, log realmente controllato; conclusione **SUCCESS**. Il workflow installa KiCad 9, esporta due netlist vere (`kicad-cli sch export netlist`), esegue ERC e DRC native e **non esclude i warning**.

### Equivalenza elettrica rigorosa

`03_Verifiche/V7.13/verifica_netlist_rx_v713.py` confronta i multiset completi di **(nome rete, ref, pin)** tra RX V7.12 e RX V7.13. Risultato **`same_net_names=true` e `same_all_pin_memberships=true`**. Non basta uguaglianza del numero reti. Nessun collegamento nuovo o perso è stato rilevato dal vero esportatore KiCad. Questo verifica la connettività codificata, **non la corretta risposta RF reale**.

### Progressione ERC della RX e della gerarchia

| Controllo KiCad | V7.12 | V7.13 | Valutazione |
|---|---:|---:|---|
| RX `endpoint_off_grid` | **46** | **0** | **PASS, difetto CAD eliminato** |
| RX errori ERC | 0 | 0 | Nessun nuovo errore |
| RX warning ERC totali | 76 | **30** | Ancora NON ZERO |
| RX `lib_symbol_issues` | 15 | **15** | HOLD: librerie non risolte |
| RX `footprint_link_issues` | 15 | **15** | HOLD: footprint non risolti |
| Root 7 fogli errori ERC | 43 | **43** | HOLD invariato |
| Root 7 fogli warning ERC | 416 | **370** | Miglioramento 46 |
| Root totale segnalazioni ERC | 459 | **413** | **Non ERC PASS** |

La regola di griglia da 50mil e i criteri ERC sono **invariati**. Non sono state introdotte `no_connect` o reti fittizie per silenziare i problemi.

### PCB RX invariato

La PCB nativa KiCad `04_KiCad/Modulo_RX_Test_50ohm_V7.12_SCHEMATIC_REPAIR_NOT_FOR_FAB/S3900E_RX_STANDALONE_V7_12_NOT_FOR_FAB.kicad_pcb` è lasciata identica alla V7.12. La DRC reale sul file conferma **85 violazioni** (70 `via_dangling`, 15 `lib_footprint_issues`), più **63 connessioni incompiute**. Le 6 via-drill sottodimensionate della V7.10 erano state corrette nella V7.11 e restano **0 errori di foratura**.

## 3. Firmware, DSP e regressioni preservate

Run V7.13: **10 test nuovi V7.13 +13 V7.12 +8 V7.11 +12 V7.10 +143 V7.1–V7.9 = 186/186 PASS, 0 FAIL e 0 SKIP**. I test storici sulla generazione numerica IF2, 270 canali RX, quantizzatore 10bit, clock virtuale, watchdog e FIR restano attivi. Icarus e sintesi Yosys **non rieseguiti in questo workflow** e non rivendicati come validazione FPGA fisica.

Sono disponibili come artifact GitHub Actions i report `.net`, `.rpt` e i JSON generati realmente dalla CI, non Gerber. Lo script `verifica_erc_grid_v713.py` blocca merge se il numero di errori ERC RX cresce, i warning RX non diminuiscono o la griglia non scende esattamente da 46 a zero. `verifica_netlist_rx_v713.py` blocca qualunque delta net-pin.

## 4. Problemi ancora da risolvere prima del PCB completo

**NON ESEGUITI:** progetto `.kicad_pro` validato e portabile completo, 15 symbol lib/15 footprint warnings RX, 43 errori ERC root, 70 vias GND con ritorni funzionali, 63 nets RX non sbrogliate, layout unico di tutta la radio, power/MCU/RX interfacce validate, filtri con componenti reali Q/SRF, pinout FPGA SG48 originale XLSX verificato, test analogici/RF/EMC, fabbricazione, emissioni e TX. I componenti e link TX rimangono tutti **DNP, non alimentati, aperti**.

**Decisione progettuale:** la V7.13 è una correzione reale dello schema CAD e dei warning di geometria verificata, NON una release di schema elettrico completo o PCB. Prossima V7.14: risolvere librerie e footprint con progetti KiCad realmente aperti, poi via dangling, collegamenti RX e problemi ERC della gerarchia senza reti arbitrarie. **NO FAB / NO TX.**
