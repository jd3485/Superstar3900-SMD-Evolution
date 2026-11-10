# ECO CAD V7.13 — RX 50 MIL GRID / NATIVE KIcad NET-PIN PARITY

**10 novembre 2026. Origine: V7.12 main `29212dd41050a658d637a412773a77d309402074`.** Valido esclusivamente per schema RX di prova **NOT FOR FAB**, nessun componente o circuito TX montato.

- Nuova copia di schema RX `04_KiCad/Modulo_RX_Test_50ohm_V7.13_GRID_NOT_FOR_FAB/S3900E_RX_GRID_V7_13_NOT_FOR_FAB.kicad_sch`: allineamento geometrico da coordinate arbitrarie alla griglia originale KiCad **1,27 mm** per 15 simboli, 31 wire, 31 label, senza toccare UUID dei componenti o pin cached, valori, references, schematic originario.
- Nuovo indice gerarchico RX/MCU/AUX V7.13 `04_KiCad/Assemblaggio_RX_Power_V7.13_GRID_NOT_FOR_FAB/S3900E_RX_POWER_V7_13_GRID_NOT_FOR_FAB.kicad_sch`, con MCU e alimentazioni come nella V7.12, fogli **elettricamente scollegati**.
- Aggiunti `sym-lib-table` e `fp-lib-table` locali per mantenere i riferimenti alle librerie archivio. **Non rivendicare una correzione** di questi link: KiCad riporta ancora 15 warning simboli e 15 warning footprint dopo il test.
- `kicad-cli sch export netlist` su entrambe le versioni RX, confronto completo delle triple **(nome rete, riferimento, numero pin)**: **IDENTICHE / PASS**. Il gate impedisce scorciatoie che taglino una net solo per far scomparire gli avvisi.
- `kicad-cli sch erc` reale: **RX 76→30 warning e 46→0 off-grid**, 0 errori RX in entrambe; gerarchia **459→413 totali** (43 errori invariati, warning 416→370). Nessuna regola ERC soppressa.
- PCB RX reale V7.12 **non modificata**, `kicad-cli pcb drc` riconferma **85 violazioni DRC e 63 unconnected**, 70 vias dangling e 15 footprint; zero nuovi segnali o alimentazioni; NO FAB.
- CI GitHub Actions [run 42869838167](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42869838167), job 130017817769 **SUCCESS**, log esaminato: **10 nuovi+13 V7.12+8 V7.11+12 V7.10+143 precedenti = 186 test Python PASS** /0 FAIL/0 SKIP. Sintesi Yosys e testbench Icarus *non* ripetuti in questa revisione, risultati archiviati nelle revisioni precedenti.
- **Prossima V7.14:** qualificare e risolvere librerie tramite vero progetto KiCad e footprint corrispondenti, lavorare sul routing reale del coupon RX e le sue zone GND con prove DRC, affrontare i 43 errori ERC root ed i 15 confini POWER/MCU/RX OPEN/HOLD con verifica primaria pin/rail. Continuare firmware DSP/PLL.

**Decisione:** V7.13 candidabile per `main` esclusivamente come correzione CAD numerica e nativa dopo verifica CI della PR. PCB completo e test elettrici NON ESEGUITI. **NO FAB / NO TX.**
