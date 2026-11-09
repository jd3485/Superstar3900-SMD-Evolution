# Changelog V5.3 — 8 novembre 2026

- Aggiunto parser statico indipendente delle espressioni S KiCad per schema, PCB e librerie di impronte.
- Ricostruiti 31 collegamenti elettrici da posizioni dei pin, fili ed etichette. Zero differenze rilevate rispetto alle reti dei pad; 15 footprint locali corrispondono alle librerie.
- 18 test nuovi, con prove di corruzione intenzionale, superati; tutte le 14 suite V4.0–V5.3 superate.
- Runner KiCad V5.2 rieseguito con esito NOT_RUN perché `kicad-cli` non è disponibile; nessun ERC/DRC native né produzione.
- Modificati soltanto documenti gestionali, con snapshot dei file originali. Schemi e PCB V5.2 e storici invariati.
- Manuale V4.0 e nove gate aperti conservati. NO FAB / NO TX; avanzamento storico 37%, nessun hardware validato.
