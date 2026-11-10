# Superstar 3900 SMD Evolution — V7.5 CLOCK UNICO e DSP MULTISTADIO (SOLO STUDIO)

**10 novembre 2026. Baseline iniziale: main V7.4, commit 7cd7e217.** Intera catena TX R7201..R7205, U7201/2, U7301, U7401 e reti V7.1–V7.4 rimane NON montata (DNP). Uscita RF, PA e antenna non interconnessi. Non sono stati realizzati schemi KiCad/ERC/DRC o prototipi fisici. Questa revisione aggiunge modelli SOFTWARE e candidati acquistabili DA VERIFICARE nel contesto reale, NON una trasmittente.

## Problema risolto numericamente: clock audio e DAC coerenti

Scegliamo un riferimento candidato da **30.720.000 Hz**. Un contatore intero nello stesso dominio genera:
- **30.720.000 / 8 = 3.840.000 Hz** per il futuro DAC900E (periodo 260,4167 ns).
- **30.720.000 / 640 = 48.000 Hz** come confine/strobe di campionamento audio.
- Quindi **80 campioni DAC per ogni strobe audio**, senza due sorgenti indipendenti o FIFO drift relativo. Se l'unico oscillatore varia di +10ppm, audio varia di +0,48 Hz e DAC di +38,4 Hz ma il rapporto nominale 80 rimane esatto. Questo NON assicura sincronismo con RX, LO1/LO2 o fonti audio esterne e non dimostra jitter/PLL hardware.

**Oscillatore candidato:** Abracon **ASDMB-30.720MHZ-LY**, 30,72MHz CMOS 3,3V, 4-SMD, ±10ppm come opzione associata al MPN nel catalogo DigiKey:
https://www.digikey.com/en/products/detail/abracon-llc/ASDMB-30-720MHZ-LY/28009074 .
Datasheet famiglia Abracon https://abracon.com/Oscillators/ASDMB.pdf e disegno pin ufficiale https://abracon.com/Support/PackageDrawing/Oscillators/ASDMB.pdf :
pin 1 = STANDBY; pin 2 = GND; pin 3 = OUT; pin 4 = VDD. La famiglia documenta startup fino a **3,0ms** (tipico 1,5ms), e STANDBY **LOW = Hi-Z; HIGH o aperto = oscillazione abilitata**: il PIN FLOTTANTE NON È UNA PROTEZIONE. R7601 pull-down 10k soltanto proposto DNP; non è stato simulato fisicamente l'oscillatore né il pin standby. Pin3 non instradato e bridge non alimentato.

**Bridge candidate:** Lattice **iCE40UP5K-SG48I**, FPGA UltraPlus 48 QFN, 5.280 LUT, fino a 39 I/O generali per SG48, con blocchi SPRAM/EBR e core nominale 1,2V:
https://www.latticesemi.com/api/document/download?id=51968 (datasheet FPGA-DS-02008-2.4). Stato: U7601 DNP, **non esiste assegnazione dei 48 pad** e non esiste bitstream/verifica timing né un PHY di 10 bit verso il DAC900. Nella famiglia i pin I/O pre-configurazione sono in tri-state con weak pull-up: anche se in futuro si usa questo bridge, la sicurezza DAC PD deve essere indipendente dall'FPGA. I rail core/PLL 1,2V, I/O e programmazione VPP_2V5 dovranno essere qualificati e sequenziati; non unire arbitrariamente i rail.

**R7603 zero ohm DNP** interrompe il segnale oscillator OUT → FPGA input virtuale; **R7604 zero ohm DNP** è un simbolo di confine digitale astratto, **non** un'unica connessione reale di 10 linee. Nessun pin fisico FPGA è inventato nella netlist V7.5. C7601 bypass 10nF è soltanto candidato DNP, suggerito nel disegno package. R7602 10k pull-up PD DAC900 è ipotesi DNP: un output al DAC non è realizzato, PD resta non controllato fisicamente.

## Interblocchi e power-on: non implementati sul PCB

Il DAC900E pin15 PD è **attivo ALTO con pulldown interno**, che se lasciato libero lo ABILITEREBBE. L'oscillatore ASDMB pin1 STANDBY è **attivo BASSO**, che se lasciato libero lo accenderebbe. L'FPGA possiede pin debolmente pull-up durante la configurazione. Questo insieme crea potenziali condizioni di avviamento incompatibili con un interblocco garantito: NON basta un permesso software. Sono previsti soltanto modelli di rischio, mai uno stato fisico sicuro validato.

