# ECO V6.6 — Interfacce e preservazione del progetto RX

- V6.5 `F501 BPF IDEALE` non viene rimpiazzato nei documenti precedenti: V6.6 definisce **due implementazioni alternative**. A (discreta) è un vero circuito RLC adatto a simulazione, ma non qualificato; B (SXBP-27R5+) è un filtro commerciale 50Ω con scheda tecnica e pinout, ma non validato con i moduli del progetto.
- Lato antenne: RX_RF_FROM_V58 (J501) → **J601/F501** → J602 → porta RF U501 ADE-1+ pin3. Lo schema completo dovrà verificare se il preselettore sia prima/dopo LNA; in caso sia dopo, analizzare blocker che saturano l'amplificatore.
- LO, guard RX/PA, IF 10,695 MHz e PA/TX safety: nessuna modifica ai file originali. Nessun collegamento all'uscita TX o a un relè TX; nessuna abilitazione RF.
- C_FEED modello = capacità parassita virtuale tra RF_IN_50R e RF_OUT_50R: non è un componente BOM o una rete da implementare.
- Il ramo shunt deve essere fisicamente RF_PRE_MID↔GND_RF; C601||C602 tra RF_PRE_A e RF_PRE_MID; C605||C606 tra RF_PRE_B e RF_OUT_50R.
- Da scegliere: Q/SRF/MPN induttori, package/footprint, geometria PCB, S-parametri reali, sonda e isolamento, stadi adattamento e NF, BOM DFM.
- Non simulata risposta in temperatura reale; nessuna revisione KiCad nativa (ERC/DRC NOT_RUN), nessun ngspice eseguito (NOT_RUN), nessuna RF misurata.
**NO FAB, NO TX.**
