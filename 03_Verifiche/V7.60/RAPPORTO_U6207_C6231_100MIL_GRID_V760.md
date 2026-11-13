# V7.60 — Correzione reale griglia KiCad U6207 e C6231 (NO FAB)

13 novembre 2026. Master precedente **V7.59**, integrato con 225 test PASS e KiCad9 ERC **28 errori / 217 avvisi**. Nuovo master V7.60 versionato per risolvere il posizionamento fuori griglia del supervisore **TPS3840PL30 U6207** e del bypass **C6231**, senza cambiare connessioni e senza simulare una qualifica di alimentazione.

## ECO esatta

- MCU `04_KiCad/Modulo_MCU_CODEC_V7.60_SUPERVISOR_C6231_GRID_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch`: U6207 centro (1010.00,415.00)→(1010.92,414.02)mm; C6231 centro (1050.00,415.00)→(1049.02,414.02)mm.
- Spostate **3 label + 2 marcature NC di U6207** e **2 label del condensatore C6231**, tutte agli esatti terminali dei simboli su griglia 2,54mm. MPN, valore, pin, tipi e footprint invariati. Nessun filo originario sulle coordinate di questi pin. Nessuna modifica alle connessioni tra moduli.
- Root `04_KiCad/Assemblaggio_RX_Power_V7.60_SUPERVISOR_C6231_GRID_REVIEW_NOT_FOR_FAB/`: cambia soltanto il collegamento al nuovo MCU. I fogli AUX/RX, la libreria simboli V7.58, `sym-lib-table`, `fp-lib-table` e `.kicad_pro` restano invariati.

## Gate richiesto

`03_Verifiche/V7.60/test_supervisor_cap_grid_native_v760.py` genera da KiCad9 **netlist ed ERC nativi** prima/dopo sullo stesso runner; attesta conservazione **139 componenti, 102 reti e OGNI pin→net**, 0 footprint fields vuoti, eFuse RTN/GND distinti e SHDN NC. L'unica variazione accettabile agli avvisi ERC è la rimozione dei due warning `endpoint_off_grid` relativi a U6207 e C6231: obiettivo **28 errori invariati**, **217→215 warning**, senza nuovo `power_pin_not_driven` o etichette scollegate. I warning non vengono soppressi: il test confronta i report nativi mantenendo tutte le segnalazioni esterne ai due componenti. Se il conteggio o la netlist differiscono, **PR RED / NON MERGE**.

La correzione geometrica NON dimostra tempi di reset del TPS3840, correttezza del circuito di supervisione, assorbimenti 5V, affidabilità termica, capacità MLCC reale a 5V, coordinamento fusibile/eFuse, né DRC di PCB completa. Rimangono Issue [#57](https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/57) eFuse indipendente, [#63](https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/63) audit ERC storico, 15 interfacce cross-module OPEN/HOLD, SG48 e Y1 pin10 HOLD. **NO FAB / NO GERBER / NO PCBWAY / NO TX.**
