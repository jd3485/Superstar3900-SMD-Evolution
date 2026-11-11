# WORK_STATO_CORRENTE.md — checkpoint canonico di ripartenza da GitHub

**Aggiornato: 11 novembre 2026.** Sorgente di verità: repository GitHub **jd3485/Superstar3900-SMD-Evolution**, branch **main**; questo documento è un checkpoint, verificare sempre HEAD / PR / Actions in diretta.

**Prima di procedere in una nuova chat Work: LEGGERE ANCHE [AGENTS.md](../AGENTS.md)** (mandato, bootstrap, vincoli e procedura multi-revisione). Il file AGENTS è la configurazione stabile, questo è il registro da aggiornare ogni volta.

## STATO ATTIVO 11 novembre 2026 — **V7.27 MERGED / 36 errori + 222 avvisi ERC**

**Main tecnico integrato corrente:** [PR #30](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/30) **MERGED**, squash `18c027c3073a2442bb3c5979382e13c6a904adaf`, su V7.26 [PR #29](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/29) squash `564e3c4ad2caebec053d000659edb3bec453c6d4`. **Native KiCad9 CI V7.27 [run #43022065783](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43022065783) SUCCESS**: 14 unit test PASS, tutti gli step KiCad netlist/ERC + `pcbnew.FootprintLoad` PASS. [Artefatto #13854479601](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43022065783/artifacts/13854479601) ZIP effettivamente scaricato e letto: `v727.native_rha41_review.json` conferma **132 componenti, 100 reti, 0 nodi di netlist modificati, 42 footprint ancora mancanti**, U1 unico componente con modifica di `Footprint`, **36 errori invariati, warning **223→222** esclusivamente `footprint_link_issues` 4→3. No waiver.

**CAD V7.27 nuovo e vero:** `04_KiCad/Librerie_Footprint_V7.27_TI_RHA_HOLD/S3900E_TI_RHA_Review.pretty/LMX2572_RHA0040H_VENDOR_CANDIDATE.kicad_mod` (TI LMX2572 SNAS740B RHA0040H 6x6mm): 40 pad perimetrali 0,60×0,25mm/pitch0,50 + EP41 rame 4,50×4,50mm e **9 aperture F.Paste separate 1,26×1,26mm** a interasse 1,46mm (~70,56% nominale secondo esempio TI). `pcbnew` 9.0.8+dfsg-1 ha caricato veri 41 copper pads/9 paste apertures, tutti numeri, layer e quote superati. Nuovi AUX `04_KiCad/Gerarchico_Alimentazioni_V7.27_PLL_RHA41_REVIEW_NOT_FOR_FAB` e root `04_KiCad/Assemblaggio_RX_Power_V7.27_PLL_RHA41_REVIEW_NOT_FOR_FAB`; una sola modifica proprietà footprint di **U1 LMX2572**, ora in libreria locale `S3900E_TI_RHA_V727_HOLD`, senza toccare né pin DAP41 già presente su GND_MAIN né altre masse, etichette o fili. Nulla di questo costituisce qualifica assemblaggio/stencil o autorizzazione produttiva.

**ERC nativo aggiornato: 36 errori** = 26 `label_dangling`, 6 `power_pin_not_driven`, 4 `pin_not_driven`. **222 avvisi** = 219 `endpoint_off_grid` + **3 `footprint_link_issues`**. Tre refs rimaste: **F200/Y1** libreria `S3900E` footprint unvalidated; **L100** `Inductor_SMD:L_10.0x10.0_H5.0` inesistente nella libreria KiCad9, componente attuale `15uH / 3.5A` ma **MPN non scelto**, dati Isat/Irms/termica e land pattern vendor assenti. Non correggere selezionando footprint a caso per rendere ERC verde. **V7.28 prossimo:** MPN + calcolo reale dell'induttore L100 e modelli power, poi eventuale CAD footprint, senza forzare interfacce non qualificate; analizzare 219 off-grid con netlist diff per ogni trasformazione, senza snap automatico indiscriminato. Possibile revisionare i 10 pin undriven soltanto con fonte/ritorno reali.

**Vincoli invariati:** 15 cross-module RX/MCU/AUX **OPEN/HOLD**, SG48 HOLD, 42 componenti senza footprint, F200/Y1 non qualificati, PCB unica non esiste e non è stata fatta DRC globale. Progresso totale ~10% *stima storica* non aggiornata per audit. **NO FAB / NO GERBER / NO PCBWAY / NO TX**. Actions sbloccato direttamente dall'utente e oltre quota fatturabile: CI V7.27 una sola `pull_request`, non duplicare azioni costose. I 344 Python del CI V7.25 restano evidenza storica, non sono stati rieseguiti integralmente nella V7.27: 12 V7.26 e 14 V7.27 nuovi PASS.

---

## STATO ATTIVO — 11 novembre 2026, V7.26 INTEGRATA: 117 avvisi simboli eliminati realmente

**GitHub live:** [PR #29](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/29) **MERGED** squash `564e3c4ad2caebec053d000659edb3bec453c6d4`. [GitHub Actions 43019926260](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43019926260) **SUCCESS**, un unico runner KiCad9 di confronto nativo V7.25→V7.26, **12 test V7.26 PASS**, nessuna regressione elettrica verificata: **132 componenti, 100 reti, delta zero nodi pin/rete, 42 footprint non assegnati**. **36 errori ERC** identici prima/dopo; avvisi **340→223**, esattamente i **117 `lib_symbol_issues`** eliminati, senza soppressione regole/waiver. [Artefatto reale 13854287534](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43019926260/artifacts/13854287534), `v726.native_library_parity.json` letto dal ZIP (conferma 36/223 e `lib_symbol_warnings_new:0`).

**Reale CAD versione V7.26:** `04_KiCad/Librerie_Simboli_V7.26_UNIFIED_NOT_FOR_FAB/S3900E.kicad_sym` con **32 simboli univoci embedded** AUX/MCU/RX; 3 copie controllate dei fogli AUX e 6 nomi R/C distinti (`R_EFUSE,C_EFUSE,R_BUCK,C_BUCK,R_PLL,C_PLL`) mantenendo pin e fili intatti; nuovo root `04_KiCad/Assemblaggio_RX_Power_V7.26_UNIFIED_SYMBOL_LIB_NOT_FOR_FAB/`, `sym-lib-table` completo. Tutti i fogli storici V7.25 intatti e disponibili. Una CI mirata su `pull_request` soltanto per limitare costi Actions. **Non dichiarare che i 344 vecchi test sono stati rieseguiti V7.26**: restano run verde V7.25, mentre 12 nuovi test specifici sono PASS.

**Residuo ERC V7.26 (nativo):** 36 errori = 26 `label_dangling`, 6 `power_pin_not_driven`, 4 `pin_not_driven`; 223 avvisi = **219 `endpoint_off_grid` + 4 `footprint_link_issues`**. Quattro link non validi esatti: F200 `S3900E:` review, Y1 `S3900E:` review (entrambi HOLD/UNVALIDATED), L100 `Inductor_SMD:L_10.0x10.0_H5.0` assente, PLL U1 `Package_DFN_QFN:VQFN-40-1EP_6x6mm_P0.5mm_EP4.35x4.35mm` assente. Da **non** far sparire usando false footprint.

**NEXT V7.27:** valutare MPN vendor **TI LMX2572 RHA0040H VQFN40 + DAP41**, il cui pad centrale 41 compare già nella netlist U1 sul GND_MAIN con 10 GND periferici (da verificare pinmap/datasheet e RF power); creare solo un'impronta `HOLD` qualificata geometrica secondo land/stencil TI, verificare con `pcbnew.FootprintLoad` nativo e, se sicuro, sostituire l'alias KiCad U1 inesistente su nuovo AUX/root **solo reviewer-only**, assicurando netlist invariata. Il datasheet TI SNAS740B (2019) riferisce pad DAP come RF ground e prescrive thermal pad saldato con vias; esempio package RHA0040H espone **41 pad**, centrale **4,5 mm**, land periferici 0,60 × 0,25 mm passo 0,50, stencil 9 aperture da 1,26 mm con ~70% copertura. La guida pin functions TI ufficiale assegna **pin 11 VccCP, pin 21 VccBUF** (non basarsi su descrizioni image/OCR ambigue). L100 15uH/3.5A senza MPN e F200/Y1 restano HOLD, non assegnare footprint inventati. Evitare DRC senza PCB unica.

**Vincoli:** 15 cross-module RX/MCU/AUX OPEN/HOLD, SG48 HOLD, nessuna PCB unificata, no Gerber, PCBWAY, TX; 42 footprint mancanti, F200/Y1 package non approvati, power source/return 13,8→5→3,3V non dimostrato. Progresso storico ~10% stima invariata. **NO FAB / NO GERBER / NO PCBWAY / NO TX**.

---

## STATO CORRENTE — 11 novembre 2026 — V7.25 **MERGED**, 344 TEST PASS (consultare prima delle sezioni storiche)

Ultimo `main` revisionato in questa sessione: [V7.25 PR #28 merged](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/28), commit squash **`a1924b2b525de27b4e677b992abd702741922781`**. Le precedenti sezioni su V7.25 come *prossima* e su 48 footprint mancanti sono **storiche** e non devono prevalere sul presente checkpoint. V7.22 PR #23, V7.23 PR #25 (real `pcbnew.FootprintLoad`), V7.24 PR #26 (ottimizzazione trigger CI a consumo) sono già MERGED.

**Verifica live KiCad 9 e Python:** [Actions run #43012099267 — success](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43012099267) su PR #28, runner realmente eseguito, **344 Python PASS, 0 FAIL/0 SKIP, 23 gruppi** (10 nuovi V7.25 + 334 storici), controlli `kicad-cli` ERC/netlist pre/post, `pcbnew.FootprintLoad` tre vendor lib da V7.23, ngspice e regressioni. Artefatto verificato localmente: [#13850348324](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43012099267/artifacts/13850348324) con `v725.six_footprints.json`, due netlist e due ERC report nativi.

**CAD integrato V7.25, 7 fogli:** `04_KiCad/Modulo_MCU_CODEC_V7.25_SIX_FOOTPRINTS_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch` associa SOLO U6201 STM32G474RET6 LQFP64 ST, U6202 TLV320AIC3204 RHB33 TI e quattro U6203–U6206 TPS7A2033PDBVR DBV5 TI alle tre librerie review con nickname `_HOLD`; root `04_KiCad/Assemblaggio_RX_Power_V7.25_SIX_FOOTPRINTS_REVIEW_NOT_FOR_FAB/`. MPN ↔ pin simbolo ↔ pad e geometrie esempio vendor ST/TI collegate *per revisione nativa*, **non** approvate per assemblaggio/stencil/produzione. Lo schema di revisione passa da **48 a 42 footprint mancanti** (90/132 campi compilati), **senza cambiare alcun pin o nodo elettrico**, 132 componenti, 100 reti, ERC **36 errori/340 avvisi** prima/dopo. Termica, mask/paste di fabbricazione, F200/Y1, power source/return e PCB integrata rimangono HOLD.

**Issue ERC da trattare prossimo:** [#27 — triage ERP nativo](https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/27): 26 `label_dangling` errors (NON unire interfacce in HOLD), 6 `power_pin_not_driven` errors, 4 `pin_not_driven` errors; 219 `endpoint_off_grid` warnings, 117 `lib_symbol_issues` warnings, 4 `footprint_link_issues` warnings. Dieci pin da investigare U6203 IN/GND, AUX U200 IN/RTN, AUX U2 IN/GND, PLL U1 SYNC/SysRefReq/RampClk/RampDir. Prossima revisione sostanziale **V7.26**: qualificare libreria `S3900E` coerente con simboli embedded, controllare conflitti per pin/MPN e librerie on-disk, ridurre i warning librerie senza waiver, senza inventare connessioni elettriche. Non assegnare 42 impronte non giustificate. Lato energia, 15 interfacce OPEN/HOLD e source/return non dimostrati.

**Blocco V7.26 — collisione simboli già riscontrata senza alterare CAD:** i fogli AUX `01_EFUSE_AUX`, `02_BUCK_5V`, `03_PLL_LDO_TCXO` incorporano più definizioni con il medesimo id `S3900E:R` e `S3900E:C`, ma **non byte-identiche** (R: 648, 761, 753 caratteri; C: 749, 863, 855). La `sym-lib-table` root punta alla libreria RX di prova che manca dei simboli MCU/AUX. **Non aggregare automaticamente le definizioni**, non scegliere arbitrariamente una variante. Prima differenziare nomi solo quando la semantica pin/grafica diverge, poi creare libreria versionata e fare KiCad9 netlist/ERC differenziale. [Issue #27 aggiornato](https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/27). Nessuna correzione elettrica V7.26 introdotta da questo audit.

**Budget:** GitHub Actions sbloccato direttamente dall'utente; ora i minuti extra sono a pagamento. CI V7.25 su **pull_request soltanto**, no doppio push+PR. Evitare test ridondanti o runner a vuoto; non modificare billing senza esplicito ordine.

**NON pronto alla produzione:** 15 interfacce cross-module RX/MCU/AUX OPEN/HOLD, SG48 HOLD, 42 footprint senza assegnazione, F200/Y1 non validati, ERC 36/340, nessun layout PCB globale o DRC completo, avance globale storica ~10% stimata NON cambiata. **NO FAB / NO GERBER / NO PCBWAY / NO TX.**

---

## Verifica V7.25 — lettura nativa ERC storica e triage rigoroso, 11 novembre 2026 (nessun nuovo CAD integrato)

**Artefatto del run verde V7.22** [13849074958](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42997229515/artifacts/13849074958) estratto in ambiente di analisi senza consumo di altri minuti Actions. Il file KiCad9 originale `v722.revised.erc.rpt` (52.064 bytes) contiene esattamente **376 messaggi: 36 errori e 340 warning**. La distribuzione letta direttamente (non ricostruita da chat precedente) è: **26 `label_dangling` errors**, **6 `power_pin_not_driven` errors**, **4 `pin_not_driven` errors**, **219 `endpoint_off_grid` warnings**, **117 `lib_symbol_issues` warnings**, **4 `footprint_link_issues` warnings**.

**Dieci pin da investigare con fonti reali prima di ogni modifica elettrica:**
- MCU U6203 **IN:1, GND:2** (nessuna sorgente/return riconosciuta, 2 ERC).
- AUX eFuse U200 **IN:1, RTN:8** (2 ERC), source/return 13.8V/EFUSE_RTN OPEN/HOLD.
- AUX U2 LDO **IN:1, GND:2** (2 ERC), source/return OPEN/HOLD.
- AUX PLL U1 **SYNC:5, SysRefReq:28, RampClk:30, RampDir:32** (4 ERC, input senza driver).

**117 warning librerie** includono simboli locali `S3900E` non trovati nella libreria dichiarata per il root (per esempio `CONN_2_EXT_DRAFT`, `HOST_SPI_6PIN_DRAFT`, `F/C/D/R`): `sym-lib-table` del root punta a RX test library insufficiente. Prossimo ECO plausibile: costruire **libreria S3900E versionata completa** da simboli embedded reali, deduplicare verificando pin/MPN, retarget root **solo dopo** aver provato che netlist non cambia; non inventare simboli o ottimizzare via waiver. **219 off-grid warnings** vanno affrontati senza snap indiscriminato; **26 dangling labels** rappresentano potenziali interfacce non qualificate, non ricollegare TX. [Issue #27 con tabella e blocker puntuali](https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/27).

**GATE:** niente nuova PR V7.25 né modifica elettrica per questi problemi finché non è dimostrata una correzione sicura. Root V7.22 invariato in V7.23/V7.24. Ultimo CI V7.0 [43011495583](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43011495583) **SUCCESS**, e successivo commit solo checkpoint precedente `cac509458f743655c5a503067b98bced74f78c77` **non ha prodotto Actions runs**, confermando il risparmio di workflow V7.24. Uso Actions ora a pagamento: evitare runner inutili.

**Sicurezza invariata:** 15 interfacce OPEN/HOLD, 48 footprint ancora mancanti, 36/340 ERC non corretti, SG48 HOLD, nessuna PCB unica/DRC globale. **NO FAB / NO GERBER / NO PCBWAY / NO TX**.

---

## Sessione 11 novembre 2026 ore 12:20 CET — **V7.23 e V7.24 INTEGRATE, V7.25 PROSSIMA**

**Verifica indipendente da GitHub live:** `main` dopo [PR #25](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/25) squash `8e46b26bb488fb1484ee9cc2b1c366b91badfb80` e [PR #26](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/26) squash `9308b710db8a13071de60ad9f9b93fed3c414b89`, entrambe **MERGED**. Base V7.22 precedente [PR #23](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/23), squash `e6b04082e4268cccc8338127824a0a2e0341ad91`, [run 42997229515 attempt 2 PASS](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42997229515) **334 Python PASS, KiCad9/ERC/netlist root prima/dopo 36 errori + 340 warning, 132 comp/100 reti, U6202 EP33 local GND**.

### V7.23: nuovo controllo vero KiCad9 sulle tre librerie

- Script `03_Verifiche/V7.23/audit_native_footprints_v723.py` usa **`pcbnew.FootprintLoad`** del KiCad nativo, NON regex per la verifica finale. Compara coordinate, dimensioni, pad numerati, layer rame F.Cu, F.Mask, F.Paste e paste-only. **102 pad elettrici numerati in totale (ST LQFP64 64 + codec TI RHB 33 + TI DBV 5)**; TI codec EP33 ha **quattro pad separati di pasta non-rame** 1,49×1,49 mm. Suite di review, nessun export né PCB di prova salvata.
- Primo [run 43010894472](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43010894472) **failure INSTALL** perché l'Ubuntu runner non ha `python3-kicad` come pacchetto separato: nessun test CAD in quel run. Corretto workflow rimuovendo il pacchetto fittizio (binding `pcbnew` installato insieme a `kicad`).
- Successivo [run 43011010863](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43011010863) **SUCCESS**, KiCad **9.0.8+dfsg-1**, step native footprint load **success**, artefatto [13849469820](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43011010863/artifacts/13849469820) `v723.native_footprint_load.json`. Letto log CI: ST64, TI RHB33+4 paste-only, TI DBV5, geometry/layers veri tutti PASS. **Non si sono assegnati footprint a U6201–U6206.** Il gate dimostra caricamento nativo, non qualifica stencil/assemblaggio/DRC globale.
- La PR #25 è stata verificata **e integrata**, quindi i tre footprint candidati restano nell'albero root, ma sempre `HOLD/NO ASSIGNMENT`.

### V7.24: controllo preventivo dei costi Actions

- **L'utente ha sbloccato Actions a pagamento**. Nessuna modifica di billing o budget effettuata dall'agente. Il vecchio workflow `.github/workflows/verifica_v70.yml` partiva su ogni push in `main`, anche solo aggiornamenti checkpoint. [PR #26](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/26) limitata ai `paths` tecnici (`ci/**`, `03_Verifiche/V6.9/**`, `03_Verifiche/V7.0/**`, `04_KiCad/**`, stesso workflow), mantenendo `workflow_dispatch` e tutti gli step SHA256/tag v7.0 + regressioni numeriche invariati. Nessuna modifica CAD o elettrica V7.24, nessun test indebolito **dentro** il workflow. Per modifiche solo a `00_Gestione_Progetto` non deve partire il runner V7.0. V7.24 merge squash `9308b710db8a13071de60ad9f9b93fed3c414b89`; [baseline run 43011495583](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43011495583) **in coda all'ultima consultazione** — verificarne il risultato in diretta, non dichiararlo verde se non completato.

### Stato reale e prossimo passo V7.25

**48 footprint ancora mancanti in schema** nonostante le nuove librerie, F200/Y1 presenti ma UNVALIDATED. **15 interfacce cross-domain OPEN/HOLD**, `EFUSE_RTN` non unire a `GND_MAIN`, SG48 HOLD. Root 7 fogli/132 comp/100 reti, **ERC 36 errori / 340 warning preesistenti**, nessuna PCB unica completata, nessun DRC globale possibile su PCB inesistente, avanzamento ~10% stima storica invariata. **NO FAB / NO GERBER / NO PCBWAY / NO TX**.

**V7.25 priorità:** confrontare pin-to-pad/vendor per U6201/U6202/U6203–U6206 anche contro netlist native, verificare stencil e assembly DFM, fare vera correzione KiCad se emerge un difetto con prova. In parallelo analizzare/reportare e poi ridurre *difetti ERC reali* senza PWR_FLAG fittizi, short fra domini o waiver; esaminare source/return 13,8V→5V→3,3V e termiche LDO; soltanto dopo assegnazione controllata di footprint e progetto PCB unitario. Usare **una CI mirata per revisione** e monitorare costo GitHub Actions.

---

## Aggiornamento 11 novembre 2026 ore 12:09 CET — **V7.22 INTEGRATA, CI VERDE, passare a V7.23**

**Fonte live verifica GitHub:** `main` revisione ingegneristica V7.22 integrata con squash [PR #23](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/23), commit **`e6b04082e4268cccc8338127824a0a2e0341ad91`**. La PR #23 è **MERGED**, non più aperta. Tutti i paragrafi sotto questa sezione che dicono `PR #23 NON MERGIATA` o `CI bloccata` sono **storico superato**, NON stato corrente.

**RUN NATIVA realmente riuscita:** [GitHub Actions 42997229515, tentativo 2, 11 Nov 11:09 UTC](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42997229515) `success`, runner attivo, KiCad9 + ngspice, esportazione netlist/ ERC root pre/post, **334 test Python PASS, 0 FAIL/0 SKIP**, 22 gruppi (26 V7.22 +308 storici). Artefatto reale [13849074958](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42997229515/artifacts/13849074958), `v722.native_pin_net_diff.json` letto e confrontato in ZIP, conferma **132 componenti /100 reti**, un solo nodo nuovo `/MCU_CODEC_AFE_existing_V2_1_UNQUALIFIED/GND, U6202, pin 33`, zero nodi rimossi. ERC **36 errori/340 warning** prima **e dopo** (non pulito, nessun peggioramento). I 3 footprint locali da vendor ST/TI sono verificati con 16 test statici di geometria (oltre ai test della ECO), registrati in fp-lib-table ma **NON assegnati**; **48 footprint ancora mancanti**. `NO FAB` sempre attivo.

**Blocco costi Actions risolto dall'utente:** budget Actions sbloccato; il runner hosted è tornato attivo e il workflow ha avuto successo. [Issue #24](https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/24) deve essere chiusa come risolta (quota pregressa 2.000/2.000 + budget $0, poi aumento approvato direttamente dall'utente). Evitare lanci ripetuti o duplicati: i nuovi minuti oltre quota sono **a pagamento**, minimizzare workflow e preferire una sola CI mirata per revisione. Non modificare billing/budget autonomamente.

**Priorità V7.23:** verificare in KiCad9 parsing eseguibile dei 3 `.kicad_mod` (non basta regex), rivedere pad/mask/paste/courtyard con datasheet e vincoli IPC, qualificare MPN-symbol-pad-footprint per U6201/U6202/U6203–U6206 prima di eventuale assegnazione, mantenendo hold qualora un elemento non dimostrato. Poi source/return della catena 13,8V→5V→3,3V ed ERC nativo. Non generare PCB dimostrativa chiamandola radio completa.

**VINCOLI:** 15 interfacce cross-module **OPEN/HOLD**, SG48 HOLD, nessun corto GND dei domini o EFUSE_RTN, nessun PWR_FLAG arbitrario; root **7 fogli, 132 comp,100 reti, ERC 36/340**, **48 footprint senza assegnazione**, F200/Y1 unvalidated, nessuna PCB unificata; ~10% stima storica immutata. **NO FAB / NO GERBER / NO PCBWAY / NO TX.**

---

## Aggiornamento confermato — quota GitHub Actions esaurita (11 novembre 2026)

**CAUSA BLOCKER IDENTIFICATA DALL'UTENTE:** screenshot originale dell'avviso ufficiale GitHub `jd3485`: **2.000 / 2.000 minuti GitHub Actions consumati, 100% del ciclo**. Reset comunicato per **1 dicembre 2026**. GitHub dichiara che oltre quota la fatturazione è possibile salvo **budget Actions impostato a $0**, caso in cui le esecuzioni vengono bloccate fino al reset. **Non è stato letto direttamente il valore budget $0 dell'account**: non inventare impostazioni; indisponibilità dei runner con `runner_id=0` su workflow nuovi e vecchi coerente con esaurimento quota. [Issue #24 aggiornata](https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/24).

**Regola operativa NO COSTI:** non modificare budget/fatturazione, non acquistare minuti, non cambiare visibilità del repo o bypassare protezione branch. Non generare workflow falliti a ripetizione prima del reset senza ragione. **Sviluppo V7.22 può proseguire su PR #23** con verifiche native offline/locali a costo zero se l'ambiente dispone di KiCad9/ngspice; per contro in questa sessione `kicad-cli` e `ngspice` risultano **assenti** e `apt-get update` ha raggiunto timeout (~18s), quindi **nessuna verifica KiCad9 locale è stata eseguita**. I test Python V7.22 non sono stati eseguiti con netlist ERC reali. Non fare merge della PR tecnica senza gate nativi; dopo reset 1 dicembre rieseguire interamente il CI e registrare ID/run/esiti effettivi.

**Stato immutato:** PR #23 aperta, branch HEAD `9aedec44e1fe10bdc61a3a55c75903263a98cbae`, tre nuovi footprint candidati ST/TI non assegnati; 26 test nuovi + 308 storici **334 previsti NON ESEGUITI**; 48 footprint root mancanti, ERC baseline V7.21 36/340, 15 interfacce OPEN/HOLD, PCB unica assente. **NO FAB / NO GERBER / NO PCBWAY / NO TX; SG48 HOLD.**

## Sessione 11 novembre 2026 — **V7.22 PR #23 NON MERGIATA**: ECO codec + tre librerie vendor, GitHub Actions runner BLOCCATO

**Verifica live:** `main` base tecnico integrato **V7.21 PR #21** (CI [42987421253](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42987421253), 308 Python PASS in KiCad9); PR #22 solo protocollo; `main` prima di questa continuazione `b805a333e23e78d44e0c357cf43a66ae6cdb3646` (checkpoint precedente). **Non dichiarare V7.22 integrata**.

**Ramo in corso (NON MERGED):** [PR #23](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/23), branch `feature/v7.22-codec-ep33-ground-eco`, HEAD corrente `9aedec44e1fe10bdc61a3a55c75903263a98cbae`.

### Modifiche CAD reali e conservazione NO FAB

- Foglio KiCad nativo versionato `04_KiCad/Modulo_MCU_CODEC_V7.22_EP33_GROUNDED_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch`: simbolo U6202 TLV320AIC3204 RHB con **pad termico fisico n. 33** passive `EP_GND_THERMAL_PAD`, etichetta `GND` esattamente sul pin locale (448.26,190.48 mm). Vecchi pin/collegamenti conservati; nessuna unione GND MCU/AUX/RX/`EFUSE_RTN`, nessun `PWR_FLAG`. Baseline V7.21 non toccata.
- Nuovo root 7 fogli `04_KiCad/Assemblaggio_RX_Power_V7.22_EP33_NOT_FOR_FAB/` punta allo schema MCU aggiornato e contiene tabelle librerie locali. Indice di moduli **NON elettricamente unificati**.
- **Tre librerie nuove con veri file `.kicad_mod`, geometria vendor controllata staticamente e registrata nel `fp-lib-table` V7.22 (non assegnate a nessun simbolo):**
  1. `04_KiCad/Librerie_Footprint_V7.22_ST_LQFP_TI_HOLD/S3900E_ST_LQFP_Review.pretty/STM32G474RE_LQFP64_ST_DS12288_CANDIDATE.kicad_mod`: ST DS12288 Rev.6 Fig.63, LQFP64 64 pad 1,20×0,30mm, passo 0,50mm, centri lati ±5,75mm, rame esterno 12,70mm.
  2. `04_KiCad/Librerie_Footprint_V7.22_RHB_TI_HOLD/S3900E_TI_RHB_Review.pretty/TLV320AIC3204_RHB0032E_VENDOR_CANDIDATE.kicad_mod`: TI SLOS602E pp.53–54, 32 pad periferici 0,60×0,25mm / passo 0,50, rame termico **EP33 3,45×3,45mm**, **4 aperture pasta 1,49×1,49mm**, copertura ~74,61% come stencil esempio TI da 0,125mm.
  3. `04_KiCad/Librerie_Footprint_V7.22_DBV_TI_HOLD/S3900E_TI_DBV_Review.pretty/TPS7A20_DBV0005A_VENDOR_CANDIDATE.kicad_mod`: TI SBVS338H p.57, cinque pad 1,10×0,60mm, centri colonna ±1,30mm e passo 0,95mm; pin1 IN,2 GND,3 EN,4 N/C,5 OUT.
- I **sei componenti U6201–U6206 rimangono senza footprint assegnato**. Per confronto i footprint standard KiCad consultati (non confermati in KiCad9 live) avevano quote pad differenti dagli esempi vendor; questa differenza **non certifica** i generici come inutilizzabili, e la compatibilità di maschera/stencil/courtyard/assemblaggio **NON** è approvata. Nessuna PCB completa, Gerber, TX, simulazione hardware, PVT o test a banco.

### Test e blocco live

- `03_Verifiche/V7.22/` report tecnico, **26 test Python nuovi** (EP33/netlist, ST64/TI5 pin names, pad 64/33/5, paste apertures, HOLD). Workflow `.github/workflows/v722_codec_ep33_native.yml` prevede **334 test totali** = 26 nuovi +308 storici, e **VERI export ERC/netlist KiCad9 prima/dopo**.
- **VERIFICHE EFFETTIVE FINORA: statiche**, lette dal GitHub branch e confrontate contro dati vendor: file S-expression bilanciati, sorgente MCU ricostruibile invertendo le sole modifiche pin33/label/titolo, root senza altre variazioni, geometria 64+33+5 pad, 4 aperture pasta EP33, tre library links e **nessun footprint assegnato**. Non confondere controlli statici con parsing/DRC/ERC nativi.
- **Actions non avvia il runner**, causa NON dimostrata: V7.0 baseline [run 42987689585](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42987689585) successo 08:31 UTC con 10 steps e runner; stesso workflow V7.0 [run 42994271590](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42994271590) failure con zero step; V7.22 HEAD [runs 42997214762](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42997214762) e [42997229515](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42997229515) `failure` con `runner_id=0, runner_name="", steps=[]`, dunque **zero test V7.22 realmente eseguiti**, non 334 PASS. Vedere [issue #24 — CI runner blocker](https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/24). GitHub job logs non disponibili; accertare Settings/Actions/runner e possibile account/billing (solo ipotesi), oppure eseguire KiCad9 su runner realmente funzionante. No waiver fittizio.
- **Non integrare PR #23** senza controllo nativo del nuovo file KiCad, dei tre `.kicad_mod`, netlist ed ERC differenziale, test regressione 334 e qualifica package; non alterare policy o account settings alla cieca.

### Prossima ripresa (non chiedere all'utente “continua”)

1. Recuperare `main`, `AGENTS.md`, questo checkpoint e [PR #23](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/23); usare lo stesso ramo esistente. Recuperare Actions #24 e motivazione reale runner KO, ripristinare CI se disponibile oppure ambiente KiCad9 equivalente; installare versioni reali senza produrre output fab. Eseguire `kicad-cli sch export netlist` + `sch erc` originale vs versione e `python -m unittest discover -s 03_Verifiche/V7.22` insieme alle regressioni.
2. Correggere eventuali difetti nativi rilevati, controllare footprint/MPN/land pattern e GND pad fisico, solo dopo CI verde e nessun gate di approvazione integrare PR e aggiornare checkpoint con merge SHA e run ID verificati.
3. Passare autonomamente a V7.23: 42 altri footprint mancanti, F200/Y1 non validati, power budget 13.8→5→3.3V, 15 cross-module HOLD, veri ERC e IF/RF/meccanica, poi PCB unica.

**Baseline main V7.21 ancora valida:** root 7 fogli, **132 componenti / 100 reti, ERC 36 errori + 340 warning**, footprint 48 mancanti (nuove librerie non cambiano il conteggio), 15 interfacce OPEN/HOLD, nessuna PCB globale; avanzamento storico ~10% *stima* invariata. **NO FAB / NO GERBER / NO PCBWAY / NO TX · SG48 HOLD**.

## Ultimo risultato ingegneristico integrato

| Campo | Valore |
|---|---|
| Ultima revisione ingegneristica | **V7.21** |
| PR | [#21 — merged](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/21) |
| Commit squash | `9805f110d0acf59e69f7f54e87e299248b99d96b` |
| Ultima CI della revisione | [run 42987421253 — success](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42987421253) |
| Test | **308 PASS, 0 FAIL, 0 SKIP**: 24 V7.21, 284 precedenti |
| Ultima vera modifica elettrica schema master | **V7.19**; V7.20–21 audit/verifiche, schemi invariati |
| Netlist root KiCad9 | **7 fogli, 132 componenti, 100 reti** |
| ERC root KiCad9 | **36 errori / 340 warning** |
| Footprint root | **84 compilati**, **48 mancanti** (46 MCU/CODEC, J100/J101), F200/Y1 esplicitamente non validati |
| Interfacce tra moduli | **15 OPEN/HOLD** |
| PCB singola completa | **NON creata**, nessun routing globale |
| Avanzamento PCB complessivo | **~10% stimato**, non automatico, non aumentato dalla V7.21 |
| Release | **NO FAB / NO GERBER / NO PCBWAY / NO TX · SG48 HOLD** |

## Prossima priorità di lavoro autonomo

**V7.22 — Correzione reale CAD con verifica vendor dei sei circuiti principali MCU/CODEC/POWER**, non solo un altro rapporto:

1. Per il codec **U6202 TLV320AIC3204 RHB** il simbolo KiCad nativo ha i soli pin **1–32**, mentre il package fisico ha la piazzola termica **EP33**. TI impone saldatura e collegamento a ground plane. Verificare [datasheet TI](https://www.ti.com/lit/ds/symlink/tlv320aic3204.pdf), aggiornare **copia versionata** dello schema/simbolo, aggiungere pin 33 e connessione di massa corretta **solo dopo** qualificare partizione GND; confronto pin-pad/EP, netlist ERC e stencil. **Non assegnare footprint prima di questa ECO**.
2. Qualificare da vendor ST **U6201 STM32G474RET6 LQFP64 10×10 0,5**; TI **U6202 RHB VQFN32 5×5 EP33**; quattro TI **U6203–U6206 TPS7A2033PDBVR SOT23-5**, con corretta funzione/pin e land pattern. Sei candidati già controllati per numeri pad in libreria KiCad9, ma *non ancora approvati*.
3. Passare poi alla qualifica degli **altri 42 footprint mancanti**, incluso X6201 e FB6201 e AUX J100/J101, e dei due assegnati esplicitamente `UNVALIDATED` F200/Y1. Non assegnare valori e footprint a caso per chiudere il contatore.
4. Risolvere in base a prove il source/return della catena 13,8 V→TPS26600 eFuse→TPS54202 5 V→TPS7A20 3,3 V. I sei LDO contano 2 su AUX 5V, 4 su MCU 5V ancora non qualificata. Nessuna unione arbitraria delle due reti o di EFUSE_RTN con GND_MAIN. Eseguire corrente/termica, inrush, PVT reali e verifiche a banco.
5. Qualificare gradualmente le **15 interfacce**, RX→IF e chassis; solo con netlist realmente integrata realizzare **PCB unica** in KiCad, poi DRC, regole RF, confronto pin-pad-net, ERC, e prototipo prima di un rilascio.

Se in questa sessione si completa V7.22, **non fermarsi automaticamente**: dopo CI/PR/merge passare subito alla priorità V7.23 e successive, finché consentito da tempo e strumenti.

## File e riferimenti obbligatori

- [Protocollo permanente agenti](../AGENTS.md)
- [Handoff storico completo](../RIPRENDI_IN_UNA_NUOVA_CHAT.md)
- [Rapporto tecnico V7.21](../03_Verifiche/V7.21/RAPPORTO_TECNICO_CAD_V7.21.md)
- [Gates per la PCB unica](../01_Specifiche/V7.21/PIANO_QUALITA_PCB_UNICA_GATES_V7_21.md)
- [Stato GitHub PR](https://github.com/jd3485/Superstar3900-SMD-Evolution/pulls)
- [Run GitHub Actions](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions)

## Contratto di aggiornamento del checkpoint

Alla fine di ogni **versione** e **prima della scadenza del contesto Work**:

- Sostituire questa sezione con **latest PR effettivamente merged**, commit, branch HEAD, ultima Actions CI verde o rossa, totale test, ERC/DRC, netlist, cambiamenti elettrici CAD REALI, percentuale PCB onesta.
- Annotare ramo/PR eventualmente **aperti ma non mergiati**, errori inattesi e prossima correzione, con comandi/file per riprendere senza chat precedenti.
- Segnalare ciò che rimane HOLD e **NO FAB / NO TX**; non dichiarare sbloccato un gate senza evidenza.
- Aggiornare lo storico `RIPRENDI_IN_UNA_NUOVA_CHAT.md`; non affidarsi alla memoria della nuova sessione.

**Una chat nuova deve riuscire a riprendere tutto leggendo `AGENTS.md` + questo documento + GitHub live, anche se non ha accesso alla cronologia della chat precedente.**
