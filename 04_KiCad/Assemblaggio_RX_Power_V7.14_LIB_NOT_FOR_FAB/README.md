# Superstar 3900 — assemblaggio KiCad gerarchico V7.14 (NON PCB completo)

Aprire **`S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_pro`** in KiCad 9. Il root `.kicad_sch` contiene gli stessi **7 fogli** della V7.13: AUX V1.5, MCU/CODEC V7.12, RX V7.14. Le tabelle di progetto `sym-lib-table` e `fp-lib-table` registrano le librerie RX, senza modificare gli originali AUX/MCU.

Le due esportazioni reali di KiCad mantengono **99 reti identiche con stessi componenti/pin**. Le **15 interfacce AUX/MCU/RX rimangono OPEN/HOLD**: i moduli NON sono ancora collegati elettricamente. La RX standalone supera l'ERC, mentre il ROOT ha ancora **43 errori e 340 warning**; non dichiararlo ERC clean. Il PCB V7.14 disponibile è soltanto il coupon RX, con 72 violazioni DRC e 63 unconnected, non un PCB di tutta la radio.

I pin FPGA SG48 restano HOLD, tutti i componenti e connessioni TX DNP/OPEN, i test RF e hardware non sono eseguiti.

**NO FAB / NO TX. Non creare Gerber né ordinare schede.**
