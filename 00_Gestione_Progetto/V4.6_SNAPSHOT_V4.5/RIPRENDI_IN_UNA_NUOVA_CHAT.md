# RIPRENDI — Superstar 3900 SMD Evolution V4.5 — 8 novembre 2026

**Allega a una nuova chat:** `Superstar3900_SMD_Evolution_V4.5.zip` (è autosufficiente, cumulativo e comprende storico, manuali, sorgenti e verifiche).

## Obiettivo della radio definitiva — requisiti, NON caratteristiche provate

Ricetrasmettitore CB estetica Superstar 3900, 6 bande A–F e 270 posizioni RX (40+5 ALFA per banda), AM/FM/USB/LSB/CW RX, PA senza RF, CH9 27,065 MHz AM, ALFA fisico, VOX, Dual Watch, Echo, Roger Beep, CTCSS/DCS, DSP, strumenti SWR/PEP, ATU. STM32G474RE, codec TLV320AIC3204 e PLL LMX2572 candidati. TX subordinata a normativa, progetto validato e interblocchi indipendenti. Manuale utente illustrato V4.0 in **bozza**.

## Stato reale alla V4.5

- **37% stimato solo progettuale**, zero hardware collaudato. **NO FAB / NO PCBWAY / NO TX**. PCB test RX 110 × 62 mm, 4 strati di studio e zone GND non validate con KiCad.
- PCB V3.8 storico immutato, SHA-256 `57dd24b13edb5dc987e3ad8cdae0d2d8cc7a1fa3aefb455a63ebc86559eec489`; PCB SMA V4.3 rimane candidato con piazzole GND spostate ±0,18 mm, NON approvato TE.
- Schema candidato RX V4.4 mappa 15 componenti, 31 pin e 8 reti coerenti con il PCB nel test statico.
- **NOVITÀ V4.5:** nuovo sotto-progetto `04_KiCad/Modulo_RX_Test_50ohm_V4.5_LIBS_PORTABILI_NOT_FOR_FAB/` con tre librerie `.pretty` (9 footprint), libreria di 9 simboli, tabelle locali per KiCad, PCB V4.3 duplicato byte-identico e schema V4.4 con basename allineato. 26/26 test statici superati. Regressioni V4.0–V4.4 superate.
- Nessun KiCad nativo disponibile nella sessione: non eseguiti ERC, DRC, refill zone e parity. Nessuna verifica geometrica CAD TE completa, né approvazione termica ADL5535; stack-up 50 Ω e misure VNA ancora mancanti.

## Come riprendere

1. Leggi prima `README.md`, `00_Gestione_Progetto/REGISTRO_DECISIONI.md`, `00_Gestione_Progetto/CHANGELOG_V4.5.md` e `03_Verifiche/V4.5/RAPPORTO_TECNICO_V4.5.md`.
2. In un computer con KiCad, apri il sotto-progetto V4.5; verifica che le librerie portabili si risolvano e avvia `03_Verifiche/V4.5/RUN_KICAD_RX_V45.sh`. Analizza gli output completi, senza scambiare un comando eseguito per un'approvazione ingegneristica.
3. Priorità V4.6: acquisire CAD del connettore esatto TE e confrontare tutte le quote; definire termica ADL5535 e stack-up; risolvere ERC/DRC e parità, poi preparare piano di misure VNA e primo prototipo di sola RX.
4. Conserva tutte le revisioni, il manuale, le note e il manifest. Le modifiche restano sempre reversibili.

**Messaggio per una nuova chat:** “Riprendi il progetto Superstar 3900 SMD Evolution dall'archivio V4.5. Leggi README, RIPRENDI, registro decisioni e rapporto V4.5. Mantieni manuale, requisiti e tutta la storia; prosegui da validazione KiCad delle librerie, CAD TE, termica ADL5535 e stack-up. Non fabbricare né attivare TX finché le verifiche non sono completate. Crea soltanto nuove revisioni cumulative verificabili.”
