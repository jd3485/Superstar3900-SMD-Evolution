# Superstar 3900 SMD Evolution — V6.3, revisione cumulativa

**Metodo:** aggiungere moduli e schemi candidati con test e simulazioni fattibili, conservando sorgenti storici; simulazioni complete e KiCad sul PC dell'utente dopo la progettazione di tutti i blocchi.

**Nuovo V6.3:** alimentazione con 79 riferimenti e 219 contatti funzionali, protezione LM74900-Q1, buck 5 V/3,3 V, LDO 3V3_A/1V8_CODEC e distribuzione audio/RF. 45 test V6.3 PASS, 25.000 combinazioni numeriche carico/rendimento, ramp ideale 13,8 V. La V6.2 viene preservata, le tre copie originali attive sotto `09_Archivi_Precedenti/Snapshot_Integrali_V6.2/`.

**FONDAMENTALE:** pin fisici NON verificati, schematico KiCad nativo NON prodotto, né ERC/DRC né ngspice; fusibile, TVS, MOSFET, correnti reali e finale RF non rilasciati. J907 PA RF e J902 test DNI. **NO FAB/NO TX.**

Nuovi file: `01_Specifiche/V6.3/SCHEMA_A_COMPONENTI_ALIMENTAZIONI_V6.3.md`, `01_Specifiche/V6.3/ALIMENTAZIONI_CANDIDATE_V6.3.json`, `07_Componenti/BOM_ALIMENTAZIONI_V6.3.csv`, `03_Verifiche/V6.3/RAPPORTO_TECNICO_V6.3.md`. Prossima V6.4: sintetizzatore PLL/LO e clock.

---

## Indicazioni di recupero, poi storico precedente (V6.2)

# Superstar 3900 SMD Evolution V6.2 — Stato per nuova chat

**Criterio attuale:** costruire progressivamente la radio completa, con controlli/simulazioni realmente disponibili per ogni revisione; verifica finale dell'intero sistema e KiCad dopo completamento architettura. NON FAB / NO TX.

**Novità V6.2:** schema tabellare a 61 componenti, 190 pin-rete del modulo interblocchi HW PA/TX e supervisione 3V3 + 13,8V; 31 test V6.2 e Monte Carlo 50.000 campioni. ECO meccanica SPDT PA, riserve MCU PB11/PB4 usate per watchdog/TX arm, reinstradamento AMP_SD/relè obbligatorio. J801 DNI aperto, FAULT_LOOP_OK da progettare, nessun finale RF connesso. Native KiCad ERC/DRC/analog SPICE NOT_RUN. Il progetto non è fabbricabile.

Aprire `01_Specifiche/V6.2/SCHEMA_A_COMPONENTI_INTERBLOCCHI_V6.2.md`, `03_Verifiche/V6.2/RAPPORTO_TECNICO_V6.2.md`, `03_Verifiche/V6.2/test_interblocchi_v62.py` e `00_Gestione_Progetto/REGISTRO_DECISIONI.md`. **Prossima V6.3: ingresso 13,8V e rail 5V/3,3V.** Storico V6.1 sotto `09_Archivi_Precedenti/Snapshot_Integrali_V6.1/`.

---

## Storico e note precedenti

# RIPRESA PROGETTO — Superstar 3900 SMD Evolution V6.1

Caricare l'archivio cumulativo `Superstar3900_SMD_Evolution_V6.1.zip`. Il progetto viene sviluppato **in molte revisioni progressive**: progettazione concreta, verifica e simulazioni possibili in ogni chat, controllo globale e KiCad nativo DOPO il completamento della radio.

**Ultima V6.1:** 156 componenti di scheda MCU/pannello, 476 pin-rete, STM32G474RET6 LQFP64, due MCP23017 0x20/0x21, 28 pulsanti/contatti, 4 spie; encoder PC10/11, CH9 PC13, PA PC0, PTT PA0. Rispettare codec V2.1 (WCLK PA9/43) e MUX audio V6.0. Sono disponibili modelli `panel_controller_v61.py` e `integration_audio_v61.py`, test 55+5 e simulazioni RC/tolleranze/rimbalzi.

**Piano prossime revisioni:** V6.2 interblocco HW TX/PA, power-good e AMP_SD, poi PLL, FI, TX, ATU, interconnessioni, firmware e meccanica. Nel finale analisi globale, KiCad, SPICE/RF e hardware. Non pretendere KiCad nativo in ambiente chat se non disponibile. Tutti i canali sono RX nello sviluppo, 40 vecchi marcatori TX SI in D NON sono permessi RF reali. TX fisicamente disabilitata finché manca gate hardware; 0 prototipi convalidati, NO FAB/PCBWAY.

---

# RIPRESA PROGETTO — Superstar 3900 SMD Evolution V6.0

Usa l'archivio cumulativo `Superstar3900_SMD_Evolution_V6.0.zip`; prima fase PROGETTAZIONE RADIO COMPLETA per tante revisioni, poi simulazioni e verifica KiCad su PC utente.

**V6.0:** circuito AUDIO/PA candidato U601 TMUX1308 PW16, U602 TLV9062 SOIC8, U604 TPA3111D1 PWP28, connettoristica J601/J602/J603/J604/J605/J606, 5 demod RX, MIC elettrete e doppio speaker BTL tramite DPDT.

