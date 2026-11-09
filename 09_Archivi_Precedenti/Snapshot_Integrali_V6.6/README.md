# Superstar 3900 SMD Evolution — V6.6

**Progressione per revisioni e verifiche incrementali, NO FAB / NO TX.**

V6.6: preselettore 50Ω F501. Due soluzioni candidate: **rete RLC discreta a 3 risonatori** (L601/L603=2µH, L602=22nH, capacità totali serie 17,5pF e shunt 1591pF) con modello 2-porte S11/S21, perdita Q, SRF e feedthrough, **e alternativa SMD** **Mini-Circuits SXBP-27R5+** 24–31MHz. Quest'ultima ha datasheet 50Ω, IL tip.1,3/max2,5dB e rigetto stopband 39–900MHz min20dB (a 25°C); NON è un modulo del progetto già validato.

Modello discreto QL=60, QC=400, SRF e C_FEED 0,05pF **assunti**: perdita RX max 5.59dB, reiezione immagine relativa min 47.96dB, RL min 6.18dB. In 4.000 stress test esplorativi, 46.8% supera 6dB di perdita massima. Valori NON prestazioni certificate. 270/270 RX simulati; 50 test nuovi + regressioni selezionate.

File nuovi: `01_Specifiche/V6.6/`, `03_Verifiche/V6.6/`, `07_Componenti/BOM_PRESELETTORE_V6.6.csv`; vedi `Superstar3900_Rapporto_Tecnico_V6.6.md` e `MANIFEST_SHA256_V6.6.csv`. Vecchi documenti di gestione integrali in `09_Archivi_Precedenti/Snapshot_Integrali_V6.5/`. KiCad/ERC/DRC e ngspice vendor **NOT_RUN**.

---

## README storico V6.5 integrale

# Superstar 3900 SMD Evolution — V6.5

**Metodo:** costruzione modulare per tante revisioni con test e simulazioni incrementali, controllo globale finale e validazione KiCad sul PC quando tutti i moduli saranno definiti.

**V6.5**: mixer passivo ADE-1+ pinout vendor confermato, IF1 10,695 MHz, LO alto 36,310–39,000MHz, piano immagini 47,005–49,695MHz per 270 RX, presa LO obiettivo +7dBm. Modello BPF Butterworth ideale (N3, ordine analogico6) 25–29MHz: reiezione immagine minima ideale ≈53,46dB; **filtro NON sintetizzato come rete fisica**. FFT toni, 12.000 scenari fC/BW, 50 test e 8 suite selezionate PASS.

**Rischi aperti:** prestazioni LO +7dBm ancora da misurare, filtri RX/IF reali, demodulatori, AGC, rumore/linerarità, livello blocker, criticità termica PLL della V6.4; KiCad CLI ed ngspice non presenti. TX rimane OFF; NO FAB / NO TX.

File nuovi in `01_Specifiche/V6.5/`, `02_Piano_Frequenze/V6.5/`, `03_Verifiche/V6.5/`, `08_Firmware_Prototipi/V6.5/`, `07_Componenti/BOM_MIXER_FI_V6.5.csv`. Originali V6.4 presenti nel percorso originale o esatti negli snapshot V6.4. SHA: `MANIFEST_SHA256_V6.5.csv`.

---

## README storico V6.4 conservato integralmente

# Superstar 3900 SMD Evolution — V6.4

**Metodo confermato:** una revisione per volta con parti nuove, calcoli, test, simulazioni fattibili e archivi cumulativi; verifica integrale di simulazioni e KiCad quando l'intera progettazione sarà definita.

La V6.4 aggiorna il piano PLL/LO RX LMX2572 a **270 posizioni** (30 ALFA), LO **36,310–39,000 MHz**, prima FI candidata 10,695 MHz, VCO 4,64768–4,992 GHz in integer-N con TCXO 12,8 MHz / R10 e ÷128. Sono stati superati 60 test nuovi e 7 suite selezionate dalla V5.9 alla V6.4. Aggiunti piano CSV, schema funzionale, BOM, pin mapping, ECO alimentazione e modello firmware RX lock/PA. Nessun profilo registri LMX è stato inventato.

**CRITICITÀ**: TPS7A20 candidato 3V3_PLL supera il limite termico nella stima prudenziale a 150 mA/85°C; TCXO, filtro loop, RF matching, spur, KiCad e TICS Pro restano da verificare. **NO FAB / NO TX**, nessun prototipo fisico. Alla V6.3 preesisteva un budget PLL_LO 150 mA su 5V_RF: non sommare due volte.

