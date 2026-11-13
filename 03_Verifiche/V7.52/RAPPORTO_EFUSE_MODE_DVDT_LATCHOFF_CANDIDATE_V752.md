# V7.52 — Scelta REALE di MODE sul TPS26600: controllo dVdT vs fault auto-retry

**Data:** 13 novembre 2026. **Baseline main V7.51 PR#55 integrata**, 138 componenti / 101 reti / 0 footprint missing / ERC 28 errori e 221 avvisi. **La V7.52 è una ECO circuitale candidata**, non una simulazione o approvazione di sicurezza dell'hardware. I collegamenti AUX→MCU e ritorni massa cross-module rimangono aperti.

## Difetto funzionale/contratto precedente

Nel foglio `01_EFUSE_AUX.kicad_sch` V7.51, **TPS26600PWPT U200 pin6 MODE** è `no_connect`; **C201 22nF da U200 pin12 dVdT a EFUSE_RTN** è presente. Il datasheet originale TI **SLVSDG2G Rev G**, §9.4 *Device Functional Modes*, **Tabella 2 pagina stampata 27** https://www.ti.com/lit/ds/symlink/tps2660.pdf descrive tre strategie NON equivalenti per TPS26600:

| Collegamento MODE | Modalità | Avviamento/risposta |
|---|---|---|
| MODE aperto (V7.51) | Circuit breaker con auto-retry | Avviamento con limite I(OL); fault timer e riavvio dopo protezione termica, **NON selezione della rampa dVdT della seconda modalità** |
| MODE direttamente a RTN | Current limit con auto-retry | Avviamento/overload limitati a I(OL), anche qui comportamento diverso |
| **MODE → resistore 402kΩ → RTN** | **Current limit con latch-off** | **Rampa dVdT attiva durante startup** e limitazione I(OL), ma dopo un fault il dispositivo **resta spento** finché non viene ripristinato (ciclo alimentazione o SHDN, da verificare nel sistema) |

**Decisione tecnica provvisoria V7.52:** preferire una rampa dVdT realmente selezionata per migliorare la prevedibilità dell'inrush della radio. **Tradeoff esplicito: latch-off**, non mantenere l'aspettativa di auto-retry. SHDN pin7 resta non cablato (internal pull-up, TI §9.3.5.7), perciò la procedura di reset manuale/digitale non è ancora progettata e deve rimanere **HOLD**. In particolare non inventare `MCU_SHDN` o unirlo a un GPIO non dimostrato, né garantire che un firmware possa ripristinare l'eFuse in questa configurazione.

**ECO schematic reale:** una nuova copia `04_KiCad/Gerarchico_Alimentazioni_V7.52_EFUSE_MODE_DVDT_LATCHOFF_REVIEW_NOT_FOR_FAB/01_EFUSE_AUX.kicad_sch` sostituisce **solo** il marker `no_connect` all'endpoint U200.6 MODE (173,120) con etichetta locale `EFUSE_MODE` e aggiunge **R204 402kΩ ±1%** con footprint candidato `Resistor_SMD:R_0603_1608Metric`, fra `EFUSE_MODE` e `EFUSE_RTN`. Sono aggiunte note visibili con avviso *latch-off e recovery HOLD*. Tutti gli altri tre fogli AUX sono byte-identici a V7.51; nuovo master `04_KiCad/Assemblaggio_RX_Power_V7.52_EFUSE_MODE_DVDT_REVIEW_NOT_FOR_FAB/` mantiene MCU/RX e root isolati. **Non è un corto RTN↔GND**: non toccare U200.8 RTN = PowerPAD pin17, U200.9 GND = J100.2 GND_MAIN.

## Sizing dVdT preliminare, NON signoff

TI **TIDUEP8 Eq2** https://www.ti.com/lit/ug/tiduep8/tiduep8.pdf riporta approssimazione `C_dVdT≈t/(8000×VIN)`, quindi `t≈8000×VIN×C_dVdT`. Con `VIN=13.8V`, `C201=22nF nominali` il modello ideale dà **t≈2.4288ms**. Il valore è solo illustrativo: non contiene Ceff di C201, input leakage, supply decoupling, condensatori e carichi a valle, soft-start del buck TPS54202, fault timer, input inrush, tolleranza VOUT, EMC/ripple, alimentazione automotive o condizioni di temperatura. **Non** dedurre assorbimento o temperatura reale dall'esempio; occorre prova ngspice/circuitale validata e misure su hardware.

**Tensione di sistema, correnti e sicurezza non qualificate:** il datasheet TI distingue I(OL), current limit e fast-trip; l'esistenza di F200 1.5A, R203 8.2k, buck TPS54202 2A output e J100 rated non determina da sola un dimensionamento sicuro a 13.8V. Il fault latch-off può rendere la radio inutilizzabile dopo un transitorio fino a un reset; è un **rischio operativo deliberato che richiede prova e decisione di sistema**. La modifica deve restare **REVIEW/NO FAB** finché non sono chiari profilo d'uso, rumore RF, Recovery e worst-case.

## Gate nativo prima/dopo e Actions ottimizzato

`03_Verifiche/V7.52/test_tps26600_mode_latchoff_native_v752.py` prevede **12 test** che verificano:
- nessuna modifica salvo U200.6 `no_connect → EFUSE_MODE`, R204 402k 1% e annotazioni;
- originale **138 componenti/101 reti**, nuovo **139 componenti/102 reti** (un solo nuovo nodo `EFUSE_MODE`); zero variazioni per tutti i pin preesistenti, **solo tre nuovi endpoint** (`U200.6`, R204.1 e R204.2);
- R204 esattamente fra MODE e RTN, **non** a GND_MAIN, confermata in netlist KiCad9 e precedenti U200.8 RTN, U200.17 PowerPAD, U200.9 GND separati;
- C201 resta sull'ingresso dVdT, **SHDN / FLT / IMON non forzati**, ERC base 28/221 non deve peggiorare, 0 footprint missing;
- il comportamento di riavvio latch-off **non viene falsamente classificato come già approvato**.

In `.github/workflows/v743_six_ldo_thermal_budget.yml` si **riutilizza il job nativo KiCad9 esistente** (senza nuovi workflow o pip/apt) con export/ERC old/new e i 12 test V7.52; mantiene le **121 prove V7.43–51**. Il controllo policy costi/sicurezza deve passare separatamente. Prima di descrivere PASS e merge verificare run_id reale e rapporto nativo nel relativo artifact.

**HOLD:** ancora 28 ERC baseline, 15 interfacce OPEN/HOLD, `GND_MAIN` vs `GND`, `EFUSE_RTN` vs GND_MAIN **sempre distinti**, Y1 TCXO pin10 AFC/GND, SG48, Ceff MLCC, protezione reverse, fault recovery, calibrazione del limite corrente, energia di avvio, termica e DRC di PCB unica non eseguita. **NO FAB / NO GERBER / NO PCBWAY / NO TX**, progresso PCB storico ~10% non aumentato per ECO candidata.
