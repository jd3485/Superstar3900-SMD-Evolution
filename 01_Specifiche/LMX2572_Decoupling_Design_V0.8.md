# LMX2572 V0.8: schema decoupling e power

**Stato:** BOZZA. Il riferimento EVM SNAU217B non e una prova di correttezza del nostro layout.

## VCC (6 ingressi separati)

|Pin|Nome|R-series|C to GND|Net locale|
|---|---|---|---|---|
|7|PLL_VCCDIG|R10 0R|C10 1uF|PLL_VCCDIG|
|11|PLL_VCCCP|R11 0R|C11 1uF|PLL_VCCCP|
|15|PLL_VCCMASH|R12 0R|C12 1uF|PLL_VCCMASH|
|21|PLL_VCCBUF|R13 0R|C13 1uF|PLL_VCCBUF|
|26|PLL_VCCVCO2|R14 0R|C14 1uF|PLL_VCCVCO2|
|37|PLL_VCCVCO|R15 0R|C15 1uF|PLL_VCCVCO|


Ingresso della rete: 3V3_PLL_INPUT_FROM_LDO, **non generato** nel presente schema.
TI propone alimentazione 3.0-3.5V per il chip; la EVM lavora a 3.3V.
Noi dobbiamo scegliere LDO, protezione e filtri propri, verificare irradiazioni e disturbi.

## Nodi di bias / regolatore

|Pin|Net|Ref|Valore preliminare|Fonte|
|---|---|---|---|---|
|3|PLL_VBIASVCO|C20|100n|TI C19|
|10|PLL_VREGIN|C21|1u|TI C28|
|27|PLL_VBIASVCO2|C22|470n|TI C25|
|29|PLL_VREFVCO2|C23|10u|TI C20|
|33|PLL_VBIASVARAC|C24|10u|TI C21|
|36|PLL_VREFVCO|C25|10u|TI C22|
|38|PLL_VREGVCO|C26|10n|TI C24|


Il pin 3 usa **100nF** e il pin 27 usa **470nF** (non invertire).
I nodi Vreg/Vref/Vbias non sono ingressi diretti di alimentazione: collegarli al solo rispettivo condensatore, salvo richieste datasheet.

## Prossimi gate obbligatori
1. Aprire in KiCad e validare sia simbologia sia footprint esatto RHA (DAP incluso).
2. Esportare netlist ed eseguire ERC; correggere qualunque warning ingiustificato.
3. Selezionare componenti reali con tensione nominale e capacita residua sotto DC bias.
4. Definire LDO 3.3V, TCXO 12.8MHz, reti AC coupling, SPI, CE/RESET, RF A/B.
5. Confrontare con TI TICS Pro / PLLatinum Sim per i 270 canali.
6. Completare layout e laboratorio prima di approvare una PCB.

Fonti: https://www.ti.com/lit/ug/snau217b/snau217b.pdf (Figura 19),
https://www.ti.com/product/LMX2572 e https://www.ti.com/lit/ds/symlink/lmx2572.pdf .