Nuovi elaborati: `01_Specifiche/V6.4/`, `02_Piano_Frequenze/V6.4/`, `03_Verifiche/V6.4/`, `08_Firmware_Prototipi/V6.4/`, `07_Componenti/BOM_PLL_LO_V6.4.csv`. Originali attivi V6.3 in `09_Archivi_Precedenti/Snapshot_Integrali_V6.3/`. Prossima V6.5: mixer RF e prima FI, filtri e reiezione immagine. `MANIFEST_SHA256_V6.4.csv` per verificare integrità.

---

## Storico esatto della V6.3

# Superstar 3900 SMD Evolution — V6.3, revisione cumulativa

**Metodo:** aggiungere moduli e schemi candidati con test e simulazioni fattibili, conservando sorgenti storici; simulazioni complete e KiCad sul PC dell'utente dopo la progettazione di tutti i blocchi.

**Nuovo V6.3:** alimentazione con 79 riferimenti e 219 contatti funzionali, protezione LM74900-Q1, buck 5 V/3,3 V, LDO 3V3_A/1V8_CODEC e distribuzione audio/RF. 45 test V6.3 PASS, 25.000 combinazioni numeriche carico/rendimento, ramp ideale 13,8 V. La V6.2 viene preservata, le tre copie originali attive sotto `09_Archivi_Precedenti/Snapshot_Integrali_V6.2/`.

**FONDAMENTALE:** pin fisici NON verificati, schematico KiCad nativo NON prodotto, né ERC/DRC né ngspice; fusibile, TVS, MOSFET, correnti reali e finale RF non rilasciati. J907 PA RF e J902 test DNI. **NO FAB/NO TX.**

Nuovi file: `01_Specifiche/V6.3/SCHEMA_A_COMPONENTI_ALIMENTAZIONI_V6.3.md`, `01_Specifiche/V6.3/ALIMENTAZIONI_CANDIDATE_V6.3.json`, `07_Componenti/BOM_ALIMENTAZIONI_V6.3.csv`, `03_Verifiche/V6.3/RAPPORTO_TECNICO_V6.3.md`. Prossima V6.4: sintetizzatore PLL/LO e clock.

---

## Storico precedente (V6.2)

# Superstar 3900 SMD Evolution V6.2 — Progetto cumulativo

**Criterio attuale:** costruire progressivamente la radio completa, con controlli/simulazioni realmente disponibili per ogni revisione; verifica finale dell'intero sistema e KiCad dopo completamento architettura. NON FAB / NO TX.

**Novità V6.2:** schema tabellare a 61 componenti, 190 pin-rete del modulo interblocchi HW PA/TX e supervisione 3V3 + 13,8V; 31 test V6.2 e Monte Carlo 50.000 campioni. ECO meccanica SPDT PA, riserve MCU PB11/PB4 usate per watchdog/TX arm, reinstradamento AMP_SD/relè obbligatorio. J801 DNI aperto, FAULT_LOOP_OK da progettare, nessun finale RF connesso. Native KiCad ERC/DRC/analog SPICE NOT_RUN. Il progetto non è fabbricabile.

Aprire `01_Specifiche/V6.2/SCHEMA_A_COMPONENTI_INTERBLOCCHI_V6.2.md`, `03_Verifiche/V6.2/RAPPORTO_TECNICO_V6.2.md`, `03_Verifiche/V6.2/test_interblocchi_v62.py` e `00_Gestione_Progetto/REGISTRO_DECISIONI.md`. **Prossima V6.3: ingresso 13,8V e rail 5V/3,3V.** Storico V6.1 sotto `09_Archivi_Precedenti/Snapshot_Integrali_V6.1/`.

---

## Storico e note precedenti

# Superstar 3900 SMD Evolution — V6.1

**Fase:** progettazione della radio COMPLETA un modulo alla volta, con verifiche e simulazioni disponibili a ogni revisione, poi revisione e validazione globale su KiCad dell'utente.

V6.1: pannello e STM32G474RET6 mappati con 64 pin reali, due MCP23017, 28 ingressi e 4 LED, CH9/PA/PTT/encoder diretti. Circuito candidato JSON/CSV e BOM sotto `01_Specifiche/V6.1`, `07_Componenti/BOM_MCU_PANNELLO_V6.1.csv`; modello firmware sotto `08_Firmware_Prototipi/V6.1`; test e simulazioni in `03_Verifiche/V6.1`. TX OFF, NO FAB.

---

# Superstar 3900 SMD Evolution — V6.0

**FASE: progettazione progressiva della radio completa — simulazioni e KiCad DOPO.**

