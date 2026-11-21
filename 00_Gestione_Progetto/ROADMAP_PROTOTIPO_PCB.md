# Roadmap operativa verificabile — Superstar 3900 SMD Evolution

## V7.87: MODE/ILIM eFuse, PCB reale e CI prima di merge (21 novembre 2026)

[PR #115](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/115) propone master PCB KiCad9 139 impronte e **24 segmenti F.Cu** (17 baseline V7.86 + 7 su due reti eFuse); spostati R203/R204 senza alterare 139 mappe pin-net o disunire i domini. [CI nativa 44899587378](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/44899587378) SUCCESS: solo **1 invalid_outline +308 unconnected**; PCB SHA256 `1f0d4b118da23d93805c55be4d811094d114de0807be5180786f7697a2ab4530`. Non è un test di circuiti funzionanti, eFuse fault recovery o idoneità a fabbricazione. Verificare CI finale sul commit checkpoint prima di merge. G3 alimentazione/eFuse, G6 power PCB, G7–G9 restano APERTI; Y1 pin10 SG48, D200, 15 interfacce HOLD, eFuse RTN≠GND_MAIN, mai FAB/TX senza consenso.

## V7.87 — G3 eFuse MODE/ILIM: rame reale proposto, NON RELEASE (21 novembre 2026)

**Baseline V7.86 verificata su main**, 139 footprint / 17 piste / KiCad9 DRC 1 invalid_outline +310 unconnected, PR #114 merge `b9fe17f05cc7e01149e31450d2b9e77048b08d68`. Nuovo ramo V7.87: 2 resistori fisicamente riposizionati R203/R204, sette tratti reali su `ILIM_NODE`/`EFUSE_MODE` per U200.11/R203.2 e U200.6/R204.2, pin e reti 139 conservati, altro rame invariato. G3 ancora APERTO: serve verificare pin11 e pin6 con TI, numeri R203/R204, eFuse recovery e tutte correnti/ground ritorni. DRC native, CI e merge ancora da provare. Nessuna connessione tra EFUSE_RTN e GND_MAIN; nessuna autorizzazione a fabbricazione, batterie o TX.

**Pin TI TPS26600 PWP qualificato da [datasheet](https://www.ti.com/lit/ds/symlink/tps2660.pdf)**: OUT15/16, NC13, FLT14 (opzionale/floating). La prima CI V7.86 falliva per test errato OUT13, non per PCB. Test corretto OUT15 + pin13/14 senza nets; nessuna correzione artificiosa ai circuiti; continuità di output e return-domain ancora da instradare/qualificare.

## V7.86 G3/G6 — disposizione fisica condensatori eFuse, non qualificazione (21 novembre 2026)

Main V7.85 [PR #113](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/113) integrata, KiCad9 run 44897986143 SUCCESS; PCB 139 footprint, 17 segmenti, DRC nonrelease **1 invalid_outline +310 unconnected**. Proposta reale V7.86: PCB nativa dedicata 139/139 footprint, tre condensatori **C200/C201/C202** riposizionati verso le rispettive piazzole di U200; resto fisico/elettrico invariato. Verifiche obbligatorie prima del merge: distanza reale migliorata per tutti e tre, pad/net preservati, KiCad9 DRC senza nuove violazioni, sicurezza CI, file PCB committato (già versionato in branch). Non confondere distance-placement con routing o loop di corrente validati. G3/G4/G6/G7/G8/G9 APERTI, 15 interfacce e SG48 HOLD, no fab/TX.

## V7.85: sottorete FB/DIV copper reale su PR #113, NON RELEASE (21 novembre 2026)

Nuova revisione PCB unico, 139 footprint, +11 segmenti F.Cu su BUCK_FB/BUCK_DIV_TOP e tre passivi riposizionati; conserva sei segmenti BOOT/EN V7.84. Run KiCad9 [44896371938](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/44896371938) ha mostrato DRC diagnostico **1 invalid_outline +310 unconnected** prima della conclusione del workflow; non dichiarare CI finale superata fino al controllo del run successivo dopo correzione log e file versionato. G6 ancora APERTO: feedback U100, power loops, 5V currents, GND returns, input fuse/eFuse, Ceff, stackup, outline e RX. Y1/SG48, D200 e 15 interfacce in HOLD. NO FAB/GERBER/PCBWAY/TX.

## G6 V7.85 — rete FB e partitore buck: rame reale in verifica (21 novembre 2026)

**Baseline main integrata:** V7.84 PR #112, KiCad9 run 44894281465 SUCCESS, PCB 139 footprint/6 tratti BOOT+EN e DRC diagnostico 1 invalid_outline +314 non instradati. **Proposta**: V7.85 riposiziona C105/R101/R102 e crea 4 collegamenti fra componenti di feedback `BUCK_FB`/`BUCK_DIV_TOP`; nessun rame GND, 13.8V, BUCK_SW, 5V ad alta corrente, RX/TX; CI e file nativo non ancora completati. I collegamenti verso U100 e le compensazioni sono sempre tecnicamente non qualificate. G6/G7/G8/G9 restano aperti e nessun ordine PCB è autorizzato.

## V7.84 gate G6 — routing locale reale buck, NONRELEASE (21 novembre 2026)

**Evidenza nativa [CI 44893786818](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/44893786818)**: PCB unico KiCad9 139 footprint, 12 posizioni buck rilocalizzate, sei tratti rame F.Cu BOOT/EN (non quelli di potenza), pad-net 139 invariati, DRC **1 invalid_outline +314 unconnected**, nessun corto residuo. File board realmente salvato su PR #112, commit `69390206f1c72787bf97e52659d232469186ba30`, SHA256 `364498b0b9ede338257698c4bb35b3ac0132dea15f720b55349d4e58fb7e8bc8`. CI finale su file versionato ancora da eseguire/verificare prima di merge. G6 ancora APERTO: manca C102 SW, corrente switching, ritorni massa, piastre dissipative, DRC di rilascio, outline e stackup. Nessuna progressione G3 alimentazioni/eFuse, ERC o interfacce provata. G7/G8/G9 totalmente HOLD; nessuna fabbricazione.

## V7.84 G6 — PCB buck local feedback/boot review, NON RELEASE (21 novembre 2026)

Baseline: V7.83 PR #111 integrata, 139 impronte fisiche. V7.84 sul ramo `pcb/v7-84-buck-local-placement-bootstrap-enable-hold` modifica realmente 12 posizioni buck e propone quattro segmenti locali netlist-qualified su `BUCK_BOOT`/`BUCK_EN`. G6 uscita intermedia **solo dopo** file PCB native versionato, confronto pin/net delle 139 impronte, DRC KiCad9 con anomalie residue enumerate, e CI aggiornata. Nessuna qualifica corrente switching/PI termica, 13,8V/eFuse, return plane, RF, outline o fab release. G3/G4/G5/G6/G7/G8/G9 restano aperti. Y1/SG48 e D200 HOLD, 15 interfacce aperte; nessuna percentuale progettuale dedotta dal numero impronte.

## V7.83 G5/G6 PCB RX fisica versionata — 21 novembre 2026, NON RELEASE

Nel [run KiCad9 44891671924](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/44891671924) risultano **139 impronte KiCad9 fisiche** sul master PCB unico: 124 V7.82 preservate + 15 del coupon RX, tutte da netlist 141 componenti /103 reti, `.kicad_pcb` effettivo salvato su PR #111 commit `22dd37985b39722f3f7294d2ccdb101d35de2b5d`. DRC diagnostico **1 invalid_outline +316 unconnected**; **non equivale** a DRC PASS, circuiti integrati, layout RF o potenza qualificata. Occorre CI **finale sul file versionato** prima di merge. Due componenti D200 DNP e Y1 SG48 HOLD intenzionalmente mancanti. G1–G9 restano APERTI dove indicati; nessuna fabbricazione. La roadmap storica sottostante resta orientativa e non deve sovrascrivere questo stato.

**G6 next exit objective:** schemi elettrici RX→IF/audio e sorgenti/ritorni 13.8/5/3.3 V qualificati; componenti vendor meccanici, orientamento SMA e outline; instradamento e piani massa reali, DRC e regole RF. Continuare senza sopprimere ERC o collegare domini sul solo nome. NO FAB/NO TX.

## Stato di lavoro V7.83 — 21 novembre 2026 — RX PCB WIP, NO FAB

**Baseline verificata su main:** V7.82 merge PR #110, HEAD `5d817ea0e8f717f982a4a2edfec60531b6eeaf18`; 124 footprint reali del PCB master, 141 componenti e 103 reti schematica, ultimo ERC nativo V7.79 **25 errori/180 warning**. DRC V7.82 diagnostico: **1 invalid_outline + 280 unconnected**, senza piste, zone né bordo. Questo paragrafo prevale sulle baseline storiche V7.74/V7.80 sotto riportate.

**G5/G6 in progresso NON certificato:** ramo `pcb/v7-83-rx-15-footprints-native-staging-hold` introduce generatore KiCad9 di 15 footprint del coupon RX: J9101, J9102, J9103, J9104, J9105, U9101, L9101, C9101–C9105, R9201–R9203. Il generatore copia ogni connessione dalla netlist nativa e confronta *tutti* i footprint e pin/net preesistenti con V7.82, senza mutare lo schema. **139/141 è un obiettivo di placement, non ancora un risultato provato**: attendere workflow KiCad9, artefatto board e versione fisica committata. D200 TVS DNP e Y1 TCXO pin10 SG48 restano esclusi HOLD. Placement RF su griglia *provvisoria*, non impedenza 50 ohm, geometria RF, connettori/orientamento meccanico né ritorni qualificati.

**Criterio di uscita G6 intermedio V7.83:** esportazione KiCad9 reale 139 riferimenti, 15 componenti RX esatti, 124 invariati, coppie pin/pad/net confrontate con netlist, nessuna pista o ponte domini, DRC nativo nonrelease con ogni violazione conservata; successivamente salvare effettivamente il `.kicad_pcb` verificato nel branch, riavviare checks e solo allora valutare merge. G6 globale rimane APERTO senza outline, routing, stackup, PCB di produzione o 15 interfacce cross-module autorizzate.

**Successivi blocchi ingegneristici:** qualifica footprint SMA RX con orientamento fisico; Ceff del buck 5V e ritorno eFuse/F200 13,8V; carichi reali sei LDO; 15 interfacce; routing RF/IF e piani massa verificati; ERC 25/180 reale, DRC e revisione indipendente. **NO FAB / NO GERBER / NO PCBWAY / NO TX.**


## Avanzamento G6 — V7.80 (19 novembre 2026), **WIP NON RELEASE**

Il generatore `03_Verifiche/V7.80/build_master_power_placement_v780.py` e il nuovo elaborato master fisico `04_KiCad/PCB_MASTER_V7.80_POWER_PLACEMENT_WIP/S3900E_MASTER_V780_STAGING_NO_FAB.kicad_pcb` (integrazione effettiva da verificare in PR/CI) iniziano lo **staging vero** di 25 footprint power da 141 componenti del master 7 fogli. Gate G6 **APERTO**: è solo piazzamento, nessun outline, routing, zone, stackup verificato o DRC di rilascio, 15 interfacce HOLD. Priorità: qualifica elettrica input/return/MPN e vincoli meccanici, poi espandere PCB con pin-net e DRC controllati. Non trattare il numero 25 come completamento percentuale.


**Baseline accertata:** 15 novembre 2026, `main` HEAD `37b1f909d56f58fe8c1dfad9b9600d0e4ac456d1`; ultima revisione tecnica integrata V7.74, PR #101, squash `91588269e3ed86922db0a79728f44bf3c04665b8`. Questo documento è un piano di gate, **non** una prova di progresso PCB, una nuova ECO elettrica o un'autorizzazione FAB.

## Evidenze riproducibili della baseline

- Master gerarchico V7.74: `04_KiCad/Assemblaggio_RX_Power_V7.74_SIX_PWR_SOURCE_RETURN_PROVENANCE_HOLD/`.
- `03_Verifiche/V7.74/RAPPORTO_SEI_PIN_POWER_SOURCE_RETURN_ERC_V774.md`, CI nativa KiCad9 [43572358648](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/43572358648): 7 fogli, 140 componenti, 103 reti, ERC **28 errori e 180 warning**; 476 test PASS, non hardware test.
- Le 28 anomalie ERC comprendono **22 label_dangling** e **6 power_pin_not_driven**; non sono autorizzazioni a cancellare label, alterare simboli o inserire PWR_FLAG.
- [Issue #57](https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/57): eFuse latch-off/reset, protezione upstream e coordinamento fuse e input non risolti.
- Nessuna PCB radio completa verificata, nessun DRC globale; gli studi RX standalone NON equivalgono alla PCB unica.

## Sequenza di gate — nessuna percentuale inventata

| Gate | Completato e verificato | Da fare e dipendenze | Blocco / criterio di uscita verificabile | Prossima azione |
| --- | --- | --- | --- | --- |
| **G1 Schemi funzionali** | Master gerarchico 7 fogli e netlist V7.74 disponibili | Inventario funzione-per-funzione RX, PLL, alimentazione, MCU, codec, IF/audio; definire componenti fisici per sezioni ancora teoriche | **APERTO** finché ogni funzione richiesta non ha schema nativo e percorso ingresso/uscita tracciato | Estrarre matrice di copertura da schemi e specifiche; creare vere ECO laddove esista pinout qualificato |
| **G2 Integrazione RX/PLL/MCU/audio/power** | 140 componenti / 103 reti nel master V7.74 | 15 interfacce RX/MCU/AUX **OPEN/HOLD**: per ciascuna dimostrare dominio, sorgente, ritorno, logica, startup, RF/IF, protezione, pin | **APERTO**: non unire per somiglianza dei nomi; SG48/Y1 pin10 HOLD; TX disabilitata | Contratto di una interfaccia per volta con datasheet e confronto pin-net prima/dopo |
| **G3 Alimentazione e sicurezza** | V7.74: sorgenti e ritorni delle sei anomalie ERC tracciati ma NON corretti | J100/sorgente 13,8V e ritorno; F200 1,5A candidato e curva fusione; U200 TPS26600 (R203 ILIM, MODE, latch-off, reset indipendente da 3,3V); SW200; D200 DNP; buck U100 TPS54202 + L100/C103/C104; sei LDO 3,3V con carichi/transienti e Ta reali | **BLOCCANTE**: topologia di recovery e protezioni da qualificare; `EFUSE_RTN` diverso da `GND_MAIN`; nessuna falsa continuità | Preparare decisione documentata power-cycle upstream vs SHDN indipendente vs autoretry e relativo schema **solo dopo** verifica datasheet/pin/limiti |
| **G4 ERC elettrico autentico** | Inventario 22 label dangling + 6 pin non pilotati, CI originaria allegata | Rimuovere le cause con collegamenti qualificati e sorgenti/ritorni legittimi | **APERTO: 28 errori/180 warning**. Ogni ECO: ERC nativo prima/dopo, multiset finding, netlist/pin-rete e giustificazione delle differenze | Prendere errore reale con solida prova elettrica, senza waiver e senza PWR_FLAG fittizi |
| **G5 Qualifica MPN/simbolo/footprint** | Qualifiche parziali di componenti e pad termico codec effettuate nelle revisioni precedenti | Registro ciascun designatore: MPN esatto, datasheet revisione, simbolo pin, pad footprint, land pattern vendor, DNP, assemblaggio | **APERTO** finché tutti i componenti montabili hanno corrispondenza MPN↔pin↔pad e footprint provati | Partire da connettore ingresso, F200, U200, U100, L100, C103/C104 e LDO; annotare i candidati non qualificati |
| **G6 PCB unica** | Studi PCB RX 50Ω standalone storici, non PCB radio completa | Stackup, outline, connettori/meccanica, placement funzionale, domini analogici/digitali/RF, loop di potenza, correnti ritorno, termica | **BLOCCANTE**: manca PCB unica con netlist coerente al master; non inventare routing antenna e ritorni | Avviare PCB master **solo con** footprint qualificati e contratti domini; non chiamare completa una PCB studio |
| **G7 DRC/PI/SI/termica/RF** | Simulazioni e prove parziali; non misure hardware | DRC globale, clearance, vias, neck-down, dissipazione, caduta tensione, Ceff reali, stabilità loop 5V, rumore PLL, impedenza RF/IF e isolamento | **APERTO**: report nativi riproducibili e nessun errore di fab noto; validare assunzioni fisiche con reviewer | Pianificare check mirati a ogni progressione reale di PCB, non solo altra analisi marginale |
| **G8 Revisione indipendente** | Non svolta su un progetto PCB completo | Reviewer esterno/indipendente, distinta, pin/pad, ERC/DRC, safety e criticità RF, piano test | **APERTO** fino a review formale con evidenze e anomalie chiuse | Richiedere review dopo G1–G7 |
| **G9 Autorizzazione prototipo** | Nessuna autorizzazione | Richiedere espresso assenso dell'utente dopo G8 | **NO FAB / NO GERBER / NO PCBWAY / NO TX**. Nessun ordine o collegamento a batteria/veicolo prima di consenso | Non eseguire |

## Backlog tecnico immediato, ordinato per sblocco

1. **Architettura 13,8V ingresso/eFuse**: estrarre dal master U200 pin1/8/9/17, J100, F200, R203/R204, SW200; verificare eventuali discontinuità elettriche contro datasheet, escludere reset MCU-only su alimentazione a valle; registrare scelta e implementare schema solo quando fondata.
2. **Budget 5V→3,3V**: raccogliere valori nominali/massimi e transitori da datasheet del carico effettivo di ogni U2/U3/U6203–U6206; stimare termica con limiti espliciti e condizioni Ta/rame. Il rating 300mA per LDO non è una misura di carico, e il budget 2A buck non è validato.
3. **Qualifica connettore/fusibile/protezioni e componenti di potenza**: MPN, impronte, land pattern e orientamento reali, specificando ogni dato mancante; non creare footprint di fantasia.
4. **Interfacce RX/PLL/MCU**: distinguere 22 label dangling da interfacce da lasciare isolate per sicurezza (PTT/TX e TCXO pin10 in particolare); integrare solo quando ogni percorso ha un contratto qualificato.
5. **Sviluppo PCB master**: aprire elaborato unico coerente e verificare ogni successiva espansione con DRC nativo; studi RF isolati restano tali.

## Regole di registrazione per ogni prossimo ciclo

Per ogni ECO annotare file CAD effettivi, PR/merge SHA, rapporti nativi eseguiti (o NOT_RUN), variazioni di errore e netlist, decisioni ancora HOLD, impatto sulla PCB e successivo problema concreto. Conservare il checkpoint `00_Gestione_Progetto/WORK_STATO_CORRENTE.md` come indice aggiornato. Non utilizzare conteggio PR o test come misura sostitutiva della PCB. In nessun caso la roadmap stessa cambia gli ERC o qualifica l'hardware.
