# SUPERSTAR 3900 SMD EVOLUTION — ARCHITETTURA CAD RX V7.13

**10 novembre 2026 | SOLO schema KiCad RX / test matematici; NO FAB / NO TX.**

## Modifica concreta

Schema nuovo: `04_KiCad/Modulo_RX_Test_50ohm_V7.13_GRID_NOT_FOR_FAB/S3900E_RX_GRID_V7_13_NOT_FOR_FAB.kicad_sch`. Creato a partire dall'RX V7.12 standalone, senza alterarne il file. Il nuovo root gerarchico `04_KiCad/Assemblaggio_RX_Power_V7.13_GRID_NOT_FOR_FAB/S3900E_RX_POWER_V7_13_GRID_NOT_FOR_FAB.kicad_sch` collega come foglio il nuovo RX, mantenendo AUX e MCU come fogli NON collegati elettricamente.

Allineati alla griglia KiCad di **50 mil = 1,27 mm** i punti di connessione del coupon:
- **15** origini di simbolo, con 19 pin cached già a multipli di 1,27mm;
- **31** segmenti di filo (62 estremi);
- **31** etichette di rete;
- nessun `lib_symbol` cached o offset pin cambiato, nessun reference designator cambiato, nessuna modifica al `.kicad_pcb` V7.12.

Gli estremi dei fili e delle etichette sono stati spostati *insieme* alle origini di simbolo: non esiste un tie libero di una rete a un'altra. I punti di wire+label non collassano in coppie di coordinate precedentemente distinte. **La prova che prevale su tutte queste ipotesi è il confronto delle vere netlist KiCad.**

## Gate di equivalenza realmente eseguiti in KiCad 9

GitHub Actions [run 42869838167](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42869838167), job **130017817769**. Workflow `.github/workflows/v713_rx_native_grid_erc.yml`.

1. `kicad-cli sch export netlist` RX V7.12 e RX V7.13: script `03_Verifiche/V7.13/verifica_netlist_rx_v713.py` confronta il **multiset esatto di (nome rete, riferimento, numero pin)**. Nessuna differenza, **PASS**. Non è una semplice uguaglianza del conteggio di nets.
2. ERC RX con regole invarianti: **46 avvisi `endpoint_off_grid` V7.12 → 0 V7.13**, warning RX totali **76→30**, errori RX **0→0**; rimangono **15 `lib_symbol_issues` e 15 `footprint_link_issues`**. Le librerie `sym-lib-table` e `fp-lib-table` sono state inserite come mapping archivio locale, **ma KiCad CLI continua a non trovare/configurare i due nickname**: non dichiarare le librerie "riparate", nessuna library warning è stata soppressa.
3. ERC root a sette fogli **459→413 segnalazioni**, di cui **43 errori** invariati, warning **416→370**, riduzione di 46 perché è stata migliorata la griglia dell'RX, non i 15 contratti tra moduli.
4. `kicad-cli pcb drc` sulla PCB RX V7.12 **NON modificata**: sempre **85 violazioni DRC /63 unconnected**, zero errori drill, **70 vias GND dangling e 15 footprint warnings**. Niente Gerber né nuovo layout.
5. **10 test Python V7.13** + **13 V7.12** + **8 V7.11** + **12 V7.10** + **143 V7.1–V7.9** = **186 PASS, 0 FAIL, 0 SKIP**; l'intera serie DSP/PLL/firmware/numerica precedente rimane attiva. Non sono state ripetute sintesi Yosys/Icarus hardware.

## Limiti ancora bloccanti

Root ERC **43 errori**, RX **30 avvisi librerie**, RX PCB **85 DRC +63 incompleti**. Altre **15 interfacce** AUX/MCU/RX sono **OPEN/HOLD** e richiedono verifica su pin, livelli, polarità, alimentazione, return path e compatibilità RF; SG48 XLSX originale Lattice rimane HOLD. Nessun PCB completo, PCB produttivo, alimentazione dell'apparato, SPICE vendor dei filtri, misure EMC/RF e collaudi fisici.

**Prossima V7.14:** stabilire un progetto `.kicad_pro` davvero portabile e qualificare link symbol/footprint (senza rinominare footprint di fortuna), proseguire su 70 vias GND e 63 collegamenti PCB con ritorni e zone reali, correggere 43 errori ERC root e collegare i primi confini certificati; preservare DSP/firmware e test.

**NO FAB / NO TX:** tutti TX, DAC/FPGA/mixer/PA/antenna DNP, non alimentati e non instradati.
