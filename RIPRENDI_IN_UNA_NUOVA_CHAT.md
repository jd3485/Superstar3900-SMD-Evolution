# HANDOFF SUPERSTAR 3900 SMD — V7.18 MODELLO EFUSE E LOOP PLL

**11 novembre 2026 · V7.18 MERGED in `main` tramite [PR #18](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/18), merge `29965cdcdfe2edd1e241295315bfe18fabc864a5`.** Sorgenti V7.17 e precedenti intatti. **NO FAB / NO TX.**

Nella directory `04_KiCad/Gerarchico_Alimentazioni_V7.18_PINMODEL_NOT_FOR_FAB/`, l'unica ECO fisica di schema è nel simbolo embedded TPS26600PWPT eFuse U200: pin OUT15 rimane `power_out`, pin OUT16 diventa `passive` *come attributo ERC soltanto*, mantenendo entrambi sullo stesso output (TI TPS2660x SLVSDG2G p.5). La nuova gerarchia completa è `04_KiCad/Assemblaggio_RX_Power_V7.18_POWER_PINMODEL_NOT_FOR_FAB/`, le altre tre schede AUX root/BUCK/PLL sono byte-intatte, RX/MCU originali intatti.

**Prova KiCad9 nativa:** [CI 42964160297](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42964160297) PASS, **ERC 43→42 errori, 340 warning invariati, `pin_to_pin` 1→0, 99 reti con tutte le membership ref/pin IDENTICHE**, interfacce OPEN/HOLD sempre 15, SG48 HOLD. **12 nuovi test V7.18 +241 regressioni V7.1–V7.17 =253 PASS**, 0 FAIL/SKIP.

**Esperimenti R2/R3 loop** su quattro cloni temporanei (NON applicati): as-is 42/340; R2 wire da fuori corpo 42/341; R3 simmetria pin 180° 42/340; entrambi 42/341. Nessuna modifica della membership di net; non si può correggere l'anello senza revisarene fisicamente pin e rete. Restano **26 label +16 altri errori ERC (6 power, 5 input, 3 wire, 2 pin NC)** e nessuna qualifica della sezione PLL 3V3/5V, IF2, SMA o real PCB.

Aprire `03_Verifiche/V7.18/RAPPORTO_TECNICO_CAD_V7.18.md`, machine JSON, `01_Specifiche/V7.18/ECO_EFUSE_DUAL_OUT_PINMODEL_V7_18.md`, workflow `.github/workflows/v718_efuse_pll_native.yml`, artifact DRC/ERC KiCad native. Non interpretare CI verde come scheda fabbricabile. Percentuale PCB completa ~10% invariata.

**Next V7.19:** verificare KiCad GUI e TI EVM del loop filter R2/R3, qualificare 5V/3V3/GND e il PLL safe-start, ridurre i 16 hard ERC su circuiti reali, poi interfacce, schematico unificato e PCB intera. **NO FAB / NO GERBER / NO PCBWAY / NO TX.**

---

## STORICO HANDOFF V7.17 E PRECEDENTI

# HANDOFF — SUPERSTAR 3900 SMD V7.17 FULL-RADIO MASTER

**11 novembre 2026 · V7.17 MERGED su `main` tramite [PR #17](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/17), merge `ff26db4e55eb2ab7368cb222de58a8b969cf08d6`. NO FAB / NO TX.**

Ultimo avanzamento non è sul coupon RX ma sulla schematica completa: nuova directory KiCad `04_KiCad/Assemblaggio_RX_Power_V7.17_INTEGRATION_HOLD_NOT_FOR_FAB/` con master a sette fogli (file volutamente denominato `S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch` perché conserva l'identità project KiCad e le annotazioni dei fogli). Native KiCad [CI 42923409956](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42923409956): **99 reti e tutti pin/refs identici baseline, ERC 43 errori/340 warning, RX ERC 0/0, 241 Python PASS** (18 V7.17+223 precedenti), 0 FAIL/SKIP. Gli errori root includono 26 label aperte e 17 problemi elettrici/fili; 219 warning off-grid e121 libreria.

`04_KiCad/Assemblaggio_RX_Power_V7.17_INTEGRATION_HOLD_NOT_FOR_FAB/MATRICE_INTERFACCE_PROPOSTE_V7_17_OPEN_HOLD.csv`: tutte **15 OPEN/HOLD**, corregge solo il nome proposto `FM_DISCR_RAW`→`FM_DISCRIM_RAW` lato MCU secondo netlist nativa, senza cablaggio. Due nomi di rete destinazione ancora assenti: `RX_IF_STAGE` e `RF_TX_UNROUTED` (TX intenzionalmente unroute). Non collegare rail 5V/3V3/GND o SPI senza qualifica, né usare un semplice naming match come verifica del segnale.

`03_Verifiche/V7.17/RAPPORTO_TECNICO_CAD_V7.17.md`, `RISULTATI_VERIFICHE_V7_17.json`, parser e parity script e workflow `.github/workflows/v717_full_board_erc.yml` documentano test. No board completa, nessun Gerber/ordine/test RF, SMA destri 180° da qualificare. **Stima PCB completa ~10%, non aumenta** con l'audit. **Next V7.18:** eliminare 17 ERC HARD dopo datasheet power/PLL, ridurre 26 label con circuiti reali, poi completare IF/contratti e integrare PCB. SG48 e TX sempre HOLD.

---

## STORICO V7.16 E PRECEDENTI

# RIPRESA SUPERSTAR 3900 SMD EVOLUTION — HANDOFF V7.16

**10 novembre 2026: V7.16 integrata su `main` con [PR #16](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/16), merge `b8ad95695aed960621f4fd2160fa4b2ae921d6eb`. Controllare sempre HEAD `main`, PR, CI e tag.** Baseline V7.15 già integrata, tag storico `v7.0` e tutte le versioni preserved. **NO FAB / NO TX.**

**KiCad nativo verificato** [Actions 42920876308](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42920876308): quattro cloni di progetto V7.14, fill zone reale con `pcbnew.ZONE_FILLER`, quindi DRC vero. Baseline J9102/J9104 a 180°: 2 warning footprint e zero unconnected. Etichette ruotate: 2. Custom pad ruotati: 2. Intero footprint J9102/J9104 ruotato a 0°: DRC 0, ma **montaggio errato** sul lato destro della PCB; il courtyard passerebbe da x117,9–137,2 a x106,8–126,1 mm, fuori direzione rispetto al connettore che deve uscire dal bordo x130. NON utilizzare questa falsa correzione. Originale byte-identico (V7.12 = V7.14), nessun TX/fab.

**Risultati software**: **10 nuovi test V7.16 +213 regressioni V7.1–V7.15 =223 PASS, 0 FAIL/SKIP**. Restano ERC RX 0/0, root 43 errori+340 warning, 15 cross-module OPEN/HOLD, SG48 HOLD, nessuna qualifica RF o vendor. Non rieseguiti Icarus/Yosys.

**Fonti/documenti**: `README.md`; `03_Verifiche/V7.16/RAPPORTO_TECNICO_CAD_V7.16.md`, `RISULTATI_VERIFICHE_V7_16.json`; `01_Specifiche/V7.16/PROTOCOLLO_SMA_ORIENTAMENTO_KICAD_V7_16.md`, workflow `.github/workflows/v716_sma_native.yml`. TE CONSMA002-SMD DXF e STEP elencati ufficialmente, ma CAD originale non scaricato/importato/approvato.

**Prossima V7.17:** import e validazione geometrica vendor DXF/STEP, mismatch SMA senza cambiare il montaggio a 180°, provare PCB refill versionata **NOT_FOR_FAB**, poi root ERC/interfacce e test DSP/PLL/firmware. No Gerber, ordini PCBWay, PA/antenna o RF TX.

---

## STORICO HANDOFF V7.15 E PRECEDENTI

# RIPRESA SUPERSTAR 3900 SMD EVOLUTION — HANDOFF V7.15

**10 novembre 2026: V7.15 integrata in `main` con [PR #15](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/15), merge `ca81deb3fe83e210778590cc9e2db1a18e16b243`. Controlla SEMPRE HEAD `main`, ultimi PR e CI prima di continuare.** Baseline V7.14 conservata, nessun PCB originale cambiato. Tag `v7.0` storico intatto. **NO FAB / NO TX.**

**Verifica tecnica conclusiva V7.15:** vera CI KiCad9 su copia temporanea del progetto RX con `pcbnew.ZONE_FILLER` e DRC nativo, refilled 4 zone GND_RF. As-is PCB: **72 DRC +63 unconnected** (70 via_dangling+2 SMA mismatch). Dopo refill *solo clone temporaneo*: **2 DRC +0 unconnected**, cioè via_dangling **70→0**, unconnected **63→0**, mismatch **2→2** su SMA **J9102/J9104**. Il source PCB V7.14 è identico (SHA256 `ec37ef62787eeb6607def2780d9a7da06a614eafd3b225283f6e9c6fd3a5f3d9`). Questo non è un PCB pronto e non approva ritorni RF o produzione. Il CLI non supportava `--refill-zones`; percorso alternativo Python pcbnew realmente eseguito, report nativi come artifact.

**Vendor:** TE/Linx `CONSMA002-SMD`, tavola `C-CONSMA002-SMD-X-X Rev D`: controllo parziale centro Ø2.05mm/trasversale 7.76mm. J9102/J9104 ruotati 180°; le firme geometriche dei pad sono identiche al modello locale, ma KiCad continua a segnalare 2 mismatch. NON aggiornare footprint senza DXF/STEP e review GUI / produttore.

**CI reale:** [push 42918178033](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42918178033), [PR 42918302874](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42918302874): **213/213 test Python PASS**, KiCad9 ERC RX **0 errori/0 warning**, root **43 errori/340 warning** aperti. Nessuna prova Icarus/Yosys nuova, RF o prototipazione. Leggere nell'ordine `README.md`, `03_Verifiche/V7.15/RAPPORTO_TECNICO_CAD_V7.15.md`, `01_Specifiche/V7.15/SMA_ZONE_READONLY_DIAGNOSTIC_V7_15.md`, `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`, JSON e workflow V7.15.

**Prossima V7.16:** risolvere vendor SMA 2 mismatch, verifica e salvataggio zone su nuova copia nativa, DRC rigoroso, stackup/ritorno GND_RF; poi 43 ERC root, 15 interfacce RX/MCU/AUX OPEN/HOLD, SG48 HOLD, regressioni DSP/PLL/firmware. Nessun Gerber, nessuna release FAB, nessuna TX.

---

## STORICO HANDOFF V7.14 E PRECEDENTI

# RIPRESA PROGETTO SUPERSTAR 3900 SMD EVOLUTION — V7.14 SU MAIN

**10 novembre 2026 · V7.14 integrata in `main`, [PR #14](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/14), merge `5c0940bf213776e93e72f2bd11fd20ce4fa842e7`.** La versione corrente va sempre ricontrollata tramite HEAD `main`, PR e GitHub Actions; `v7.0` storico intatto. **NO FAB / NO TX.**

**Avanzamento CAD vero:** creati due progetti KiCad 9 con `.kicad_pro` e tabelle librerie locali: `04_KiCad/Modulo_RX_Test_50ohm_V7.14_LIB_DIAGNOSTIC_NOT_FOR_FAB/` (schema **e PCB** di coupon RX) e `04_KiCad/Assemblaggio_RX_Power_V7.14_LIB_NOT_FOR_FAB/` (gerarchia 7 fogli, NON collegamento elettrico fra i blocchi). I file storici rimangono conservati e il PCB RX è byte-identico alla V7.12. L'ERC RX è **0 errori /0 warning**, da **0/30** V7.13, grazie al corretto caricamento delle librerie KiCad tramite `.kicad_pro` (nessun waiver). La netlist RX e la gerarchia mantengono tutte le membership pin-rete originali: **99 reti gerarchiche identiche**. Il DRC RX è diminuito **85→72 violazioni**, ma rimangono **70 via GND dangling**, **2 footprint mismatch SMA J9102/J9104**, **63 unconnected items** e nessuna nuova pista. ERC root ancora **43 errori +340 warning** (V7.13: 43+370). Questi difetti sono BLOCCANTI per produzione.

**CI della PR #14 verificata:** [Actions run 42886396335](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42886396335), log controllato: **15 V7.14 + 186 regressioni V7.1–V7.13 =201 test Python PASS, 0 FAIL/SKIP**, KiCad9 vero su due progetti con ERC/DRC e netlist. Icarus/Yosys non rieseguiti e nessun test fisico/RF realizzato. Rapporto corrente `Superstar3900_Rapporto_Tecnico_V7.14.md`, specifica `01_Specifiche/V7.14/PROGETTI_KICAD_RX_LIBRERIE_V7_14.md`, ECO `00_Gestione_Progetto/ECO_INTEGRAZIONE_CAD_V7.14.md`, JSON `03_Verifiche/V7.14/RISULTATI_VERIFICHE_V7_14.json`.

**Prossima V7.15:** verificare con disegno manufacturer i due footprint SMA discordanti J9102/J9104, poi analizzare 70 via GND e 63 reti RX incomplete; ridurre i 43 errori ERC gerarchici, qualificare 15 interfacce MCU/AUX/RX ancora **OPEN/HOLD** e pin FPGA SG48 tuttora HOLD. Proseguire firmware, DSP, PLL, simulazioni, BOM e test. **Nessun Gerber, PCB completo, fabbricazione, PA/antenna o trasmissione RF autorizzati.**

**Procedura nuova chat:** verificare main/PR/tags/CI, leggere questo file, `README.md`, `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md` e rapporto V7.14; continuare V7.15 con vero KiCad, preservando sorgenti storici e senza fabbricare.

---

## ARCHIVIO ISTRUZIONI V7.13 E PRECEDENTI

# RIPRESA PROGETTO SUPERSTAR 3900 SMD EVOLUTION — V7.13 SU MAIN

**10 novembre 2026:** versione integrata più recente **V7.13**, PR [#13](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/13), merge `81928a6fc36f6e3bb98c04338026a4ed2f78769d`. Tag storico `v7.0` conservato. **Alla nuova chat controllare HEAD di `main`, PR aperte e GitHub Actions:** la revisione più recente prevale sempre su questo testo.

1. Leggere `README.md`, `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`, `Superstar3900_Rapporto_Tecnico_V7.13.md`, `01_Specifiche/V7.13/GRID_NETLIST_EQUIVALENCE_V7_13.md`, ECO, JSON e workflow V7.13.
2. V7.13 ha **vero schema KiCad RX snap a griglia 50mil** (15 simboli +31 wire +31 labels) in `04_KiCad/Modulo_RX_Test_50ohm_V7.13_GRID_NOT_FOR_FAB` e root gerarchico `04_KiCad/Assemblaggio_RX_Power_V7.13_GRID_NOT_FOR_FAB`. **Netlist KIcad9 identiche punto per punto (nome rete/ref/pin)** V7.12 vs V7.13. Non sono stati aggiunti fili fra AUX, MCU e RX.
3. **Vere misure ERC:** RX **46→0 off-grid**, **76→30 warning**, **0 ERC error**; root **459→413 segnalazioni**, di cui **43 errori** invariati. I 30 RX warning sono ancora 15 simboli e15 footprint: `sym-lib-table` e `fp-lib-table` ci sono, ma **non risultano effettivamente risolte dal KiCad CLI**. PCB RX non toccata: **85 DRC+63 unconnected**, 70 via dangling, 15 footprint warnings.
4. **CI PR #13** [run 42870757111](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42870757111), job 130021089653, log verificato: **186 test Python PASS** (10 V7.13+13 V7.12+8 V7.11+12 V7.10+143 storici), reali export KiCad/ERC/DRC. Icarus/Yosys non rieseguiti su questa revisione. No scheda completa, misure RF, elettronica fabbricata.
5. **Prossima V7.14:** riparare link KiCad vendor e preparare progetto `.kicad_pro` davvero portabile; risolvere routing/ground 70 via dangling+63 unconnected sulla PCB RX mantenendo le nets, poi 43 errori ERC del root e 15 interfaces MCU/AUX/RX OPEN/HOLD con pin verificati. Non collegare alla cieca.
6. Conservare ogni revisione storica, tag `v7.0`, dati DSP/PLL/firmware; continuare sviluppo su branch, regressioni reali, rapporti PASS/FAIL/NON ESEGUITO e merge solo dopo CI comprovata.

**NO FAB / NO TX:** TX/DAC/FPGA/mixer/PA/antenna DNP, non alimentati e non instradati. Nessun Gerber, PCB fabbricabile, PTT o TX permesso; pinout FPGA SG48 XLSX ufficiale ancora HOLD.

---

## ARCHIVIO — V7.12 E PRECEDENTI

# RIPRENDERE IL PROGETTO SUPERSTAR 3900 SMD EVOLUTION — V7.12 SU MAIN

**10 novembre 2026:** V7.12 integrata in `main`, [PR #12](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/12), merge `aad39c250fe626fa94424ff9ce2c08cb6b9ebcc8`. Tag `v7.0` baseline storica. **Verificare HEAD `main`, PR e Actions in ogni nuova chat**: se versione più nuova, usare quella e non questa intestazione.

## Continuità tecnica
1. Leggere `README.md`, `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`, `Superstar3900_Rapporto_Tecnico_V7.12.md`, spec/ECO, `.github/workflows/v712_kicad_native_annotation.yml`.
2. KiCad vero V7.12: root `04_KiCad/Assemblaggio_RX_Power_V7.12_REANNOTATED_NOT_FOR_FAB/S3900E_RX_POWER_INTEGRATION_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch` + MCU rinumerato e RX schema/PCB allineati. Native KiCad9 netlist **7 sheets/132 instances/99 nets**, **11 conflitti ref→0**. Tutti i 15 limiti cross-module V7.10 ancora OPEN/HOLD, niente power/RF collegato.
3. RX standalone V5.2 falliva parser KiCad exit3 per nota grafica con LF reale e UUID mancante: la copia V7.12 escapando `\n` e aggiungendo UUID è **loadable**, con `sch erc` **0 errori e 76 warning** (46 endpoint off-grid, 15 libs, 15 footprint). Root ERC **43 errori+416 warning**, PCB RX DRC **85 violazioni +63 unconnected**, di cui 70 dangling via +15 lib warnings: **non** ERC/DRC PASS totale.
4. **PR CI finale verificata** [run 42866103256](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42866103256): **176 test Python PASS** (13 V7.12+8 V7.11+12 V7.10+143 firmware/DSP V7.1–V7.9), native KiCad exports/diagnostics PASS, nessun nuovo Icarus/Yosys. Il successo della CI è uno stato di diagnosi, non fabbricabilità.
5. **Prossima V7.13:** risolvere warning schematic off-grid/symbol/footprint RX su nuova copia versionata, avanzare nel routing real RF 50ohm e ritorni massa, ridurre le 63 unconnected/70 via dangling, affrontare 43 ERC root e collegare power/MCU/RX solo quando pin/supply/impedance/vendor verificati. Conservare e continuare simulazioni, firmware, DSP, PLL, BOM e test.
6. Mantenere revisioni storiche e `v7.0`, integrare nuove revisioni CAD+test su branch PR dopo CI effettiva, distinguere **PASS esecuzione** da **FAIL ERC/DRC elettrici**. Pinout iCE40 SG48 originale resta HOLD, tutta la catena TX resta **DNP/OPEN**.

**Vincolo inviolabile: NO FAB / NO TX.** Non produrre PCB o Gerber e non alimentare trasmettitori/PA/antenna senza validazione reale.

---

## ARCHIVIO STORICO — V7.11 e precedenti

# RIPRESA SUPERSTAR 3900 SMD EVOLUTION — V7.11 SU MAIN

**10 novembre 2026:** V7.11 integrata [PR #11](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/11), merge `028c3a5f8d9f638d423be251a7a06336a961ead7`. Verificare sempre l'ultimo HEAD `main`: una revisione successiva prevale. Tag `v7.0` storico immutato.

## Procedura e stato accertato
1. Leggere repository GitHub privato `jd3485/Superstar3900-SMD-Evolution`, `README.md`, questo file, `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md` e il rapporto `Superstar3900_Rapporto_Tecnico_V7.11.md`; controllare HEAD main, PR e workflow prima di procedere.
2. **V7.11 reale:** nuova copia `.kicad_pcb` del coupon RX V5.2 con sei via corrette foro 0,25→0,30mm, rame 0,55→0,60mm, originale preservato, fp-lib-table locale. KiCad CLI DRC su entrambi i file: **91→85 violazioni**, **6→0 errori drill**, **70 via dangling e 15 footprint warnings invariati**, **63 connessioni mancanti invariati**. **PCB DRC FAIL nel complesso**. GitHub Actions [run 42856926563](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42856926563), log verificato: **163 Python PASS (8+12+143)**, niente nuovi Icarus/Yosys in questa CI.
3. Il root V7.10 in `04_KiCad/Assemblaggio_RX_Power_V7.10_NOT_FOR_FAB` ha 7 fogli, 132 componenti, 11 designatori riutilizzati e 99 nets; connettere i moduli è ancora bloccato. ERC root **43 errors +416 warnings**, RX V5.2 standalone **exit3** in `kicad-cli sch erc`. Le 15 interfacce tra AUX/MCU/RX sono `OPEN/HOLD`; non inferire connessioni per nomi simili o unire rail/pin senza validazione.
4. **Prossima V7.12:** correggere caricamento schema RX standalone nativo, riannotare tutti i duplicati su copie versionate con report netlist, verificare footprint SMA/LNA con libre, risolvere 70 via dangling e 63 unconnected in modo elettricamente coerente, ridurre ERC e connettere gradualmente power/MCU/RX. Parallelamente preservare e rieseguire firmware/DSP/simulazioni.
5. Tutti i componenti e interblocchi TX rimangono `DNP/OPEN`. Pinout iCE40 SG48 `HOLD`. **NO FAB / NO TX**: nessuna release Gerber, nessun PCB completo né hardware validato, nessun bench RF o trasmissione.

---

## ARCHIVIO — istruzioni V7.10 e precedenti

# RIPRENDERE SUPERSTAR 3900 SMD EVOLUTION — V7.10 IN MAIN, KIcad NATIVO

**10 novembre 2026:** V7.10 integrata con [PR #10](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/10), merge `8a18c12df4455265db8414784587f4d82a1f82ae`. Questo stato non prevale su versioni successive: **controllare sempre HEAD di `main`**. Il tag `v7.0` è storico preservato.

## Come continuare
1. Aprire repository GitHub privato `jd3485/Superstar3900-SMD-Evolution`, leggere `README.md`, questo file e `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`, verificare `main`, PR, tag e Actions prima di procedere.
2. Leggere `Superstar3900_Rapporto_Tecnico_V7.10.md`, `01_Specifiche/V7.10/PIANO_CAD_INTEGRAZIONE_RX_POWER_V7.10.md`, `00_Gestione_Progetto/ECO_INTEGRAZIONE_CAD_V7.10.md` e `03_Verifiche/V7.10/RISULTATI_VERIFICHE_V7_10.json`. Aprire davvero in KiCad `04_KiCad/Assemblaggio_RX_Power_V7.10_NOT_FOR_FAB/S3900E_RX_POWER_INTEGRATION_V7_10_NOT_FOR_FAB.kicad_sch`; conserva legami relativi ai 3 schemi originali. ZIP con 4 directory CAD e reports nel workflow [42855337776](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42855337776).
3. Risultati verificati: KiCad CLI **9.0.8** export **7 sheets/132 components/99 nets**, **11 ref ambigui**. ERC root **43 errori +416 avvisi**; AUX V1.5 **22/248**, MCU V2.1 **18/92**; RX standalone **exit 3, impossibile da caricare**. PCB coupon RX V5.2: **91 violazioni DRC e 63 unconnected**. Tutto questo è **BLOCCANTE, non ERC/DRC PASS**. CI diagnostica ha **12 test V7.10 +143 regressioni DSP/firmware V7.1–V7.9 =155 PASS**, dopo avere effettivamente prodotto i report KiCad.
4. **Prossima V7.11** focalizzata su CAD: recuperare/caricare schema RX standalone su copia verificata, annotare univocamente componenti in 7 fogli, risolvere cause footprint/library, R/X 63 unconnected, drills Ø0,25 vs rule min Ø0,30, ERC dei tre moduli, quindi integrare connessioni reali di alimentazioni/PLL/MCU/RX con componenti verificati, ripetere native KiCad CI. Non iniziare vero PCB full-radio prima della netlist stabile; non abbandonare test firmware e simulazioni.
5. Tutti i moduli non inclusi nel root restano storici; l'intero TX (DAC900, FPGA iCE40, mixer, PA, antenna) **DNP, non alimentato, non connesso**. Originale XLSX pin SG48 Lattice doc 51971 ancora **HOLD**. Nessun PCB fabbricabile, Gerber, KiCad ERC/DRC zero, EMC, test radio TX autorizzato.
6. Conservare storico e tag, lavorare su feature branch, far eseguire realmente KiCad e regressioni, riportare separatamente **PASS diagnostica / FAIL ERC-DRC / NON ESEGUITO hardware**, integrare in `main` solo dati corretti senza rivendicare avanzamenti non avvenuti.

**Messaggio sufficiente:** Prosegui il progetto privato `jd3485/Superstar3900-SMD-Evolution` dal main più recente. Leggi rapporti CAD e i tre file di continuità, poi sviluppa V7.11 risolvendo realmente ERC/DRC e collegamenti KiCad, mantenendo regressioni DSP/firmware e **NO FAB / NO TX**.

---

## ARCHIVIO — V7.9 E PRECEDENTI

# RIPRESA FUTURA — SUPERSTAR 3900 SMD EVOLUTION V7.9 SU MAIN

**10 novembre 2026.** V7.9 integrata in `main` con [PR #9](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/9), merge `38b9828728b02581bf24c070401dd70782051dbd`. `v7.0` è tag storico intatto. Se la prossima chat trova una revisione più recente su `main`, usare quella e non questa fotografia.

## Procedura da seguire
1. Accedere a GitHub privato `jd3485/Superstar3900-SMD-Evolution`; leggere `README.md`, questo file e `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`. Verificare HEAD `main`, PR aperte, tag e **risultati delle GitHub Actions**, non fidarsi della sola versione scritta nei vecchi documenti.
2. Rapporto corrente `Superstar3900_Rapporto_Tecnico_V7.9.md` e `03_Verifiche/V7.9/RAPPORTO_TECNICO_V7.9.md`; specifica `01_Specifiche/V7.9/ARCHITETTURA_HEARTBEAT_WATCHDOG_SRF_V7.9.md`; ECO `00_Gestione_Progetto/ECO_INTEGRAZIONE_V7.9.md`; distinte e test in cartelle V7.9.
3. Stato V7.9: heartbeat numerico 30,72MHz /307200 **toggle ogni 10ms**, WDI falling ogni **20ms**, window TI TPS3430WDRCR CWD=NC SET0=0 SET1=1 **2,22ms max lower /23,375ms min upper**. Secondo riferimento candidato Abracon ASFLK 32.768kHz **DNP**. Il vecchio heartbeat V7.8 /8 è troppo veloce per un riferimento 32,768kHz: non usarlo come interfaccia di monitoraggio fisica. DAC900 PD active-HIGH e WDO TPS3430 open-drain active-LOW NON compatibili senza hardware autonomo con latch.
4. Filtro IF2 screening numerico di due induttori Coilcraft con SRF catalogo e Q ASSUNTO: mai classificare 0,235dB/88,7dB come prestazioni RF reali. Pinout Lattice `iCE40UP5K` SG48 **HOLD** fino a verifica del workbook XLSX vendor documento 51971. Tutti i ponti TX DNP/OPEN.
5. **CI verificata PR #9** [run 42848254217](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42848254217): **17 nuovi + 126 regressioni = 143 test Python PASS, 4 bench Icarus PASS, Yosys generic PASS**, log esaminato, zero FAIL/SKIP. Hardware, KiCad ERC/DRC, PNR/STA, EMC, misure, fabbricazione e TX **NON ESEGUITI**.
6. **Prossima V7.10:** acquisire originale XLSX Lattice con verifica SHA256 e review package/PIO; progettare su carta supervisor indipendente e gate PD/fail-open con simulazione power loss e single fault senza montarlo; qualificare F7401 con vendor Q/ESR/cap/SRF e DAC900 corrente-output I/V; migliorare DSP fixed-point e misure numeriche. Creare report/ECO/BOM/test/CI in branch temporaneo, integrare revisione coerente in main dopo PASS, preservando storia.

**Vincolo permanente NO FAB / NO TX:** nessuna PCB, nessuna alimentazione dei componenti DAC/FPGA/PA, nessuna uscita verso antenna, nessuna abilitazione PTT o emissioni; non attribuire sicurezza reale a booleani HDL.

---

## ARCHIVIO — istruzioni riferite a V7.8 e precedenti

# RIPRESA DI SUPERSTAR 3900 SMD EVOLUTION — V7.8 IN MAIN

**10 novembre 2026:** main ha integrato **V7.8** tramite [PR #8](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/8), merge `75027e768bef2b5a00f69d1675e462b8c35b1366`. Tag `v7.0` baseline storica immutata. Le indicazioni V7.7/V7.6/V7.5 riportate sotto sono archivio: all'inizio della prossima chat verificare comunque se `main` è avanzata oltre questa fotografia.

## Procedura permanente
1. Aprire repository privato `jd3485/Superstar3900-SMD-Evolution`, leggere `README.md`, questo file e `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`; controllare HEAD `main`, PR, tag e GitHub Actions prima di scegliere la versione attuale.
2. Leggere `Superstar3900_Rapporto_Tecnico_V7.8.md`, `03_Verifiche/V7.8/RAPPORTO_TECNICO_V7.8.md`, `01_Specifiche/V7.8/ARCHITETTURA_WATCHDOG_PINOUT_DSP_V7.8.md`, ECO, BOM, netlist, workflow e modello.
3. Stato V7.8: **2 clock virtuali per rilevare arresto master**, fault latched, Icarus e Yosys generici PASS; **126/126 Python PASS**, con [run 42842592233](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42842592233) verificato. Tool di confronto XLSX vendor testato **SOLO con file sintetici**: originale Lattice SG48 documento 51971 non acquisito e pin/PCF **HOLD**. Nuovo quantizzatore digitale con guardia stretta pre-headroom e analisi non periodica. **Nessun DAC/FPGA/clock/riferimento/PD/PA/antenna reale**.
4. **Prossima V7.9:** ottenere e autenticare originale XLSX Lattice, confrontare tutti i 48 pin e il paddle, verificare banks I/O e clock, scegliere MPN watchdog di clock fisico + riferimento indipendente, PDSR supervisor fail-safe verificabile anche a rail assente, filtri analogici con SRF/Q vendor, DSP su transitori/rumore. In assenza di documento primario non approvare PCF né procedere a PNR/PCB.
5. Per ogni revisione sviluppare specifica, ECO, BOM, netlist solo con pin verificati, modelli/firmware/RTL pertinenti, CI e regressioni reali, rapporto distinguendo **PASS/FAIL/SKIP/NON ESEGUITO**; mantenere tag/storico e integrare versione coerente in `main`.
6. **NO FAB / NO TX**. DAC900 PD active-high con pulldown interno può abilitarsi se flottante; output RTL zero non sostituisce protezioni hardwired. Non fabbricare, non collegare PA/antenna, non rivendicare KiCad ERC/DRC, EMC, SPICE vendor o misure hardware non eseguiti.

**Messaggio breve per riprendere:** Continua `jd3485/Superstar3900-SMD-Evolution` dal main attuale, leggi report e protocollo, sviluppa la prossima revisione, verifica CI e integra in main mantenendo **NO FAB / NO TX**.

---

## ARCHIVIO — ISTRUZIONI STORICHE V7.7 E PRECEDENTI

# RIPRENDERE IL PROGETTO IN NUOVA CHAT — V7.7 IN MAIN

**Fotografia 10 novembre 2026:** revisione progettuale **V7.7 già integrata in `main`** mediante [PR #7](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/7), merge `e68743f5474be26732cfb6cd4ad9953404a2935c`. Il tag `v7.0` è storico. Gli stati V7.6 e precedenti riportati sotto l'archivio sono soltanto cronologia.

## Istruzioni permanenti di continuità
1. Aprire `jd3485/Superstar3900-SMD-Evolution` su GitHub privato, leggere `README.md`, questo file e `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`. **Verificare SEMPRE HEAD `main`, PR e Actions**, perché se la revisione è già passata alla V7.8 o successiva, prevale quella.
2. Leggere `Superstar3900_Rapporto_Tecnico_V7.7.md`, `03_Verifiche/V7.7/RAPPORTO_TECNICO_V7.7.md`, `01_Specifiche/V7.7/ARCHITETTURA_RTL_QUANTIZZAZIONE_V7.7.md`, ECO, BOM e netlist prima di modificare sorgenti.
3. V7.7: **top RTL diagnostico** con strobe/FIFO, porte RF/PD/analogico tutte 0, due bench Icarus **PASS**, sintesi logica **Yosys generica PASS**, **106 Python PASS**, log [run 42819963860](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42819963860). I commit successivi al run validato contenevano soltanto report/documentazione; la PR-run finale era ancora in installazione alla data del merge: controllarne l'esito prima di citarla. Modello quantizzazione 10bit offline SNR numerica ~51,47dB; NO DAC fisico.
4. **Prossima V7.8:** acquisire originale XLSX Lattice SG48 documento `51971` e confrontare pin 1–48/paddle, conservare **HOLD** sulla PCF sino alla verifica ufficiale. Solo dopo, top fisico, PNR, STA e pin IO bank; approfondire supervisor indipendente PD e watchdog autonomo, power sequencing, filtro Q/SRF con MPN. Tutta l'elettronica TX DNP.
5. Ogni sviluppo aggiunge specifiche, distinta, netlist accurata, modello/RTL quando pertinente, test e regressioni, report distinguendo **PASS, FAIL, SKIP, NON ESEGUITO**, poi integra in **`main`** quando coerente. Non sovrascrivere lo storico/tag.
6. **NO FAB / NO TX**. DAC900 PD active-high con pull-down interno può essere ON con pin flottante; nessun modello software rende un hardware safe. RF, PA, antenna e PTT non connessi, nessun KiCad ERC/DRC, banco, EMC, misure TX o fabbricazione dichiarati senza prova reale.

**Messaggio per la prossima chat:** Riprendi Superstar 3900 SMD Evolution da `jd3485/Superstar3900-SMD-Evolution`. Verifica lo stato attuale di main e la CI, leggi README, protocollo e rapporto tecnico più recente e sviluppa la revisione seguente, mantenendo DNP e NO FAB / NO TX.

---

## ARCHIVIO — istruzioni storiche riferite a V7.6 E PRECEDENTI

# RIPRESA DA QUALSIASI NUOVA CHAT — V7.6 SU MAIN

**10 novembre 2026.** Ultima revisione integrata in `main`: **V7.6**, PR #6, merge `8309d11e1a06473119aafcb71a0cbe2aa0171e61`. Il tag v7.0 preserva soltanto la baseline storica; gli stati V7.5 e precedenti in questo file sotto l'archivio NON sono lo stato corrente. In una chat futura prevale comunque **l'ultimo commit verificato su main** anche quando più nuovo della V7.6.

## Procedura operativa di ripresa
1. Aprire il repository GitHub privato `jd3485/Superstar3900-SMD-Evolution`, leggere `README.md`, questo file e `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`; controllare commit HEAD main, tag, PR aperte e workflow GitHub Actions.
2. Leggere il rapporto più recente, oggi `Superstar3900_Rapporto_Tecnico_V7.6.md` e `03_Verifiche/V7.6/RAPPORTO_TECNICO_V7.6.md`, la specifica V7.6, ECO, BOM e netlist. Se main è passato alla V7.7 o successiva, NON tornare indietro.
3. Stato V7.6: RTL comportamentale Verilog per strobi /8 e /640 e FIFO virtuale con fault bloccati, **testbench Icarus PASS**, **92/92 Python PASS** in CI su PR #6 [run 42814827870](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42814827870). Segnali RF e rilascio PD sempre zero; simulazione NON equivale a firmware FPGA. Pin-plan SG48 candidata 48 pin + paddle, PCF **HOLD / non verificato contro XLSX vendor originale**, nessun place-route, PCB o collegamento RF.
4. Prossima revisione **V7.7**: verificare XLSX ufficiale Lattice document_id=51971 e concludere il pinout FPGA senza inventare pad; implementare un TOP HDL simulabile e qualificare sintesi/constraints quando disponibili; monitor esterno di arresto clock, supervisor POR/PD analogico indipendente, analisi single-fault, DAC 10bit quantizzato, DSP su multitoni/transitori e filtro Q/SRF vendor.
5. Conservare i file storici e la baseline immutabile, usare un branch provvisorio per sviluppare, eseguire test/regressioni reali, scrivere report con PASS/FAIL/SKIP/NON ESEGUITO, e integrare in **main** dopo verifiche superate. Non accettare green CI numerica come approvazione KiCad/ERC/DRC, EMI o safety hardware.
6. **NO FAB / NO TX senza eccezioni.** Il DAC900 PD pin15 active-high con pulldown interno, oscillatore ASDMB STANDBY active-low, FPGA con GPIO non definiti durante avvio e GND sul paddle richiedono verifica fisica indipendente. Tutti i componenti e ponti del TX sono DNP; nessun finale RF o antenna TX collegata; non abilitare PTT/emissioni.

**Messaggio minimo:** Riprendi Superstar 3900 SMD Evolution dal repository GitHub privato `jd3485/Superstar3900-SMD-Evolution`; verifica `main`, leggi README, protocollo e rapporto tecnico più recente, poi continua la revisione successiva con test e merge in main, mantenendo **NO FAB / NO TX**.

---

## ARCHIVIO — istruzioni storiche V7.5 e precedenti

# RIPRENDERE IN QUALSIASI NUOVA CHAT — SUPERSTAR 3900 SMD EVOLUTION V7.5

**Fotografia 10 novembre 2026: V7.5 INTEGRATA IN MAIN** tramite PR #5, merge `a5ef405f9500c114e8a4d56d7f9b17ba5a89caf1`. Tag `v7.0` storico preservato, non ultimo ramo. Le sezioni V7.4/V7.3/V7.2 ecc. più sotto sono solo archivio.

## Procedura permanente di ripresa
1. Aprire GitHub privato `jd3485/Superstar3900-SMD-Evolution` e leggere `README.md`, questo file e `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`. Verificare **ULTIMO COMMIT SU MAIN**, tag, PR aperte e workflow GitHub Actions prima di decidere la revisione attiva.
2. Leggere `Superstar3900_Rapporto_Tecnico_V7.5.md`, `03_Verifiche/V7.5/RAPPORTO_TECNICO_V7.5.md`, `01_Specifiche/V7.5/ARCHITETTURA_CLOCK_UNICO_DSP_V7.5.md` ed ECO, BOM/netlist. Se `main` ha una revisione successiva, usare QUELLA.
3. Stato V7.5: clock matematico comune 30,72MHz/8=3,84MHz DAC e /640=48kHz audio, oscillatore Abracon ASDMB candidato **4 pin DNP**, bridge Lattice iCE40UP5K QFN48 candidato **DNP senza pin mappati**; FIR multistadio 5×4×4 e analisi spettrale 750Hz solo offline, **77 test software PASS in CI** [run 42810514397](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42810514397). Nessuna simulazione HDL o MCU runtime, PCB o circuito TX montato.
4. **Prossima V7.6**: pinout/constraints FPGA verificati, RTL di prova simulabile, controllo POR/PD realmente fail-closed proposto ma NON ancora montato, clock reset indipendente, calcolo spettrale multitono/transitori del nuovo interpolatore, Q/SRF e filtro analogico con dati vendor; proseguire progressivamente nei blocchi RX/TX evitando salti alla produzione.
5. Ogni revisione: specifiche, BOM, pin-to-net solo se verificati, algoritmi o modelli funzionanti, CI e regressioni; distinguere **PASS / FAIL / SKIP / NON ESEGUITO** nel rapporto, conservare tutto lo storico, usare branch temporanei e unire in `main` solo dopo controlli realmente superati.
6. **SICUREZZA INVARIABILE: NO FAB / NO TX**. DAC900 PD pin15 è active-high con pulldown interno: non lasciarlo flottante in eventuali studi futuri; ASDMB STANDBY pin1 è active-low con high/open=ON. Software e FPGA non sono interblocchi fisici indipendenti. Tutti gli IC e ponti TX DNP, nessuna RF/PA/antenna connessa, KiCad/ERC/DRC e hardware NON ESEGUITI.

**Messaggio sufficiente:** Riprendi Superstar 3900 SMD Evolution da `jd3485/Superstar3900-SMD-Evolution`. Leggi i tre documenti di continuità e il rapporto più recente su main, verifica CI e continua la revisione successiva, integrando in main con NO FAB / NO TX.

---

## ARCHIVIO STORICO — istruzioni riferite a V7.4 E PRECEDENTI

# CONTINUITA NUOVA CHAT — SUPERSTAR 3900 SMD EVOLUTION V7.4

**Versione progettuale integrata al 10 novembre 2026: V7.4 su main**, PR #4, commit merge f92220b0e789673cb927f4e21a72ed4d16b92faf. Il tag v7.0 rimane la vecchia baseline intatta e NON sostituisce l'HEAD di main. Le intestazioni delle revisioni V7.3/V7.2/V7.1/V7.0 sotto questa sezione sono **storico**.

## Come riprendere in una chat futura
1. Accedere al repository GitHub privato jd3485/Superstar3900-SMD-Evolution, leggere README.md, questo file e 00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md. Verificare SEMPRE ultimo commit main, tag, PR aperte e GitHub Actions prima di prendere decisioni.
2. Leggere l'ultima versione del rapporto tecnico (attualmente Superstar3900_Rapporto_Tecnico_V7.4.md e 03_Verifiche/V7.4/RAPPORTO_TECNICO_V7.4.md), poi la specifica V7.4, ECO e BOM. In presenza di V7.5 o revisione maggiore già su main, usare quella; non ripartire automaticamente da V7.4.
3. Stato tecnico V7.4: solo modelli software, 10bit DAC900E virtuale, FIFO fault latched, clock 3.84MHz, I/V 49.9Ω+49.9Ω ispirato a TI Fig.6, **tutto DNP**. 21 nuovi test e 34 regressioni precedenti, **55/55 PASS** verificati in CI [run 42807026035](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42807026035). Tutti gli switch/PA/antenna TX rimangono fisicamente assenti; R7503 separa IOUT da F7401 come **vincolo DNP concettuale**, non scheda montata.
4. **Sviluppare V7.5:** scegliere un circuito clock 48k/3.84MHz sincronizzato e bridge dati con MPN/pinout documentati; analizzare PD hardwired, power rails e reset sicuri; sviluppare IOUT/IOUTB, carichi analogici e filtro LC realmente selezionabili, ottimizzare DUC adatto alle risorse MCU/FPGA, mantenere interfaccia TX completamente disabilitata.
5. Ogni revisione: specifica funzionale concreta, BOM, netlist pin-to-net solo quando i pin del produttore sono verificati, software e verifiche riproducibili, regressioni CI, report distinguendo PASS/FAIL/SKIP/NON ESEGUITO, storico intatto. Il branch serve ai test, poi eseguire merge in main se coerente.
6. **NO FAB / NO TX sempre**: non produrre PCB né abilitare PA/antenna, PTT o RF. KiCad/ERC/DRC, SPICE vendor, EMI/EMC, clock, DATI DAC, protezioni PD e test di trasmissione reali non sono stati eseguiti.

**Messaggio sufficiente nella nuova chat:** Riprendi Superstar 3900 SMD Evolution dal mio repository privato jd3485/Superstar3900-SMD-Evolution, verifica main, leggi README e protocollo, continua la revisione successiva con CI, integra in main e mantieni NO FAB/NO TX.

---

## ARCHIVIO — istruzioni storiche dalla V7.3 in poi

# RIPRENDERE IL PROGETTO — V7.3 IN MAIN · 10 NOVEMBRE 2026

**La V7.3 è già integrata in `main` tramite PR #3, merge `9f64126f5490d34921da726d41354518b34be9a7`.** Questa sezione prevale sugli stati V7.2, V7.1, V7.0 e vecchi piani riportati in seguito. Il tag `v7.0` identifica la baseline storica, **non** la versione da cui riprendere il lavoro.

## Procedura permanente per la prossima chat
1. Aprire GitHub privato `jd3485/Superstar3900-SMD-Evolution`, leggere `README.md`, questo file e `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`. Verificare l'ultimo commit su **`main`**, eventuali PR/tag e test CI prima di avanzare la versione.
2. Leggere `Superstar3900_Rapporto_Tecnico_V7.3.md`, `01_Specifiche/V7.3/ARCHITETTURA_DUC_DAC_V7.3.md`, `00_Gestione_Progetto/ECO_INTEGRAZIONE_V7.3.md`, BOM e netlist. La V7.3 ha un DSP causale *offline* IF2 455kHz, DAC900E candidato **DNP**, LPF ricostruzione **solo matematica**, e **34/34 test software in CI PASS**. NESSUN hardware o TX.
3. **Prossima V7.4:** sviluppare concretamente il bridge/clock per DAC e l'interfaccia corrente→tensione e filtraggio a 455kHz con componenti veri e pin verificati, budget alimentazioni, architettura DSP più efficiente. **Non** supporre che STM32G474 possa emettere direttamente 3,84MSa/s paralleli, né che una LPF 50Ω si adatti automaticamente al DAC in corrente.
4. Revisioni successive: aggiungere schemi candidati, BOM, netlist pin-to-net solo se documentata, MCU/firmware/modelli, verifiche numeriche riproducibili e regressioni con esiti **PASS/FAIL/SKIP/NON ESEGUITO**; preservare lo storico e integrare in `main` al superamento delle verifiche dichiarate.
5. **NO FAB / NO TX**: tutti i componenti TX nelle V7.1–V7.3 DNP, uscita mixer non instradata; KiCad/ERC/DRC e misure su hardware NON ESEGUITI. Nessun finale RF o antenna connessa.
6. Se `main` è avanzato ancora rispetto a queste note, prevalgono gli **ultimi commit e rapporti realmente presenti**, non questa fotografia. La continuità dipende dal repository, non dalla memoria della chat.

---

## ARCHIVIO STORICO — istruzioni riferite a V7.2 e revisioni precedenti

# RIPRESA IN QUALSIASI NUOVA CHAT — V7.2 INTEGRATA SU MAIN

**10 novembre 2026: la V7.2 è integrata in `main` dalla PR #2 (merge `faab93ea00d64d43b3d4977a5a43f512977043a9`).** Questa intestazione prevale sui vecchi stati V7.1 e V7.0 presenti in archivio qui sotto. Il tag `v7.0` è storico e immutabile: la versione da riprendere è quella del **commit più recente su `main`**.

## Procedura di continuità obbligatoria
1. Apri il repository GitHub privato `jd3485/Superstar3900-SMD-Evolution`, leggi `README.md`, questo file e `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`, quindi verifica HEAD `main`, tag, PR e CI.
2. Apri il **rapporto tecnico più recente** (oggi `Superstar3900_Rapporto_Tecnico_V7.2.md` e `03_Verifiche/V7.2/RAPPORTO_TECNICO_V7.2.md`), l'ECO, le BOM e le netlist. Se esiste una revisione più recente su `main`, **usa quella**.
3. **Prossima V7.3** da V7.2: selezione concreta DAC/clock e filtro di ricostruzione 455kHz su datasheet, trasformazione del DUC/Hilbert in algoritmo causale a stato per audio non periodico, budget MCU realistico e verifiche offline di spur/occupazione. Non collegare alcun PA, antenna o rete RF TX, non abilitare PTT/TX.
4. Per ogni revisione aggiungi specifiche, distinta candidati, netlist pin-to-net quando fisicamente documentata, firmware/modello pertinente, test, regressioni, rapporto con **PASS/FAIL/SKIP/NON ESEGUITO** e criticità. Conserva lo storico e integra in `main` dopo verifiche realmente superate.
5. **NO FAB / NO TX** permanente; i componenti V7.1 e V7.2 della catena TX rimangono **DNP** e l'uscita RF non è instradata. Nessuna dichiarazione inventata di test KiCad ERC/DRC, ngspice, EM o misure hardware.

**Contesto breve:** V7.2 DUC multitonale offline 48kHz→3.84MSa/s a IF2 455kHz, Hilbert 257-tap, AM/FM/USB/LSB/CW; 11 test V7.2 + 8 V7.1 superati in CI, 270 canali verificati, filtri analogici ancora solo ideali. La verifica CI è documentata nel rapporto e su GitHub Actions. Le revisioni precedenti qui sotto sono **storico**, non nuove istruzioni.

---

## ARCHIVIO: istruzioni al tempo di V7.1

**Decisione del 10 novembre 2026: la revisione progettuale integrata più recente deve essere su `main`.** V7.1 è stata incorporata in `main` con la PR #1 (merge `4c3585c`). L'ultima baseline taggata, `v7.0`, rimane intatta e recuperabile. **TX RF sempre scollegata e vietata; NO FAB.**

**Sequenza obbligatoria alla ripresa:** (1) aprire GitHub privato `jd3485/Superstar3900-SMD-Evolution`; (2) leggere `README.md`, questo file e `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`; (3) controllare l'ultimo commit `main`, i tag, le PR e la CI prima di scegliere la revisione; (4) leggere il rapporto tecnico più recente e i relativi file BOM/netlist/test; (5) continuare un modulo concreto, verificare ciò che è realmente verificabile e aggiornare rapporti e istruzioni; (6) integrare in `main` quando la revisione candidata è coerente e le verifiche dichiarate sono controllate. Se ci sono errori o rischi bloccanti, non forzare il merge.

**Prossimo obiettivo dalla V7.1: V7.2**, generazione IF2/DUC a 455kHz e modulazione multitonale, filtri di selezione IF/RF e fail-closed, senza collegare un finale o un'antenna TX. Non confondere test numerici con KiCad ERC/DRC o prove hardware: **NON ESEGUITI** finché non verificati.

**Nota di continuità:** il contesto deve essere ricostruito dal repository in ogni nuova chat; non dipendere dalla memoria di una chat precedente. Se `main` nel frattempo è avanzato, scegliere **la revisione successiva all'ultimo commit/reporto presente**, non tornare indietro alla V7.1.

---

# RIPRENDERE SUPERSTAR 3900 — V7.1 CANDIDATA, STATO 10 NOVEMBRE 2026

**Verificare prima commit/tag/branch su GitHub.** Il tag `v7.0` rimane la baseline tecnica immutabile. La V7.1 è un overlay di studio ora **integrato in main** via PR #1, NON una radio completa né una TX funzionante.

1. Leggere questo aggiornamento, README, `03_Verifiche/V7.1/RAPPORTO_TECNICO_V7.1.md`, `01_Specifiche/V7.1/ARCHITETTURA_TX_IF_INIBITA_V7.1.md`, BOM, netlist ed ECO V7.1. La PR #1 è stata integrata; usare `main` per recuperare la V7.1.
2. V7.1 ha definito IF2 455kHz → IF1 10.695MHz → RF di canale con prodotti immagine 9.785MHz e 47.005–49.695MHz; modello Python offline per cinque modi. Tutti i componenti/collegamenti TX sono DNP e il nodo RF non viene instradato.
3. **Prossima V7.2**: generatore 455kHz/DUC e vera modulazione audio a più toni + selezione dei filtri IF/RF con dati e simulazioni; non collegare TX RF o finale, non inventare firmware DAC/PLL validato.
4. Regole invariabili: storico intatto, BOM e netlist, test reali con PASS/SKIP/NOT_RUN separati; ERC/DRC nativo, fabbricazione, laboratorio e trasmissione RF NON autorizzati. Non trattare la documentazione storica V6.x/V7.0 sotto questa sezione come stato più recente di `main`.

---

# RIPRENDERE SUPERSTAR 3900 SMD EVOLUTION — STATO CORRENTE V7.0

**Aggiornamento 9 novembre 2026: il repository GitHub privato è stato popolato con la baseline V7.0 e il tag `v7.0`.** Tutte le sezioni storiche V6.x che seguono sono soltanto archivio; non usarle per determinare la prossima revisione.

## Procedura per una NUOVA CHAT
1. Collega GitHub se necessario e apri **`jd3485/Superstar3900-SMD-Evolution`** (repository PRIVATO). Verifica il tag più recente e il branch `main`. L'ultima versione tecnica nota a questa nota è **V7.0**; se esistono commit/tag successivi, controlla prima i loro rapporti.
2. Leggi `README.md`, `Superstar3900_Rapporto_Tecnico_V7.0.md`, `03_Verifiche/V7.0/RAPPORTO_TECNICO_COMPLETO_V7.0.md`, `00_Gestione_Progetto/ECO_INTEGRAZIONE_V7.0.md`.
3. Prossimo modulo da sviluppare **V7.1: TX modulatore e FI/upconversion candidati**, con PTT/RF sempre interbloccati e finale RF scollegato. Prosegui poi sugli altri moduli, senza affermare che la radio sia completa.
4. Ogni revisione: specifiche, BOM, netlist pin-to-net, MCU/firmware se pertinente, verifiche numeriche riproducibili, regressioni e rapporto che distingua PASS, NON ESEGUITO e criticità. Sorgenti storici intatti; snapshot o commit tracciati per i cambiamenti ai documenti gestionali.
5. **NON dichiarare fabbricazione pronta, KiCad ERC/DRC o collaudo hardware eseguiti. NON abilitare TX RF.** Sono ancora aperti: immagine RX, termica/PLL, filtro 455k, livelli LO2, schema nativo, alimentazioni e sicurezza.
6. `MANIFEST_SHA256_V7.0.csv` rappresenta il contenuto del **tag v7.0**: verificare quello; il branch `main` evolve e non deve essere confrontato contro il manifest immutabile del vecchio tag.

## Messaggio sintetico da incollare
> Riprendi Superstar 3900 SMD Evolution dal repository GitHub privato `jd3485/Superstar3900-SMD-Evolution`. Leggi `README.md` e `RIPRENDI_IN_UNA_NUOVA_CHAT.md` nelle loro prime sezioni aggiornate, verifica l'ultimo tag disponibile, consulta il rapporto tecnico più recente e continua con la revisione successiva. Preserva lo storico, esegui verifiche reali e mantieni TX RF fisicamente disabilitata fino a validazione.

---

## ARCHIVIO STORICO — istruzioni precedenti V6.8 e precedenti, conservate integralmente

# Riprendere il progetto dalla V6.8

1. Leggere `Superstar3900_Rapporto_Tecnico_V6.8.md` e `01_Specifiche/V6.8/CIRCUITO_FI_AGC_V6.8.md`.
2. Prossima **V6.9**: definire generatore LO2 e BFO (10.2385–10.2415MHz; 453.5/455.7/456.5kHz), filtri SSB/CW realizzabili, selettore 455 e demodulatori AM/FM/SSB/CW, con test e modelli numerici.
3. Non presupporre che sia già terminata la radio: RX/TX antenna switch, protezione e filtri, LO e demod, firmware, PCB, finale RF e ATU aperti. TX fisicamente OFF.
4. Eseguire verifiche incrementali REALI in chat; dichiarare NOT_RUN per KiCad/ngspice/EM/hardware dove non disponibili; poi verifica completa sul computer dell'utente.
5. Per ripristinare V6.7 consultare `09_Archivi_Precedenti/Snapshot_Integrali_V6.7/`; preservare tutti i 1.211 file storici.

---

## Stato precedente V6.7

# Come riprendere Superstar 3900 SMD Evolution dalla V6.7

1. Leggere `Superstar3900_Rapporto_Tecnico_V6.7.md` e `README.md`.
2. Proseguire con V6.8: prima FI a 10,695MHz, filtri per AM/FM/SSB/CW, AGC e demodulazione RX.
3. Conservare tutte le revisioni e il manifesto SHA, non alterare sorgenti KiCad vecchi finché non si dispone di schematici finali.
4. Ogni revisione: aggiungere un modulo reale, eseguire test/modelli possibili, riportare in modo distinto verifiche eseguite e attività aperte.
5. ATTENZIONE: RX antenna fisica connessa alla TX **non progettata**, RClamp D701 DNI, isolamento e tensioni non qualificati, filtro immagini minimo 20dB vendor, interblocco PA e RX supply incompleto, NO FAB, NO TX.

---

## Istruzioni storiche V6.6

# RIPRESA PROGETTO SUPERSTAR 3900 — aggiornamento V6.6

Procedere con revisioni progressive cumulando file **senza perdere storico**; per ogni revisione eseguire calcoli e simulazioni realmente possibili. Progetto **RX+TX in sviluppo** ma **RF TX permanentemente disabilitata** nei candidati, **NO FAB/NO PCBWay**.

Ultima consegna V6.6: F501 preselettore 50Ω discreto LC 3 risonatori e variante commerciale preferenziale SXBP-27R5+ (24–31MHz, 50Ω, min20dB stopband immagine e IL max2.5dB a 25°C secondo datasheet; prestazioni PCB NON validate). Studio LC L1/L3=2µH, L2=22nH, Cserie=17.5pF per lato, Cshunt=1591pF; Q/SRF/feedthrough ipotizzati, nessun MPN induttori. Matrice Y/S su 270 canali, MC 4.000 campioni, test V6.6 50/50. Non approvare la rete LC: IL e return loss in molti scenari non soddisfano obiettivi interni provvisori; tenere conto che 20dB garantiti del filtro SMD NON equivalgono ai 53dB del precedente modello ideale.

Prossima V6.7: integrare filtro fisico, LNA ADL5535/storico front-end, posizione del preselettore rispetto a LNA e protection RX, calcolare blocchi di guadagno/rumore/dinamica e drive mixer +7dBm con esclusione fisica TX. Rimangono aperte termica PLL V6.4, IF/AGC/SSB/CW/FM, alimentazione RF TX, ERC/DRC, misure VNA, simulazioni SPICE vendor. Non dichiarare hardware collaudato.

Elaborati nuovi: `01_Specifiche/V6.6`, `03_Verifiche/V6.6`, `07_Componenti/BOM_PRESELETTORE_V6.6.csv`, `Superstar3900_Rapporto_Tecnico_V6.6.md`. Originali V6.5 integralmente recuperabili tramite snapshot per i 3 documenti aggiornati.

---

## RIPRESA STORICA V6.5 INTEGRALE

# Superstar 3900 SMD Evolution — V6.5

**Metodo:** costruzione modulare per tante revisioni con test e simulazioni incrementali, controllo globale finale e validazione KiCad sul PC quando tutti i moduli saranno definiti.

**V6.5**: mixer passivo ADE-1+ pinout vendor confermato, IF1 10,695 MHz, LO alto 36,310–39,000MHz, piano immagini 47,005–49,695MHz per 270 RX, presa LO obiettivo +7dBm. Modello BPF Butterworth ideale (N3, ordine analogico6) 25–29MHz: reiezione immagine minima ideale ≈53,46dB; **filtro NON sintetizzato come rete fisica**. FFT toni, 12.000 scenari fC/BW, 50 test e 8 suite selezionate PASS.

**Rischi aperti:** prestazioni LO +7dBm ancora da misurare, filtri RX/IF reali, demodulatori, AGC, rumore/linerarità, livello blocker, criticità termica PLL della V6.4; KiCad CLI ed ngspice non presenti. TX rimane OFF; NO FAB / NO TX.

File nuovi in `01_Specifiche/V6.5/`, `02_Piano_Frequenze/V6.5/`, `03_Verifiche/V6.5/`, `08_Firmware_Prototipi/V6.5/`, `07_Componenti/BOM_MIXER_FI_V6.5.csv`. Originali V6.4 presenti nel percorso originale o esatti negli snapshot V6.4. SHA: `MANIFEST_SHA256_V6.5.csv`.

---

## README storico V6.4 conservato integralmente

# Superstar 3900 SMD Evolution — V6.4

**Metodo confermato:** una revisione per volta con parti nuove, calcoli, test, simulazioni fattibili e archivi cumulativi; verifica integrale di simulazioni e KiCad quando l'intera progettazione sarà definita.

La V6.4 aggiorna il piano PLL/LO RX LMX2572 a **270 posizioni** (30 ALFA), LO **36,310–39,000 MHz**, prima FI candidata 10,695 MHz, VCO 4,64768–4,992 GHz in integer-N con TCXO 12,8 MHz / R10 e ÷128. Sono stati superati 60 test nuovi e 7 suite selezionate dalla V5.9 alla V6.4. Aggiunti piano CSV, schema funzionale, BOM, pin mapping, ECO alimentazione e modello firmware RX lock/PA. Nessun profilo registri LMX è stato inventato.

**CRITICITÀ**: TPS7A20 candidato 3V3_PLL supera il limite termico nella stima prudenziale a 150 mA/85°C; TCXO, filtro loop, RF matching, spur, KiCad e TICS Pro restano da verificare. **NO FAB / NO TX**, nessun prototipo fisico. Alla V6.3 preesisteva un budget PLL_LO 150 mA su 5V_RF: non sommare due volte.

Nuovi elaborati: `01_Specifiche/V6.4/`, `02_Piano_Frequenze/V6.4/`, `03_Verifiche/V6.4/`, `08_Firmware_Prototipi/V6.4/`, `07_Componenti/BOM_PLL_LO_V6.4.csv`. Originali attivi V6.3 in `09_Archivi_Precedenti/Snapshot_Integrali_V6.3/`. Prossima V6.5: mixer RF e prima FI, filtri e reiezione immagine. `MANIFEST_SHA256_V6.4.csv` per verificare integrità.

---

## Storico esatto della V6.3

# Superstar 3900 SMD Evolution — V6.3, revisione cumulativa

**Metodo:** aggiungere moduli e schemi candidati con test e simulazioni fattibili, conservando sorgenti storici; simulazioni complete e KiCad sul PC dell'utente dopo la progettazione di tutti i blocchi.

**Nuovo V6.3:** alimentazione con 79 riferimenti e 219 contatti funzionali, protezione LM74900-Q1, buck 5 V/3,3 V, LDO 3V3_A/1V8_CODEC e distribuzione audio/RF. 45 test V6.3 PASS, 25.000 combinazioni numeriche carico/rendimento, ramp ideale 13,8 V. La V6.2 viene preservata, le tre copie originali attive sotto `09_Archivi_Precedenti/Snapshot_Integrali_V6.2/`.

**FONDAMENTALE:** pin fisici NON verificati, schematico KiCad nativo NON prodotto, né ERC/DRC né ngspice; fusibile, TVS, MOSFET, correnti reali e finale RF non rilasciati. J907 PA RF e J902 test DNI. **NO FAB/NO TX.**

Nuovi file: `01_Specifiche/V6.3/SCHEMA_A_COMPONENTI_ALIMENTAZIONI_V6.3.md`, `01_Specifiche/V6.3/ALIMENTAZIONI_CANDIDATE_V6.3.json`, `07_Componenti/BOM_ALIMENTAZIONI_V6.3.csv`, `03_Verifiche/V6.3/RAPPORTO_TECNICO_V6.3.md`. Prossima V6.4: sintetizzatore PLL/LO e clock.

---

## Indicazioni di recupero, poi storico precedente (V6.2)

# Superstar 3900 SMD Evolution V6.2 — Stato per nuova chat

**Criterio attuale:** costruire progressivamente la radio completa, con controlli/simulazioni realmente disponibili per ogni revisione; verifica finale dell'intero sistema e KiCad dopo completamento architettura. NON FAB / NO TX.

**Novità V6.2:** schema tabellare a 61 componenti, 190 pin-rete del modulo interblocchi HW PA/TX e supervisione 3V3 + 13,8V; 31 test V6.2 e Monte Carlo 50.000 campioni. ECO meccanica SPDT PA, riserve MCU PB11/PB4 usate per watchdog/TX arm, reinstradamento AMP_SD/relè obbligatorio. J801 DNI aperto, FAULT_LOOP_OK da progettare, nessun finale RF connesso. Native KiCad ERC/DRC/analog SPICE NOT_RUN. Il progetto non è fabbricabile.

Aprire `01_Specifiche/V6.2/SCHEMA_A_COMPONENTI_INTERBLOCCHI_V6.2.md`, `03_Verifiche/V6.2/RAPPORTO_TECNICO_V6.2.md`, `03_Verifiche/V6.2/test_interblocchi_v62.py` e `00_Gestione_Progetto/REGISTRO_DECISIONI.md`. **Prossima V6.3: ingresso 13,8V e rail 5V/3,3V.** Storico V6.1 sotto `09_Archivi_Precedenti/Snapshot_Integrali_V6.1/`.

---

## Storico e note precedenti

# RIPRESA PROGETTO — Superstar 3900 SMD Evolution V6.1

Caricare l'archivio cumulativo `Superstar3900_SMD_Evolution_V6.1.zip`. Il progetto viene sviluppato **in molte revisioni progressive**: progettazione concreta, verifica e simulazioni possibili in ogni chat, controllo globale e KiCad nativo DOPO il completamento della radio.

**Ultima V6.1:** 156 componenti di scheda MCU/pannello, 476 pin-rete, STM32G474RET6 LQFP64, due MCP23017 0x20/0x21, 28 pulsanti/contatti, 4 spie; encoder PC10/11, CH9 PC13, PA PC0, PTT PA0. Rispettare codec V2.1 (WCLK PA9/43) e MUX audio V6.0. Sono disponibili modelli `panel_controller_v61.py` e `integration_audio_v61.py`, test 55+5 e simulazioni RC/tolleranze/rimbalzi.

**Piano prossime revisioni:** V6.2 interblocco HW TX/PA, power-good e AMP_SD, poi PLL, FI, TX, ATU, interconnessioni, firmware e meccanica. Nel finale analisi globale, KiCad, SPICE/RF e hardware. Non pretendere KiCad nativo in ambiente chat se non disponibile. Tutti i canali sono RX nello sviluppo, 40 vecchi marcatori TX SI in D NON sono permessi RF reali. TX fisicamente disabilitata finché manca gate hardware; 0 prototipi convalidati, NO FAB/PCBWAY.

---

# RIPRESA PROGETTO — Superstar 3900 SMD Evolution V6.0

Usa l'archivio cumulativo `Superstar3900_SMD_Evolution_V6.0.zip`; prima fase PROGETTAZIONE RADIO COMPLETA per tante revisioni, poi simulazioni e verifica KiCad su PC utente.

**V6.0:** circuito AUDIO/PA candidato U601 TMUX1308 PW16, U602 TLV9062 SOIC8, U604 TPA3111D1 PWP28, connettoristica J601/J602/J603/J604/J605/J606, 5 demod RX, MIC elettrete e doppio speaker BTL tramite DPDT.

Fonte per netlist: `01_Specifiche/V6.0/CIRCUITO_COMPONENTI_AUDIO_PA_V6.0.json`; `07_Componenti/BOM_AUDIO_PA_V6.0.csv`; nuova suite `03_Verifiche/V6.0/test_audio_pa_v60.py`. Firmware concettuale `08_Firmware_Prototipi/V6.0/audio_controller_v60.py`.

Prossimo sviluppo V6.1: MCU/pannello vintage e vera matrice pin, successivamente V6.2 interblocco HW PA/TX e AMP_SD. Continuiamo a costruire i moduli della radio **prima** delle simulazioni sistematiche e verifiche KiCad. TX inibita; 9 gate NO FAB aperti; hardware 0.

---

# RIPRESA — Superstar 3900 SMD Evolution V5.9 — 9 novembre 2026

Il committente desidera **sviluppo progettuale incrementale completo di tutta la radio in molte revisioni**, come prima, ma **non** una successione di revisioni dedicate soltanto a KiCad e audit del modulo RX. PRIMA finire schemi, moduli, firmware, PCB candidati e documentazione di ogni funzione; POI revisione globale, simulazioni RF/IF/audio/power, controlli KiCad col programma installato sul PC dell'utente, prototipi e misure. Durante la progettazione eseguire soltanto test software e controlli di coerenza necessari; problemi evidenti vanno corretti quando scoperti.

**V5.9 nuova:** contratti logici 26 moduli e 54 interconnessioni, piano modulare V6.0–V6.9, mappa architettura, studio audio/PA e modello fail-closed `audio_route_v59.py`. Il microfono e l'audio demodulato devono arrivare a ADC_L e ADC_R separati del codec. È previsto mux analogico RX 5:1 ancora da progettare. Nessuna scheda audio nuova fabbricabile e nessuna TX abilitata. Conservati tutti i 1025 file V5.8; copie documenti in `09_Archivi_Precedenti/Snapshot_Integrali_V5.8`.

**Prossima revisione V6.0:** progettazione dettagliata del modulo audio/PA con schema componenti candidati, mute, speaker, mux e connettori; non ripartire da un ennesimo solo audit KiCad. Data/completezza per singolo modulo e revisioni future in `00_Gestione_Progetto/PIANO_MODULI_COMPLETAMENTO_V5.9.md`.

**Vincoli sempre:** 270 RX A–F con ALFA, CH9 27,065 AM, AM/FM/USB/LSB/CW RX, PA audio senza RF, VOX/DW/RB/Echo/CTCSS-DCS/DSP/ATU/SWR-PEP; 37% stima storica, zero prototipi, 9 gate OPEN, KiCad nativo NOT_RUN, NO FAB/NO TX. Le simulazioni e KiCad non sono ancora state fatte, non promettere risultati certi.

---
## RIPRESA storica V5.8 e precedenti

# RIPRENDI — Superstar 3900 SMD Evolution V5.8 — 9 novembre 2026

Usare l'archivio cumulativo `Superstar3900_SMD_Evolution_V5.8.zip`. Lo ZIP comprende l'intero storico, CAD KiCad originale, schemi candidati, librerie, manuale illustrato V4.0 e tutte le istanze sperimentali. Nessun hardware validato, **NO FAB / NO TX**.

**Requisiti radio finale invariati:** stile Superstar 3900, bande A–F, 270 posizioni RX incluse ALFA, AM/FM/USB/LSB/CW in ricezione, CH9 AM emergenza, funzione PA senza emissione RF, VOX/Dual Watch/Roger Beep/Echo/CTCSS-DCS/DSP, strumenti SWR/PEP e tuner antenna. La TX rimane vietata fino alla verifica normativa e ad interblocchi indipendenti.

**V5.8:** audit geometrico di 13 piste su 6 reti RF e 70 via GND; max distanza centro-pista/centro-via 9,5811 mm su RF_ATTEN_IN. Il ritorno di corrente non è stato modellato e i quattro piani GND sono UNFILLED; non interpretare distanza via come problema RF certificato. 30/30 test V5.8 e 19/19 suite storiche. Modifiche al rame: nessuna. Lo studio ha prodotto `03_Verifiche/V5.8/AUDIT_RITORNO_RF_V5.8.json`, CSV e SVG. Eseguito lanciatore su macchina priva di KiCad 10: `NOT_RUN_KICAD_MISSING`, exit 5. I nove gate sono aperti e la percentuale documentale resta 37%.

**Passo necessario:** su macchina effettivamente dotata di KiCad 10 eseguire `python3 -B 03_Verifiche/V5.8/run_audit_e_kicad_v58.py --output REPORT_NATIVE_V5.8`, conservare tutti i JSON ERC/DRC/refill/parità. Confrontare GND dei SMA, attenuatore, pad U101 e vie termiche; acquisire CAD ufficiale TE e DFM scritto per VIPPO/stencil. Nessuna produzione prima di chiudere i gate.

Prompt ripresa: «Continua il Superstar 3900 SMD Evolution dal pacchetto cumulativo V5.8; richiedi soltanto report KiCad REALI, non toccare gli originali e mantieni NO FAB/NO TX.»

---
## Storico precedente

# RIPRENDI — Superstar 3900 SMD Evolution V5.7 — 8 novembre 2026

Ripartire dallo ZIP cumulativo `Superstar3900_SMD_Evolution_V5.7.zip`. Gli originali, il manuale d'uso illustrato, i sorgenti KiCad, i rapporti e tutti gli snapshot di documenti modificati sono conservati.

**Radio finale nelle specifiche:** stile Superstar 3900; 6 bande A–F, 270 posizioni RX (40+5 ALFA/banda), CH9 AM emergenza, AM/FM/USB/LSB/CW RX; PA con RF TX disabilitata; ALFA fisico, VOX, Dual Watch, Roger Beep, Echo, CTCSS/DCS, DSP, lettura SWR/PEP e tuner antenna. TX vietata fino a conformità normativa, interblocchi hardware e prove indipendenti.

**Stato V5.7:** quattro piani GND non riempiti; la V5.6 misurava 64 isole fisiche su F.Cu senza refill. La V5.7 ha stimato, non riempito, un contorno ideale continuo su ciascuno dei 4 strati: 70/70 vie GND entro le zone; 24 pad GND F.Cu sovrapposti alla zona ideale; margine rame via/bordo zona min 2,05 mm; 96,08% di superficie ideale F.Cu. Sono solo verifiche geometriche permissive, **non KiCad, non prova delle termiche, non elettricità verificata**. 30/30 nuovi test e 18/18 suite regressive. KiCad 10 mancante, ERC/DRC/parità/refill REALI `NOT_RUN`. 9 gate OPEN; TE SMA, VIPPO/stencil U101, stackup RF, termica e hardware da approvare. Prototipi testati zero; 37% stima documentale; NO FAB/NO TX.

**Priorità V5.8:** far eseguire `.github/workflows/kicad_native_v57.yml` manualmente su un repository autorizzato (non ancora pubblicato) oppure `run_piani_e_kicad_v57.py` su un PC con KiCad 10; recuperare e interpretare report ERC/DRC con `--refill-zones --schematic-parity`, controllando tutti i 64 gruppi pre-refill, gli spoke termici e il ritorno GND. Acquisire dati CAD TE e risposta DFM su U101; non ordinare PCB.

Prompt di ripresa: «Continua Superstar 3900 SMD Evolution dal pacchetto cumulativo V5.7, prima acquisisci eventuali report nativi KiCad, non alterare originali e mantieni NO FAB/NO TX».

---
## Storico precedente

# RIPRENDI — Superstar 3900 SMD Evolution V5.6 — 8 novembre 2026

Utilizzare il solo `Superstar3900_SMD_Evolution_V5.6.zip` per riprendere tutto il progetto; contiene manuale d'uso illustrato, sorgenti storici, programmi di verifica, report e snapshot di documenti aggiornati.

**Radio definitiva solo in specifica:** estetica Superstar 3900, 6 bande A–F, 270 posizioni RX (40+5 ALFA per banda), CH9, AM/FM/USB/LSB/CW, PA con TX RF disabilitato, VOX, Dual Watch, Echo, Roger Beep, CTCSS/DCS, DSP, ATU, SWR/PEP. TX fisicamente interdetta fino a verifiche normative/hardware e interblocchi.

**Ultima revisione V5.6:** audit topologico statico del rame F.Cu: 7/7 reti non GND in un unico gruppo ciascuna, massa GND in 64 gruppi prima delle 4 zone da riempire (24 con pad, 40 via-only). Test 23/23, regressioni 17/17, nessun errore statico segnale. Rame PCB V5.2 geometricamente identico a V4.8, originali intatti. KiCad native ERC/DRC/zone refill NON ESEGUITI, CI non lanciata, nessuna approvazione TE SMA/termica ADL5535/PCBWay. Nove gate V5.0 tutti OPEN. 37% storico stimato, 0 hardware validato. NO FAB/NO TX.

**Priorità V5.7:** far girare realmente KiCad 10 CLI/CI e acquisire ERC, DRC --refill-zones, controllo `unconnected_items` e parità schema/PCB. Verificare che le 64 isole F.Cu si connettano correttamente ai piani senza bridge mancanti; non attribuire loro 64 errori in assenza di zone fill. Acquisire CAD TE e approvazione produttore/assemblatore per le vie termiche U101, determinare stack-up e ritorno RF.

**Prompt per nuova chat:** «Riprendi Superstar 3900 SMD Evolution V5.6 dall'archivio ZIP; consulta README, RIPRENDI, registro decisioni e audit V5.6; verifica prima eventuali nuovi report KiCad nativi; non sovrascrivere sorgenti storici, non autorizzare fabbricazione né TX.»

---
## Note storiche V5.5 e precedenti

# RIPRENDI — Superstar 3900 SMD Evolution V5.5 — 8 novembre 2026

Allegare il solo archivio cumulativo `Superstar3900_SMD_Evolution_V5.5.zip` in una nuova chat. Leggere `README.md`, questo file, `03_Verifiche/V5.5/RAPPORTO_TECNICO_V5.5.md`, `00_Gestione_Progetto/REGISTRO_DECISIONI.md`, i gate V5.0 e la procedura KiCad V5.5.

**Radio finale in specifica (non costruita):** estetica Superstar 3900; sei bande A–F per 270 RX, ALFA e CH9, AM/FM/USB/LSB/CW, PA RX disabilitando RF TX, VOX, Dual Watch, Echo, Roger Beep, CTCSS/DCS, DSP, ATU, SWR/PEP. TX interdetta fino a verifiche fisiche, compliance e interblocchi indipendenti.

**V5.5:** screening geometrico indipendente F.Cu passato con soglia di analisi 0,30 mm; distanza minima 0,45 mm; cinque coppie di pad alla minima. Esclusi rame di zone non riempite e tutti i controlli KiCad nativi. 22 nuovi test e 16 regressioni software riusciti. Post-validatore JSON ERC/DRC e CI manuale preparati, NON eseguiti sul servizio GitHub né sul programma KiCad. GATE V5.0=9 OPEN, prototipi fisici=0, 37% stima storica, NO FAB/NO PCBWAY/NO TX.

**Priorità V5.6:** far realmente eseguire KiCad 10 sul progetto candidato V5.2, ottenere report `ERC`, `DRC_PARITY`, `STATUS` e `SUMMARY`, leggere i difetti ed effettuare modifiche su una nuova copia; ottenere CAD TE e conferma DFM VIPPO/stencil, verificare stack-up/termica. Non fabbricare né trasmettere.

**Messaggio riutilizzabile:** «Riprendi Superstar 3900 SMD Evolution V5.5 dall'archivio cumulativo. Leggi README/RIPRENDI/rapporto/registro, verifica eventuali report nativi KiCad acquisiti e conserva manuale, revisioni e gate. Nessun rilascio FAB o TX.»

---
## Stato della V5.4 e precedenti

# RIPRENDI — Superstar 3900 SMD Evolution V5.4 — 8 novembre 2026

**In una nuova chat allega soltanto** `Superstar3900_SMD_Evolution_V5.4.zip` e chiedi di leggere questo file, `README.md`, `03_Verifiche/V5.4/RAPPORTO_TECNICO_V5.4.md`, `00_Gestione_Progetto/REGISTRO_DECISIONI.md` e i gate V5.0.

**Radio finale prevista** (non hardware funzionante): estetica vintage Superstar 3900, 6 bande A–F/270 RX, ALFA e CH9, AM/FM/USB/LSB/CW RX, PA, VOX, Dual Watch, Echo, Roger Beep, CTCSS/DCS, DSP, ATU, SWR/PEP. TX disabilitata fino a conformità e collaudo.

**Stato V5.4:** revisione di automazione, non riprogettazione del PCB. Workflow `.github/workflows/kicad_native_v54.yml` e runner `03_Verifiche/V5.4/run_native_v54.py` predisposti per produrre veri report KiCad 10 **solo quando eseguiti** su un host compatibile. In questa sessione KiCad è assente; ERC/DRC/refill/parità = NOT_RUN. I test (8 simulati + 15 suite software) sono riusciti, non costituiscono ERC/DRC. Il workflow non è stato caricato su GitHub né eseguito. Nessuna approvazione esterna acquisita. 37% storico stimato, zero prototipi validati, NO FAB/NO PCBWAY/NO TX.

**Priorità:** ottenere rapporti nativi ERC/DRC con parità e refill; correggere gli eventuali errori su copia; completare TE DXF/STEP e approvazione DFM VIPPO/stencil, stack-up, termica. Conservare le vecchie versioni e manuali.

**Messaggio riutilizzabile:** «Riprendi Superstar 3900 SMD Evolution dal pacchetto V5.4. Leggi README, RIPRENDI, rapporto V5.4 e registro decisioni. Mantieni le revisioni cumulative; ottieni/esamina ERC/DRC KiCad veri e non autorizzare fabbricazione o TX.»

---
## Ripresa V5.3 e precedenti

# RIPRENDI — Superstar 3900 SMD Evolution V5.3 — 8 novembre 2026

**In una nuova chat allega unicamente** `Superstar3900_SMD_Evolution_V5.3.zip`. Leggi `README.md`, questo file, il rapporto V5.3, il registro decisioni e i nove gate V5.0.

**Radio finale (solo requisiti):** Superstar 3900 estetica vintage, 6 bande A–F e 270 RX, ALFA/CH9, AM/FM/USB/LSB/CW RX, PA, VOX, Dual Watch, Echo, Roger Beep, CTCSS/DCS, DSP, ATU e misure SWR/PEP. TX disabilitata.

**Stato verificato V5.3:** 37% stima storica, 0 hardware validato. Nessun file KiCad storico o candidato modificato. Audit indipendente della coppia V5.2: 15 componenti, 31 pin, 31 fili etichettati, 8 reti, nessuna divergenza statica; 18 nuovi test e 14 suite di regressione superati. **Non sono test nativi KiCad**. `kicad-cli` assente, ERC/DRC/refill/parità `NOT_RUN`. Non ci sono risposte DFM o collaudi reali. **NO FAB / NO PCBWAY / NO TX**.

**Priorità V5.4:** eseguire la procedura nativa `03_Verifiche/V5.2/run_kicad_v52.py` su PC KiCad 10, allegare ERC/DRC/parità e correggere errori reali su copia; acquisire modello CAD TE esatto e approvazione scritta VIPPO/stencil/termica e stack-up RF. Manuale illustrato `06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf`. Preservare tutto e produrre ZIP cumulativo con manifest SHA-256.

**Prompt da incollare:** «Riprendi Superstar3900 SMD Evolution dal ZIP V5.3 allegato. Leggi README, RIPRENDI, rapporto V5.3, registro decisioni e gate V5.0. Mantieni tutte le versioni; prosegui con KiCad nativo e qualifica TE/ADL5535 senza dichiarare hardware validato o autorizzare fabbricazione/TX.»

---
## Storico V5.2 e precedenti

# RIPRENDI — Superstar 3900 SMD Evolution V5.2 — 8 novembre 2026

**Per una nuova chat allegare soltanto** `Superstar3900_SMD_Evolution_V5.2.zip`. Leggere prima `README.md`, poi questo file, `03_Verifiche/V5.2/RAPPORTO_TECNICO_V5.2.md` e `00_Gestione_Progetto/REGISTRO_DECISIONI.md`.

**Radio completa richiesta:** estetica Superstar 3900; RX 270 posizioni su sei bande, ALFA/CH9, AM/FM/USB/LSB/CW RX, PA, VOX, Dual Watch, Echo, Roger Beep, CTCSS/DCS, DSP, ATU, strumenti SWR/PEP. Sono requisiti di progetto, NON funzioni hardware collaudate. TX disabilitata.

**Novità V5.2:** candidato separato di allineamento nativo schema/PCB, con 15 relazioni UUID e 15 riferimenti di progetto corretti rispetto alla copia V4.8. Rame, via, pad, zone e reti invariati; 12 test statici superati. **ERC/DRC KiCad non eseguiti**, CLI assente. V5.1 conserva BOM 15 componenti / 31 pin / 8 reti. Materiale di prova: `03_Verifiche/V5.2/`; candidato: `04_KiCad/Modulo_RX_Test_50ohm_V5.2_PARITY_LINK_STUDY_NOT_FOR_FAB/`.

**Bloccanti:** 9 gate di fabbricazione aperti; manca verifica nativa KiCad 10, CAD STEP/DXF TE, risposta scritta VIPPO/stencil, termica, stack-up 50 Ω, MPN e collaudi. **37% stima storica, 0 moduli funzionanti, NO FAB / NO TX.** Manuale in `06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf`.

**Prossimo passo:** eseguire `python3 03_Verifiche/V5.2/run_kicad_v52.py --output REPORT_NATIVE_V5.2` su computer KiCad 10; allegare i report nativi in nuova chat per correggere gli errori. Non autorizzare produzione sulla base dei soli test statici.

---
## Ripresa V5.1 e precedenti

# RIPRENDI — Superstar 3900 SMD Evolution V5.1 — 8 novembre 2026

**Allegare questo solo file ZIP `Superstar3900_SMD_Evolution_V5.1.zip` in una nuova chat.** Leggere nell'ordine `README.md`, questo file, `03_Verifiche/V5.1/RAPPORTO_TECNICO_V5.1.md`, `00_Gestione_Progetto/REGISTRO_DECISIONI.md` e `03_Verifiche/V5.0/GATE_RELEASE_V5.0.json`.

**Requisiti radio finale invariati:** look Superstar 3900, 270 posizioni RX su 6 bande, CH9, ALFA, AM/FM/USB/LSB/CW RX, PA, VOX, Dual Watch, Echo, Roger Beep, CTCSS/DCS, DSP, ATU, misure SWR/PEP; non sono funzioni collaudate. TX vietata sino a revisione autorizzata e conformità normativa.

**Cosa è nuovo V5.1:** dalla variante PCB V4.8 (non da hardware) sono stati ricavati una BOM preliminare **15 componenti** e un pin-net **31 connessioni / 8 reti**, con **13/13 test** statici; script e CSV in `03_Verifiche/V5.1/`. Bozza DFM per PCBWay non inviata. KiCad nativo non eseguito; gate R-01...R-09 tutti OPEN. PCB e schema invariati, manuale illustrato in `06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf`. **Stato 37% storico stimato, 0 hardware validato, NO FAB, NO TX.**

**Proseguimento:** eseguire la procedura `03_Verifiche/V5.1/ISTRUZIONI_VALIDAZIONE_ESTERNA_V5.1.md` su macchina KiCad 10 e conservare ERC/DRC/parità; acquisire CAD TE ufficiale e approvazione del processo VIPPO/stencil U101. In ogni futura revisione preservare integrali le versioni precedenti con manifest SHA-256 e backup dei documenti aggiornati.

Messaggio per nuova chat: «Riprendi Superstar 3900 SMD Evolution dal ZIP V5.1 allegato, leggi README, RIPRENDI e rapporto V5.1, conserva tutte le decisioni e le revisioni; parti dall'esecuzione KiCad nativa, CAD TE SMA e risposta DFM VIPPO senza autorizzare produzione o TX.»

---
## Storico V5.0 e precedenti

# RIPRENDI — Superstar 3900 SMD Evolution V5.0 — 8 novembre 2026

**Allega solo l'archivio `Superstar3900_SMD_Evolution_V5.0.zip`.** Leggi questo file, `README.md`, `03_Verifiche/V5.0/RAPPORTO_TECNICO_V5.0.md`, `00_Gestione_Progetto/REGISTRO_DECISIONI.md` e `03_Verifiche/V5.0/GATE_RELEASE_V5.0.json`.

**Radio finale richiesta:** estetica Superstar 3900, 6 bande A–F / 270 RX, ALFA, CH9, AM/FM/USB/LSB/CW RX, PA, VOX, Dual Watch, Echo, Roger Beep, CTCSS/DCS, DSP, ATU e misure SWR/PEP. Sono **specifiche**, non funzioni di un apparato già costruito. Trasmissione disabilitata fino a conformità, collaudo e approvazione.

**Stato V5.0:** 37% storico stimato, 0 moduli hardware validati. PCB originale V3.8, candidato SMA V4.3, librerie portabili V4.5 e variante U101 con sei via-in-pad V4.8 conservati separati e TUTTI NOT_FOR_FAB. V5.0 confronta due geometrie di stencil: 81% pasta esistente con riempimento/cappatura da validare, contro 29,69% di due finestre evitando i fori, studio non raccomandato per produzione senza verifica montaggio/termica. **Nessun file KiCad del PCB o dello schema è stato modificato.**

**Non eseguiti:** KiCad ERC/DRC/refill/parità nativi (CLI assente), qualifica CAD TE STEP/DXF completa, approvazione PCBWay e assemblatore VIPPO, stack-up 50 Ω, termica, collaudi RF. Sono nove i gate aperti nel `GATE_RELEASE_V5.0.json`. NO FAB / NO PCBWAY / NO TX.

**Manuale illustrato:** `06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf`. Per il prossimo passo eseguire sul proprio PC KiCad 10 il lanciatore `03_Verifiche/V5.0/run_kicad_native_v50.py`, allegando i report in una nuova chat, e ottenere conferme scritte di produttore/assemblatore. Nel frattempo preservare ogni revisione in uno ZIP cumulativo con manifest SHA-256, senza dichiarare test fisici inesistenti.

**Messaggio pronto per nuova chat:** «Riprendi Superstar 3900 SMD Evolution dal ZIP V5.0 allegato; leggi README, RIPRENDI, rapporto V5.0, registro decisioni e gate di rilascio. Mantieni manuali e sorgenti storici; prosegui da KiCad 10 nativo, CAD TE e risposta DFM VIPPO/stencil; non autorizzare produzione o TX e prepara solo revisioni cumulative verificabili».

---
## Handoff storico V4.9 e precedenti

# RIPRENDI — Superstar 3900 SMD Evolution V4.9 — 8 novembre 2026

**Allega questo archivio intero:** `Superstar3900_SMD_Evolution_V4.9.zip`, NON un singolo file KiCad. Conserva le revisioni cumulative e tutti i manuali. Inizia da `README.md`, `00_Gestione_Progetto/REGISTRO_DECISIONI.md` e `03_Verifiche/V4.9/RAPPORTO_TECNICO_V4.9.md`.

**Radio finale desiderata (requisiti, non apparecchio reale):** estetica Superstar 3900, 6 bande A–F / 270 RX, ALFA, CH9, AM/FM/USB/LSB/CW RX, PA, VOX, Dual Watch, Echo, Roger Beep, CTCSS/DCS, DSP, ATU, misure SWR/PEP. TX disabilitata, subordinata a verifica normativa e hardware.

**Stato V4.9:** 37% storico stimato; 0 prototipi validati; PCB V3.8 originale invariato, candidati SMA V4.3, KiCad portabile V4.5 e sei vie U101 V4.8 separati, **tutti NON FAB**. Questa revisione non modifica PCB/schema/footprint. È stato rilevato che tutti e 6 i fori termici Ø0,25 mm della V4.8 ricadono completamente nell'apertura F.Paste teorica 1,62×3,132 mm (pad 1,80×3,48 mm). Occorre decisione scritta su VIPPO/riempimento/cappatura, stencil e ispezione, oltre a stack-up RF. PCBWay ha capacità pubbliche generali ma non ha approvato questa scheda; nessun contatto/invio è stato fatto.

**Non eseguiti:** ERC/DRC/refill/parità nativi KiCad, confronti TE DXF/STEP, analisi termiche validate, misure RF e collaudi reali. NO PCBWAY, NO FAB, NO TX.

**Nuovi materiali:** `03_Verifiche/V4.9/` per audit, test, report e procedura KiCad; `05_Produzione_PCBWay/RICHIESTA_FATTIBILITA_V4.9.md` per chiedere in futuro valutazione di producibilità, non un ordine. Manuale illustrato in `06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf`.

**Prossima milestone V5.0:** acquisire CAD TE del componente esatto, eseguire ERC/DRC KiCad nativi su copia e ottenere risposte scritte da fabbricante e assemblatore prima di modificare lo stencil o ordinare la scheda. Conservare ogni revisione con backup byte-identici dei documenti attivi, manifest SHA-256 e test; non incrementare la percentuale senza risultati hardware.

**Prompt per nuova chat:** «Riprendi Superstar3900 SMD Evolution V4.9 dallo ZIP allegato. Leggi README, RIPRENDI, registro decisioni e rapporto tecnico V4.9; conserva manuali e ogni revisione. Prosegui i gate DFM VIPPO/stencil U101, CAD TE e ERC/DRC KiCad su copia senza approvare produzione né TX. Crea archivio cumulativo con hash verificati.»

---
## Ripresa storica V4.8 (per rintracciabilità)

# RIPRENDI — Superstar 3900 SMD Evolution V4.8 — 8 novembre 2026

Allega `Superstar3900_SMD_Evolution_V4.8.zip` a una nuova chat. Leggi nell'ordine: `README.md`, `00_Gestione_Progetto/REGISTRO_DECISIONI.md`, `03_Verifiche/V4.8/RAPPORTO_TECNICO_V4.8.md`, `03_Verifiche/V4.8/AUDIT_VARIANTE_TERMICA_V4.8.json`.

**Radio finale**: estetica Superstar 3900; 6 bande RX 270 posizioni, ALFA, CH9, AM/FM/USB/LSB/CW RX, PA, VOX, Dual Watch, Echo, Roger Beep, CTCSS/DCS, DSP, ATU, strumenti PEP/SWR. Requisiti, non hardware funzionante. TX legalmente limitato e NON ABILITATO.

**Stato V4.8**: conservati tutti i sorgenti V3.8–V4.7; manuale illustrato in `06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf`. 37% stimato, 0 moduli hardware collaudati. NO PCBWay/NO TX. La V4.8 aggiunge solo un PCB *candidato* con sei via-in-pad GND sotto U101, NON approvato; il datasheet ADL5535 mostra una matrice di vie, ma il processo di riempimento/cappatura e lo stencil non sono definiti. Lo schema e il pad di pasta non sono modificati. KiCad non installato: ERC/DRC/parity/refill non eseguiti. DXF/STEP ufficiali TE non acquisiti: SMA non approvati.

**Prossimo passo**: sottoporre via-in-pad/stencil a PCB maker e assemblatore, ottenere DXF/STEP TE del componente esatto, eseguire ERC/DRC nativi su una copia, acquisire stack-up 50 Ω, validare termica e S-parametri di un prototipo. NON ordinare PCB prima dei gate.

**Per verificare la variante**: `python3 03_Verifiche/V4.8/test_variante_termica_v48.py` (10 test). Per verifiche native su macchina KiCad 10: `bash 03_Verifiche/V4.8/RUN_KICAD_CANDIDATO_V48.sh` (non deve dichiarare esito se assente).

**Prompt per nuova chat**: «Riprendi Superstar 3900 SMD Evolution dall'archivio V4.8. Leggi README, RIPRENDI, registro decisioni e rapporto V4.8; conserva ogni sorgente e il manuale. Verifica termica via-in-pad e stencil, footprint SMA TE e DRC/ERC KiCad 10. Mantieni NO FAB/NO TX fino a validazione reale. Produci nuovo archivio cumulativo con manifest e snapshot».

---
## Storico delle istruzioni V4.7 e precedenti

# RIPRENDI — Superstar 3900 SMD Evolution V4.7 — 8 novembre 2026

**Per una nuova chat, allegare soltanto:** `Superstar3900_SMD_Evolution_V4.7.zip`. E' cumulativo: comprende tutte le revisioni, manuali, progetti e manifest.

**Radio finale (requisiti, non prodotto esistente):** aspetto Superstar 3900, 6 bande A–F con 270 posizioni RX, ALFA fisico, CH9 prioritario, AM/FM/USB/LSB/CW RX, PA, VOX, Dual Watch, Echo, Roger Beep, CTCSS/DCS, DSP, ATU e misure SWR/PEP. Le architetture PLL/MCU/codec sono candidate. TX soggetto a normativa e interblocchi.

**Stato reale:** 37% progettuale stimato, 0 moduli hardware validati. PCB V3.8 originale conservato; V4.3 candidato SMA e V4.5 librerie portabili con schema RX staticamente allineato, non approvati. NO FAB / NO PCBWAY / NO TX.

**Novità V4.7:** disegno TE C-CONSMA002-SMD-X-X rev D letto: pad centrale Ø2,05 mm e inviluppo GND 7,76 mm coincidono nello studio, ma DXF/STEP non acquisiti; geometria 3D, maschera e pasta non validati. U101 pad termico 1,80×3,48 mm con paste ratio -0,100 (circa 81% area nominale) non qualificato. 28 nuovi test statici + regressioni V4.0–V4.6 superati. KiCad 10 non disponibile: ERC/DRC/parità e refill NOT_RUN.

**Leggere per iniziare:** `README.md`, `00_Gestione_Progetto/REGISTRO_DECISIONI.md`, `03_Verifiche/V4.7/RAPPORTO_TECNICO_V4.7.md`, `03_Verifiche/V4.7/AUDIT_SMA_TE_V4.7.json`, `03_Verifiche/V4.7/CHECKLIST_ACCETTAZIONE_V4.7.csv`; manuale in `06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf`.

**Prossimi passi:** ottenere/importare DXF/STEP TE del part-number esatto; validare F.Cu/F.Paste/F.Mask e courtyard; completare analisi termica ADL5535 e stack-up RF; eseguire test nativi KiCad 10 su copie con la procedura già disponibile `03_Verifiche/V4.6/RUN_KICAD_RX_V46.sh`. Non dichiarare conformità in assenza dei rapporti. Confezionare sempre nuove revisioni cumulative con hash e snapshot.

**Prompt nuova chat:** «Riprendi Superstar3900 SMD Evolution dall'archivio V4.7 allegato. Leggi README, RIPRENDI, registro decisioni e rapporto V4.7. Conserva le revisioni storiche e il manuale; continua il confronto TE DXF/STEP, KiCad nativo e termica ADL5535 senza ordinare PCB o abilitare TX. Produci un archivio cumulativo verificato.»

---

## Handoff storico V4.6

# RIPRENDI — Superstar 3900 SMD Evolution V4.6 — 8 novembre 2026

**Allega in una nuova chat:** `Superstar3900_SMD_Evolution_V4.6.zip`, ZIP cumulativo con manuali, schemi, script, revisioni e manifest SHA-256.

## Radio finale desiderata (REQUISITI, NON ancora un apparato funzionante)

Estetica tradizionale Superstar 3900, sei bande A–F, 270 posizioni RX (40+5 ALFA ciascuna), AM/FM/USB/LSB/CW ricezione, PA senza RF, ALFA fisico, CH9 27,065 MHz AM prioritario, VOX, Dual Watch, Echo, Roger Beep, CTCSS/DCS, DSP, strumenti SWR/PEP, ATU. LMX2572, STM32G474RE e TLV320AIC3204 sono componenti/architetture candidate. Trasmissione solo nel rispetto di norme, collaudo e interblocchi hardware+firmware.

## Stato reale V4.6

- **37% stima progettuale, zero hardware validato, NO FAB / NO PCBWAY / NO TX.**
- PCB RX 110×62 mm sperimentale: V3.8 originale immutato; V4.3 candidato SMA distinto; V4.5 progetto portabile con tre librerie di footprint (9 modelli) e libreria di simboli (9 modelli). Schema/PCB staticamente coerenti con 15 componenti, 31 pin elettrici e 8 reti, **non verificati nativamente**.
- **Novità V4.6:** audit della geometria U101 ADL5535: paddle 1,80×3,48 mm, via più vicino Ø0,70/foro Ø0,30 mm, 0,50 mm distanza rame-rame; nessun centro di via sul paddle. Quattro zone GND ancora non riempite con KiCad. Niente prova di temperatura o dissipazione.
- Quattro SMA TE CONSMA002-SMD-G: footprint di studio V4.3 NON approvato; CAD ufficiale DXF/STEP disponibile da link TE, download non completato nella sessione. Non procedere con correzioni inventate.
- Nuova procedura `03_Verifiche/V4.6/RUN_KICAD_RX_V46.sh`: usa KiCad 10 se realmente disponibile, verifica opzioni CLI, esegue su copia e **non** genera Gerber. In questa sessione KiCad non installato, ERC/DRC/refill/parità **NON ESEGUITI**.
- 24 test statici V4.6 riusciti; regressioni V4.0–V4.5 riuscite, escluse verifiche hardware. Il manuale illustrato V4.0 rimane bozza.

## File iniziali da leggere

1. `README.md` e `00_Gestione_Progetto/REGISTRO_DECISIONI.md`.
2. `03_Verifiche/V4.6/RAPPORTO_TECNICO_V4.6.md` e `AUDIT_TERMICA_SMA_V4.6.json`.
3. `04_KiCad/Modulo_RX_Test_50ohm_V4.5_LIBS_PORTABILI_NOT_FOR_FAB/README.md`.
4. `03_Verifiche/V4.6/TEST_V4.6.txt`, `PROVA_NO_KICAD/STATUS.txt`.
5. `06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf`.

## Priorità V4.7

Ottenere disegno TE e STEP/DXF *del part number esatto*, fare il confronto completo con pad/paste/mask/courtyard/PCB e scegliere il footprint definitivo. Eseguire KiCad 10 nativo ERC+DRC con refill e parity; risolvere tutti gli errori e documentare warning residui. Progettare e giustificare il percorso termico/pasta saldante dell'ADL5535; fissare stack-up RF da produttore e misure VNA prima di qualsiasi prototipo RX. Mai abilitare TX in questa fase.

**Prompt per nuova chat:** “Riprendi Superstar 3900 SMD Evolution dall'archivio cumulativo V4.6 allegato. Leggi README, RIPRENDI, registro decisioni e rapporto V4.6. Conserva storici e manuale, prosegui da CAD TE, verifica termica ADL5535 e KiCad 10 nativo; non dichiarare collaudi inesistenti e non autorizzare fabbricazione o TX. Produci revisioni cumulative e manifest verificati.”


## V6.9 — LO2, BFO e demodulazione (9 novembre 2026)

Nuovi circuiti candidati U971 SI5351C 20-QFN, U981 TS5A3157, demod AM/FM provvisori; 1.350 profili e 70 test nuovi, 541 selezionati. Restano non realizzati il buffer +7dBm, filtri SSB/CW, demod FM hardware, interlock output indipendente, ERC/DRC e hardware. **Non fabbricare e non trasmettere.** Vedi 03_Verifiche/V6.9/RAPPORTO_TECNICO_COMPLETO_V6.9.md.


## V7.0 — RX IF2 AM/FM / driver LO2 / FIR SSB-CW (9 novembre 2026)

V7.0 overlay nuovo: U7101 AD8307 AM, U7102 TLV3201 comparator, U7103 HC4046 PLL FM, U7104 TLV9062 buffer, U7121 GALI-3+ driver LO2 e LPF a 50ohm; FIR post-demod 48kHz Q15. Test: 75/75 nuovi, 616/616 selezionati. D991/B991/B992 precedenti DNP, F823/F824 455k DNP, GALI LO2 +7dBm non verificati. ECO 00_Gestione_Progetto/ECO_INTEGRAZIONE_V7.0.md e report 03_Verifiche/V7.0/RAPPORTO_TECNICO_COMPLETO_V7.0.md. **NO FAB / NO TX.**
