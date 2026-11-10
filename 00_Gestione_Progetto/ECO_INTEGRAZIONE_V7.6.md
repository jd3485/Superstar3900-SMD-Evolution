# ECO V7.6 — clock/FIFO RTL simulati, SG48 HOLD, transitori (NO FAB / NO TX)

**10 novembre 2026** — evoluzione dalla V7.5 preservandone tutti i file, la storia e il tag immutabile v7.0.

1. Aggiunto codice **Verilog puro di simulazione**: divisori di strobo 30,72MHz/8 e /640, FIFO virtuale 10bit×16, fault latched per underflow/overflow e supervisori solo simbolici. Le uscite RF permission, PD release e analog link sono sempre 0. Non esiste clock DAC elettrico, output I/O FPGA con top-level o programma hardware.
2. Aggiunto testbench Icarus Verilog che verifica 1280 tick master -> 160 DAC strobes + 2 audio strobes, ordine FIFO, latching dei fault, reset e flag costanti. Da eseguire sulla CI reale; mai dichiarare HDL synthesis/place-route se non eseguiti.
3. Nuovo SG48 **pin-plan candidato** 48 pin+pad GND con PCF HOLD, ricostruito da **fonte secondaria** del pinout e conteggi incrociati con il datasheet Lattice FPGA-DS-02008-2.4 (39 GPIO/17+14+8, pad massa). Il **foglio vendor ufficiale document_id=51971 non è stato confrontato**: PCB/pinout NON APPROVATI. Non interpretare il PCF come specifica funzionante: mancano top-level FPGA, rail, I/O bank timing e bitstream.
4. Sviluppato test di multitono coerente 750+1250Hz e transitorio a gradino 0→0,4→0 su FIR V7.5. Il gradino produce picco di campione ~0,45682 nel modello (+14,2% rispetto allo steady level); il dato motiva headroom/limiter prima di un eventuale DAC, non rappresenta una misura RF. Le immagini sono misure digitali offline in doppia precisione, non prova del filtro analogico.
5. Il datasheet primario Lattice impone sequenza VCC/VCCPLL → SPI_VCCIO1 → VPP_2V5 → VCCIO0/2; nessun regolatore, reset o supervisor indipendente progettato. DAC900 PD attivo HIGH con pulldown interno e ASDMB STANDBY attivo LOW sono rischi reali se lasciati flottanti. Il modello RTL NON risolve la condizione fisica.
6. Nuova BOM simulazione V7.6 **5 componenti tutti DNP** e netlist virtuale **8 terminali OPEN/DNP**. Nessuna modifica ai ponti R7701/R7702 (DNP), ai mixer U7201/U7202, DAC U7401, FPGA U7601 o percorso PA/antenna TX.
7. Integrare su main solo se Icarus bench, Python V7.6 e regressioni V7.1–V7.5 hanno esito PASS e indicare accuratamente il run. **NO FAB / NO TX** sempre, inclusa assenza di misure/PCB reali.

**Prossima V7.7:** pinout Lattice XLSX primario, top sintetizzabile e constraints verificati, clock/PD supervisor separato con simulazioni fault, analisi DAC e filtri con Q/SRF MPN e multitone/transienti dopo quantizzazione.
