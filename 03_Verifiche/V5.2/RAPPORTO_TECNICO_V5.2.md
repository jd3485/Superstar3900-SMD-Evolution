# Superstar 3900 SMD Evolution — rapporto tecnico V5.2

**8 novembre 2026 · RICEVITORE RF TEST A 50 Ω · NON PER FABBRICAZIONE**

## Nuovo risultato

Dal sorgente V4.8 è stato identificato un problema di collegamento: ciascuno dei 15 simboli del file schema conserva `instances (project "S3900E_RX_TEST_50R_V4_5_LIBS_CANDIDATE_NOT_FOR_FAB")`, mentre il PCB non riporta il campo `(path ...)` che associa il footprint alla UUID del simbolo. Queste carenze possono limitare il controllo di parità nativo KiCad, anche se i nomi dei componenti e delle reti coincidono nei controlli statici.

La V5.2 crea una **copia candidata distinta** della V4.8, aggiungendo 15 percorsi footprint→simbolo e riallineando 15 riferimenti di istanza al nome del progetto candidato. Nessun altro contenuto del PCB è stato modificato: rimuovendo esclusivamente i 15 nuovi campi `(path ...)`, il PCB risultante è byte-identico al V4.8. Analogamente, ripristinando esclusivamente i 15 nomi di progetto, lo schema è byte-identico all'originale.

**Attenzione:** l'associazione costruita è un'ipotesi KiCad conforme alla struttura corrente dei file, ma la parità e la corretta interpretazione dei percorsi **non sono ancora state confermate con KiCad**. Qualunque errore dovrà essere corretto su una nuova copia, mai alterando i file storici.

## Test e limitazioni

- 12 test automatici V5.2, inclusi casi di mutazione dei percorsi e dei valori.
- Eseguibile KiCad 10 assente: **ERC, DRC, refill e parità non eseguiti**. Tentativo aggiornamento pacchetti scaduto senza installazione (non considerato un test KiCad).
- Script portabile in `03_Verifiche/V5.2/run_kicad_v52.py`; su macchina KiCad 10 lavora su una cartella temporanea, genera ERC e DRC con `--schematic-parity --refill-zones`, non Gerber; non approva la fabbricazione.
- Il richiamo `test_v52.py` controlla solo struttura e identità del testo, **non** validazione sintattica o regole CAD native.

## Bloccanti invariati

I nove gate del `03_Verifiche/V5.0/GATE_RELEASE_V5.0.json` restano **OPEN**: ERC, DRC/parità, CAD TE, DFM VIPPO, approvazione stencil, termica ADL5535, stack-up 50 Ω, BOM/collaudo e autorizzazione esplicita. Il connettore TE CONSMA002-SMD-G elenca STEP/DXF sul sito ufficiale, ma non è stato importato o confrontato integralmente. Nessuna risposta di PCBWay è stata ricevuta. Manuale d'uso V4.0 conservato.

**Stato:** 37% storico stimato, zero moduli hardware validati, **NO FAB / NO TX**.

Fonti di riferimento:
- https://docs.kicad.org/10.0/en/cli/cli.html
- https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/
- https://www.te.com/en/product-CONSMA002-SMD-G.html
- https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf
