# V7.69 — C103/C104 TDK 22µF, 100mil CAD e limite di capacità reale BUCK 5V

13 novembre 2026. Baseline V7.68 main 140 componenti, 103 reti, ERC 28 errori/195 warning, 366 test PASS.

## 1 — ECO KiCad reale di uscita, non elettrico

Nuovo AUX `04_KiCad/Gerarchico_Alimentazioni_V7.69_TDK_OUTPUT_CEFF_GRID_REVIEW_NOT_FOR_FAB/02_BUCK_5V.kicad_sch`: due TDK automotive AEC-Q200 **C103/C104** 22µF 25V X7R ciascuno, **MPN `CGA6P3X7R1E226M250AB` invariato**, spostati su griglia 2.54mm: C103 centro (277,120)→(276.86,119.38)mm, C104 centro (304,120)→(304.80,119.38)mm. Spostati in modo solidale i terminali etichettati `5V_RF_PREREGULATED` e `GND_MAIN` e tutte le proprietà dei simboli, comprese **Manufacturer, MPN e Qualification = DC_BIAS_THERMAL_HOLD**. In totale **18 atomi** di sorgente consentiti: due centri, dodici coordinate proprietà, quattro etichette. Valori elettrici, librerie, footprint vendor candidato, altri fogli e reti invariati. Nuovo master sette fogli `04_KiCad/Assemblaggio_RX_Power_V7.69_TDK_OUTPUT_CEFF_GRID_REVIEW_NOT_FOR_FAB/`, cambia solo percorso al foglio AUX. **Nessuna PCB globale né DRC globale.**

## 2 — Fonte primaria TDK, senza inventare DC-bias numerici

TDK product center <https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=CGA6P3X7R1E226M250AB> e [characterization sheet TDK del MPN ESATTO](https://product.tdk.com/system/files/dam/doc/product/capacitor/ceramic/mlcc/charasheet/cga6p3x7r1e226m250ab.pdf) del 16 febbraio 2022: `CGA6P3X7R1E226M250AB` è AEC-Q200, 1210 (3.2×2.5mm), 22µF ±20%, 25V X7R, -55 a +125°C. La scheda mostra curva **DC Bias Cap. Change (%)** in caduta al crescere dei volt, un diagramma separato della temperatura con curva addizionale `TCBias(1/2 Rated)`, e grafico ESR vs frequenza; i grafici sono **curve di caratterizzazione, non limiti garantiti** di Ceff per ogni temperatura/lotto/aging. Non digitalizzare la curva in un numero sicuro a 5.0/5.3V senza dati tabellati e correlazione con temperatura. C103/C104 restano in HOLD, nessun MPN dichiarato approvato.

## 3 — Formula TI effettivamente applicabile, rischio in fSW minima

TI [TPS54202 Rev C Feb 2026](https://www.ti.com/lit/ds/symlink/tps54202.pdf) §7.2.3.5.2 **Equation 11** per il minimo teorico di capacità in un gradino di carico, trascurando ESR/transitorio loop: `Cout_req = 2 × ΔIout / (fSW × ΔVout)`. Con **ΔIout=1.5A e ΔVout=0.25V** come nell'esempio TI:
- `fSW=500kHz` tipico ⇒ **Cout_req = 24.00µF**.
- `fSW=390kHz` minimo TI tabella §5.5 ⇒ **Cout_req = 30.769µF**.
- I due C103/C104 marcati 22µF ciascuno danno **44µF solo nominali**; anche prima di aggiungere bias/temperatura/aging, il ±20% nominale può ridurre il totale a **35.2µF**.
- **Analisi di sensitività, non worst-case certificato:** se si ipotizzano simultaneamente fattore tolleranza 0.8, temperatura 0.85 e bias 0.95, si ottiene `44×0.8×0.85×0.95 = 28.424µF`, **inferiore ai 30.769µF richiesti dal modello semplificato a 390kHz**. I coefficienti 0.85 e 0.95 sono *ipotesi parametriche*, non la garanzia TDK a 5V e una determinata temperatura. Non assumere indipendenza delle curve; potrebbero essere correlate e non moltiplicabili in modo rigoroso.
- Otto scenari variando tolleranza 1/0.8, temperatura 1/0.85, bias 1/0.95 e l'equivalente droop a 390kHz sono generati in output CI JSON. Il requisito di 24µF o 30.769µF è **il solo criterio transitorio Eq11**, non una verifica di stabilità loop, ESR, ripple, induttore saturazione, EMI, reazione PWM né margine degli LDO.

**Conclusione di revisione:** anche se le due C da 22µF sono in produzione e corrispondono al package previsto, **non approvarle come sufficienti senza dati di Ceff verificabili a 5–5.30V su tutto il range termico, aging e load step**, insieme al minimum fSW e margini. Qualsiasi proposta di aggiunta di terzo condensatore o MPN alternativo richiederà nuovo budget, layout/vendor footprint e prove native. Non cambiare BOM per far passare un calcolo nominale.

## 4 — Gate e HOLD

`03_Verifiche/V7.69/test_tdk_c103_c104_output_ceff_native_v769.py`: 20 nuovi test; comparazione **KiCad9 CLI sette fogli V7.68 ↔ V7.69** con conservazione completa di 140 componenti/103 reti/tutti i pin→net, eFuse RTN pin8/17 distinto da GND_MAIN pin9, SW200 SHDN; ECC nessuna nuova connessione. ERC baseline **28/195**, target **28/193** consentendo soltanto due `endpoint_off_grid` C103/C104. Fallimento degli ERC/connessioni blocca merge; nessun PWR_FLAG/waiver. Numeri 24.00, 30.769, 28.424 e otto scenari sono audit numerici, NON misure hardware o simulazione SPICE con elementi non disponibili.

**HOLD:** [Issue #57](https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/57) F200/eFuse fuse current/thermal/fault-reset, SW200 meccanica/ESD, D200 TVS DNP, L100 termica/saturazione, sei LDO reale 5V budget, 15 crossmodule OPEN/HOLD, SG48/Y1 pin10 HOLD, 28 errori ERC e mancanza di PCB unica/DRC globale. **NO FAB / NO GERBER / NO PCBWAY / NO TX**.
