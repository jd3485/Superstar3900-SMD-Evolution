# Superstar 3900 SMD Evolution — Rapporto tecnico V7.20: ngspice, 270 canali e sei power ERC

**11 novembre 2026 — verifica circuitale/di integrazione, NON nuova PCB. NO FAB / NO TX.**

## 1. Obiettivo, risultati nativi e limiti

La V7.20 prosegue il lavoro sullo schematico della radio completa dopo l'ECO V7.19, **senza creare un circuito integrato elettricamente o una PCB unica in assenza delle qualifiche**. I tre tracciati verificati sono:
1. **ngspice nativo** sul file reale di filtro `04_KiCad/Bozze_pre_KiCad/Filtro_LMX2572_V0.6_ac.cir` (passivo, R2/C2/C1/R3/C3), confrontato con un'analisi nodale complessa indipendente in Python standard library.
2. **270 configurazioni Integer-N reali del file di piano frequenze**, con due sweep differenti: 2430 casi ipotetici di sensibilità (Kvco e Icp liberi) e 270 casi addizionali modellati sui dati *tipici* TI per VCO3/VCO4 e la corrente CP nominale.
3. **6 errori `power_pin_not_driven`** del master KiCad completo a 7 fogli, estratti da **veri ERC e netlist native KiCad9** e classificati per pin/reticolo, senza alcun PWR_FLAG o falso ponticello verso massa.

**CI nativa:** [GitHub Actions 42971210346](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42971210346) **success**, 18 nuovi unit test V7.20 + **266 regressioni V7.19–V7.1 =284 PASS**, 0 FAIL, 0 SKIP. In più KiCad9 CLI reale, ngspice AC reale e controllo dei 6 nodi di alimentazione. Nessun FPGA synthesis nuovo, hardware, PLLatinum Sim, PCB globale, ordine o TX.

## 2. Due modelli numerici indipendenti contro il circuito SPICE reale

Fonte: `03_Verifiche/V7.20/verify_pll_spice_270_v720.py`. Dal circuito esatto del progetto vengono verificati cinque elementi nominali **C1 220pF, C2 120nF, C3 2,2nF, R2 620Ω e R3 22Ω**. La rete ha due nodi analogici CPOUT e VTUNE con ramo R2–C2 in serie. `ngspice -b` analizza 501 punti AC a 10 Hz–1 MHz; il verificatore ricalcola separatamente l'impedenza complessa vista a VTUNE:

\[
 Z_{Vtune}(s)=\frac{1/R3}{(sC1+1/(R2+1/(sC2))+1/R3)(sC3+1/R3)-(1/R3)^2}
\]

Lo **scarto relativo massimo in modulo** fra ngspice e analisi nodale è **8,31×10⁻⁷** (~0,0000831%) su 501 punti. La sintesi storica V0.6 è riprodotta entro la tolleranza dichiarata: **~4.015,5 Hz crossover**, **~59,76° margine** con Icp assunto 2,5mA, Kvco assunto 55 MHz/V e N 3750.

Questa è una verifica di **coerenza matematico-SPICE del filtro passivo**, non una simulazione di tutti i blocchi PLL né una misura di risposta nel tempo, phase noise, spurs o della variabilità reale.

## 3. Piano a 270 canali e Kvco *tipico* TI

Fonte del piano esatto: `02_Piano_Frequenze/Tabella_LMX2572_270_Integer_N_V0.5.csv`. Viene accettato solo se contiene **270 valori univoci N=3631…3900**, fPFD=1,28MHz, Numerator=0, Denominator=1 e fVCO=N×fPFD. Lo stato di tutte le righe rimane **`frequency_arithmetic_only`**, non firmware validato.