V6.0 aggiunge il modulo AUDIO/PA a livello di componenti: BOM, netlist di pin, tre IC candidati, cinque ingressi RX, microfono, amplificatore BTL e relay DPDT speaker. Tutti i dettagli sotto `01_Specifiche/V6.0/` e `03_Verifiche/V6.0/`. Non esiste PCB audio fabbricabile; TX sempre disabilitata.

# Superstar 3900 SMD Evolution — V5.9 cumulativa — 9 novembre 2026

**Nuova fase secondo le indicazioni del committente:** costruire la RADIO COMPLETA per revisioni incrementali. Le verifiche sistematiche KiCad e simulazioni sono previste *dopo* il completamento della progettazione; restano solo i test software di coerenza e le correzioni necessarie durante il lavoro. Questo NON significa ignorare errori già noti.

**Nuovo progetto V5.9:** architettura funzionale integrata a **26 blocchi / 54 collegamenti logici**, contratto JSON tipizzato, mappa SVG e selettore audio RX 5:1 candidato che evita il conflitto ADC del codec. Modello software di routing audio MIC/RX/PA con RF TX sempre OFF; prove unit test incluse. Nuove fonti ufficiali TI/ST archiviate come URL, non come CAD certificato.

**File iniziali:** `01_Specifiche/V5.9/ARCHITETTURA_RADIO_COMPLETA_V5.9.md`, `01_Specifiche/V5.9/SCHEMA_FUNZIONALE_AUDIO_PA_V5.9.md`, `00_Gestione_Progetto/PIANO_MODULI_COMPLETAMENTO_V5.9.md`. `01_Specifiche/V5.9/CONTRATTO_MODULI_V5.9.json` è una specifica logica, **NON** una netlist o schema KiCad fabbricabile.

**Stato di progetto:** 37% storico documentale stimato, 0 hardware validato. KiCad ERC/DRC nativi ancora NOT_RUN; 9 gate V5.0 aperti; NO FAB / NO PCBWAY / NO TX. Il PCB RX V5.2 e tutti i file precedenti non sono modificati. Tutta la cronologia rimane conservata.

---
## README storico V5.8 e precedenti

# Superstar 3900 SMD Evolution — V5.8 cumulativa — 9 novembre 2026

**STATO: NON FAB / NO PCBWay / NO TX.** Zero hardware testato. Nove gate V5.0 aperti, KiCad ERC/DRC/refill/parità nativi `NOT_RUN`. Avanzamento storico 37% (documentale/stimato, NON hardware).

**Novità V5.8:** audit statico e riproducibile della distanza centro-pista RF / centro-via GND. Su 6 reti RF, 13 segmenti F.Cu e 70 via GND, il peggiore tratto campionato è `RF_ATTEN_IN` con **9,5811 mm**, seguito da `RF_ATTEN_OUT` con **6,9385 mm**. I campioni lungo piste rettilinee sono spaziati ≤0,20 mm, bound di errore sul massimo geometrico ≤0,10 mm. **NON** è la lunghezza del ritorno di corrente, non è un criterio di accettazione RF e NON prova una discontinuità; i piani GND rimangono UNFILLED.

**Test nuovi V5.8:** 30/30; regressioni V4.0–V5.8: 19/19. Runner nativo locale `NOT_RUN_KICAD_MISSING`, exit 5. I PCB, schemi, librerie, firmware e manuali non sono stati modificati. CSV con 6 reti e mappa SVG tecnica sorgente inclusi.

Leggere `03_Verifiche/V5.8/RAPPORTO_TECNICO_V5.8.md`, `03_Verifiche/V5.8/PROCEDURA_V5.8.md`, il registro decisioni e `RIPRENDI_IN_UNA_NUOVA_CHAT.md`.

---
## Revisioni precedenti

# Superstar 3900 SMD Evolution — V5.7 cumulativa — 8 novembre 2026

**STATO: NO FAB / NO PCBWay / NO TX**, nessun hardware testato, ERC/DRC KiCad **NOT_RUN**, 9 gate V5.0 OPEN, avanzamento storico documentale 37% stimato.

**Novità V5.7:** audit indipendente e prudenziale delle sagome di GND_RF sui quattro strati non riempiti. Nel modello geometrico superiore, 70/70 vie GND possono intersecare ciascuno dei quattro contorni di zona, distanza minima rame-via/contorno 2,05 mm, su F.Cu una regione ideale da 6.323,1039 mm² (96,08% della zona); gli altri tre strati risultano ciascuno un contorno ideale geometrico completo. Le connessioni termiche e le regole di riempimento reali **NON sono modellate**. Il PCB conserva ancora 64 gruppi GND pre-refill, non 64 errori DRC dimostrati.

