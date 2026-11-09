# Piano moduli radio V6.0 — costruzione progressiva PRIMA della simulazione

V5.9: definite 26 responsabilità di sistema e interconnessioni logiche. V6.0: schematizzato il primo modulo AUDIO/PA tramite componenti, pin, connettori e netlist preliminare. **Non è ancora un PCB e non equivale a un modulo collaudato.**

1. V6.0 AUDIO/PA: COMPONENT-LEVEL CANDIDATE con MUX 5:1, bias, MIC elettrete, codec remoto, finale mono BTL, 2 speaker, sequencing PA/PTT e protezione TX esclusa.
2. V6.1 MCU/pannello: assegnazioni GPIO reali, rotative, ALFA, CH9, display e comandi; integrerà le 16 linee J604.
3. V6.2 Alimentazioni e interblocchi: circuito HW vero della condizione `PA_MODE_HW -> RF_TX_ENABLE = 0` e gating di `AMP_SD`, power-good e watchdog; verifica correnti audio.
4. V6.3 PLL/BFO; V6.4 FI/demodulatori; V6.5 TX IF; V6.6 PA RF e filtri; V6.7 ATU+ROS/PEP; V6.8 PCB/cablaggi/meccanica; V6.9 firmware/consolidamento.
5. **DOPO** il progetto completo: riesame tecnico globale, simulazioni SPICE/RF/audio/termica, KiCad ERC/DRC nativi, revisioni correttive e collaudi.

Criticità non rimandabili: scegliere e definire componente elettronico corretto prima di congelare il circuito, mantenere TX fail-closed e non dichiarare un circuito completo quando mancano gli interblocchi fisici.