Fonte per netlist: `01_Specifiche/V6.0/CIRCUITO_COMPONENTI_AUDIO_PA_V6.0.json`; `07_Componenti/BOM_AUDIO_PA_V6.0.csv`; nuova suite `03_Verifiche/V6.0/test_audio_pa_v60.py`. Firmware concettuale `08_Firmware_Prototipi/V6.0/audio_controller_v60.py`.

Prossimo sviluppo V6.1: MCU/pannello vintage e vera matrice pin, successivamente V6.2 interblocco HW PA/TX e AMP_SD. Continuiamo a costruire i moduli della radio **prima** delle simulazioni sistematiche e verifiche KiCad. TX inibita; 9 gate NO FAB aperti; hardware 0.

---

# RIPRESA — Superstar 3900 SMD Evolution V5.9 — 9 novembre 2026

Il committente desidera **sviluppo progettuale incrementale completo di tutta la radio in molte revisioni**, come prima, ma **non** una successione di revisioni dedicate soltanto a KiCad e audit del modulo RX. PRIMA finire schemi, moduli, firmware, PCB candidati e documentazione di ogni funzione; POI revisione globale, simulazioni RF/IF/audio/power, controlli KiCad col programma installato sul PC dell'utente, prototipi e misure. Durante la progettazione eseguire soltanto test software e controlli di coerenza necessari; problemi evidenti vanno corretti quando scoperti.

**V5.9 nuova:** contratti logici 26 moduli e 54 interconnessioni, piano modulare V6.0–V6.9, mappa architettura, studio audio/PA e modello fail-closed `audio_route_v59.py`. Il microfono e l'audio demodulato devono arrivare a ADC_L e ADC_R separati del codec. È previsto mux analogico RX 5:1 ancora da progettare. Nessuna scheda audio nuova fabbricabile e nessuna TX abilitata. Conservati tutti i 1025 file V5.8; copie documenti in `09_Archivi_Precedenti/Snapshot_Integrali_V5.8`.

**Prossima revisione V6.0:** progettazione dettagliata del modulo audio/PA con schema componenti candidati, mute, speaker, mux e connettori; non ripartire da un ennesimo solo audit KiCad. Data/completezza per singolo modulo e revisioni future in `00_Gestione_Progetto/PIANO_MODULI_COMPLETAMENTO_V5.9.md`.

**Vincoli sempre:** 270 RX A–F con ALFA, CH9 27,065 AM, AM/FM/USB/LSB/CW RX, PA audio senza RF, VOX/DW/RB/Echo/CTCSS-DCS/DSP/ATU/SWR-PEP; 37% stima storica, zero prototipi, 9 gate OPEN, KiCad nativo NOT_RUN, NO FAB/NO TX. Le simulazioni e KiCad non sono ancora state fatte, non promettere risultati certi.

---
## RIPRESA storica V5.8 e precedenti

# RIPRENDI — Superstar 3900 SMD Evolution V5.8 — 9 novembre 2026

Usare l'archivio cumulativo `Superstar3900_SMD_Evolution_V5.8.zip`. Lo ZIP comprende l'intero storico, CAD KiCad originale, schemi candidati, librerie, manuale illustrato V4.0 e tutte le istanze sperimentali. Nessun hardware validato, **NO FAB / NO TX**.

**Requisiti radio finale invariati:** stile Superstar 3900, bande A–F, 270 posizioni RX incluse ALFA, AM/FM/USB/LSB/CW in ricezione, CH9 AM emergenza, funzione PA senza emissione RF, VOX/Dual Watch/Roger Beep/Echo/CTCSS-DCS/DSP, strumenti SWR/PEP e tuner antenna. La TX rimane vietata fino alla verifica normativa e ad interblocchi indipendenti.

**V5.8:** audit geometrico di 13 piste su 6 reti RF e 70 via GND; max distanza centro-pista/centro-via 9,5811 mm su RF_ATTEN_IN. Il ritorno di corrente non è stato modellato e i quattro piani GND sono UNFILLED; non interpretare distanza via come problema RF certificato. 30/30 test V5.8 e 19/19 suite storiche. Modifiche al rame: nessuna. Lo studio ha prodotto `03_Verifiche/V5.8/AUDIT_RITORNO_RF_V5.8.json`, CSV e SVG. Eseguito lanciatore su macchina priva di KiCad 10: `NOT_RUN_KICAD_MISSING`, exit 5. I nove gate sono aperti e la percentuale documentale resta 37%.

**Passo necessario:** su macchina effettivamente dotata di KiCad 10 eseguire `python3 -B 03_Verifiche/V5.8/run_audit_e_kicad_v58.py --output REPORT_NATIVE_V5.8`, conservare tutti i JSON ERC/DRC/refill/parità. Confrontare GND dei SMA, attenuatore, pad U101 e vie termiche; acquisire CAD ufficiale TE e DFM scritto per VIPPO/stencil. Nessuna produzione prima di chiudere i gate.

