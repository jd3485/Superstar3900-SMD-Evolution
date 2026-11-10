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
