# Registro verifiche V0.3

| ID | Verifica | Esito | Limite |
|---|---|---|---|
| SW01 | Numero 270 canali, ALFA, CH9 | PASS | Test automatico, no radio fisica |
| SW02 | Sintesi ADF4351 R20/PFD640kHz/INT/N 270 canali | PASS | Solo matematica, no programmazione chip |
| SW03 | Logica PTT e interlock firmware modello | PASS | Hardware non realizzato |
| SW04 | Budget rumore RX Friis valori teorici | PASS | Parametri ipotetici |
| SW05 | Pinout e range PLL, test addizionali | PASS | Pinout confrontato con datasheet, connessioni proposte |
| SW06 | S21 modello filtro ideale, finite Q, sweep e Monte Carlo | PASS | Simulazione analitica a blocchi RLC, NON SPICE/EM |
| HW01 | Filtro anello PLL, stabilita', fase | NON FATTO | Mancano valori e modello |
| HW02 | Misurazioni mixer LO +7dBm, spurie, phase noise | NON FATTO | Mancano buffer e scheda |
| CAD01 | KiCad schema/ ERC, PCB/ DRC | NON FATTO | Nessun KiCad verificabile in ambiente |
| PR01 | Prototipo, misure e conformita' | NON FATTO | Non fabbricato |
