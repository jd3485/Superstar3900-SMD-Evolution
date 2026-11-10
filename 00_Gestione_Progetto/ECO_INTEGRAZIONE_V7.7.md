# ECO V7.7 — top RTL diagnostico, sintesi logica e quantizzazione (NO FAB / NO TX)

**Data 10 novembre 2026**, partenza `main` V7.6 (`591b3df`). Conservare revisioni V7.0–V7.6, tag `v7.0` e tutti i componenti TX DNP.

1. Nuovo top Verilog `v77_offline_top` collega i componenti V7.6 `v76_clock_ce` e `v76_virtual_fifo_guard` in un'unità **diagnostica virtuale**. I tre output di consenso fisico `tx_rf_permission/dac_pd_released/analog_path_connected` sono **0** in ogni condizione. Non esiste porta DAC900 reale.
2. Testbench V7.7 aggiunge monitor di controllo esterno *assunto* e underflow; Icarus compila/simula. Yosys esegue `synth` generico e `check -assert`. Non considerare tale verifica come nextpnr, iCE40 STA, bitstream o prova elettrica.
3. Pinout Lattice official XLSX `document_id=51971` rilevato nel catalogo prodotto, ma il download bytes non è riuscito. Il file V7.6 dei 48 pin/PCF rimane HOLD, senza autorizzazione a usare pad/footprint; datasheet primario conferma solo conteggi/paddle.
4. Modello quantizzazione 10bit e due toni 750/1250Hz dopo FIR 5×4×4 con headroom 70%; calcola errori RMS numerici e step code ranges; non misura DAC900, SNR RF o filtro fisico.
5. Nuovo inventario dei guasti indipendenti: PD floating/stuck-low, supervisor open/short, clock stop, configurazione FPGA, backfeed, PA relay welded. Tutti i fault sono **NOT_RUN** per copertura fisica. Il watchdog su clock fermo non può essere implementato dalla sola logica sincrona alimentata dal master.
6. BOM V7.7 **8 elementi OPEN/DNP**, netlist virtuale **10 terminali OPEN/DNP**. Nessun rail, oscillatore, FPGA, DAC, IF o TX elettricamente connessi. Conservare i ponti DNP precedenti.
7. Eseguire CI + regressioni e riportare PASS/FAIL/SKIP/NOT_RUN prima di unire PR in `main`. **NO FAB / NO TX**. Prossima V7.8: pinout originale e solo allora PNR, guard hardware con componenti candidati e spettri più realistici.
