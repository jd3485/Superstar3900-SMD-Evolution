# Superstar 3900 SMD Evolution — Rapporto tecnico CAD V7.14

**10 novembre 2026 · progetto KiCad RX/MCU/AUX con librerie realmente accessibili. NO FAB / NO TX.** Base V7.13 già su `main`. Questa è una revisione di sorgenti KiCad, prove diagnostiche native e regressioni software, **non** un circuito o PCB radio fabbricabile.

## 1. Novità concreta: progetti KiCad (non solo fogli sciolti)

Sono stati creati due progetti KiCad versione 9, entrambi con i file `.kicad_pro` nel percorso del progetto:
- **Coupon RX 50 Ω**, `04_KiCad/Modulo_RX_Test_50ohm_V7.14_LIB_DIAGNOSTIC_NOT_FOR_FAB/S3900E_RX_LIB_V7_14_NOT_FOR_FAB.kicad_pro`, con `.kicad_sch` e `.kicad_pcb` di identico nome, libreria locale `S3900E.kicad_sym` e tabelle `sym-lib-table` e `fp-lib-table`. I 15 designatori schema/PCB sono allineati. Il PCB riprende **byte per byte** il coupon V7.12 e non cambia nessuna pista, via, foro o componente reale.
- **Gerarchia RX/MCU/AUX**, `04_KiCad/Assemblaggio_RX_Power_V7.14_LIB_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_pro`, con il relativo root `.kicad_sch` e tabelle di progetto che puntano ai simboli e footprint RX conservati nel repository. I 7 fogli esistono; **nessun filo intermodulo è stato creato**. AUX V1.5 e MCU V7.12 rimangono immutati.

L'iniziale warning indicava testualmente che la configurazione corrente non includeva la libreria `S3900E` e le tre librerie `S3900E_V38_Review`, `S3900E_v33`, `S3900E_v35`. Copiare i simboli senza un vero `.kicad_pro` **non aveva eliminato i 30 warning**; aggiungendo il file di progetto corrispondente i CLI KiCad hanno caricato le tabelle. I controlli non sono stati disabilitati né abbassati di severità. I simboli e i footprint sono tuttora candidati e **non qualificati rispetto ai datasheet o in laboratorio**.

## 2. Risultati realmente misurati con KiCad 9

| Controllo nativo | V7.13 | V7.14 | Significato |
|---|---:|---:|---|
| RX ERC — errori | 0 | **0** | Invariato |
| RX ERC — warning totali | 30 | **0** | **PASS, configurazione librerie corretta** |
| RX `lib_symbol_issues` | 15 | **0** | Libreria ora accessibile |
| RX `footprint_link_issues` | 15 | **0** | Librerie ora accessibili |
| PCB coupon RX — violazioni DRC | 85 | **72** | 13 in meno, senza nuove piste |
| PCB coupon RX — `via_dangling` | 70 | **70** | Ancora BLOCCANTI |
| PCB coupon RX — `lib_footprint_mismatch` | Non diagnosticabili come mismatch | **2** | **J9102, J9104** da verificare contro disegno SMA |
| PCB coupon RX — `unconnected_items` | 63 | **63** | Routing ancora da eseguire |
| Root 7 fogli — errori ERC | 43 | **43** | Ancora BLOCCANTI |
| Root 7 fogli — warning ERC | 370 | **340** | 30 in meno |
| Root 7 fogli — segnalazioni totali | 413 | **383** | **NON ERC PASS** |
| Netlist root | 99 reti | **99 reti** | Ogni net+ref+pin invariato |

Le **due discrepanze di footprint** sono emerse proprio perché KiCad ha potuto leggere la libreria. I disegni SMA J9102/J9104 montati nel PCB sono diversi dalla definizione presente in `S3900E_V38_Review.pretty`: correggerli senza un disegno manufacturer sarebbe improprio. Non è stato fabbricato, testato o alimentato nulla. Il DRC complessivo resta **NON SUPERATO**, malgrado le 13 segnalazioni in meno.

Il root contiene ancora **117 issue per librerie di simboli** degli altri moduli, **4 link di footprint**, **219 endpoint off-grid** e i 43 errori elettrici (tra cui power non driven, label/wire dangling e pin incompatibili). La rimozione dei warning RX non autorizza a collegare alcuna delle **15 interfacce RX/AUX/MCU che rimangono OPEN/HOLD**.

## 3. Prova di invarianza elettrica e test software

I due script in `03_Verifiche/V7.14/` esaminano veri report KiCad e due esportazioni `kicad-cli sch export netlist`:
- `probe_library_erc_v714.py`: ERC **30→0** e identità completa della mappa `nome rete → (reference,pin)` nel singolo coupon RX;
- `verifica_root_kicad_v714.py`: identità **di tutte le 99 reti e di tutti i relativi terminali** nella gerarchia e nessun aumento di errori/warning ERC;
- `test_rx_project_v714.py`: **15 test** di sorgenti KiCad, percorsi librerie, progetto, 15 refs, PCB identico e blocco delle connessioni TX.

Verifica eseguita su GitHub Actions [run 42885432839](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42885432839), job `130072389853`, log realmente ispezionato: **15 nuovi test + 186 regressioni precedenti = 201 Python PASS, 0 FAIL, 0 SKIP**. KiCad CLI, ERC, DRC e netlist native PASS **per i gate sopra descritti**; risultati grezzi in artifact `v714-native-kicad-library-diags-NO-FAB`.

La suite V7.14 non riesegue Icarus/Yosys: sono mantenute le verifiche software storiche ma non rivendicata alcuna validazione FPGA hardware.

## 4. Criticità e piano V7.15

**Restano da fare:** confronto vendor per i footprint SMA **J9102/J9104**, verifica pin/thermal del candidato ADL5535, qualifica delle altre impronte RF e di tutti i 15 componenti; pianificazione dei piani di massa e del ritorno RF per **70 via dangling**; routing delle **63 connessioni non completate**; sistemazione dei 43 errori ERC root e dei 15 contratti intermodulo, revisione alimentazioni e rail, PNR FPGA SG48, misure hardware/RF/EMC. Il progetto schematico e PCB dell'intera radio **non** è ancora realizzato.

**Prossima V7.15:** confrontare footprint SMA PCB vs `.pretty` e datasheet manufacturer, affrontare via e net RX con qualificazione topologica ed elettrica, ridurre ERC AUX/MCU, mantenendo DSP, firmware e test. Nessun collegamento fisico PA, DAC900, FPGA o antenna, nessun Gerber o TX.

**Decisione progettuale:** integrabile come miglioramento reale del progetto KiCad, **non approvato per fabbricazione**. **NO FAB / NO TX.**
