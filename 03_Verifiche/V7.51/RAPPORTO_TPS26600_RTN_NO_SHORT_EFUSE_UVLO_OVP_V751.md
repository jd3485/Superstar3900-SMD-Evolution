# V7.51 — Sicurezza elettrica TPS26600: RTN/GND, PowerPAD e soglie 13.8V

**Data:** 13 novembre 2026. **Baseline V7.50:** PR#54 integrata, master a 7 fogli con 138 componenti, 101 reti, zero footprint senza assegnazione, ERC 28 errori e 221 avvisi. Questo ECO **non modifica le connessioni**: aggiunge alla pagina eFuse una **nota esplicita con riferimento alla specifica primaria**, più test elettrici riproducibili con netlist KiCad9 reali. Non è una falsa riduzione ERC né una saldatura tra domini.

## Pericolo confermato dal produttore — impedire il ponte RTN↔GND

TI **TPS26600PWPT**, eFuse reverse-input-polarity, datasheet [SLVSDG2G Rev G](https://www.ti.com/lit/ds/symlink/tps2660.pdf) **§9.3.5.5 e §10.4 p37**: il pin **RTN (PWP8)** è il riferimento di controllo interno; **GND (PWP9)** è il ritorno dell'alimentazione di sistema. **RTN non va collegato direttamente a GND**, perché ciò disabilita la protezione contro l'inversione di polarità e può danneggiare il componente in tale condizione. TI richiede inoltre PowerPAD collegato al **piano RTN**, e i resistori/capacitori di ILIM, dVdT, UVLO/OVP riferiti a RTN. Questa separazione è differente da quella top-level AUX `GND_MAIN`↔MCU `GND`, pure non qualificata. *Non dedurre* che RTN possa essere unito a qualsiasi piano ground globale solo perché il nome include return.

La **netlist nativa** deve dimostrare queste relazioni:
- `U200 pin8 RTN` **=** `U200 pin17 PowerPAD` **=** `EFUSE_RTN`.
- `U200 pin9 GND` **=** `J100 pin2 GND_MAIN`, **diverso da EFUSE_RTN**.
- `R203 pin2` (ILIM), `C201 pin2` (dVdT) e `R202 pin2` (fondo partitore OVP) tutti a **EFUSE_RTN**.
- `U200 pin1/2` su `EFUSE_VIN`, alimentati attraverso `F200` dal `J100 pin1 PWR_13V8_AUX_RAW`; `U200 pin15/16` su `BUCK_VIN_PROTECTED`.
- Il root resta un **indice di 3 fogli senza pin gerarchici di alimentazione AUX→MCU**; `U6205.2 GND` non è elettricamente connesso a `U200.9 GND_MAIN`.

## Resistenze e soglie *solo statiche*

Valori esatti presenti nel file KiCad:
`R200 = 365kΩ ±1%`, `R201 = 16.2kΩ ±1%`, `R202 = 30.1kΩ ±1%`; catena `EFUSE_VIN → R200 → UVLO_NODE → R201 → OVP_NODE → R202 → EFUSE_RTN`. Le soglie eFuse secondo **TI SLVSDG2G §7.5** sono `V(UVLOR) = 1.175/1.19/1.225 V` (min/typ/max), `V(OVPR) = 1.17/1.19/1.225 V` (min/typ/max). Il test usa tutti gli **otto corner ±1% indipendenti** dei tre resistori, incrociati con i limiti del comparatore:

| Condizione del partitore in equilibrio, senza leakage | Trigger risalita ingresso teorico |
|---|---:|
| UVLO nominale | **10.571 V** |
| UVLO limite statico corners | **10.255 – 11.077 V** |
| OVP nominale | **16.261 V** |
| OVP limite statico corners | **15.694 – 17.052 V** |

**A 13.8V nominali**: il limite massimo UVLO statico è inferiore a 13.8V, e il minimo OVP statico è superiore. Il dato è una prova **di coerenza del partitore nel modello ideale**, non un'autorizzazione ad accendere il PCB. Non comprende leakage del nodo UVLO/OVP (TI specifica corrente leakage), capacità parassite, transitori dell'auto 12V, ripple, temperature PCB, cadute su fuse e cablaggio, slittamento soglia su fault, derating d'ingresso né esito delle prove ESD/surge/inversione. Non confondere i 13.8V nominali con tutte le condizioni dell'alimentazione in esercizio.

## ECO e test nativi

Nuovo `04_KiCad/Gerarchico_Alimentazioni_V7.51_TPS26600_RTN_SAFETY_REVIEW_NOT_FOR_FAB/01_EFUSE_AUX.kicad_sch`: **una sola stringa testuale di avviso visibile** `TI TPS26600 SLVSDG2G sect. 10.4: MAI CORTOCIRCUITARE RTN A GND...`; gli altri tre sottosheet copiati senza alcuna modifica. Nuovo master `04_KiCad/Assemblaggio_RX_Power_V7.51_TPS26600_RTN_SAFETY_REVIEW_NOT_FOR_FAB/` referenzia la nuova pagina eFuse via AUX senza cambiare pin, wires, componenti, reti o root MCU/RX.

`03_Verifiche/V7.51/test_tps26600_rtn_reverse_and_threshold_native_v751.py`: **15 test** fail-closed su fonte CAD, compatibilità netlist esportata KiCad9 eFuse/U200/return, corner resistivi, conservazione **138 componenti/101 reti**, zero differenze elettriche ed ERC **28 errori/221 avvisi** invariati. La verifica è più forte di una semplice ispezione text-search: interroga la **membership di ciascun pin nella netlist elettrica reale** ed impedisce un futuro corto RTN/GND. **Nessun nuovo workflow:** il job KiCad9 esistente `.github/workflows/v743_six_ldo_thermal_budget.yml` viene esteso con due export netlist/ ERC V7.51 prima/dopo, poi 15 unittest, riusando immagine e runner e conservando le 106 regressioni già presenti. Policy cost/safety da superare prima del merge.

**Da risolvere prima della PCB:** 28 errori ERC ancora reali (22 label_dangling intenzionali/incompleti e 6 power-pin-not-driven), 15 interfacce crossmodule, l'interconnessione elettrica qualificata AUX→MCU, `GND_MAIN` vs `GND`, scelta del return fisico RTN, PCB PowerPAD/thermal e corrente fusibile, ESP, cablaggio JST, reverse polarity hardware, budget buck 2A, sei LDO e Ceff MLCC, TCXO Y1 pin10 AFC/GND, SG48. **NO FAB / NO GERBER / NO PCBWAY / NO TX**. Nessuna PCB unificata né DRC globale, progresso storico ~10% senza incremento per una nota o un test.
