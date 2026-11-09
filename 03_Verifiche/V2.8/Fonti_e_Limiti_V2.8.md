# Fonti e limitazioni V2.8

- Coilcraft 0805CS 220nH: https://www.coilcraft.com/en-us/products/rf/ceramic-core-chip-inductors/0805-%282012%29/0805cs/0805cs-221/
- Coilcraft 0805CS series: https://www.coilcraft.com/en-us/files/datasheet/0805CS
- Elliptic parallel resonance series: https://ham.v4.si/books/microwave/Microstrip%20Filters%20for%20RF-Microwave%20Applications.pdf
- Murata GJM C0G availability: https://www.trustedparts.com/en/manufacturers/murata/GJM

ATTENZIONE: i valori 180nH/470nH e 56/62pF sono candidati, non una BOM approvata.
Il filtro utilizza due risonatori L||C inseriti in serie, concetto tipico dei filtri a zeri di trasmissione.
Il modello NON include ESR/ESL completi, C parassita bobina, SRF, via, piste, accoppiamenti, RF relay e sfasamenti di rete. Q=20/30/60 e tan_delta=0,001 sono ipotesi.
Nessun S2P reale e nessuna validazione elettromagnetica. La presenza del filtro LP senza passa-alto espone ai forti segnali HF sotto la banda utile.
