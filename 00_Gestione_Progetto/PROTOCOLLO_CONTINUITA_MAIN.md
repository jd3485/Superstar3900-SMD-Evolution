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
