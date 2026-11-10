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
