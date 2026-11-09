**ATTUALE:** leggere prima il file `RIPRENDI_IN_UNA_NUOVA_CHAT.md` nella cartella radice della V4.0.

# RIPRENDI - Superstar 3900 SMD Evolution V4.0 (2026-11-08)

**Archivio unico:** `Superstar3900_SMD_Evolution_V4.0.zip`. Non serve la vecchia chat, ma consultare i documenti per evitare di inventare decisioni mai registrate.

**Stato:** 37% progettuale stimato (invariato); hardware RF funzionante verificato: **0 moduli**. Ultimo PCB sperimentale RX: **V3.8** 110 x 62 mm, 15 footprint, 8 reti, 44 segmenti, 64 vias, 4 zone non riempite. DRC nativo non eseguito. PROTOTIPO NO FAB/NO PCBWAY, TX scollegata.

**Requisiti congelati:** 6 bande A-F, 40+5 ALFA =270 posizioni RX; ALFA fisico; CH9 27,065 MHz AM prioritario; ricezione AM/FM/USB/LSB/CW, PA RF-OFF; VOX, Dual Watch, Roger Beep, Echo, 50 toni CTCSS, 104 DCS, filtri, DSP, display frequenza, misure SWR/potenza/modulazione, ATU. TX solo sotto vincoli di profilo nazionale, conformita' e interlock HW/firmware indipendenti. PLL LMX2572, MCU STM32G474RE e codec TLV320AIC3204 sono candidati/studi, NON componenti tutti approvati.

**Lavoro V4.0:** `06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf` (11 pagine, disegno pannello chiaramente illustrativo) e `.md` (tabella completa 270); `08_Firmware_Prototipi/radio_supervisor_v40.py` simulazione pura di priorita' CH9/PA/DW/VOX e TX fail-closed; test `03_Verifiche/V4.0/test_radio_supervisor_v40.py` su 2400 casi combinatori + guasti e input malformati. Questa non e' certificazione firmware o RF.

**PROSSIMO STEP:** completare import/verifica geometrica 2D/3D TE CONSMA002-SMD-G in una copia PCB (non ridistribuire CAD proprietario), controllare pad termico ADL5535 e paste; KiCad CLI ERC/DRC nativi con refill zone e netlist reale; conferma stack-up PCBWay 50 ohm; solo dopo approvazione e collaudo VNA il prototipo RX. Non emettere Gerber, non ordinare scheda, non connettere TX.

**Protocollo:** `01_Specifiche/Protocollo_Accettazione_CAD_V3.9.md`; rapporto `03_Verifiche/V4.0/RAPPORTO_V4.0.md`; storico `00_Gestione_Progetto/CHANGELOG_V4.0.md`; registro decisioni cumulativo; manifest `MANIFEST_SHA256_V4.0.csv`.

**MESSAGGIO DI RIPRESA CONSIGLIATO:** "Riprendi il progetto Superstar 3900 SMD Evolution dal pacchetto V4.0 allegato. Leggi prima README.md e RIPRENDI_IN_UNA_NUOVA_CHAT.md, registro decisioni, stato e test V4.0. Non dichiarare validati schematico, RF o TX; conserva tutte le revisioni e continua dal blocco SMA TE/DRC. Ogni nuova versione deve essere cumulativa, con manifest SHA-256 e un handoff aggiornato."