La macchina astratta StartupFaultPlanner richiede 8 condizioni (rail oscillatore/core FPGA/I/O FPGA/DAC, configurazione FPGA, clock, supervisor e dati FIFO) stabili per **92.160 cicli master** come default del modello (= 3,00ms al clock nominale, uguale al massimo startup riportato nel datasheet); i test brevi possono sovrascrivere tale durata per verificare solo la macchina di stato, senza costituire un contratto di accensione hardware; il raggiungimento del guard non modifica mai lo stato TX; DAC_PD elettronico non viene pilotato. Qualsiasi guasto, gap di clock o inject_fault causa FAULT bloccato senza rilascio software. Le 256 combinazioni delle condizioni devono mantenere tx_permission False. Per hardware reale servono POR/supervisor indipendente, ritardo durante il power-up (> startup specificata), optoisolamento o switch analogico fail-open, analisi stuck-low di PD e backfeed su DAC/FPGA, guasti comuni e controllo normativo. Niente di questo è implementato.

## Prototipo algoritmico: interpolazione a tre stadi

La V7.3 usa Hilbert 257tap e un interpolatore unico **80×, 32 tap/fase**; budget teorico dei prodotti di coefficienti circa 122,88M/s per interpolazione + 6,144M/s Hilbert = **129,024M/s**. Nuovo file:
08_Firmware_Prototipi/V7.5/interpolatore_multistadio_offline_v75.py

- **48kHz ×5 → 240kHz**, sinc/Blackman causale a **16 tap per fase**.
- **240kHz ×4 → 960kHz**, stesso tipo FIR.
- **960kHz ×4 → 3,84MHz**, stesso tipo FIR.
- Budget matematico 16×(0,24+0,96+3,84)MHz = **80,64M prodotti/s**, + Hilbert precedente **6,144M/s** = **86,784M prodotti/s**, riduzione stimata **32,74%** in prodotti scalari rispetto al modello precedente. Non è misura CPU, tempi di pipeline, costo FPGA DSP/IQ o riduzione di consumo. Il nuovo codice elabora vettori COMPLESSI in doppia precisione e non genera RF IF2 da solo.
- State/phase conservati fra blocchi; test controllano consistenza chunk vs intero, zero, DC, tono. **FIR nuovi NON equivalenti** in risposta alla V7.3, che resta il riferimento IF2 preesistente. Non utilizzare i dati spettrali V7.3 per garantire reiezione della V7.5. In particolare mancano spettro dei transitori, droop sui 300..2700Hz, reiezione immagini 48k/240k/960k, misura in codice 10bit, confronto Hilbert e tempi reali.

## Budget dati e memoria

Per 512 campioni audio: 512×80 = 40.960 parole DAC; 16 bit packed → **81.920 byte** solo dati; non contati doppi buffer e risultati intermedi. Lattice iCE40UP5K dispone di blocchi di memoria interni, ma il loro controller, le porte simultanee, la velocità e l'allocazione devono essere verificati. Non si afferma che l'intero progetto stia in FPGA o STM32G474.

## Evidenze e tracciabilità
- Modelli: 08_Firmware_Prototipi/V7.5/clock_pd_offline_v75.py e interpolatore_multistadio_offline_v75.py
- Verifiche: 03_Verifiche/V7.5/test_clock_dsp_v75.py, workflow .github/workflows/v75_clock_dsp_offline.yml
- Distinta: 07_Componenti/BOM_CLOCK_BRIDGE_V7.5.csv, **8 righe tutte DNP**. Netlist parziale 01_Specifiche/V7.5/NETLIST_CLOCK_GUARDS_V7.5.csv, **12 terminali DNP**: 4 del solo oscillatore ASDMB realmente documentati e 8 di quattro resistori generici. Non inventare pin dell'iCE40.
- Rapporto: 03_Verifiche/V7.5/RAPPORTO_TECNICO_V7.5.md. ECO: 00_Gestione_Progetto/ECO_INTEGRAZIONE_V7.5.md.

**NON ESEGUITI:** selezione footprint FPGA pad-level, schema KiCad, clock HDL e time-closure, PD hardwired, alimentazioni, SPICE/EMC, termica, test DAC/RF, calibrazione VCO/LO, laboratorio, produzione e trasmissione. **NO FAB / NO TX.**

## Prossima V7.6
Una volta qualificata la V7.5 come studio documentale/software, completare su carta e con simulazioni una vera pianificazione FPGA: allocazione pin, vincoli timing, driver DAC a 10 bit, memoria/streaming, progettazione indipendente POR+PD+isolamento RF; filtro di ricostruzione con componenti a SRF/Q documentati, misure spettrali offline del nuovo FIR multistadio. Solo allora valutare dettagli hardware, senza MAI interpretare il merge in main come autorizzazione a fabbricare o trasmettere.
