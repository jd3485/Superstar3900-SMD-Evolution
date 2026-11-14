# V7.74 — sei reali errori ERC power_pin_not_driven, provenienza e ritorno alimentazione

14 novembre 2026. `main` V7.73: 140 componenti/103 reti, ERC **28 errori e 180 warning**, 461 PASS. Questa revisione approfondisce **sei** errori specifici, non dichiara falsamente che siano risolti.

## Analisi elettrica e source/return da circuiti reali

| Riferimento | Pin | Rete nativa da verificare | Percorso reale già rappresentato | Limitazione |
|---|---:|---|---|---|
| U200 TI TPS26600 eFuse | 1 IN | EFUSE_VIN | F200 (fusibile 1.5A) → IN | Origine esterna PWR_13V8_AUX_RAW e ritorno/non-inversione non convalidati |
| U200 | 8 RTN | EFUSE_RTN | RTN8 e RTN17 stessa rete | **RTN separata da GND_MAIN pin9**, non cortocircuitare |
| U2 TI TPS7A2033 PLL | 1 IN | 5V_RF_PREREGULATED | Alimentazione 5V condivisa con LDO U3 e buck TPS54202 nello schema AUX | Non implica che sorgente/avvio/transienti siano qualificati |
| U2 | 2 GND | GND_MAIN | Ritorno 5V lato AUX | Piano GND/PCB e correnti di ritorno non provati |
| U6203 TI TPS7A2033 MCU | 1 IN | 5V_DIGITAL_FILTERED | Uscita del bead FB6201 e altre LDO digitali | Ingresso FB6201 e crossmodule non sono una sorgente qualificata |
| U6203 | 2 GND | GND | Ground MCU distinto dal dominio GND_MAIN AUX | Non connettere a caso i domini separati per silenziare ERC |

Tutte queste informazioni sono **ipotesi di topologia da confrontare con la netlist KiCad9**; il gate in `03_Verifiche/V7.74/test_six_power_pin_source_return_native_v774.py` impone la corrispondenza vera delle sei reti e dei collegamenti F200, FB6201, U3, U200 RTN8/17. Nessun generatore di potenza è stato qualificato per il connettore di alimentazione in ingresso o per il futuro PCB.

## Vera ECO negli schemi: avvertimenti costruttivi vincolanti

Versionate nuove istanze degli schemi:
- `04_KiCad/Gerarchico_Alimentazioni_V7.74_SIX_PWR_SOURCE_RETURN_PROVENANCE_HOLD/01_EFUSE_AUX.kicad_sch`: nota ad U200 di non collegare EFUSE_RTN a GND_MAIN, F200 e sorgente esterna HOLD.
- `04_KiCad/Gerarchico_Alimentazioni_V7.74_SIX_PWR_SOURCE_RETURN_PROVENANCE_HOLD/03_PLL_LDO_TCXO.kicad_sch`: nota su U2 ingresso 5V/ritorno, sei LDO reali e 5V ancora HOLD.
- `04_KiCad/Modulo_MCU_CODEC_V7.74_U6203_PWR_SOURCE_RETURN_PROVENANCE_HOLD/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch`: nota su U6203/FB6201 e dominio GND locale da non cortocircuitare.
- Il master versionato `04_KiCad/Assemblaggio_RX_Power_V7.74_SIX_PWR_SOURCE_RETURN_PROVENANCE_HOLD/` punta **solo** alle nuove copie AUX e MCU. Altri elementi/libri KiCad e schemi BUCK/MCU/RX invariati, nessuna modifica a fili, simboli, pin, BOM, footprint, valori o altre etichette.

Le tre note sono vere proprietà grafiche degli schemi CAD: **non rappresentano circuiti nuovi, prove sperimentali o risoluzione degli errori ERC**.

## Gate nativo e esito atteso

Si usa il workflow KiCad9 esistente, netlist/ERC nativi **sette fogli prima e dopo**, 15 unit test per impedire falsi aggiornamenti: 140 componenti, 103 reti, **intera mappa pin→rete esatta**, tre sole annotazioni, 28 errori e 180 warning **identici anche nelle singole segnalazioni**. Sei originari `power_pin_not_driven` restano esplicitamente nell'ERC. `EFUSE_RTN` resta separato da `GND_MAIN`, ground MCU distinto, 22 dangling label lasciate intatte.

**Dati mancanti prima di un ECO elettrico:** alimentatore e connettore PWR_13V8_AUX_RAW, configurazione masse/ritorni PCB, mappa completa dei quindici intermodulo, correnti e transitori carichi sei TPS7A2033, simulazione e misura del ciclo di startup/fault F200/eFuse/TPS54202, L100, C103/C104, C50..C55. [Issue #57](https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/57) OPEN. **NO FAB / NO GERBER / NO PCBWAY / NO TX, SG48/Y1 pin10 HOLD, D200 TVS DNP**.
