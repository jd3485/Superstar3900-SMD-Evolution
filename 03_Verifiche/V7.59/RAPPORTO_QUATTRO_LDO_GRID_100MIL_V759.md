# V7.59 — Quattro regolatori TPS7A2033 MCU riallineati alla griglia 100mil (review NO FAB)

13 novembre 2026. **ECO geometrica reale** del foglio MCU, esclusivamente sui regolatori **U6203, U6204, U6205 e U6206**, che nel master V7.58 hanno geometrie fuori griglia. Nessuna nuova connessione elettrica, né qualifica di potenza o di dissipazione.

## Modifica

Nuovo foglio `04_KiCad/Modulo_MCU_CODEC_V7.59_FOUR_LDO_100MIL_GRID_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch` copiato dal MCU V7.58, e nuovo root `04_KiCad/Assemblaggio_RX_Power_V7.59_FOUR_LDO_100MIL_GRID_REVIEW_NOT_FOR_FAB/` che cambia solo l'indirizzo del foglio MCU. **Libreria simboli, numero/pin/nome/tipo/footprint, dispositivi AUX, RX e tutte le altre pagine invariati.**

| Riferimento | Centro prima mm | Centro dopo mm | Punti esterni ricollocati |
|---|---|---|---|
| U6203 | 710.00,320.00 | 711.20,320.04 | 4 label + 1 NC |
| U6204 | 810.00,415.00 | 810.26,414.02 | 4 label + 1 NC |
| U6205 | 870.00,415.00 | 871.22,414.02 | 4 label + 1 NC |
| U6206 | 930.00,415.00 | 929.64,414.02 | 4 label + 1 NC |

I pin esterni dei dispositivi sono a ±10.16mm dal centro: spostando i centri su multipli di 2.54mm, e ricollocando esattamente i loro label/NC, tutte le connessioni restano sul passo KiCad da 100 mil. Gli originali non hanno segmenti wire sulle coordinate dei pin coinvolti; l'uso della stessa etichetta garantisce conservazione della rete a condizione che il gate nativo lo confermi.

## Gate rigoroso

`03_Verifiche/V7.59/test_four_ldo_grid_native_v759.py` confronta esportazioni **reali KiCad9 7-sheet** V7.58 prima e V7.59 dopo, verifica che l'unica differenza sorgente siano quattro spostamenti di simbolo e 20 terminali label/NC, componenti **139**, reti **102**, identico mapping di ogni pin→rete; preserva differenza EFUSE_RTN/GND_MAIN e SHDN no-connect. Richiede **28 errori ERC invariati** (compresi gli errori reali di alimentazione U6203, nessun PWR_FLAG artificiale), **221 warning V7.58 → 217 warning V7.59** con rimozione di quattro `endpoint_off_grid` e confronto identico di tutti gli altri rilievi, eccetto coordinate fisiche del medesimo power pin U6203. Nessun waiver, soppressione di diagnostic o corto cross-module.

Se il test nativo risulta negativo la PR resta bloccata; il report numerico non è un DRC PCB. Questi LDO necessitano ancora del **budget termico 5V→3.3V**, reale corrente per canale, capacità di bypass, comportamento transitorio di carico, affidabilità PCB, e connessioni alimentazione tra moduli.

**Restano invariati:** Issue #57 ripristino eFuse indipendente, Issue #63 audit ERC storico, 15 interfacce OPEN/HOLD, SG48/Y1 pin10 HOLD, PCB unica non completata. **NO FAB / NO GERBER / NO PCBWAY / NO TX.**
