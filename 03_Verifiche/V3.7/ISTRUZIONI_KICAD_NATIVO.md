# Verifica KiCad nativa — V3.7 (DA ESEGUIRE)

1. Aprire la PCB in KiCad 9 o successivo, da questa directory, con `fp-lib-table` e `S3900E_Review.pretty` presenti.
2. Verificare che J101/J103 presentino l'uscita coassiale verso SINISTRA e J102/J104 verso DESTRA; il verso è assunto rispetto alla freccia locale del footprint NON validato.
3. Confrontare le piazzole con il land pattern consigliato TE/Linx rev D foglio 2; ricostruire la geometria delle aree GND (oggi quattro quadrati non fedeli) e l'ingombro metallico reale. Confermare l'assenza di fori centrali NON prescritti.
4. Confrontare U101 con ADL5535 rev A Fig. 17 e definire GND paddle/paste/termiche.
5. Controllare stack-up, larghezza delle piste da 50 ohm e solder mask usando stack-up confermato dal fabbricante.
6. Riempire TUTTE le zone di rame in KiCad (B). Poi usare PCB Editor → Inspect → Design Rules Checker; correggere errori e warning.
7. Eseguire (da terminale con KiCad installato):

   `kicad-cli pcb drc -o DRC_V3.7.txt S3900E_RX_TEST_50R_V3_7_SMA_FOOTPRINT_REVIEW_NOT_FOR_FAB.kicad_pcb`

8. Collegare schematico e PCB ed eseguire ERC e controllo di concordanza; nessuna produzione senza elenco errori chiuso.
9. Mai collegare alla linea TX: il coupon è RX-only e non contiene un commutatore TX/RX.

NON sono stati realizzati Gerber o drill per questa revisione. Nessun pass DRC è dichiarato.