**Test eseguiti:** 30/30 V5.7, 18/18 suite software V4.0–V5.7, inclusi errori introdotti intenzionalmente. Runner locale `NOT_RUN_KICAD_MISSING`; workflow GitHub Actions V5.7 predisposto ma **non pubblicato né eseguito**. Nessun PCB, schema o libreria modificato.

Leggere `03_Verifiche/V5.7/RAPPORTO_TECNICO_V5.7.md`, `03_Verifiche/V5.7/PROCEDURA_V5.7.md`, `RIPRENDI_IN_UNA_NUOVA_CHAT.md` e `00_Gestione_Progetto/REGISTRO_DECISIONI.md`.

---
## Versioni precedenti

# Superstar 3900 SMD Evolution — V5.6 cumulativa — 8 novembre 2026

**STATO:** 37% documentale stimato, 0 prototipi fisici validati, ERC/DRC KiCad nativi **NOT_RUN**, NO FAB / NO PCBWay / NO TX.

**Novità V5.6:** audit STATICO della topologia del rame F.Cu sul PCB candidato V5.2. Le 7 reti di segnale/+5 V sono continue. La massa GND_RF è costituita da 64 gruppi di rame sul lato superiore prima del riempimento: 24 gruppi con pad e 40 con solo via; sono presenti 4 zone GND UNFILLED su F.Cu/In1.Cu/In2.Cu/B.Cu. Questi gruppi NON sono dichiarati come difetti DRC: occorre riempimento zone KiCad e controllo nativo dei ritorni RF. Geometria F.Cu V5.2 identica alla variante termica V4.8.

Nuovo verificatore `03_Verifiche/V5.6/audit_continuita_fcu_v56.py`, 23/23 test V5.6, 17/17 suite di regressione V4.0–V5.6. Workflow GitHub Actions manuale V5.6 e runner fail-closed predisposti, NON eseguiti su KiCad reale. I PCB, schemi, librerie, il firmware e il manuale illustrato restano intatti. Nove gate V5.0 ancora OPEN.

**File principali:** `03_Verifiche/V5.6/RAPPORTO_TECNICO_V5.6.md`, `03_Verifiche/V5.6/PROCEDURA_CONTINUITA_E_KICAD_V5.6.md`, `03_Verifiche/V5.6/AUDIT_CONTINUITA_FCU_V5.6.json`. Per riprendere leggere `RIPRENDI_IN_UNA_NUOVA_CHAT.md` e `00_Gestione_Progetto/REGISTRO_DECISIONI.md`.

---
## Versione V5.5 e documentazione storica

# Superstar 3900 SMD Evolution — V5.5 cumulativa (8 novembre 2026)

**STATO ATTUALE:** 37% documentale stimato; nessun hardware validato; ERC/DRC KiCad nativi **NOT_RUN**; NO FAB, NO PCBWay, NO TX.

**Novità V5.5:** screening di clearance sul rame `F.Cu` tramite Shapely, 44 pad, 44 piste, 70 vie, 5.267 confronti fra reti, distanza minima 0,45 mm (cinque coppie di pad); nessun risultato sotto soglia analitica 0,30 mm. Le **4 zone GND sono UNFILLED**, perciò NON è un DRC. Report `03_Verifiche/V5.5/AUDIT_RAME_FCU_V5.5.json`.

Postvalidazione dei JSON KiCad 10 con controllo esplicito di violazioni ERC, unconnected_items e schematic_parity: `03_Verifiche/V5.5/validate_native_reports_v55.py`. Runner `run_native_v55.py` e workflow GitHub Actions manuale `.github/workflows/kicad_native_v55.yml` predisposti, **NON eseguiti su KiCad reale**. Il test locale ha registrato il blocco previsto.

**Test:** 22/22 V5.5 e 16/16 suite di regressione V4.0–V5.5; tutti test statici/software. I file di schema, PCB, librerie, firmware e manuale illustrato sono invariati. I nove gate V5.0 rimangono tutti aperti.

