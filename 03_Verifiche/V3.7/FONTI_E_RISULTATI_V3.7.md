# V3.7 — SMA land, lato di accoppiamento e footprint ADL5535

FONTI PRIMARIE (consultate 2026-11-07):
TE/Linx CONSMA002-SMD-* rev D, foglio 2/3, impronta consigliata:
https://www.ic-components.cz/files/17/CONSMA002-SMD.pdf
Analog Devices ADL5535 rev A, Fig. 17 pagina 11 e Fig. 16:
https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf
KiCad CLI v9 DRC reference:
https://docs.kicad.org/9.0/en/cli/cli.html

## Conclusioni

- Ø2,05 appare nel **RECOMMENDED FOOTPRINT** TE: è il diametro del land centrale; non appare come prescrizione di foratura. Il layout usa un pad SMD circolare senza drill.
- I quattro connettori ad angolo retto hanno verso di accoppiamento esplicitato; due ruotati di 180°, senza cambiare la connettività elettrica data la simmetria della disposizione di prova.
- Le quattro piazzole quadrate GND del candidato **NON riproducono ancora** il contorno di massa sagomato dal fabbricante. Il footprint è **NON APPROVATO**.
- L’ADL5535 riproduce le quote principali della Fig.17, ma mancano revisione paste/termica e veri controlli ERC/DRC.
- KiCad CLI assente (installazione Debian tentata, repository non raggiungibile). Nessuna zona riempita, nessun Gerber, nessun hardware misurato.
