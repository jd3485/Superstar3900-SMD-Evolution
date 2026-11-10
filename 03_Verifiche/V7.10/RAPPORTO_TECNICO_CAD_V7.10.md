# SUPERSTAR 3900 SMD EVOLUTION — RAPPORTO TECNICO CAD V7.10

**10 novembre 2026 · PASSAGGIO A KIcad NATIVO · NO FAB / NO TX.**
Questa revisione aggiunge un progetto schematico KiCad gerarchico per **RX / power / MCU**, con risultati di controllo effettivamente prodotti da `kicad-cli 9.0.8` su GitHub Actions. **Il PCB completo della radio non esiste ancora**, la TX non è in alcun modo attivata e le connessioni inter-modulo non sono state autorizzate.

## 1. Artefatto CAD realmente realizzato

`04_KiCad/Assemblaggio_RX_Power_V7.10_NOT_FOR_FAB/S3900E_RX_POWER_INTEGRATION_V7_10_NOT_FOR_FAB.kicad_sch` è un **vero file di schema KiCad**, non PNG o modello teorico. Riutilizza con sheet link:
- alimentazione AUX V1.5 con 3 sottofogli eFuse, buck 5V, LDO/TCXO/PLL;
- MCU/codec/AFE V2.1;
- modulo RX 50ohm V5.2, che possiede un PCB coupon separato `.kicad_pcb`.

L'aggregatore è un primo **indice gerarchico isolato**, non un circuito con alimentazioni o segnali RX connessi: tutti i 15 contratti cross-module sono **OPEN e HOLD** in `MATRICE_INTERFACCE_DA_QUALIFICARE_V7_10.csv`. Un progetto KiCad completo dovrà implementare e verificare quei collegamenti uno ad uno. La catena TX non è implementata nel nuovo root, e rimane tutta DNP/unrouted.

**KiCad-cli sch export netlist** sul nuovo root: **PASS generazione reale del file `integration.net`**, con warning di annotazione. Nel report native-netlist si contano:
- **7 pagine gerarchiche KiCad**, comprendenti il root, AUX power, MCU, RX, tre sottofogli AUX;
- **132 istanze di componenti**, **118 designatori distinti**, **11 designatori ripetuti** su più fogli (**14 istanze extra**), quindi **annotazione globale NON OK**;
- **99 reti** esportate, non una prova di continuità elettrica voluta tra moduli.

Fra i 11 designatori da riannotare: J101; C201/C202; R201/R202/R203; C101/C102/C103/C104/C105. I ref duplicati attraversano fogli AUX, MCU e coupon RX. Non si possono generare BOM e file di assemblaggio aggregati affidabili prima della correzione.

## 2. Audit KiCad reale — quantità di difetti rilevati

| Elaborato | Verifica effettiva | Risultato |
|---|---|---|
| Root V7.10 RX/POWER/MCU | `kicad-cli sch export netlist` | **PASS**, con warning annotazione |
| Root V7.10 | `kicad-cli sch erc` | **43 errori, 416 avvisi** (459 segnalazioni) |
| AUX V1.5 | `kicad-cli sch erc` | **22 errori, 248 avvisi** |
| MCU/CODEC V2.1 | `kicad-cli sch erc` | **18 errori, 92 avvisi** |
| RX schematic V5.2 standalone | `kicad-cli sch erc` | **BLOCCATO, exit 3: Failed to load schematic**, nessun rapporto ERC standalone |
| RX coupon PCB V5.2 | `kicad-cli pcb drc` | **91 violazioni DRC**, **63 connessioni non completate** |

Per il PCB RX, KiCad segnala nello specifico: **6 errori `drill_out_of_range`** (via hole 0,25 mm con regola min 0,30 mm), **70 warning `via_dangling`**, **15 warning `lib_footprint_issues`** e **63 `unconnected_items`**. Il report raggruppa le prime tre famiglie nelle 91 violazioni DRC e presenta separatamente le 63 connessioni mancanti; non sommare senza spiegazione due conteggi di categorie diverse. Le ERC del root contengono quelle dei moduli figli, quindi non sommare i 43 errori root ai 22 e 18 dei singoli moduli per dichiarare un nuovo totale.

