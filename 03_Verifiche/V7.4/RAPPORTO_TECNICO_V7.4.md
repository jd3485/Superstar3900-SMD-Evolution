# Superstar 3900 SMD Evolution — RAPPORTO TECNICO V7.4

**10 novembre 2026 — contratto digitale DAC900 e studio corrente/tensione — NO FAB / NO TX.**
Revisione candidata incrementale della V7.3. Storico preservato; nessuna alimentazione DAC fisica, nessun segnale GPIO, nessun collegamento RF, mixer o finale, nessun PCB.

## Moduli nuovi

**1. Modello digitale offline** — 08_Firmware_Prototipi/V7.4/dac900_bridge_offline_v74.py. FIFO virtuale di 1024 codici DAC 10 bit, campioni 3.84MSa/s e rapporto 80:1 con audio a 48kHz. Dati acquisiti idealmente sul fronte ascendente, aggiornamento uscita ipotetico sul discendente. Margini studio di 20ns prima e dopo il fronte (scelta progettuale, non requisito TI garantito). Fault latched su mancanza clock/supply, overflow, underflow, parola invalida o errore di timing. Il modello genera soltanto dizionari di traccia in RAM. Nessun driver DAC900/STM32/FPGA.

**2. Conversione corrente/tensione semplificata** — DAC900E TI pin22 IOUT; corrente IFS×code/1024 secondo TI SBAS093B Fig.6. Shunt 49.9Ω + terminazione 49.9Ω in parallelo (circa 24.95Ω), candidato Vishay CRCW060349R9FKEA 0603 ±1%. IFS nominale 20mA e code1023 danno circa **0.4985V**, **4.98mW** per ramo resistivo, angoli di tolleranza 1% **~0.4935–0.5035V**. È soltanto un equivalente DC: nessun dato di distorsione, spettri o filtro fisico. I due resistori e isolatori sono **DNP**.

**3. Contratti e risorse:** bus 10bit parallelo **38.4Mbit/s** grezzi; packed 16 bit **7.68MB/s**; 512 campioni audio generano **40.960** parole IF2, equivalenti a **81.920 byte**. FIFO 1024 = 266.67µs nominali. Due clock indipendenti divergenti 50ppm producono **192 parole/s** di drift, saturazione di 1024 parole in 5.33s se non corretti. U7501 bridge e X7501 clock rimangono TBD/DNP, senza allocazione registri STM32.

**4. BOM e netlist** — 07_Componenti/BOM_DAC_BRIDGE_IV_V7.4.csv (**7 voci tutte DNP**), 01_Specifiche/V7.4/NETLIST_CONTRATTI_DNP_V7.4.csv (**8 righe terminali tutte DNP**). R7503 0ohm non montato mantiene interrotto IOUT→F7401, senza uscita verso U7201 o PA. IOUTB/filtri/PD e domini di alimentazione non progettati fisicamente; non inventare pin per bridge o oscillatore.

Fonte vendor originale DAC900: https://www.ti.com/lit/ds/symlink/dac900.pdf (Rev.B, pin p.4, timing p.5, I/V Fig.6 p.14, PD p.15). Resistore catalogo: https://www.digikey.com/en/products/detail/vishay-dale/CRCW060349R9FKEA/1174519 .

## Verifiche effettivamente eseguite su GitHub

| Gruppo | Risultato | Limite |
|---|---|---|
| Nuovi V7.4 | **21 PASS, 0 FAIL, 0 SKIP** | Solo modelli, controlli logici e file |
| Regressione V7.3 | **15 PASS, 0 FAIL, 0 SKIP** | DSP causale e filtro matematico |
| Regressione V7.2 | **11 PASS, 0 FAIL, 0 SKIP** | DUC offline e filtro ideale |
| Regressione V7.1 | **8 PASS, 0 FAIL, 0 SKIP** | Piano IF/RF e storico DNP |
| **Totale CI** | **55 PASS / 0 FAIL / 0 SKIP** | GitHub Actions [run 42806194163](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42806194163), job 129795819928, log esaminato |
| Consensi TX | **512/512 = False**, fault latched sulla macchina virtuale | Non equivale a un interblocco PD/PA reale |
| Piano frequenze | **270/270** posizioni, **30 ALFA**, TX storico 0 | Solo coerenza CSV |
| Corrente, terminazioni, tolleranze e risorse FIFO | **PASS in software** | Non misure né SPICE vendor |
| KiCad nativo, ERC/DRC, SPICE/IBIS, EMC, misure DAC/RF, PCB, termica, collaudi e trasmissione | **NON ESEGUITI** | Nessuna dichiarazione di conformità o fabbricabilità |

I dettagli macchina sono in 03_Verifiche/V7.4/RISULTATI_VERIFICHE_V7.4.json e il contratto in 01_Specifiche/V7.4/ARCHITETTURA_DAC_CLOCK_IV_V7.4.md.

## Blocchi tecnici irrisolti

1. **DAC900 PD pin15 è active HIGH con pulldown interno**: lasciarlo floating mette il componente in normale funzionamento. La variabile di modello PD assertito non rende l'hardware sicuro. Pull-up R7401 V7.3 rimane DNP e mancano analisi di guasto hardware e di alimentazione indipendente. Nessuna emissione RF permessa.
2. Rete 49.9Ω locale/remota segue una configurazione TI per singola uscita e cavo terminato, **non** valida automaticamente il filtro F7401 come due porte 50Ω sul reale DAC current-output (IOUTB, capacità parassita e ritorni non definiti).
3. Il clock 3.84MHz non ha oscillatore/PLL/FPGA/clock tree reali; setup 1.5ns e hold 1ns sono documentati come tipici, NON garantiscono margini del nostro bus. DUT/DAC non alimentati.
4. V7.3 DSP naïve ~129.024MMAC/s non ha prove su STM32G474; non selezionato bridge, firmware o memoria. VA/VD da 2.7 a 5.5V ammesse da TI, alimentazione proposta 3.3V non progettata né misurata. TI power 170mW tipico a 5V e condizioni di test differenti, non attribuibile a questa ipotesi.
5. F7201/F7202/F7301/F7401 non qualificati; RX immagine, LO/PLL/termica e interblocchi V6.2 ancora aperti.

## Decisione e sviluppo successivo

**V7.4 pronta come sola revisione progettuale candidata su main**, non per fabbricazione/trasmissione. Prossima **V7.5**: clock sincronizzato e ponte digitale con MPN e pinout verificati, rete IOUT/IOUTB con filtro implementabile e SRF/Q vendor, alimentazioni/PD indipendente, efficienza DSP multistadio, regressioni. **NO FAB / NO TX.**
