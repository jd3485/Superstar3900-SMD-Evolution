# Superstar 3900 SMD Evolution — RAPPORTO TECNICO V7.13

**10 novembre 2026 — Progresso reale sui file KiCad RX, nessuna fabbricazione o TX.**

## 1. Sorgenti e modifica CAD

Da V7.12 su `main` (HEAD di partenza `29212dd41050a658d637a412773a77d309402074`) è stata creata una nuova copia nativa KiCad RX nello spazio `04_KiCad/Modulo_RX_Test_50ohm_V7.13_GRID_REPAIR_NOT_FOR_FAB/`: `S3900E_RX_STANDALONE_V7_13_GRID_NOT_FOR_FAB.kicad_sch` e il corrispondente `.kicad_pcb`. Il PCB è una copia **bit-for-bit per rame, footprint, reti e vias** del coupon V7.12 (è cambiato solo il nome del progetto). Nessun PCB dell'intera radio è stato ancora progettato.

Nello schema RX sono state allineate alla griglia **1,27 mm / 50 mil** tutte le **154 coppie di coordinate di posizionamento** di simboli, proprietà, collegamenti, etichette e nota. Lo spostamento massimo di ciascun asse è 0,635 mm. **Nessuna** definizione di simbolo, pin, UUID, reference, valore o `lib_symbols` è stata modificata. Sono stati conservati i 15 componenti RX e le sei vie il cui foro era stato corretto nella V7.11. Il nuovo root `04_KiCad/Assemblaggio_RX_Power_V7.13_GRID_REPAIR_NOT_FOR_FAB/S3900E_RX_POWER_INTEGRATION_V7_13_GRID_NOT_FOR_FAB.kicad_sch` riferisce correttamente i fogli AUX V1.5, MCU V7.12 e RX V7.13: non sono state inventate connessioni elettriche.

Il primo tentativo di root V7.13 conteneva un `Sheetfile` che cercava un MCU V7.13 non esistente: la netlist risultava di 58 anziché 99 reti. Il difetto è stato individuato dal **gate di confronto di tutte le membership dei pin**, corretto puntando al vero MCU V7.12 e bloccato contro ricorrenze con un test di esistenza dei tre file. Un successivo tentativo di CI ha evidenziato anche una regex di test troppo escapata; corretta senza cambiare le regole ERC o il circuito. **Non si sono nascosti gli errori di test**.

Sono state aggiunte tabelle locali `sym-lib-table` e `fp-lib-table` che puntano alle librerie storiche RX. La disponibilità di questi file **non** risolve automaticamente l'idoneità dei simboli o dei footprint: rimangono 15 warning di libreria simboli e 15 di collegamento footprint. Pin/pad SMA e termica ADL5535 non qualificati.

## 2. Verifica elettrica tramite netlist KiCad, NON equivalenza presunta

Il workflow `.github/workflows/v713_rx_grid_native_erc.yml` installa KiCad CLI 9 ed esporta effettivamente due netlist della gerarchia 7-fogli: V7.12 e V7.13. Lo script `03_Verifiche/V7.13/verifica_integrita_netlist_v713.py` confronta il nome di **ogni rete** e l'insieme completo di coppie **(designatore, numero pin)** appartenenti a ogni rete, non soltanto la cardinalità globale.

Risultato nativo confermato da GitHub Actions [run 42869660331](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42869660331): **99 reti prima, 99 dopo, zero differenze di appartenenza pin-rete**. Nessuna nuova interconnessione elettrica. In particolare, le 15 interfacce fra AUX/MCU/RX restano `OPEN/HOLD` e tutta la catena TX resta `DNP/OPEN`. La qualificazione hardware non deriva da una semplice equivalenza di netlist teorica.

## 3. Risultati veri di ERC e DRC KiCad 9

| Verifica nativa | Prima V7.12 | Dopo V7.13 | Interpretazione |
|---|---:|---:|---|
| RX `endpoint_off_grid` | **46** | **0** | Correzione KiCad reale |
| RX `lib_symbol_issues` | 15 | 15 | Ancora aperti |
| RX `footprint_link_issues` | 15 | 15 | Ancora aperti |
| **ERC RX: errori / warning** | **0 / 76** | **0 / 30** | Miglioramento, ERC RX non privo di warning |
| **ERC root: errori / warning** | **43 / 416** | **43 / 370** | 46 warning in meno, 43 errori bloccanti |
| **DRC coupon RX: violazioni** | **85** | **85** | PCB fisico non avanzato in questa revisione |
| DRC coupon RX: `unconnected_items` | 63 | 63 | Nessuna pista o collegamento inventato |
| DRC coupon: `via_dangling` / footprint | 70 / 15 | 70 / 15 | Da trattare elettricamente |
| **Netlist gerarchica** | 99 reti | 99 reti | **Zero differenze di ref+pin** |

I 43 errori ERC di gerarchia sono stati conservati integralmente. Un segnale `PASS` nella CI significa che il miglioramento specifico è stato provato; **non** che i controlli ERC/DRC completi siano superati.

## 4. Test e tracciabilità

Sorgenti della verifica: `03_Verifiche/V7.13/test_rx_grid_v713.py` (12 test di invarianti CAD), `verifica_integrita_netlist_v713.py` (confronto di reti e terminali) e `verifica_erc_drc_nativi_v713.py` (gate numerici sui report veri KiCad). I precedenti test Python dei modelli V7.1–V7.12 restano nel workflow: **176 regressioni storiche**, per un totale previsto e verificato nei run completi di **188 test Python PASS, senza FAIL o SKIP**. Icarus e Yosys non sono stati rieseguiti in V7.13; non sono dichiarati nuovi test RTL.

Rapporti nativi `*.rpt`, due netlist KiCad e comparazioni JSON vengono pubblicati come artifact dal workflow. Nel report macchina `03_Verifiche/V7.13/RISULTATI_VERIFICHE_V7_13.json` sono registrati risultati e blocchi.

## 5. Sicurezza e piano successivo

**NON ESEGUITI:** 15 simboli RX/15 collegamenti footprint qualificati, SMA e ADL5535 impronte vendor certificate, 70 ritorni via GND sulla scheda, 63 collegamenti di rame, 43 errori del root, 15 confini MCU/AUX/RX, alimentazione sicura, pad FPGA Lattice SG48, misura RF, test hardware, KiCad DRC totale PASS, produzione PCB, EMC o trasmissione.

**Prossima V7.14:** riparare cause delle 30 warning ERC RX (senza alterare componenti/pin), verificare contro datasheet le 15 impronte e il percorso corrente RF, poi risolvere le via GND dangling e le 63 connessioni dopo valutazione topologica. Collegare una per una le interfacce MCU/AUX/RX solo dopo verifica di rail e logica. Continuare DSP, firmware, simulazioni, BOM e regression test in parallelo.

**Decisione:** V7.13 integrabile in `main` soltanto come miglioramento CAD nativo e verificato, **NON** come board approvata. **NO FAB / NO TX.**
