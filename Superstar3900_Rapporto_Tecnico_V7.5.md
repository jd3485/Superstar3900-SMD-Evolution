# Superstar 3900 SMD Evolution — RAPPORTO TECNICO V7.5

**10 novembre 2026 · REVISIONE PROGETTUALE SOFTWARE / CANDIDATI DNP · NO FAB / NO TX.**

## Moduli realizzati

**Clock da riferimento comune:** modello integer-only da 30,72 MHz con divisori /8 e /640, generando nominalmente 3,84MHz per DAC900 e 48kHz audio nel medesimo dominio, rapporto esatto 80:1. Oscillatore candidato Abracon ASDMB-30.720MHZ-LY (DigiKey MPN 30,72MHz CMOS, opzione ±10ppm), pin fisici verificati da disegno Abracon: 1 STANDBY active-low, 2 GND, 3 OUT, 4 VDD. L'uscita non è fisicamente presente, i pin non sono instradati e il componente rimane DNP. Startup fino a 3ms da datasheet; guard di progetto numerico predefinito di 92.160 periodi master, senza abilitare alcun PD reale.

**Ponte dati programmabile candidato:** Lattice iCE40UP5K-SG48I, QFN48 (48 pin), 5280 LUT, core nominale 1,2V e domini I/O ulteriori da datasheet FPGA-DS-02008-2.4, **DNP**, senza assegnazioni di pin, PCB, sintesi, placement/timing, bitstream o alimentazione. La famiglia presenta weak pull-up sui pin prima della configurazione: non considerare la logica FPGA come un interblocco indipendente. Il DAC900 PD è active-high con pulldown interno e l'oscillatore ASDMB STANDBY aperto è ON: fail-safe fisico NON progettato né provato.

**DSP alternativo:** interpolatore causale multistadio a 16 tap/fase (48k×5→240k×4→960k×4→3,84MHz), conservazione storia fra blocchi e ingresso complesso. Prodotti di coefficienti teorici FIR **80,64 milioni/s**, sommati ai 6,144 milioni/s del Hilbert V7.3 danno **86,784 milioni/s**, rispetto ai 129,024 milioni/s della soluzione diretta V7.3 (**−32,74%**). È calcolo di budget, NON benchmark DSP reale, potenza, occupazione SRAM o prestazione spettrale equivalente.

**Nuova distinta:** 8 componenti DNP, 12 terminali pin-to-net DNP per solo oscillatore 4-pin e quattro resistori 2-pin generici; niente pin dell'FPGA inventati. R7603 lascia OUT oscillatore verso ingresso FPGA aperto e R7604 è un confine concettuale, NON un ponte reale unico per le 10 linee DAC. R7601/R7602 safety pull resistors proposti, anch'essi DNP. RF, LO TX, mixer, PA e antenna non instradati, vincoli DNP V7.1–V7.4 invariati.

## Esecuzioni software effettive GitHub Actions

| Gruppo | Esito | Interpretazione |
|---|---|---|
| Nuovi test V7.5 | **22 PASS / 0 FAIL / 0 SKIP** | Divisori, eventi senza drift relativo, startup guard, tolleranze, fault inibiti, FIR a blocchi e spot-check spettrale |
| Regressioni V7.4 | **21 PASS / 0 FAIL / 0 SKIP** | DAC virtuale FIFO, corrente/terminazioni DNP |
| Regressioni V7.3 | **15 PASS / 0 FAIL / 0 SKIP** | Hilbert causale, CW/AM/FM, filtro matematico |
| Regressioni V7.2 | **11 PASS / 0 FAIL / 0 SKIP** | IF2 DUC offline e piano 270 |
| Regressioni V7.1 | **8 PASS / 0 FAIL / 0 SKIP** | Modelli IF e all-DNP |
| **Totale** | **77 PASS / 0 FAIL / 0 SKIP** | [GitHub Actions run 42810193536](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42810193536), job 129809378021, **log verificato**; non misura hardware |
| Matrice di consenso V7.5 | **256/256** permesso TX=False | Analisi combinatoria software, non fault injection elettronica |
| Piano storico V6.4 | **270/270** posizioni; 30 ALFA; flag TX=0 | Controllo CSV, non synthesizer LO o RX PCB |

### Spot-check numerico spettrale nuovo FIR

