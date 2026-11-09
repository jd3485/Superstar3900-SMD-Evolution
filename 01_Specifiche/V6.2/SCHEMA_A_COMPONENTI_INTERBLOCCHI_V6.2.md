# V6.2 — circuito candidato, NON schematico KiCad

La V6.2 definisce componenti con pin fisici e collegamenti nominativi; **non è un progetto hardware validato**. Le assegnazioni sono in `NETLIST_INTERBLOCCHI_V6.2.csv` e `CIRCUITO_INTERBLOCCHI_V6.2.json`.

## Catena TX fail-closed (solo logica 3,3 V)

**SUP_3V3_OK = /RESET TPS3823A-33**, alimentato da 3V3_D, alto solo quando il reset non è attivo e il watchdog è sano (in condizioni definite dal datasheet). **BAT_UV_OK / BAT_OV_OK** provengono dalle uscite open-drain con pullup del TPS3700 alimentato a 3,3 V, con ingressi separati su +13V8_PROTECTED tramite partitori 287k/10k e 374k/10k. Soglie nominali 11,88 V e 15,36 V, non garantite considerando accuratezza, isteresi, ripple, tolleranze e carico.

**TX_ENABLE_HARD = SUP_3V3_OK ∧ BAT_UV_OK ∧ BAT_OV_OK ∧ RX_SAFE_NC ∧ ¬PA_MODE_HW ∧ FAULT_LOOP_OK ∧ TX_ARM_REQUEST ∧ ¬PTT_N ∧ TX_BENCH_KEY**.

`TX_BENCH_KEY` resta LOW, con resistenza a massa da 47k e jumper J801 **DNI/non montato**. Il segnale TX_ENABLE_HARD va soltanto a un futuro connettore logico; **nessun finale RF è connesso**, non esiste autorizzazione TX.

## Miglioria importante rispetto alla V6.1

Il secondo polo del selettore PA denominato S742 in V6.1 era stato rappresentato come DPST, ma un semplice contatto normalmente aperto **non realizza la sicurezza per filo interrotto**. È richiesta una **ECO meccanica**: contatto separato **SPDT break-before-make**, COM=3V3_D, NC=RX_SAFE_NC (alto solo in RX), NO=PA_MODE_HW (alto solo in PA). RX_SAFE_NC e PA_MODE_HW hanno pull-down. La logica nega la trasmissione anche se per guasto RX_SAFE_NC resta alto mentre PA_MODE_HW è alto. In caso di disconnessione comune entrambi sono bassi -> TX OFF. Il primo polo PA_SENSE_N del pannello rimane separato.

Il contratto V6.1 del microcontrollore richiede inoltre due riserve convertite in uscite: **PB11/pin33 WDI_HEARTBEAT**, **PB4/pin57 TX_ARM_REQUEST**; aggiornamento di firmware/schema da fare nella variante attiva futura. Non sono stati sovrascritti i file V6.1 storici.

## Interfacce e vincoli aperti

J803 passa POWER_GOOD_HW al PA12 MCU, AMP_SD verso J604 pin10, PA_RELAY_EN verso il driver relè. Il collegamento diretto precedente tra PA8 e AMP_SD deve essere **interrotto**; PA8 diventa solo richiesta, analogamente PA10/relè. La V6.0 usava un BTL: entrambi i fili dell'altoparlante restano isolati da GND e commutati da relè a doppio scambio.

Il TPS3823A-33 necessita di heartbeat fisici adeguati sul WDI e di verifica delle condizioni di watchdog. U802 non è protetto da disturbi reali, il partitore va dimensionato per tensioni transitorie, ESD e picchi automotive. Protezioni ingresso 13,8V (fusibile, inversione, TVS, filtraggio, brownout), isolamento domini 3V3_A/UI/D e unità SWR/termiche da progettare. Il loop FAULT_LOOP_OK è futuro: **nessun bypass in produzione**.

Nessuna prova di immunità a singolo guasto, qualifica EMC o idoneità normativa; il contatto incollato e i cortocircuiti al 3V3 possono vanificare alcuni interblocchi. Prima del TX reale occorreranno ulteriori interblocchi indipendenti, misure e processo di collaudo.

## Fonti dati

- TI TPS3823, scheda prodotto: https://www.ti.com/product/TPS3823
- TI TPS3700, scheda prodotto: https://www.ti.com/product/TPS3700
- TI SN74LVC1G08, scheda prodotto: https://www.ti.com/product/SN74LVC1G08
- TI SN74LVC1G04, datasheet: https://www.ti.com/lit/ds/symlink/sn74lvc1g04.pdf

Controlli elettronici e gate della **radio completa** da integrare nelle prossime revisioni, simulazioni native a chiusura architettura e test intermedi a ogni versione. Nessun Gerber, nessuna fabbricazione.
