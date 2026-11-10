# ECO V7.4 — DAC900 bus, clock e I/V: NO FAB / NO TX

**10 novembre 2026.** Overlay incrementale sulla V7.3; lo storico V7.0–V7.3 rimane intatto.

1. Nuovo modulo Python offline V7.4: FIFO virtuale DAC900 10bit, orologio di progetto 3,84MHz, due fronti, ingressi con contratto setup/hold ipotetico, FAULT latched su dati non validi, overflow, underflow, mancanza clock, mancanza alimentazione e violazioni di timing. **Nessun driver DAC né GPIO/PA**, nessuna emissione fisica possibile.
2. Calcolo I/V da datasheet TI DAC900 Rev.B Fig.6: IOUT=IFS*code/1024, coppia di carichi 49,9Ω (circa 25Ω equivalente) e tensione di picco ~0,4985V a IFS nominale 20mA. Due componenti Vishay CRCW060349R9FKEA, R7501/R7502, **DNP**. I numeri sono solo equivalenti resistivi, non misure.
3. R7503 0Ω resta **DNP / aperto** fra DAC IOUT e F7401. R7504 carico IOUTB, U7501 bridge, X7501 clock e J7501 connessione sono candidati **DNP** senza IC/MPN scelti. Nuova BOM V7.4 **7 righe DNP**, netlist concettuale **8 terminali DNP**, pin DAC900 reali conservati in V7.3.
4. Clock audio 48kHz ×80 e dati 10 bit richiedono sorgente sincronizzata; drift 50ppm=192 campioni/sec, FIFO virtuale 1024 parole = ~266,67µs a 3,84MSa/s. Throughput grezzo 38,4Mbit/s, packed 16bit 7,68MB/s. Nessuna allocazione GPIO STM32G474/FPGA, latenze DMA o profilazione realtime inventate.
5. PD pin15 TI è active-high, con pulldown interno: non basta software/FIFO per uno stato di potenza sicuro. R7401 V7.3 resta DNP, servono interblocchi hardwired e reset indipendenti con analisi guasti. V7.4 tiene tx_permission=False per ogni stato; non sostituisce test di interblocco reale.
6. La V7.3 ha già studio F7401 su due porte 50Ω ideali e un DSP senza benchmark, **non** qualificati. Il carico resistivo del DAC non prova attenuazioni di F7401, filtri TX, emission masks, spettri né fabbricabilità.
7. Test V7.4 e regressioni V7.1–V7.3 obbligatori sulla CI, rapporti con PASS/FAIL/SKIP/NON ESEGUITO. Le criticità RX, PLL, LO, IF, schema KiCad, EMC, termica e sicurezza fisica rimangono aperte.

**Prossima V7.5:** progettazione dei clock/bridge con MPN e pinout verificati, alimentazioni e PD hardwired, filtri fisici e ottimizzazione DSP. **NO FAB / NO TX.**
