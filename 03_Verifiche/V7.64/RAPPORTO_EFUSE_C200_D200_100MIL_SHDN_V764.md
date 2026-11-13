# V7.64 — eFuse C200/D200 griglia 100mil e limiti reset SHDN (NO FAB)

13 novembre 2026. Baseline V7.63 KiCad9 140 componenti/103 reti, ERC 28 errori +214 warning, 276 test PASS. Modifica CAD vera limitata alla geometria dei terminali di ingresso U200 TPS26600: `C200` condensatore 100nF/100V e `D200` TVS SMBJ18CA **DNP**. Il TVS NON è approvato o installato, e questa revisione non lo rende una protezione transitori valida.

## Correzione CAD

Nuova copia `04_KiCad/Gerarchico_Alimentazioni_V7.64_C200_D200_INPUT_GRID_REVIEW_NOT_FOR_FAB/01_EFUSE_AUX.kicad_sch`. **C200** centro (83,94)→(83.82,93.98)mm; **D200** centro (104,94)→(104.14,93.98)mm. Mosse con il simbolo le rispettive due connessioni etichettate: C200 `EFUSE_VIN` e hierarchical `GND_MAIN`; D200 `EFUSE_VIN` e `GND_MAIN`. Pin terminali su griglia 2.54mm e simboli, footprint, valori, DNP, posizione degli altri componenti e reti invariati. Nuovo root `04_KiCad/Assemblaggio_RX_Power_V7.64_C200_D200_INPUT_GRID_REVIEW_NOT_FOR_FAB/` cambia esclusivamente Sheetfile del foglio AUX eFuse. `sym-lib-table`, `fp-lib-table`, `.kicad_pro`, altri tre fogli AUX, MCU e RX invariati.

## Reset manuale: specifica verificabile, non convalida hardware

TI [TPS2660x datasheet](https://www.ti.com/lit/ds/symlink/tps2660.pdf) §9.3.5.7 richiede SHDN basso **sotto 0.76 V** per DISABLE, alto **almeno 1.0 V** per ENABLE. Sotto 400mV il pull-down deve assorbire almeno 10µA. Tra 0.76 e 1.0 V lo stato è **indeterminato**. Il pulsante C&K [KMR2 ULC](https://www.ckswitches.com/media/1479/kmr2.pdf) riporta bounce ≤3ms; **non** è un tempo sufficiente di reset dimostrato, e non si deve interpretare la tensione di enable o il contatto come ripartenza garantita se il corto persiste. Una press-release completa deve essere misurata ai pin TPS26600 con corrente/temperatura/reverse-input reali e con un fault correttamente simulato; qualsiasi ESD da un attuatore accessibile all'utente è ancora HOLD. Nessun RC/TVS ESD inventato in questo ECO.

Test `03_Verifiche/V7.64/test_efuse_c200_d200_grid_shdn_native_v764.py`: confronto **KiCad9 nativo 7 fogli** prima/dopo, identità di 140 componenti, 103 reti e TUTTI i pin-net, RTN U200.8/17 non GND_MAIN U200.9, SHDN7=SW200.1/4, SW200.2/3=GND_MAIN, R204 MODE invariato. Confronto di **ogni** finding ERC con rimozione consentita esclusivamente dei warning `endpoint_off_grid` C200 e D200, senza waiver e con target **28 errors invariati, 214→212 warning**; se differisce, merge **BLOCCATO**. Modello logico SHDN con sei stati/casi di soglia, **non** simulazione SPICE né prova temporale.

**OPEN/HOLD:** 28 errori ERC reali, D200 `dnp yes`, eFuse fault reset SW200 da collaudare, selezione meccanica e ESD, 15 interfacce crossmodule OPEN/HOLD, U200 reverse RTN e F200/5V budget, C103/C104 Ceff bias/temp/aging, SG48/Y1 pin10, nessuna PCB completa né DRC globale. [Issue #57](https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/57) resta aperta. **NO FAB / NO GERBER / NO PCBWAY / NO TX**.
