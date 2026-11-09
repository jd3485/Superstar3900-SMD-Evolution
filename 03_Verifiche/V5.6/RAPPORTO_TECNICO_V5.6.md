# Rapporto tecnico V5.6 — Continuità rame F.Cu senza piani riempiti

**Data:** 8 novembre 2026  
**Progetto:** Superstar 3900 SMD Evolution — modulo RX sperimentale 50 Ω  
**Stato di rilascio:** **BLOCCATO — NON PER FABBRICAZIONE — NON TX**.

## Risultato misurabile

Sulla coppia candidata schema/PCB V5.2, con geometria del rame identica alla variante a sei vie termiche V4.8, il nuovo audit indipendente ha ricostruito graficamente i collegamenti fra pad F.Cu, piste F.Cu e rame dei via passanti sullo strato superiore. Le sette reti diverse dalla massa (`RF_LNA_INPUT`, `RF_LNA_IC_IN`, `RF_BIAS_OUT`, `RF_LNA_OUT`, `+5V_BENCH`, `RF_ATTEN_IN`, `RF_ATTEN_OUT`) hanno **un unico gruppo connesso ciascuna**. Questo è un controllo di contiguità del rame, NON una misura d'impedenza a 50 Ω, né un ERC o DRC KiCad.

La rete **GND_RF ha 64 isole distinte sul rame F.Cu non riempito**: **24 isole con piazzole GND** e **40 isole composte da un via isolato** sul lato superiore. Le **24 piazzole GND** sono in gruppi topologicamente indipendenti senza le zone. Nel gruppo del pad termico U101 sono presenti **sette vie** (sei della variante termica e una preesistente). Questi numeri **non rappresentano automaticamente errori DRC**; indicano che la connessione comune dipende dai riempimenti GND sui vari strati.

La scheda contiene **4 zone GND_RF non riempite** sui layer `F.Cu`, `In1.Cu`, `In2.Cu` e `B.Cu`. Finché il riempimento reale non viene calcolato, non è possibile certificare che le 24 isole con pad e le 40 isole con soli via siano davvero collegate a massa attraverso i piani, né che i passaggi RF abbiano un ritorno adeguato.

## Campione e metodo

- PCB V5.2: `04_KiCad/Modulo_RX_Test_50ohm_V5.2_PARITY_LINK_STUDY_NOT_FOR_FAB/S3900E_RX_TEST_50R_V5_2_LINKED_STUDY_NOT_FOR_FAB.kicad_pcb`.
- Riferimento geometrico: file PCB originale della variante termica V4.8, conservato separatamente.
- Analisi: parser S-expression storico e forme Shapely dell'audit V5.5, raggruppamento con intersezione/distanza entro 0,00001 mm (solo arrotondamenti numerici, non tolleranza DRC).
- Oggetti: **44 piazzole**, **44 piste**, **70 via** e **4 zone senza poligoni riempiti**.
- Reti: **8**; tutte le vie attualmente appartengono alla massa `GND_RF`.
- Confronto di identità delle geometrie e delle reti del rame F.Cu fra V5.2 e V4.8: **PASS statico**. Nessuna correzione fisica introdotta in V5.6.
- Output: `AUDIT_CONTINUITA_FCU_V5.6.json`, `RETI_RAME_FCU_V5.6.csv`, `ISOLE_GND_PAD_FCU_V5.6.csv`.

## Prove eseguite

- **23/23 nuovi test V5.6 superati**, comprese mutazioni per interruzioni artificiali delle tracce, cambio di rete di una pista o di una zona, simulazione di riempimento modificato, copia del rame alterata e controllo dello stato non nativo.
- **17/17 suite di regressione software V4.0–V5.6 superate** (inclusa la prova del supervisore su 2.400 combinazioni).
- Il lanciatore V5.6 ha registrato `NOT_RUN_KICAD_MISSING` e codice 5; `kicad-cli` non è installato. Tentativo `apt-get update`: impossibile risolvere l'host del repository Debian.
- KiCad 10, ERC, DRC, calcolo dei riempimenti e controllo parità **NON ESEGUITI**. Nessuna esecuzione GitHub Actions né approvazione DFM acquisita.

## Limiti e decisione

La geometria Shapely è un'approssimazione delle forme CAD; mancano controllo nativo delle termiche, connessioni interstrato, fori, soldermask, silk, court, fabbricazione, EMC, prestazioni RF e misura termica. Non è lecito dedurre che 64 isole in assenza dei riempimenti costituiscano altrettanti cortocircuiti o errori di progetto: i piani previsti possono connetterle, ma non sono verificati.

**Decisione V5.6:** non modificare PCB o schema sulla sola base di queste 64 isole. Eseguire il workflow `kicad_native_v56.yml` su macchina KiCad 10 e acquisire i report reali con `--refill-zones --schematic-parity`, esaminare `unconnected_items` e connettività di GND_RF. Il controllo della continuità statica NON chiude nessuno dei nove gate di rilascio V5.0. Rimangono necessari CAD TE, accettazione VIPPO/stencil U101, stack-up RF, revisione termica e collaudi fisici.

## Documentazione e riferimenti

- `03_Verifiche/V5.6/PROCEDURA_CONTINUITA_E_KICAD_V5.6.md`
- `03_Verifiche/V5.0/GATE_RELEASE_V5.0.json` — nove gate tutti aperti.
- [Documentazione ufficiale KiCad 10 CLI](https://docs.kicad.org/10.0/en/cli/cli.html) — i comandi `sch erc` e `pcb drc`, inclusi `--refill-zones` e `--schematic-parity`.
- [Analog Devices ADL5535](https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf) — raccomandazioni di collegamento del pad esposto alla massa.

**Progressione globale storica:** 37% documentale stimato; **prototipi collaudati: 0**; fabbricazione PCBWay e trasmissione radio ancora vietate.
