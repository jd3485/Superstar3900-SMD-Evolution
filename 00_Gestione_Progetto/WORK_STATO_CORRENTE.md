# WORK_STATO_CORRENTE.md — checkpoint canonico di ripartenza da GitHub

**Aggiornato: 11 novembre 2026.** Sorgente di verità: repository GitHub **jd3485/Superstar3900-SMD-Evolution**, branch **main**; questo documento è un checkpoint, verificare sempre HEAD / PR / Actions in diretta.

**Prima di procedere in una nuova chat Work: LEGGERE ANCHE [AGENTS.md](../AGENTS.md)** (mandato, bootstrap, vincoli e procedura multi-revisione). Il file AGENTS è la configurazione stabile, questo è il registro da aggiornare ogni volta.

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
