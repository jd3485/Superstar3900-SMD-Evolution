# Superstar 3900 SMD Evolution — rapporto tecnico V5.5

**8 novembre 2026 — Revisione software non per fabbricazione.**

## Obiettivo e risultato verificabile

Aggiungere uno screening geometrico top-copper al modulo RX candidato V5.2 e rafforzare il controllo dei report che verranno prodotti da KiCad reale. Non è stata eseguita alcuna nuova ERC/DRC nativa; `kicad-cli` non è installato in questo ambiente.

La nuova analisi geometrica usa `Shapely` per ricostruire **44 pad** (incluse sagome SMA custom), **44 segmenti** `F.Cu` e **70 vie**. **5.267** coppie di geometrie di reti differenti hanno fornito una distanza minima del rame di **0,45 mm**. Non emergono collisioni con soglia di screening 0,30 mm, ma **cinque coppie di pad** (C101, C102, R201, R202, R203) sono alla distanza minima. La soglia analitica non è una regola KiCad configurata/approvata.

La scheda definisce quattro zone GND, tutte con poligoni non ancora riempiti (0 zone compilate). Questo limita fortemente l'audit. DRC completo, refill, separazioni su altri layer, drill clearance, aperture mask, stack-up, transizioni RF e termica NON sono eseguiti. Il precedente pad termico U101 con sei vie è ancora candidato, processo VIPPO/stencil da concordare.

## Post-validazione JSON KiCad

Il runner V5.4 accettava staticamente qualunque oggetto JSON non vuoto purché il comando avesse exit-code 0. V5.5 aggiunge un secondo livello che richiede struttura coerente coi report KiCad 10, versione corretta, liste ERC per foglio e tutte e tre le liste di DRC (`violations`, `unconnected_items`, `schematic_parity`). Un report troncato, una violazione o un problema di parità blocca il controllo. Il post-validatore **non autentica** l'origine del file JSON: serve ancora eseguire il workflow o il runner su un host affidabile e controllare i log.

## Test eseguiti

- **22/22** test V5.5 (10 geometrici, 12 su metadati/violazioni di report fittizi) superati.
- Le regressioni V4.0–V5.5 sono riportate in `REGRESSIONI_V5.5.json` e `.txt`, e devono essere interpretate separatamente dalla verifica nativa.
- Esecuzione locale del `run_native_v55.py` senza KiCad: stato di blocco atteso, non un test nativo.
- Schema, PCB, librerie e manuale illustrato **non modificati**.

## Condizioni di rilascio

**NO FAB / NO PCBWay / NO TX.** Restano indispensabili KiCad 10 su macchina compatibile, CAD ufficiale del connettore TE, risposta scritta DFM sull'ADL5535/VIPPO e qualificazione dello stack-up e dei parametri RF. L'avanzamento storico **37%** rimane una stima documentale, non un progresso hardware misurato.
