# Superstar 3900 SMD Evolution — V7.19 / contratto TI per il filtro di anello LMX2572

**11 novembre 2026 — diagnosi della connettività nativa, NON approvazione dei valori RF, NO FAB / NO TX.**

## 1. Riferimenti primari controllati

- [Texas Instruments LMX2572 datasheet SNAS740B](https://www.ti.com/lit/ds/symlink/lmx2572.pdf), sezione **8.1.11**, pagina stampata 75, **Figura 179 — External Loop Filter**: circuito di riferimento a tre poli, pin CPout e Vtune, R3 in serie tra CPOUT e VTUNE, C1 verso GND dal lato CPOUT, ramo **R2–C2 in serie verso massa** dal lato CPOUT, C3 verso GND su VTUNE.
- Stesso datasheet: **Vtune pin 35** richiede almeno **1,5 nF** di capacità shunt verso VCO ground; la vicinanza fisica del condensatore a Vtune è importante per il phase noise. **CPout pin 12**.
- [TI LMX2572EVM SNAU217B](https://www.ti.com/lit/ug/snau217b/snau217b.pdf), **Fig. 19 pagina 13** e Table 1 p.5: EVM effettiva ha una scelta diversa dei valori (`C2_LF=15nF`, `C4_LF=2.2nF`, `R2_LF=330Ω`, `R3_LF/R4_LF=0Ω`, `C1_LF/C3_LF=DNP`) per quel progetto EVM; **non** va scambiata con una validazione dei valori del Superstar.
- Il candidato Superstar V7.18 ha R2 **620Ω**, R3 **22Ω**, C1 **220 pF**, C2 **120 nF**, C3 **2,2 nF**. Il valore proposto C3 soddisfa solo il minimo **numerico** 1,5 nF e **NON** dimostra banda, margine di fase, spur, rumore o piazzamento.

Il contratto macchina `CONTRATTO_TOPOLOGIA_LOOP_PLL_TI_V7_19.json` stabilisce **i nodi che devono risultare nel netlist finale**:

| Nodo | Terminali richiesti (simbologia V7.18) |
|---|---|
| **`PLL_CPOUT`** | U1:12, C1:2, R2:1, R3:1 |
| **`PLL_R2_C2`** | R2:2, C2:2 |
| **`PLL_VTUNE`** | U1:35, R3:2, C3:2 |
| **`GND_MAIN`** | C1:1, C2:1, C3:1, soggetto a conferma del ground di riferimento PLL |

Il solo nome uguale di una `label` **non qualifica** il ritorno GND_RF, le correnti o la posa RF: serve **appartenenza nativa di ciascun pin alla rete corretta**, assenza di rail cortocircuitate e simulazioni.

## 2. Causa del blocco KiCad

La baseline native V7.18 ([run 42964734310](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42964734310)) ha **42 errori ERC / 340 warning**. Sebbene il testo dello schema contenga il filtro, **KiCad non esporta alcuna appartenenza di R2/R3 alle reti**; gli ERC includono `pin_not_connected` x2 e `wire_dangling` x3, mentre U1:35 `PLL_VTUNE` è una net con un solo ingresso. Il circuito attuale non è un PLL elettricamente integrato.

`03_Verifiche/V7.19/probe_loop_endpoint_v719.py` esegue **quattro prove KiCad9** su veri progetti completi **clonati ed eliminati**, preservando tutti gli schemi versionati:
- V7.18 originale **42/340** (errori/warning);
- filo verso pin esterno R2 **40/340**, elimina due `pin_not_connected`, ma **non collega ancora R2/R3 nella netlist** e restano tre wire_dangling;
- aggiunta di stub al pin R3 **40/342**, non corretta;
- riancoraggio R2/R3 su griglia **40/336**, ma **ANCORA senza appartenenza R2/R3 nella netlist**.

Pertanto **non si promuove nessuno dei tre candidati V7.19 a schematica di produzione**. Una seconda prova a labels dirette `probe_loop_label_attach_v719.py` viene verificata separatamente, sempre con confronto di tutti i pin. Il suo risultato diagnostico è conservato nella CI, senza promozione automatica.

## 3. Criterio di accettazione tecnico

Un futuro ECO di schema PLL può avanzare soltanto con **tutti** questi risultati verificabili:
1. KiCad 9 nativo esporta U1:12, R2:1, R3:1, C1:2 su `PLL_CPOUT`.
2. KiCad 9 esporta R2:2 insieme a C2:2 su `PLL_R2_C2`, senza corti verso `GND_MAIN`.
3. KiCad 9 esporta U1:35, R3:2, C3:2 su `PLL_VTUNE` e il circuito chiude il loop reale senza pin inutilizzati.
4. I ritorni GND di C1/C2/C3 e il VCO ground vengono controllati elettricamente e in layout; la risoluzione non introduce archi TX, nodi 5 V ↔ 3V3 o interfacce OPEN/HOLD.
5. I valori e stabilità del loop sono verificati con **PLLatinum Sim o equivalente**, su frequenze/fPD/Kvco/corrente CP del vero piano della radio. Non fabbricare finché RF, BOM, stack-up, EMI, PCB globale e protezioni sono HOLD.

**Il conteggio ERC da solo non è un criterio di completamento.** Root PCB completa stimata **~10%, invariata**. SG48, TX, SMA meccanica e 15 interfacce cross-module rimangono HOLD.
