# Procedura nativa obbligatoria prima di rilasciare il coupon V3.8

## Stato
Tutti i passaggi in questo documento sono **DA ESEGUIRE**, non compiuti; durante la revisione V3.8 `kicad-cli` non era disponibile.

1. Installare KiCad 9 o 10 su una macchina con librerie S3900E disponibili; conservare la copia sorgente V3.8 immutata.
2. Aprire `S3900E_RX_TEST_50R_V3_8_SHAPED_LAND_THERMAL_REVIEW_NOT_FOR_FAB.kicad_pcb` in PCB Editor. Segnalare ogni errore di parsing/compatibilità ed esportare screenshot.
3. Aprire i footprint personalizzati e confrontare le piazzole TE con le dimensioni **ufficiali** della versione acquistata (CONSMA002-SMD-G non automaticamente uguale a CONSMA002-SMD). Approvare anche courtyard e ingombro SMA a montaggio avvenuto.
4. Verificare ADL5535, pad termico 1,8 × 3,48 mm, stencil F.Paste, tenting dei via e isolamento dei pin RF. Il valore -0,10 della pasta è solo sperimentale.
5. Approvare lo stack-up: L1 microstrip RF, L2 ground; spessori reali e solder mask dichiarati dal produttore.
6. Riempire i quattro piani GND con KiCad e verificare assenza di isole isolate; non presupporre che la loro sola definizione garantisca continuità.
7. Eseguire DRC su una copia **dopo refill**, documentando numero, tipo e gravità delle violazioni; nessuna violazione bloccante accettabile.
8. Comando di avvio possibile (KiCad 9):

   `kicad-cli pcb drc --severity-all --exit-code-violations -o drc_v38.txt S3900E_RX_TEST_50R_V3_8_SHAPED_LAND_THERMAL_REVIEW_NOT_FOR_FAB.kicad_pcb`

   Il comando sopra **non effettua e non conserva automaticamente il refill nella versione 9**. Dopo aver riempito le zone con l'interfaccia KiCad, salvare la copia e ripetere il DRC. La versione KiCad 10 dispone di opzioni aggiuntive `--refill-zones` e `--save-board` da verificare nella versione installata.
9. Confrontare netlist contro lo schema V3.1; non assumere il controllo statico 31 pin come ERC schematico.
10. Validare meccanica in 3D, dimensioni bordo e launch SMA; approvare soldermask/solderpaste Gerber prima della fabbricazione.
11. Soltanto dopo le verifiche precedenti produrre Gerber, drill e distinta finali. Eseguire collaudo VNA RX con segnale debole e alimentatore limitato, antenna TX scollegata.

### Fonti
- https://docs.kicad.org/9.0/en/cli/cli.html
- https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf
- https://www.mouser.com/datasheet/2/418/9/ENG_DS_CONSMA002_SMD_G_B-3238924.pdf
