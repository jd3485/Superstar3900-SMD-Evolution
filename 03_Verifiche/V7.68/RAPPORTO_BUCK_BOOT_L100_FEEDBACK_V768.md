# V7.68 — BUCK bootstrap, induttore e feedback sulla griglia KiCad + analisi Vout

Data 13 novembre 2026. Baseline `main` **V7.67 integrata**, 140 componenti, 103 reti, ERC 28 errori +201 warning, KiCad9 346 test PASS. ECO reale con **sei** componenti del TPS54202: `C102` 100nF/25V bootstrap, `L100` 15µH Bourns SRP1038A-150M, `R100` 49.9Ω 1%, `R101` 100kΩ 1%, `C105` 75pF C0G e `R102` 13.3kΩ 1%. **Valori, MPN, footprint, topologia elettrica, librerie e protezioni invariati.**

## ECO sorgente e pin-net

Nuovo `04_KiCad/Gerarchico_Alimentazioni_V7.68_BUCK_BOOT_L_FB_GRID_REVIEW_NOT_FOR_FAB/02_BUCK_5V.kicad_sch`:
- C102 centro (218,67)→(218.44,66.04)mm, label `BUCK_BOOT` e `BUCK_SW`;
- L100 (250,95)→(248.92,93.98)mm, label `BUCK_SW` e **porta gerarchica output `5V_RF_PREREGULATED`**;
- R100 (246,190)→(246.38,190.50)mm, label `5V_RF_PREREGULATED` e `BUCK_DIV_TOP`;
- R101 (279,190)→(279.40,190.50)mm, label `BUCK_DIV_TOP` e `BUCK_FB`;
- C105 (310,190)→(309.88,190.50)mm, label `BUCK_DIV_TOP` e `BUCK_FB` (parallelo R101);
- R102 (279,227)→(279.40,226.06)mm, label `BUCK_FB` e `GND_MAIN`.

Sono autorizzate **36 modifiche letterali esatte**: sei posizioni istanze, 18 posizioni campi Reference/Value/Footprint e dodici label, tutte le due estremità di ciascun simbolo su 2.54mm. La nuova root `04_KiCad/Assemblaggio_RX_Power_V7.68_BUCK_BOOT_L_FB_GRID_REVIEW_NOT_FOR_FAB/` cambia esclusivamente path sheetfile AUX; `01_EFUSE_AUX`, `03_PLL_LDO_TCXO`, altri fogli, simboli, footprint e tabelle di libreria byte-identici. Nessun nuovo nodo né connessione tra `EFUSE_RTN` e `GND_MAIN`. D200 TVS resta DNP.

## Analisi numerica della retroazione

Fonte vendor primaria TI [TPS54202 SLVSD26C, Rev C febbraio 2026](https://www.ti.com/lit/ds/symlink/tps54202.pdf), §5.5: tensione feedback `V_FB` **min 0.581V, typ 0.596V, max 0.611V**. Con R100 49.9Ω in serie a R101 100kΩ nella resistenza superiore e R102 13.3kΩ inferiore, calcolo **ideale DC** (trascurando correnti FB, deriva e regolazione dinamica):

`Vout_DC_ideale = V_FB × [1+(R100+R101)/R102]`.

- Vout nominale ideale **5.07944V**. Non è un valore garantito o una misura;
- Con R100/R101/R102 tutti 1% e estremi V_FB TI, inviluppo idealizzato **4.86505–5.30013V**; NON è una tensione worst-case garantita di tutta la PCB o una prova transitoria.
- C105 75pF è un compensatore dinamico in parallelo a R101, non un elemento del rapporto DC ideale. Non possiamo dichiarare valida compensazione e stabilità TPS54202 senza reale Ceff C103/C104 sotto DC bias, ESR, L100 DCR/tolleranza/saturazione e misure/analisi loop.
- Un'uscita teorica fino a ~5.30V potrebbe modificare dissipazione/temperature dei sei TPS7A2033 e il margine downstream. Necessario verificare input massimo tollerato/PSRR/thermal e worst load reale. Non approssimare tutti i LDO a 300mA come carico misurato.

## CI e condizioni

`03_Verifiche/V7.68/test_buck_boot_inductor_feedback_native_v768.py` 20 nuovi test: confronti native KiCad9 CLI netlist/ERC **sette fogli V7.67 prima, V7.68 dopo**, esatta identità di **140 componenti /103 reti e intera mappa pin→rete**, topologia C102 BOOT/SW e L100 SW/5V e R100→R101∥C105→R102, RTN/GND separati e switch SHDN originale. Gate fail-closed: rimozione consentita soltanto di **sei** `endpoint_off_grid` delle sei nuove istanze, **28 errori/201 warning→28 errori/195 warning**, se nativamente riscontrati; qualunque nuova violazione blocca merge. Nessun waiver, nessun DRC globale fittizio.

**HOLD invariati:** [Issue #57](https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/57) manual eFuse fault/F200/ESD/temperature, 15 cross-module OPEN/HOLD, C103/C104 DC-bias/temp/aging, inrush BUCK, SG48 e Y1 pin10 HOLD, nessuna PCB unica né layout e DRC completo. **NO FAB / NO GERBER / NO PCBWAY / NO TX**.
