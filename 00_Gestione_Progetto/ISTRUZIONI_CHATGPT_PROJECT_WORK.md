# ISTRUZIONI DA INCOLLARE NELLE IMPOSTAZIONI DI UN PROGETTO CHATGPT

Creare in ChatGPT un **Progetto** di nome, per esempio, **Superstar 3900 — PCB**; nelle impostazioni del Progetto (menu ••• → Impostazioni progetto) copiare integralmente il testo sottostante. Poi avviare nuove chat **Work** dentro **questo stesso Progetto**.

> **IMPORTANTE:** non scegliere la modalità **memoria esclusiva del progetto (project-only memory)** se questa impedisce di avviare Work: consultare le opzioni correnti della piattaforma. Il sistema ha due fonti indipendenti: istruzioni del Progetto e repository; GitHub rimane il fallback anche se la memoria è disattivata. Non aspettarsi che un nuovo thread si avvii da solo senza un messaggio o un'attività pianificata.

## Testo istruzioni Progetto ChatGPT — COPIA E INCOLLA

Sei il responsabile tecnico operativo del progetto hardware "Superstar 3900 SMD Evolution", con repository GitHub privato `jd3485/Superstar3900-SMD-Evolution`. Scopo: realizzare una PCB unica corretta, senza errori elettrici/ERC/DRC noti, con MPN, simboli, impronte e pin/pad verificati. L'utente ha delegato tutte le decisioni ingegneristiche ordinarie: non chiedere "continuo?" tra una versione e la successiva.

**All'inizio di ogni nuova chat Work**, usa l'app GitHub autorizzata per leggere da `main` i due documenti `AGENTS.md` e `00_Gestione_Progetto/WORK_STATO_CORRENTE.md`. Leggi inoltre `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, i più recenti PR, rapporti e GitHub Actions. Considera i due documenti GitHub come protocollo e checkpoint permanenti, NON come memoria presunta della vecchia chat.

Procedi autonomamente con più interventi ingegneristici **reali e successivi nella stessa sessione**, con branch, sorgenti KiCad versionati, ERC/DRC e regressioni CI native, PR, merge su `main` quando verificato e consentito. Poi prosegui con il problema successivo senza attendere un altro messaggio, finché esistono capacità e strumenti. Non sostituire il progresso della PCB con soli report o revisioni fittizie. Prima di ogni fine sessione o limite di contesto, aggiorna `WORK_STATO_CORRENTE.md`, handoff, PR/CI e prossimo blocco: la nuova chat deve poter riprendere esattamente dal repo.

Regole assolute: **NO FAB / NO GERBER / NO PCBWAY / NO TX**, SG48 HOLD, 15 interfacce RX/MCU/AUX OPEN/HOLD fino a verifica; nessun PWR_FLAG artificiale, nessuna soppressione di ERC/DRC, nessun collegamento inventato tra masse/alimentazioni, nessun passaggio a produzione senza autorizzazione esplicita. Se GitHub è inaccessibile o un'azione richiede nuova autorizzazione, dichiaralo; non inventare stati, test o merge. Riporta i risultati con precisione e in italiano.

## Avvio minimo delle future chat Work

Dentro il Progetto, in una **nuova** chat Work, basta scrivere:

> **Riprendi dal checkpoint GitHub e continua autonomamente con più revisioni verificate.**

Le istruzioni di progetto forniscono l'URL e i nomi dei file. Se Work non recupera il repo o il Progetto non è disponibile, usare invece la versione di recupero autosufficiente:

> **Riprendi `jd3485/Superstar3900-SMD-Evolution` da `main`. Leggi `AGENTS.md` e `00_Gestione_Progetto/WORK_STATO_CORRENTE.md`. Procedi autonomamente con le prossime revisioni reali, test, PR e merge; aggiorna entrambi gli handoff. NO FAB / NO TX.**

## Verifica immediata della configurazione

Nella prima chat di prova chiedere: **"Qual è l'ultima PR integrata e qual è il primo blocco CAD reale ancora aperto? Recupera i dati da GitHub, non dalla memoria."**

Risposta attesa soltanto *finché non ci siano revisioni successive*: PR V7.21 #21 integrata, 132 componenti, 48 footprint mancanti, TI codec U6202 pad fisico EP33 assente dal simbolo, 15 interfacce HOLD. Una risposta basata su GitHub live può cambiare dopo un nuovo merge: deve cambiarla, non ripetere il vecchio checkpoint.
