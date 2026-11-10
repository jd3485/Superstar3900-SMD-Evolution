# V7.4 — bus DAC900, clock e I/V: contratto software e candidati DNP

**10 novembre 2026 — NO FAB / NO TX.** Overlay dalla V7.3. Non esistono circuito alimentato, KiCad nativo, cablaggi né DAC funzionante: sono un modello Python, BOM e netlist concettuale. I mixer e ponti TX V7.1-V7.3 restano DNP e senza uscita RF instradata.

## 1. Contratto digitale

Fonte primaria TI DAC900E, 10 bit paralleli, TSSOP-28, datasheet SBAS093B Rev.B, https://www.ti.com/lit/ds/symlink/dac900.pdf : pagina stampata 4 (pin), 5 (temporizzazioni), 14 (Fig.6 carico), 15 (PD). D9..D0 sono pin fisici 1..10, CLK pin28, PD pin15 attivo ALTO. La fonte indica i dati acquisiti sul fronte di salita del clock, mentre l'uscita cambia al fronte di discesa. Nella tabella timing sono illustrati 1.5ns di setup e 1ns hold come valori **tipici**, non garanzie worst-case PVT.

- Rapporto audio/IF2 matematico 48.000 Sa/s × 80 = 3.840.000 Sa/s. Periodo DAC 260,4167ns, semiperiodo 130,2083ns a duty del 50%.
- Modello di trasporto: porta parallela 10 bit = 38,4Mbit/s grezzi; parole di memoria 16 bit = 7,68MB/s; 512 campioni audio → 40.960 codici IF2 → 81.920 byte senza doppio buffering. Non equivale a una configurazione reale STM32/FPGA.
- Contratto di temporizzazione **assunto**: dati validi da almeno 20ns prima a 20ns dopo il fronte di salita, con cambi sul semiperiodo precedente/successivo. È una scelta di studio conservativa e NON una misura o un requisito TI garantito.
- Modello OfflineParallelBridge: FIFO virtuale 1.024 codici (266,67 microsecondi nominali se piena), registra solo parole e tempi di fronti ipotetici. Un errore CLOCK_MISSING, POWER_NOT_GOOD, DATA_TIMING_NOT_MET, FIFO_UNDERFLOW, FIFO_OVERFLOW o INVALID_CODE blocca irreversibilmente l'istanza nello stato FAULT e svuota la coda. Nessuna azione GPIO o DAC.
- Sincronizzazione clock **non progettata fisicamente**: ratio 80:1 deve discendere da una sorgente comune. Con due clock indipendenti distanti 50ppm il modello calcola 192 campioni/s di drift; 1.024 parole rappresentano solo ~5,33 secondi di drift prima della saturazione. X7501 oscillatore e U7501 bridge sono TBD/DNP senza pinout, jitter, PLL o bench.
- Gate incondizionato tx_permission=False; PD_PHYSICALLY_RELEASED=False e altre costanti False sono SOLTANTO proprietà del modello. PD pin15 del DAC900 dispone di PULLDOWN interno e, se lasciato libero, porta il DAC in NORMALE funzionamento; il pull-up R7401 V7.3 è un'ipotesi DNP di sicurezza, non un interblocco reale. Occorre protezione indipendente, sequenza rail, analisi guasti, isolamento fisico e verifica hardware.

## 2. Conversione di corrente in tensione: figura 6 TI (non PCB)

TI documenta DAC900 single-ended con shunt 50 ohm locale e terminazione remota 50 ohm, equivalenti circa 25 ohm in parallelo: I_FS 20mA produce esempio 0..0,5V. Nel modello V7.4 i due resistori sono **49,9Ω ±1% Vishay CRCW060349R9FKEA** (R7501 shunt e R7502 terminazione); dettaglio distributore https://www.digikey.com/en/products/detail/vishay-dale/CRCW060349R9FKEA/1174519. Entrambi DNP e non collegati, non acquistati.

- Dato TI: IOUT = I_FS × code / 1024 (code 0..1023), IOUTB = I_FS × (1023 − code) / 1024. R_eq = 49,9 || 49,9 = 24,95 ohm, Vout teorica al codice 1023 ≈ **0,4985V** con I_FS nominale 20mA. Power teorica ~**4,98mW** per resistore al massimo codice.
- Semplici angoli di tolleranza ±1% su entrambi i valori danno Vout teorica ~0,4935–0,5035V, prima di errori del DAC e dell'alimentazione. La conformità d'uscita TI −1,0..+1,25V risulta rispettata **in questo solo equivalente DC**. La potenza è inferiore al rating catalogo 0,125W in questo modello; non prova AC, linearità, mismatch, layout o temperatura.
- R7503 zero ohm **DNP** resta separatore fra DAC IOUT pin22 e filtro F7401 V7.3. R7504 IOUTB è un candidato **non simulato come percorso completo**. F7401 è un modello a 7 poli per DUE porte 50Ω, non un filtro vendor collegabile direttamente a una corrente senza valutare la terminazione, la topologia, il ritorno a massa, SRF/Q e gli effetti della capacità d'uscita del DAC.
- La figura 6 TI è un esempio di conversione SINGLE-ENDED con cavo doppiamente terminato. Non equivale al nostro RF system né alla validazione della F7401. Non c'è uscita elettrica verso mixer, PA o antenna.

## 3. Alimentazioni e fattibilità

TI consente VA e VD da 2,7 a 5,5V. Ipotesi di progetto: 3,3V, ma nessun rail è instradato. Per VD=3V il datasheet elenca VIH>=2V e VIL<=0,8V; non sono prove di edge/skew sul nostro bus. TI documenta un punto di prova +5V e 50MSPS, I_FS=20mA, con potenza 170mW tipica e 230mW massima: NON trasferire quei numeri come misure a 3,3V/3,84MSPS. Servono alimentatore, riferimento, clock source, analisi termica, bypass, ESD, PD, EMI e footprint verificati.

Budget V7.3 DSP naïve 129,024MMAC/s per FIR Hilbert+interpolazione resta senza benchmark MCU; V7.4 aggiunge il contratto di trasferimento, NON una soluzione fisica STM32. U7501 bridge/FPGA è TBD e resta DNP.

## 4. File e gate

- Modello: 08_Firmware_Prototipi/V7.4/dac900_bridge_offline_v74.py.
- Suite: 03_Verifiche/V7.4/test_dac900_bridge_v74.py. Workflow: .github/workflows/dac_bridge_v74_offline.yml con regressioni V7.1-V7.3.
- Distinta: 07_Componenti/BOM_DAC_BRIDGE_IV_V7.4.csv: **7 DNP**. Netlist terminali generici: 01_Specifiche/V7.4/NETLIST_CONTRATTI_DNP_V7.4.csv: **8 DNP**. Nessuna numerazione fittizia per U7501/X7501/J7501; pin reali DAC900 in V7.3.
- NON ESEGUITI: KiCad/ERC/DRC, datasheet PCB CAD completo, clock e bridge reali, DAC/PD alimentati, vendor SPICE/IBIS, misura spettro, filtro, alimentatore, termica, EMC, hardware, fabbricazione, TX RF.

## 5. Prossima V7.5

Scegliere una sorgente comune audio/DAC e bridge con MPN, profilare capacità MCU/FPGA e DUC multistadio, progettare stadio IOUTB/differenziale con selezione filtro e SRF/Q, definire alimentazioni e fail-closed indipendente su PD. **NO FAB / NO TX** fino a validazione esterna.
