# Procedura valida per eseguire la V5.2 su PC con KiCad 10

1. Estrarre **l'intero archivio** in una cartella permanente (non lavorare dentro lo ZIP).
2. Aprire la cartella `04_KiCad/Modulo_RX_Test_50ohm_V5.2_PARITY_LINK_STUDY_NOT_FOR_FAB` e verificare i nomi identici `.kicad_sch` e `.kicad_pcb`.
3. Con Python 3.10+ lanciare dalla radice del progetto: `python3 03_Verifiche/V5.2/audit_associazioni_v52.py` e `python3 03_Verifiche/V5.2/test_v52.py`. Questi sono controlli **statici**, non ERC/DRC.
4. Su computer dove `kicad-cli version` mostra **10.x**, avviare `python3 03_Verifiche/V5.2/run_kicad_v52.py --output REPORT_NATIVE_V5.2`.
5. Conservare `STATUS_V5.2.json`, `LOG_ERC.txt`, `LOG_DRC.txt`, `ERC_V5.2.json`, `DRC_V5.2.json` (quando prodotti) e consegnarli per analisi. Anche codice uscita zero non costituisce approvazione DFM.
6. Prima di qualsiasi produzione, validare ufficialmente TE SMA, il processo delle 6 vie termiche e la pasta U101, lo stack-up RF e i collaudi. **NO GERBER / NO ORDINE / NO TX.**
