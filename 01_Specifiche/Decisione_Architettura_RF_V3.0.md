# Decisione tecnica preliminare V3.0

**Nessuna nuova architettura RF approvata per produzione.**

Il modello Coilcraft V2.9 indica un CORE9 nominale con 2,00 dB di perdita massima e 62,95 dB di reiezione minima delle immagini, ancora senza parassiti del layout e commutazione TX/RX.

Il calcolo della catena V3.0 considera inizialmente il CORE9 prima dell'ADL5535, in quanto mantiene il maggior filtraggio prima dell'amplificatore; in alternativa sono studiati un attenuatore 6 dB dopo l'LNA, l'esclusione LNA e un filtro diviso solo ipotetico.

La figura di rumore della catena è approssimata via Friis; l'IIP3 via formula small-signal reciproca. Il mixer ADE-1+ ha specifiche generiche +7 dBm LO, circa 5 dB di perdita e +15 dBm IP3. L'ADL5535 usa i dati tipici del datasheet a 20 MHz come proxy per i 27 MHz (16,7 dB guadagno; 3,0 dB NF; 41,5 dBm OIP3); i dati a 27 MHz andranno misurati.

La sensibilità effettiva, la capacità di ricezione sotto forti segnali, la NF del mixer rispetto al percorso SSB, e le spurie PLL **non sono validate**. I risultati numerici non costituiscono un progetto PCB o una garanzia prestazionale.

Link fonti ufficiali:
- https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf
- https://www.analog.com/en/products/adl5535.html
- https://www.minicircuits.com/WebStore/dashboard.html?model=ADE-1%2B
- https://www.coilcraft.com/getmedia/c86a99da-e310-4932-bb03-09af08346f8a/spice_0805cs.pdf
