# V5.1 — passaggio di mano per la validazione KiCad 10

**Questo documento non contiene report nativi:** nel corrente ambiente `kicad-cli` e `pcbnew` non sono disponibili, e il tentativo di aggiornare gli indici dei pacchetti è stato interrotto senza completamento. Non sono stati eseguiti ERC/DRC/refill/parità.

1. Installare KiCad 10 da fonte ufficiale su una macchina compatibile e verificare `kicad-cli version`.
2. Estrarre **l'intero** ZIP V5.1, preservando cartelle e file `.pretty`, `.kicad_sym`, `fp-lib-table`, `sym-lib-table`.
3. Dalla radice del progetto eseguire `python3 03_Verifiche/V5.0/run_kicad_native_v50.py --output-dir ./KICAD_REPORTS_V5_1` (su Windows: `py -3 03_Verifiche/V5.0/run_kicad_native_v50.py --output-dir .\KICAD_REPORTS_V5_1`).
4. Il programma usa **una copia temporanea** dei sorgenti, non produce Gerber e segnala se il comando CLI manca o non dispone delle opzioni necessarie. Allega i file `ERC_V5.0.json`, `DRC_PARITY_REFILL_V5.0.json`, `STATUS_V5.0.json` e i log, se disponibili, alla prossima revisione del progetto.
5. Se ERC/DRC riportano violazioni o i report risultano incompleti, lasciare il gate di produzione bloccato. Anche report senza errori richiedono controllo visivo, parità col progetto, confronto TE, processi VIPPO/stencil e collaudi hardware.

**Nota:** i nomi dei report riportano V5.0 perché si usa la procedura già collaudata staticamente, su un **PCB candidato immutato V4.8**; la V5.1 non dichiara l'esecuzione dei report.

Test statico indipendente: `python3 03_Verifiche/V5.1/test_v51.py`; distinta e netlist del PCB rigenerabili con `python3 03_Verifiche/V5.1/genera_bom_net_v51.py`.
