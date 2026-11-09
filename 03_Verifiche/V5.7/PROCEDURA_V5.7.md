# Procedura operativa V5.7 (studio GND + KiCad reale)

**NON FAB / NO TX.** Non utilizzare alcun report di questa procedura come prova di autorizzazione produttiva.

1. Estrarre l'archivio V5.7 completo senza modificare la coppia schema/PCB originale.
2. Per replicare la stima geometrica: `python3 -B 03_Verifiche/V5.7/audit_piani_gnd_v57.py --output AUDIT_RIPETUTO.json` (richiede Python 3.11+ e Shapely 2.x). Seguire con `python3 -B 03_Verifiche/V5.7/test_piani_gnd_v57.py`.
3. Su un PC Linux con KiCad **10**, lanciare `python3 -B 03_Verifiche/V5.7/run_piani_e_kicad_v57.py --output REPORT_NATIVE_V5.7` (stessa dipendenza Python). Il programma usa il runner storico fail-closed che lavora su una copia. Una mancanza di KiCad crea `NOT_RUN_KICAD_MISSING` e ritorna codice 5.
4. Alternativa non ancora eseguita: pubblicare manualmente il progetto in un repository di propria scelta e avviare `.github/workflows/kicad_native_v57.yml` mediante `workflow_dispatch`; scaricare **tutti** i report allegati. La sola presenza del file YAML non dimostra l'esecuzione.
5. Esaminare il DRC con `--refill-zones`, gli `unconnected_items`, parità schema/PCB ed ERC. Verificare **ogni massa SMA**, ciascun pad U101, il collegamento alle vie termiche e l'assenza di isole dopo le regole di rimozione; una superficie geometrica teorica continua non basta.
6. Chiudere formalmente i 9 gate V5.0 solo dopo DRC/ERC/verifiche meccaniche/termiche/DFM e prove hardware. Vietata ogni produzione in assenza delle autorizzazioni specifiche.

L'audit statico assume una distanza di 0,30 mm dalle reti non GND per i soli ostacoli F.Cu e non modella thermals, riempimento KiCad, foro/via, neck eliminati, netclass clearance prevalenti o stack-up. **Non è il software KiCad.**
