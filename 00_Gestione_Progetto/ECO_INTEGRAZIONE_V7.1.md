# ECO V7.1 — TX/IF solo candidato, blocco fisico permanente

**Non modifica file V7.0 né le revisioni precedenti.** Il tag v7.0 resta la baseline immutabile, i commit di branch V7.1 formano il delta.

- **ECO-71-01:** V6.4 LO1 è definito per RX soltanto; calcolo TX usa la stessa relazione LO1=fRF+10.695MHz **solo su carta**. Nessun profilo LMX2572 TX né nuovo GPIO.
- **ECO-71-02:** U7201 e U7202 (ADE-1+) **DNP**, filtri F7201/F7202 **DNP** e senza MPN; R7201–R7205 **DNP**, con R7203 bypass IF1 proibito e R7205 uscita RF non instradata. Nessuna presa antenna o PA TX.
- **ECO-71-03:** Non collegare il LO2 V6.9/V7.0 allo stadio TX. Driver GALI-3+ a 10.24MHz e LO1 non qualificati nemmeno per la sola catena RX; budget TX +7dBm da dimostrare separatamente.
- **ECO-71-04:** Necessario generatore IF2 455kHz con modulazione AM/FM/SSB/CW e filtraggio. Il codec 48kHz non può emettere direttamente campioni reali a 455kHz. Il software V7.1 è **solo simulatore offline**.
- **ECO-71-05:** Inversione delle bande USB/LSB: LO alto in seconda conversione richiede IF2 USB a 455k-f_audio e IF2 LSB a 455k+f_audio. FM con segno deviazione invertito. Verifica le 270 frequenze come pura aritmetica; **TX_PERMITTED=FALSE** su tutte.
- **ECO-71-06:** Interblocchi V6.2 J801 DNI + FAULT_LOOP_OK ancora non implementato, commutatore antenna e finale assenti. Non trasformare alcuna richiesta firmware in TX enable.
- **GATE:** 0 prototipi TX, nessun ERC/DRC KiCad, ngspice, test RF/EMI, certificazione o DFM. **NO FAB / NO TX**.
