# V2.1 - Registro modifica

- Fonte: progetto cumulativo V2.0 (con storico completo).
- Corretto errore di progetto: FM su ADC destro U202/16 invece che ADC sinistro U202/15.
- Aggiornati schema KiCad modificabile e tabella pin completa; non modificati C229 / R208 / C230 perche' rimangono parametri candidati.
- Confrontate le 8 assegnazioni delle periferiche STM32 SAI/I2C/SPI con alternate functions del datasheet ST. AF non ancora validate in CubeMX.
- Creato calcolo riproducibile delle frequenze immagine e del budget di rumore ideale.
- Stima avanzamento complessivo: **29%**, invariata, poiche' si tratta di correzione strutturale e studio iniziale RF, senza completamento di un sottosistema validato.
- Bloccanti: ERC nativo, pin/footprint TCXO, PLL reale, doppio ADC configurazione codec, livelli audio, RF simulazioni/misure, TX compliance.
- PCBWay: NOT READY.