Prompt ripresa: «Continua il Superstar 3900 SMD Evolution dal pacchetto cumulativo V5.8; richiedi soltanto report KiCad REALI, non toccare gli originali e mantieni NO FAB/NO TX.»

---
## Storico precedente

# RIPRENDI — Superstar 3900 SMD Evolution V5.7 — 8 novembre 2026

Ripartire dallo ZIP cumulativo `Superstar3900_SMD_Evolution_V5.7.zip`. Gli originali, il manuale d'uso illustrato, i sorgenti KiCad, i rapporti e tutti gli snapshot di documenti modificati sono conservati.

**Radio finale nelle specifiche:** stile Superstar 3900; 6 bande A–F, 270 posizioni RX (40+5 ALFA/banda), CH9 AM emergenza, AM/FM/USB/LSB/CW RX; PA con RF TX disabilitata; ALFA fisico, VOX, Dual Watch, Roger Beep, Echo, CTCSS/DCS, DSP, lettura SWR/PEP e tuner antenna. TX vietata fino a conformità normativa, interblocchi hardware e prove indipendenti.

**Stato V5.7:** quattro piani GND non riempiti; la V5.6 misurava 64 isole fisiche su F.Cu senza refill. La V5.7 ha stimato, non riempito, un contorno ideale continuo su ciascuno dei 4 strati: 70/70 vie GND entro le zone; 24 pad GND F.Cu sovrapposti alla zona ideale; margine rame via/bordo zona min 2,05 mm; 96,08% di superficie ideale F.Cu. Sono solo verifiche geometriche permissive, **non KiCad, non prova delle termiche, non elettricità verificata**. 30/30 nuovi test e 18/18 suite regressive. KiCad 10 mancante, ERC/DRC/parità/refill REALI `NOT_RUN`. 9 gate OPEN; TE SMA, VIPPO/stencil U101, stackup RF, termica e hardware da approvare. Prototipi testati zero; 37% stima documentale; NO FAB/NO TX.

**Priorità V5.8:** far eseguire `.github/workflows/kicad_native_v57.yml` manualmente su un repository autorizzato (non ancora pubblicato) oppure `run_piani_e_kicad_v57.py` su un PC con KiCad 10; recuperare e interpretare report ERC/DRC con `--refill-zones --schematic-parity`, controllando tutti i 64 gruppi pre-refill, gli spoke termici e il ritorno GND. Acquisire dati CAD TE e risposta DFM su U101; non ordinare PCB.

Prompt di ripresa: «Continua Superstar 3900 SMD Evolution dal pacchetto cumulativo V5.7, prima acquisisci eventuali report nativi KiCad, non alterare originali e mantieni NO FAB/NO TX».

---
## Storico precedente

# RIPRENDI — Superstar 3900 SMD Evolution V5.6 — 8 novembre 2026

Utilizzare il solo `Superstar3900_SMD_Evolution_V5.6.zip` per riprendere tutto il progetto; contiene manuale d'uso illustrato, sorgenti storici, programmi di verifica, report e snapshot di documenti aggiornati.

**Radio definitiva solo in specifica:** estetica Superstar 3900, 6 bande A–F, 270 posizioni RX (40+5 ALFA per banda), CH9, AM/FM/USB/LSB/CW, PA con TX RF disabilitato, VOX, Dual Watch, Echo, Roger Beep, CTCSS/DCS, DSP, ATU, SWR/PEP. TX fisicamente interdetta fino a verifiche normative/hardware e interblocchi.

**Ultima revisione V5.6:** audit topologico statico del rame F.Cu: 7/7 reti non GND in un unico gruppo ciascuna, massa GND in 64 gruppi prima delle 4 zone da riempire (24 con pad, 40 via-only). Test 23/23, regressioni 17/17, nessun errore statico segnale. Rame PCB V5.2 geometricamente identico a V4.8, originali intatti. KiCad native ERC/DRC/zone refill NON ESEGUITI, CI non lanciata, nessuna approvazione TE SMA/termica ADL5535/PCBWay. Nove gate V5.0 tutti OPEN. 37% storico stimato, 0 hardware validato. NO FAB/NO TX.

**Priorità V5.7:** far girare realmente KiCad 10 CLI/CI e acquisire ERC, DRC --refill-zones, controllo `unconnected_items` e parità schema/PCB. Verificare che le 64 isole F.Cu si connettano correttamente ai piani senza bridge mancanti; non attribuire loro 64 errori in assenza di zone fill. Acquisire CAD TE e approvazione produttore/assemblatore per le vie termiche U101, determinare stack-up e ritorno RF.

**Prompt per nuova chat:** «Riprendi Superstar 3900 SMD Evolution V5.6 dall'archivio ZIP; consulta README, RIPRENDI, registro decisioni e audit V5.6; verifica prima eventuali nuovi report KiCad nativi; non sovrascrivere sorgenti storici, non autorizzare fabbricazione né TX.»

---
## Note storiche V5.5 e precedenti

# RIPRENDI — Superstar 3900 SMD Evolution V5.5 — 8 novembre 2026

Allegare il solo archivio cumulativo `Superstar3900_SMD_Evolution_V5.5.zip` in una nuova chat. Leggere `README.md`, questo file, `03_Verifiche/V5.5/RAPPORTO_TECNICO_V5.5.md`, `00_Gestione_Progetto/REGISTRO_DECISIONI.md`, i gate V5.0 e la procedura KiCad V5.5.

**Radio finale in specifica (non costruita):** estetica Superstar 3900; sei bande A–F per 270 RX, ALFA e CH9, AM/FM/USB/LSB/CW, PA RX disabilitando RF TX, VOX, Dual Watch, Echo, Roger Beep, CTCSS/DCS, DSP, ATU, SWR/PEP. TX interdetta fino a verifiche fisiche, compliance e interblocchi indipendenti.

**V5.5:** screening geometrico indipendente F.Cu passato con soglia di analisi 0,30 mm; distanza minima 0,45 mm; cinque coppie di pad alla minima. Esclusi rame di zone non riempite e tutti i controlli KiCad nativi. 22 nuovi test e 16 regressioni software riusciti. Post-validatore JSON ERC/DRC e CI manuale preparati, NON eseguiti sul servizio GitHub né sul programma KiCad. GATE V5.0=9 OPEN, prototipi fisici=0, 37% stima storica, NO FAB/NO PCBWAY/NO TX.

**Priorità V5.6:** far realmente eseguire KiCad 10 sul progetto candidato V5.2, ottenere report `ERC`, `DRC_PARITY`, `STATUS` e `SUMMARY`, leggere i difetti ed effettuare modifiche su una nuova copia; ottenere CAD TE e conferma DFM VIPPO/stencil, verificare stack-up/termica. Non fabbricare né trasmettere.

**Messaggio riutilizzabile:** «Riprendi Superstar 3900 SMD Evolution V5.5 dall'archivio cumulativo. Leggi README/RIPRENDI/rapporto/registro, verifica eventuali report nativi KiCad acquisiti e conserva manuale, revisioni e gate. Nessun rilascio FAB o TX.»

---
## Stato della V5.4 e precedenti

# RIPRENDI — Superstar 3900 SMD Evolution V5.4 — 8 novembre 2026

**In una nuova chat allega soltanto** `Superstar3900_SMD_Evolution_V5.4.zip` e chiedi di leggere questo file, `README.md`, `03_Verifiche/V5.4/RAPPORTO_TECNICO_V5.4.md`, `00_Gestione_Progetto/REGISTRO_DECISIONI.md` e i gate V5.0.

**Radio finale prevista** (non hardware funzionante): estetica vintage Superstar 3900, 6 bande A–F/270 RX, ALFA e CH9, AM/FM/USB/LSB/CW RX, PA, VOX, Dual Watch, Echo, Roger Beep, CTCSS/DCS, DSP, ATU, SWR/PEP. TX disabilitata fino a conformità e collaudo.

**Stato V5.4:** revisione di automazione, non riprogettazione del PCB. Workflow `.github/workflows/kicad_native_v54.yml` e runner `03_Verifiche/V5.4/run_native_v54.py` predisposti per produrre veri report KiCad 10 **solo quando eseguiti** su un host compatibile. In questa sessione KiCad è assente; ERC/DRC/refill/parità = NOT_RUN. I test (8 simulati + 15 suite software) sono riusciti, non costituiscono ERC/DRC. Il workflow non è stato caricato su GitHub né eseguito. Nessuna approvazione esterna acquisita. 37% storico stimato, zero prototipi validati, NO FAB/NO PCBWAY/NO TX.

**Priorità:** ottenere rapporti nativi ERC/DRC con parità e refill; correggere gli eventuali errori su copia; completare TE DXF/STEP e approvazione DFM VIPPO/stencil, stack-up, termica. Conservare le vecchie versioni e manuali.

**Messaggio riutilizzabile:** «Riprendi Superstar 3900 SMD Evolution dal pacchetto V5.4. Leggi README, RIPRENDI, rapporto V5.4 e registro decisioni. Mantieni le revisioni cumulative; ottieni/esamina ERC/DRC KiCad veri e non autorizzare fabbricazione o TX.»

---
## Ripresa V5.3 e precedenti

# RIPRENDI — Superstar 3900 SMD Evolution V5.3 — 8 novembre 2026

**In una nuova chat allega unicamente** `Superstar3900_SMD_Evolution_V5.3.zip`. Leggi `README.md`, questo file, il rapporto V5.3, il registro decisioni e i nove gate V5.0.

**Radio finale (solo requisiti):** Superstar 3900 estetica vintage, 6 bande A–F e 270 RX, ALFA/CH9, AM/FM/USB/LSB/CW RX, PA, VOX, Dual Watch, Echo, Roger Beep, CTCSS/DCS, DSP, ATU e misure SWR/PEP. TX disabilitata.

**Stato verificato V5.3:** 37% stima storica, 0 hardware validato. Nessun file KiCad storico o candidato modificato. Audit indipendente della coppia V5.2: 15 componenti, 31 pin, 31 fili etichettati, 8 reti, nessuna divergenza statica; 18 nuovi test e 14 suite di regressione superati. **Non sono test nativi KiCad**. `kicad-cli` assente, ERC/DRC/refill/parità `NOT_RUN`. Non ci sono risposte DFM o collaudi reali. **NO FAB / NO PCBWAY / NO TX**.

