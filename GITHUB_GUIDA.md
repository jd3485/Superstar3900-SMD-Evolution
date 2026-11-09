# Superstar 3900 SMD Evolution — origine Git V7.0

**Repository remoto previsto:** `https://github.com/jd3485/Superstar3900-SMD-Evolution` (PRIVATO; non ancora creato da ChatGPT).

Questa è una **importazione Git locale**, non una conferma che i file siano già su GitHub. Il commit iniziale include gli **1.281 file originali V7.0**, invariati. Gli altri file (`.gitattributes`, `.gitignore`, `GITHUB_GUIDA.md`, `ci/`, `.github/workflows/verifica_v70.yml`) sono aggiunte di infrastruttura, senza modificare il contenuto del progetto storico.

## Importazione

1. Su GitHub crea **un repository privato** chiamato `Superstar3900-SMD-Evolution`, sotto l'account `jd3485`, **vuoto** (nessun README, .gitignore o licenza iniziali).
2. Scarica `Superstar3900_Kit_GitHub_V7.0.zip`, estrai e avvia `IMPORTA_GITHUB_WINDOWS.bat` (con Git for Windows) oppure lo script per macOS/Linux. Lo script clona il `*.bundle`, assegna il repository remoto e invia il branch `main` e il tag `v7.0`. L'accesso GitHub avviene tramite il normale sistema di autenticazione Git: non salvare password o token nei file del progetto.
3. Controlla il repository privato e il workflow **Verifica archivio e test RX**. Il workflow viene eseguito al push su `main` e può essere eseguito manualmente.

**Nota sullo ZIP storico:** `09_Archivi_Precedenti/Superstar3900_SMD_Evolution_V1.1.zip` pesa ~38 MiB e viene tracciato solo per preservare tutti i file del progetto V7.0. Da V7.1 in poi, pubblicare gli archivi cumulativi come allegati di Release (o usare Git LFS) invece di inserirli in ogni nuovo commit.

## Workflow delle revisioni

- Sviluppo in un branch `sviluppo/v7.x` (dopo l'importazione).
- Ad ogni modifica: aggiornare netlist, BOM, specifiche e report; registrare test reali e limiti aperti.
- Commit con descrizione della variazione e tag al rilascio (`v7.1`, ecc.).
- Nessuna approvazione automatica di PCB, TX, DRC/ ERC o SPICE; le relative prove richiedono esecuzione e registrazione separate.
- `python -B ci/verifica_manifest.py MANIFEST_SHA256_V7.0.csv` controlla l'integrità di V7.0 (può non riuscire se file storici vengono modificati senza creare una revisione/snapshot conforme).

### V7.0 non implica radio collaudata

Gli schemi KiCad integrali, le verifiche elettromagnetiche e le misure di laboratorio non sono completati. La trasmissione RF resta fisicamente disabilitata e la fabbricazione non è autorizzata.
