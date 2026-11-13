# V7.54 — TPS54202, filtro 5V e DC-bias MLCC: verifica parametrica, NO FAB

**Data 13 novembre 2026.** Baseline CAD V7.52 (V7.53 tests-only) NON modificata. Questo contributo misura il rischio di margine di capacità e transitori, senza dichiarare un carico reale o una qualificazione fisica.

## Riferimento produttore e schema reale

TI [TPS54202 SLVSD26C Rev C, febbraio 2026, Tabella 7-2, Equazione 11, §7.4](https://www.ti.com/lit/ds/symlink/tps54202.pdf): schema tipico 5V ha 15 µH L, **44 µF** capacità di uscita nominale, FB 100k / 13.3k e condensatore feedforward 75pF, con frequenza 500kHz e soft-start interno 5ms. I parametri del master V7.52 sono L100 15µH Bourns SRP1038A-150M, C103+C104 **2×22µF 25V X7R** con soli footprint generici `C_1210_3225Metric`, R101=100k, R102=13k3 e C105=75pF. **La parità dei valori nominali NON convalida capacità effettiva né stabilità.** Nessun MPN di C103/C104 è qualificato e la riduzione DC-bias, tolleranza/aging e ripple non è verificata.

Il modello V7.54 non assume alcuna curva reale MLCC. Parametrizza la frazione di capacità trattenuta fra 0 e 1 (esempi puramente ipotetici): 100%→44µF, 80%→35.2µF, 50%→22µF. Con esempio TI ΔIout=1.5A e ΔVout ammissibile=0.25V (5%) per due cicli a 500kHz, Eq.11 richiede almeno **24µF effettivi** solo per quel criterio. Retention minima 24/44≈**54.55%**. Questi numeri non impongono una specifica di ripple/EMC reale né sostituiscono analisi complessiva dei poli dell'anello.

Il modello ideale di due cicli dà ΔV ≈ 2×ΔI/(f×Ceff). A 80% ≈**0.1705V** (per il solo criterio); al 50% ≈**0.2727V**, maggiore dello scenario 5% scelto dal datasheet. Il ripple ideale dell'induttore `ΔIL=(VIN−VOUT)×(VOUT/VIN)/(L×f)` va calcolato sulla vera VIN a U100 dopo le cadute eFuse, non sulla sorgente J100. Corrente di picco condizionale a 2A di carico: 2A+ΔIL/2, da confrontare con specifica della bobina e corrente switch su tutta l'area operativa, margini termici e transienti.

## Vincoli di rilascio

1. Identificare MPN C103/C104 e scaricare **curve del produttore a 5V DC**, temperatura, dispersione/aging; controllare footprint e Ceff WORST-CASE (non nominale).
2. Specificare il vero gradino di carico AUX/MCU/RX, ripple e tensione minima accettabile; ricalcolare Ceff, risposta dinamica e margine dell'anello. Valutare se servano modifiche CAD, senza aggiungere condensatori arbitrari (aumenterebbero inrush).
3. Vincolare VIN minimo reale su buck sotto carico, 5V budget, Iin eFuse/F200, corrente picco 15µH, capacità bootstrap C102 e C100 10µF sotto bias; simulare e misurare su prototipo in seguito.
4. **Issue #57** reset eFuse MODE latch-off indipendente da MCU ancora OPEN: SHDN pin7 NC, nessun fake GND_MAIN→EFUSE_RTN, nessuna auto-retry senza stress test.
5. 15 interfacce crossmodulo OPEN/HOLD, 28 ERC e 221 warning precedenti, SG48/Y1 AFC HOLD; **NO FAB / NO GERBER / NO PCBWAY / NO TX**.

`03_Verifiche/V7.54/test_tps54202_ceff_transient_native_source_v754.py` contiene 18 controlli Python sulle reali proprietà dello schema e sull'analisi condizionale. È una validazione numerica limitata; i precedenti test KiCad9 devono rimanere verdi. **Nessuna ECO KiCad in V7.54, percentuale PCB invariata.**