Fonte vendor [TI LMX2572 SNAS740B, tabella 135 p.64 ed equazione 4 p.65](https://www.ti.com/lit/ds/symlink/lmx2572.pdf):
- **VCO3**: fVCO 4,20–4,65 GHz, Kvco tipico da 47 a 64 MHz/V, **2 canali** a 4,64768–4,64896 GHz.
- **VCO4**: fVCO 4,65–5,20 GHz, Kvco tipico da 50 a 73 MHz/V, **268 canali** da 4,65024 GHz in su.
- [TI §7.3.3 tabella 2, p.16](https://www.ti.com/lit/ds/symlink/lmx2572.pdf): **CPG=4 o 8 corrisponde a corrente CP 2,5 mA**; valore ipotizzato nel modello, **mai letto/scritto in un registro del chip di progetto**.

L'interpolazione viene ricalcolata **canale per canale**, non usa più un Kvco fisso universale come «dato tipico». Dai 270 calcoli *solo lineari*:

| Misura con dati tipici TI e valori R/C provvisori | Minimo | Massimo |
|---|---:|---:|
| Attraversamento unitario, crossover | **3.814 Hz** | **4.678 Hz** |
| Margine di fase matematico | **58,63°** | **62,87°** |
| N / canale agli estremi | **3633 / A3** | **3632 / A2** |

I casi estremi cadono vicino alla transizione VCO3→VCO4, dove i **Kvco tipici dei due core sono differenti**. Questi valori non devono essere letti come «guadagno VCO garantito» o «PLL ha margine di fase certificato». Il tool produce il file completo `v720.TI_typical_270_channel_linear_model.csv` e l'artefatto JSON con le ipotesi.

Uno sweep aggiuntivo di **2430 casi assunti** usa 270N ×3 Kvco (39/55/85 MHz/V) ×3 Icp (2,3/2,5/2,7 mA), **non** come limiti TI. L'analisi storica V0.6 Monte Carlo (4000 campioni) includeva **2 risultati sotto 45°** con campionamenti arbitrari di tolleranze e Kvco: la robustezza vera deve ancora essere verificata. **Non è stato eseguito PLLatinum Sim** ([strumento TI](https://www.ti.com/tool/PLLATINUMSIM-SW)), e non sono note impostazioni CP reali, VCO calibration, nonlinearità, parametri PVT, rumore/ref spur o ripple.

## 4. I sei errori ERC delle alimentazioni: ledger completo

CI `kicad-cli sch erc` sul master V7.19: **36 errori e 340 warning**. `kicad-cli sch export netlist` completo: **100 reti**. Il verificatore `03_Verifiche/V7.20/audit_native_power_v720.py` deve trovare esattamente gli stessi sei pin ERC e la loro rete nativa (nessuno con un pin `power_out` sulla *medesima net*), senza sopprimere nessuna segnalazione.

| Pin ERC | Net KiCad nativa nel rispettivo foglio | Qualifica mancante |
|---|---|---|
| **U200:1 IN** eFuse | `EFUSE_VIN` | sorgente esterna 13,8V, fusibile/TVS, protezione e transitori ancora da approvare |
| **U200:8 RTN** eFuse | `EFUSE_RTN` | percorso ritorno a protezione anti-inversione, **NON** da unire arbitrariamente a GND_MAIN |
| **U2:1 IN** LDO PLL | `5V_RF_PREREGULATED` | generazione reale da buck e filtro, corrente/power-path, EMI e tolleranze |
| **U2:2 GND** LDO PLL | `GND_MAIN` | source/return e partition RF/CP/VCO non qualificati |
| **U6203:1 IN** LDO MCU | `5V_DIGITAL_FILTERED` | provenienza e protezione dell'alimentazione MCU/codec non integrate |
| **U6203:2 GND** LDO MCU | `GND` | massa MCU distinta dal GND_MAIN AUX, piano e accoppiamento non validati |

KiCad `power_pin_not_driven` segnala assenza di **power-output sulla rete classificata**; può esistere una sorgente a monte di componenti passivi o un connettore esterno non ancora qualificato. Non bisogna confondere il flag ERC con «la tensione fisica sicuramente manca». In V7.20 nessun nodo viene auto-connesso, nessun tipo pin cambiato, nessun `PWR_FLAG` artificiale o waiver inserito: **tutti e 6 restano HOLD**.

## 5. Stato e prossime ECO autorizzabili

- **Root KiCad:** 36 errori (**26 label_dangling +6 power_pin_not_driven +4 pin_not_driven**) e **340 warning**. Nessuna riduzione nominale: è intenzionale perché un modello e uno studio non riparano cablaggi reali.
- **Interfacce RX/MCU/AUX:** 15 OPEN/HOLD con `tx_permission=0`; TX e SG48 ancora bloccati, RX_IF_STAGE da progettare. Nessuna modifica di schemi V7.19/V7.18 o PCB RX sperimentale.
- **RF:** C3 nominale 2,2 nF supera il minimo numerico 1,5nF suggerito dal datasheet, **posizione PCB e impedenza ground non qualificate**. R/C/CPG e rumore/phase margin da validare in PLLatinum Sim e bench.
- **PCB completa:** ancora stima **~10%**, invariata perché nessuna `.kicad_pcb` della radio completa creata o sbrogliata. Gli SMA J9102/J9104 lato destro a 180° sono ancora da convalidare meccanicamente.
- **Prossimo V7.21:** qualiﬁca elettrica della catena 13,8V→eFuse→buck→LDO e del domain GND, interfacce di potenza MCU, parametri PLL/CPG reali e post-validazione del modello TI; solo poi routing e fab.

**NO FAB / NO GERBER / NO PCBWAY / NO TX.**