**Avviare dal PC con KiCad 10:** leggere `03_Verifiche/V5.5/PROCEDURA_E_LIMITI_V5.5.md`. Per una nuova chat leggere `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, il rapporto V5.5 e `00_Gestione_Progetto/REGISTRO_DECISIONI.md`.

---
## README della V5.4 e delle versioni precedenti

# Superstar 3900 SMD Evolution — V5.4 cumulativa (8 novembre 2026)

**Stato:** 37% storico stimato, nessun hardware collaudato, ERC/DRC nativi ancora **NOT_RUN**. NO FAB / NO PCBWay / NO TX.

**Novità:** procedura di verifica KiCad 10 `03_Verifiche/V5.4/run_native_v54.py` con conservazione report ERC/DRC e parità; workflow facoltativo `.github/workflows/kicad_native_v54.yml` per esecuzione manuale su GitHub Actions, **mai pubblicato né eseguito**. Eseguire dal proprio PC `python3 -B 03_Verifiche/V5.4/run_native_v54.py --output REPORT_NATIVE_V5.4`, oppure seguire `03_Verifiche/V5.4/PROCEDURA_NATIVA_E_CI_V5.4.md`.

**Test svolti realmente:** 8 test V5.4 con CLI simulate e 15 suite di regressione software tutti riusciti. Il lancio locale reale segnala KiCad assente e `NOT_RUN`; il passaggio a KiCad 10 è ancora da fare. Tutte le nove condizioni di produzione sono OPEN. Schema/PCB/librerie e manuale d'uso invariati.

**Per riprendere:** aprire `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, `03_Verifiche/V5.4/RAPPORTO_TECNICO_V5.4.md` e `00_Gestione_Progetto/REGISTRO_DECISIONI.md`. Conservare l'intero ZIP cumulativo.

---
## README V5.3 e precedenti

# Superstar 3900 SMD Evolution — V5.3 cumulativa (8 novembre 2026)

**STATO REALE: 37% stima storica, zero moduli hardware validati, NO FAB / NO PCBWAY / NO TX.**

**Novità V5.3:** il parser indipendente `03_Verifiche/V5.3/audit_indipendente_v53.py` legge geometricamente simboli, pin, fili e label del candidato V5.2 e confronta le reti ai pad, percorsi UUID, valori, footprint e geometrie di 15 librerie/istanze. Risultati: **15 componenti, 31 pin, 31 fili, 8 reti, zero incongruenze rilevate staticamente**. I **18 nuovi test** e le **14 suite V4.0–V5.3** sono riusciti. Nessun sorgente KiCad modificato.

**KiCad CLI non installato:** ERC/DRC/refill/parità **NON ESEGUITI**. Eseguire `python3 03_Verifiche/V5.2/run_kicad_v52.py --output REPORT_NATIVE_V5.3` su un PC con KiCad 10. Nove gate di rilascio restano aperti; TE SMA e termica ADL5535 non approvati; manuale illustrato V4.0 conservato.

