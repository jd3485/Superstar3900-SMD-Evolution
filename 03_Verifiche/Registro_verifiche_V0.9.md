# Registro verifiche V0.9

| Controllo | Esito | Portata |
|---|---|---|
| Fonti TI pinout U2/U3 SOT23-5 | PASS su datasheet p4 | IN1, GND2, EN3, NC4, OUT5 |
| Pinout TXC generico 7N | PARZIALE | Pin10 AFC/GND specifico da verificare |
| Schema KiCad parentesi / ref unici | PASS Python | Non equivale a ERC o compatibilita KiCad |
| Reti LDO separate | PASS etichette e campi | Non si sostituisce al netlist KiCad |
| Stima termica | PASS matematica | Correnti e thetaJA ipotetici |
| Sei suite software V0.8 | PASS | Non provano l'hardware |
| KiCad ERC/DRC | NON ESEGUITO | KiCad CLI assente nel runtime |
| Test TCXO in oscilloscopio, spurie e rumore | NON ESEGUITO | Serve prototipo e strumentazione |
| Progettazione 13.8 V -> 5.0 V | NON ESEGUITA | Sorgente esterna nel presente schema |
| Componenti / footprint TCXO | BLOCCATO | Richiede verifica MPN e disegno meccanico |
