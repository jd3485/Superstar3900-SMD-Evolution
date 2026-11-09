# Registro verifiche V1.0

| Verifica | Esito | Significato |
|---|---|---|
| Pin 1-6 TPS54202DDCR | CONTROLLATO vs TI | DDC p1 GND p2 SW p3 VIN p4 FB p5 EN p6 BOOT |
| Componenti design reference | CONTROLLATO vs TI | 13 ref, 8 reti, schematico separato, verifiche statiche |
| Vout 0.596*(1+100/13.3) | CALCOLATO | circa 5.077V tipici nel modello |
| Ripple 15uH 500kHz | CALCOLATO | Modello buck ideale, non misura/simulazione |
| Suite regression V0.9 / V1.0 | PASS | Script locali; senza SPICE o EDA |
| ERC e netlist KiCad ufficiale | NON ESEGUITO | tool nativo non presente |
| Protezioni ingresso | NON PROGETTATE | front-end fusibile/TVS/reverse polarity |
| Verifica PCB e dissipazione | NON ESEGUITA | nessuna PCB reale |
| Spurie RF e rumore ricevitore | NON ESEGUITI | richiede test fisici |
| TXC pin10 e impronta | BLOCCANTE | documentazione fornitore specifica da acquisire |