**Priorità V5.4:** eseguire la procedura nativa `03_Verifiche/V5.2/run_kicad_v52.py` su PC KiCad 10, allegare ERC/DRC/parità e correggere errori reali su copia; acquisire modello CAD TE esatto e approvazione scritta VIPPO/stencil/termica e stack-up RF. Manuale illustrato `06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf`. Preservare tutto e produrre ZIP cumulativo con manifest SHA-256.

**Prompt da incollare:** «Riprendi Superstar3900 SMD Evolution dal ZIP V5.3 allegato. Leggi README, RIPRENDI, rapporto V5.3, registro decisioni e gate V5.0. Mantieni tutte le versioni; prosegui con KiCad nativo e qualifica TE/ADL5535 senza dichiarare hardware validato o autorizzare fabbricazione/TX.»

---
## Storico V5.2 e precedenti

# RIPRENDI — Superstar 3900 SMD Evolution V5.2 — 8 novembre 2026

**Per una nuova chat allegare soltanto** `Superstar3900_SMD_Evolution_V5.2.zip`. Leggere prima `README.md`, poi questo file, `03_Verifiche/V5.2/RAPPORTO_TECNICO_V5.2.md` e `00_Gestione_Progetto/REGISTRO_DECISIONI.md`.

**Radio completa richiesta:** estetica Superstar 3900; RX 270 posizioni su sei bande, ALFA/CH9, AM/FM/USB/LSB/CW RX, PA, VOX, Dual Watch, Echo, Roger Beep, CTCSS/DCS, DSP, ATU, strumenti SWR/PEP. Sono requisiti di progetto, NON funzioni hardware collaudate. TX disabilitata.

**Novità V5.2:** candidato separato di allineamento nativo schema/PCB, con 15 relazioni UUID e 15 riferimenti di progetto corretti rispetto alla copia V4.8. Rame, via, pad, zone e reti invariati; 12 test statici superati. **ERC/DRC KiCad non eseguiti**, CLI assente. V5.1 conserva BOM 15 componenti / 31 pin / 8 reti. Materiale di prova: `03_Verifiche/V5.2/`; candidato: `04_KiCad/Modulo_RX_Test_50ohm_V5.2_PARITY_LINK_STUDY_NOT_FOR_FAB/`.

**Bloccanti:** 9 gate di fabbricazione aperti; manca verifica nativa KiCad 10, CAD STEP/DXF TE, risposta scritta VIPPO/stencil, termica, stack-up 50 Ω, MPN e collaudi. **37% stima storica, 0 moduli funzionanti, NO FAB / NO TX.** Manuale in `06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf`.

**Prossimo passo:** eseguire `python3 03_Verifiche/V5.2/run_kicad_v52.py --output REPORT_NATIVE_V5.2` su computer KiCad 10; allegare i report nativi in nuova chat per correggere gli errori. Non autorizzare produzione sulla base dei soli test statici.

---
## Ripresa V5.1 e precedenti

# RIPRENDI — Superstar 3900 SMD Evolution V5.1 — 8 novembre 2026

**Allegare questo solo file ZIP `Superstar3900_SMD_Evolution_V5.1.zip` in una nuova chat.** Leggere nell'ordine `README.md`, questo file, `03_Verifiche/V5.1/RAPPORTO_TECNICO_V5.1.md`, `00_Gestione_Progetto/REGISTRO_DECISIONI.md` e `03_Verifiche/V5.0/GATE_RELEASE_V5.0.json`.

**Requisiti radio finale invariati:** look Superstar 3900, 270 posizioni RX su 6 bande, CH9, ALFA, AM/FM/USB/LSB/CW RX, PA, VOX, Dual Watch, Echo, Roger Beep, CTCSS/DCS, DSP, ATU, misure SWR/PEP; non sono funzioni collaudate. TX vietata sino a revisione autorizzata e conformità normativa.

**Cosa è nuovo V5.1:** dalla variante PCB V4.8 (non da hardware) sono stati ricavati una BOM preliminare **15 componenti** e un pin-net **31 connessioni / 8 reti**, con **13/13 test** statici; script e CSV in `03_Verifiche/V5.1/`. Bozza DFM per PCBWay non inviata. KiCad nativo non eseguito; gate R-01...R-09 tutti OPEN. PCB e schema invariati, manuale illustrato in `06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf`. **Stato 37% storico stimato, 0 hardware validato, NO FAB, NO TX.**

**Proseguimento:** eseguire la procedura `03_Verifiche/V5.1/ISTRUZIONI_VALIDAZIONE_ESTERNA_V5.1.md` su macchina KiCad 10 e conservare ERC/DRC/parità; acquisire CAD TE ufficiale e approvazione del processo VIPPO/stencil U101. In ogni futura revisione preservare integrali le versioni precedenti con manifest SHA-256 e backup dei documenti aggiornati.

Messaggio per nuova chat: «Riprendi Superstar 3900 SMD Evolution dal ZIP V5.1 allegato, leggi README, RIPRENDI e rapporto V5.1, conserva tutte le decisioni e le revisioni; parti dall'esecuzione KiCad nativa, CAD TE SMA e risposta DFM VIPPO senza autorizzare produzione o TX.»

