# Registro rischi aperti - V0.2

| ID | Rischio | Mitigazione prima del PCB |
|---|---|---|
| R-01 | Spurie/rumore di fase ADF4351 a 36-39MHz | Simulare PLL, filtri e misurare LO con analizzatore |
| R-02 | ADF4351 +5dBm non sufficiente per mixer LO +7dBm | Buffer e filtro con alimentazione dedicata, misure matching/isolamento |
| R-03 | Filtri 10,695MHz/2,4kHz SMD non acquistabili o prestazioni scarse | Valutare filtro custom/quarzi o cambiare architettura FI |
| R-04 | LNA migliora NF ma satura con segnali forti | Attenuatori e bypass LNA, progettazione IP3, 2-tone test |
| R-05 | MCU/display generano spurie udibili in RX | Schermature, supply filter, clock planning, layout RF, EMI scan |
| R-06 | ATU con ROS elevato stressa L/C/relè | Design voltage/current margin, carichi reattivi, riduzione potenza |
| R-07 | Termica PA e dissipazione SMD | PA meccanicamente/termicamente appropriato, misure termiche |
| R-08 | Compatibilita con guscio anni 80 sconosciuta | Rilevare dimensioni/punti di fissaggio prima della PCB |
| R-09 | Normativa RED/ETSI e limitazioni per apparato 270 RX | Blocchi TX HW, revisione conformita e laboratorio competente |
| R-10 | Mancanza software CAD/SPICE nell'ambiente corrente | Non attribuire ERC/DRC/simulazione non eseguita; installare in fase adeguata |
