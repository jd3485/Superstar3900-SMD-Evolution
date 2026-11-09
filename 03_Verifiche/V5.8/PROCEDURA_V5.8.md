# Procedura V5.8 — analisi RF + verifica KiCad 10 (NO FAB)

Eseguire dalla radice ZIP estratta, con Python >=3.11, NumPy e Shapely 2.x:

```bash
python3 -B 03_Verifiche/V5.8/audit_ritorno_rf_v58.py --output VERIFICA_RITORNO_RF.json
python3 -B 03_Verifiche/V5.8/test_ritorno_rf_v58.py
python3 -B 03_Verifiche/V5.8/genera_mappa_rf_v58.py
```

Per tentare la verifica nativa (serve **KiCad 10** installato e funzionante):

```bash
python3 -B 03_Verifiche/V5.8/run_audit_e_kicad_v58.py --output REPORT_V5.8
```

Il lanciatore esegue prima l'audit RF e poi il runner V5.7, che verifica topologia e modello di zona e invoca il precedente runner ERC/DRC/refill/parità su **una copia**. Senza `kicad-cli` genera `NOT_RUN_KICAD_MISSING`, codice 5. Il workflow GitHub Actions V5.7 è presente ma NON è stato avviato. Conservare tutti i report con la revisione esatta del PCB. Se KiCad restituisce errori, risolvere solo in una nuova copia sperimentale, non negli originali.

**Interpretazione:** una via GND a 9,58mm NON prova un problema di ritorno RF; il piano di massa può fornire il ritorno. Una zona ideale non è una zona KiCad riempita. Non eseguire fabbricazione finché ERC/DRC reali, stackup, CAD TE e DFM termica non sono completati e approvati. **No TX**.