---
## Storico V5.0 e precedenti

# RIPRENDI — Superstar 3900 SMD Evolution V5.0 — 8 novembre 2026

**Allega solo l'archivio `Superstar3900_SMD_Evolution_V5.0.zip`.** Leggi questo file, `README.md`, `03_Verifiche/V5.0/RAPPORTO_TECNICO_V5.0.md`, `00_Gestione_Progetto/REGISTRO_DECISIONI.md` e `03_Verifiche/V5.0/GATE_RELEASE_V5.0.json`.

**Radio finale richiesta:** estetica Superstar 3900, 6 bande A–F / 270 RX, ALFA, CH9, AM/FM/USB/LSB/CW RX, PA, VOX, Dual Watch, Echo, Roger Beep, CTCSS/DCS, DSP, ATU e misure SWR/PEP. Sono **specifiche**, non funzioni di un apparato già costruito. Trasmissione disabilitata fino a conformità, collaudo e approvazione.

**Stato V5.0:** 37% storico stimato, 0 moduli hardware validati. PCB originale V3.8, candidato SMA V4.3, librerie portabili V4.5 e variante U101 con sei via-in-pad V4.8 conservati separati e TUTTI NOT_FOR_FAB. V5.0 confronta due geometrie di stencil: 81% pasta esistente con riempimento/cappatura da validare, contro 29,69% di due finestre evitando i fori, studio non raccomandato per produzione senza verifica montaggio/termica. **Nessun file KiCad del PCB o dello schema è stato modificato.**

**Non eseguiti:** KiCad ERC/DRC/refill/parità nativi (CLI assente), qualifica CAD TE STEP/DXF completa, approvazione PCBWay e assemblatore VIPPO, stack-up 50 Ω, termica, collaudi RF. Sono nove i gate aperti nel `GATE_RELEASE_V5.0.json`. NO FAB / NO PCBWAY / NO TX.

**Manuale illustrato:** `06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf`. Per il prossimo passo eseguire sul proprio PC KiCad 10 il lanciatore `03_Verifiche/V5.0/run_kicad_native_v50.py`, allegando i report in una nuova chat, e ottenere conferme scritte di produttore/assemblatore. Nel frattempo preservare ogni revisione in uno ZIP cumulativo con manifest SHA-256, senza dichiarare test fisici inesistenti.

**Messaggio pronto per nuova chat:** «Riprendi Superstar 3900 SMD Evolution dal ZIP V5.0 allegato; leggi README, RIPRENDI, rapporto V5.0, registro decisioni e gate di rilascio. Mantieni manuali e sorgenti storici; prosegui da KiCad 10 nativo, CAD TE e risposta DFM VIPPO/stencil; non autorizzare produzione o TX e prepara solo revisioni cumulative verificabili».

---
## Handoff storico V4.9 e precedenti

# RIPRENDI — Superstar 3900 SMD Evolution V4.9 — 8 novembre 2026

**Allega questo archivio intero:** `Superstar3900_SMD_Evolution_V4.9.zip`, NON un singolo file KiCad. Conserva le revisioni cumulative e tutti i manuali. Inizia da `README.md`, `00_Gestione_Progetto/REGISTRO_DECISIONI.md` e `03_Verifiche/V4.9/RAPPORTO_TECNICO_V4.9.md`.

**Radio finale desiderata (requisiti, non apparecchio reale):** estetica Superstar 3900, 6 bande A–F / 270 RX, ALFA, CH9, AM/FM/USB/LSB/CW RX, PA, VOX, Dual Watch, Echo, Roger Beep, CTCSS/DCS, DSP, ATU, misure SWR/PEP. TX disabilitata, subordinata a verifica normativa e hardware.

**Stato V4.9:** 37% storico stimato; 0 prototipi validati; PCB V3.8 originale invariato, candidati SMA V4.3, KiCad portabile V4.5 e sei vie U101 V4.8 separati, **tutti NON FAB**. Questa revisione non modifica PCB/schema/footprint. È stato rilevato che tutti e 6 i fori termici Ø0,25 mm della V4.8 ricadono completamente nell'apertura F.Paste teorica 1,62×3,132 mm (pad 1,80×3,48 mm). Occorre decisione scritta su VIPPO/riempimento/cappatura, stencil e ispezione, oltre a stack-up RF. PCBWay ha capacità pubbliche generali ma non ha approvato questa scheda; nessun contatto/invio è stato fatto.

**Non eseguiti:** ERC/DRC/refill/parità nativi KiCad, confronti TE DXF/STEP, analisi termiche validate, misure RF e collaudi reali. NO PCBWAY, NO FAB, NO TX.

**Nuovi materiali:** `03_Verifiche/V4.9/` per audit, test, report e procedura KiCad; `05_Produzione_PCBWay/RICHIESTA_FATTIBILITA_V4.9.md` per chiedere in futuro valutazione di producibilità, non un ordine. Manuale illustrato in `06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf`.

