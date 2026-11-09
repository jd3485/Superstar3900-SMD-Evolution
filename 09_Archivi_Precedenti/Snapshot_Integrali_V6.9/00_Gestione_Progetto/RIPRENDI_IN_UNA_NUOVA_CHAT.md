# Ripresa gestione V5.8 — 9 novembre 2026

Scaricare solo `Superstar3900_SMD_Evolution_V5.8.zip`, leggere prima `RIPRENDI_IN_UNA_NUOVA_CHAT.md` radice e `03_Verifiche/V5.8/RAPPORTO_TECNICO_V5.8.md`. Manuale RX/uso illustrato V4.0 e tutte le revisioni conservate.

V5.8: 13 piste RF, 6 reti RF, 70 vie GND; distanza max da via su `RF_ATTEN_IN` 9,5811 mm, 5mm soglia esclusivamente diagnostica, non prestazione RF. Quattro zone GND ancora UNFILLED. 30/30 test; regressioni V4.0–V5.8 19/19. `kicad-cli` assente => `NOT_RUN_KICAD_MISSING`; NO FAB, NO PCBWay, NO TX; 9 gate aperti; storico 37% stimato.

---
## Stato precedente

# Gestione ripresa V5.7 — 8 novembre 2026

Usare il solo archivio cumulativo `Superstar3900_SMD_Evolution_V5.7.zip`; leggere prima `RIPRENDI_IN_UNA_NUOVA_CHAT.md` in radice, il rapporto V5.7 e il registro delle decisioni.

V5.7: modello geometrico upper-bound quattro zone GND UNFILLED, 70 via in ogni contorno, regione ideale unica per layer; superficie F.Cu ideale 96,08%, margine via/contorno ≥2,05 mm. Thermal spokes e zone vere **NON CALCOLATI**. 30/30 test V5.7 e 18/18 suite storiche passati. KiCad 10 non disponibile, ERC/DRC nativi NOT_RUN; 9 gate OPEN e nessun PCB approvato o TX consentita. Manuale conservato, zero hardware collaudato.

---
## Stato precedente

# Gestione ripresa — V5.6 — 8 novembre 2026

Archivio corrente `Superstar3900_SMD_Evolution_V5.6.zip`: 100% cumulativo, documentazione e manuale conservati. Leggere il file di ripresa radice e `03_Verifiche/V5.6/RAPPORTO_TECNICO_V5.6.md`.

Nuovo dato: su rame F.Cu senza poligoni delle quattro zone, 7 reti non GND continue e 64 gruppi GND (24 con pad, 40 via-only). Non sono automaticamente errori DRC; richiedere refill/DRC KiCad 10 e verifica parità. 23 test nuovi e 17 suite storiche superati. Nessun KiCad reale, hardware fisico o DFM produttore; 37% documentale stimato; NO FAB/PCBWay/TX.

---
## Stato storico

# Note di gestione V5.5 — 8 novembre 2026

La versione corrente è l'archivio `Superstar3900_SMD_Evolution_V5.5.zip`, contenente cronologia integrale, manuale illustrato, schemi e PCB originali intatti. Leggere la guida di ripresa radice `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, il rapporto `03_Verifiche/V5.5/RAPPORTO_TECNICO_V5.5.md` e i gate V5.0.

Nuove verifiche: analisi statica distanze top-copper 0,45mm minimo con zone GND ancora UNFILLED; 22/22 nuovi test, 16/16 regressioni software. KiCad/ERC/DRC reali non eseguiti; nessun risultato di produttore o collaudo hardware. 37% documentale stimato; 0 prototipi validati. NO FAB / NO PCBWay / NO TX.

---
## Note gestionali storiche

# RIPRENDI — Superstar 3900 SMD Evolution V5.3 — 8 novembre 2026

**In una nuova chat allega unicamente** `Superstar3900_SMD_Evolution_V5.3.zip`. Leggi `README.md`, questo file, il rapporto V5.3, il registro decisioni e i nove gate V5.0.

**Radio finale (solo requisiti):** Superstar 3900 estetica vintage, 6 bande A–F e 270 RX, ALFA/CH9, AM/FM/USB/LSB/CW RX, PA, VOX, Dual Watch, Echo, Roger Beep, CTCSS/DCS, DSP, ATU e misure SWR/PEP. TX disabilitata.

**Stato verificato V5.3:** 37% stima storica, 0 hardware validato. Nessun file KiCad storico o candidato modificato. Audit indipendente della coppia V5.2: 15 componenti, 31 pin, 31 fili etichettati, 8 reti, nessuna divergenza statica; 18 nuovi test e 14 suite di regressione superati. **Non sono test nativi KiCad**. `kicad-cli` assente, ERC/DRC/refill/parità `NOT_RUN`. Non ci sono risposte DFM o collaudi reali. **NO FAB / NO PCBWAY / NO TX**.

**Priorità V5.4:** eseguire la procedura nativa `03_Verifiche/V5.2/run_kicad_v52.py` su PC KiCad 10, allegare ERC/DRC/parità e correggere errori reali su copia; acquisire modello CAD TE esatto e approvazione scritta VIPPO/stencil/termica e stack-up RF. Manuale illustrato `06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf`. Preservare tutto e produrre ZIP cumulativo con manifest SHA-256.

**Prompt da incollare:** «Riprendi Superstar3900 SMD Evolution dal ZIP V5.3 allegato. Leggi README, RIPRENDI, rapporto V5.3, registro decisioni e gate V5.0. Mantieni tutte le versioni; prosegui con KiCad nativo e qualifica TE/ADL5535 senza dichiarare hardware validato o autorizzare fabbricazione/TX.»

---
## Storico V5.2 e precedenti

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

# Gestione progetto — indice di ripresa V4.6

L'istruzione corrente è nella **radice dell'archivio**, `RIPRENDI_IN_UNA_NUOVA_CHAT.md`. Non utilizzare i riferimenti V4.4 qui precedentemente riportati come stato attuale. L'originale V4.5 di questa pagina è conservato in `00_Gestione_Progetto/V4.6_SNAPSHOT_V4.5/`.

Per ultimo stato e rischi leggi `03_Verifiche/V4.6/RAPPORTO_TECNICO_V4.6.md`, `00_Gestione_Progetto/REGISTRO_DECISIONI.md`, quindi `03_Verifiche/V4.6/TEST_V4.6.txt`. Archivio cumulativo **V4.6**, 0 moduli validati, fabbricazione e TX bloccate.


## V6.9 — LO2, BFO e demodulazione (9 novembre 2026)

Nuovi circuiti candidati U971 SI5351C 20-QFN, U981 TS5A3157, demod AM/FM provvisori; 1.350 profili e 70 test nuovi, 541 selezionati. Restano non realizzati il buffer +7dBm, filtri SSB/CW, demod FM hardware, interlock output indipendente, ERC/DRC e hardware. **Non fabbricare e non trasmettere.** Vedi 03_Verifiche/V6.9/RAPPORTO_TECNICO_COMPLETO_V6.9.md.
