# Superstar 3900 SMD Evolution — V7.17 master di integrazione della radio

**Indice gerarchico KiCad a sette fogli, NON schematico integrato elettricamente, NON PCB dell'intera radio. NO FAB / NO TX.**

## Aprire in KiCad

Aprire `S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_pro` e il relativo file `.kicad_sch` in **questa cartella V7.17**. Il nome base `V7_14` è volutamente conservato per preservare i riferimenti delle istanze già annotate nei sottoprogetti e verificare con il tool nativo KiCad ogni esatto collegamento pin/net V7.14↔V7.17. La cartella ed il titolo schematics identificano l'integrazione **V7.17**.

Contiene esattamente gli stessi tre fogli esterni già presenti nella gerarchia V7.14: AUX_POWER (tre figli eFuse, buck, PLL/TCXO), MCU+CODEC+AFE, RX coupon 50ohm. I componenti **non sono cablati tra fogli**: nessun nuovo pin gerarchico, filo, power rail, TX, RF path, connettore o footprint è aggiunto. Il progetto contiene le tabelle di libreria locali, ancora non certificate dal vendor.

La matrice `MATRICE_INTERFACCE_PROPOSTE_V7_17_OPEN_HOLD.csv` ha 15 righe **OPEN/HOLD**; modifica soltanto il nome del candidato lato MCU per il segnale FM (`FM_DISCR_RAW` della sorgente esterna → **`FM_DISCRIM_RAW`** già presente nella netlist MCU). Questo è **allineamento di un nome proposto, non collegamento elettrico**. L'impedenza, i livelli e la protezione ESD del discriminatore sono ancora da stabilire. Le altre 14 righe sono invariate.

## Diagnosi reale da KiCad 9

I report in `03_Verifiche/V7.17/output-ci` dell'artefatto GitHub Actions misurano in modo nativo:
- 7 schede, 99 reti, con tutte le coppie **nome rete ↔ riferimento/pin** invariate rispetto alla V7.14, se il gate di parità nativa è PASS;
- **43 errori root ERC**, di cui 26 etichette non connesse, 3 wires sospesi, 6 alimentazioni senza driver, 5 input non pilotati, 2 pin non collegati e 1 conflitto output power ↔ output power;
- **340 warning root**, con 219 off-grid e 121 problemi di libreria;
- RX ERC standalone V7.14: **0 errori /0 warning**;
- dopo la rettifica del nome candidato FM, i due candidati `RX_IF_STAGE` e `RF_TX_UNROUTED` **non risultano reti presenti nel rispettivo foglio**. Il secondo è mantenuto intenzionalmente senza percorso TX.

La matrice registra corrispondenze di **nomi di rete nella netlist nativa**, non prova cablaggio esterno né approvazione del pin fisico. Non trasformare la matrice in connessioni PCB per uguaglianza di nome.

## Sviluppo PCB completo: gate prima del routing

1. **Alimentazione e ritorni**: riesaminare il pin-to-pin eFuse U200 15/16 (entrambi `power output`), sorgenti di 5V/3V3, domini GND_MAIN/GND_RF, EMC e corrente d'ingresso; vietato unire 5V→3V3.
2. **PLL / TCXO e SPI MCU**: verificare manualmente livelli SPI e MUXOUT, abilitazione CE fail-closed, SysRef/Ramp e loop filter; chiudere gli errori senza no-connect falsi.
3. **Catena RX→IF**: `RF_ATTEN_OUT` esiste solo nel coupon; manca lo stadio `RX_IF_STAGE`; non scegliere automaticamente topologia o frequenze prima delle specifiche RF.
4. **Codec/AFE/discriminatore FM**: la denominazione del segnale è allineata, ma porta esterna e livelli non validati; microfono, bias e filtri richiedono MPN/parametri.
5. **Fase PCB vera**: dopo la qualificazione dei 15 contratti e la correzione root ERC, creare una `.kicad_pcb` nuova della radio con stack-up, ritorni RF, piazzamento e netlist reali; valutare la validità geometrica TE degli SMA prima di Fab.

Tutti gli artefatti qui sono strumenti di integrazione pre-layout. **Non creano Gerber, non autorizzano PCBWay e non attivano TX.**
