# AGENTS.md — Superstar 3900 SMD Evolution, protocollo permanente per ChatGPT Work e altri agenti

> **LEGGERE ALL'INIZIO DI OGNI NUOVA SESSIONE**. Questo file è una procedura di lavoro persistente nel repository GitHub. Non presume memoria personale, né che una nuova chat conosca la precedente.
>
> Repository canonico: **jd3485/Superstar3900-SMD-Evolution** · ramo canonico: **main**.
>
> Stato corrente operativo: leggere **[WORK_STATO_CORRENTE.md](00_Gestione_Progetto/WORK_STATO_CORRENTE.md)** da **main** (non dedurre lo stato dalla data di questo file). Storico: [RIPRENDI_IN_UNA_NUOVA_CHAT.md](RIPRENDI_IN_UNA_NUOVA_CHAT.md) e [PROTOCOLLO_CONTINUITA_MAIN.md](00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md).

## Mandato permanente dell'utente

Realizzare una **PCB unica Superstar 3900 SMD Evolution** tecnicamente corretta, coerente con i componenti reali, **senza errori elettrici o di DRC noti**. L'utente delega **scelte tecniche ordinarie, priorità e sequenza di revisioni**; NON vuole dover inviare `continua` dopo ogni piccolo passo. Il mandato vale come **orientamento del flusso** per nuove sessioni avviate dall'utente; da solo non attiva Work in background né autorizza spese, fabbricazione o atti che richiedono conferma dell'utente.

**Modalità esecutiva:** in una singola sessione Work/agent, procedere attraverso **più revisioni sensate e sostanziali**, finché esistono tempo, capacità e fonti attendibili. Non fermarsi soltanto perché una PR è stata integrata. Dopo una PR verde, aggiornare lo stato, passare al prossimo blocker ragionevole, continuare entro i limiti della sessione. Fermarsi quando manca un dato essenziale, non c'è accesso all'app/strumento o per un vincolo di sicurezza reale. Non promettere lavoro dopo la chiusura della sessione.

## Regola permanente V7.30: ChatGPT progetta; GitHub conserva; Actions verifica solo quando serve

**Il responsabile tecnico degli errori è ChatGPT, non GitHub Actions.** Ogni modifica CAD/elettrica deve avere una valutazione dei datasheet, delle connessioni, di pin e pad e dei rischi; non sostituire la diagnosi con un run verde.

1. Eseguire localmente quando effettivamente disponibili KiCad CLI, Python e ngspice. Se una prova non è realizzabile localmente, usarne la **CI tecnica mirata sulla PR** e registrare run ID e rapporti nativi. Non considerare superato un test non eseguito. Prima del merge di una PR CAD richiedere ERC e netlist nativi prima/dopo, conservazione dei nodi pin-rete, test componenti/footprint e simulazioni pertinenti; DRC quando esiste una vera PCB. Mai sopprimere errori o abbreviare gate safety per risparmiare.
2. **49 workflow rilevati in `main` all'audit del 13 novembre 2026** (il numero è storico e può cambiare): solo `pull_request` con `paths` tecnici pertinenti oppure `workflow_dispatch` manuale. I quattro controlli KiCad V5.4–V5.7 **e la sonda sperimentale V7.12 `v712_rx_schematic_native_probe.yml`** sono manual-only; la suite completa V7.12 resta automatica. Non duplicare push, PR e merge. Le librerie V7.22 condivise restano eccezione intenzionale per i due controlli complementari elettrico/footprint. La CI rapida `actions_policy_quick.yml` verifica YAML, liste paths, policy di sicurezza e segnala ogni **nuova sovrapposizione esatta** fra trigger PR non esplicitamente autorizzata. Non creare un workflow nuovo per ogni report: raggruppare revisioni coerenti quando i controlli nativi e il fail-closed restano possibili.
3. Per 03_Verifiche escludere soltanto rapporti Markdown con !03_Verifiche/**/*.md alla fine dei filtri; non escludere test Python, netlist, modelli, CSV, dati tecnici e input reali. Non escludere le specifiche Markdown se usate dalle prove. Conservare integrità SHA256 tag v7.0, manifest e regressioni numeriche automatiche su input originali e manuali per CAD indipendente; non avviare il workflow numerico V7.0 a ogni merge KiCad se la CI nativa specifica è già passata.
4. Concurrency annulla soltanto run **PR obsoleti della stessa PR** e **mai** un controllo manuale/finale. Conservere tutti gli step tecnici preesistenti; evitare apt/pip, job o installazioni ripetute quando non necessari. Per nuovi workflow usare permissions contents:read e workflow_dispatch con trigger PR paths stretti se necessario.
5. Non modificare billing, budget, visibilità o settings GitHub senza consenso esplicito. GitHub Actions può costare dopo quota inclusa; audit e prove locali vanno privilegiati ma non inventati. Memorizzare i veri esiti di CI, errori e HOLD nel checkpoint GitHub.
6. Invariati **NO FAB / NO GERBER / NO PCBWAY / NO TX, SG48 HOLD, 15 cross-module OPEN/HOLD**, nessun PWR_FLAG artificiale, corto fra domini o falsa PCB completa.

## Contratto di bootstrap per una nuova chat

**Prima di modificare qualsiasi cosa**:

