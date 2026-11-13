# V7.71 — Thermal budget SEI TPS7A2033 SOT-23 + Bourns L100 saturated-current screen

**Date:** 14 novembre 2026. Baseline `main` V7.70: 140 components/103 nets, KiCad9 ERC **28 errors/192 warnings**, 406 PASS. Questa versione **NON** approva carico, PCB, temperatura o produzione.

## 1. Fonte dati primaria del progetto e vendor

Leggi i SEI riferimenti *realmente presenti* nel progetto, non sei carichi inventati:
- `U6203` → `3V3_AUDIO_CLK`, `U6204` → `3V3_MCU`, `U6205` → `3V3_CODEC_IO`, `U6206` → `3V3_CODEC_LDOIN`, tutti sul percorso `5V_DIGITAL_FILTERED` a valle bead `FB6201`; ingresso di 5V dal buck **non** è per questo automaticamente qualificato tra tutti i moduli;
- `U2` → `3V3_PLL_INPUT_FROM_LDO`, `U3` → `3V3_REF_LDO`, in AUX/PLL sul `5V_RF_PREREGULATED`;
- ciascun `TPS7A2033PDBVR` SOT-23-5 è **rated maximum output 0.300 A**, che NON significa che ogni rail assorbe 0.300 A.
- V7.43 matrice `03_Verifiche/V7.43/MATRICE_CARICHI_TERMICA_5V_V743.json` ha ancora tutte le **6 vere correnti massime/transienti null**; non introdurre dati fittizi.

