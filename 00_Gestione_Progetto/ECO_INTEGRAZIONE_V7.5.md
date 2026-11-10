# ECO V7.5 — clock unico e interpolazione DSP multistadio (NO FAB / NO TX)

**10 novembre 2026.** Continuazione incrementale da V7.4, senza riscrivere V7.0–V7.4, senza progetti KiCad TX né componenti montati.

1. **Clock candidato fisico non assemblato:** X7601 Abracon ASDMB-30.720MHZ-LY CMOS 30,72MHz 4-pad, pin1 STANDBY low→Hi-Z, pin2 GND, pin3 OUT, pin4 VDD, vendor drawing Abracon. Nella distinta è **DNP**: non esiste uscita 30,72MHz cablata. R7601 pull-down standby DNP non garantisce spegnimento in caso di guasto.
2. **Bridge candidato non assemblato:** U7601 Lattice iCE40UP5K-SG48I QFN48, datasheet FPGA-DS-02008-2.4, 1,2V core e domini I/O aggiuntivi; **NESSUN pin FPGA assegnato**, nessun bitstream, nessun vincolo timing, né fusione arbitraria con pin STM32G474. R7603 DNP isola il clock, R7604 DNP è un confine digitale soltanto CONCETTUALE, non ponticella 10 vere linee.
3. **Clock share matematico:** 30.720.000 /8 = 3.840.000 e /640 = 48.000; rapporto 80 esatto se derivati dallo stesso master. Variazioni ppm comuni cambiano frequenze assolute ma non il rapporto in interi; nessun clock RF/LO o audio esterno sincronizzato implicitamente.
4. **Interblocchi non fisici:** DAC900 PD pin15 active-high con pulldown interno tende a ON se flottante; oscillatore STANDBY tende a ON se aperto. Il modello propone R7602 pull-up PD DNP; NON attribuire a FPGA, firmware o modello bool una garanzia. Startup guard software predefinito 92.160 cicli (3ms), power-on supervisor e hardware independent inhibit non progettati.
5. **DSP multistadio candidato:** x5 @240kHz, x4 @960kHz, x4 @3,84MHz con 16tap/fase, stato FIR persistente. Budget prodotti di coefficienti teorici 80,64M/s interpolatore + 6,144M/s Hilbert preesistente = **86,784M/s**, contro **129,024M/s** V7.3 (riduzione aritmetica 32,74%). Spettri, immagini, overhead, quantizzazione e runtime STM32/FPGA da verificare; NON significa firma DSP TX pronta.
6. **Contratti DNP:** 8 voci BOM, 12 righe netlist parziale, tutte DNP; solo 4 pin dell'oscillatore realmente provenienti da tabella vendor, i 2-pin resistivi sono generici. Nessuna uscita RF, PA o antenna.
7. Test software V7.5 e regressioni V7.4/V7.3/V7.2/V7.1 vanno eseguiti e trascritti con PASS/FAIL/SKIP. Tutti i problemi RX immagine, LO/PLL, IF analogica, termica, interblocchi, clock, PCB, EMC e compatibilità normativa restano aperti. **NO FAB / NO TX**.

**V7.6:** pinout FPGA fisico/constraints/HDL di sola simulazione, verifiche spettrali multistadio, vero budget IRQ/DMA/MCU, progettazione supervisor indipendente e filtro analogico con MPN/Q/SRF.
