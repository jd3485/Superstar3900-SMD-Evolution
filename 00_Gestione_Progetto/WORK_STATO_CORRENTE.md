# WORK_STATO_CORRENTE.md — checkpoint canonico di ripartenza da GitHub

**Aggiornato: 11 novembre 2026.** Sorgente di verità: repository GitHub **jd3485/Superstar3900-SMD-Evolution**, branch **main**; questo documento è un checkpoint, verificare sempre HEAD / PR / Actions in diretta.

**Prima di procedere in una nuova chat Work: LEGGERE ANCHE [AGENTS.md](../AGENTS.md)** (mandato, bootstrap, vincoli e procedura multi-revisione). Il file AGENTS è la configurazione stabile, questo è il registro da aggiornare ogni volta.

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
