# V7.67 — BUCK 5V ingresso/EN griglia 100mil; F200/eFuse corrente di carico e scenari

13 novembre 2026, V7.66 integrata baseline: 140 componenti /103 reti, ERC 28 errori +205 warning, 326 Python test PASS, F200 fusibile 045101.5MRL 1.5A REVIEW ONLY, R203=8.2kΩ TPS26600 limite nominale ~1.463A.

## Vera modifica CAD (quattro componenti)

Nuovo AUX `04_KiCad/Gerarchico_Alimentazioni_V7.67_BUCK_VIN_EN_GRID_REVIEW_NOT_FOR_FAB/02_BUCK_5V.kicad_sch`: C100 filtro ingresso 10µF/35V da (52,85)→(50.8,83.82), C101 bypass ingresso 100nF/50V da (76,85)→(76.2,83.82), R103 buck EN 510k 5% da (52,132)→(50.8,132.08), R104 EN 105k 1% da (76,132)→(76.2,132.08); tutte coordinate in mm. Mosse con loro **otto label** dei pin, ai nodi `BUCK_VIN_PROTECTED`, `GND_MAIN` e `BUCK_EN`, senza cambiare reti. Esattamente **24 atomi sorgente** controllati (quattro origini, dodici posizioni proprietà, otto label). Terminali sulla griglia da 2.54mm e valori/footprint/MPN/collegamenti invariati. Master `04_KiCad/Assemblaggio_RX_Power_V7.67_BUCK_VIN_EN_GRID_REVIEW_NOT_FOR_FAB/` cambia solo path AUX, altri sei fogli e tabelle/versioni libreria identici. NO FAB.

## Lettura corretta dei datasheet: non confondere limiti

**Littelfuse 451/453** [datasheet ufficiale](https://www.littelfuse.com/~/media/electronics/datasheets/fuses/littelfuse_fuse_451_453_datasheet.pdf.pdf) (revision GD 2025-12-01, pagine 1-3): per la variante **1.5A** in tabella: resistenza fredda nominale **0.063Ω**, nominal melting **I²t 0.853 A²s** (dato caratterizzazione a 8ms, NON energia verificata di avviamento), prova **100% In: almeno 4 ore**, **200% In (3A): ≤5 secondi**. La curva tempo-corrente è media, NON un limite di protezione garantito a corrente arbitraria. Derating 25% standard continuo ⇒ **1.125A di riferimento**, più rerating ambientale non calcolato. **È errato dedurre che F200 scatti a 1.125A**. Il limite TPS26600 R203 **1.463A nominale** è un comportamento di protezione su guasto, NON un carico continuo; la semplice disuguaglianza **1.463 > 1.125** non prova incompatibilità, se il carico continuo è inferiore. Tuttavia sotto corto/inrush/temperatura la coppia non è qualificata.

**TI TPS54202** [Rev. C, febbraio 2026](https://www.ti.com/lit/ds/symlink/tps54202.pdf): buck ingresso 4.5–28V, uscita continua **massimo dichiarato 2A**, soft-start interna **5ms** tipica e modalità OCP/hiccup. Per **corrente media DC teorica di ingresso** a 5V, esclusi altre perdite e ricariche condensatori: `Iin≈(5V×Iout)/(VIN×η)`. `η` qui è un'**ipotesi**, non una curva garantita dal costruttore a 13.8V e con questo layout: effettuati 60 scenari (VIN 10.2545/13.8/17.0524V × η 75/85/90/95% × Iout 0.25/0.5/1/1.5/2A).
- Caso 13.8V, η ipotetico 85%, 5V/2A: **0.8525A medi**; inferiore al criterio F200 1.125A continuo, quindi in tale caso NON emerge un conflitto di regime.
- Caso VIN 10.2545V, η ipotetico 75%, 5V/2A: **1.3004A medi**; superiore al riferimento 1.125A; in tale condizione il requisito non è dimostrato.
- Alla stessa VIN/η, limitazione del carico sostenibile dal criterio continuo 1.125A equivale a **~1.730A a 5V**. È solo un inviluppo teorico: **non** garantisce 1.73A del buck in condizioni reali.
- Le tensioni 10.2545 e 17.0524V sono scenari di soglie eFuse calcolati V7.66 ignorando pin leakage e transitori; **non** tutte condizioni necessariamente di funzionamento stazionario.

**Per chiudere il rischio** servono: vero massimo carico misurato 5V incluse sei LDO e relative correnti; η del circuito (VIN, temperatura e carico); temperatura fusibile e rerating; picco ingresso e I²t durante power-on, soft-start e recovery manuale; curve di intervento F200 vs corrente nel tempo in ogni guasto, tolleranze TPS26600, limiti VIN sorgente 13.8V, ripple e capacità C100/C103/C104 effettive sotto polarizzazione. Il dato 5ms di soft-start non permette di inferire un I²t senza il profilo reale. NON cambiare F200 o R203 senza tali misure.

## Verifiche native

`03_Verifiche/V7.67/test_buck_four_vin_enable_grid_f200_envelope_native_v767.py`: 20 nuovi test: **KiCad9 CLI** sette fogli netlist/ERC V7.66 ↔ V7.67, 140 componenti/103 reti e **intera mappa pin/rete identica**, controlli reti C100/C101 e partitore EN, U200 RTN/GND e SW200 SHDN; ERC invariati salvo rimozione attesa **esattamente quattro** `endpoint_off_grid` C100 C101 R103 R104: **28 errori /205→201 warning se CI li conferma**. Nessun waiver, nessun DRC PCB inventato. Report 60 scenari JSON numerico e HOLD fisici in output-ci.

[Issue #57](https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/57) ancora OPEN; 15 crossmodule OPEN/HOLD, SG48/Y1 pin10 HOLD, D200 TVS DNP, SW200 meccanica/ESD/reset fault non misurati, 28 ERC reali, nessuna PCB unificata e nessun DRC globale. **NO FAB / NO GERBER / NO PCBWAY / NO TX**.
