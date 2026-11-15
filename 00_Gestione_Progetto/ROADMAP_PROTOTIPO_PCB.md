# Roadmap operativa verificabile — Superstar 3900 SMD Evolution

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
