# V7.72 — Sei condensatori reali di bypass sui due LDO PLL, 100mil KiCad

14 novembre 2026. Baseline live `main` V7.71, 140 componenti, 103 reti, ERC **28 errori/192 warning**, CI 428 test superati.

## ECO nativa vera (non soltanto rapporto)

Nuovo foglio `04_KiCad/Gerarchico_Alimentazioni_V7.72_PLL_SIX_LDO_BYPASS_GRID_REVIEW_NOT_FOR_FAB/03_PLL_LDO_TCXO.kicad_sch`:

| Componente | Funzione e valore conservati | Prima (mm) | Dopo (mm) |
|---|---|---|---|
| C50 | IN U2, 2.2µF/10V X7R, 5V_RF_PREREGULATED→GND_MAIN | (374,122) | (373.38,121.92) |
| C51 | OUT U2, 4.7µF/10V X7R, 3V3_PLL_INPUT_FROM_LDO→GND_MAIN | (439,122) | (439.42,121.92) |
| C52 | OUT U2, 10µF/10V X7R, stessa OUT | (464,122) | (464.82,121.92) |
| C53 | IN U3, 2.2µF/10V X7R, 5V_RF_PREREGULATED→GND_MAIN | (374,215) | (373.38,215.90) |
| C54 | OUT U3, 4.7µF/10V X7R, 3V3_REF_LDO→GND_MAIN | (439,215) | (439.42,215.90) |
| C55 | OUT U3, 10µF/10V X7R, stessa OUT | (464,215) | (464.82,215.90) |

Per ciascun condensatore viene tradotto il centro, le tre coordinate proprietà Reference/Value/Footprint, la label **superiore** (rete IN/OUT), il **vero tratto di wire collegato al terminale inferiore** e la label **GND_MAIN** terminale finale. L'estremità inferiore del wire è anche riportata su griglia a 2.54mm: i fili vengono mantenuti (non soppressi). **42 atomi sorgente** consentiti, tutti i sei condensatori e i loro 12 contatti restano fisicamente presenti, valori e footprint `Capacitor_SMD:C_0805_2012Metric` invariati; nessuna alterazione a MCU/RX/eFuse, PLL U2/U3 pinout o rail. Spostamento di CAD schematico **NON è layout fisico PCB**, non viene qualificato il valore di capacità effettiva DC-bias.

Nuovo master `04_KiCad/Assemblaggio_RX_Power_V7.72_PLL_SIX_LDO_BYPASS_GRID_REVIEW_NOT_FOR_FAB/` cambia soltanto Sheetfile AUX verso il foglio V7.72; tutta la libreria simboli versione V7.70, lib/footprint tables e gli altri fogli sono byte-identici a V7.71. La V7.71 annotazione termica nativa rimane conservata.

## Prove obbligatorie

`03_Verifiche/V7.72/test_pll_six_ldo_bypass_100mil_native_v772.py` verifica:
- `kicad-cli sch export netlist` e `kicad-cli sch erc` nativi su **tutti e sette i fogli** V7.71 prima e V7.72 dopo;
- 140 componenti /103 reti, *mappa completa di ogni pin→rete*, C50/C53 su 5V/GND, C51/C52 in parallelo sulla 3V3_PLL/GND, C54/C55 sulla 3V3_REF/GND, eFuse RTN8/17 ≠ GND_MAIN9, SW200/GND/SHDN invariati;
- baseline ERC 28 errori /192 warning, vietata QUALSIASI nuova violazione. Solo le effettive vecchie istanze `endpoint_off_grid` attribuite a C50..C55 e ai loro sei fili possono sparire, e nessun altro warning può essere eliminato artificialmente. Il numero finale warning **deve risultare dal run nativo**, non è ipotizzato o forzato;
- dizione `NO FAB/TX`, classificazioni D200 DNP, sei reali LDO thermal HOLD e 15 interfacce OPEN/HOLD.

## Rischi aperti NON ridotti con il miglioramento schematico

Conservare U2/U3 TPS7A2033 SOT23 thermal e current budget **V7.71**: TI [SBVS338H datasheet](https://www.ti.com/lit/ds/symlink/tps7a20.pdf) thetaJA 187.1°C/W su PCB di riferimento e 300mA rating, non carico reale. Non equiparare i `2.2µF/4.7µF/10µF` etichettati ai loro valori efficaci sotto bias/temp/aging. Qualificare vera Tj/TA, correnti di ciascun rail e calore su PCB, PSRR/rumore PLL, ripple, decoupling e layout analogico/RF, C103/C104 e TPS54202 loop, L100 saturation fault, F200 eFuse/SHDN reset e D200 DNP. Le interfacce crossmodule restano separate, SG48/Y1 pin10 HOLD. Non esiste PCB unica né DRC globale. **NO FAB / NO GERBER / NO PCBWAY / NO TX**.
