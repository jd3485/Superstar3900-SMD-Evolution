# Superstar 3900 SMD Evolution — guida GitHub (V7.0)

**Repository creato e popolato:** https://github.com/jd3485/Superstar3900-SMD-Evolution (**PRIVATO**, verificato il 9 novembre 2026).

## Importazione completata
- Il branch `main` è stato importato dal kit Git locale e il tag annotato `v7.0` è presente.
- Commit originale della baseline: `b4242f58b75ecaea7093fe960e63c96c5a43d87a`.
- Il commit iniziale conteneva **1.286 file Git**, inclusi gli **1.281 file originali V7.0** e 5 file di infrastruttura. Manifest originale: `MANIFEST_SHA256_V7.0.csv` (1.280 record/hash dei file del pacchetto, escluso il manifest stesso).
- Il workflow `.github/workflows/verifica_v70.yml` è stato eseguito con successo dopo l'importazione. Per permettere l'evoluzione del branch `main`, la verifica hash immutabile della V7.0 opera sulla **copia di lavoro del tag v7.0**; i test di regressione verificano il branch corrente.
- README e istruzioni di ripresa hanno una sezione corrente V7.0 in testa; il testo storico precedente è stato conservato integralmente. I file originali sono sempre recuperabili dal tag `v7.0`.

## Come lavorare alle revisioni successive
1. Sviluppare nuove specifiche, BOM, schemi, netlist, codice e test in percorsi per versione (es. `V7.1`).
2. Salvare tramite commit GitHub i soli file nuovi o cambiati, verificare `main` e i risultati CI; registrare quanto NON è stato eseguito.
3. Creare un tag `v7.1`, `v7.2` ecc. per la relativa versione completa.
4. Da ogni tag GitHub rende disponibile uno **ZIP sorgente cumulativo** dell'intero albero versionato, senza dover inserire dentro Git lo ZIP personalizzato dell'intero progetto per ogni revisione. Gli ZIP storici personalizzati, se richiesti, vanno prodotti separatamente e identificati con SHA256; per caricarli come allegati di Release occorre un'azione apposita di upload.
5. Mantenere un documento di ripresa aggiornato nella radice e aprire le nuove chat leggendo prima la sezione corrente del file.

## Restrizioni tecniche
**NO FAB, NO TX**: il progetto è ancora candidato; non sono stati effettuati collaudi fisici, PCB native completi, ERC/DRC, simulazioni EM/RF misurate o autorizzazioni a trasmettere. La TX RF resta fisicamente disabilitata.
