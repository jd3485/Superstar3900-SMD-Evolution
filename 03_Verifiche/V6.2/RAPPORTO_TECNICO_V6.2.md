# Superstar 3900 SMD Evolution — Rapporto tecnico V6.2

Data: 9 novembre 2026. **FASE PROGETTAZIONE COMPLETA RADIO / NON FAB / NO TX.**

## Obiettivo e progresso reale

La V6.2 aggiunge la **scheda candidata di supervisione alimentazioni e interblocco HW PA/TX** a livello di componenti, con netlist a pin reali, distinta componenti e architettura di sicurezza a 3,3 V. Invariati i file KiCad storici, lo schema RX e il manuale. La radio intera non è completata: alimentatore protetto, PLL/FI/TX, PA reale, misure, accordatore e PCB multipli restano da progettare.

Il blocco contiene **61 componenti candidati, 190 associazioni pin-rete e 15 porte logiche** (13 AND e 2 inverter), riportati negli allegati JSON e CSV. Si tratta di **uno schema a componenti tabellare, non di uno schematico KiCad nativo**.

## Interblocco hardware — principio

- U801 **TPS3823A-33**: reset/watchdog 3V3, uscita /RESET `SUP_3V3_OK`, 200 ms nominali di ritardo rilascio / 1,6 s nominale watchdog, dipendenti dalle condizioni datasheet.
- U802 **TPS3700**: due uscite open drain, separatamente pull-up a 3V3; misura batteria protetta tramite due partitori e rileva tensione bassa o alta.
- U803/U804 inverter SN74LVC1G04: PTT attivo basso trasformato in segnale alto; veto PA trasformato in `NOT_PA_MODE_HW`.
- U805–U817 porte SN74LVC1G08: richieste audio/relè separate dalle condizioni necessarie per il consenso futuro TX.
- J801 jumper di prova **non montato (DNI)**; `TX_BENCH_KEY` resta a zero tramite resistenza da 47k e il pin logico `TX_ENABLE_HARD` non comanda alcuna emissione RF. J802 loop termico/SWR futuro resta aperto fino alla progettazione delle protezioni.

Il segnale logico TX candidato soddisfa nel modello:

`TX_ENABLE_HARD = SUP_3V3_OK & BAT_UV_OK & BAT_OV_OK & RX_SAFE_NC & !PA_MODE_HW & FAULT_LOOP_OK & TX_ARM_REQUEST & !PTT_N & TX_BENCH_KEY`.

Nessun gate software bypassa l'assenza del jumper, un'alimentazione fuori finestra, PA o la perdita del loop di protezione. Questo vale **nel modello logico ideale**, non prova tolleranza a guasti nei componenti reali.

## Scoperta e correzioni richieste alle interfacce V6.1/V6.0

**ECO-V62-01 (obbligatoria):** il secondo polo del selettore PA definito DPST nella V6.1 non offre un contatto normalmente chiuso RX. Per ottenere una linea `RX_SAFE_NC` che cada a zero in caso di filo aperto, serve un **contatto indipendente SPDT break-before-make** (COM=3V3, NC=RX_SAFE_NC, NO=PA_MODE_HW) mantenendo il sensore PA della MCU su altro polo.

**ECO-V62-02:** MCU STM32 pin33 **PB11** (riserva V6.1) assegnato al watchdog `WDI_HEARTBEAT`, pin57 **PB4** assegnato a `TX_ARM_REQUEST`. PA9/WCLK audio e SWD non cambiano. È un cambio del contratto candidato, non una modifica nascosta ai file storici.

**ECO-V62-03:** `AMP_SD` e comando relè non possono restare collegati direttamente alle uscite MCU. Il ramo V6.0/V6.1 va reinstradato attraverso V6.2: PA8 → `AMP_SD_REQUEST` → porte → `AMP_SD` e PA10 → `PA_RELAY_CMD` → porte → `PA_RELAY_EN` e successivo driver da dimensionare.

## Analisi numerica realmente eseguita

Partitori candidato: `287 kΩ / 10 kΩ` (UV) e `374 kΩ / 10 kΩ` (OV), riferimento tipico 0,4 V. **Soglie nominali 11,88 V e 15,36 V**. Analisi Monte Carlo a semi fisso con **50,000 campioni**, tolleranze uniformi ±1% (per ogni resistore e per riferimento), senza modellare ogni errore reale dell'integrato, isteresi, disturbi o temperatura completa:

| Soglia | Min simulato | Nominale | Max simulato |
|---|---:|---:|---:|
| Sottotensione UV | 11.553 V | 11,88 V | 12.224 V |
| Sovratensione OV | 14.920 V | 15,36 V | 15.805 V |

Per la batteria nominale **13,8 V**, tutti i 50,000 campioni risultano dentro la finestra *del modello*. **Non è una certificazione delle soglie reali né una simulazione SPICE**. La distribuzione uniformemente campionata non dimostra copertura statistica di guasti rari o dei worst-case industriali.

## Test e regressioni effettivamente eseguiti

- **31 test V6.2** superati, fra cui verifica di **8.192 stati digitali** delle 13 variabili logiche, controllo pin fisici, coerenza dei jumper e perturbazioni introdotte intenzionalmente.
- Il test include **50.000 combinazioni numeriche** nel codice di prova e la simulazione Monte Carlo autonoma produce un altro dataset riproducibile da 50.000 valori con un diverso seme.
- Regressioni selezionate V5.9, V6.0, V6.1 (55 test MCU, 5 integrazione audio) e V6.2 **tutte PASS**. Non è stata rieseguita l'intera storia dalla V4.0.
- `kicad-cli` e `ngspice` **non presenti nell'ambiente**: niente ERC/DRC nativi, SPICE analogico o collaudo hardware. I risultati della logica sono deterministici e numerici, non segnali misurati.

## Criticità / restrizioni aperte

Il modello non garantisce comportamento sicuro in cortocircuiti dei contatti verso 3V3, gate guasto alto, stuck-high MCU, guasti comuni dell'alimentazione o disturbi EMC. Mancano lo schema KiCad, verifica dei limiti di input dei componenti nei transitori 13.8V, qualificazione di tutti i sensori, relè driver, fault feedback hardware, layout/ESD, stop TX indipendente e supervisione del vero amplificatore RF. L'uscita `TX_ENABLE_HARD` è un segnale 3,3 V NON collegato al finale RF. **Non rilasciare PCB, Gerber, produzione o TX**.

## Fonti produttore

- [TI TPS3823](https://www.ti.com/product/TPS3823) — reset/watchdog
- [TI TPS3700](https://www.ti.com/product/TPS3700) — finestra 18V, comparator OD
- [TI SN74LVC1G08](https://www.ti.com/product/SN74LVC1G08) — AND 2 ingressi
- [TI SN74LVC1G04](https://www.ti.com/lit/ds/symlink/sn74lvc1g04.pdf) — NOT singolo

**Prossima V6.3:** progettare il modulo di ingresso 13,8 V (fusibile, polarità inversa, TVS, filtri, convertitori 5V/3,3V, sequenziamento e dissipazione), con calcoli e simulazioni numeriche dove possibili. La verifica globale del ricetrasmettitore avverrà dopo che tutti i moduli saranno stati progettati; proseguono nel frattempo test incrementali a ogni revisione.
