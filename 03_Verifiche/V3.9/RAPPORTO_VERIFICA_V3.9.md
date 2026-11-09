# Rapporto V3.9 — audit e avanzamento

**Esito: NON PRONTO PER LA FABBRICAZIONE.** Progressione stimata 37% invariata. PCB V3.8 immutato.

## Evidenza nuova
- La fonte TE ufficiale contiene il disegno cliente comune alle varianti `CONSMA002-SMD` e `CONSMA002-SMD-G` (rev D): si chiarisce il significato del suffisso oro; non si considera per questo automaticamente corretta la libreria KiCad.
- Nel confronto nominale con il foglio 2, il land centrale V3.8 corrisponde al diametro Ø2,05 mm; l'estensione Y delle pad GND custom è 7,40 mm, mentre il disegno TE mostra 7,76 mm per il footprint raccomandato. Il disegno include anche una quota circolare Ø4,56 mm, non ancora ricondotta a una geometria CAD approvata.
- Un mancato allineamento nominale NON significa automaticamente corto o guasto: significa assenza di equivalenza verificata e blocco all'approvazione.
- L'audit riproducibile registra dimensioni e la SHA-256 del PCB, preservando lo schema di lavoro e la produzione in stato NO FAB.

## Test eseguiti
- Verifica CRC del pacchetto V3.8: riuscita.
- Validazione SHA-256 di 605 elementi sul manifest della V3.8 prima degli aggiornamenti: zero discrepanze.
- Regressione Python V3.8: 44/44; V3.7: 17/17. Questi risultati sono **interni, statici** e non sostituiscono KiCad ERC/DRC.
- Ambiente corrente: `kicad-cli` assente; refill nativo, ERC/DRC, controllo STEP e misure RF **non eseguiti**.

## Fonti
- https://www.te.com/en/product-CONSMA002-SMD-G.html
- https://www.analog.com/en/products/adl5535.html
- https://docs.kicad.org/9.0/en/cli/cli.html
- https://docs.kicad.org/10.0/en/cli/cli.html