**Leggere per iniziare:** `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, `03_Verifiche/V5.3/RAPPORTO_TECNICO_V5.3.md`, `03_Verifiche/V5.3/ISTRUZIONI_RIPRESA_E_KICAD_V5.3.md`, `00_Gestione_Progetto/REGISTRO_DECISIONI.md`.

---
## Storico V5.2 e precedenti

# Superstar 3900 SMD Evolution — V5.2 cumulativa (8 novembre 2026)

**STATO:** 37% storico stimato; zero hardware validato; **NO FAB / NO TX**.

**Novità:** creato candidato schema/PCB separato con 15 riferimenti `instances (project...)` aggiornati nello schema e 15 collegamenti `(path...)` footprint→simbolo nel PCB. Non sono state modificate geometrie o reti: rimuovendo soltanto queste annotazioni il sorgente V4.8 è recuperato byte per byte. **Non è ancora una validazione KiCad nativa.**

**Test:** 12 nuovi test automatici V5.2; `kicad-cli` non installato: ERC, DRC, parità e refill **NON ESEGUITI**. Consultare `03_Verifiche/V5.2/RAPPORTO_TECNICO_V5.2.md`, `audit_associazioni_v52.py`, `run_kicad_v52.py` e `ISTRUZIONI_PROVA_KICAD_V5.2.md`.

Tutti i precedenti file, manuali e librerie preservati. Gate 9/9 OPEN. La revisione di fabbricazione resta vietata.

---
## README V5.1 e precedenti

# Superstar 3900 SMD Evolution — V5.1 cumulativa (8 novembre 2026)

**Stato:** progetto sperimentale. Avanzamento storico stimato 37%, **0 hardware validato**, **NO FAB / NO PCBWay / NO TX**.

## Risultati V5.1

- Inventario verificabile da PCB candidato RX V4.8: **15 componenti / 31 pin elettrici / 8 reti**, con BOM CSV preliminare e CSV pin-rete, MPN non assegnati e quattro SMA da confermare con CAD TE.
- Attenuatore Pi 150/37,4/150 Ω: attenuazione resistiva ideale **6,012876 dB a 50 Ω**, non una misura.
- `03_Verifiche/V5.1/genera_bom_net_v51.py` e `test_v51.py`: **13/13 test statici riusciti**, anche test di mutazione; suite precedenti V4.0–V5.0 rieseguite.
- `05_Produzione_PCBWay/V5.1/RICHIESTA_DFM_DA_INVIARE_V5.1.md`: richiesta di fattibilità aggiornata, **non inviata**. Condizioni VIPPO/stencil in attesa di conferma scritta.
- KiCad 10 **NON disponibile** dopo tentativo di aggiornamento pacchetti interrotto per timeout: **ERC/DRC/refill/parità NON ESEGUITI**.
- PCB, schema, librerie, manuale illustrato, revisioni cumulative **non modificati**. Gate R-01...R-09 ancora aperti.
- Rapporti: `03_Verifiche/V5.1/RAPPORTO_TECNICO_V5.1.md`, `03_Verifiche/V5.1/ISTRUZIONI_VALIDAZIONE_ESTERNA_V5.1.md`.

**Prossima verifica decisiva:** usare `03_Verifiche/V5.0/run_kicad_native_v50.py` su un PC con KiCad 10 e fornire i report; ottenere CAD TE del SMA esatto e una risposta DFM scritta su via-in-pad/stencil. Non avviare ordini.

---
## README storico V5.0 e precedenti

# Superstar 3900 SMD Evolution — V5.0 cumulativa (8 novembre 2026)

**Stato: 37% storico stimato, zero hardware validato; NO FAB / NO PCBWAY / NO TX.** La V5.0 è una revisione di prevalidazione: modello dello stencil U101, procedura KiCad 10 fail-closed, gate di rilascio, piano di collaudo RX. **Non** modifica PCB o schema e **non** registra approvazioni esterne.

## Novità V5.0

- `03_Verifiche/V5.0/RAPPORTO_TECNICO_V5.0.md`: risultati misurati dai sorgenti e limiti.
- `03_Verifiche/V5.0/STUDIO_STENCIL_V5.0.json` + `CONFRONTO_STENCIL_U101_V5.0.svg`: apertura attuale 81% vs due finestre alternative 29,69% con distanza nominale foro/pasta ≥0,125 mm. La seconda è **solo studio**, non progetto stencil approvato.
- `03_Verifiche/V5.0/run_kicad_native_v50.py` + `ISTRUZIONI_KICAD_V5.0.md`: lanciatore ERC/DRC/parità/refill su copia; KiCad non disponibile in questa sessione, quindi **NON ESEGUITI**.
- `03_Verifiche/V5.0/GATE_RELEASE_V5.0.json`: **9 gate OPEN**, tutte le autorizzazioni bloccate.
- `03_Verifiche/V5.0/PIANO_COLLAUDO_RX_V5.0.md`: prove proposte J101–J104, tutte `NOT_RUN`.
- `05_Produzione_PCBWay/DECISIONE_VIPPO_STENCIL_V5.0.md`: richiesta di fattibilità non inviata.
- `03_Verifiche/V5.0/test_v50.py`: 20/20 test statici superati, incluse prove d'errore; regressioni V4.0–V4.9 tutte riuscite.
- `09_Archivi_Precedenti/Snapshot_Integrali_V4.9/`: copie integrali byte-identiche dei 5 documenti attivi aggiornati.

**In una nuova chat:** allegare solo questo ZIP V5.0 e leggere `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, poi il rapporto V5.0 e il registro delle decisioni. Tutti i manuali, sorgenti e revisioni sono conservati.

---
## README storico V4.9 e precedenti

# Superstar 3900 SMD Evolution — V4.9 cumulativa (2026-11-08)

**Stato progettuale:** 37% storico stimato, zero hardware testato; **NO FAB / NO PCBWAY / NO TX**. Questa revisione aggiunge un audit statico del rischio via-in-pad/stencil e una richiesta di fattibilità, non nuovi PCB né collaudi RF.

## Novità V4.9

- `03_Verifiche/V4.9/RAPPORTO_TECNICO_V4.9.md`: misure da sorgenti KiCad, criticità e gate di accettazione.
- `03_Verifiche/V4.9/AUDIT_VIA_STENCIL_V4.9.json`: calcolo replicabile su V4.8, 6/6 fori della via-in-pad interamente nella F.Paste del pad esposto U101. Pad 1,80×3,48 mm; pasta teorica 1,62×3,132 mm, copertura 81%.
- `03_Verifiche/V4.9/audit_via_stencil_v49.py` + `test_v49.py`: 14 test statici compresi casi volutamente alterati. **Non sono ERC/DRC nativi**.
- `03_Verifiche/V4.9/U101_APERTURA_PASTE_V4.9.svg`: disegno geometrico illustrativo, non CAM.
- `05_Produzione_PCBWay/RICHIESTA_FATTIBILITA_V4.9.md` e `GATE_PRODUZIONE_V4.9.csv`: specifica da sottoporre eventualmente a fabbricante e montatore, **non un ordine**.
- `03_Verifiche/V4.9/PROCEDURA_KICAD_V4.9.md`: procedura nativa da svolgere su una macchina KiCad 10.