Fonte ufficiale [TI TPS7A20 Rev H SBVS338H](https://www.ti.com/lit/ds/symlink/tps7a20.pdf), §5.4: `RθJA(DBV) = 187.1 °C/W` **caratterizzato su scheda JEDEC, NON temperatura della futura PCB**; §5.5: `IGND tip a 300mA = 2mA` (**tipico, NON massimo**) e Tj intervallo operativo **-40–125°C**. Le resistenze termiche cambiano con rame, piste, via, strati, aerazione, radiatori e temperatura interna al case.

## 2. Screen 5V→3.3V non autorizza 300mA sempre

Formula di semplice screening DC termico (non misure e non simulazione di transitori):

`P_D=(VIN - 3.3V)×Iout + VIN×IGND`;

`Tj_screen = Ta + 187.1°C/W×P_D`.

Per i punti principali, assumendo **IGND fisso 2mA tipico (non limite garantito né reale funzione Iout)**:

| VIN ipotetica | Ta ipotetica | Ogni LDO con 300mA: Tj stimata | Corrente teorica massima per Tj125°C |
|---|---|---|---|
| 5.000 V | 25°C | 122.3°C | 308.5mA (ridurre comunque al rating 300mA) |
| 5.000 V | 85°C | 182.3°C | 119.9mA |
| 5.300 V | 25°C | 139.2°C | 261.9mA |
| 5.300 V | 60°C | 174.2°C | 168.4mA |
| 5.300 V | 85°C | **199.2°C** | **101.6mA** |

VIN=5.300V è estremo alto *idealizzato* calcolato da V7.68 con TI TPS54202 VFB e partitore 1%, **NON un valore garantito del buck**. Ta 85°C è uno scenario di progetto, non la reale temperatura interna rilevata. La Tj 199°C è una **predizione oltre il range raccomandato**, non una temperatura a cui il regolatore lavorerà stabilmente: la protezione termica può intervenire. L'uscita 3.3V assunta nominale: la sua tolleranza, il comportamento reale di IGND, la θJA effettiva, le cadute bead/PCB e le interazioni termiche dei 6 LDO potrebbero peggiorare o migliorare il risultato. Condividere 5V/3V3 da solo non quantifica le correnti.

La somma dei **rating** `6×0.3A=1.8A` lascia **solo 0.2A nominali** rispetto ai 2A rated TPS54202 **se** tutti lavorassero simultaneamente al limite, senza altri carichi diretti: confronto progettuale, NON una misura o una prova di corrente consumata. Quattro LDO MCU dietro FB6201 sommano rating 1.2A contro bead rating 2A (ma non è un contratto elettrico firmato). Poiché esistono carichi diretti e transitori ancora ignoti, **NON dichiarare riserva garantita**.

Suite **360 scenari** = sei regolatori × quattro VIN (4.865054 / 5 / 5.079439 / 5.300131 V) × Ta 25/60/85°C × correnti 50/100/150/200/300mA. Nessun punto di questa tabella è uno stato misurato o una previsione reale vincolante.

## 3. Bourns L100 SRP1038A-150M, margine scenario ideale

Fonte primaria [Bourns SRP1038A datasheet tabella elettrica a 25°C](https://www.bourns.com/docs/product-datasheets/srp1038a.pdf):
- modello esatto **SRP1038A-150M**, **15µH ±20%**, `DCR_typ=40mΩ`, `DCR_max=45mΩ`, `Irms=6.25A` (test 40°C rise), `Isat=10A` (corrente con riduzione induttanza del **20%**), AEC-Q200;
- Isat10A **NON** è una soglia dura di non-saturazione fino a 10 A e non garantisce comportamento del materiale a ogni temperatura; Isat è un metodo di definizione vendor a 25°C.

Analisi ideale per buck CCM con **VIN=10.2545/13.8/17.0524V**, **Iout=.5/1/1.5/2A**, **Vout=5V**, **fSW minimo nominale 390kHz** e **Lmin=12µH**:
`ΔIL_pp≈Vout(1−Vout/VIN)/(L×fSW)`,
`Ipeak≈Iout+ΔIL_pp/2`,
`Irms≈√(Iout² + ΔIL_pp²/12)`.
Caso più severo entro questi 12 punti a 17.0524V e 2A: **ΔIL≈0.755 A p-p**, **picco≈2.378 A**, **Irms≈2.012 A**, **perdita DCR con massimo45mΩ≈0.182 W**. Valori di scenario sotto Irms6.25A e Isat10A del datasheet, dunque **non emerge un allarme di saturazione nominale nel regime CCM ideale di 2 A**, ma questo *non* convalida start-up, OCP/hiccup e corto circuito, tolleranze SW, temperature, forma d'onda reale, effetto ripple e loop, rampe e DCR riscaldata. Non adottare regole di derating induttore arbitrarie.

## 4. Nuova annotazione tecnica direttamente negli schemi KiCad (non solo report)

Nuovo AUX `04_KiCad/Gerarchico_Alimentazioni_V7.71_LDO_THERMAL_L100_LIMITS_REVIEW_NOT_FOR_FAB/`:
- `02_BUCK_5V.kicad_sch` contiene DUE nuove annotazioni native sulla tabella vendor L100 e sul fatto che **1.8A è somma di rating LDO, non carico misurato**.
- `03_PLL_LDO_TCXO.kicad_sch` contiene DUE annotazioni native sulla temperatura teorica **199°C** nel caso 5.3V/85°C/300mA e su U2/U3 + U6203–U6206 **HOLD**.
- Quattro soli nodi `(text ...)` aggiunti, UUID univoci, nessuna proprietà, pin, valore o wire modificato. Nuovo root `04_KiCad/Assemblaggio_RX_Power_V7.71_LDO_THERMAL_L100_LIMITS_REVIEW_NOT_FOR_FAB/` cambia solo AUX Sheetfile. Gli altri componenti/footprint/librerie sono byte-identici.
- `03_Verifiche/V7.71/test_six_tps7a2033_l100_thermal_envelope_native_v771.py` verifica differenze letterali native, netlist+ERC KiCad9 sette fogli V7.70 vs V7.71, **140 componenti/103 reti e mappa completa pin→net identici**, *tutti* i findings ERC byte-equivalenti: **28 errors +192 warnings** sia prima che dopo. Ogni alterazione elettrica/ERC blocca merge.
- Soglie e limiti progettuali valutati con test Python trasparenti, con file JSON scenario compilato CI. Questi nuovi test **NON** equivalgono a misure PCB, loop simulation o DRC.

## 5. HOLD e prossimo intervento

**È indispensabile ottenere almeno:** corrente continua + transitoria di **ciascuno** dei sei LDO e di tutti gli altri consumatori diretti a 5V; limite Ta nel case e scelta di margine Tj; modello termico reale θJA PCB + distribuzione del rame; temperatura effettiva con sei LDO attivi, reale 5V con VFB/ripple/line/load; curve I_L e recovery TPS54202. Prima di 300mA LDO con Ta85°C bisogna cambiare architettura termica o ridurre corrente, non occultare il rischio.

Altri blocchi invariati: C103/C104 DC bias/temp/aging (vedi V7.69), F200 fusibile vs TPS26600 e SW200 reset (Issue #57), D200 TVS DNP, 15 interfacce crossmodule OPEN/HOLD, SG48 e Y1 pin10 HOLD. Nessuna PCB unica né DRC globale, **NO FAB / NO GERBER / NO PCBWAY / NO TX**.
