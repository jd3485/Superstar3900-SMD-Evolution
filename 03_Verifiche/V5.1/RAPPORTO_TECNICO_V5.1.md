# Superstar 3900 SMD Evolution — Rapporto tecnico V5.1

**8 novembre 2026 · Modulo RX 50 Ω · stato `NON PER FABBRICAZIONE`**

## Obiettivo e risultato concreto

La V5.1 aggiunge una distinta componenti e una mappatura pin-rete ricavate **dal PCB KiCad candidato V4.8**, uno script riproducibile con test di alterazione, una richiesta tecnica aggiornata per la fabbricazione/assemblaggio e una procedura esatta per ottenere i report **nativi** da una macchina KiCad 10. Non si modificano PCB, schema, rame, aperture F.Paste o librerie storiche.

I dati estratti sono **15 riferimenti**, **31 pin elettrici unici**, **8 reti non vuote**, di cui `GND_RF` e `+5V_BENCH`. Il modulo prevede quattro connettori SMA, un amplificatore ADL5535, cinque condensatori, un induttore 470 nH, tre resistenze e due piazzole di alimentazione. La distinta non contiene ancora codici d'ordine approvati per tutti i componenti, tolleranze, rating RF/termici e verifica di disponibilità. Tutti i componenti sono marcati da verificare.

| Verifica statico-analitica | Risultato | Limite |
|---|---:|---|
| Componenti / pin elettrici / reti | 15 / 31 / 8 | Lettura dal PCB candidato, non netlist ERC nativa |
| Attenuatore pi greco nominale | 150 Ω / 37,4 Ω / 150 Ω | Valori ideali senza parassiti e tolleranze |
| Attenuazione a 50 Ω | 6,012876 dB | Non misura RF né simulazione elettromagnetica |
| Return loss S11 ideale | circa 67,04 dB | Non prestazione della scheda reale |
| Test V5.1 | 13/13 passati | Test Python strutturali, non KiCad |
| KiCad `sch erc` / `pcb drc` | NON ESEGUITI | `kicad-cli` non disponibile; tentativo aggiornamento pacchetti non completato |
| Accettazione PCBWay | NON RICEVUTA | Non è stata inviata alcuna richiesta |

## Rischio termico U101 e processi possibili

Il candidato V4.8 ha **sei vie nel pad esposto U101**: diametro rame 0,55 mm, foro 0,25 mm, PCB a quattro strati spessore nominale 1,6 mm. La finestra di pasta F.Paste del pad ha dimensioni nominali 1,62 × 3,132 mm (81% dell'area rame), e **tutte e sei le aperture di foratura sono dentro tale finestra**. Questo comporta un rischio di assorbimento della pasta nel foro se le vie restano aperte. La proposta a due finestre del dossier V5.0 copre circa il 29,69% del pad: è solo un'alternativa di studio, **non è adottata**.

La documentazione PCBWay sulle vie riempite descrive due categorie: *electroplated filled vias* e *copper paste filled vias*. Per queste ultime sono pubblicati intervalli generici di foro da 0,1 a 1,0 mm e spessore da 0,2 a 4,0 mm. **Non sono garanzia di accettazione, planarità, rilavorazione o assemblabilità della nostra scheda**. Occorre una conferma scritta del processo selezionato, con specifiche di planarizzazione/cappatura e compatibilità stencil/reflow. Fonti: https://www.pcbway.com/pcb_prototype/PCB_Via_in_Pad.html e https://www.pcbway.fr/helpcenter/ordering_parameter_instruction/Via_Filled_with_Copper.html.

La geometria dei quattro connettori SMA non è ancora approvata con il modello ufficiale TE. Il produttore elenca DXF/STEP per `CONSMA002-SMD-G`, ma i modelli non sono acquisiti in questo pacchetto. Fonte: https://www.te.com/en/product-CONSMA002-SMD-G.html.

## Condizioni aperte per rilascio

Rimangono **9 gate di produzione OPEN** della V5.0: ERC, DRC/parità/refill, approvazione CAD TE, DFM del VIPPO, approvazione assemblatore/stencil, validazione termica, stack-up 50 Ω, BOM e collaudi, autorizzazione esplicita. La presente distinta fa avanzare solo **la preparazione** del gate BOM, non lo chiude. Nessun prototipo fisico è stato collaudato; fabbricazione e TX sono vietate.

## Come verificare altrove

Su computer con **KiCad 10** e Python 3.10+ estrarre l'intero ZIP, quindi eseguire il lanciatore della V5.0 come indicato in `03_Verifiche/V5.1/ISTRUZIONI_VALIDAZIONE_ESTERNA_V5.1.md`. Condividere i report ERC/DRC originali insieme allo `STATUS_V5.0.json`, senza modificare i file sorgenti. Non produrre Gerber da questi candidati. Un DRC senza errori da solo non è approvazione alla fabbricazione.
