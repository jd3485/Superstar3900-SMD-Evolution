# Superstar 3900 SMD Evolution — rapporto tecnico V5.3

**08/11/2026 · modulo ricevente RF 50 Ω · revisione di controllo statico · NON PER FABBRICAZIONE**

## Risultato nuovo

È stato sviluppato `audit_indipendente_v53.py`, un verificatore che interpreta da zero le espressioni S dei sorgenti `.kicad_sch`, `.kicad_pcb` e delle impronte locali `.kicad_mod`. A differenza dei test storici fondati soprattutto su stringhe e identificatori, legge i pin definiti nelle librerie dei simboli, calcola i punti terminali, percorre i fili e le relative etichette e li confronta con le reti assegnate alle piazzole sul PCB candidato **V5.2**.

| Controllo | Risultato statico |
|---|---|
| Simboli e footprint associati | 15 / 15 |
| Pin elettrici ricostruiti dalla geometria dello schema | 31 / 31 |
| Segmenti di filo con un'etichetta di rete agli estremi | 31 / 31 |
| Reti distinte | 8 |
| Discordanze pin–rete schema/PCB | 0 rilevate |
| Avvisi su pin senza filo o etichetta | 0 rilevati |
| Divergenze nella geometria delle piazzole tra PCB e librerie locali | 0 sui 15 footprint |
| Associazioni del percorso UUID simbolo → footprint | 15 / 15 coerenti nel modello |

**Limite sostanziale:** i risultati si riferiscono unicamente al formato e alle caratteristiche supportate dal parser Python in questo progetto; non equivalgono a un netlist esportato da KiCad, a ERC, DRC, prova RF, misura 50 Ω o verifica meccanica/termica. Non sono stati modificati i sorgenti CAD.

L'analisi controlla inoltre gli SMA: il footprint presenta 1 pad RF e quattro piazzole GND tutte con **numero 2**, coerente con il simbolo a due pin, ma la correttezza dimensionale TE di queste piazzole rimane **da approvare**. Il paddle U101 resta nella variante sperimentale con sei vie termiche, con processo via-in-pad e stencil **non approvati**.

## Prove e tracciabilità

- `03_Verifiche/V5.3/test_v53.py`: **18 test superati**; includono test che introducono volutamente disconnessioni dei fili, errori di rete, di valore, di footprint, di UUID e di geometria nelle librerie, verificando il rilevamento.
- `03_Verifiche/V5.3/run_regressioni_v53.py`: **14 suite dalla V4.0 alla V5.3 superate**, comprese le 2.400 combinazioni di supervisione software della V4.0; in `REGRESSIONI_V5.3.json` sono registrati esiti e output.
- `03_Verifiche/V5.3/NATIVE_KICAD_NOT_RUN/STATUS_V5.2.json`: il runner V5.2 è stato eseguito ma `kicad-cli` non è presente. **ERC, DRC, refill e parità: NOT_RUN.** I repository apt non erano raggiungibili tramite DNS, perciò non è stata installata una versione nativa del programma.
- `03_Verifiche/V5.3/AUDIT_INDIPENDENTE_V5.3.json`: risultati sintetici del controllo geometrico delle connessioni e delle impronte.

## Mancanze bloccanti della produzione

Rimangono aperte tutte le **nove condizioni** del file `03_Verifiche/V5.0/GATE_RELEASE_V5.0.json`: KiCad ERC/DRC e parità su copia, verifiche CAD TE CONSMA002-SMD-G, DFM scritto VIPPO/riempimento/cappatura, processo stencil U101, qualificazione termica ADL5535, impedenza controllata con stack-up reale 50 Ω, distinta con MPN e prove di laboratorio, oltre all'autorizzazione esplicita al rilascio.

**Vincoli assoluti:** zero hardware validato, 37% storico stimato, **NO FAB / NO PCBWAY / NO TX**. Non esistono Gerber di fabbricazione approvati, dati RF misurati o una risposta del produttore in questa revisione.

## Prossima azione esterna indispensabile

Su PC con KiCad 10 e librerie estratte dallo ZIP, eseguire:

```bash
python3 03_Verifiche/V5.2/run_kicad_v52.py --output REPORT_NATIVE_V5.3
```

Conservare e allegare `STATUS_V5.2.json`, `ERC_V5.2.json`, `DRC_V5.2.json`, `LOG_ERC.txt` e `LOG_DRC.txt`. Il runner copia i sorgenti in una cartella temporanea e non genera Gerber. **I report effettivi, se prodotti, devono essere analizzati** e gli errori risolti in una copia candidata; anche una verifica KiCad senza errori non approva automaticamente lo stencil, il connettore o la costruzione.

Riferimenti: [KiCad 10 CLI](https://docs.kicad.org/10.0/en/cli/cli.html), [TE CONSMA002-SMD-G](https://www.te.com/en/product-CONSMA002-SMD-G.html), [ADI ADL5535](https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf).
