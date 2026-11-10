# KiCad V7.13 — indice gerarchico RX / MCU / AUX

Aprire `S3900E_RX_POWER_INTEGRATION_V7_13_GRID_NOT_FOR_FAB.kicad_sch` con KiCad 9. I tre fogli collegati esistono realmente:
- AUX power V1.5 originale, senza modifiche;
- MCU/CODEC V7.12 rinumerato, senza modifiche;
- RX coupon V7.13, schema corretto sulla griglia 1,27mm.

`kicad-cli sch export netlist` conferma **99 nets con esatti stessi ref/pin** del root V7.12. Il root **NON collega elettricamente AUX/MCU/RX**: 15 interfacce OPEN/HOLD. ERC root **43 errori +370 warning**, DRC RX **85 violazioni+63 unconnected**. Nessun circuito o PCB completo della radio esiste e la TX è DNP/OPEN.

**NO FAB / NO TX**.
