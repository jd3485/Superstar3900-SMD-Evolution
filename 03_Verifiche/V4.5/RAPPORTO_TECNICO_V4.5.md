# Superstar 3900 SMD Evolution — Rapporto tecnico V4.5

**Data:** 8 novembre 2026  
**Ambito:** modulo sperimentale RX a 50 Ω (NON radio completa)  
**Stato:** ricostruzione librerie portabili **NON qualificata per produzione**.

## Risultato principale

La revisione converte i footprint incorporati nella **copia sperimentale** del PCB SMA V4.3 e i simboli embedded nello schema candidato V4.4 in librerie locali KiCad. Nuovo progetto in:
`04_KiCad/Modulo_RX_Test_50ohm_V4.5_LIBS_PORTABILI_NOT_FOR_FAB/`.

- **3 librerie `.pretty`**, **9 footprint `.kicad_mod`** distinti, corrispondenti alle **15 istanze** del PCB.
- **1 libreria `.kicad_sym`** con **9 tipi di simbolo**; gli ID delle istanze dello schema sono gli stessi degli embedded.
- Tabelle `fp-lib-table` e `sym-lib-table` con variabile `${KIPRJMOD}`; non richiedono le cartelle del computer dove i file sono stati generati.
- Stesso basename per il nuovo `.kicad_sch` e `.kicad_pcb`. Il secondo è **byte-identico al PCB V4.3 sperimentale**; lo schema deriva dal V4.4 con aggiornamento del nome di progetto, non è una netlist nativa KiCad.
- Le piazzole delle 9 librerie sono state confrontate con i corrispondenti footprint incorporati nel PCB, preservando forme, offset, dimensioni e orientamenti locali. Le net e i dati di collocazione propri del PCB non sono stati copiati nella libreria.
- **26 test statici superati**, incluse mutazioni intenzionali per rilevare discrepanze geometriche e simboli mancanti. Ripetute le regressioni V4.0–V4.4: 2.400 combinazioni logiche V4.0, 12 test V4.1, 19 V4.2, 21 V4.3, 20 V4.4.

**Importante:** ricostruzione fedele della geometria di studio **non** significa verifica di correttezza di un'impronta o idoneità di produzione. Il nome delle librerie storiche è stato mantenuto per non rompere le associazioni in schema/PCB, anche quando il footprint SMA della copia V4.3 è sperimentale.

## Controlli non eseguiti

`kicad-cli` **non disponibile** nell'ambiente: nessun ERC, DRC, refill delle zone, controllo nativo di parità tra schema e PCB. La procedura `03_Verifiche/V4.5/RUN_KICAD_RX_V45.sh` copia prima il progetto in una cartella temporanea e si arresta con codice 3 se non trova KiCad, senza generare falsi rapporti positivi. La prova del blocco è in `PROVA_LAUNCHER_NO_KICAD/STATUS.txt`.

## Rischi aperti (NO GO produzione)

| Rischio | Attività necessaria | Stato |
|---|---|---|
| SMA TE CONSMA002-SMD-G | Download CAD DXF/STEP e confronto completo quote, mask, paste, sporgenze, bordo PCB e footprint V4.3; approvazione componente esatto | **Aperto** |
| ADL5535 | Verifica pin 2 e paddle sul piano di massa, strategia vie, dissipazione, stencil, assemblaggio e temperatura a regime | **Aperto** |
| Librerie portabili | Aprire con KiCad, correggere eventuali warning, verificare associazioni UUID/footprint e pin | **Aperto** |
| Regole elettriche | ERC su schema e DRC con riempimento zone e `--schematic-parity` su PCB candidato | **Non eseguiti** |
| Impedenza | Stack-up confermato, geometria CPWG reale, modelli S11/S21 e misure VNA | **Aperto** |
| RF fisica | Prototipo, alimentazione in sicurezza, corrente, temperatura, guadagno e stabilità, mismatch e isolamento | **Non eseguito** |

L'ADL5535 richiede che il paddle esposto e il pin GND abbiano un collegamento termico adeguato al piano di massa. Il layout attuale non contiene via-in-pad sotto il paddle: un percorso alternativo **non** ne dimostra la capacità termica. Le quattro zone di massa del PCB sono ancora da riempire/validare nativamente. La differenza nominale degli SMA V3.8/V4.3 è stata trattata come *ipotesi geometrica*, non come correzione certificata.

## Fonti ufficiali

- TE Connectivity, prodotto CONSMA002-SMD-G, disegno e file CAD elencati: https://www.te.com/en/product-CONSMA002-SMD-G.html
- Analog Devices ADL5535, dati tecnici e land pattern: https://www.analog.com/en/products/adl5535.html
- KiCad, gestione librerie PCB e schematiche: https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html e https://docs.kicad.org/9.0/en/eeschema/eeschema.html
- KiCad, comandi `sch erc` e `pcb drc`: https://docs.kicad.org/9.0/en/cli/cli.html

## Riproduzione

```bash
python3 03_Verifiche/V4.5/crea_librerie_v45.py
python3 03_Verifiche/V4.5/test_librerie_v45.py
bash 03_Verifiche/V4.5/RUN_KICAD_RX_V45.sh ./rapporti_native
```

Il terzo comando necessita di `kicad-cli` installato e non modifica i sorgenti originali. Una volta disponibili risultati reali, devono essere valutati manualmente prima di autorizzare la produzione. **Nessun file Gerber né ordine PCBWay è stato generato.**

**Avanzamento globale stimato:** 37% invariato; hardware RX convalidato: **0 moduli**; TX sempre disabilitata/non realizzata.
