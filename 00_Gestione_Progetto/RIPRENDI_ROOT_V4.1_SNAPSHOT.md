# RIPRENDI — Superstar 3900 SMD Evolution V4.1 — 2026-11-08

**Unico archivio necessario:** `Superstar3900_SMD_Evolution_V4.1.zip` (cumulativo); non serve allegare le versioni precedenti.

**Stato consolidato:** 37% progettuale stimato, invariato; **0 hardware collaudati**; nessun ordine PCBWay, NO FAB, TX fisicamente scollegata. Ultimo PCB RF: V3.8 (`04_KiCad/Modulo_RX_Test_50ohm_V3.8/`, SHA-256 `57dd24b13edb5dc987e3ad8cdae0d2d8cc7a1fa3aefb455a63ebc86559eec489`), 110×62 mm, 15 footprints, 8 nets, 44 segments, 64 vias, 4 copper zone non riempite. KiCad nativo non eseguito.

**Requisiti radio finale:** Superstar vintage, 6 bande A–F, 40 + 5 ALFA per banda = 270 posizioni RX; ALFA fisico; CH9 override 27,065 MHz AM; AM/FM/USB/LSB/CW RX, PA senza RF, VOX, Dual Watch, Echo, Roger Beep, CTCSS/DCS, DSP, strumenti SWR/PEP/modulazione e ATU. La TX richiede profilo normativo conforme e protezioni HW/firmware indipendenti; caratteristiche finali non ancora realizzate su hardware.

**V4.0 preesistente:** manuale MU-01 illustrato *bozza* 11 pagine e simulatore `08_Firmware_Prototipi/radio_supervisor_v40.py` con test software combinatori. Non è firmware embedded approvato.

**V4.1 aggiunto:** static RF preflight `03_Verifiche/V4.1/audit_rf_v41.py`, 12 test unitari; audit JSON e rapporto. Quattro SMA TE: estensione pad GND locale 7,40 mm contro disegno 7,76 mm (-0,36 mm, non approvato). U101 ADL5535 paddle 1,80×3,48 mm; via GND esterno a 0,50 mm dal bordo rame paddle con pista GND esplicita; zero via centrati sotto il paddle, termica non validata. Rete π a 50 Ω R201/R203/R202 150/37,4/150 Ω: perdita resistiva ideale 6,013 dB, non misurata. A 5 V e 97 mA Iq tipica ADL5535 consuma elettricamente circa 0,485 W a riposo; servono prove termiche reali.

**Blocchi successivi (ordine):** (1) confronto DXF/STEP TE originale `CONSMA002-SMD-G` su *copia* footprint e approvazione CAD; (2) termica/stencil ADL5535; (3) KiCad CLI 10+ refill 4 zone su copia, DRC nativo + ERC schema e parity verificata; (4) stack-up PCBWay per 50 Ω; (5) soltanto dopo tutte le approvazioni, coupon RX e prove VNA. Non produrre Gerber né connettere TX.

**Letture principali:** `README.md`; `00_Gestione_Progetto/REGISTRO_DECISIONI.md`; `01_Specifiche/Requisiti_Accettazione_RF_V4.1.md`; `03_Verifiche/V4.1/RAPPORTO_V4.1.md`; `MANIFEST_SHA256_V4.1.csv`. Le fonti TE/ADI sono citate nei file, non incorporate per copyright.

**Messaggio consigliato nuova chat:** "Riprendi Superstar 3900 SMD Evolution dal solo ZIP V4.1. Leggi README, RIPRENDI, registro decisioni, requisiti accettazione e rapporto V4.1. Conserva i file di ogni revisione, mantieni NO FAB, non dichiarare validato l'hardware. Prosegui da CAD SMA ufficiale, termica ADL5535 e DRC nativo, usando copia del PCB. Crea aggiornamenti cumulativi con manifest SHA-256 e handoff nuovo."
