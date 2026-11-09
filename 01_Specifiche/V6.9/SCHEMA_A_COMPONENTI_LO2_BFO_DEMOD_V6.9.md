# V6.9 — Schema a componenti candidato LO2/BFO/demod (RX ONLY)

## 1. Generazione oscillatori
- U971 = **SI5351C-B-GM**, 20-QFN 4×4mm, 8 output CLK0..CLK7. **Non** usare il footprint/pinout della variante a 16 pin. Il pinout completo è nel CSV: CLKIN pin6; SCL4, SDA5; OEB7, INTR3; CLK0 pin13 e CLK1 pin12; VDD pin20; output banks VDDOA11 VDDOB10 VDDOC18 VDDOD14; pad centrale massa. Pin XA1/XB2 senza cristallo nel piano CLKIN, gestione PCB da convalidare.
- U971 su **3V3_LO2** candidata: 4 × 100nF più 4.7µF; consumo e capacità alimentatore della V6.3 ancora da qualificare. R971 10k pullup di OEB: power-up **output disabled**; transistor Q971 2N7002 lo può tirare basso solo con `LO2_EN_HARDWARE_GRANTED`, che **non è ancora una rete HW completa**. R972 100k a massa del gate, R977 1k in serie. **Mai collegare OEB permanentemente a massa.**
- CLKIN riceve 12.8MHz da `B972` buffer/fanout **da scegliere**. Uso condiviso con LMX2572 V6.4; ampiezza segnale e fase/ripple da convalidare.
- Target **PLLA = PLLB = 800MHz** ricavati da 12.8MHz * 62.5 (nominale, rapporto frazionario); output CLK0 = LO2 a 10.2385/10.2400/10.2415MHz, divider R=1; CLK1 = BFO a 453.5/456.5/455.7kHz, divider R=16. Modello razionale riproducibile in `08_Firmware_Prototipi/V6.9/lo2_bfo_planner_v69.py`. **Non è un file registri Si5351 pronto da inviare su I²C**. Restano le impostazioni PLL reset, source-select register, phase/noise optimization, disable masks, output drive, lock/readback, address e sequenza I²C.
- Driver LO2 a +7dBm **B971 UNSELECTED**: non si può presumere che l'uscita CMOS di U971 soddisfi il requisito LO del mixer ADE-1+. Nodo `LO2_RF_7DBM_PENDING` è interfaccia **non pilotata** finché il driver non viene realizzato. Spur, armoniche, matching, carico, jitter da misurare.
- MCU V6.1: PC12 e PB11 candidati ECO (non ancora impegnati nello storico), bus PB6/PB7 I²C condiviso; non modificare vecchia mappa pin senza revisione. Necessario calcolo completo dei pullup del bus prima PCB.

## 2. Demodulatore SSB/CW di studio
- U981 TS5A3157DBVR SOT23-6; pin: 1 NO=IF2 inverso, 2 GND, 3 NC=IF2 diretto, 4 COM=uscita commutata, 5 +3.3V, 6 IN=BFO CMOS. `B981` buffer/inverter da scegliere deve produrre le due fasi con **offset 1.65V** e ampiezza interamente nell'intervallo 0–3.3 V (limite switch). L'IF2 da filtro non va collegata direttamente a U981 senza matching e bias.
- R981/C982 + R982/C983 due sezioni RC candidate (6.8kΩ/4.7nF, ogni sezione ideale f≈4.98kHz); carico reciproco, attenuazione, fase e livello audio reali DA SIMULARE. C984 + R983 uscita AC per multiplexer V6.0. Il prodotto sincrono con BFO a 456.5k USB / 453.5k LSB ricostruisce il tono baseband nel **modello matematico**. CW BFO 455.7k produce battimento di 700Hz.

## 3. AM e FM
- AM: D991 Schottky **senza MPN/footprint**, R991 10k/C991 4.7n envelope, C992 blocco DC e R992 riferimento. Non qualificata sensibilità per segnali deboli, non selezionato il buffer dalla 455k filtrata al rivelatore.
- FM: `B991` limiter + `B992` discriminatore in quadratura **non scelti**, filtro audio R993/C993 6.8k/4.7n, C994 + R994 per AC out. Il modello simula la quadratura usando un ritardo ideale di un quarto di periodo; **nessuna rete LC hardware 90° già approvata**.
- SSB F823 e CW F824 da V6.8 restano SENZA MPN. Le reti AM/FM/SSB/CW non hanno ancora convalida d'isolamento e impedenza verso il selettore.

## 4. Fail-closed e stato progetto
- Configurare in ordine: power good e RX hard switch, verificare reference, disabilitare clock, programmare entrambi PLL/output con clock bloccati, controllare status, selettore filtro pronto, sbloccare solo in RX, poi rimuovere mute audio. Durante retune/fault/PA/PTT scollegare audio e riportare OEB alto. Attenzione: `LO2_EN_HARDWARE_GRANTED` è solo un **contratto verso un circuito HW da realizzare**, non sicurezza già dimostrata.
- **NO FAB / NO TX.** ERC, DRC, simulazione SPICE valida e misure su PCB **non eseguiti**.

## Fonti
- Si5351C 20-QFN: https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/data-sheets/Si5351-B.pdf
- TS5A3157: https://www.ti.com/product/TS5A3157
- AN619 (frazioni e registri): https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/application-notes/AN619.pdf
