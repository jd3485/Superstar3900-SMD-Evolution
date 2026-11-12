# V7.34 — Audit tecnico dei 30 condensatori MCU/CODEC (HOLD, non autorizzato per fabbricazione)

Data: 12 novembre 2026. Baseline: V7.33 integrata su `main`, 132 componenti, 100 reti, ERC 36 errori / 218 warning, 33 footprint non assegnati. Questa è una fase di *qualifica preliminare*, **non** una ECO CAD completata.

## Inventario estratto dal file KiCad V7.33

Sorgente: `04_KiCad/Modulo_MCU_CODEC_V7.33_YAGEO_8R_0402_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch`. I 30 simboli da C6201 a C6230 hanno tutti la proprietà Footprint vuota.

| Valore nello schema | Quantità | Riferimenti |
| --- | ---: | --- |
| 100nF | 12 | C6201, C6203, C6205, C6207, C6209, C6210, C6211, C6212, C6214, C6217, C6220, C6227 |
| 10uF | 5 | C6202, C6204, C6206, C6208, C6219 |
| 1uF | 11 | C6213, C6215, C6216, C6218, C6221, C6222, C6223, C6224, C6225, C6226, C6229 |
| 4.7nF | 1 | C6228 |
| 10nF | 1 | C6230 |
| **Totale** | **30** | |

## Evidenze vendor (candidati, NON design-in approvato)

- Murata GRM155R71C104KA88D: 100nF, X7R, 16 V, ±10%, package 0402 (1005 metrico). Fonte distributore: https://www.mouser.it/it/ProductDetail/Murata-Electronics/GRM155R71C104KA88D ; famiglia Murata 100nF 0402: https://pim.murata.com/asset/pim4/ceramicCapacitorSMD/GRM155R71C104JA88-01A-EN_PDF_CERAMICCAPACITORSMD?lastModifiedDatetime=20250813144737 . Il PDF della variante **JA88** non è prova delle caratteristiche esatte **KA88D** oltre ai campi effettivamente coincidenti.
- Murata GRM21BR71A106KE51: 10uF, X7R, 10 V, ±10%, package 0805 (2012 metrico), *candidato per analisi* e non assegnato. Elenco ufficiale Murata: https://www.murata.com/-/media/webrenewal/tool/library/common-pdf/dynamic-model/component-list-d-mlcc-2504.ashx?cvid=20250523010405000000&la=en .
- Nessun MPN approvato per gli undici 1uF, il 4.7nF e il 10nF; nessuna decisione sul package per nessuno dei 30.

## Blocchi tecnici che impediscono l'assegnazione dei footprint

1. Non sono ancora documentate pin-per-pin le rail effettive, compresi i nodi di alimentazione/uscita analogica per ogni C62xx; il valore nello schema non prova la tensione applicata.
2. Per i MLCC classe II la capacità **effettiva** varia con DC bias, temperatura, invecchiamento e tolleranza. Per i 10uF serve curva specifica per MPN e tensione, non basta '10uF/10V'.
3. Verificare prescrizioni di bypass, ESR/ESL, impedenza e ordine di grandezza del ripple per i datasheet di MCU, codec e alimentazioni. Reti analogiche o di filtro richiedono valutazione del dielettrico e della precisione prima di usare X7R.
4. Verificare geometria di land *del produttore per MPN esatto*, pad 1/2, clearance, saldatura e stencil; non riciclare il footprint delle resistenze 0402.
5. Prima di cambiare il CAD: prova KiCad9 netlist/ERC prima-dopo, 132 componenti, 100 reti identiche, zero pin-net delta; verificare che ogni footprint sia associato esclusivamente a un condensatore approvato.
6. Attendere vera qualifica elettrica e meccanica, non ridurre artificialmente gli errori/ERC o il numero di footprint HOLD.

## Stato e ripartenza

La V7.34 è **audit in corso**, non integrata né CAD-validata; nessuna modifica alla V7.33 da questo documento. Target successivo: mappa C62xx→nodi elettrici→tensione in tutti gli stati (nominale, start-up, fault) e verifica delle curve DC-bias di vendor; soltanto allora ECO KiCad con test nativi e PR idonea. I 33 footprint mancanti, 36 errori ERC e 218 warning restano invariati. HOLD: 15 interfacce cross-domain, SG48, Y1 pin10 AFC/GND, thermal/power/PLL. **NO FAB / NO GERBER / NO PCBWAY / NO TX.**