1. Recuperare **l'ultimo HEAD di `main`**, non una copia storica della chat.
2. Leggere **`AGENTS.md`** (questo file) e **`00_Gestione_Progetto/WORK_STATO_CORRENTE.md`**, poi il rapporto tecnico più recente, `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, eventuali PR o check non completati.
3. Ricostruire lo stato reale con **GitHub PR, file nativi KiCad, test e CI**: distinguere chiaramente branch, PR aperta, merge confermato e artefatti hardware. Il documento di stato è un *indice*, non prova indipendente.
4. Se esiste un ramo/PR attivo già avviato e valido, **riprendere quello** invece di duplicare. Altrimenti scegliere in autonomia il primo problema elettrico/PCB non risolto, creare branch di lavoro e puntare a modificarne concretamente gli artefatti.
5. Eseguire verifiche proporzionate: **kicad-cli sch erc/netlist, DRC se esiste PCB, test Python, vendor docs**. Confrontare prima/dopo. Non falsificare i controlli o cancellare regressioni.
6. Se CI passa e non ci sono vincoli di approvazione, aprire PR e integrare con merge previsto dal repository; se fallisce, correggere e rilanciare. **L'integrazione automatica di normali revisioni ingegneristiche è autorizzata dall'utente, se i tool e le policy lo consentono**; operazioni ad alto impatto richiedono i consensi necessari.
7. Dopo **ogni revisione sostanziale/merge**, aggiornare `00_Gestione_Progetto/WORK_STATO_CORRENTE.md` con PR, commit, test, prossimo blocker, rischi aperti, e il più recente handoff; non lasciare solo la descrizione nella chat. Inserire date, URL e run ID veri. In caso di lavoro incompleto indicare esattamente cosa NON è stato unito.
8. Finché il lavoro e gli strumenti lo consentono, **proseguire con il blocker successivo senza attendere un nuovo messaggio**. Prima che la sessione termini, produrre un **handoff autonomo** sufficiente alla prossima chat, anche se il task è incompleto.

**Regola anti-loop**: non creare microrevisioni di soli report se è praticabile una reale correzione dei file CAD; non aumentare arbitrariamente la percentuale PCB per audit, script o documenti; non creare un PCB dimostrativo scollegato chiamandolo «radio completa».

## Vincoli di sicurezza non negoziabili

- **NO FAB / NO GERBER / NO PCBWAY / NO TX**, senza nuova autorizzazione esplicita dopo verifiche complete e prototipi. **SG48 HOLD**; mai abilitare/integrare un percorso di trasmissione solo per eliminare un errore.
- **15 interfacce cross-module RX/MCU/AUX restano OPEN/HOLD** finché non sono dimostrate tensioni, livelli logici, fonte/ritorno, pin, condizioni di startup, RF/IF, protezione e documentazione. Non unire reti con lo stesso nome se domini distinti.
- **Niente PWR_FLAG inventati, waiver ERC/DRC fittizi, corti fra masse non qualificate o `EFUSE_RTN` e `GND_MAIN`**, nessuna soppressione artificiale per generare test verdi.
- Qualificare **MPN ↔ pin del simbolo ↔ pad del footprint ↔ impronta produttore** e package/librerie prima dell'assegnazione; evitare footprint ipotetici, masse e piste RF arbitrarie.
- Non sostituire l'assenza di scheda completa con una stima di «100%». Prove di simulazione **non equivalgono a misure hardware**.
- Diffidare dei vecchi rapporti se contraddetti dal **master `main`**; usare sempre la più recente evidenza nativa.

## Stato tecnico alla creazione del protocollo (11 novembre 2026, **V7.21 integrata**)

Questo paragrafo è storico; consultare sempre il file di stato attuale. V7.21: [PR #21](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/21) integrata con squash `9805f110d0acf59e69f7f54e87e299248b99d96b`; [CI finale run 42987421253](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42987421253) successo **308 Python PASS, 0 FAIL/0 SKIP**, KiCad9/nGspice, root **7 fogli, 132 componenti, 100 reti, ERC 36 errori/340 warning**. **48 footprint mancanti** (46 MCU/CODEC, J100/J101 AUX), 2 popolati ma esplicitamente non validati (F200 fusibile, Y1 TCXO). Sei package candidati controllati come numeri di pad nella libreria KiCad9, **non assegnati**. TI TLV320AIC3204 RHB pad termico **EP33** è fisico ma **manca dal simbolo U6202** nativo (solo pin1–32); TI richiede connessione a ground-plane, dunque ECO obbligatoria con pin-pad-ground/stencil verificati. Sei TPS7A2033 300mA: caso teorico JEDEC DBV 5→3,3V @300mA e 40°C dà Tj~135,4°C, un **segnale di rischio** non una misura. Ingresso 13,8V/eFuse/return, buck 5V, 3,3V, RX→IF, meccanica rimangono da qualificare. Nessuna PCB unica. Progresso totale PCB ~10% stimato, **non** misurato. **Next starting target V7.22**: ECO pin fisico EP33 e qualifica MPN/symbol/footprint dei sei IC prioritari, più reale modifica CAD versionata.

## Sblocco del passaggio tra chat

Se l'utente apre una nuova chat Work, bastano le istruzioni del **Progetto ChatGPT** oppure questa frase:

> **Riprendi autonomamente il progetto `jd3485/Superstar3900-SMD-Evolution`: leggi `AGENTS.md` e `00_Gestione_Progetto/WORK_STATO_CORRENTE.md` da `main`, quindi continua più revisioni tecniche reali con CI/PR/merge e aggiorna l'handoff. Mantieni NO FAB / NO TX.**

In assenza di contesto della vecchia chat **non inventare ricordi**: il repo e le evidenze sono la memoria affidabile. Se GitHub non è disponibile nella nuova sessione, dirlo subito senza fingere di aver letto i documenti.
