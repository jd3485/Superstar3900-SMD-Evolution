# Superstar 3900 SMD Evolution — esecuzione KiCad 10 (V5.4)

**Progetto di studio, NON PER FABBRICAZIONE.** L'archivio include il workflow, **ma non ha eseguito KiCad 10**. Il file `NATIVE_NOT_RUN/STATUS_V5.4.json` lo documenta.

## Percorso A: PC con KiCad 10

1. Estrarre interamente il pacchetto ZIP, incluse le sottocartelle `04_KiCad`, le librerie `.pretty`, le tabelle e lo schema; non lanciare controlli dallo ZIP compresso.
2. Installare KiCad 10 ufficiale. Controllare `kicad-cli version` nel terminale. Su Windows aggiungere al PATH la directory KiCad 10 `bin` se necessario.
3. Nella radice dell'archivio eseguire:

   ```bash
   python3 -B 03_Verifiche/V5.4/run_native_v54.py --output REPORT_NATIVE_V5.4
   ```

4. Allegare `REPORT_NATIVE_V5.4/STATUS_V5.4.json`, `ERC_V5.4.json`, `DRC_PARITY_V5.4.json` e i log prodotti. Un errore di KiCad è un risultato tecnico da analizzare, non un via libera; qualsiasi stato `NOT_RUN` o `VIOLATIONS_OR_INCOMPLETE` è bloccante.

**Protezione:** il runner verifica la versione e le opzioni CLI, copia il progetto in una cartella temporanea, calcola hash prima/dopo dei sorgenti, non chiama comandi Gerber, non modifica le revisioni storiche e non autorizza mai la produzione. `--refill-zones` e `--schematic-parity` sono inclusi nel DRC. Il superamento della CLI **non** copre il confronto CAD TE, VIPPO, stencil, stack-up, termica, validazione RF o conformità normativa.

## Percorso B: GitHub Actions, senza installare KiCad sul proprio PC

Il file `.github/workflows/kicad_native_v54.yml` è un **workflow predisposto ma NON eseguito**. Per usarlo, l'utente deve caricare autonomamente il contenuto **estratto** del progetto in un proprio repository GitHub (preferibilmente privato), aprire **Actions → Superstar3900 RX KiCad 10 - native verification (NO FAB) → Run workflow** e scaricare l'artefatto `superstar3900-native-kicad-v54-reports`. Il workflow installa KiCad 10 dal PPA ufficiale su un runner `ubuntu-24.04`, esegue gli stessi controlli e carica i report anche se il controllo fallisce. Non è una garanzia che l'esecuzione futura riesca: dipende dal servizio GitHub, dall'accessibilità del PPA e dalla compatibilità reale dei sorgenti.

Il caricamento su GitHub è un'azione volontaria dell'utente: **questo pacchetto non è stato inviato a GitHub, a TE o a PCBWay**. Non attivare ordini, Gerber o trasmissione RF.

## Interpretazione di `STATUS_V5.4.json`

- `NOT_RUN`: non è stato possibile avviare KiCad 10 o verificare le opzioni necessarie.
- `VIOLATIONS_OR_INCOMPLETE`: ERC/DRC segnala violazioni, un errore, un timeout oppure il report è mancante/danneggiato.
- `EXECUTED_REVIEW_REQUIRED`: KiCad ha prodotto un report JSON con exit code 0, che deve comunque essere letto da una persona competente.
- `release = BLOCKED_NOT_FOR_FAB`: **sempre**, anche se non emergono violazioni nei controlli CLI. I nove gate V5.0 restano aperti.

## Verifiche software V5.4

`python3 -B 03_Verifiche/V5.4/test_native_runner_v54.py` prova *con comandi CLI simulati* la gestione di: programma assente, versione errata, output positivo simulato, violazioni simulate, JSON non valido, immutabilità dei file e gate non approvati. **Nessuna di tali prove è un'esecuzione KiCad reale.**

`python3 -B 03_Verifiche/V5.4/run_regressioni_v54.py` riesegue 14 suite storiche e questa suite V5.4 (15 in totale), creando il solo rapporto V5.4.

Fonti per configurazione: https://docs.kicad.org/10.0/en/cli/cli.html ; https://www.kicad.org/download/details/ubuntu/ .