## V7.34 — Mappatura diretta delle etichette sui pin, dal sorgente nativo (12 novembre 2026)

Il simbolo `S3900E:C_DRAFT` ha pin 1 a coordinate relative (0,+5.08) KiCad e pin 2 (0,-5.08); nelle coordinate disegno i rispettivi contatti corrispondono a `y-5.08` e `y+5.08`. Tutte le 30 istanze sono orientate a zero gradi. Il seguente inventario è determinato dalle **etichette di rete posizionate esattamente sui terminali**, non da ipotesi di vicinanza ai nomi dei componenti. Non prova da solo continuità globale, tensioni o corretta connessione elettrica, per cui la netlist KiCad resta il riferimento di qualifica finale.

| C | Pin 1: etichetta di rete | Pin 2: etichetta di rete |
| --- | --- | --- |
| C6201 | `3V3_CODEC_IO` | `GND` |
| C6202 | `CODEC_REF` | `GND` |
| C6203 | `CODEC_AVDD_LDO_OUT` | `GND` |
| C6204 | `CODEC_AVDD_LDO_OUT` | `GND` |
| C6205 | `CODEC_DVDD_LDO_OUT` | `GND` |
| C6206 | `CODEC_DVDD_LDO_OUT` | `GND` |
| C6207 | `3V3_CODEC_LDOIN` | `GND` |
| C6208 | `3V3_CODEC_LDOIN` | `GND` |
| C6209 | `3V3_MCU` | `GND` |
| C6210 | `3V3_MCU` | `GND` |
| C6211 | `3V3_MCU` | `GND` |
| C6212 | `3V3_MCU` | `GND` |
| C6213 | `3V3_MCU` | `GND` |
| C6214 | `3V3_ANA_MCU` | `GND` |
| C6215 | `5V_DIGITAL_FILTERED` | `GND` |
| C6216 | `3V3_AUDIO_CLK` | `GND` |
| C6217 | `3V3_AUDIO_CLK` | `GND` |
| C6218 | `3V3_AUDIO_CLK` | `GND` |
| C6219 | `5V_DIGITAL_FILTERED` | `GND` |
| C6220 | `5V_DIGITAL_FILTERED` | `GND` |
| C6221 | `5V_DIGITAL_FILTERED` | `GND` |
| C6222 | `3V3_MCU` | `GND` |
| C6223 | `5V_DIGITAL_FILTERED` | `GND` |
| C6224 | `3V3_CODEC_IO` | `GND` |
| C6225 | `5V_DIGITAL_FILTERED` | `GND` |
| C6226 | `3V3_CODEC_LDOIN` | `GND` |
| C6227 | `MIC_PREAMP_OUT` | `MIC_AC_COUPLED` |
| C6228 | `MIC_CODEC_IN` | `GND` |
| C6229 | `FM_DISCRIM_RAW` | `FM_AC_COUPLED` |
| C6230 | `FM_CODEC_IN` | `GND` |

**Risultati tecnici rilevanti:** `C6227` e `C6229` sono condensatori *in serie* ai segnali MIC e FM; non vanno qualificati come semplici MLCC di alimentazione. `C6228` e `C6230` sono tra ingressi del codec e GND, probabili elementi di rete analogica, ma funzione e frequenza di taglio richiedono l'analisi del circuito completo. `C6202` 10uF è su `CODEC_REF`, non su un rail nominale 3.3 V; `C6204` e `C6206` 10uF sono sulle uscite LDO interne `CODEC_AVDD_LDO_OUT` e `CODEC_DVDD_LDO_OUT`: prima di approvare MPN, verificare specifiche TI su stabilità, capacità effettiva, ESR e startup. Le etichette `5V_DIGITAL_FILTERED` / `3V3_*` non certificano da sole livelli effettivi, sovratensioni transitorie o tensione massima.

### Gate immediato

Il nuovo `test_capacitor_inventory_v734.py` vincola l'inventario e i 60 accoppiamenti pin/etichette estratti dal sorgente KiCad. Qualunque cambiamento inatteso va bloccato e riesaminato. **Non modifica lo schema, non esegue netlist/ERC nativi, non è signoff fabbricativo.** Il prossimo passaggio elettrico è confrontare questi 60 nodi con netlist esportata in KiCad9 e le specifiche dei regolatori codec, poi scegliere MPN esatti con curve DC-bias e land del produttore.
