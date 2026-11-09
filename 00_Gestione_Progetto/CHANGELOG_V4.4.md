# CHANGELOG V4.4 — 2026-11-08

- Generato, SENZA alterare i PCB né V3.1, uno schema elettrico candidato RX con 15 componenti/31 pin/8 reti, i valori e gli ID footprint del PCB storico.
- Due etichette di rete storiche riallineate (`RF_LNA_INPUT`, `RF_BIAS_OUT`), campi footprint compilati nella copia V4.4.
- Generatore deterministico e con controllo SHA256 del PCB V3.8; CSV netmap, JSON di verifica e 20 test con casi negativi. Regressioni V4.3 21, V4.2 19, V4.1 12, firmware V4.0 su 2.400 stati rieseguite.
- Script per ERC/DRC nativi su COPIE, fermato in assenza di `kicad-cli` (nessun falso PASS); parità/UUID non ancora verificati.
- Riepilogo blocchi: librerie dei footprint autonome incomplete, SMA TE, termica ADL5535, stack-up reale e misure RF.
- Manuale V4.0 e tutti i file della V4.3 preservati; snapshot integrali degli attivi modificati; produzione NON autorizzata.