**Bloccanti**: VIPPO e stencil U101 non approvati; DXF/STEP TE ancora da confrontare; KiCad ERC/DRC/parity non eseguiti; stack-up RF, termica e collaudi mancanti. Nessuna versione del PCB è abilitata a fabbricazione.

**Come riprendere in un'altra chat:** allega solo il ZIP V4.9, leggi `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, poi questo README, il registro decisioni e il rapporto tecnico V4.9. Tutti i sorgenti e il manuale illustrato V4.0 sono conservati.

---
## README storico V4.8 e precedenti

# Superstar 3900 SMD Evolution — V4.8 (cumulativa)

**Stato**: progetto sperimentale. Nessun hardware collaudato, 37% avanzamento progettuale stimato. **NO FAB / NO PCBWAY / NO TX.**

## Novità V4.8

- `03_Verifiche/V4.8/RAPPORTO_TECNICO_V4.8.md`: relazione e limiti delle verifiche.
- `04_KiCad/Modulo_RX_Test_50ohm_V4.8_TERMICA_6VIE_STUDIO_NON_FAB/`: progetto candidato *separato*, con sei via-in-pad GND 0,55/0,25 mm sotto U101. Non fabbricabile senza via fill/cap, stencil e qualifica RF/termica.
- `03_Verifiche/V4.8/test_variante_termica_v48.py`: controllo reversibilità e geometria.
- `03_Verifiche/V4.8/RUN_KICAD_CANDIDATO_V48.sh`: ERC/DRC su copia, senza Gerber; non eseguito per KiCad assente.
- `MANIFEST_SHA256_V4.8.csv`: hash dei file correnti escluso sé stesso.
- `09_Archivi_Precedenti/Snapshot_Integrali_V4.7/`: copie byte-identiche dei documenti attivi aggiornati.

**Ripresa:** leggere `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, registro decisioni e rapporto V4.8. Manuale illustrato V4.0 ancora presente nella cartella `06_Manuali`.

---
## Testo storico (V4.7 e precedenti)

# Superstar 3900 SMD Evolution — V4.7 cumulativa (8 novembre 2026)

**Stato:** ricerca/progettazione 37% stimato, **zero hardware collaudato**, **NO FAB / NO PCBWay / NO TX**.

## Novità verificata V4.7

- Recuperato il **disegno ufficiale TE rev. D** del `CONSMA002-SMD-G`. Nel candidato SMA V4.3/V4.5 coincidono staticamente soltanto Ø2,05 mm del disco centrale e 7,76 mm dell'inviluppo verticale GND. Non è una validazione completa del footprint. DXF/STEP disponibili sul sito TE ma **non acquisiti**.
- I pad GND custom degli SMA dispongono di F.Mask/F.Paste senza riduzione esplicita, da approvare con l'assemblatore. Per U101 ADL5535 la formula nominale dell'apertura paste con ratio -0,100 dà circa 81% dell'area pad: **non** una misura termica o verifica stencil.
- **28/28 test V4.7 superati**; regressioni V4.0–V4.6 rieseguite. KiCad CLI assente: **ERC/DRC, refill e parità NON ESEGUITI**. Schemi, PCB e librerie candidati rimangono inalterati.
- `03_Verifiche/V4.7/RAPPORTO_TECNICO_V4.7.md`, `AUDIT_SMA_TE_V4.7.json`, `GEOMETRIA_SMA_STUDIO_V4.7.png` e `CHECKLIST_ACCETTAZIONE_V4.7.csv`.
- Tutte le versioni precedenti e il manuale illustrato V4.0 sono inclusi; documenti sostituiti salvati byte-per-byte in `00_Gestione_Progetto/V4.7_SNAPSHOT_V4.6/`.

**Per proseguire:** aprire `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, poi il rapporto V4.7; acquisire CAD TE esatto e validare in KiCad 10 prima di un prototipo.

---

## README precedente V4.6 conservato

# Superstar 3900 SMD Evolution — V4.6 cumulativa (8 novembre 2026)

**Stato ufficiale:** ricerca/progettazione in corso, **37% stimato**, **0 moduli hardware validati**. **NO FAB / NO PCBWay / NO TX**.

