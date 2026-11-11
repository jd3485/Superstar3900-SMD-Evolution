# WORK_STATO_CORRENTE.md — checkpoint canonico di ripartenza da GitHub

**Aggiornato: 11 novembre 2026.** Sorgente di verità: repository GitHub **jd3485/Superstar3900-SMD-Evolution**, branch **main**; questo documento è un checkpoint, verificare sempre HEAD / PR / Actions in diretta.

**Prima di procedere in una nuova chat Work: LEGGERE ANCHE [AGENTS.md](../AGENTS.md)** (mandato, bootstrap, vincoli e procedura multi-revisione). Il file AGENTS è la configurazione stabile, questo è il registro da aggiornare ogni volta.

## Sessione 11 novembre 2026 — V7.22 **IN PR NON MERGIATA**, CI NON ESEGUITA (leggere prima di V7.21)

**Ultima revisione tecnicamente integrata resta V7.21 / PR #21**: la PR #22 ha integrato soltanto la procedura di continuità. HEAD di main all'avvio di questa sessione: `ac244c8f4a6058be3f9093f00d60a850d68a9501`. Nessuna nuova ECO elettrica V7.22 è stata integrata in main.

**Lavoro reale NON integrato:** [PR #23 — V7.22 codec EP33](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/23), ramo `feature/v7.22-codec-ep33-ground-eco`, HEAD aggiornato `7e30d105e33cb9ed9c6530d9304799aba9c07697` (dopo fix del test sul pin 33 della MCU). Nuovi CAD nativi versionati:
- `04_KiCad/Modulo_MCU_CODEC_V7.22_EP33_GROUNDED_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch` aggiunge U6202 TLV320AIC3204 RHB **EP33** pin passivo, label GND locale all'endpoint (448.26,190.48), senza collegare domini cross-module; simboli/pin esistenti invariati.
- `04_KiCad/Assemblaggio_RX_Power_V7.22_EP33_NOT_FOR_FAB/` contiene indice root aggiornato a 7 fogli, progetto e tabelle librerie. U6202 **senza footprint assegnato**, TI land/stencil e qualificazione ancora HOLD.
- `03_Verifiche/V7.22/test_ep33_v722.py` include **10 test scritti ma non eseguiti in CI**: deve risultare un singolo ref-pin-net in più su `/MCU_CODEC_AFE_existing_V2_1_UNQUALIFIED/GND` U6202:33, zero connessioni tolte e zero regressioni ERC. `.github/workflows/v722_codec_ep33_native.yml` prevede anche 308 precedenti regressioni (318 attesi **NON CONFERMATI**).
- `03_Verifiche/V7.22/RAPPORTO_TECNICO_CAD_V7.22.md` documenta ECO e rischi.


**Qualifica statica vendor aggiuntiva sullo stesso ramo PR #23:** confronto numerazione-nomi completo di **U6201 STM32G474RE, 64/64 pin**, contro [ST DS12288 Rev.6 Figura 7 LQFP64 p50](https://www.st.com/resource/en/datasheet/stm32g474vb.pdf); confronto **U6203/U6204/U6205/U6206 TPS7A2033PDBVR, 5/5 pin** contro [TI SBVS338H Rev.H DBV Figura 4-4 p4](https://www.ti.com/lit/ds/symlink/tps7a20.pdf), ordine 1 IN, 2 GND, 3 EN, 4 N/C, 5 OUT. Due test Python statici aggiunti (10 V7.22, 318 totali attesi), **nessuno eseguito in CI**. È verifica pin-symbol vendor, NON autorizzazione MPN-land pattern/footprint/stencil, verifiche termiche, o release.

**Gate GitHub Actions BLOCCATO prima del runner:** run [42993364753](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42993364753) e [42993371627](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42993371627), entrambi `failure` entro secondi, **runner_id=0, runner_name vuoto, steps=[] (zero comandi eseguiti)**. Anche run precedenti [42992722193](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42992722193) e [42992776122](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42992776122) falliti con zero step. Non disponibili log (BlobNotFound). **Causa non confermata**: verificare Actions/runner, eventuale restrizione/billing del repository privato e annotazioni degli assegni; non attribuire il fallimento a kicad-cli o al test senza log.  Ultimi run aggiornati sul commit corrente: [42994080741](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42994080741) e [42994090571](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42994090571), entrambi ancora failure con 0 step, nessun runner. **Nessun ERC/netlist/DRC KiCad9 V7.22 eseguito o approvato in questa sessione**; niente merge automatico prima di CI verde.

**Verifica statica effettivamente eseguita via GitHub:** letto schemi originale e nuovo; parentesi S-expression bilanciate, sottraendo solo (a) nuovo pin EP33, (b) nuova label GND, (c) titolo rev si ricostruisce **esattamente byte-per-byte** lo schema MCU precedente; facendo retarget del foglio e dei titoli si ricostruisce esattamente il root originale. Nessun PWR_FLAG introdotto. Controllo ha anche identificato e corretto su PR un falso test che contava il pin 33 della MCU e del codec insieme. Questa è una verifica *statica*, **non** conferma connettività KiCad nativa.

**Prossime azioni obbligatorie (senza nuovo ramo V7.22):** riprendere PR #23 e HEAD, risolvere motivo dell'assenza runner o eseguire gli stessi comandi KiCad9 in ambiente idoneo; esaminare output ERC/netlist prima/dopo e total 316 test; se verde e merge consentito integrare PR, quindi aggiornare nuovamente questo checkpoint con SHA merge e Actions ID. Solo poi V7.23: verifica vendor U6201 STM32G474RET6 LQFP64 e U6203–U6206 TPS7A2033PDBVR DBV e footprint/stencil. Non assegnare footprint senza vendor signoff; non confondere 33 pad con connessione validata e PCB reale.

**Rischi aperti confermati:** baseline main V7.21 **36 errori/340 warning ERC**, 48 footprint mancanti, F200/Y1 non validati; 15 interfacce OPEN/HOLD, cross-ground/return source non qualificati, PCB unica assente, avanzamento ~10% *stima storica invariata*, SG48 HOLD. **NO FAB / NO GERBER / NO PCBWAY / NO TX**.

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
