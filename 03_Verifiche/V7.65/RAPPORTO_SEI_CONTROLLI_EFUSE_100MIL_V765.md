# V7.65 — sei componenti di controllo eFuse sulla griglia KiCad 100mil (NO FAB)

13 novembre 2026. Baseline integrata **V7.64**: 140 componenti, 103 reti, ERC 28 errori/212 warning, KiCad9 292 test PASS. ECO CAD reale su rete UVLO/OVP/limitazione corrente/soft-start/MODE del TPS26600, senza cambiare alcun valore elettrico né terminazione.

## Modifica esatta e confini

Nuova AUX `04_KiCad/Gerarchico_Alimentazioni_V7.65_SIX_EFUSE_CONTROL_GRID_REVIEW_NOT_FOR_FAB/01_EFUSE_AUX.kicad_sch`. Traslate su griglia **2.54mm** le sei istanze: R200 (50,183)→(50.80,182.88), R201 (78,183)→(78.74,182.88), R202 (105,183)→(104.14,182.88), R203 (240,195)→(238.76,195.58), C201 (272,195)→(271.78,195.58), R204 (333,195)→(332.74,195.58) [millimetri]. Spostate insieme **12 etichette ancorate** `EFUSE_VIN`, `UVLO_NODE`, `OVP_NODE`, `ILIM_NODE`, `DV_DT_NODE`, `EFUSE_MODE`, `EFUSE_RTN`. Esattamente 36 atomi di source modificabili: sei posizioni simbolo, diciotto campi posizione ref/value/footprint e dodici label. Nessun filo aggiunto o mancante. Nessun PWR_FLAG e nessun corto massa.

**Tutti i componenti, MPN, valori e footprint restano identici:** R200=365k 1%, R201=16.2k 1%, R202=30.1k 1%, R203=8.2k 1%, C201=22nF X7R/50V, R204=402k 1% MODE_LATCHOFF_CANDIDATE→`EFUSE_RTN`. U200.8 RTN e U200.17 PowerPAD distinti da U200.9 `GND_MAIN`. SW200 KMR223NG ULC LFG 4 pad mantiene SHDN7↔pin1/4 e GND9↔pin2/3. C200 e D200 (DNP) restano V7.64. Tutti i fogli AUX restanti, MCU/RX, librerie e `fp-lib-table`, `sym-lib-table`, `.kicad_pro` identici. Nuova root `04_KiCad/Assemblaggio_RX_Power_V7.65_SIX_EFUSE_CONTROL_GRID_REVIEW_NOT_FOR_FAB/` cambia soltanto il percorso Sheetfile AUX.

## Prova nativa fail-closed

`03_Verifiche/V7.65/test_efuse_six_control_100mil_native_v765.py` 14 nuovi test: ricostruzione source mediante esattamente 36 differenze letterali autorizzate, KiCad9 export netlist/ERC prima V7.64/dopo V7.65 sullo stesso container; 140 componenti/103 reti, intero pin-to-net identico e mantenimento U200 MODE, SHDN, RTN/GND; ogni finding ERC esterno ai sei `endpoint_off_grid` identico. Atteso 28 errori e **212→206 warning** (sei warning geometrici realmente rimossi), **se** confermato dal KiCad9 nativo; fallimento blocca merge. Nessuna soppressione diagnostics.

Non sono state qualificate le soglie effettive UVLO/OVP, corrente limitatrice R203, dVdT C201 o recovery reale: servono vendor tolerance, temperature, transitori 13.8V, carico 5V/6 LDO ed esperimenti al banco. [Issue #57](https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/57) rimane APERTA. 15 RX/MCU/AUX cross-module OPEN/HOLD, 28 ERC errori residui, SG48 e Y1 pin10 HOLD, D200 DNP e nessuna PCB unificata/DRC globale. **NO FAB / NO GERBER / NO PCBWAY / NO TX**.
