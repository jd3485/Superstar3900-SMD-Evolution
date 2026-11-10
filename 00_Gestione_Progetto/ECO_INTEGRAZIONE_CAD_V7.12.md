# ECO V7.12 — RX standalone riparato e annotazione KiCad globale non ambigua

**10 novembre 2026 — Sviluppo CAD nativo, NO FAB / NO TX.** La revisione V7.12 prende come baseline `main` V7.11; non modifica gli schemi/piazzamenti originali AUX V1.5, MCU V2.1, RX V5.2 e PCB V7.11, né i modelli firmware/DSP/PLL.

## Esecuzione, file e decisioni

1. Nuovo **root gerarchico KiCad V7.12** `04_KiCad/Assemblaggio_RX_Power_V7.12_REANNOTATED_NOT_FOR_FAB/S3900E_RX_POWER_INTEGRATION_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch`. Include power V1.5 storica e copie rinumerate di MCU/codec e RX. **Tutti i 15 collegamenti fra moduli rimangono OPEN/HOLD** per mancata verifica rail/pin; non introduce fili, sheet pins, global labels, TX o PA.
2. MCU copia V7.12: **46 designatori** rinumerati +6000 (es. `U201→U6201`). RX copia: **15 designatori** +9000 (es. `J101→J9101`, `R201→R9201`). Modificati sia i `Reference` grafici sia il `reference` salvato negli `instances` del foglio. Il PCB RX copia dal V7.11 ha **le stesse 15 refs** rinumerate e stesse reti/vie/fori.
3. **KiCad9 `sch export netlist` davvero eseguito su root V7.10 e V7.12:** 7 fogli/132 istanze/99 reti *identiche*, ripetizioni riferimenti **11→0** e istanze extra duplicate **14→0**. Risultato controllato automaticamente dall'analizzatore sui due output nativi, non semplicemente da regex sui sorgenti.
4. **Root cause risolta per RX standalone:** nella V5.2 la nota grafica `(text)` aveva **LF reali non escapati dentro una stringa quoted**, e non aveva l'UUID grafico necessario; KiCad falliva con `exit3 Failed to load schematic`. Il parser probe con copie usa senza alterare originali: librerie e 15 simboli e 31 fili e 31 etichette isolati caricavano, la variante con testo non valido no. Nella copia V7.12 testo riparato (`\n` S-expression e UUID) + metadati foglio; il vero `kicad-cli sch erc` standalone ora **exit0**, produce **76 ERC warning /0 ERC error**. **Non è ERC clean**.
5. **Root ERC** del nuovo assemblaggio: **43 errori +416 warning =459 rilievi**, invariato. **PCB RX DRC:** 85 violazioni con 70 dangling vias +15 footprint warnings, e **63 connessioni non terminate**. La V7.12 non nasconde o risolve questi difetti; mantiene le sei riparazioni fori V7.11 e tutte le geometrie del PCB.
6. Workflow `.github/workflows/v712_kicad_native_annotation.yml`: installa KiCad CLI 9, esporta due netlist, verifica nomi, esegue ERC root/RX standalone e DRC coupon, conserva tutti i report e ritenta 13 nuovi test Python V7.12 +8 V7.11 +12 V7.10 +143 regressioni V7.1–V7.9 = **176 Python PASS** sui run verificati. Nessun nuovo Icarus/Yosys; gli HDL storici rimangono validi come prove software precedenti, non qualifica RF.
7. Le prime CI hanno rilevato una soglia test dimensione file troppo rigida, un `grep` improprio sul report e il persistere della nota RX raw LF. Tutti sono stati corretti **senza diminuire soglie ERC/DRC**; citare soltanto l'ultima CI conclusa sul commit verificato.
8. Documenti e dati sono versionati: rapporto root `Superstar3900_Rapporto_Tecnico_V7.12.md`, spec `01_Specifiche/V7.12/RIANNOTAZIONE_NATIVE_RX_MCU_V7_12.md`, JSON risultati e report nativi come artifact GitHub Actions.

## Stato e decisione

**Superato:** il blocco di caricamento dello schema RX standalone e i riferimenti ripetuti della gerarchia.
**Ancora bloccante:** 43 ERC error sul root, warning KiCad, 85 DRC del PCB RX, 63 unconnected, footprint SMA/thermal qualificati, rete RF e alimentazioni RX/MCU realmente connesse. I pin FPGA Lattice SG48 restano HOLD. **Nessun PCB full-radio o TX**.

**Prossima V7.13:** correggere in KiCad le cause reali di warning pin/off-grid/footprint, poi collegamenti e massa del modulo RX e verificare CRC/DRC a ogni iterazione; solo dopo collegare una per una interfacce power/MCU/RX vendor verificate. Continuare modelli e firmware in parallelo. **NO FAB / NO TX.**
