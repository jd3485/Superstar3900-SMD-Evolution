# Requisiti prima di liberare la scheda-sintetizzatore

1. Scegliere TCXO: datasheet originale, fase noise, layout pad e livelli OSCin compatibili.
2. Eseguire TI PLLatinum Sim (o simulazione RF validata) alle estremita, confine VCO3/VCO4 e canale 9; verificare PN @ 100 Hz, 1k, 10k, 100k, 1MHz e spurie.
3. Validare i valori filtro d'anello in tutte le condizioni reali; considerare thermal/DC bias dei condensatori e dispersione CPG e KVCO.
4. Definire circuito alimentazione low-noise e simulare worst case termico / inrush / instabilita LDO.
5. Schema KiCad con libreria pin completata, file symbol/footprint validati contro TI Rev B, ERC senza errori non giustificati.
6. Generare file programma PLL da TICS Pro e collaudarli su EVM o PCB prototipo con misura lock, livello e spurie, registro per registro, soprattutto output divider /128.
7. Verificare buffer LO 36-39MHz, 50 ohm, level plan per mixer, armoniche e isolation digitali.
8. PCB 4 layer: via-in-pad DAP se assemblaggio lo permette, stella massa RF continua, filtri pin vicini, nessuna via su CPout/VTUNE se evitabile, pareti schermanti e test point disaccoppiati.
9. Produzione sotto test su carico fittizio. Nessuna dichiarazione di EMC o conformita prima dei test del dispositivo completo.

Stato: 0/9 gate chiusi; solo verifiche aritmetiche e modello preliminare eseguiti.
