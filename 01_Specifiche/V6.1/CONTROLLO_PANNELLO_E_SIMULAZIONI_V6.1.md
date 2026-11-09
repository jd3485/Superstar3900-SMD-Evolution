# V6.1 — controlli e modelli eseguibili nel workspace ChatGPT

## Audit elettrico R-C, NON SPICE
- Pull-up ingresso: 10 kΩ; serie interruttore: 220 Ω; C locale 100 nF; VDD 3,3 V.
- Ingressi LOW idealizzati con contatto chiuso: 0.0710 V; Microchip MCP23017 DS20001952D usa per GPIO VIL_max 0,2·VDD = 0.660 V e VIH_min 0,8·VDD = 2.640 V.
- Soglia HIGH idealizzata al rilascio: 1.588 ms, senza contatto rimbalzante, senza capacità di cavo o ESD.
- Corrente di un contatto chiuso: 0.323 mA; tutti i 28 input chiusi simultaneamente: ~9.04 mA (caso elettrico pessimo, non realistico per i selettori one-hot).
- I2C 4,7 kΩ e Cbus 150 pF ipotetici: t_r 30–70% = 0.597 µs; più lento dei 0,3 µs di Fast-Mode, ma entro 1 µs di Standard-Mode. Dunque 100 kHz preliminari, e **non 400 kHz**.
- `CURVE_RC_CONTATTI_V6.1.svg` è grafico calcolato dalle equazioni analitiche, non simulazione SPICE modello transistor o PCB.

## Validazione logica eseguita
- `panel_controller_v61.py`: modello Python di banda, modo, 40+5 posizioni per banda, priorità PA>CH9>RX, mute immediato sui selettori incoerenti, TX sempre OFF.
- Campionamento one-hot a 5 ms, conferma 4 campioni = 20 ms; rotativi con break-before-make generano eventi intermedi mutati.
- Decoder quadratura a 1 ms, 2 campioni identici per ogni lato Gray, 4 transizioni per scatto. **Non garantisce accuratezza del vero encoder ad alta velocità**: filtro/previsione di impulsi mancanti vanno collaudati.
- Suite `test_mcu_pannello_v61.py`: test dei 64 pin, 2×28 piedini I/O expander, collisioni, codici banda/mode, 270 frequenze, CH9 fisico e PA prioritaria, 10.000 combinazioni pseudo-casuali senza TX.

## Controlli ancora aperti
- Nessun ERC/DRC KiCad, firmware compilato su STM32 o SPICE con modelli reali. Il circuito è **candidato**, non montabile direttamente senza selezione connettori, protezioni ESD, layout EMC, isolamenti e valida architettura potenza.
- Ricontrollare la tolleranza dei valori RC con temperatura, Cbus reale, interrupt MCP23017, comportamento di switch rotativi meccanici e consumo del display su prototipo.
- Con V6.2 completare interblocco HARDWARE che neghi RF in PA e dopo qualsiasi reset; nessun risultato Python costituisce autorizzazione TX.
