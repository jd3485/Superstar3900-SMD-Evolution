# SUPERSTAR 3900 SMD EVOLUTION — RAPPORTO TECNICO CAD V7.12

**10 novembre 2026. Schema RX standalone e riannotazione di sette fogli KiCad reali. NO FAB / NO TX.** Il progetto prosegue dalla V7.11 integrata su main. Tutti i vecchi file e le regressioni firmware/DSP rimangono preservati.

## 1. Risultati CAD veramente realizzati

**File KiCad nativi modificabili**, tutti su **copie versionate**: `04_KiCad/Assemblaggio_RX_Power_V7.12_REANNOTATED_NOT_FOR_FAB/S3900E_RX_POWER_INTEGRATION_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch` (root di integrazione), foglio MCU `04_KiCad/Modulo_MCU_CODEC_V7.12_REANNOTATED_NOT_FOR_FAB/`, foglio RX e PCB con refs allineate `04_KiCad/Modulo_RX_Test_50ohm_V7.12_SCHEMATIC_REPAIR_NOT_FOR_FAB/`. I tre blocchi AUX/MCU/RX sono ancora **elettricamente isolati**: non unire alimentazioni, IF, bus SPI o terra non verificati; nessun blocco TX inserito.

La V7.10 aveva **132 istanze componenti**, 7 fogli, 99 nets, **11 reference designators ambigui** corrispondenti a 14 istanze in eccesso. La V7.12 conserva gli stessi 132/7/99 ed elimina le 11 ambiguità (0 extras) mediante vera riannotazione nella proprietà simbolo e nel relativo `instances/reference`:
- **MCU/codec**: 46 riferimenti ridenominati con offset 6000; il foglio V2.1 originale non è modificato.
- **RX**: 15 riferimenti ridenominati con offset 9000, *anche* nella copia `.kicad_pcb`, così riferimenti di schema e board corrispondono.
- **AUX power**: fogli originali immutati. Nessuna modifica alle tracce, net, valori o componenti fisici.

La verifica `kicad-cli sch export netlist` è stata **realmente eseguita su entrambi i root** e confrontata da `03_Verifiche/V7.12/verifica_netlist_annotazione_v712.py`. **PASS** solo per consistenza delle refs; non è uno schema elettrico completo.

## 2. Riparazione verificata del caricamento standalone RX

Il vero schema RX V5.2 era utilizzabile come foglio gerarchico, ma come root standalone `kicad-cli sch erc` e `sch export netlist` fallivano `exit3: Failed to load schematic`. La causa è stata isolata con `03_Verifiche/V7.12/probe_rx_schematic_parser_v712.py`: librerie e piazzamenti di **15 simboli, 31 wire e 31 label** venivano letti, mentre la nota grafica multiriga rendeva il file illeggibile.

La nota originale conteneva a capo **LF reali dentro una stringa quoted S-expression** e non aveva UUID; la copia V7.12 aggiunge UUID, converte gli a capo in sequenze `\n` letterali e completa `sheet_instances`/`embedded_fonts`. La procedura usa i requisiti di serializzazione del formato KiCad, non rimuove simboli, pin, connessioni o note.

**Nuova verifica nativa KiCad 9:** `sch erc` su RX V7.12 standalone **exit0, report generato**. Il report segnala **0 errori e 76 warning**, suddivisi in **46 `endpoint_off_grid`, 15 `lib_symbol_issues`, 15 `footprint_link_issues`**. **Non significa ERC pulito**. Anche il `sch export netlist` sulla copia di diagnostica con testo ora carica. L'originale V5.2 è conservato esattamente come archivio.

Fonte KiCad per escaped newline: https://dev-docs.kicad.org/en/components/sexpr/ .

## 3. ERC dell'assemblaggio e DRC PCB RX restano BLOCCANTI

| Verifica | Dato reale | Giudizio |
|---|---|---|
| Netlist 7-sheet nuova | 132 componenti, 99 nets, **0 ref ripetuti** | **PASS annotazione** |
| Schema RX standalone | Parser `exit0`, **0 errori ERC /76 warning** | **PASS caricamento, ERC non pulito** |
| Schema root V7.12 | **43 errori ERC +416 warning = 459** | **ERC NON PASS** |
| PCB RX V7.12 | **85 DRC violazioni**, **63 unconnected** | **DRC NON PASS** |
| Via `drill_out_of_range` | **0** (correzioni V7.11 conservate) | **PASS solo per foro** |
| Via dangling / footprint | **70 / 15** | Da correggere |
| Verifica hardware/RF | **NON ESEGUITA** | Nessuna FAB/TX |

La versione V7.12 non crea PCB dell'intera radio e non tenta alcun routing non qualificato; il PCB rimane il coupon di test RX 50Ω. I warning di footprint e le vias dangling non sono soppressi e i 15 contratti power/MCU/RX sono ancora OPEN/HOLD. Il pinout iCE40 SG48 resta HOLD per mancata verifica XLSX Lattice originale.

## 4. Regressioni eseguite

Workflow `.github/workflows/v712_kicad_native_annotation.yml`, con **KiCad CLI 9.0.8** su GitHub Actions: netlist vecchia/nuova, `sch erc` root e RX standalone, `pcb drc` del coupon, parser probe, confronti JSON con gate automatici. La CI su codice verificato è [run 42865217281](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42865217281), job 130001625196, **conclusione success**. Rapporto nativo `integration_v712_reannotated.net`, `v712_hierarchy_erc.rpt`, `v712_rx_standalone_erc.rpt`, `v712_rx_reannotated_pcb_drc.rpt` e JSON sono caricati come artifact del run, non Gerber.

Sono eseguiti **13 nuovi test Python V7.12**, **8 V7.11**, **12 V7.10**, **143 V7.1–V7.9**: totale **176 Python PASS, 0 FAIL/0 SKIP**. Non è stata ripetuta alcuna sintesi Yosys o testbench Icarus in questo workflow; le verifiche digitali delle versioni precedenti restano storiche, senza dichiararle eseguite ora.

La CI diagnosticamente verde significa che i file KiCad *si caricano* e che i duplicati sono azzerati; **non** che la scheda supera ERC, DRC, simulazioni vendor o prove reali.

## 5. Prossime fasi

**V7.13:** correggere a priorità i 46 `endpoint_off_grid`, 15 simboli/15 footprint warning RX e identificare ciascuna delle 63 connessioni non completate con vera compatibilità elettro-RF. Sistemare via dangling e ritorni RF, verificare impronte SMA e termica LNA, poi passare alle 43 ERC error della gerarchia e connettere progressivamente una delle 15 interfacce MCU/AUX/RX solo con pin, tensione e terra qualificati. Firmware DSP, calcoli IF2, PLL e test automatici proseguono in parallelo.

**NO FAB / NO TX.** Nessun Gerber, fabbricazione, alimentazione FPGA/DAC/PA, antenna RF, emissioni o licenza affermata.