Un **singolo tono 750Hz** a 48kHz, ingresso ampiezza 0,4, finestre periodiche coerenti di 8ms **dopo il transitorio** e campioni matematici a 3,84Msps forniscono ampiezza desiderata **0,3999996**. Componenti immagini digitali nel modello in doppia precisione, relativamente al tono desiderato:
- 47.250Hz **−114,0dB**, 48.750Hz **−114,3dB**;
- 239.250Hz **−140,9dB**, 240.750Hz **−140,9dB**;
- 959.250Hz **−164,9dB**, 960.750Hz **−164,9dB**.

Questi valori **non** sono livelli dBc misurati in RF, non rappresentano rumore di quantizzazione 10-bit, DAC sample/hold, F7401, phase noise, transitori audio, 2-tone IMD, SFDR o uno spettro hardware. Il test automatizzato usa limiti numerici molto più conservativi (−60/−75/−90 dB), non una maschera normativa. La V7.3 non è sostituita da una catena IF2 operativa.

## Gate e rischi aperti

1. Oscillatore ASDMB può essere ON se pin1 STANDBY è aperto. DAC900 può essere ON se PD pin15 è aperto (pulldown interno). Anche il reset weak-pullup FPGA è incompatibile con dichiarare sicurezza in assenza di hardware: servono supervisor indipendente, interlock fisico, sequenze rail, analisi stuck-at, fail-open e power backfeed.
2. Startup 3ms nel datasheet: i 92.160 tick in modello non provano che il clock fosse stabilizzato o che supervisor/FPGA avessero terminato configurazione. GPIO, rail 1,2/3,3 e memorie/PLL non assegnati a pin o registri. Il rapporto /8 /640 non sincronizza automaticamente TCXO e LO V6.x.
3. FPGA Lattice è candidato *catalogo*, non design pin-to-pin: pinmap 48 fisici, VCC/VCCPLL/VPP/IO domains e SRF/PCB/bitstream ancora da qualificare. Memoria 81.920B per batch 512 input, throughput 7,68MB/s e timing DMA/MCU **NON misurati**.
4. La riduzione 32,74% è solo confronto del numero di prodotti di coefficienti. Interpolazione su numeri complessi e filtri a diversa risposta; non garantisce realtime STM32G474 o risparmio energetico. Verificare output IF2, quantizzazione, spettro su audio a più toni/transienti e immagini analogiche nelle revisioni successive.
5. Restano filtri analogici senza MPN/Q/SRF/simulazione vendor, alimentazioni e termica, PLL/LO, immagini RX, interblocchi V6.2, schema KiCad/ERC/DRC e conformità.

**NON ESEGUITI**: simulazione RTL/FPGA, bench oscillatore/divisori, firmware STM32, circuito POR/PD, netlist elettrica completa, KiCad/ERC/DRC, SPICE/EM, PCB, EMC, radio in TX, fabbricazione e collaudo fisico.

## Tracciabilità

- Specifica: 01_Specifiche/V7.5/ARCHITETTURA_CLOCK_UNICO_DSP_V7.5.md
- ECO: 00_Gestione_Progetto/ECO_INTEGRAZIONE_V7.5.md
- Modello clock/interlock: 08_Firmware_Prototipi/V7.5/clock_pd_offline_v75.py
- Modello FIR: 08_Firmware_Prototipi/V7.5/interpolatore_multistadio_offline_v75.py
- Spettri: 03_Verifiche/V7.5/analizza_immagini_multistadio_v75.py
- Test CI: 03_Verifiche/V7.5/test_clock_dsp_v75.py
- BOM / netlist: 07_Componenti/BOM_CLOCK_BRIDGE_V7.5.csv e 01_Specifiche/V7.5/NETLIST_CLOCK_GUARDS_V7.5.csv
- Vendor: https://abracon.com/Oscillators/ASDMB.pdf ; https://abracon.com/Support/PackageDrawing/Oscillators/ASDMB.pdf ; https://www.digikey.com/en/products/detail/abracon-llc/ASDMB-30-720MHZ-LY/28009074 ; https://www.latticesemi.com/api/document/download?id=51968 .

**Verdetto: V7.5 è un avanzamento progettuale SOFTWARE validato nei test dichiarati, integrabile come candidata in main. NON autorizzata alla fabbricazione né a qualsiasi trasmissione RF.**

**Prossima V7.6:** pin fisici FPGA e piano di clock/reset/PD indipendente, RTL di prova su simulatore, prova spettrale sul nuovo path multistadio per multi-tone e transitori, dimensionamento filtro e power senza accendere TX.