**NON si dichiara ERC/DRC PASS**. Il successo della **CI di audit** significa che i problemi sono stati realmente rilevati, numerati e archiviati; non che il circuito sia corretto. Il test `valida_report_nativi_v710.py` blocca qualunque inventario mancante o flag di autorizzazione fabbricazione.

Un'ipotesi di correzione RX root (aggiunta `sheet_instances` su copia versionata) è stata provata con KiCad: **FAIL**, non ha risolto l'errore di caricamento; la copia sperimentale è stata eliminata e l'originale V5.2 conservato. Il problema deve essere risolto con indagine successiva, non soppresso.

## 3. Regressioni e workflow

`.github/workflows/v710_kicad_native_rx_audit.yml` usa **KiCad nativo 9.0.8** su GitHub Actions Ubuntu, conserva in un artifact ZIP:
- `integration.net` prodotto da Eeschema (non generato a mano);
- `integration_erc.rpt`, `aux_power_v15_erc.rpt`, `mcu_codec_v21_erc.rpt`, `rx_v52_pcb_drc.rpt` e output di errore RX standalone;
- `cad_audit_summary.json` e `integration_reference_collisions.json` con tutti i flag **NO FAB**.

Il primo audit completo con esito positivo per **esecuzione diagnostica** è [run 42853943931](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42853943931), job **129961760643**, log verificato: **12 test statici V7.10 PASS + 143 regressioni Python V7.1–V7.9 PASS = 155/155**, 0 FAIL e 0 SKIP. Il controllo sui riferimenti duplicati è stato aggiunto successivamente per non ripetere gli errori BOM.

Non sono stati eseguiti dal nuovo workflow i testbench HDL Icarus o la sintesi generica Yosys; gli esiti precedenti della V7.9 restano nello storico ma **non** costituiscono una compilazione FPGA per la V7.10. Le librerie footprint/simboli mancanti, la netlist e le errori native sono bloccanti da verificare prima della creazione dello sbroglio integrato.

## 4. Sviluppo parallelo e limiti

**Proseguiamo con due filoni coordinati:** EDA fisico e verifiche software/firmware. Il firmware RX/PLL, i modelli DSP IF2 a 455kHz, i contratti DAC/clock e le prove di watchdog rimangono importanti, riproducibili, versionati in GitHub; nessuno è stato cancellato. Ma i loro risultati non sostituiscono un collegamento elettrico certificato fra i blocchi CAD.

**NON ESEGUITI:** schema unico elettricamente connesso, ERC senza errori, DRC RX senza violazioni, footprint SMA e LNA termico qualificati, release BOM, alimentazioni/PLL/pin MCU finali, schema/layout PCB integrato, KiCad PCB full-radio, clock/PA/DAC TX, verifiche statiche analogiche/EMC/RF da banco, assemblaggio, produzione o trasmissione. Lattice SG48 pinout originale resta **HOLD**.

## 5. Prossima revisione V7.11

Priorità 1: riparare il caricamento standalone del coupon RX su nuova copia verificata con **KiCad CLI**, rendere portabili le librerie e correggere i 63 unconnected/6 drill/70 dangling e i vincoli footprint senza abbassare le regole DRC. Priorità 2: riannotare univocamente le 132 istanze fra moduli e ridurre gli ERC principali. Priorità 3: validare rail 5V/3V3 e segnali SPI fisici, poi connettere gerarchicamente power→MCU→RX con pin reali. In parallelo mantenere regressioni firmware/software. **NO FAB / NO TX**.

**Verdetto:** prima integrazione gerarchica KiCad ed audit nativo eseguito, MA il circuito completo e il PCB della radio restano da sviluppare e NON APPROVATI.
