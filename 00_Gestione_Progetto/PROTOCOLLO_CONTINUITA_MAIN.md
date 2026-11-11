> **CONTINUITÀ WORK TRA CHAT:** protocollo permanente [AGENTS.md](../AGENTS.md), stato operativo dinamico [WORK_STATO_CORRENTE.md](WORK_STATO_CORRENTE.md), istruzioni persistenti [ISTRUZIONI_CHATGPT_PROJECT_WORK.md](ISTRUZIONI_CHATGPT_PROJECT_WORK.md). All'avvio della nuova chat Work ricostruire HEAD/PR/CI dal repo, eseguire *più versioni tecniche consecutive* e aggiornare il checkpoint dopo ogni merge; mai richiedere un nuovo «continua» dopo ogni PR, né inventare esecuzioni in background. **NO FAB / NO TX.**

# PROTOCOLLO CONTINUITÀ — V7.21 PRE-LAYOUT QUALITY / BOM / TERMICA (NO FAB/TX)

**11 novembre 2026 · V7.21 MERGED su `main` tramite [PR #21](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/21), squash merge `9805f110d0acf59e69f7f54e87e299248b99d96b`.**

- Vero KiCad9 master 7 fogli V7.19 / netlist 100 reti: **132 componenti**, 48 footprint missing (46 MCU/CODEC +2 AUX J100/J101), 84 assigned (NON tutti approvati), F200 e Y1 assigned con marcatori espliciti non validati. Root ERC ancora **36 errors/340 warnings**, 15 interfaces OPEN/HOLD.
- **CRITICAL pin/pad mismatch:** codec U6202 TI RHB footprint has EP33 thermal pad whereas actual embedded KiCad symbol has **only pins 1–32** (verified from exported libpart). TI SLOS602E §12.1 says thermal pad MUST be connected to PCB ground plane, and is not internally connected. Must add EP33 pin and qualify its GND in V7.22; no footprint release before.
- Real KiCad9 library test **6 candidate packages** senza assegnazione: U6201 ST LQFP64 10x10/p0.5 pad1..64, U6202 TI RHB VQFN32 5x5/p0.5 32 perim + pad **33 EP**, U6203..6206 TI TPS7A20 DBV SOT23-5 pad1..5. MPN ↔ symbol pin and stencil/mask/thermal/integration NOT verified.
- Serious thermal *screen*: TPS7A20 DBV JEDEC `RθJA=187.1°C/W`. 5→3.3V @300mA =0.51W, 40°C ambient JEDEC example TJ≈135.4°C above 125°C operating. Not measured load nor board temperature; require continuous load & derating calculation before PCB release. 6 LDO nameplate 1.8A not real load, 2 AUX 5V,4 isolated MCU 5V.
- TPS54202 buck 2A, feedback R101100k/R10213k3 -> Vout_nom≈5.077V, Vref+R tolerance-only arithmetic 4.863–5.298V, not guaranteed total. eFuse TPS26600 2.23A adjustable upper, F200 1.5A candidate and footprint not validated. GND_MAIN vs GND MCU and EFUSE_RTN isolated, no PWR_FLAG or fake connection.
- Native GitHub Actions [CI 42986310630](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42986310630) **success**, **24 V7.21 tests +284 past=308 PASS 0 FAIL/SKIP**, no hardware. All KiCad original files unchanged, no global PCB, Gerber or TX.
- Outputs `03_Verifiche/V7.21/RAPPORTO_TECNICO_CAD_V7.21.md`, results JSON, CI CSV missing48 and package6, spec `01_Specifiche/V7.21/PIANO_QUALITA_PCB_UNICA_GATES_V7_21.md`. Whole PCB approx **10% estimate unchanged**; next **V7.22** source-vendor pin map + EP33 and 6 IC package assignment versioned, then remaining 42 and power/mechanical gate.
- **NO FAB / NO GERBER / NO PCBWAY / NO TX**, SG48 HOLD. Do not claim zero errors without ERC+DRC/inspection/bench.

---

## STORICO PROTOCOLLO V7.20 E PRECEDENTI

# PROTOCOLLO CONTINUITÀ MAIN — V7.20 PLL SPICE + POWER ERC

**11 novembre 2026 · V7.20 MERGED su `main` tramite [PR #20](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/20), squash commit `271cf7c84c0ceeb1e490ac44ff065147c76fbb4e`. NO FAB / NO TX.**

- `03_Verifiche/V7.20/verify_pll_spice_270_v720.py`: **verifica ngspice AC nativa** file passivo `Filtro_LMX2572_V0.6_ac.cir`, 501 punti su 10Hz–1MHz, accordo modulo dell'impedenza con analisi nodale indipendente errore max **8,31e-7**. Modello ancora IDEAL, non PLLatinum Sim né banco, PLL CPG e Kvco reali non caratterizzati; valori filtro TI non approvati.
- 270 canali esatti N3631..3900 con piano frequenze `frequency_arithmetic_only`, 2430 scenari KVCO (39/55/85) × Icp (2,3/2,5/2,7mA), **non tolleranze TI**; 270 scenari *tipici* da TI SNAS740B Table135 Eq4 (2 VCO3/268 VCO4). CPG=4 o8 corrisponde a 2,5mA ma configurazione non verificata. Solo modello: crossover **3814..4678Hz**, margine **58,63..62,87°** su Kvco tipico.
- `03_Verifiche/V7.20/audit_native_power_v720.py`: **6 power_pin_not_driven** da KiCad9 ERC+netlist reale: U200 IN (EFUSE_VIN), U200 RTN (EFUSE_RTN); U2 IN (5V_RF_PREREGULATED), U2 GND (GND_MAIN); U6203 IN (5V_DIGITAL_FILTERED), U6203 GND (GND MCU). 0 Power flags/waiver. Reti GND distinte, eFuse RTN non unire a massa; 13,8V/5V/3V3 non unire implicitamente.
- Native [CI 42971210346](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42971210346) **success**: **18 nuovi+266 regressioni=284 PASS**; 36 ERC root errori +340 warning conservati,100 reti,15 interfaces OPEN/HOLD e TX0. Icarus/Yosys e HW non nuovi.
- V7.20 non cambia KiCad V7.19, RX coupon, PCB, firmware o manufatti. La percentuale della PCB completa rimane ~10%. V7.21 power-domain qualification, TI official PLLatinum/hardware, 15 nets crossmodule prima del layout. Fonte `03_Verifiche/V7.20/RAPPORTO_TECNICO_CAD_V7.20.md`, JSON, spec `01_Specifiche/V7.20/`, workflow.
- **NO FAB / NO GERBER / NO PCBWAY / NO TX**, SG48, IF missing e SMA vendor HOLD.

---

## STORICO PROTOCOLLO V7.19 E PRECEDENTI

# PROTOCOLLO CONTINUITÀ MAIN — V7.19 LMX2572 LOOP PIN-NET

**11 novembre 2026 · V7.19 MERGED su `main` con PR #19, squash merge `6d5ccb179cbe46760605edde6c44c2fc89a9ac5e`. NO FAB / NO TX.**

- Origine: V7.18 root KiCad ERC 42 errori/340 avvisi; `R2/R3` disegnati ma mancanti dalla netlist nativa. Schema vendor [TI LMX2572 SNAS740B Fig179 p75](https://www.ti.com/lit/ds/symlink/lmx2572.pdf) e EVM SNAU217B confermano topologia CPout-R3-Vtune, C1 shunt CP, R2-C2 in serie shunt, C3 shunt Vtune.
- V7.19 master a sette fogli `04_KiCad/Assemblaggio_RX_Power_V7.19_PLL_PINNET_NOT_FOR_FAB/`; ramo versionato `04_KiCad/Gerarchico_Alimentazioni_V7.19_PLL_PINNET_NOT_FOR_FAB/`. Nel SOLO file PLL aggiunte **esattamente sei label** su R2:1/R2:2/R3:1/R3:2/C2:2/C3:2; tutti gli altri schemi AUX byte identici a V7.18 e RX/MCU immutati.
- Vero KiCad9 [CI 42967147073](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42967147073): **36 ERC errori (prima 42), 340 warning invariati**, rete nativa 99→100 (**sola `PLL_R2_C2`**), 12 membership pin TI esatti, no cambi fuori dalle tre reti `PLL_CPOUT/PLL_R2_C2/PLL_VTUNE`. -2 pin_not_connected/-3 wire_dangling/-1 pin_not_driven. **266 Python PASS =13 V7.19+253 regressioni;0 FAIL/SKIP**.
- HOLD non risolti: **36 ERC =26 dangling-label+6 power undriven+4 input undriven**, 340 warning, 15 interfacce OPEN/HOLD, SG48 HOLD, RF filter R2 620/R3 22/C1 220p/C2 120n/C3 2.2n non simulato/qualificato, GND per VCO da verificare, SMA 180° J9102/J9104 mismatch non qualificato. Nessun vero PCB globale / Gerber / PCBWay / TX.
- Percentuale della PCB COMPLETA ~10% invariata perché è avanzato lo schematico, non routing e layout. V7.20: **PLLatinum Sim** e power input qualification, poi 15 interfacce e PCB reale. Source `03_Verifiche/V7.19/RAPPORTO_TECNICO_CAD_V7.19.md`, JSON, artifact nativo.

**NO FAB / NO TX, niente emissioni, protezioni PA/antenna non installate.**

---

## STORICO PROTOCOLLO V7.18 E PRECEDENTI

# PROTOCOLLO CONTINUITÀ — V7.18 ECO ERC TPS26600 / PLL TEST

**11 novembre 2026 · V7.18 MERGED in `main` tramite PR #18, merge `29965cdcdfe2edd1e241295315bfe18fabc864a5`.** Storico preservato, nessuna modifica ai vecchi KiCad. **NO FAB / NO TX.**

- Nuovo AUX versionato `04_KiCad/Gerarchico_Alimentazioni_V7.18_PINMODEL_NOT_FOR_FAB/`: nel solo simbolo embedded U200 TPS26600PWPT OUT16 `power_out`→`passive`, OUT15 resta `power_out`. TI SLVSDG2G p.5: entrambi pin OUT15/16 stessa uscita power. **Wiring identico / nessun pin eliminato**.
- Nuovo master KiCad 7 fogli `04_KiCad/Assemblaggio_RX_Power_V7.18_POWER_PINMODEL_NOT_FOR_FAB/`: tutta la netlist **99 reti e pin/refs IDENTICI** al master V7.17; ERC nativo [CI 42964160297](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42964160297) **43→42 errori**, 340 warning invariati; sola categoria `pin_to_pin` -1. 12 test V7.18+241 storici=**253 PASS**, 0 FAIL/skip; no hardware.
- PLL R2/R3: **4 prove su CLONI** con vero `kicad-cli` confermano nessun miglioramento. R2 rewire proposto 42/341 avvisi, R3 invert 42/340; entrambi 42/341 vs 42/340 baseline. Le proposte non sono state salvate nello schema versionato. Occorre topologia TI e revisione visuale prima di aggiungere piste.
- Residuo **42 errori =26 label +16 hard**: 6 power undriven,5 input undriven,3 wire dangling,2 pin non connected; 15 interfaces OPEN/HOLD, 5V vs3V3 distinti, SG48 HOLD, TX fisicamente assente, RX_IF mancante, SMA 180° non qualificato.
- Full PCB layout ~10% stimato senza aumento; `03_Verifiche/V7.18/RAPPORTO_TECNICO_CAD_V7.18.md`+JSON e `01_Specifiche/V7.18/ECO_EFUSE_DUAL_OUT_PINMODEL_V7_18.md` danno handoff. Prossimo V7.19: riparare loop filter con verifica TI e root ERC, senza inventare connessioni di alimentazione.
- **NO FAB / NO GERBER / NO PCBWAY / NO TX**, nessun collaudo vero, nessuna antenna o PA.

---

## STORICO PROTOCOLLO V7.17 E PRECEDENTI

# PROTOCOLLO — SUPERSTAR 3900 SMD V7.17 FULL-BOARD INTEGRATION GATE

**11 novembre 2026 · V7.17 MERGED su `main` tramite PR #17, merge `ff26db4e55eb2ab7368cb222de58a8b969cf08d6`. NO FAB / NO TX.**

- Master KiCad vero a sette pagine: `04_KiCad/Assemblaggio_RX_Power_V7.17_INTEGRATION_HOLD_NOT_FOR_FAB/`; nessun collegamento elettrico fra AUX/MCU/RX aggiunto; componenti/refs/99 reti e pin membership **IDENTICI** alla V7.14, testati nativamente [GitHub Actions 42923409956](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42923409956).
- ERC master ancora 43 errori/340 warning, RX 0/0. Priorità 17 problemi elettrici/fili (6 undriven power, 5 undriven inputs, 3 dangling wires, 2 pins NC, 1 power output conflict) +26 label dangling. 219 endpoint_off_grid +121 library issues da risolvere successivamente.
- CSV V7.17 con 15 interface OPEN/HOLD, `tx_permission=0`, unica rettifica di denominazione candidata destinazione FM `FM_DISCRIM_RAW` come appare in netlist MCU. Assenti `RX_IF_STAGE` (ricezione incompleta), `RF_TX_UNROUTED` (TX intenzionalmente assente). Nessuna alimentazione 5V/3V3, GND_MAIN/GND_RF o PLL SPI può essere implicitamente unita.
- 18 test V7.17 +223 storici =**241 Python PASS**, 0 falliti/skip; nessuna misura reale, Icarus/Yosys nuovo, PCB totale, assembly o fabbricazione.
- Rapporto `03_Verifiche/V7.17/RAPPORTO_TECNICO_CAD_V7.17.md`, JSON e artifact nativo ERC+netlist+ledger. Stima PCB totale **~10%**, diagnostica non alza il layout. Prossimo V7.18: risolvere 17 ERC hard guidato da datasheet e circuiti veri, qualificare rail/IF/PLL prima di PCB. SMA J9102/J9104 mantengono 180° meccanici e mismatch da qualificare.
- **NO FAB / NO PCBWAY / NO GERBER / NO TX**, SG48 HOLD, nessuna antenna o PA connessi.

---

## STORICO PROTOCOLLO V7.16 E PRECEDENTI

# PROTOCOLLO PERMANENTE — V7.16 DIAGNOSTICA SMA, NO FAB / NO TX

**10 novembre 2026 · V7.16 integrata in `main` con PR #16, merge `b8ad95695aed960621f4fd2160fa4b2ae921d6eb`. Verificare sempre HEAD `main`.** Baseline V7.15 conservata e tag storico v7.0 intatto.

- KiCad9 CI [run 42920876308](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42920876308): **223 Python PASS**, 10 V7.16 +213 storici; quattro DRC nativi da veri cloni con fill/checkout path relativo corretto.
- Test scientifico isolato sul vero PCB: 2 warning `lib_footprint_mismatch` J9102/J9104 con orientamento 180°, 0 unconnected; 2 warning invariate modificando etichette o rotazione custom pad; zero warning modificando l'orientamento completo da 180°→0°. **Zero DRC sul clone NON è una correzione valida**: i due SMA sul bordo destro a 0° avrebbero body/courtyard rivolti all'interno, mentre a 180° sporgono 7,2mm oltre x130 (estensione fino x137,2). Sorgente PCB originale invariato.
- TE Connectivity/Linx `CONSMA002-SMD`, drawing Rev D e CAD DXF/STEP elencati sul sito ufficiale. Modellazione 2D/3D originale, F.Paste/F.Mask, stackup, RF return, DFM e qualifica vendor NON ESEGUITI.
- RX ERC baseline 0/0; root ERC ancora 43 errori+340 warning, 15 interfacce RX/AUX/MCU OPEN/HOLD, SG48 HOLD; nessun nuovo Icarus/Yosys hardware o RF/EMC.
- Rapporti `03_Verifiche/V7.16/RAPPORTO_TECNICO_CAD_V7.16.md` e JSON, protocollo vendor in `01_Specifiche/V7.16/`; codice in `03_Verifiche/V7.16/`; workflow `.github/workflows/v716_sma_native.yml`. **Next V7.17:** qualificare vendor/transform conservando 180°, poi clone PCB con refill persistito e ERC root, storico preservato.
- Non creare Gerber, non produrre, non collegare/accendere DAC/FPGA/PA/antenna e non trasmettere. **NO FAB / NO TX**.

---

## STORICO PROTOCOLLO V7.15 E PRECEDENTI

# PROTOCOLLO DI CONTINUITÀ MAIN — V7.15 DIAGNOSTICA NATIVA, NO FAB / NO TX

**10 novembre 2026 · V7.15 integrata su `main` con PR #15, merge `ca81deb3fe83e210778590cc9e2db1a18e16b243`; verificare HEAD `main` a ogni nuova chat.** Baseline V7.14 integrata intatta, `v7.0` preservata. Non cambiare circuiti o autorizzare TX in assenza di verifica fisica.

- V7.15 aggiunge inventario e audit PCB nativo, 12 test e workflow. Dati KiCad9 riproducibili in [run push 42918178033](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42918178033) e [PR 42918302874](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42918302874): **213 Python PASS** incluso 201 regressioni; ERC RX 0/0, root 43 errori+340 warning.
- Test DRC realmente eseguito PRIMA refill su PCB RX originale V7.14 **72 DRC +63 unconnected** (70 via dangling e 2 mismatch SMA J9102/J9104). File 15 footprints, 44 segmenti, 70 via net GND_RF, quattro zone senza `filled_polygon` persistiti.
- Il KiCad CLI del runner non supporta `--refill-zones`: ramo NON ESEGUITO. **Alternativa vera:** copia temporanea di TUTTO il progetto in sibling folder, `pcbnew.ZONE_FILLER`, DRC nativo sulla copia salvata e poi distrutta. Misurati **2 DRC (solo J9102/J9104) +0 unconnected, zero via_dangling**. Originale SHA256 `ec37ef62787eeb6607def2780d9a7da06a614eafd3b225283f6e9c6fd3a5f3d9` invariato. Non equivale a layout fisico approvato.
- Confronto parziale manufacturer TE/Linx `CONSMA002-SMD`, drawing Rev D: Ø2,05 e 7,76mm; DXF/STEP non importato, condizioni termiche/assembly e impedenza ancora HOLD. 15 interface MCU/AUX/RX OPEN/HOLD, FPGA SG48 HOLD, no new Icarus/Yosys/RF/EMC.
- Documenti attuali: `03_Verifiche/V7.15/RAPPORTO_TECNICO_CAD_V7.15.md`, `03_Verifiche/V7.15/RISULTATI_VERIFICHE_V7_15.json`, `01_Specifiche/V7.15/SMA_ZONE_READONLY_DIAGNOSTIC_V7_15.md`, workflow `v715_rx_sma_zone_native.yml`, `README.md`, `RIPRENDI_IN_UNA_NUOVA_CHAT.md`.
- **NEXT V7.16:** qualificare J9102/J9104 con vendor CAD, revisionare/salvare su nuova copia il riempimento zone verificato, analizzare return RF, risolvere ERC root e contratti OPEN/HOLD, preservare firmware/DSP/PLL e versioni storiche. **NO FAB / NO TX.** Nessun Gerber, PCBWay, PA/antenna o trasmissione autorizzati.

---

## ARCHIVIO PROTOCOLLO V7.14 E PRECEDENTI

# PROTOCOLLO PERMANENTE MAIN — V7.14 SU MAIN, NO FAB / NO TX

**10 novembre 2026 · V7.14 integrata in `main`, [PR #14](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/14), merge `5c0940bf213776e93e72f2bd11fd20ce4fa842e7`.** La versione corrente va sempre ricontrollata tramite HEAD `main`, PR e GitHub Actions; `v7.0` storico intatto. **NO FAB / NO TX.**

**Avanzamento CAD vero:** creati due progetti KiCad 9 con `.kicad_pro` e tabelle librerie locali: `04_KiCad/Modulo_RX_Test_50ohm_V7.14_LIB_DIAGNOSTIC_NOT_FOR_FAB/` (schema **e PCB** di coupon RX) e `04_KiCad/Assemblaggio_RX_Power_V7.14_LIB_NOT_FOR_FAB/` (gerarchia 7 fogli, NON collegamento elettrico fra i blocchi). I file storici rimangono conservati e il PCB RX è byte-identico alla V7.12. L'ERC RX è **0 errori /0 warning**, da **0/30** V7.13, grazie al corretto caricamento delle librerie KiCad tramite `.kicad_pro` (nessun waiver). La netlist RX e la gerarchia mantengono tutte le membership pin-rete originali: **99 reti gerarchiche identiche**. Il DRC RX è diminuito **85→72 violazioni**, ma rimangono **70 via GND dangling**, **2 footprint mismatch SMA J9102/J9104**, **63 unconnected items** e nessuna nuova pista. ERC root ancora **43 errori +340 warning** (V7.13: 43+370). Questi difetti sono BLOCCANTI per produzione.

**CI della PR #14 verificata:** [Actions run 42886396335](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42886396335), log controllato: **15 V7.14 + 186 regressioni V7.1–V7.13 =201 test Python PASS, 0 FAIL/SKIP**, KiCad9 vero su due progetti con ERC/DRC e netlist. Icarus/Yosys non rieseguiti e nessun test fisico/RF realizzato. Rapporto corrente `Superstar3900_Rapporto_Tecnico_V7.14.md`, specifica `01_Specifiche/V7.14/PROGETTI_KICAD_RX_LIBRERIE_V7_14.md`, ECO `00_Gestione_Progetto/ECO_INTEGRAZIONE_CAD_V7.14.md`, JSON `03_Verifiche/V7.14/RISULTATI_VERIFICHE_V7_14.json`.

**Prossima V7.15:** verificare con disegno manufacturer i due footprint SMA discordanti J9102/J9104, poi analizzare 70 via GND e 63 reti RX incomplete; ridurre i 43 errori ERC gerarchici, qualificare 15 interfacce MCU/AUX/RX ancora **OPEN/HOLD** e pin FPGA SG48 tuttora HOLD. Proseguire firmware, DSP, PLL, simulazioni, BOM e test. **Nessun Gerber, PCB completo, fabbricazione, PA/antenna o trasmissione RF autorizzati.**

**Criterio di merge:** aggiornare sorgenti KiCad/firmware/modelli, controllare CI specifica e integrità baseline; nessuna CI verde sui modelli autorizza da sola produzione, collaudi reali o emissioni RF. Mantenere tutti gli originali e il tag v7.0.

---

## ARCHIVIO V7.13 E PRECEDENTI

# PROTOCOLLO PERMANENTE MAIN — V7.13 CAD NATIVO, 10 NOVEMBRE 2026

- V7.13 **integrata in main**, [PR #13](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/13), commit di merge `81928a6fc36f6e3bb98c04338026a4ed2f78769d`. Ogni nuova chat deve verificare HEAD `main`, PR, Actions e tag storico `v7.0`; versione successiva prevale su questa nota.
- Progresso reale: schema RX standalone su **griglia 1,27mm/50mil**, 15 simboli+31 wire+31 labels rilocalizzati su copia V7.13, originale V7.12 intatto e PCB V7.12 non modificata. Prova `kicad-cli sch export netlist` **stesso multiset esaustivo di (net, ref, pin)** prima/dopo. RX ERC 46→0 off-grid e warning 76→30, RX error 0; root ERC 459→413, **43 errori persistenti**.
- Root schema a 7 fogli ancora elettricamente isolato; 15 interfacce MCU/AUX/RX OPEN/HOLD. RX `sym-lib-table`+`fp-lib-table` NON risolvono ancora 15+15 warning di libreria. PCB coupon RX **85 DRC +63 unconnected**, 70 vias dangling, 15 footprint warning. **Non ERC/DRC PASS globale**.
- CI PR #13 [run 42870757111](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42870757111), job 130021089653, log controllato: **186 Python PASS, 0 FAIL/SKIP**, export/ ERC/DRC KiCad nativo PASS solo per gates specifici; Icarus/Yosys non rieseguiti in questa revisione. Documenti correnti: `README.md`, `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, `Superstar3900_Rapporto_Tecnico_V7.13.md`, `01_Specifiche/V7.13/GRID_NETLIST_EQUIVALENCE_V7_13.md`.
- Prossima V7.14: librerie KiCad realmente configurate, footprint vendor, correggere DRC 70 vias dangling e63 unconnected con vere zone/piste e ritorni RF, poi 43 errori ERC root e confini power/MCU/RX qualificati. Proseguono DSP/firmware/simulazioni e relativi test.
- **NO FAB / NO TX:** nessun PCB completo, KiCad/ERC/DRC full green, Gerber, hardware RF misurato, DAC/FPGA/mixer/PA/antenna collegati o alimentati, nulla da trasmettere. Pinout Lattice SG48 ufficiale HOLD. Non scambiare successo CI per qualifica elettrica hardware.

---

# PROTOCOLLO CONTINUITÀ MAIN — V7.12 CAD NATIVO INTEGRATA (10 NOVEMBRE 2026)

- Revisione corrente su main a questa fotografia **V7.12**, PR [#12](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/12), commit merge `aad39c250fe626fa94424ff9ce2c08cb6b9ebcc8`. All'avvio di qualunque chat **verificare HEAD main, PR, tag, CI**; revisioni successive prevalgono. Il tag `v7.0` è storico preservato.
- KiCad CLI 9 nativo confermato: `sch export netlist` V7.10 vs V7.12 su **7 fogli /132 istanze /99 reti**: **11 designatori duplicati e14 extras→ZERO**. MCU 46 ref +6000, RX 15 ref +9000; nuovi file nativi editabili `.kicad_sch` e `.kicad_pcb`, originali inalterati. Tutti i confini tra moduli ancora OPEN/HOLD.
- Bug KiCad standalone RX V5.2: testo grafico con LF non escapato + UUID mancante; copia V7.12 corretta, nativo `sch erc` ora **exit0, 0 errori/76 warning**. Root **43 errori+416 warning**; PCB coupon **85 DRC violazioni+63 unconnected** (70 dangling via,15 footprint warnings); *NON* dichiarare ERC/DRC globalmente superati.
- CI finale [run 42866103256](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42866103256), job 130004727547: **176 Python PASS/0 FAIL/0 SKIP**, native netlist/ ERC/DRC inventory checks PASS, log verificato. Icarus/Yosys non rieseguiti in questa revisione. Report `Superstar3900_Rapporto_Tecnico_V7.12.md`, spec `01_Specifiche/V7.12/RIANNOTAZIONE_NATIVE_RX_MCU_V7_12.md`, ECO `00_Gestione_Progetto/ECO_INTEGRAZIONE_CAD_V7.12.md`.
- **Prossima V7.13:** correggere off-grid/footprint/symbol RX con KiCad, affrontare DRC coupon via dangling e unconnected, ridurre ERC root e qualificare reti MCU/power/RX una per volta, proseguire firmware, DSP, modelli numerici, BOM e prove automatiche. Pinout Lattice SG48 originale ancora HOLD.
- **NO FAB / NO TX.** Nessun PCB dell'intero apparato, no Gerber, no DAC/FPGA/PA o RF TX connessi/alimentati, nessuna validazione hardware/EMC o emissioni. Ogni CI verde è diagnosi, non autorizzazione fabbricazione; conservare storici.

---

# PROTOCOLLO CONTINUITÀ MAIN — V7.11 CAD NATIVO, 10 NOVEMBRE 2026

- Stato su `main` alla data: **V7.11 integrata** con [PR #11](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/11), merge `028c3a5f8d9f638d423be251a7a06336a961ead7`. Verificare HEAD/PR/CI in ogni nuova chat; eventuale versione successiva prevale. `v7.0` tag storico preservato.
- Correzione KiCad autentica sulla COPIA V7.11 del coupon RX 50Ω V5.2: sei vie GND via-in-pad da **Øforo 0,25→0,30mm**, Ørame 0,55→0,60mm. `kicad-cli pcb drc` originale **91 DRC +63 unconnected**; V7.11 **85 DRC +63 unconnected**. Sei `drill_out_of_range` risolti, ma **70 via_dangling, 15 library warnings e 63 missing connections** ancora BLOCCANTI. `fp-lib-table` creata, avvisi librerie ancora presenti: non dichiarare riparata portabilità.
- Esecuzione reale [GitHub Actions run 42856926563](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42856926563), job 129972377360: **8 V7.11 +12 V7.10 +143 V7.1–V7.9 = 163 Python PASS**, 0 FAIL/SKIP, DRC **miglioramento** PASS, ma DRC complessivo **NON PASS**. Icarus e Yosys nuovi non eseguiti in questa CI.
- Root KiCad V7.10 ancora non interconnesso: **132 istanze**, **11 refs duplicati**, **43 ERC errors+416 warnings**, schema RX standalone exit3, 15 interfacce AUX/MCU/RX ancora OPEN/HOLD. Nessun PCB dell'intera radio, nessun Gerber o release per produttore.
- Documentazione corrente `README.md`, `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, `Superstar3900_Rapporto_Tecnico_V7.11.md`, `01_Specifiche/V7.11/PIANO_CORREZIONI_KICAD_RX_V7.11.md`, `00_Gestione_Progetto/ECO_INTEGRAZIONE_CAD_V7.11.md`; storico V7.0–V7.10 conservato.
- **Prossima V7.12:** riparare il caricamento RX standalone e annotare refs duplicati, qualificare libs e GND, eliminare via dangling/unconnected con vere connessioni, ridurre ERC native, qualificare interfacce AUX/MCU/RX per vero PCB integrato. Test DSP/firmware/PLL/RTL paralleli indispensabili.
- **NO FAB / NO TX:** nessun PA/antenna, FPGA/DAC TX alimentati o collegati, nessuna KiCad ERC/DRC full pass, misure RF/EMC o fabbricazione autorizzata. Il colore verde della CI non equivale a progetto elettrico completo.

---

# PROTOCOLLO PERMANENTE — V7.10 KIcad NATIVO INTEGRATO SU MAIN, 10 NOVEMBRE 2026

- Revisione integrata più recente al momento di questo aggiornamento: **V7.10**, [PR #10](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/10), merge `8a18c12df4455265db8414784587f4d82a1f82ae`; il tag `v7.0` rimane storico. Nuove chat devono **verificare HEAD main/PR/CI**, perché una revisione successiva prevale su questa fotografia.
- Nuovo **schema KiCad gerarchico nativo e riutilizzabile** `04_KiCad/Assemblaggio_RX_Power_V7.10_NOT_FOR_FAB/S3900E_RX_POWER_INTEGRATION_V7_10_NOT_FOR_FAB.kicad_sch`: riferisce AUX V1.5 (con 3 sottopagine), MCU/CODEC V2.1 e coupon RX V5.2; **7 pagine, 132 istanze, 99 nets esportati**, ma **11 designatori duplicati** e **15 interfacce tra blocchi OPEN/HOLD**, senza cablaggio reale. Non esiste PCB completo della radio.
- **AUDIT nativo KiCad 9.0.8**: root 43 ERC errors / 416 warnings; AUX 22/248, MCU 18/92; RX schema standalone exit3 (non caricabile); RX coupon PCB DRC **91 violations, altre 63 unconnected**. Non dichiarare KiCad/ERC/DRC risolti. Il root esporta la netlist con warning di annotazione. La prima ipotesi di fix `sheet_instances` su RX standalone era falsa ed è stata annullata.
- **Test regressivi non abbandonati**: 12 unit test V7.10 +143 unit test V7.1–V7.9 = **155 PASS /0 FAIL/0 SKIP**; [GitHub Actions run 42855337776](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42855337776) successo **solo per audit/tracciabilità**, con CAD netlist e rapporti artifact, non significa ERC/DRC pass.
- **Prossima V7.11:** correggere lo schema RX standalone, consolidare annotazione e librerie footprint, ridurre 63 missing nets e difetti via, qualificare le alimentazioni e le interfacce SPI/RX. Creare vero circuito KiCad integrato e PCB solo dopo link/netlist verificati, senza perdere sviluppo firmware/modelli, report rigoroso.
- Rapporti correnti: `README.md`, `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, `Superstar3900_Rapporto_Tecnico_V7.10.md`, `01_Specifiche/V7.10/PIANO_CAD_INTEGRAZIONE_RX_POWER_V7.10.md`, `00_Gestione_Progetto/ECO_INTEGRAZIONE_CAD_V7.10.md`, audit JSON in `03_Verifiche/V7.10`.
- **NO FAB / NO TX**: tutte le sezioni TX DNP, nessuna uscita PA/antenna, nessun Gerber o release PCB. SG48 Lattice originale XLSX pinout resta HOLD. Ogni esecuzione e violazione deve essere registrata con esito PASS/FAIL/NOT_RUN e nessun falso claim.

---

# PROTOCOLLO CONTINUITÀ MAIN — V7.9 INTEGRATA, 10 NOVEMBRE 2026

- Revisione più recente al momento di questa annotazione: **V7.9 su `main`**, merge [PR #9](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/9) commit `38b9828728b02581bf24c070401dd70782051dbd`. L'HEAD `main` va sempre verificato prima di sviluppare: se maggiore, questo documento è solo archivio. Tag storico `v7.0` non alterato.
- **Verifiche:** GitHub Actions [run 42848254217](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42848254217), job 129941518720: **17 Python V7.9 + 126 regressioni V7.1–V7.8 = 143 PASS, 0 FAIL/0 SKIP**, **4 testbench Icarus PASS**, Yosys sintesi generica V7.9 PASS. Log reale controllato; verifica baseline RX post-merge da controllare sul commit definitivo.
- V7.9 corregge heartbeat V7.8 troppo veloce a 32kHz: nuovo /307200 dal 30.72MHz master, 100 transizioni/s, WDI falling ogni 20ms. TI TPS3430WDRCR finestra vendor lower max2.22ms upper min23.375ms; pin 1..10 e pad verificati da datasheet TI, **ancora DNP/non alimentati**. WDO open drain active LOW ≠ DAC900 PD active HIGH e reset non è latch, necessarie protezioni elettriche indipendenti a rail=0. Oscillatore secondario Abracon ASFLK-32.768KHZ-LJT è DNP senza pinout sul PCB.
- Screening F7401 con Coilcraft MSS1260T-472MLD 4.7µH e MS590PNB183MSZ 18µH: SRF vendor tip/min, Q **assunto**, risultato solo ABCD matematico (~0.235dB IF2 e ~88.7dB immagini), non DAC900 I/V/PCB/EMC. BOM **11 DNP/OPEN**, netlist **15 terminali DNP/OPEN**. Nessun file di progettazione approva la TX.
- Originale XLSX Lattice SG48 (document_id=51971) non ancora recuperato/confrontato: **pin-plan V7.6 / PCF HOLD**, niente FPGA pin-mapping o PNR/STA approvati. Storico V7.0–V7.8 conservato.
- Documenti correnti: `README.md`, `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, `Superstar3900_Rapporto_Tecnico_V7.9.md`, `01_Specifiche/V7.9/ARCHITETTURA_HEARTBEAT_WATCHDOG_SRF_V7.9.md`, `00_Gestione_Progetto/ECO_INTEGRAZIONE_V7.9.md`.
- **Prossima V7.10**: pinout originale Lattice autenticato, schemi DNP di supervisor/PD e isolamento RF normally-open con fault-mode rail=0 e componenti qualificati, filtro con Q/SRF/cap reali e DAC I/V, DSP fixed-point; integrare in main dopo test CI, preservare report storici.
- **PROIBITO dichiarare FAB o TX:** tutto l'hardware TX DNP, nessuna trasmissione o scheda, test RF/EMC, KiCad/ERC/DRC, alimentazioni fisiche o normative non eseguiti. I gate software/RTL non sostituiscono interblocchi hardware.

---

# PROTOCOLLO MAIN / CONTINUITÀ — V7.8 INTEGRATA, 10 NOVEMBRE 2026

- Versione integrata sulla main al momento: **V7.8**, [PR #8](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/8), commit merge `75027e768bef2b5a00f69d1675e462b8c35b1366`. Controllare l'HEAD `main` e le CI in ogni nuova chat: revisioni successive hanno priorità; il tag `v7.0` è baseline storica.
- **Verifiche:** 20 V7.8 + 14 V7.7 + 15 V7.6 + 22 V7.5 + 21 V7.4 + 15 V7.3 + 11 V7.2 + 8 V7.1 = **126 Python PASS, 0 FAIL/SKIP**, 3 bench Icarus e 2 `Yosys synth; check -assert` generici PASS, [run 42842592233](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42842592233), log verificato. Primo FAIL V7.8 corretto aggiungendo guardia normalized unity prima headroom. Verifiche dopo merge vanno controllate separatamente.
- Nuovi blocchi: rilevatore master clock stop su **secondo dominio di riferimento virtuale**; acquisizione XLSX Lattice originale 51971 **fallita**, pinout/PCF SG48 resta HOLD; tool di comparazione ZIP/XML testato con sintetici, non vendor; test DSP non periodico a 10bit con SNR errore numerica ~49,392dB e overrange fail-closed; candidato TI TPS3840PH30DBVR solo DNP, non interblocco fisico.
- Archivi autorevoli `README.md`, `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, `Superstar3900_Rapporto_Tecnico_V7.8.md`, `01_Specifiche/V7.8/ARCHITETTURA_WATCHDOG_PINOUT_DSP_V7.8.md`. Distinta V7.8 8 voci DNP/OPEN, netlist 10 terminali DNP/OPEN; precedente TX DNP immutato.
- **Prossima V7.9:** ottenimento originale vendor, approvazione documentale dei pad SG48, clock watchdog e secondo reference fisico candidati con verifiche su datasheet, power sequencing/PD supervision anche rail=0, filtro Q/SRF con MPN, nessun PNR e nessun TX finché gate aperti.
- Protocollo permanente: sviluppare concretamente su branch e CI, rapporti PASS/FAIL/NON ESEGUITO, poi integrare in `main` preservando storico; NON inventare nomi pin/hardware/risultati. **NO FAB / NO TX**. FPGA/DAC/mixer/PA/antenna TX fisicamente assenti, non alimentati e non instradati.

---

# PROTOCOLLO MAIN / CONTINUITÀ — V7.7 INTEGRATA, 10 NOVEMBRE 2026

- Fotografia di stato: **V7.7 su `main`**, merge PR #7 `e68743f5474be26732cfb6cd4ad9953404a2935c`. Il tag `v7.0` rimane baseline storica, non la versione integrata. Nelle nuove chat controllare **prima di tutto HEAD `main`, PR e workflow**: revisioni successive prevalgono su questa intestazione e sull'archivio.
- V7.7 comprende `v77_offline_top` di diagnostica, gate TX/PD/analogico zero costante, 2 bench RTL Icarus e sintesi Yosys **generica** (non implementazione iCE40), più modello numerico DAC10bit multitone/gradino e FMEA requisiti. **106 Python PASS / 0 FAIL / 0 SKIP**, 2 bench PASS, Yosys PASS nel run [42819963860](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42819963860); ultimo run PR ancora in installazione al merge, quindi non dichiararne un esito inesistente. Gli ultimi commit sul branch dopo il run avevano modificato soltanto documentazione.
- Stato pinout SG48 **HOLD**: XLSX originale Lattice `iCE40UP5K Pinout`, document_id `51971`, è pubblicato dal produttore, ma non è stato scaricato/verificato nel contenuto. Nessun PCF o pad può essere approvato per PCB, no nextpnr/STA, bitstream, supervisione elettrica, clock e DAC fisico.
- **Prossima V7.8:** verifica byte/righe XLSX vendor e associazioni per banca, poi qualifica dei constraints e PNR/STA, monitor clock indipendente e PD hardwired fail-closed, simulazione single fault, filtri analogici Q/SRF e DAC con dati vendor. Nuove funzioni restano DNP/OPEN senza TX.
- L'ultima documentazione tecnica è `Superstar3900_Rapporto_Tecnico_V7.7.md`, `03_Verifiche/V7.7/RAPPORTO_TECNICO_V7.7.md`, `01_Specifiche/V7.7/ARCHITETTURA_RTL_QUANTIZZAZIONE_V7.7.md`, `README.md` e `RIPRENDI_IN_UNA_NUOVA_CHAT.md`.
- Protocollo invariabile: sviluppare davvero con specifiche/BOM/netlist/modelli/test e rapporto con **PASS/FAIL/SKIP/NON ESEGUITO**, verificare CI, integrare revisioni coerenti in `main`, preservare storia; mai confondere simulazione con hardware qualificato. **NO FAB / NO TX**, mixer e finale RF fisicamente scollegati, nessun PCB/TX autorizzato.

---

# PROTOCOLLO DI CONTINUITA — V7.6 INTEGRATA SU MAIN, 10 NOVEMBRE 2026

- Revisione più recente integrata al momento di questo aggiornamento: **V7.6**, [PR #6](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/6), merge `8309d11e1a06473119aafcb71a0cbe2aa0171e61`. Verificare SEMPRE HEAD `main` in ogni nuova chat: qualsiasi versione successiva prevale su questa fotografia e sui tag storici.
- CI funzionale modello **Icarus RTL bench PASS** (clock-enable /8,/640, FIFO 16x10bit e fault latched) + **15 Python V7.6 + 22 V7.5 + 21 V7.4 + 15 V7.3 + 11 V7.2 + 8 V7.1 = 92 PASS, 0 FAIL, 0 SKIP**, [GitHub Actions run 42814827870](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42814827870), log verificato; nulla di fisico testato.
- SG48 `iCE40UP5K-SG48I`: proposta di 48 pin + pad massa e PCF **HOLD**, numerazione ottenuta da copia SECONDARIA e solo conteggi incrociati con Lattice primario; verifica contro documento XLSX ufficiale Lattice ancora bloccante. Nessuna programmazione/HDL synthesis, place-route o mappa pin elettrica approvata.
- Ultimi documenti: `README.md`, `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, `Superstar3900_Rapporto_Tecnico_V7.6.md`, `01_Specifiche/V7.6/ARCHITETTURA_RTL_PINPLAN_PROTEZIONI_V7.6.md`. BOM V7.6 5 DNP, netlist 8 OPEN/DNP. Lo storico v7.0–V7.5 rimane preservato.
- **Prossima V7.7:** confronto vendor XLSX pinout, top FPGA e tempi/output di clock, monitor clock esterno, POR/PD indipendente, multitone/gradino con DAC quantizzato e filtro/Q/SRF; conservare NO FAB / NO TX anche se i test digitali riescono. Non progettare PA/antenna TX prima di interblocchi fisici indipendenti e validazione normativa.
- Regola permanente invariata: branch temporanei per sviluppo/test, poi merge nella main più recente dopo verifiche reali; report con PASS/FAIL/SKIP/NON ESEGUITO. **Non dichiarare KiCad/ERC/DRC, SPICE vendor, EMC, hardware, fabbricazione o TX non eseguiti.**

---

# AGGIORNAMENTO PERMANENTE — V7.5 INTEGRATA SU MAIN (10 NOVEMBRE 2026)

- La revisione progettuale integrata più recente alla data di queste note è **V7.5**, [PR #5](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/5), merge `a5ef405f9500c114e8a4d56d7f9b17ba5a89caf1`. Su nuove chat bisogna verificare l'HEAD `main`: una revisione successiva prevale su questo stato storico e sui tag precedenti.
- Verifiche software registrate: **22 test V7.5 + 21 V7.4 + 15 V7.3 + 11 V7.2 + 8 V7.1 = 77 PASS, 0 FAIL / 0 SKIP**, [GitHub Actions 42810514397](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42810514397) (log esaminato), oltre all'integrità della baseline v7.0 quando eseguita. Nessuna misura fisica.
- Nuovo sviluppo V7.5: clock unico 30,72MHz, oscillatore Abracon ASDMB con pin ufficiali, ponte Lattice iCE40UP5K **senza mappatura pin e senza RTL**, interpolatore DSP 5×4×4 a budget teorico ridotto; tutti i componenti e i ponti TX DNP, RF/PA/antenna assenti. Documenti principali: README.md, RIPRENDI_IN_UNA_NUOVA_CHAT.md e Superstar3900_Rapporto_Tecnico_V7.5.md.
- **Prossima V7.6:** pinout e constraints FPGA, modello HDL simulabile, supervisione hardware indipendente PD/rail e guasti, spettri multitonali/transienti e filtri con dati Q/SRF/MPN. L'intero circuito TX resta scollegato: **NO FAB / NO TX**.
- Lo storico V7.0–V7.4 e le vecchie istruzioni di seguito sono **archivio conservato**. Il vecchio tag `v7.0` non equivale allo stato attuale `main`. Mantenere test riproducibili, dichiarare sempre NON ESEGUITO per KiCad/ERC/DRC, RTL reale, misura hardware, EMC o fabbricazione non realizzati; continuare su feature branch durante CI e unire in main una revisione candidata coerente.

---

# AGGIORNAMENTO PROTOCOLLO — V7.4 IN MAIN, 10 NOVEMBRE 2026

- Revisione più recente integrata al momento di questo commit: **V7.4** tramite [PR #4](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/4), merge f92220b0e789673cb927f4e21a72ed4d16b92faf, su **main**. È sviluppo sperimentale software/documentale **NO FAB / NO TX**, non collaudo fisico.
- CI GitHub Actions V7.4 [run 42807026035](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42807026035) conclusa con successo: **21 test nuovi V7.4 + 15 V7.3 + 11 V7.2 + 8 V7.1 = 55 test PASS, 0 FAIL/0 SKIP**. I/O analogici, clock e DAC reali NON provati.
- Rapporti correnti: Superstar3900_Rapporto_Tecnico_V7.4.md, 03_Verifiche/V7.4/RAPPORTO_TECNICO_V7.4.md, README.md e RIPRENDI_IN_UNA_NUOVA_CHAT.md. Le istruzioni precedenti sono archivio. La prima fonte di verità è SEMPRE l'ultimo commit presente su main.
- **Prossima revisione progettuale V7.5:** selezione MPN/pin clock sincronizzato e bridge, analisi power/PD indipendente, filtro DAC con modello e componenti SRF/Q, verifiche realtime e riduzione complessità DSP. Tutti i dispositivi TX e output verso PA/antenna DNP/non instradati. Conservare storia e utilizzare PR temporanee poi integrare in main dopo CI.
- Il tag storico v7.0 rimane immutato. **Non confondere** il protocollo/versione software con qualifica KiCad, cablaggio, schede o autorizzazione TX.

---

# AGGIORNAMENTO PROTOCOLLO — V7.3 INTEGRATA IN MAIN · 10 NOVEMBRE 2026

- `main` contiene **V7.3**, merge PR #3 `9f64126f5490d34921da726d41354518b34be9a7`; 34/34 test software GitHub Actions PASS ([run 42803248288](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42803248288)). Modello causal/stateful, DAC900E candidato, F7401 matematica. **NO FAB / NO TX**.
- **Prossima revisione V7.4:** dominio clock/FPGA/dati di DAC e I/V/filtri con valori/MPN verificati e modelli; continuare in `main` dopo test, preservando tutto lo storico; non dichiarare la catena TX operativa.
- In ogni nuova chat il primo controllo è l'ultimo `main`, non il tag più recente né la memoria del testo storico. Per lo stato tecnico consultare `README.md`, `RIPRENDI_IN_UNA_NUOVA_CHAT.md` e il rapporto tecnico più recente; in presenza di nuovo commit prevale quel nuovo stato.
- La procedura e gli obblighi di sicurezza contenuti di seguito rimangono integralmente validi; gli stati V7.2/V7.1 in archivio restano informazioni storiche.

---

# Aggiornamento stato protocollo — 10 novembre 2026, V7.2 in MAIN

- **Ultima revisione integrata al momento di questo aggiornamento: V7.2**, PR #2, merge `faab93ea00d64d43b3d4977a5a43f512977043a9`. Per stabilire cosa fare in futuro **verificare sempre HEAD `main` prima di leggere questa fotografia storica**.
- **CI V7.2:** 11 test software V7.2 + 8 test di regressione V7.1, tutti PASS. GitHub Actions run 42794577497; `README.md`, `RIPRENDI_IN_UNA_NUOVA_CHAT.md` e `Superstar3900_Rapporto_Tecnico_V7.2.md` sono gli accessi principali.
- **Prossimo progetto V7.3:** DAC/clock e filtro 455kHz candidati con datasheet, streaming DSP causale, spettro offline, mantenendo DNP tutti i TX, NO FAB/NO TX. L'ultima baseline taggata v7.0 non è equivalente alla revisione integrata.
- **Conservazione:** la storia V7.0/V7.1 e lo stato documentale precedente restano disponibili. Le regole permanenti del protocollo sotto questa intestazione non cambiano.

---

# Protocollo permanente di ripresa — Superstar 3900 SMD Evolution

**Decisione concordata il 10 novembre 2026. Fonte di verità: repository privato `jd3485/Superstar3900-SMD-Evolution`.**

## Regola di lavoro
1. **`main` contiene l'ultima revisione progettuale integrata**, anche se è ancora una revisione sperimentale NON fabbricabile. Non confondere "integrata" con "validata su hardware".
2. Per la revisione successiva: controllare il commit `main`, i tag, le PR aperte e le ultime esecuzioni CI, poi leggere `README.md`, `RIPRENDI_IN_UNA_NUOVA_CHAT.md` e il rapporto tecnico dell'ultima revisione. L'ultimo tag **non** prevale su commit successivi di `main`.
3. Continuare con sviluppo progressivo della radio: specifiche circuitali candidate, componenti e BOM, netlist pin-to-net, interfacce MCU/firmware se pertinenti, calcoli/modelli riproducibili e verifiche incrementali. **Non** trasformare la progettazione in sole revisioni di audit senza avanzamento funzionale.
4. È lecito usare un branch e una pull request per isolare lo sviluppo durante i test, ma **quando una revisione progettuale è coerente e i test dichiarati sono verificati**, integrarla in `main` senza lasciarla come stato finale separato. Se ci sono test falliti o bloccanti, non nasconderli né forzare un merge: correggere o segnalare.
5. Conservare integralmente la storia Git, i sorgenti precedenti e i documenti gestionali storici. Creare commit riconoscibili, aggiornare i documenti di ripresa e i rapporti. Quando opportuno e supportato dagli strumenti, creare un tag della revisione consolidata; **il tag `v7.0` è immutabile**. Il `MANIFEST_SHA256_V7.0.csv` si confronta **solo** con la baseline del tag `v7.0`, mai con un `main` successivo.
6. Ogni rapporto deve distinguere chiaramente **PASS**, **FAIL**, **SKIP**, **NON ESEGUITO**; dichiarare il tipo di verifica e i limiti, non trasformare modelli numerici in misure fisiche. Non dichiarare mai KiCad ERC/DRC, SPICE vendor, EMC, hardware o test non realmente eseguiti.
7. **SICUREZZA INVARIABILE: NO FAB / NO TX.** Fino a completa progettazione, analisi normativa, controllo fisico indipendente e collaudo reale, non collegare PA/finale/antenna TX e non abilitare emissione RF, nemmeno per prove. Interblocchi V6.2 e componenti DNP rimangono aperti.
8. In ogni nuova chat, non presupporre di ricordare il contesto precedente: recuperare lo stato **dal repository**. Non serve conservare lo ZIP o incollare migliaia di righe di storia se GitHub è connesso e leggibile.

## Stato di partenza al 10 novembre 2026
- `main` ha integrato la **V7.1**, mediante PR #1, merge `4c3585cc90de86860f14c7097bc50e5caf79349e`. V7.1 è **candidata**, non collaudata; righe BOM/NET TX DNP e uscita RF non instradata.
- `v7.0` è il tag della baseline tecnica precedente, puntato alla commit `b4242f58b75ecaea7093fe960e63c96c5a43d87a`.
- GitHub Actions V7.1 ha superato **8/8 test software** su checkout integrale; nessun KiCad/DRC/ERC/hardware è stato validato.
- **Prossimo obiettivo previsto:** V7.2 generatore IF2 455kHz/DUC, modulazione audio multitonale AM/FM/SSB/CW e criteri per filtri IF/RF, sempre con TX non connessa.
- Se `main` presenta una revisione successiva a queste note, prevale il **nuovo commit e relativo rapporto tecnico**, non questa fotografia storica.

## Formula di ripresa minima per nuove conversazioni
> Riprendi Superstar 3900 SMD Evolution dal repository GitHub privato `jd3485/Superstar3900-SMD-Evolution`. Leggi `README.md`, `RIPRENDI_IN_UNA_NUOVA_CHAT.md` e `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`; verifica la versione più recente su `main`, tag e CI, e continua la successiva revisione incrementale. Dopo i test integra in `main`, preserva lo storico, **NO FAB / NO TX**.
