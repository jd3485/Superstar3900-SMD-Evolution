# V7.61 — Riparazione della libreria simboli KiCad TPS3840 U6207 (NO FAB)

13 novembre 2026. Baseline V7.60 **139 componenti, 102 reti, ERC 28 errori/215 warning**, 238 test PASS. KiCad9 segnala `lib_symbol_issues`: `Symbol 'TPS3840PL30_DBV5_REVIEW' not found in symbol library 'S3900E'` sul supervisore U6207. Questo avviso è distinto dai warning `endpoint_off_grid` già eliminati con la V7.60.

## ECO CAD reale: libreria unificata completa

Il simbolo U6207 **esiste già come definizione embedded nel foglio MCU V7.60** con i suoi cinque pin (1 RESET_N, 2 VDD, 3 GND, 4 MR_N, 5 CT), il footprint reviewer-only TI DBV0005A e i collegamenti U6207 alla rete. Mancava esclusivamente nella libreria esterna `S3900E` referenziata dal master. Una copia completa versionata `04_KiCad/Librerie_Simboli_V7.61_SUPERVISOR_U6207_HOLD/S3900E.kicad_sym` contiene ora una **esatta copia della definizione embedded**, rinominando soltanto l'intestazione `S3900E:TPS3840PL30_DBV5_REVIEW` in `TPS3840PL30_DBV5_REVIEW` come previsto nel file di libreria. Tutte le altre definizioni restano byte-identiche alla libreria V7.58.

La nuova root `04_KiCad/Assemblaggio_RX_Power_V7.61_U6207_SYMBOL_LIBRARY_REVIEW_NOT_FOR_FAB/` modifica **solo il percorso della libreria nel `sym-lib-table`**. Foglio MCU/codec V7.60, schemi AUX/RX, pin, valori, PCB footprint, `.kicad_pro`, `fp-lib-table`, root `.kicad_sch` e 15 interfacce aperte rimangono identici.

## Verifica fail-closed

`03_Verifiche/V7.61/test_tps3840_u6207_library_native_v761.py` confronta la S-expression del simbolo embedded con la nuova libreria, conta i 5 pad/pin, confronta **netlist 7-sheet native KiCad9 prima/dopo** 139 componenti, 102 reti e ogni pin→net invariato, e preserva il ritorno eFuse RTN separato da GND_MAIN. Richiede **28 errori ERC identici** e rimozione di **uno ed esattamente uno** warning `lib_symbol_issues` U6207, senza nuovi findings: target **215→214 warning**. Se l'ECO introducesse un `lib_symbol_mismatch` o cambiasse qualsiasi net, il gate fallirebbe. Nessuna soppressione o waiver.

Questa correzione dimostra soltanto coerenza libreria/schema; **non** qualifica elettricamente il supervisore `TPS3840PL30DBVR`, la supervisione LDO o reset del codec. Richiesta ancora revisione del timing MR_N/CT e soglie, delle tensioni di alimentazione e del carico 5V. [Issue #57](https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/57) eFuse latch-off senza reset indipendente ancora aperta, [Issue #63](https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/63) audit storico, 15 crossmodule OPEN/HOLD, SG48/Y1 pin10 HOLD, PCB unica non completata. **NO FAB / NO GERBER / NO PCBWAY / NO TX.**
