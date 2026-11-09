# Registro verifiche V0.1

| Verifica | Metodo | Stato |
|---|---|---|
| Piano 270 frequenze | Script Python, conteggio, unicità, estremi | ESEGUITO: test_frequency_plan.py |
| Sequenza 6 bande 40+5 | Confronto con chart storica | PRELIMINARE |
| Interruttore ALFA separato | Test di frequenza per 3,7,11,15,19 | ESEGUITO: modello software |
| Richiamo CH9 | Test 27,065 MHz con priorità | ESEGUITO: modello software |
| Inibizione TX su canali extra CB | Regole software e test del modello | ESEGUITO SOLO A LIVELLO LOGICO |
| Interblocco hardware TX | Schema + fault injection in prototipo | DA PROGETTARE |
| PLL e rumore di fase | Budget di rumore e simulazione circuitale, strumentazione | DA PROGETTARE |
| Filtri preselettori + FI | Simulazione S-parameter/attenuazione, misure VNA | DA PROGETTARE |
| Sensibilità/dinamica RX | Segnalatore RF calibrato, SINAD, intermodulazione | NON MISURATO |
| TX armoniche e spurie | Simulazione + analizzatore di spettro e carico 50 Ω | NON MISURATO |
| Wattmetro e ROS | Taratura con wattmetro campione e carichi noti | NON MISURATO |
| Accordatore | Test su carichi controllati / ROS / potenza / protezioni | NON MISURATO |
| Alimentazioni e temperatura | Simulazione, sovracorrente, camera termica / termografia | NON MISURATO |
| ERC / DRC KiCad | Verifiche integrate e test di fabbricabilità | IN ATTESA DI SCHEMI/PCB |
| Assemblaggio PCBWay | DFM/DFT, BOM componenti realmente disponibili | IN ATTESA DI SCHEMI/PCB |
| Conformità regolamentare | Laboratorio competente e documentazione RED | DA VERIFICARE PRIMA DI QUALSIASI USO TX |

Una simulazione soddisfacente non sostituisce mai le verifiche fisiche RF o una certificazione.
