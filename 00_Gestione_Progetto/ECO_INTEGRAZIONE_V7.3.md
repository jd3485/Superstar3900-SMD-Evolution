# ECO integrazione V7.3 — DAC900 candidato e IF2 causale (10 novembre 2026)

**Overlay senza riscrivere V7.2/V7.1.** Il tag v7.0 e i precedenti commit restano la storia. Versione corrente dopo merge su `main` (non equivale a validazione hardware).

1. `CausalIF2` sostituisce la sola *ipotesi algoritmica* di Hilbert circolare con FIR causale stateful Blackman 257tap, interpolatore stateful 32tap e NCO con fase persistente, non sostituisce `duc_if2_offline_v72.py` che resta disponibile come riferimento periodico.
2. Nuovo **U7401 DAC900E TI TSSOP28 (DNP)**, 28 pin fisici da datasheet, rail e clock mai forniti. PD pin15 è **active-high con pulldown interno**, quindi un mero collegamento al GPIO non garantisce OFF: R7401 10k pull-up (DNP nello studio) rappresenta una futura guardia da verificare con power sequencing, rampa e guasti. U7401 IOUT pin22 e IOUTB pin21 rimangono NON INSTRADATI. Non collegare 50Ω senza rete I/V.
3. U7402 FPGA/bridge, X7401 3.84MHz e F7401 LC 850kHz 7 poli **senza MPN, footprint, clock o schemi fisici**. BOM V7.3: 12 righe DNP, netlist: 42 terminali concettuali DNP; 28 pin reali verificati sono *solo* quelli del DAC900.
4. Modello filtro ABCD 50Ω 7 poli con Q finite, L/C teorici, MC400; non reinterpretare le attenuazioni ideali come prestazioni di F7401 montato. SRF induzioni ~17µH, matching, layout, tolleranze reali sono bloccanti.
5. STM32G474 MCU V6.1 conserva tutto il pinmapping precedente: **non assegnare 10 linee dati + CLK a pin liberi arbitrari**. La banda grezza 38.4Mbit/s e ~129MMAC/s di DSP naïve dimostrano che occorre architettura digitale dedicata o ottimizzata, non solo una modifica software banale.
6. `U7201/U7202/R7201..R7205` V7.1, `U7301/R7301..R7303` V7.2 e tutto V7.3 **DNP**; RClamp e interblocchi precedenti invariati. TX_ENABLE_HARD V6.2 non validato, nessuna PA/antenna connessa.
7. Documentare PASS/FAIL/NON ESEGUITO separatamente. Ogni transizione verso circuiti fisici richiederà fornitori, firmware reale, PCB e verifica hardware/normativa indipendente: **NO FAB / NO TX**.
