# V7.13 — Coupon RX a griglia 50 mil / 1,27 mm, SOLTANTO studio KiCad

**NO FAB / NO TX.** Lo schema `S3900E_RX_GRID_V7_13_NOT_FOR_FAB.kicad_sch` è una copia modificabile del foglio RX standalone V7.12, con **15 origini di simboli, 31 segmenti di filo e 31 ancore di etichetta** riallineati geometricamente alla griglia di connessione KiCad da **1,27 mm**. I pin delle librerie cached erano già multipli della griglia. Non sono stati modificati i simboli, pin, identificativi di riferimento, valori dei componenti, portata del ricevitore, né la scheda PCB V7.12.

**Condizione di approvazione: confronto degli output veri `kicad-cli sch export netlist`** dello schema V7.12 e V7.13: per ciascuna net devono essere IDENTICI nomi, designatori e numeri pin; un solo delta blocca la correzione e vieta di chiamarla equivalente. Inoltre il nuovo ERC nativo deve segnare zero `endpoint_off_grid` rispetto ai 46 V7.12, senza nuove violazioni di tipo error. Il vecchio DRC della PCB resta 85 violazioni e 63 connessioni incomplete: non è uno sbroglio o un PCB completo.

La cartella include `sym-lib-table` e `fp-lib-table` con riferimenti relativi alle **librerie storiche NON QUALIFICATE**. La presenza dei file tabella **non dimostra la risoluzione dei warning di libreria**: verificare i messaggi del vero ERC KiCad prima di dichiarare risultati. Il root a sette fogli V7.13, nella cartella `../Assemblaggio_RX_Power_V7.13_GRID_NOT_FOR_FAB`, mantiene interfacce AUX/MCU/RX NON CONNESSE e riferimenti univoci.

Tutti i DAC, TX, PA, FPGA e connettori RF in trasmissione restano DNP/non alimentati/non instradati. Non generare o inviare Gerber. Prossime attività: qualificare librerie/pin, risolvere ERC root, DRC RX e collegare soltanto reti validate.
