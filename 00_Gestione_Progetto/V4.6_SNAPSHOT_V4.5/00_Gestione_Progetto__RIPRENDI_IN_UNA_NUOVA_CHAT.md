**ATTUALE: V4.4. Leggere il file `RIPRENDI_IN_UNA_NUOVA_CHAT.md` nella cartella radice.**

# RIPRENDI — Superstar 3900 SMD Evolution V4.4 (2026-11-08)

**Archivio da allegare a una nuova chat:** `Superstar3900_SMD_Evolution_V4.4.zip`. Questo ZIP è cumulativo e conserva i file storici, compreso il manuale d'uso illustrato V4.0.

## Visione della radio finale (requisiti, non caratteristiche dimostrate)

Ricetrasmettitore CB con estetica Superstar 3900 vintage, 6 bande A–F e 270 posizioni RX (40+5 ALFA per banda), AM/FM/USB/LSB/CW RX, PA senza RF, CH9 27,065 MHz AM, ALFA fisico, VOX, Dual Watch, Echo, Roger Beep, CTCSS/DCS, DSP, strumenti SWR/PEP, ATU. MCU STM32G474RE, codec TLV320AIC3204 e PLL LMX2572 candidati. TX vincolata a norme, conformità e interblocchi hardware/firmware indipendenti. Manuale V4.0 ancora **bozza**.

## Stato tecnico

- **37% stimato solo progettuale**, hardware collaudato 0; NO FAB / NO PCBWAY / NO TX. PCB sperimentale 110×62 mm, quattro strati in studio, 4 zone GND non riempite.
- PCB V3.8 immutato, SHA-256 `57dd24b13edb5dc987e3ad8cdae0d2d8cc7a1fa3aefb455a63ebc86559eec489`; variante di studio SMA V4.3 non approvata TE, 16 pad GND spostati ±0,18 mm e inviluppo nominale 7,76 mm. Nessuna verifica CAD TE integrale.
- **NOVITÀ V4.4:** schema RX ricostruito in `04_KiCad/Modulo_RX_Test_50ohm_V4.4_SCHEMA_MATCH/`, con mappa verificata staticamente: 15 riferimenti, 31 pin, 8 reti, valori e ID footprint congruenti con PCB V3.8 e V4.3. Schema V3.1 originale intatto. 20 test V4.4 superati, rieseguiti V4.3 (21), V4.2 (19), V4.1 (12), supervisore (2.400 stati). Non è collaudato con KiCad.
- **Bloccanti:** KiCad CLI non disponibile: nessun ERC, DRC, refill o check parità schematico-PCB; associazioni UUID e librerie `.pretty` incomplete; footprint SMA TE non approvato; ADL5535 thermal pad senza via sotto pad e termica/paste aperte; 50 Ω senza stack-up confermato; nessuna misura VNA/RF o prototipo fisico.

## Istruzioni per la ripresa

1. Leggere `README.md`, `00_Gestione_Progetto/REGISTRO_DECISIONI.md`, `00_Gestione_Progetto/CHANGELOG_V4.4.md`.
2. Leggere `03_Verifiche/V4.4/RAPPORTO_TECNICO_V4.4.md` e `VERIFICA_SCHEMA_PCB_V4.4.json`.
3. Rigenerare il candidato con `python3 03_Verifiche/V4.4/sincronizza_schema_rx_v44.py`, poi `python3 03_Verifiche/V4.4/test_schema_pcb_v44.py` (stdlib e parser storico, nessun accesso web).
4. Priorità V4.5: creare librerie footprint autonome da geometrie verificate, verificare DXF/STEP TE e quote/courtyard/mask/paste su copia, piano termico ADL5535; successivamente ERC/DRC KiCad native e parità, stack-up 50 Ω e test RF.
5. Conservare sempre tutte le revisioni, manuali, sorgenti, registro decisioni e manifest hash. Non produrre Gerber né fabbricare finché il percorso di validazione non è concluso.

**Messaggio da incollare in una nuova chat:** “Riprendi Superstar3900 SMD Evolution dall'archivio V4.4 allegato. Leggi prima README e RIPRENDI_IN_UNA_NUOVA_CHAT, registro decisioni e rapporto V4.4. Mantieni le decisioni e tutti gli storici; continua da footprint libraries, CAD TE, termica ADL5535, ERC/DRC nativi e parità. Nessuna fabbricazione o TX finché non validati. Produci sempre revisioni cumulative verificabili.”