**Prossima milestone V5.0:** acquisire CAD TE del componente esatto, eseguire ERC/DRC KiCad nativi su copia e ottenere risposte scritte da fabbricante e assemblatore prima di modificare lo stencil o ordinare la scheda. Conservare ogni revisione con backup byte-identici dei documenti attivi, manifest SHA-256 e test; non incrementare la percentuale senza risultati hardware.

**Prompt per nuova chat:** «Riprendi Superstar3900 SMD Evolution V4.9 dallo ZIP allegato. Leggi README, RIPRENDI, registro decisioni e rapporto tecnico V4.9; conserva manuali e ogni revisione. Prosegui i gate DFM VIPPO/stencil U101, CAD TE e ERC/DRC KiCad su copia senza approvare produzione né TX. Crea archivio cumulativo con hash verificati.»

---
## Ripresa storica V4.8 (per rintracciabilità)

# RIPRENDI — Superstar 3900 SMD Evolution V4.8 — 8 novembre 2026

Allega `Superstar3900_SMD_Evolution_V4.8.zip` a una nuova chat. Leggi nell'ordine: `README.md`, `00_Gestione_Progetto/REGISTRO_DECISIONI.md`, `03_Verifiche/V4.8/RAPPORTO_TECNICO_V4.8.md`, `03_Verifiche/V4.8/AUDIT_VARIANTE_TERMICA_V4.8.json`.

**Radio finale**: estetica Superstar 3900; 6 bande RX 270 posizioni, ALFA, CH9, AM/FM/USB/LSB/CW RX, PA, VOX, Dual Watch, Echo, Roger Beep, CTCSS/DCS, DSP, ATU, strumenti PEP/SWR. Requisiti, non hardware funzionante. TX legalmente limitato e NON ABILITATO.

**Stato V4.8**: conservati tutti i sorgenti V3.8–V4.7; manuale illustrato in `06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf`. 37% stimato, 0 moduli hardware collaudati. NO PCBWay/NO TX. La V4.8 aggiunge solo un PCB *candidato* con sei via-in-pad GND sotto U101, NON approvato; il datasheet ADL5535 mostra una matrice di vie, ma il processo di riempimento/cappatura e lo stencil non sono definiti. Lo schema e il pad di pasta non sono modificati. KiCad non installato: ERC/DRC/parity/refill non eseguiti. DXF/STEP ufficiali TE non acquisiti: SMA non approvati.

**Prossimo passo**: sottoporre via-in-pad/stencil a PCB maker e assemblatore, ottenere DXF/STEP TE del componente esatto, eseguire ERC/DRC nativi su una copia, acquisire stack-up 50 Ω, validare termica e S-parametri di un prototipo. NON ordinare PCB prima dei gate.

**Per verificare la variante**: `python3 03_Verifiche/V4.8/test_variante_termica_v48.py` (10 test). Per verifiche native su macchina KiCad 10: `bash 03_Verifiche/V4.8/RUN_KICAD_CANDIDATO_V48.sh` (non deve dichiarare esito se assente).

**Prompt per nuova chat**: «Riprendi Superstar 3900 SMD Evolution dall'archivio V4.8. Leggi README, RIPRENDI, registro decisioni e rapporto V4.8; conserva ogni sorgente e il manuale. Verifica termica via-in-pad e stencil, footprint SMA TE e DRC/ERC KiCad 10. Mantieni NO FAB/NO TX fino a validazione reale. Produci nuovo archivio cumulativo con manifest e snapshot».

---
## Storico delle istruzioni V4.7 e precedenti

# RIPRENDI — Superstar 3900 SMD Evolution V4.7 — 8 novembre 2026

**Per una nuova chat, allegare soltanto:** `Superstar3900_SMD_Evolution_V4.7.zip`. E' cumulativo: comprende tutte le revisioni, manuali, progetti e manifest.

**Radio finale (requisiti, non prodotto esistente):** aspetto Superstar 3900, 6 bande A–F con 270 posizioni RX, ALFA fisico, CH9 prioritario, AM/FM/USB/LSB/CW RX, PA, VOX, Dual Watch, Echo, Roger Beep, CTCSS/DCS, DSP, ATU e misure SWR/PEP. Le architetture PLL/MCU/codec sono candidate. TX soggetto a normativa e interblocchi.

**Stato reale:** 37% progettuale stimato, 0 moduli hardware validati. PCB V3.8 originale conservato; V4.3 candidato SMA e V4.5 librerie portabili con schema RX staticamente allineato, non approvati. NO FAB / NO PCBWAY / NO TX.

**Novità V4.7:** disegno TE C-CONSMA002-SMD-X-X rev D letto: pad centrale Ø2,05 mm e inviluppo GND 7,76 mm coincidono nello studio, ma DXF/STEP non acquisiti; geometria 3D, maschera e pasta non validati. U101 pad termico 1,80×3,48 mm con paste ratio -0,100 (circa 81% area nominale) non qualificato. 28 nuovi test statici + regressioni V4.0–V4.6 superati. KiCad 10 non disponibile: ERC/DRC/parità e refill NOT_RUN.

**Leggere per iniziare:** `README.md`, `00_Gestione_Progetto/REGISTRO_DECISIONI.md`, `03_Verifiche/V4.7/RAPPORTO_TECNICO_V4.7.md`, `03_Verifiche/V4.7/AUDIT_SMA_TE_V4.7.json`, `03_Verifiche/V4.7/CHECKLIST_ACCETTAZIONE_V4.7.csv`; manuale in `06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf`.

