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
