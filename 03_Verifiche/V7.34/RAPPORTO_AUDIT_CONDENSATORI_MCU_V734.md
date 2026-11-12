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
