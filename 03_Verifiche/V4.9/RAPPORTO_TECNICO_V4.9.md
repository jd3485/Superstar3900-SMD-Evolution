# Superstar 3900 SMD Evolution — rapporto tecnico V4.9

**8 novembre 2026 · REVISIONE DOCUMENTALE E AUDIT STATICO · NON AUTORIZZATA ALLA FABBRICAZIONE.**

## Scopo e avanzamento

Questa revisione identifica e quantifica un rischio di assemblaggio precedentemente non modellato in modo automatico: la sovrapposizione tra le **sei vie in pad U101** (variante RX V4.8) e **l'apertura F.Paste corrente**, ereditata dal layout precedente. Non modifica PCB, footprint, schema, BOM o istruzioni CAM. Non ci sono collaudi fisici.

## Risultati riproducibili direttamente dai file KiCad

| Elemento | Lettura statica V4.9 |
|---|---|
| PCB candidato | `04_KiCad/Modulo_RX_Test_50ohm_V4.8_TERMICA_6VIE_STUDIO_NON_FAB/S3900E_RX_TEST_50R_V4_8_6VIE_STUDIO_NOT_FOR_FAB.kicad_pcb` |
| Strati rame / spessore nominale PCB | 4 / 1,60 mm |
| U101 exposed pad (F.Cu, F.Mask, F.Paste) | 1,80 × 3,48 mm |
| U101 centro piazzola (coordinate scheda) | 68,00 × 33,64 mm |
| Rapporto riduzione F.Paste | −0,10 per asse |
| Apertura teorica continua F.Paste | **1,620 × 3,132 mm**, superficie **5,07384 mm²** |
| Copertura geometrica nominale pasta sul pad | **81%** (non è volume di pasta depositato) |
| Vie termiche | Sei, tutte GND_RF net 1 |
| Diametro rame / foro nominale via | Ø0,55 / Ø0,25 mm |
| Rapporto spessore/foro | 1,60 / 0,25 = **6,4:1** |
| Anello nominale rame per via | (0,55−0,25)/2 = **0,150 mm** |
| Fori sotto F.Paste | **6/6**, con cerchio del foro interamente interno all'apertura geometrica teorica |
| Margine minimo fra bordo foro e F.Paste | circa **0,281 mm** |
| Controllo file V4.8 (SHA-256 atteso) | invariato |

La copertura dell'81% è derivata dal parametro KiCad `solder_paste_margin_ratio -0.100` per una piazzola rettangolare, **non** da una fotoplot CAM. L'intersezione è calcolata nel modello 2D; il riempimento effettivo dello stencil e la metallizzazione della via dipendono dai processi scelti. La frazione geometrica dei fori dentro la F.Paste è ~5,8%; non va interpretata come una percentuale di saldatura persa.

### Conseguenza tecnica

Senza processo adeguato, le vie esposte possono creare percorsi di migrazione della lega saldante, vuoti o difetti di assemblaggio. Non approvare lo stencil corrente semplicemente perché la percentuale di pasta è 81%. La mitigazione candidata è **via-in-pad riempita e cappata con superficie planare**, previo accordo tecnico con fabbricante e assemblatore. Non è approvata e non sono stati acquistati servizi. Il semplice *tented via* non equivale automaticamente a un processo VIPPO.

## Fattibilità preliminare del fabbricante

PCBWay documenta per il processo avanzato un foro nominale di Ø0,25 mm su schede fino a 2,0 mm; lo spessore 1,6 mm del candidato è all'interno di questa soglia **solo per il vincolo dimensionale generale**. PCBWay descrive separatamente i processi *via-in-pad*, riempimento/resina/cappatura e, in un'altra pagina, il riempimento con pasta di rame; gli ordini reali richiedono una specifica di processo approvata. Non sono confermati per la nostra scheda la finitura planare, gli spessori effettivi, i costi, il rendimento, le tolleranze, il tipo di riempimento, la compatibilità con l'assemblaggio o lo stack-up RF.

## Decisioni tecniche aperte

1. **Opzione A (studio preferenziale, non approvata):** conservare sei vie sotto U101, chiedere al fabbricante processo *filled-and-capped / VIPPO* e al montatore nuova approvazione F.Paste, stencil, reflow e ispezione X-ray/visiva.
2. **Opzione B (riserva):** ridisegnare il collegamento GND con vie esterne alla piazzola o altra disposizione, misurando nuovamente impedenza e termica; non automaticamente equivalente all'opzione A.
3. **Opzione C (esclusa dalla baseline):** mantenere la variante attuale con vie aperte e stencil invariato senza prova del processo. La geometria da sola non ne dimostra l'assemblabilità.

La scelta non può essere chiusa senza risposta documentata di fabbricante **e** montatore. Non generare un pacchetto CAM di produzione né ordinare la PCB.

## Altri gate bloccanti invariati

- KiCad non disponibile in questa sessione: **ERC/DRC nativi, parità schema-PCB e refill zone NON ESEGUITI**.
- Connettore TE `CONSMA002-SMD-G`: DXF/STEP non acquisiti; geometria completa non approvata.
- Stack-up quattro strati, riferimento piano GND, DK, spessori dielettrici e controllo 50 Ω **non approvati**.
- Analisi di temperatura di giunzione e misure S11/S21/VNA non effettuate.
- Distinta componenti, stencil completo, pick-and-place e processi di saldatura da validare.
- Nessun modulo hardware costruito o validato; la radio finale e il manuale d'uso restano un progetto.

## Deliverable V4.9

- `03_Verifiche/V4.9/audit_via_stencil_v49.py`: legge i sorgenti e calcola in modo riproducibile quote, aperture, intersezioni e stato dei gate.
- `03_Verifiche/V4.9/AUDIT_VIA_STENCIL_V4.9.json`: esito numerico con hash del file PCB.
- `03_Verifiche/V4.9/test_v49.py` e `TEST_V4.9.txt`: test statici e test negativi.
- `05_Produzione_PCBWay/RICHIESTA_FATTIBILITA_V4.9.md`: richiesta tecnica da inviare **solo con autorizzazione dell'utente**, non ordine.
- `05_Produzione_PCBWay/GATE_PRODUZIONE_V4.9.csv`: registro esplicito dei blocchi.
- `03_Verifiche/V4.9/PROCEDURA_KICAD_V4.9.md`: controlli da eseguire esternamente.

## Fonti esterne consultate

- ADI ADL5535, sito e datasheet Rev A: https://www.analog.com/en/products/adl5535.html
- PCBWay, capacità advanced: https://www.pcbway.com/capabilities.html
- PCBWay, via-in-pad: https://www.pcbway.com/pcb_prototype/PCB_Via_in_Pad.html
- PCBWay, riempimento rame: https://www.pcbway.com/helpcenter/ordering_parameter_instruction/Via_Filled_with_Copper.html
- TE connettore esatto: https://www.te.com/en/product-CONSMA002-SMD-G.html
- KiCad 10 CLI: https://docs.kicad.org/10.0/en/cli/cli.html

**Stato finale: NON FAB / NON PCBWAY / TX DISABILITATA.** 37% è stima storica di avanzamento progettuale, non prova di funzionalità.
