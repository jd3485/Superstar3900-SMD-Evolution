# Registro V1.1: stato verifiche

| Oggetto | Esito | Ambito |
|---|---|---|
| Pin PWP TPS26600 U200 1-17 | CONTROLLATO vs TI | pin map nel datasheet, non nella libreria KiCad nativa |
| RTN diverso da GND | PASS statico | reti distinte, non verifica PCB |
| Divisore UVLO/OVP | PASS matematico | equazioni TI, tolleranze resistori senza leakage |
| Limite corrente R=8.2k | PASS matematico | tipico 1.463A, non misurato |
| 6 suite precedenti e test V1.0 | PASS locale | Python, non circuito |
| Test KiCad ERC, DRC | NON ESEGUITI | CLI assente; necessario |
| Simulazioni elettroniche di surge, ripple, EMI | NON ESEGUITE | necessario |
| Corrente, termica, inverter/corto hardware | NON ESEGUITI | necessario |
| TXC pin10, footprint | BLOCCANTE | da verificare variante reale |
| Protezione TVS/fusibile | INCOMPLETA | MPN, I2t, surge e fusibile non scelti |
| CW e PA | REQUISITI SOLI | hardware/firmware non progettati |

Datasheet: https://www.ti.com/lit/ds/symlink/tps2660.pdf
