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
