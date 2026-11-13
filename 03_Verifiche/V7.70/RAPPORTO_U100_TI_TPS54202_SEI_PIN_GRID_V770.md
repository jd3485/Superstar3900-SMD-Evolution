# V7.70 — U100 TPS54202, pin fisici TI SOT-23 DDC e griglia 100mil

13 novembre 2026. Baseline `main` V7.69: 140 componenti/103 reti; ERC 28 errori, 193 warning; 386 Python PASS.

## Datasheet vendor, NON rimappare i pin

Texas Instruments [TPS54202 Rev C 2026](https://www.ti.com/lit/ds/symlink/tps54202.pdf), **§4 figura 4-1 package SOT-23 DDC top view** e Table 4-1: pin fisici 1=GND, 2=SW, 3=VIN, 4=FB, 5=EN, 6=BOOT. I sei numeri erano già corretti nel simbolo `S3900E:TPS54202_DDC`, ma i terminali locali erano fuori griglia KiCad. Ho corretto **solo le coordinate locali**, senza rinumerare né cambiare funzioni, tipo o footprint:
- GND pin1: (-20,-12)→(-20.32,-12.70)mm;
- SW pin2: (20,2)→(20.32,2.54);
- VIN pin3: (-20,10)→(-20.32,10.16);
- FB pin4: (20,-10)→(20.32,-10.16);
- EN pin5: (-20,-2)→(-20.32,-2.54);
- BOOT pin6: (20,12)→(20.32,12.70).

## ECO reale e libreria versionata

Nuovo foglio `04_KiCad/Gerarchico_Alimentazioni_V7.70_U100_TI_SOT23_6PIN_GRID_REVIEW_NOT_FOR_FAB/02_BUCK_5V.kicad_sch`. Il centro U100 (148,99)→(147.32,99.06) mm; ref/value/footprint property coordinate traslate e **tutte e sei le label attaccate ai veri estremi dei pin** aggiornate su griglia 2.54mm: GND_MAIN (127,111.76), BUCK_SW (167.64,96.52), BUCK_VIN_PROTECTED (127,88.90), BUCK_FB (167.64,109.22), BUCK_EN (127,101.60), BUCK_BOOT (167.64,86.36). Nessun nuovo circuito, passivo, nodo, waiver, GND/RTN short o PWR_FLAG. Le altre geometrie del buck V7.69 restano inalterate.

Libreria symbols versionata `04_KiCad/Librerie_Simboli_V7.70_TPS54202_U100_PIN_GRID_HOLD/S3900E.kicad_sym` conserva TUTTI gli altri simboli identici a V7.63 e varia soltanto coordinate dei sei pin U100. Nuovo master `04_KiCad/Assemblaggio_RX_Power_V7.70_U100_TI_SOT23_6PIN_GRID_REVIEW_NOT_FOR_FAB/` con solo Sheetfile AUX aggiornato e nuovo `sym-lib-table` per utilizzare tale libreria; `fp-lib-table`, `.kicad_pro`, fogli RX/MCU/AUX non-BUCK e tutta la footprint library sono byte-identici. **U100 mantiene MPN TPS54202DDCR e footprint standard Package_TO_SOT_SMD:SOT-23-6** (il suo package/land e produzione devono comunque essere valutati nel layout reale).

## Native KiCad9 fail-closed

`03_Verifiche/V7.70/test_tps54202_u100_six_pin_100mil_native_v770.py` aggiunge 20 test: esatte 16 sostituzioni di coordinate schema (6 embedded pin, 6 label, 4 istanza/proprietà), esattamente 6 variazioni coordinate libreria standalone e solo 1 cambio di percorso sym-lib-table; sette fogli KiCad9 originale V7.69 vs revisione V7.70 `kicad-cli sch export netlist` e `sch erc`, mappa COMPLETA di 140 componenti/103 reti e TUTTI i pin→net invariati; test specifico mapping vendor PIN→net; eFuse RTN8/17 separati da GND9, SW200 SHDN7 immutato. Solo **un** warning U100 `endpoint_off_grid` nativamente riportato da KiCad9 (pin3 VIN) è autorizzato a sparire, benché siano riallineati tutti e sei i terminali, **ERC atteso 28 errori /193→192 warning**; ogni altro finding diverso blocca merge, nessuna waiver. Verificare risultati effettivi CI prima del merge.

## HOLD non sbloccati

Gli errori ERC reali e collegamenti incerti rimangono; **15 interfacce crossmodule OPEN/HOLD**, [Issue #57](https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/57) F200/eFuse 1.5A corrente limite e pulsante SHDN access/ESD, C103/C104 TDK Ceff worst-case e loop TPS54202, L100 15µH corrente saturazione, budget carichi sei TPS7A2033 e termica, SG48/Y1 pin10 HOLD, D200 TVS DNP. **Nessuna PCB unificata e nessun DRC globale. NO FAB / NO GERBER / NO PCBWAY / NO TX**.
