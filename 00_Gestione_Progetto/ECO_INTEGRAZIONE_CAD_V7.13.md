# ECO V7.13 — allineamento griglia KiCad RX 50 mil

**10 novembre 2026. Base `main` V7.12 SHA `29212dd41050a658d637a412773a77d309402074`. NO FAB / NO TX.**

1. Nuova copia `.kicad_sch` RX V7.13 con **154 coppie XY** allineate a multipli di **1,27 mm**; zero modifica a simboli interni/pin, UUID, valori, 15 designatori. Nuova `.kicad_pcb` di solo studio con le stesse 15 impronte e stessa geometria, 0 alterazioni di rame. Originali V7.12 e precedenti preservati.
2. Root V7.13 links AUX V1.5 e MCU V7.12 storici e RX V7.13, **senza fili tra moduli**. Aggiunta verifica automatica di tutti i tre sheetfile per evitare ripetizione del primo FAIL causato da file MCU non trovato. 15 interfacce cross-module OPEN/HOLD, FPGA pinout SG48 HOLD.
3. Aggiunta `sym-lib-table` locale con path relativo alla libreria simboli RX esistente; conservata `fp-lib-table`. Il dato nativo **non dimostra ancora la risoluzione** degli avvisi vendor/librerie: 15 lib symbol +15 footprint RX restano aperti.
4. `kicad-cli sch export netlist` autentico su V7.12 e V7.13: **99→99 reti**, **0 differenze fra tutti i componenti/pin appartenenti a ciascuna rete**, gate bloccante in caso di differenza.
5. `kicad-cli sch erc` reale: RX **0 errori /76→30 warning**, di cui `endpoint_off_grid` **46→0**. Root **43 errori e 416→370 warning** (totale 459→413). **ERC complessivo resta FAIL/non idoneo**.
6. `kicad-cli pcb drc` reale: RX coupon **85 violazioni +63 unconnected** invariati; 70 dangling via e15 footprint warnings. **DRC non è PASS**. Nessun nuovo componente fisico o pista RF.
7. Test V7.13: **12 nuovi Python** più **176 regressioni V7.1–V7.12 =188 PASS**, Icarus/Yosys non rieseguiti. Workflow `.github/workflows/v713_rx_grid_native_erc.yml` e raporti native `.rpt` scaricabili dall'Actions artifact.
8. Prossima V7.14: librerie/pin vendor e ritorni massa/connessioni del coupon RX, poi ERC del root; DSP, firmware, PLL e simulazioni restano in processo.

**NO FAB / NO TX.** Non generare Gerber o alimentare DAC/FPGA/PA/mixer/antenna, non dichiarare RF misurata o fabbricabilità.
