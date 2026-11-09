# Changelog V3.6 - 7 novembre 2026

**Avanzamento totale stimato 37% (invariato rispetto a V3.5).** Studio indipendente della rete GND e riconciliazione delle reti del coupon RX a 50 ohm.

- Generata da V3.5 una nuova PCB KiCad con 20 segmenti GND aggiuntivi, 20 via di ritorno espliciti e 40 via di stitching selezionati per le linee RF; 43 segmenti / 64 via totali, 15 impronte, 8 reti.
- Aggiunta dichiarazione di zona In2.Cu GND: quattro layer con zone GND **non riempite**.
- Corretta numerazione delle piazzole dell'induttore L101: pin1=+5V e pin2=RFOUT_BIAS (coerenza V3.1).
- Implementato audit indipendente shapely con convalida topologica 7 reti, verifica di 31 pin V3.1, 24 contatti GND e distanza minima F.Cu modellata 0.45 mm; zero collisioni al limite esplorativo 0.20 mm.
- Aggiunti test negativi: pin L101 V3.5 erronei, corto artificiale, rete intenzionalmente interrotta.
- Aggiunti protocollo collaudo futuro, registro 7 blocchi e disegno aggiornato. Nessun componente fisico collaudato; KiCad nativo non disponibile.
- Il connettore SMA con caratteristiche Ø2.05 non è approvato: **NO GERBER, NO PCBWAY**.

La V3.6 non modifica i requisiti dell'intera radio né le restrizioni TX, recepisce tutte le revisioni precedenti nel ZIP cumulativo.