**Prossimi passi:** ottenere/importare DXF/STEP TE del part-number esatto; validare F.Cu/F.Paste/F.Mask e courtyard; completare analisi termica ADL5535 e stack-up RF; eseguire test nativi KiCad 10 su copie con la procedura già disponibile `03_Verifiche/V4.6/RUN_KICAD_RX_V46.sh`. Non dichiarare conformità in assenza dei rapporti. Confezionare sempre nuove revisioni cumulative con hash e snapshot.

**Prompt nuova chat:** «Riprendi Superstar3900 SMD Evolution dall'archivio V4.7 allegato. Leggi README, RIPRENDI, registro decisioni e rapporto V4.7. Conserva le revisioni storiche e il manuale; continua il confronto TE DXF/STEP, KiCad nativo e termica ADL5535 senza ordinare PCB o abilitare TX. Produci un archivio cumulativo verificato.»

---

## Handoff storico V4.6

# RIPRENDI — Superstar 3900 SMD Evolution V4.6 — 8 novembre 2026

**Allega in una nuova chat:** `Superstar3900_SMD_Evolution_V4.6.zip`, ZIP cumulativo con manuali, schemi, script, revisioni e manifest SHA-256.

## Radio finale desiderata (REQUISITI, NON ancora un apparato funzionante)

Estetica tradizionale Superstar 3900, sei bande A–F, 270 posizioni RX (40+5 ALFA ciascuna), AM/FM/USB/LSB/CW ricezione, PA senza RF, ALFA fisico, CH9 27,065 MHz AM prioritario, VOX, Dual Watch, Echo, Roger Beep, CTCSS/DCS, DSP, strumenti SWR/PEP, ATU. LMX2572, STM32G474RE e TLV320AIC3204 sono componenti/architetture candidate. Trasmissione solo nel rispetto di norme, collaudo e interblocchi hardware+firmware.

## Stato reale V4.6

- **37% stima progettuale, zero hardware validato, NO FAB / NO PCBWAY / NO TX.**
- PCB RX 110×62 mm sperimentale: V3.8 originale immutato; V4.3 candidato SMA distinto; V4.5 progetto portabile con tre librerie di footprint (9 modelli) e libreria di simboli (9 modelli). Schema/PCB staticamente coerenti con 15 componenti, 31 pin elettrici e 8 reti, **non verificati nativamente**.
- **Novità V4.6:** audit della geometria U101 ADL5535: paddle 1,80×3,48 mm, via più vicino Ø0,70/foro Ø0,30 mm, 0,50 mm distanza rame-rame; nessun centro di via sul paddle. Quattro zone GND ancora non riempite con KiCad. Niente prova di temperatura o dissipazione.
- Quattro SMA TE CONSMA002-SMD-G: footprint di studio V4.3 NON approvato; CAD ufficiale DXF/STEP disponibile da link TE, download non completato nella sessione. Non procedere con correzioni inventate.
- Nuova procedura `03_Verifiche/V4.6/RUN_KICAD_RX_V46.sh`: usa KiCad 10 se realmente disponibile, verifica opzioni CLI, esegue su copia e **non** genera Gerber. In questa sessione KiCad non installato, ERC/DRC/refill/parità **NON ESEGUITI**.
- 24 test statici V4.6 riusciti; regressioni V4.0–V4.5 riuscite, escluse verifiche hardware. Il manuale illustrato V4.0 rimane bozza.

## File iniziali da leggere

1. `README.md` e `00_Gestione_Progetto/REGISTRO_DECISIONI.md`.
2. `03_Verifiche/V4.6/RAPPORTO_TECNICO_V4.6.md` e `AUDIT_TERMICA_SMA_V4.6.json`.
3. `04_KiCad/Modulo_RX_Test_50ohm_V4.5_LIBS_PORTABILI_NOT_FOR_FAB/README.md`.
4. `03_Verifiche/V4.6/TEST_V4.6.txt`, `PROVA_NO_KICAD/STATUS.txt`.
5. `06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf`.

## Priorità V4.7

Ottenere disegno TE e STEP/DXF *del part number esatto*, fare il confronto completo con pad/paste/mask/courtyard/PCB e scegliere il footprint definitivo. Eseguire KiCad 10 nativo ERC+DRC con refill e parity; risolvere tutti gli errori e documentare warning residui. Progettare e giustificare il percorso termico/pasta saldante dell'ADL5535; fissare stack-up RF da produttore e misure VNA prima di qualsiasi prototipo RX. Mai abilitare TX in questa fase.

**Prompt per nuova chat:** “Riprendi Superstar 3900 SMD Evolution dall'archivio cumulativo V4.6 allegato. Leggi README, RIPRENDI, registro decisioni e rapporto V4.6. Conserva storici e manuale, prosegui da CAD TE, verifica termica ADL5535 e KiCad 10 nativo; non dichiarare collaudi inesistenti e non autorizzare fabbricazione o TX. Produci revisioni cumulative e manifest verificati.”
