# Procedura riproducibile KiCad 10 — V5.0

Il pacchetto comprende il candidato V4.8 con librerie locali; nessun file CAM è autorizzato. Usare **KiCad 10** reale su un computer che disponga di `kicad-cli` nel PATH e Python 3.10+.

Su Windows PowerShell, entrare nella cartella principale del progetto estratto e lanciare:

```powershell
py -3 03_Verifiche/V5.0/run_kicad_native_v50.py --output-dir .\KICAD_V50_REPORTS
```

Su Linux/macOS:

```bash
python3 03_Verifiche/V5.0/run_kicad_native_v50.py --output-dir ./KICAD_V50_REPORTS
```

Il programma verifica versione/opzioni CLI, copia l'intera cartella candidato in una directory temporanea (librerie comprese), esegue `sch erc` e `pcb drc` con `--refill-zones --schematic-parity`, registra i report JSON/log e controlla che i sorgenti originali siano rimasti byte-identici.

- Se KiCad manca, `STATUS_V5.0.json` esplicita `NOT_RUN` e il comando restituisce exit code 3.
- Se la versione/opzioni non sono compatibili, nessun controllo nativo è considerato eseguito.
- Se i comandi falliscono o i report mancano, lo stato è `FAILED_OR_INCOMPLETE`.
- Se i comandi terminano senza errore, lo stato è `COMMAND_COMPLETED_REVIEW_REQUIRED`, **non** `FAB_APPROVED`.

In ogni caso il gate produzione resta BLOCCATO fino a revisione manuale dei report, parità reale, footprint TE, VIPPO, stencil, stack-up, collaudi termici/RF e autorizzazione esplicita. Conservare i report in una successiva revisione cumulativa. **Non generare Gerber o caricare file sul portale di fabbricazione a partire da questa procedura.**
