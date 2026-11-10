# V7.12 — Riannotazione KiCad reale e schema RX standalone riparato

**10 novembre 2026 · NO FAB / NO TX.** Il progetto `jd3485/Superstar3900-SMD-Evolution` continua da V7.11. Nessun nuovo collegamento elettrico qualificato tra alimentazioni, MCU, RX e TX; tutti gli output verso DAC900/FPGA/mixer/PA/antenna restano DNP/non alimentati/non instradati.

## 1. Root KiCad V7.12 realmente editabile

Nuovo schema `04_KiCad/Assemblaggio_RX_Power_V7.12_REANNOTATED_NOT_FOR_FAB/S3900E_RX_POWER_INTEGRATION_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch` include (come fogli gerarchici **non collegati elettricamente**):
- AUX power V1.5 esistente con 3 fogli interni eFuse/buck/PLL — originale **intatto**;
- MCU/CODEC AFE V2.1 su copia V7.12 `04_KiCad/Modulo_MCU_CODEC_V7.12_REANNOTATED_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch`;
- RX test coupon 50Ω V5.2 su copia V7.12 `04_KiCad/Modulo_RX_Test_50ohm_V7.12_SCHEMATIC_REPAIR_NOT_FOR_FAB/S3900E_RX_STANDALONE_V7_12_NOT_FOR_FAB.kicad_sch`.

**Riannotazione esplicita, senza cambiare nets:** tutte le 46 istanze MCU hanno suffissi +6000 (es. `U201 → U6201`, `C201 → C6201`), tutte le 15 RX suffissi +9000 (es. `J101 → J9101`, `C101 → C9101`, `R201 → R9201`), AUX rimane originale. Gli `instances/project/path/reference` dei simboli sono modificati insieme alle proprietà Reference. Un `.kicad_pcb` RX corrispondente nella stessa cartella V7.12 riporta i 15 riferimenti RX identici. È una copia del PCB V7.11 con gli stessi fori già corretti e **nessuna pista, net o via modificata**.

## 2. Netlist native, non confronto di soli testi

Verifica `kicad-cli sch export netlist` reale su entrambi i root: `03_Verifiche/V7.12/verifica_netlist_annotazione_v712.py` legge entrambi gli output di KiCad, non inventa una BOM. I criteri imposti sono:
- **7 fogli**, **132 istanze**, **99 reti** in entrambi i root;
- **11 designatori ripetuti, 14 istanze extra** nella V7.10 originale → **0 ripetizioni, 0 istanze extra** nella V7.12;
- tutte le interfacce RX/POWER/MCU ancora **OPEN/HOLD** per pin e rail: non basta che la netlist sia esportabile per essere elettricamente corretta.

Una riannotazione non è un collegamento elettrico e non costituisce un ERC o DRC pulito.

## 3. Root cause e riparazione dello schema RX standalone

La V5.2 conteneva una nota grafica KiCad `(text "...")` con **caratteri LF reali dentro la stringa tra virgolette e UUID mancante**, violando la codifica S-expression di KiCad. Il loader della gerarchia V7.10 includeva il foglio RX, ma **`kicad-cli sch erc` e `sch export netlist` direttamente sul file standalone fallivano con exit 3**. Aggiungere soltanto `sheet_instances` (tentativo V7.10 storico) non poteva eliminare l'errore.

La nuova copia V7.12:
- aggiunge UUID reale alla nota grafica;
- converte i caratteri newline dentro la stringa grafica in escape **`\n` letterali** (nessuna cancellazione del messaggio o cambiamento di geometria del circuito);
- include metadati di root KiCad `sheet_instances` e `embedded_fonts no`;
- reannota i 15 riferimenti RX, con PCB di prova rinumerato in parallelo.

Diagnosi `03_Verifiche/V7.12/probe_rx_schematic_parser_v712.py`: crea **copie temporanee di diagnostica**, mantiene tutte le librerie, piazzamenti, wire e label e testa l'aggiunta del testo. Prima della correzione: file senza testo `export netlist` **PASS**, con testo `exit 3`. Dopo l'escape e UUID, KiCad 9 esegue **`sch erc` standalone (exit 0, report reale 76 segnalazioni)** e `sch export netlist` su copia diagnostica con testo. Il fatto che il parser funzioni **NON** equivale a ERC senza errori: la RX standalone ha **76 violazioni ERC** ancora aperte.

Specifica ufficiale KiCad S-expression: https://dev-docs.kicad.org/en/components/sexpr/ , stringhe multilines devono essere escape per `\n`.

## 4. DRC invariato, nessuna modifica nascosta di PCB

Il workflow ripete `kicad-cli pcb drc` sul PCB RX V7.12 rinumerato e controlla la non regressione rispetto alla V7.11:
- **85 violazioni DRC** (fra cui **70 via_dangling** e **15 lib_footprint_issues**),
- **63 connessioni non completate** segnalate a parte,
- **zero** `drill_out_of_range` dopo riparazione sei fori V7.11.

La tabella `fp-lib-table` con librerie storiche è conservata ma i 15 warning footprint **non** risultano risolti. Anche il root gerarchico continua a produrre **459 segnalazioni ERC** (V7.10 43 errori/416 warning); il nuovo CRC delle refs è una riduzione documentale, non una correzione degli errori di rete.

## 5. Gate e prossime attività

La CI V7.12 esegue CLI native, confronto netlist, ERC RX/root, DRC coupon, prove di parser e **13 test statici V7.12 +8 V7.11 +12 V7.10 +143 V7.1–V7.9 = 176 test Python**. Distinguere chiaramente: **PASS caricamento/riannotazione/non regressione** ≠ **FAIL ERC/DRC elettrici ancora aperti**.

**Prossima V7.13:** lavorare direttamente sulle 70 via GND dangling e 63 unconnected del coupon RX con verifica poligoni/ritorni RF, valutare footprint/courtyard/pad vendor, ridurre i 76 ERC RX e 459 ERC root. Collega i 15 confini RX/AUX/MCU soltanto dopo avere qualificato rails, polarità, footprint e pin; integra la catena IF completa ed eventualmente un PCB unico solo dopo netlist elettricamente coerente. Firmware/DSP/PLL continuano in parallelo.

**NO FAB / NO TX:** niente Gerber, alimentazione TX, PTT, PA, antenna, assemblaggio o prove radio.