## Novità V4.6

- Audit dimensionale dei collegamenti di massa dell'ADL5535 U101: pad esposto 1,80×3,48 mm, via GND più vicino separato da 0,50 mm di rame; assenza di via-in-pad. Il layout è invariato e la termica rimane NON APPROVATA.
- Analisi dei quattro SMA J101–J104 nel candidato portabile: CAD TE DXF/STEP elencati dal produttore ma non acquisiti. Footprint e ingombro restano NON APPROVATI.
- Nuovo lanciatore KiCad che verifica `--refill-zones` e `--schematic-parity`, usa una copia temporanea e non salva il PCB: **KiCad non disponibile qui, native checks NON ESEGUITI**. Procedura KiCad 10 pronta per verifica esterna.
- 24/24 nuovi test statici e di blocco fail-closed superati, più suite V4.0–V4.5 rieseguite. Il manuale d'uso illustrato V4.0 e tutte le revisioni storiche restano nell'archivio.
- Corretta la guida interna di ripresa che era rimasta a V4.4; gli originali V4.5 sono salvati in `00_Gestione_Progetto/V4.6_SNAPSHOT_V4.5/`.

## Per riprendere rapidamente

1. Leggi `RIPRENDI_IN_UNA_NUOVA_CHAT.md` e `00_Gestione_Progetto/REGISTRO_DECISIONI.md`.
2. Leggi `03_Verifiche/V4.6/RAPPORTO_TECNICO_V4.6.md`, `AUDIT_TERMICA_SMA_V4.6.json` e il disegno `DETTAGLIO_PAD_TERMICO_U101_V4.6.png`.
3. Per i test: `python3 03_Verifiche/V4.6/test_rischi_v46.py`; per KiCad **reale**, su macchina con KiCad 10, `bash 03_Verifiche/V4.6/RUN_KICAD_RX_V46.sh ./risultati_kicad`.
4. Non produrre o ordinare nulla fino ad approvazione del CAD TE, termica ADL5535, impedenza e controlli nativi KiCad, seguiti da collaudi RF.

---

## README storico V4.5 (conservato per orientamento)

# Superstar 3900 SMD Evolution — V4.5 cumulativa (2026-11-08)

**Stato: progettazione/documentazione 37% stimato, zero prototipi convalidati; NO FAB / NO PCBWAY / NO TX.**

## Novità V4.5

Il modulo RX sperimentale dispone ora di **librerie KiCad locali**, generate dai footprint incorporati nella copia V4.3 del PCB e dai simboli dello schema candidato V4.4.

- **3 librerie footprint `.pretty` con 9 componenti tipo**, una libreria simboli con 9 simboli e tabelle riferite a `${KIPRJMOD}`. Layout 15 componenti riprodotto; non modificato il rame del candidato né l'originale V3.8.
- **26 test statici V4.5 superati**; eseguite di nuovo suite V4.0–V4.4. Non eseguiti ERC, DRC/refill o verifica di parità con KiCad, perché `kicad-cli` non disponibile.
- **Rischi aperti**: confronto CAD ufficiale TE CONSMA002-SMD-G, dissipazione ADL5535, approvazione stack-up 50 Ω, validazione PCB KiCad e misure RF.
- **Manuale illustrato V4.0** incluso: `06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf`. È ancora una bozza, non un manuale di un apparato collaudato.

## File di accesso

1. `RIPRENDI_IN_UNA_NUOVA_CHAT.md` e `00_Gestione_Progetto/REGISTRO_DECISIONI.md`.
2. `03_Verifiche/V4.5/RAPPORTO_TECNICO_V4.5.md`, `INVENTARIO_LIBRERIE_V4.5.json`, `TEST_V4.5.txt`.
3. `04_KiCad/Modulo_RX_Test_50ohm_V4.5_LIBS_PORTABILI_NOT_FOR_FAB/README.md`.
4. `03_Verifiche/V4.5/crea_librerie_v45.py` (rigenerazione), `test_librerie_v45.py` (suite) e `RUN_KICAD_RX_V45.sh` (richiede KiCad installato).
5. `00_Gestione_Progetto/CHANGELOG_V4.5.md` e tutti gli snapshot e manifest precedenti.

L'archivio V4.5 è **cumulativo**. I documenti attivi V4.4 aggiornati hanno copie byte-identiche denominate SNAPSHOT; tutte le revisioni e il manuale restano nell'archivio. Il progetto V4.5 non è utilizzabile per fabbricazione senza una revisione ingegneristica e verifiche hardware.
