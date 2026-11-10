# RX 50 Ω — KiCad V7.13, griglia 50 mil corretta

Aprire con **KiCad 9** `S3900E_RX_STANDALONE_V7_13_GRID_NOT_FOR_FAB.kicad_sch`, la copia reale dello schema RX V7.12. Tutti i 15 componenti conservano valori, nomi, pin e rete; **154 coppie coordinate** di elementi di schema sono state allineate sulla griglia 1,27mm; nessuna connessione diversa secondo il confronto completo delle netlist KiCad esportate (**99 reti /0 divergenze** nella gerarchia).

Il file `.kicad_pcb` adiacente è una COPIA identica del coupon V7.12 (non è una nuova board radio completa): **85 DRC violazioni +63 unconnected** restano; `fp-lib-table` e `sym-lib-table` sono diagnostiche locali e i warning di libreria non sono risolti. `kicad-cli sch erc` V7.13 RX riporta **0 errori/30 warning**; non è clean ERC.

**NO FAB / NO TX.** Non ordinare prototipi e non usare RF.
