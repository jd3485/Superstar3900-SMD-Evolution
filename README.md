# SUPERSTAR 3900 SMD EVOLUTION — V7.13 CAD NATIVO INTEGRATA IN MAIN

**10 novembre 2026:** V7.13 su `main`, [PR #13](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/13), merge `81928a6fc36f6e3bb98c04338026a4ed2f78769d`. Questo è uno stato SOFTWARE/CAD DIAGNOSTICO, non una release per fabbricare. Verificare sempre ultimo HEAD, PR, tag e Actions in una nuova chat; `v7.0` baseline storica conservata.

## Nuovo avanzamento V7.13 (KiCad autentico, non soltanto documentazione)
- Creato lo schema nativo `04_KiCad/Modulo_RX_Test_50ohm_V7.13_GRID_NOT_FOR_FAB/S3900E_RX_GRID_V7_13_NOT_FOR_FAB.kicad_sch`. **15 simboli, 31 wires, 31 labels** riallineati a 1,27mm /50mil. Nuovo root 7-sheet `04_KiCad/Assemblaggio_RX_Power_V7.13_GRID_NOT_FOR_FAB/S3900E_RX_POWER_V7_13_GRID_NOT_FOR_FAB.kicad_sch`, AUX e MCU ancora **NON collegati elettricamente**. Sorgenti V7.12 intatti, PCB RX V7.12 NON modificata.
- **Native KiCad9 sch export netlist**: tutti gli elementi `(nome rete, reference, pin)` della RX V7.12 e V7.13 risultano **identici**. **ERC RX endpoint_off_grid 46→0**, warning RX **76→30**, errori RX **0**. ERC root 7sheet **459→413 segnalazioni** (errori **43 invariati**, warning 416→370). Il gate misura vere esportazioni ERC, non simula il CAD.
- **Ancora bloccanti**: RX 15 warning `lib_symbol_issues` +15 `footprint_link_issues`, nonostante `sym-lib-table/fp-lib-table` locali (non qualificati), root **43 errori ERC**, PCB RX **85 violazioni DRC e63 unconnected** (70 dangling via +15 footprint). Ancora **15 interfacce power/MCU/RX OPEN/HOLD**, nessuna PCB completa; pinout SG48 originale vendor HOLD.
- **CI finale PR #13** [run 42870757111](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42870757111), job 130021089653, SUCCESS: **10 nuovi V7.13 +13 V7.12 +8 V7.11 +12 V7.10 +143 V7.1–V7.9 =186 Python PASS, 0 FAIL/SKIP**. Regressioni DSP/PLL/firmware conservate; Icarus/Yosys non rieseguiti in V7.13.
- Rapporto `Superstar3900_Rapporto_Tecnico_V7.13.md`, spec `01_Specifiche/V7.13/GRID_NETLIST_EQUIVALENCE_V7_13.md`, ECO `00_Gestione_Progetto/ECO_INTEGRAZIONE_CAD_V7.13.md`, risultati JSON `03_Verifiche/V7.13/RISULTATI_VERIFICHE_V7_13.json`.

**Prossima V7.14:** risolvere veramente caricamento librerie simboli/footprint con progetto KiCad portabile e footprint vendor, poi 70 via dangling/63 nets RX tramite ritorni GND e routing verificati; ridurre 43 errori ERC root e qualificare gradualmente confini MCU/AUX/RX. Continuare DSP, firmware e simulazioni.

**Vincolo permanente NO FAB / NO TX:** nessuna nuova RF/TX attiva, DAC/FPGA/mixer/PA/antenna DNP/scollegati/non alimentati, nessun PCB finale o Gerber; una CI verde non dimostra sicurezza fisica. In una nuova chat leggere `RIPRENDI_IN_UNA_NUOVA_CHAT.md` e `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`.

---

## ARCHIVIO STORICO — V7.12 E PRECEDENTI (non revisione corrente)

# SUPERSTAR 3900 SMD EVOLUTION — V7.12 CAD NATIVO INTEGRATA IN MAIN

**10 novembre 2026:** V7.12 integrata su `main` con [PR #12](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/12), merge `aad39c250fe626fa94424ff9ce2c08cb6b9ebcc8`. Verificare sempre HEAD `main` all'inizio della prossima chat: se esiste versione successiva prevale. Tag storico `v7.0` conservato.

## Progresso concreto V7.12 — KiCad vero + DSP e firmware conservati
- Nuovo root KiCad nativo editabile `04_KiCad/Assemblaggio_RX_Power_V7.12_REANNOTATED_NOT_FOR_FAB/S3900E_RX_POWER_INTEGRATION_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch`: collega **gerarchicamente, NON elettricamente**, power AUX V1.5, MCU/CODEC copia V7.12 (46 ref +6000) e RX coupon copia V7.12 (15 ref +9000). La PCB RX copiata mantiene gli stessi 15 nuovi designatori, nets, 70 via e sei fori già corretti dalla V7.11; gli originali rimangono inalterati.
- **KiCad CLI 9.0.8 native export:** root V7.10 e V7.12: **7 fogli, 132 istanze, 99 reti**, refs ripetuti **11→0** (14 istanze extra duplicate→0). PASS reale sui file KiCad, non è una BOM di fabbricazione o un sistema elettricamente interconnesso.
- **Schema RX V5.2 standalone exit3 riparato sulla copia V7.12:** la nota grafica conteneva LF non escapati e UUID mancante. Ora stringa escape `\\n`, UUID e sheet root metadata: vero `kicad-cli sch erc` esegue con exit0, **0 ERC error /76 warning** (46 off-grid, 15 footprint issues, 15 libreria simboli). Il caricamento è OK, **non** ERC pulito.
- **Ancora bloccanti:** ERC root **43 errori+416 warning=459**; PCB RX **85 violazioni DRC +63 unconnected** (70 via_dangling +15 footprint warnings), non è PCB integrato. Tutti i **15 confini power/MCU/RX restano OPEN/HOLD**, nessuna rete tra moduli alimentata o unita. Pinout originale Lattice iCE40 SG48 resta HOLD.
- **CI finale PR #12** [run 42866103256](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42866103256), job 130004727547 **SUCCESS**: netlist confrontate, ERC RX/root, PCB DRC, parser tests, **13 nuovi +8 V7.11+12 V7.10+143 V7.1–V7.9 =176 Python PASS, 0 FAIL/SKIP**. Icarus/Yosys non rieseguiti in V7.12, ma lo storico DSP/firmware e i risultati precedenti restano conservati. Rapporti nativi nell'artifact GitHub Actions, non Gerber.
- Report `Superstar3900_Rapporto_Tecnico_V7.12.md`, specifica `01_Specifiche/V7.12/RIANNOTAZIONE_NATIVE_RX_MCU_V7_12.md`, ECO `00_Gestione_Progetto/ECO_INTEGRAZIONE_CAD_V7.12.md`, machine-readable `03_Verifiche/V7.12/RISULTATI_VERIFICHE_V7_12.json`.

**Prossima V7.13:** ridurre *realmente in KiCad* 46 off-grid, 15 simboli e 15 footprint problematici dello schema RX, studiare connessioni, 70 via GND dangling e 63 unconnected RX su PCB reale senza piste arbitrarie, poi ridurre gli ERC root e qualificare uno ad uno rail e bus MCU/AUX/RX. Firmware, simulazioni, DAC/PLL/DSP e relativi test proseguono. Nessuna scheda completa né validazione RF.

**NO FAB / NO TX:** nessun Gerber, produzione, DAC/FPGA/PA TX montati, alimentati o collegati, nessuna trasmissione. La CI verde dimostra la qualità del controllo e due riparazioni CAD circoscritte, non la sicurezza del circuito.

---

## ARCHIVIO STORICO — V7.11 e precedenti

# SUPERSTAR 3900 SMD EVOLUTION — V7.11 CAD NATIVO SU MAIN

**10 novembre 2026:** V7.11 integrata con [PR #11](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/11), merge `028c3a5f8d9f638d423be251a7a06336a961ead7`. La priorità attuale è **schemi e PCB KiCad reali**, senza abbandonare firmware, DSP, simulazioni, componenti, documentazione e test. Verificare sempre HEAD `main`; il tag `v7.0` rimane storico.

## Cosa è stato realmente modificato in V7.11
- Creato un nuovo **`.kicad_pcb` nativo, editabile** da una copia del coupon RX 50Ω V5.2: `04_KiCad/Modulo_RX_Test_50ohm_V7.11_DRC_REPAIR_NOT_FOR_FAB/S3900E_RX_TEST_50R_V7_11_DRILL_LIBRARY_REPAIR_NOT_FOR_FAB.kicad_pcb`. Sei fori delle via GND sotto U101 corretti **0,25→0,30mm** e relative piazzole rame **0,55→0,60mm**; originale V5.2 inalterato, nessuna nuova pista/net/componenti TX.
- **Confronto DRC con `kicad-cli` nativo, REALMENTE ESEGUITO**: RX originale **91 DRC violations /63 unconnected**, V7.11 **85 DRC violations /63 unconnected**. Esattamente **6 `drill_out_of_range`→0**; restano **70 `via_dangling`** e **15 `lib_footprint_issues`**, anche dopo nuova `fp-lib-table` relativa. **Non è un DRC PASS** e non si autorizza fabbricazione.
- Verifiche sul branch: [Actions run 42856926563](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42856926563), job 129972377360, log esaminato: **8 test Python V7.11 +12 V7.10 +143 regressioni V7.1–V7.9 = 163 PASS /0 FAIL/0 SKIP**; DRC nativo comparativo PASS per miglioramento soltanto, **non** zero errori. Rapporto `Superstar3900_Rapporto_Tecnico_V7.11.md`, specifica `01_Specifiche/V7.11/PIANO_CORREZIONI_KICAD_RX_V7.11.md`, ECO `00_Gestione_Progetto/ECO_INTEGRAZIONE_CAD_V7.11.md`, JSON `03_Verifiche/V7.11/RISULTATI_VERIFICHE_V7_11.json`.
- Il root KiCad gerarchico V7.10 RX/AUX/MCU rimane un **indice elettricamente isolato**, con 132 istanze/11 riferimenti duplicati, 15 interfacce OPEN/HOLD, 43 errori ERC+416 warning. Lo schema RX standalone continua a fallire `kicad-cli sch erc` (exit3). **Il PCB completo della radio ancora non esiste**. Il pinout Lattice SG48 resta HOLD. Nessuna protezione TX fisica autorizzata.

**Prossima V7.12:** sistemare caricamento KiCad schema RX standalone e designatori ripetuti, riparare librerie/footprint, reti GND e **63 connessioni mancanti** senza tracciare a caso; affrontare i residui ERC e connettere power/MCU/RX soltanto dopo validazione delle reti. Continuare regressioni DSP/firmware e simulazioni; nessun Gerber o TX.

**NO FAB / NO TX:** non alimentare DAC/FPGA/mixer/PA/antenna; i test KiCad diagnosticano difetti e non autorizzano PCB o emissioni. Per riprendere da un'altra chat leggere `RIPRENDI_IN_UNA_NUOVA_CHAT.md` e `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`.

---

## ARCHIVIO — V7.10 e versioni precedenti

# SUPERSTAR 3900 SMD EVOLUTION — V7.10 CAD NATIVO INTEGRATA IN MAIN

**10 novembre 2026:** V7.10 integrata su `main` con [PR #10](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/10), merge `8a18c12df4455265db8414784587f4d82a1f82ae`. È la prima milestone centrata sul **vero progetto KiCad**, senza abbandonare software, DSP, firmware e test storici. Il tag `v7.0` è storico e preservato: verificare sempre l'HEAD di `main` prima di continuare.

## Stato effettivo V7.10
- Creato **nuovo file schematico nativo KiCad** `04_KiCad/Assemblaggio_RX_Power_V7.10_NOT_FOR_FAB/S3900E_RX_POWER_INTEGRATION_V7_10_NOT_FOR_FAB.kicad_sch`. È un indice gerarchico che richiama tre blocchi già realizzati: **AUX power V1.5** (eFuse, buck e LDO/TCXO/PLL), **MCU/codec V2.1**, **RX test coupon 50Ω V5.2**. Il progetto KiCad di test RX possiede un `.kicad_pcb` separato. **I tre fogli non sono ancora connessi elettricamente tra loro** e il PCB completo dell'apparato **non esiste**.
- `MATRICE_INTERFACCE_DA_QUALIFICARE_V7_10.csv`: **15 confini elettrici OPEN/HOLD**; vietato unire per nome le reti 5V, 3V3, SPI, IF/RX e masse senza pin e protezioni realmente qualificati. Nessuna catena TX aggiunta: DAC, FPGA, PA/antenna tutti DNP e non collegati.
- **Prima CI con KiCad CLI nativo 9.0.8**: `sch export netlist` riuscito con warning annotazione; risultato **7 fogli, 132 istanze componenti, 118 ref univoci, 11 designatori riutilizzati (14 occorrenze in eccesso), 99 reti esportate**. Il root ha **43 errori ERC +416 avvisi**. Alimentazione V1.5 **22 errori/248 avvisi**, MCU V2.1 **18 errori/92 avvisi**. RX V5.2 standalone non caricabile da `kicad-cli sch erc` (exit3), anche se incluso nel root, quindi nessun ERC standalone certificato.
- **PCB coupon RX V5.2 DRC nativo:** **91 violazioni DRC e altre 63 connessioni non completate**, tra cui 6 via drill sotto limite, 70 via dangling warnings e 15 problemi footprint library. **Questo NON è un DRC PASS e NON è un PCB completo**. Tentativo di aggiungere `sheet_instances` per riparare RX standalone FALLITO: originale preservato, fix inefficace rimosso.
- **CI di AUDIT V7.10:** 12 test statici nuovi PASS e **143 regressioni Python V7.1–V7.9 PASS** = **155/155** sul branch, workflow [run 42855337776](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42855337776), log ispezionato. Workflow è GREEN perché *diagnosi KiCad realmente eseguita*, NON perché gli errori ERC/DRC sono assenti. Gli output sono scaricabili come artifact `v710-kicad-native-audit-not-for-fab`, incluso ZIP con sorgenti KiCad modificabili, netlist autentica e rapporti.
- Rapporto `Superstar3900_Rapporto_Tecnico_V7.10.md`, specifica `01_Specifiche/V7.10/PIANO_CAD_INTEGRAZIONE_RX_POWER_V7.10.md`, ECO `00_Gestione_Progetto/ECO_INTEGRAZIONE_CAD_V7.10.md`, risultati `03_Verifiche/V7.10/RISULTATI_VERIFICHE_V7_10.json`.

**Prossima V7.11:** con nuovi file KiCad versionati, risolvere prima il caricamento dello schema RX V5.2, correggere i designatori ripetuti, verificare footprint/simboli, affrontare le 63 connessioni PCB e le via fuori specifica, ridurre ERC/DRC e collegare uno per uno i moduli power/PLL/MCU/RX sulla base di pin verificati. In parallelo continuare DSP/firmware/CI. Il pinout FPGA SG48 rimane HOLD finché non acquisito l'XLSX Lattice originale. Solo quando lo schema integrato è connesso e verificato iniziare il **PCB integrato vero**.

**NO FAB / NO TX**: nessun Gerber, nessuna alimentazione TX, PA o antenna, nessun ordine PCB. Non attribuire sicurezza o stato di produzione a semplici simulazioni o a una CI diagnostica verde. Per ripresa da nuova chat leggere `RIPRENDI_IN_UNA_NUOVA_CHAT.md` e `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`, poi verificare HEAD `main`, PR/tag/actions.

---

## ARCHIVIO STORICO — V7.9 e precedenti, non stato corrente

# SUPERSTAR 3900 SMD EVOLUTION — V7.9 INTEGRATA SU MAIN

**10 novembre 2026:** V7.9 integrata con [PR #9](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/9), merge `38b9828728b02581bf24c070401dd70782051dbd`. È **software/RTL simulato + screening documentale**, NON hardware fabbricabile o una radio in trasmissione. Tag storico `v7.0` conservato; verificare sempre HEAD `main` e la CI in ogni nuova chat.

## Stato tecnico corrente V7.9
- Corretto il modello V7.8 che commutava heartbeat a **3,84 milioni di transizioni/s**, non campionabile da un secondo riferimento a 32,768kHz. V7.9 ha `MASTER_TICKS_PER_TOGGLE=307200` sul master nominale 30,72MHz: cambio livello ogni **10ms**, fronte WDI discendente ogni **20ms**. Sono **segnali virtuali**, nessun FPGA o DAC alimentato.
- Candidato reale **TI TPS3430WDRCR** watchdog window, pin verificati su datasheet SBVS366A p.3, WDI falling-edge; configurazione solo studio `CWD=NC, SET0=0, SET1=1, CRST=NC`: lower limit max 2,22ms, upper limit min 23,375ms; 20ms è aritmeticamente nella finestra. **WDO open-drain active LOW non può essere collegata direttamente a DAC900 PD active HIGH**; manca un latch/supervisor indipendente e protezione a rail=0. Riferimento possibile **Abracon ASFLK-32.768KHZ-LJT** 3,3V ±20ppm, DNP senza pinout fisico verificato.
- Screening **filtro F7401 non implementabile direttamente**: Coilcraft `MSS1260T-472MLD` 4,7µH (SRF tipica 38MHz), `MS590PNB183MSZ` 18µH (SRF min 11,2MHz), Q induttore 60 e Q condensatore 500 **assunti** per ABCD 50Ω numerico. Risultato matematico con SRF stimata: loss IF2 ~**0,235dB**, attenuazione relativa alle immagini ~**88,7dB**; NON qualifica reale Q/ESR, I/V DAC900, PCB o emissioni. Tutti DNP.
- **CI finale PR #9 PASS:** [GitHub Actions run 42848254217](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42848254217), log job 129941518720 verificato: **143/143 test Python PASS** (17 V7.9 +126 regressioni V7.1–V7.8), **4 bench Icarus PASS**, `Yosys synth/check` generico PASS, 0 FAIL/SKIP. Nessun test fisico.
- V7.9 BOM **11 righe DNP/OPEN**, netlist **15 terminali DNP/OPEN** (TPS3430 pin ufficiali verificati). `Superstar3900_Rapporto_Tecnico_V7.9.md`, `01_Specifiche/V7.9/ARCHITETTURA_HEARTBEAT_WATCHDOG_SRF_V7.9.md`, `00_Gestione_Progetto/ECO_INTEGRAZIONE_V7.9.md`, `03_Verifiche/V7.9/RISULTATI_VERIFICHE_V7.9.json`.
- **Pinout FPGA SG48 rimane HOLD:** foglio XLSX Lattice ufficiale `51971` ancora non acquisito/confrontato e nessun PNR/STA. Non produrre PCB usando PCF V7.6.

**Prossima V7.10:** recuperare XLSX Lattice e verificare package/pad, sviluppare schemi DNP di interblocco PD e watchdog indipendenti e analizzare power-loss single-fault, selezionare componenti LC con Q/SRF vendor a 455kHz e rete I/V, prova DSP fixed point/MCU, continuare CI. **NO FAB / NO TX**; nessun PTT, mixer, PA o antenna RF connessi.

**Per cambiare chat:** verificare `main`/tag/PR/CI e leggere `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md` e rapporto tecnico più recente. Conservare storico e integrare in main solo dopo test verificati.

---

## ARCHIVIO STORICO — V7.8 e precedenti, non stato corrente

# SUPERSTAR 3900 SMD EVOLUTION — V7.8 INTEGRATA SU MAIN

**10 novembre 2026:** V7.8 integrata con [PR #8](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/8), merge `75027e768bef2b5a00f69d1675e462b8c35b1366`. Questa è la revisione progettuale più recente di questa fotografia, NON hardware certificato. Verificare sempre HEAD `main` e le CI/PR all'inizio di una nuova chat; `v7.0` rimane tag storico immutato.

## Aggiornamenti V7.8
- **Watchdog diagnostico RTL su due clock virtuali:** heartbeat master e monitor da secondo dominio di riferimento simulato, 3 FF di sincronizzazione, fault latched quando si arresta il master ma il riferimento resta attivo. Tutti i permessi RF, PD e analogici restano **0 costanti**. Secondo clock, hardware supervisor e interlock **NON ESISTONO FISICAMENTE**.
- **Pinout Lattice SG48:** tool `03_Verifiche/V7.8/audit_pinout_vendor_v78.py` per confronto SHA256/ZIP XML se disponibile originale XLSX. Documento ufficiale 51971 non recuperato, test fatti solo su workbook sintetici: file pin e PCF V7.6 rimangono **HOLD NON APPROVATI PER PCB**.
- **DSP rigoroso:** quantizzazione 10 bit con guardia `|x| ≤ 1` **prima** dell'headroom del 70%; step 1,0 genera picco FIR numerico **1,142051** e fallisce senza clipping silenzioso. Stimolo audio 375/1730Hz + rumore non periodico, streaming invariato a blocchi, SNR digitale di solo errore di quantizzazione **49,392 dB** (NON SNR DAC reale).
- **Supervisor rail candidato TI TPS3840PH30DBVR** SOT23-5, reset active-high 3,0V. Solo **DNP/OPEN**, non connesso a PD e non è un watchdog di clock. Nuove BOM **8 DNP/OPEN** e netlist **10 terminali DNP/OPEN**.
- **CI verificata su codice della feature:** **20 V7.8 + 106 regressioni = 126/126 Python PASS**, 3 testbench Icarus PASS, 2 sintesi logiche Yosys generiche PASS. GitHub Actions [run 42842592233](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42842592233), log controllato. Una prima CI FAIL ha rilevato il criterio headroom debole, poi corretto e riprovato. I commit successivi alla CI positiva hanno aggiunto soltanto registri e rapporti. Le CI sul merge/main vanno verificate separatamente.
- Rapporto: `Superstar3900_Rapporto_Tecnico_V7.8.md`; specifica: `01_Specifiche/V7.8/ARCHITETTURA_WATCHDOG_PINOUT_DSP_V7.8.md`; ECO: `00_Gestione_Progetto/ECO_INTEGRAZIONE_V7.8.md`.

**Prossima V7.9:** acquisire/autenticare originale XLSX Lattice e verificare pin/bank/pad SG48, scegliere davvero secondo riferimento clock/watchdog e isolamento fisico con datasheet/pin, analizzare PD a perdita alimentazione, CDC/MTBF e F7401 con componenti Q/SRF verificati. No PNR/STA né PCB finché la mappa vendor non è approvata.

**Metodo di continuità:** leggere `RIPRENDI_IN_UNA_NUOVA_CHAT.md` e `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`, controllare ultima main, lavorare in branch con test/rapporti, unire in `main` dopo risultati validati. **NO FAB / NO TX**: tutti i componenti TX DNP, mixer/PA/antenna non collegati; nessuna emissione o collaudo fisico dichiarato.

---

## ARCHIVIO STORICO — V7.7 E PRECEDENTI (non stato corrente)

# SUPERSTAR 3900 SMD EVOLUTION — V7.7 SU MAIN

**10 novembre 2026 · PR #7 integrata**, merge `e68743f5474be26732cfb6cd4ad9953404a2935c`. Ultima revisione **candidata software/documentale**, **non circuito fabbricabile**. Il tag storico `v7.0` è preservato. Per il prossimo lavoro verificare sempre l'ultimo HEAD di `main`, non solo questa fotografia.

## Novità V7.7
- **Top Verilog diagnostico** `08_Firmware_Prototipi/V7.7/rtl/top_virtuale_v77.v`: combina gli strobi /8 e /640 e FIFO virtuale V7.6; `tx_rf_permission`, `dac_pd_released` e `analog_path_connected` restano **0 costanti**. Nessun DAC, clock pin, PA o antenna fisicamente guidati.
- **Verifiche realmente passate su codice identico:** due testbench Icarus Verilog **PASS**, `Yosys synth -top v77_offline_top; check -assert` generico **PASS**, e **106/106 test Python PASS**, zero FAIL/SKIP (14 V7.7 + 92 V7.1–V7.6); [run GitHub Actions 42819963860](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42819963860), log ispezionato. I commit successivi alla CI positiva hanno cambiato **solo documenti**, non codice/test; la CI sulla PR finale era ancora in fase di installazione al merge. Non attribuirle PASS finché non sia effettivamente completata.
- Quantizzazione **solo numerica DAC 10bit** con headroom 70%: multitono 750/1250Hz, SNR di errore di quantizzazione **51,47dB**, **NON** prestazione DAC900 elettrico. Step FIR 0→0,4: overshoot 14,205%. Inventario di 12 guasti e requisiti di PD/clock/isolamento indipendente **NON PROVATI HARDWARE**.
- **Pinout FPGA Lattice SG48 non approvato:** documento ufficiale XLSX v1.1 `51971` identificato ma file binario non acquisito; PCF V7.6 e 48 pad restano **HOLD**, non realizzare il PCB con quei vincoli. Generica Yosys non significa nextpnr/STA/bitstream iCE40.
- Nuova BOM **8 voci DNP/OPEN**, netlist virtuale **10 terminali DNP/OPEN**, tutte le revisioni V7.1–V7.7 TX fisicamente assenti e non instradate.
- Rapporti: `Superstar3900_Rapporto_Tecnico_V7.7.md`, `03_Verifiche/V7.7/RAPPORTO_TECNICO_V7.7.md`, `01_Specifiche/V7.7/ARCHITETTURA_RTL_QUANTIZZAZIONE_V7.7.md`, `00_Gestione_Progetto/ECO_INTEGRAZIONE_V7.7.md`.

**Prossima V7.8:** verifica del foglio XLSX Lattice originale con i 48 pin, qualificazione dei bank/pad/power, vero monitor clock indipendente e supervisor PD hardwired ancora DNP, prove quantitative DSP più ampie e filtro analogico con MPN, Q e SRF; soltanto dopo pinout verificato considerare PNR/STA. **NO FAB / NO TX**.

**Ripresa in altra chat:** leggere `RIPRENDI_IN_UNA_NUOVA_CHAT.md` e `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`; esaminare HEAD `main`, tag, PR, Actions e report più recente, quindi sviluppare prossima revisione con branch/CI/merge. Non dichiarare mai test elettrici, KiCad ERC/DRC, EMC o fabbricazione non eseguiti.

---

## ARCHIVIO — V7.6 E PRECEDENTI (non stato corrente)

# SUPERSTAR 3900 SMD EVOLUTION — V7.6 INTEGRATA IN MAIN (10 novembre 2026)

**V7.6 su main**, integrata con [Pull Request #6](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/6), merge `8309d11e1a06473119aafcb71a0cbe2aa0171e61`. È una **revisione sperimentale software/documentale**, non un dispositivo TX o un PCB validato. Il tag storico `v7.0` rimane immutato; prevale sempre HEAD `main` per lo stato più recente.

## Stato tecnico V7.6
- Modulo RTL Verilog comportamentale `08_Firmware_Prototipi/V7.6/rtl/clock_fifo_virtual_v76.v`, div clock-enable **/8 e /640** per DAC/audio nominali da master 30,72MHz, FIFO virtuale 10bit×16, fault latched. **Nessuna clock waveform DAC fisica**; porte di permesso RF e rilascio DAC PD **sempre zero**.
- Testbench con Icarus Verilog `03_Verifiche/V7.6/tb_clock_fifo_virtual_v76.v` eseguito con **PASS**; **92/92 test Python PASS**, zero FAIL/SKIP (15 V7.6 + 22 V7.5 + 21 V7.4 + 15 V7.3 + 11 V7.2 + 8 V7.1), GitHub Actions [run 42814827870](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42814827870), log del job verificato. Non è sintesi/place-route, timing closure o test elettrico.
- Nuovo pin-plan del candidato FPGA `iCE40UP5K-SG48I`, **48 pin periferici + paddle GND**, con vincoli PCF **HOLD**, perché i numeri provengono da una riproduzione secondaria e non sono ancora stati confrontati con l'XLSX ufficiale Lattice; il datasheet primario conferma i conteggi per banca e l'obbligo del paddle GND. **Non usare per produzione o programmazione FPGA**.
- DSP multitone numerico 750/1250Hz e gradino 0→0,4→0; picco di FIR ~**0,45682** (+14,2%) evidenzia rischio di overshoot e necessità di headroom; non è una misura di emissioni DAC/RF.
- Nuova BOM **5 elementi DNP** e netlist **8 terminali OPEN/DNP**; tutte le revisioni TX V7.1–V7.6 e le interfacce PA/antenna fisiche restano non montate e non instradate.
- Documenti tecnici: `Superstar3900_Rapporto_Tecnico_V7.6.md`, `03_Verifiche/V7.6/RAPPORTO_TECNICO_V7.6.md`, `01_Specifiche/V7.6/ARCHITETTURA_RTL_PINPLAN_PROTEZIONI_V7.6.md`, `00_Gestione_Progetto/ECO_INTEGRAZIONE_V7.6.md`.

**Prossima revisione V7.7:** verificare pinout nel file XLSX Lattice ufficiale, chiudere top/constraints FPGA con simulazione e sintetizzabilità tracciate, clock output e monitor esterno, progettare POR/PD hardwired indipendente, quantizzazione DAC e filtri con dati Q/SRF reali. Non confondere software simulato con hardware sicuro.

**Ripresa nuova chat:** leggere `RIPRENDI_IN_UNA_NUOVA_CHAT.md` e `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`, verificare HEAD `main`/tag/PR/CI e sviluppare la revisione successiva. Merge in `main` solo dopo verifiche controllate. **NO FAB / NO TX.**

---

## ARCHIVIO — stato V7.5 e revisioni precedenti (storico, non stato corrente)

# SUPERSTAR 3900 SMD EVOLUTION — V7.5 IN MAIN (10 novembre 2026)

**V7.5 integrata su main** tramite [PR #5](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/5), merge `a5ef405f9500c114e8a4d56d7f9b17ba5a89caf1`. Revisione **software e candidata documentale**, NON un circuito RF completo o pronto da fabbricare. Il tag `v7.0` è storico e immutabile. L'ultimo commit di `main` prevale sulla fotografia di queste note.

## Novità V7.5
- Clock unico nominale **30,72MHz** con rapporto intero **/8 = 3,84MHz DAC** e **/640 = 48kHz audio**, indipendenza da drift *relativo* fra clock derivati da una stessa sorgente. Oscillatore candidato **Abracon ASDMB-30.720MHZ-LY**, 4 terminali con pin verificati dal disegno vendor, **DNP e non collegato**.
- Bridge FPGA candidato **Lattice iCE40UP5K-SG48I**, QFN48, **DNP**, **nessun pin FPGA allocato e nessun bitstream/PCB**. PD DAC900 active-high con pulldown interno e oscillator STANDBY active-low che sarebbe ON se floating: sicurezza hardware e power-up indipendenti ancora da progettare, NON dimostrati da software.
- Nuovo interpolatore multistadio *offline* **×5 ×4 ×4** con 16 tap/fase, stato conservato tra blocchi. Budget matematico FIR e Hilbert **86,784 M prodotti/s** rispetto a **129,024 M/s** V7.3 (−32,74%); NON benchmark realtime STM32G474/FPGA. Verifica di immagini digitali nominali su singolo tono coerente 750Hz, **non** prestazioni di DAC, filtro o emissioni RF.
- Nuovi 8 componenti BOM e 12 terminali netlist, **TUTTI DNP**, RF/PA/antenna non instradati. Tutte le revisioni storiche e gli interblocchi documentali precedenti conservati.
- **77/77 unit test software PASS**, 0 FAIL/0 SKIP (22 nuovi V7.5 + 21 V7.4 + 15 V7.3 + 11 V7.2 + 8 V7.1), [GitHub Actions PR run 42810514397](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42810514397), log verificato; NON qualifica hardware.
- Leggere `Superstar3900_Rapporto_Tecnico_V7.5.md`, `03_Verifiche/V7.5/RAPPORTO_TECNICO_V7.5.md`, `01_Specifiche/V7.5/ARCHITETTURA_CLOCK_UNICO_DSP_V7.5.md`, `00_Gestione_Progetto/ECO_INTEGRAZIONE_V7.5.md`.

**Prossima V7.6:** pin-mapping FPGA e constraints documentati, simulazione RTL di clock/FIFO solo software, analisi POR/PD hardwired indipendente, spettro digitale su transitori/multitono e selezione di componenti analogici con dati SRF/Q. Non collegare RF TX, finale o antenna; non autorizzare PCB.

**Regola di continuità fra chat:** controllare `main`, tag, PR e CI, poi leggere `RIPRENDI_IN_UNA_NUOVA_CHAT.md` e `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`; continuare a sviluppare la prossima revisione e integrarla in `main` dopo test verificati. **NO FAB / NO TX.**

---

## ARCHIVIO STORICO — V7.4 E PRECEDENTI (non stato corrente)

# SUPERSTAR 3900 SMD EVOLUTION — V7.4 IN MAIN

**10 novembre 2026: V7.4 integrata in main** tramite [Pull Request #4](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/4), merge commit f92220b0e789673cb927f4e21a72ed4d16b92faf. La V7.4 è una revisione **software e di progettazione DNP**, NON un circuito completo, fabbricabile o abilitato alla trasmissione RF. Il tag v7.0 è la baseline storica intatta, mentre la versione attiva si ricava dall'HEAD attuale di main.

## Contenuto nuovo della V7.4
- Studio del **bus DAC900E 10-bit** in 08_Firmware_Prototipi/V7.4/dac900_bridge_offline_v74.py: clock 48kHz ×80 → **3.84MSa/s**, FIFO virtuale di 1024 parole, traccia fittizia clock e fallimenti latched su underflow/overflow/timing/rail/clock. NON è un driver hardware né firmware FPGA/STM32.
- Calcolo **I/V passivo** a corrente DAC nominale 20mA con due terminazioni **49.9Ω** Vishay CRCW060349R9FKEA candidate: R_eff 24.95Ω, uscita ideale ~0.4985V al codice 1023. R7501/R7502 e tutti gli altri dispositivi **DNP**; R7503 mantiene IOUT→F7401 **aperto**.
- **7 righe BOM e 8 terminali netlist tutti DNP**; ponte U7501 e oscillatore X7501 **TBD** senza MPN né pin verificati; il PA, mixer e antenna TX rimangono non collegati.
- **55/55 test Python automatici PASS, 0 FAIL / 0 SKIP** (21 V7.4, 15 V7.3, 11 V7.2 e 8 V7.1), sul commit della PR #4; [GitHub Actions run 42807026035](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42807026035), log verificato. Modelli numerici + integrità del CSV storico (270 canali); NON misure di circuiti.
- Rapporti: Superstar3900_Rapporto_Tecnico_V7.4.md, 03_Verifiche/V7.4/RAPPORTO_TECNICO_V7.4.md; specifica 01_Specifiche/V7.4/ARCHITETTURA_DAC_CLOCK_IV_V7.4.md; ECO 00_Gestione_Progetto/ECO_INTEGRAZIONE_V7.4.md.

**Prossima V7.5:** sorgente sincronizzata clock/bridge con scelta IC e dati pin verificati, dominio power-up e PD indipendente, uscita analogica IOUT/IOUTB e filtro realizzabile con Q/SRF reali, architettura DSP più efficiente. Nessun salto alla fabbricazione o TX RF. Non sono stati effettuati KiCad ERC/DRC, simulazioni circuitali vendor, schede funzionanti, EMC o test in trasmissione.

**Per continuare in una nuova chat:** leggere la parte iniziale di README.md, RIPRENDI_IN_UNA_NUOVA_CHAT.md e 00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md, verificare commit main/tag/PR/CI e ripartire dal rapporto tecnico più recente. Lo sviluppo passa da branch provvisorio a main dopo verifiche, con storico conservato. **NO FAB / NO TX.**

---

## ARCHIVIO — stato V7.3 e precedenti (non stato corrente)

# Superstar 3900 SMD Evolution — STATO CORRENTE V7.3 SU MAIN

**10 novembre 2026.** `main` ha integrato la **V7.3**, via [PR #3](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/3), merge `9f64126f5490d34921da726d41354518b34be9a7`. **Revisione progettuale candidata, NON hardware approvato.** Il tag storico `v7.0` è preservato; controllare sempre HEAD di `main` per trovare la versione effettivamente più recente.

## Sviluppo V7.3
- `08_Firmware_Prototipi/V7.3/duc_if2_causale_v73.py`: DSP **offline causale a stato**, Hilbert 257 tap, interpolazione 80×/32 tap/fase a 3,84MSa/s da audio 48kHz, AM/FM/USB/LSB/CW, continuità fra blocchi e segnalazione overrange. **Non** firmware operativo STM32.
- `U7401` TI **DAC900E TSSOP-28**, 10bit parallel/current-output, pin verificati dal datasheet TI SBAS093B, **DNP**; clock 3,84MHz e bridge digitali senza MPN/pin/realizzazione. **12 righe BOM DNP, 42 righe netlist DNP**; IOUT/IOUTB non instradati.
- `F7401` LC 7 poli, cutoff matematico 850kHz, circuito 50Ω **non collegato al DAC in corrente**: test ABCD e MC400 con Q/induttanze ipotizzati, **non filtro fisico qualificato**.
- **34/34 test software PASS** (15 V7.3 + 11 V7.2 + 8 V7.1), GitHub Actions [run 42803248288](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42803248288), log verificati e 0 skip/fail.
- Consultare `Superstar3900_Rapporto_Tecnico_V7.3.md`, `03_Verifiche/V7.3/RAPPORTO_TECNICO_V7.3.md`, `01_Specifiche/V7.3/ARCHITETTURA_DUC_DAC_V7.3.md` e `00_Gestione_Progetto/ECO_INTEGRAZIONE_V7.3.md`.

**Prossima V7.4:** progettare il dominio digitale DAC/clock/bridge, candidati I/V/matching analogici e alimentazioni, valutare ottimizzazione DSP e vincoli MCU, senza collegare il finale o RF TX. Lo storico e gli schemi precedenti restano intatti. KiCad ERC/DRC, SPICE vendor, EMC, test fisici e autorizzazioni normative **NON ESEGUITI**.

**Procedura permanente per nuove chat:** leggere `RIPRENDI_IN_UNA_NUOVA_CHAT.md` e `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`, verificare il commit `main`, sviluppare la revisione seguente con verifiche concrete e poi integrarvi il lavoro. **NO FAB / NO TX.**

---

## ARCHIVIO STORICO — intestazioni V7.2 e precedenti (non stato corrente)

# Superstar 3900 SMD Evolution — STATO ATTUALE V7.2 IN MAIN

**10 novembre 2026 · `main` integra la V7.2 tramite [PR #2](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/2), merge `faab93ea00d64d43b3d4977a5a43f512977043a9`.** Questo è un **avanzamento progettuale candidato**, non un trasmettitore validato. Ultimo tag storico immutabile `v7.0`; per la revisione attiva controllare sempre HEAD di `main`, non soltanto il tag.

## Novità V7.2
- Modello digitale **solo offline** di sorgente IF2 455 kHz: audio 48 kHz, interpolazione 80× a 3,84 MSa/s, Hilbert 257 tap per USB/LSB e AM/FM/CW a più toni/impulso; nessun DAC/GPIO/PA fisicamente controllato.
- Studio numerico matematico F7201 IF1 e F7202 RF (Butterworth **ideali**, non filtri qualificati), comparazione aritmetica con **270 canali / 30 ALFA** del piano storico, regressioni logiche fail-closed.
- **19/19 test GitHub Actions PASS** (11 V7.2 + 8 V7.1) nel checkout integrale; [run 42794577497](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42794577497) completata con `success`. Non sono misure di laboratorio.
- Nuova BOM da **8 voci DNP**, netlist concettuale **12 terminali DNP**: DAC U7301 e filtro F7301 senza MPN e pin fisici non inventati. U7201/U7202 e tutti i ponti TX V7.1 restano DNP; uscita RF senza instradamento.
- Documenti: `01_Specifiche/V7.2/ARCHITETTURA_DUC_IF2_V7.2.md`, `Superstar3900_Rapporto_Tecnico_V7.2.md`, `03_Verifiche/V7.2/RAPPORTO_TECNICO_V7.2.md`, `00_Gestione_Progetto/ECO_INTEGRAZIONE_V7.2.md`.

**Prossima V7.3:** selezione progettuale DAC/clock e filtro di ricostruzione 455 kHz, digital processing *causale* per audio non periodico, budget computazionale e test spettrali offline su transitori; nessun collegamento a finale/antenna. Persistono blocchi RX/PLL, alimentazioni, MPN filtri, interblocchi V6.2, KiCad/ERC/DRC, EM, hardware e conformità normativa.

**Regola permanente per nuove chat:** leggere `RIPRENDI_IN_UNA_NUOVA_CHAT.md` e `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`, verificare l'ultima revisione `main` e proseguire con nuovo modulo/test; integrare la revisione coerente in `main`, mantenendo lo storico. **NO FAB / NO TX.**

---

## ARCHIVIO: stato V7.1 integrato in main (10 novembre 2026)

**10 novembre 2026 · V7.1 integrata con PR #1 · commit merge `4c3585c`.** Il branch principale `main` è la fonte dell'ultima revisione progettuale integrata. Il tag `v7.0` rimane la baseline storica immutabile. **V7.1 è solo un candidato numerico/documentale: NO FAB / NO TX.**

**Regola per tutte le nuove chat:** leggere `RIPRENDI_IN_UNA_NUOVA_CHAT.md` e [`00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`](00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md); controllare l'HEAD `main`, i tag, le PR e la CI. Sviluppare la revisione successiva con test reali dichiarati, poi integrare in `main` (eventuale branch temporaneo solo per lavorare e verificare). Conservare la cronologia e aggiornare i documenti di ripresa a ogni revisione.

**Prossima revisione pianificata: V7.2** — generazione IF2 455 kHz/DUC, modulazione audio multitonale e studio filtri IF/RF. Controlli nativi KiCad, misure RF, qualifica hardware e autorizzazioni TX rimangono aperti.

---

## Dettaglio V7.1 — integrazione candidata (10 novembre 2026)

**Baseline tag immutabile: `v7.0`. La V7.1 TX modulatore/IF *SOLO STUDIO* è integrata in `main`.** La V7.1 non abilita alcuna RF, non è un circuito completo, e non sostituisce il rapporto V7.0.

- Novità: piano matematico IF2 455kHz → 10.695MHz → 25.615–28.305MHz, inversione USB/LSB per LO alto, simulatori mono-tono AM/FM/SSB/CW esclusivamente offline.
- Elaborati: `01_Specifiche/V7.1/ARCHITETTURA_TX_IF_INIBITA_V7.1.md`, `NETLIST_PIN_TO_NET_TX_V7.1.csv`, `07_Componenti/BOM_TX_IF_V7.1.csv`, `08_Firmware_Prototipi/V7.1/tx_if_offline_v71.py`, `03_Verifiche/V7.1/RAPPORTO_TECNICO_V7.1.md`.
- Controllo incremento: 270 posizioni × 5 modi confrontati aritmeticamente con il CSV storico, 9 righe BOM e 22 mapping di pin tutti DNP. Test locali: 6 PASS, 2 SKIP per checkout parziale. **GitHub Actions: 8/8 PASS, 0 SKIP** sul checkout integrale (run 42791419516); non è prova hardware.
- **Forte vincolo NO TX / NO FAB:** mixer e ponticelli DNP, porta RF non instradata, nessuna alimentazione/LO/PA TX fisicamente interconnessi. KiCad ERC/DRC, SPICE/EM e hardware NON ESEGUITI.
- Prossimo sviluppo: specificare la vera generazione IF2/DUC e filtri, con verifiche di selettività, EMC e interblocchi, sempre in assenza di emissione.

---

# Superstar 3900 SMD Evolution — STATO ATTUALE V7.0

**Archivio storico dello stato al 9 novembre 2026; prevale lo stato V7.1 in cima a questo file e la HEAD corrente di `main`.**
**Ultima versione tecnica completata e importata: V7.0. Prossima revisione pianificata: V7.1 (TX modulatore/FI candidato, TX fisicamente disabilitata).**

## Ripresa sicura in nuove chat
1. Aprire il repository **privato** `jd3485/Superstar3900-SMD-Evolution`; leggere prima questo file e `RIPRENDI_IN_UNA_NUOVA_CHAT.md`.
2. Leggere `Superstar3900_Rapporto_Tecnico_V7.0.md`, `03_Verifiche/V7.0/RAPPORTO_TECNICO_COMPLETO_V7.0.md` e `00_Gestione_Progetto/ECO_INTEGRAZIONE_V7.0.md`.
3. Confrontare sempre `main` e i tag per individuare eventuali versioni successive; non interpretare le intestazioni V6.x nella cronologia sottostante come stato attuale.
4. Preservare tutti i file storici e registrare modifiche, report e test. Il tag `v7.0` conserva in modo immutato la baseline importata.

## Avanzamento tecnico verificato V7.0
- RX: candidati IF2 455 kHz, demodulazione AM AD8307 e FM HC4046, amplificazione LO2 10,24 MHz e filtri audio FIR Q15 SSB/CW. Il livello LO2 +7 dBm **non è stato misurato**; filtri 455 kHz SSB/CW restano DNP.
- Test registrati nella revisione: **75/75 nuovi** e **616/616** selezionati V5.9–V7.0, su modelli numerici e verifiche statiche, **non** su prototipo fisico.
- Gate aperti: selettività/immagine RF, PLL e programmazione registri, alimentazione/termica, filtri analogici, interblocchi, schemi KiCad nativi, ERC/DRC, PCB e collaudi.
- **NO FAB / NO TX:** trasmissione RF fisicamente inibita; nessun hardware qualificato o autorizzazione di trasmissione dichiarati.

## Versioni e archivi cumulativi
Ogni commit Git rappresenta un'intera istantanea dei file tracciati; il tag `v7.0` identifica la baseline originaria. GitHub consente di scaricare lo **ZIP cumulativo del codice sorgente** relativo a un tag dalla pagina dei tag/release: non occorre committare un nuovo ZIP da 50 MB per ogni revisione. Questo ZIP contiene i file versionati, ma non la directory `.git` né è necessariamente identico byte-per-byte allo ZIP storico `Superstar3900_SMD_Evolution_V7.0.zip`. Gli eventuali ZIP cumulativi nel formato storico saranno preparati separatamente e identificati con SHA-256; il caricamento come asset di Release richiede una funzione di upload apposita. Il manifest `MANIFEST_SHA256_V7.0.csv` appartiene alla **baseline tag v7.0**, non allo stato mutabile di `main`.

---

## ARCHIVIO STORICO — testo precedente V6.8 e precedenti, conservato integralmente

# Superstar 3900 SMD Evolution — V6.8

**Studio candidato FI1 10,695MHz, AGC AD8338, FI2 455kHz, filtri e piano LO2/BFO. NO FAB/NO TX.**

Nuovi 36 riferimenti di distinta (alcuni non selezionati), 100 assegnazioni terminale-rete, 1.350 combinazioni frequenza/modo, 12.000 stress numerici, 60 test di coerenza e 471 test di regressione selezionati dalla V5.9 alla V6.8 PASS. **Nessun circuito è approvato per produzione.**

Percorsi nuovi: `01_Specifiche/V6.8/`, `03_Verifiche/V6.8/`, `02_Piano_Frequenze/V6.8/`, `07_Componenti/BOM_FI_AGC_V6.8.csv`, `08_Firmware_Prototipi/V6.8/`, rapporto di revisione `Superstar3900_Rapporto_Tecnico_V6.8.md`.

GATE APERTI: buffer FI1, filtri SSB/CW, commutatori, oscillator LO2/BFO, demodulatori, AGC dinamico, alimentazioni, IF2 matching, isolamento RX/TX; schemi KiCad precedenti NON alterati. Prima la radio completa con verifiche incrementali, poi simulazione/controllo finale con il KiCad dell'utente.

L'originale V6.7 dei quattro documenti gestionali modificati è in `09_Archivi_Precedenti/Snapshot_Integrali_V6.7/`.

---

## README storico V6.7

# Superstar 3900 SMD Evolution — V6.7

**Revisione cumulativa RX front-end 50Ω (STUDIO, NO FAB / NO TX).**

V6.7 integra F501 SXBP-27R5+, U101 ADL5535 (riutilizzato dalla V5.x, non duplicato), U501 ADE-1+ con interfacce J701/J702, ESD D701 **DNI**, alimentazione RX 5 V commutata **da implementare**, rete Pi configurabile 0/6dB. 60 test V6.7 + 20.000 stress numerici e 270 frequenze; 9 suite selezionate regressive V5.9–V6.7 superate. Modelli NF/Friis **non sono misure**, immagini non qualificate, TX totalmente disabilitata.

Nuovi documenti: `01_Specifiche/V6.7/`, `03_Verifiche/V6.7/`, `07_Componenti/BOM_FRONTEND_RX_V6.7.csv`, `Superstar3900_Rapporto_Tecnico_V6.7.md`; storico immutato (originali gestionali V6.6 duplicati in `09_Archivi_Precedenti/Snapshot_Integrali_V6.6/`).

**Prossima V6.8: IF 10,695MHz, AGC e selezione filtri di demodulazione RX.** La progettazione continua con test incrementali e controllo globale finale su KiCad.

---

## README storico V6.6 integrale

# Superstar 3900 SMD Evolution — V6.6

**Progressione per revisioni e verifiche incrementali, NO FAB / NO TX.**

V6.6: preselettore 50Ω F501. Due soluzioni candidate: **rete RLC discreta a 3 risonatori** (L601/L603=2µH, L602=22nH, capacità totali serie 17,5pF e shunt 1591pF) con modello 2-porte S11/S21, perdita Q, SRF e feedthrough, **e alternativa SMD** **Mini-Circuits SXBP-27R5+** 24–31MHz. Quest'ultima ha datasheet 50Ω, IL tip.1,3/max2,5dB e rigetto stopband 39–900MHz min20dB (a 25°C); NON è un modulo del progetto già validato.

Modello discreto QL=60, QC=400, SRF e C_FEED 0,05pF **assunti**: perdita RX max 5.59dB, reiezione immagine relativa min 47.96dB, RL min 6.18dB. In 4.000 stress test esplorativi, 46.8% supera 6dB di perdita massima. Valori NON prestazioni certificate. 270/270 RX simulati; 50 test nuovi + regressioni selezionate.

File nuovi: `01_Specifiche/V6.6/`, `03_Verifiche/V6.6/`, `07_Componenti/BOM_PRESELETTORE_V6.6.csv`; vedi `Superstar3900_Rapporto_Tecnico_V6.6.md` e `MANIFEST_SHA256_V6.6.csv`. Vecchi documenti di gestione integrali in `09_Archivi_Precedenti/Snapshot_Integrali_V6.5/`. KiCad/ERC/DRC e ngspice vendor **NOT_RUN**.

---

## README storico V6.5 integrale

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

## Storico precedente (V6.2)

# Superstar 3900 SMD Evolution V6.2 — Progetto cumulativo

**Criterio attuale:** costruire progressivamente la radio completa, con controlli/simulazioni realmente disponibili per ogni revisione; verifica finale dell'intero sistema e KiCad dopo completamento architettura. NON FAB / NO TX.

**Novità V6.2:** schema tabellare a 61 componenti, 190 pin-rete del modulo interblocchi HW PA/TX e supervisione 3V3 + 13,8V; 31 test V6.2 e Monte Carlo 50.000 campioni. ECO meccanica SPDT PA, riserve MCU PB11/PB4 usate per watchdog/TX arm, reinstradamento AMP_SD/relè obbligatorio. J801 DNI aperto, FAULT_LOOP_OK da progettare, nessun finale RF connesso. Native KiCad ERC/DRC/analog SPICE NOT_RUN. Il progetto non è fabbricabile.

Aprire `01_Specifiche/V6.2/SCHEMA_A_COMPONENTI_INTERBLOCCHI_V6.2.md`, `03_Verifiche/V6.2/RAPPORTO_TECNICO_V6.2.md`, `03_Verifiche/V6.2/test_interblocchi_v62.py` e `00_Gestione_Progetto/REGISTRO_DECISIONI.md`. **Prossima V6.3: ingresso 13,8V e rail 5V/3,3V.** Storico V6.1 sotto `09_Archivi_Precedenti/Snapshot_Integrali_V6.1/`.

---

## Storico e note precedenti

# Superstar 3900 SMD Evolution — V6.1

**Fase:** progettazione della radio COMPLETA un modulo alla volta, con verifiche e simulazioni disponibili a ogni revisione, poi revisione e validazione globale su KiCad dell'utente.

V6.1: pannello e STM32G474RET6 mappati con 64 pin reali, due MCP23017, 28 ingressi e 4 LED, CH9/PA/PTT/encoder diretti. Circuito candidato JSON/CSV e BOM sotto `01_Specifiche/V6.1`, `07_Componenti/BOM_MCU_PANNELLO_V6.1.csv`; modello firmware sotto `08_Firmware_Prototipi/V6.1`; test e simulazioni in `03_Verifiche/V6.1`. TX OFF, NO FAB.

---

# Superstar 3900 SMD Evolution — V6.0

**FASE: progettazione progressiva della radio completa — simulazioni e KiCad DOPO.**

V6.0 aggiunge il modulo AUDIO/PA a livello di componenti: BOM, netlist di pin, tre IC candidati, cinque ingressi RX, microfono, amplificatore BTL e relay DPDT speaker. Tutti i dettagli sotto `01_Specifiche/V6.0/` e `03_Verifiche/V6.0/`. Non esiste PCB audio fabbricabile; TX sempre disabilitata.

# Superstar 3900 SMD Evolution — V5.9 cumulativa — 9 novembre 2026

**Nuova fase secondo le indicazioni del committente:** costruire la RADIO COMPLETA per revisioni incrementali. Le verifiche sistematiche KiCad e simulazioni sono previste *dopo* il completamento della progettazione; restano solo i test software di coerenza e le correzioni necessarie durante il lavoro. Questo NON significa ignorare errori già noti.

**Nuovo progetto V5.9:** architettura funzionale integrata a **26 blocchi / 54 collegamenti logici**, contratto JSON tipizzato, mappa SVG e selettore audio RX 5:1 candidato che evita il conflitto ADC del codec. Modello software di routing audio MIC/RX/PA con RF TX sempre OFF; prove unit test incluse. Nuove fonti ufficiali TI/ST archiviate come URL, non come CAD certificato.

**File iniziali:** `01_Specifiche/V5.9/ARCHITETTURA_RADIO_COMPLETA_V5.9.md`, `01_Specifiche/V5.9/SCHEMA_FUNZIONALE_AUDIO_PA_V5.9.md`, `00_Gestione_Progetto/PIANO_MODULI_COMPLETAMENTO_V5.9.md`. `01_Specifiche/V5.9/CONTRATTO_MODULI_V5.9.json` è una specifica logica, **NON** una netlist o schema KiCad fabbricabile.

**Stato di progetto:** 37% storico documentale stimato, 0 hardware validato. KiCad ERC/DRC nativi ancora NOT_RUN; 9 gate V5.0 aperti; NO FAB / NO PCBWAY / NO TX. Il PCB RX V5.2 e tutti i file precedenti non sono modificati. Tutta la cronologia rimane conservata.

---
## README storico V5.8 e precedenti

# Superstar 3900 SMD Evolution — V5.8 cumulativa — 9 novembre 2026

**STATO: NON FAB / NO PCBWay / NO TX.** Zero hardware testato. Nove gate V5.0 aperti, KiCad ERC/DRC/refill/parità nativi `NOT_RUN`. Avanzamento storico 37% (documentale/stimato, NON hardware).

**Novità V5.8:** audit statico e riproducibile della distanza centro-pista RF / centro-via GND. Su 6 reti RF, 13 segmenti F.Cu e 70 via GND, il peggiore tratto campionato è `RF_ATTEN_IN` con **9,5811 mm**, seguito da `RF_ATTEN_OUT` con **6,9385 mm**. I campioni lungo piste rettilinee sono spaziati ≤0,20 mm, bound di errore sul massimo geometrico ≤0,10 mm. **NON** è la lunghezza del ritorno di corrente, non è un criterio di accettazione RF e NON prova una discontinuità; i piani GND rimangono UNFILLED.

**Test nuovi V5.8:** 30/30; regressioni V4.0–V5.8: 19/19. Runner nativo locale `NOT_RUN_KICAD_MISSING`, exit 5. I PCB, schemi, librerie, firmware e manuali non sono stati modificati. CSV con 6 reti e mappa SVG tecnica sorgente inclusi.

Leggere `03_Verifiche/V5.8/RAPPORTO_TECNICO_V5.8.md`, `03_Verifiche/V5.8/PROCEDURA_V5.8.md`, il registro decisioni e `RIPRENDI_IN_UNA_NUOVA_CHAT.md`.

---
## Revisioni precedenti

# Superstar 3900 SMD Evolution — V5.7 cumulativa — 8 novembre 2026

**STATO: NO FAB / NO PCBWay / NO TX**, nessun hardware testato, ERC/DRC KiCad **NOT_RUN**, 9 gate V5.0 OPEN, avanzamento storico documentale 37% stimato.

**Novità V5.7:** audit indipendente e prudenziale delle sagome di GND_RF sui quattro strati non riempiti. Nel modello geometrico superiore, 70/70 vie GND possono intersecare ciascuno dei quattro contorni di zona, distanza minima rame-via/contorno 2,05 mm, su F.Cu una regione ideale da 6.323,1039 mm² (96,08% della zona); gli altri tre strati risultano ciascuno un contorno ideale geometrico completo. Le connessioni termiche e le regole di riempimento reali **NON sono modellate**. Il PCB conserva ancora 64 gruppi GND pre-refill, non 64 errori DRC dimostrati.

**Test eseguiti:** 30/30 V5.7, 18/18 suite software V4.0–V5.7, inclusi errori introdotti intenzionalmente. Runner locale `NOT_RUN_KICAD_MISSING`; workflow GitHub Actions V5.7 predisposto ma **non pubblicato né eseguito**. Nessun PCB, schema o libreria modificato.

Leggere `03_Verifiche/V5.7/RAPPORTO_TECNICO_V5.7.md`, `03_Verifiche/V5.7/PROCEDURA_V5.7.md`, `RIPRENDI_IN_UNA_NUOVA_CHAT.md` e `00_Gestione_Progetto/REGISTRO_DECISIONI.md`.

---
## Versioni precedenti

# Superstar 3900 SMD Evolution — V5.6 cumulativa — 8 novembre 2026

**STATO:** 37% documentale stimato, 0 prototipi fisici validati, ERC/DRC KiCad nativi **NOT_RUN**, NO FAB / NO PCBWay / NO TX.

**Novità V5.6:** audit STATICO della topologia del rame F.Cu sul PCB candidato V5.2. Le 7 reti di segnale/+5 V sono continue. La massa GND_RF è costituita da 64 gruppi di rame sul lato superiore prima del riempimento: 24 gruppi con pad e 40 con solo via; sono presenti 4 zone GND UNFILLED su F.Cu/In1.Cu/In2.Cu/B.Cu. Questi gruppi NON sono dichiarati come difetti DRC: occorre riempimento zone KiCad e controllo nativo dei ritorni RF. Geometria F.Cu V5.2 identica alla variante termica V4.8.

Nuovo verificatore `03_Verifiche/V5.6/audit_continuita_fcu_v56.py`, 23/23 test V5.6, 17/17 suite di regressione V4.0–V5.6. Workflow GitHub Actions manuale V5.6 e runner fail-closed predisposti, NON eseguiti su KiCad reale. I PCB, schemi, librerie, il firmware e il manuale illustrato restano intatti. Nove gate V5.0 ancora OPEN.

**File principali:** `03_Verifiche/V5.6/RAPPORTO_TECNICO_V5.6.md`, `03_Verifiche/V5.6/PROCEDURA_CONTINUITA_E_KICAD_V5.6.md`, `03_Verifiche/V5.6/AUDIT_CONTINUITA_FCU_V5.6.json`. Per riprendere leggere `RIPRENDI_IN_UNA_NUOVA_CHAT.md` e `00_Gestione_Progetto/REGISTRO_DECISIONI.md`.

---
## Versione V5.5 e documentazione storica

# Superstar 3900 SMD Evolution — V5.5 cumulativa (8 novembre 2026)

**STATO ATTUALE:** 37% documentale stimato; nessun hardware validato; ERC/DRC KiCad nativi **NOT_RUN**; NO FAB, NO PCBWay, NO TX.

**Novità V5.5:** screening di clearance sul rame `F.Cu` tramite Shapely, 44 pad, 44 piste, 70 vie, 5.267 confronti fra reti, distanza minima 0,45 mm (cinque coppie di pad); nessun risultato sotto soglia analitica 0,30 mm. Le **4 zone GND sono UNFILLED**, perciò NON è un DRC. Report `03_Verifiche/V5.5/AUDIT_RAME_FCU_V5.5.json`.

Postvalidazione dei JSON KiCad 10 con controllo esplicito di violazioni ERC, unconnected_items e schematic_parity: `03_Verifiche/V5.5/validate_native_reports_v55.py`. Runner `run_native_v55.py` e workflow GitHub Actions manuale `.github/workflows/kicad_native_v55.yml` predisposti, **NON eseguiti su KiCad reale**. Il test locale ha registrato il blocco previsto.

**Test:** 22/22 V5.5 e 16/16 suite di regressione V4.0–V5.5; tutti test statici/software. I file di schema, PCB, librerie, firmware e manuale illustrato sono invariati. I nove gate V5.0 rimangono tutti aperti.

**Avviare dal PC con KiCad 10:** leggere `03_Verifiche/V5.5/PROCEDURA_E_LIMITI_V5.5.md`. Per una nuova chat leggere `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, il rapporto V5.5 e `00_Gestione_Progetto/REGISTRO_DECISIONI.md`.

---
## README della V5.4 e delle versioni precedenti

# Superstar 3900 SMD Evolution — V5.4 cumulativa (8 novembre 2026)

**Stato:** 37% storico stimato, nessun hardware collaudato, ERC/DRC nativi ancora **NOT_RUN**. NO FAB / NO PCBWay / NO TX.

**Novità:** procedura di verifica KiCad 10 `03_Verifiche/V5.4/run_native_v54.py` con conservazione report ERC/DRC e parità; workflow facoltativo `.github/workflows/kicad_native_v54.yml` per esecuzione manuale su GitHub Actions, **mai pubblicato né eseguito**. Eseguire dal proprio PC `python3 -B 03_Verifiche/V5.4/run_native_v54.py --output REPORT_NATIVE_V5.4`, oppure seguire `03_Verifiche/V5.4/PROCEDURA_NATIVA_E_CI_V5.4.md`.

**Test svolti realmente:** 8 test V5.4 con CLI simulate e 15 suite di regressione software tutti riusciti. Il lancio locale reale segnala KiCad assente e `NOT_RUN`; il passaggio a KiCad 10 è ancora da fare. Tutte le nove condizioni di produzione sono OPEN. Schema/PCB/librerie e manuale d'uso invariati.

**Per riprendere:** aprire `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, `03_Verifiche/V5.4/RAPPORTO_TECNICO_V5.4.md` e `00_Gestione_Progetto/REGISTRO_DECISIONI.md`. Conservare l'intero ZIP cumulativo.

---
## README V5.3 e precedenti

# Superstar 3900 SMD Evolution — V5.3 cumulativa (8 novembre 2026)

**STATO REALE: 37% stima storica, zero moduli hardware validati, NO FAB / NO PCBWAY / NO TX.**

**Novità V5.3:** il parser indipendente `03_Verifiche/V5.3/audit_indipendente_v53.py` legge geometricamente simboli, pin, fili e label del candidato V5.2 e confronta le reti ai pad, percorsi UUID, valori, footprint e geometrie di 15 librerie/istanze. Risultati: **15 componenti, 31 pin, 31 fili, 8 reti, zero incongruenze rilevate staticamente**. I **18 nuovi test** e le **14 suite V4.0–V5.3** sono riusciti. Nessun sorgente KiCad modificato.

**KiCad CLI non installato:** ERC/DRC/refill/parità **NON ESEGUITI**. Eseguire `python3 03_Verifiche/V5.2/run_kicad_v52.py --output REPORT_NATIVE_V5.3` su un PC con KiCad 10. Nove gate di rilascio restano aperti; TE SMA e termica ADL5535 non approvati; manuale illustrato V4.0 conservato.

**Leggere per iniziare:** `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, `03_Verifiche/V5.3/RAPPORTO_TECNICO_V5.3.md`, `03_Verifiche/V5.3/ISTRUZIONI_RIPRESA_E_KICAD_V5.3.md`, `00_Gestione_Progetto/REGISTRO_DECISIONI.md`.

---
## Storico V5.2 e precedenti

# Superstar 3900 SMD Evolution — V5.2 cumulativa (8 novembre 2026)

**STATO:** 37% storico stimato; zero hardware validato; **NO FAB / NO TX**.

**Novità:** creato candidato schema/PCB separato con 15 riferimenti `instances (project...)` aggiornati nello schema e 15 collegamenti `(path...)` footprint→simbolo nel PCB. Non sono state modificate geometrie o reti: rimuovendo soltanto queste annotazioni il sorgente V4.8 è recuperato byte per byte. **Non è ancora una validazione KiCad nativa.**

**Test:** 12 nuovi test automatici V5.2; `kicad-cli` non installato: ERC, DRC, parità e refill **NON ESEGUITI**. Consultare `03_Verifiche/V5.2/RAPPORTO_TECNICO_V5.2.md`, `audit_associazioni_v52.py`, `run_kicad_v52.py` e `ISTRUZIONI_PROVA_KICAD_V5.2.md`.

Tutti i precedenti file, manuali e librerie preservati. Gate 9/9 OPEN. La revisione di fabbricazione resta vietata.

---
## README V5.1 e precedenti

# Superstar 3900 SMD Evolution — V5.1 cumulativa (8 novembre 2026)

**Stato:** progetto sperimentale. Avanzamento storico stimato 37%, **0 hardware validato**, **NO FAB / NO PCBWay / NO TX**.

## Risultati V5.1

- Inventario verificabile da PCB candidato RX V4.8: **15 componenti / 31 pin elettrici / 8 reti**, con BOM CSV preliminare e CSV pin-rete, MPN non assegnati e quattro SMA da confermare con CAD TE.
- Attenuatore Pi 150/37,4/150 Ω: attenuazione resistiva ideale **6,012876 dB a 50 Ω**, non una misura.
- `03_Verifiche/V5.1/genera_bom_net_v51.py` e `test_v51.py`: **13/13 test statici riusciti**, anche test di mutazione; suite precedenti V4.0–V5.0 rieseguite.
- `05_Produzione_PCBWay/V5.1/RICHIESTA_DFM_DA_INVIARE_V5.1.md`: richiesta di fattibilità aggiornata, **non inviata**. Condizioni VIPPO/stencil in attesa di conferma scritta.
- KiCad 10 **NON disponibile** dopo tentativo di aggiornamento pacchetti interrotto per timeout: **ERC/DRC/refill/parità NON ESEGUITI**.
- PCB, schema, librerie, manuale illustrato, revisioni cumulative **non modificati**. Gate R-01...R-09 ancora aperti.
- Rapporti: `03_Verifiche/V5.1/RAPPORTO_TECNICO_V5.1.md`, `03_Verifiche/V5.1/ISTRUZIONI_VALIDAZIONE_ESTERNA_V5.1.md`.

**Prossima verifica decisiva:** usare `03_Verifiche/V5.0/run_kicad_native_v50.py` su un PC con KiCad 10 e fornire i report; ottenere CAD TE del SMA esatto e una risposta DFM scritta su via-in-pad/stencil. Non avviare ordini.

---
## README storico V5.0 e precedenti

# Superstar 3900 SMD Evolution — V5.0 cumulativa (8 novembre 2026)

**Stato: 37% storico stimato, zero hardware validato; NO FAB / NO PCBWAY / NO TX.** La V5.0 è una revisione di prevalidazione: modello dello stencil U101, procedura KiCad 10 fail-closed, gate di rilascio, piano di collaudo RX. **Non** modifica PCB o schema e **non** registra approvazioni esterne.

## Novità V5.0

- `03_Verifiche/V5.0/RAPPORTO_TECNICO_V5.0.md`: risultati misurati dai sorgenti e limiti.
- `03_Verifiche/V5.0/STUDIO_STENCIL_V5.0.json` + `CONFRONTO_STENCIL_U101_V5.0.svg`: apertura attuale 81% vs due finestre alternative 29,69% con distanza nominale foro/pasta ≥0,125 mm. La seconda è **solo studio**, non progetto stencil approvato.
- `03_Verifiche/V5.0/run_kicad_native_v50.py` + `ISTRUZIONI_KICAD_V5.0.md`: lanciatore ERC/DRC/parità/refill su copia; KiCad non disponibile in questa sessione, quindi **NON ESEGUITI**.
- `03_Verifiche/V5.0/GATE_RELEASE_V5.0.json`: **9 gate OPEN**, tutte le autorizzazioni bloccate.
- `03_Verifiche/V5.0/PIANO_COLLAUDO_RX_V5.0.md`: prove proposte J101–J104, tutte `NOT_RUN`.
- `05_Produzione_PCBWay/DECISIONE_VIPPO_STENCIL_V5.0.md`: richiesta di fattibilità non inviata.
- `03_Verifiche/V5.0/test_v50.py`: 20/20 test statici superati, incluse prove d'errore; regressioni V4.0–V4.9 tutte riuscite.
- `09_Archivi_Precedenti/Snapshot_Integrali_V4.9/`: copie integrali byte-identiche dei 5 documenti attivi aggiornati.

**In una nuova chat:** allegare solo questo ZIP V5.0 e leggere `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, poi il rapporto V5.0 e il registro delle decisioni. Tutti i manuali, sorgenti e revisioni sono conservati.

---
## README storico V4.9 e precedenti

# Superstar 3900 SMD Evolution — V4.9 cumulativa (2026-11-08)

**Stato progettuale:** 37% storico stimato, zero hardware testato; **NO FAB / NO PCBWAY / NO TX**. Questa revisione aggiunge un audit statico del rischio via-in-pad/stencil e una richiesta di fattibilità, non nuovi PCB né collaudi RF.

## Novità V4.9

- `03_Verifiche/V4.9/RAPPORTO_TECNICO_V4.9.md`: misure da sorgenti KiCad, criticità e gate di accettazione.
- `03_Verifiche/V4.9/AUDIT_VIA_STENCIL_V4.9.json`: calcolo replicabile su V4.8, 6/6 fori della via-in-pad interamente nella F.Paste del pad esposto U101. Pad 1,80×3,48 mm; pasta teorica 1,62×3,132 mm, copertura 81%.
- `03_Verifiche/V4.9/audit_via_stencil_v49.py` + `test_v49.py`: 14 test statici compresi casi volutamente alterati. **Non sono ERC/DRC nativi**.
- `03_Verifiche/V4.9/U101_APERTURA_PASTE_V4.9.svg`: disegno geometrico illustrativo, non CAM.
- `05_Produzione_PCBWay/RICHIESTA_FATTIBILITA_V4.9.md` e `GATE_PRODUZIONE_V4.9.csv`: specifica da sottoporre eventualmente a fabbricante e montatore, **non un ordine**.
- `03_Verifiche/V4.9/PROCEDURA_KICAD_V4.9.md`: procedura nativa da svolgere su una macchina KiCad 10.

**Bloccanti**: VIPPO e stencil U101 non approvati; DXF/STEP TE ancora da confrontare; KiCad ERC/DRC/parity non eseguiti; stack-up RF, termica e collaudi mancanti. Nessuna versione del PCB è abilitata a fabbricazione.

**Come riprendere in un'altra chat:** allega solo il ZIP V4.9, leggi `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, poi questo README, il registro decisioni e il rapporto tecnico V4.9. Tutti i sorgenti e il manuale illustrato V4.0 sono conservati.

---
## README storico V4.8 e precedenti

# Superstar 3900 SMD Evolution — V4.8 (cumulativa)

**Stato**: progetto sperimentale. Nessun hardware collaudato, 37% avanzamento progettuale stimato. **NO FAB / NO PCBWAY / NO TX.**

## Novità V4.8

- `03_Verifiche/V4.8/RAPPORTO_TECNICO_V4.8.md`: relazione e limiti delle verifiche.
- `04_KiCad/Modulo_RX_Test_50ohm_V4.8_TERMICA_6VIE_STUDIO_NON_FAB/`: progetto candidato *separato*, con sei via-in-pad GND 0,55/0,25 mm sotto U101. Non fabbricabile senza via fill/cap, stencil e qualifica RF/termica.
- `03_Verifiche/V4.8/test_variante_termica_v48.py`: controllo reversibilità e geometria.
- `03_Verifiche/V4.8/RUN_KICAD_CANDIDATO_V48.sh`: ERC/DRC su copia, senza Gerber; non eseguito per KiCad assente.
- `MANIFEST_SHA256_V4.8.csv`: hash dei file correnti escluso sé stesso.
- `09_Archivi_Precedenti/Snapshot_Integrali_V4.7/`: copie byte-identiche dei documenti attivi aggiornati.

**Ripresa:** leggere `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, registro decisioni e rapporto V4.8. Manuale illustrato V4.0 ancora presente nella cartella `06_Manuali`.

---
## Testo storico (V4.7 e precedenti)

# Superstar 3900 SMD Evolution — V4.7 cumulativa (8 novembre 2026)

**Stato:** ricerca/progettazione 37% stimato, **zero hardware collaudato**, **NO FAB / NO PCBWay / NO TX**.

## Novità verificata V4.7

- Recuperato il **disegno ufficiale TE rev. D** del `CONSMA002-SMD-G`. Nel candidato SMA V4.3/V4.5 coincidono staticamente soltanto Ø2,05 mm del disco centrale e 7,76 mm dell'inviluppo verticale GND. Non è una validazione completa del footprint. DXF/STEP disponibili sul sito TE ma **non acquisiti**.
- I pad GND custom degli SMA dispongono di F.Mask/F.Paste senza riduzione esplicita, da approvare con l'assemblatore. Per U101 ADL5535 la formula nominale dell'apertura paste con ratio -0,100 dà circa 81% dell'area pad: **non** una misura termica o verifica stencil.
- **28/28 test V4.7 superati**; regressioni V4.0–V4.6 rieseguite. KiCad CLI assente: **ERC/DRC, refill e parità NON ESEGUITI**. Schemi, PCB e librerie candidati rimangono inalterati.
- `03_Verifiche/V4.7/RAPPORTO_TECNICO_V4.7.md`, `AUDIT_SMA_TE_V4.7.json`, `GEOMETRIA_SMA_STUDIO_V4.7.png` e `CHECKLIST_ACCETTAZIONE_V4.7.csv`.
- Tutte le versioni precedenti e il manuale illustrato V4.0 sono inclusi; documenti sostituiti salvati byte-per-byte in `00_Gestione_Progetto/V4.7_SNAPSHOT_V4.6/`.

**Per proseguire:** aprire `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, poi il rapporto V4.7; acquisire CAD TE esatto e validare in KiCad 10 prima di un prototipo.

---

## README precedente V4.6 conservato

# Superstar 3900 SMD Evolution — V4.6 cumulativa (8 novembre 2026)

**Stato ufficiale:** ricerca/progettazione in corso, **37% stimato**, **0 moduli hardware validati**. **NO FAB / NO PCBWay / NO TX**.

## Novità V4.6

- Audit dimensionale dei collegamenti di massa dell'ADL5535 U101: pad esposto 1,80×3,48 mm, via GND più vicino separato da 0,50 mm di rame; assenza di via-in-pad. Il layout è invariato e la termica rimane NON APPROVATA.
- Analisi dei quattro SMA J101–J104 nel candidato portabile: CAD TE DXF/STEP elencati dal produttore ma non acquisiti. Footprint e ingombro restano NON APPROVATI.
- Nuovo lanciatore KiCad che verifica `--refill-zones` e `--schematic-parity`, usa una copia temporanea e non salva il PCB: **KiCad non disponibile qui, native checks NON ESEGUITI**. Procedura KiCad 10 pronta per verifica esterna.
- 24/24 nuovi test statici e di blocco fail-closed superati, più suite V4.0–V4.5 rieseguite. Il manuale d'uso illustrato V4.0 e tutte le revisioni storiche restano nell'archivio.
- Corretta la guida interna di ripresa che era rimasta a V4.4; gli originali V4.5 sono salvati in `00_Gestione_Progetto/V4.6_SNAPSHOT_V4.5/`.

## Per riprendere rapidamente

1. Leggi `RIPRENDI_IN_UNA_NUOVA_CHAT.md` e `00_Gestione_Progetto/REGISTRO_DECISIONI.md`.
2. Leggi `03_Verifiche/V4.6/RAPPORTO_TECNICO_V4.6.md`, `AUDIT_TERMICA_SMA_V4.6.json` e il disegno `DETTAGLIO_PAD_TERMICO_U101_V4.6.png`.
3. Per i test: `python3 03_Verifiche/V4.6/test_rischi_v46.py`; per KiCad **reale**, su macchina con KiCad 10, `bash 03_Verifiche/V4.6/RUN_KICAD_RX_V46.sh ./risultati_kicad`.
4. Non produrre o ordinare nulla fino ad approvazione del CAD TE, termica ADL5535, impedenza e controlli nativi KiCad, seguiti da collaudi RF.

---

## README storico V4.5 (conservato per orientamento)

# Superstar 3900 SMD Evolution — V4.5 cumulativa (2026-11-08)

**Stato: progettazione/documentazione 37% stimato, zero prototipi convalidati; NO FAB / NO PCBWAY / NO TX.**

## Novità V4.5

Il modulo RX sperimentale dispone ora di **librerie KiCad locali**, generate dai footprint incorporati nella copia V4.3 del PCB e dai simboli dello schema candidato V4.4.

- **3 librerie footprint `.pretty` con 9 componenti tipo**, una libreria simboli con 9 simboli e tabelle riferite a `${KIPRJMOD}`. Layout 15 componenti riprodotto; non modificato il rame del candidato né l'originale V3.8.
- **26 test statici V4.5 superati**; eseguite di nuovo suite V4.0–V4.4. Non eseguiti ERC, DRC/refill o verifica di parità con KiCad, perché `kicad-cli` non disponibile.
- **Rischi aperti**: confronto CAD ufficiale TE CONSMA002-SMD-G, dissipazione ADL5535, approvazione stack-up 50 Ω, validazione PCB KiCad e misure RF.
- **Manuale illustrato V4.0** incluso: `06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf`. È ancora una bozza, non un manuale di un apparato collaudato.

## File di accesso

1. `RIPRENDI_IN_UNA_NUOVA_CHAT.md` e `00_Gestione_Progetto/REGISTRO_DECISIONI.md`.
2. `03_Verifiche/V4.5/RAPPORTO_TECNICO_V4.5.md`, `INVENTARIO_LIBRERIE_V4.5.json`, `TEST_V4.5.txt`.
3. `04_KiCad/Modulo_RX_Test_50ohm_V4.5_LIBS_PORTABILI_NOT_FOR_FAB/README.md`.
4. `03_Verifiche/V4.5/crea_librerie_v45.py` (rigenerazione), `test_librerie_v45.py` (suite) e `RUN_KICAD_RX_V45.sh` (richiede KiCad installato).
5. `00_Gestione_Progetto/CHANGELOG_V4.5.md` e tutti gli snapshot e manifest precedenti.

L'archivio V4.5 è **cumulativo**. I documenti attivi V4.4 aggiornati hanno copie byte-identiche denominate SNAPSHOT; tutte le revisioni e il manuale restano nell'archivio. Il progetto V4.5 non è utilizzabile per fabbricazione senza una revisione ingegneristica e verifiche hardware.


## V6.9 — LO2, BFO e demodulazione (9 novembre 2026)

Nuovi circuiti candidati U971 SI5351C 20-QFN, U981 TS5A3157, demod AM/FM provvisori; 1.350 profili e 70 test nuovi, 541 selezionati. Restano non realizzati il buffer +7dBm, filtri SSB/CW, demod FM hardware, interlock output indipendente, ERC/DRC e hardware. **Non fabbricare e non trasmettere.** Vedi 03_Verifiche/V6.9/RAPPORTO_TECNICO_COMPLETO_V6.9.md.


## V7.0 — RX IF2 AM/FM / driver LO2 / FIR SSB-CW (9 novembre 2026)

V7.0 overlay nuovo: U7101 AD8307 AM, U7102 TLV3201 comparator, U7103 HC4046 PLL FM, U7104 TLV9062 buffer, U7121 GALI-3+ driver LO2 e LPF a 50ohm; FIR post-demod 48kHz Q15. Test: 75/75 nuovi, 616/616 selezionati. D991/B991/B992 precedenti DNP, F823/F824 455k DNP, GALI LO2 +7dBm non verificati. ECO 00_Gestione_Progetto/ECO_INTEGRAZIONE_V7.0.md e report 03_Verifiche/V7.0/RAPPORTO_TECNICO_COMPLETO_V7.0.md. **NO FAB / NO TX.**
