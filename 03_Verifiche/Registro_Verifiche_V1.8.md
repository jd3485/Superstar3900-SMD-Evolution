# Verifiche V1.8

PASS: algebra MCLK/BCLK/FS, pinout candidato X201 4 pin e U203 5 pin, inventario connessioni, S-expression bilanciata, script automatico.

NON ESEGUITO: controllo nativo KiCad ERC/DRC, assegnazione footprint, simulazioni SPICE, configurazione STM32 SAI/codec via hardware, misure EMI/RF, prova di rumore e jitter.

Osservazione di progetto: V1.7 presupponeva due domini clock potenzialmente indipendenti. V1.8 attribuisce a codec l'origine BCLK/WCLK sincronizzati al 12.288 MHz, con STM32 SAI slave. Restano prove di firmware e registri TI.
