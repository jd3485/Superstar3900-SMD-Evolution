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
