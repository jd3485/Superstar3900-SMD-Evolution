# RIPRENDI — Superstar 3900 SMD Evolution V4.3 — 2026-11-08

Archivio cumulativo: `Superstar3900_SMD_Evolution_V4.3.zip` — contiene interamente V4.2 e tutti gli storici.

## Radio definitiva prevista
Estetica Superstar 3900 classica, 6 bande A–F, 270 posizioni RX (40 ordinarie e 5 ALFA per banda), RX AM/FM/USB/LSB/CW, PA senza RF, interruttori ALFA e CH9 27,065 MHz AM, VOX, Dual Watch, Echo, Roger Beep, CTCSS/DCS, DSP, strumentazione SWR/PEP, ATU; TX vincolata a legge, conformità, progettazione indipendente fail-safe e prove. Sono **obiettivi**, non funzioni hardware validate. Manuale V4.0 **bozza**.

## Stato attuale
- 37% progettuale stimato (non misura hardware); 0 moduli fisici validati; NO FAB / NO PCBWAY / NO TX.
- PCB sperimentale originale: `04_KiCad/Modulo_RX_Test_50ohm_V3.8/...kicad_pcb`, SHA-256 `57dd24b13edb5dc987e3ad8cdae0d2d8cc7a1fa3aefb455a63ebc86559eec489`, **non modificato**. 110x62 mm, 15 footprint, 44 piste, 64 via, 4 zone GND non riempite.
- NUOVO V4.3: `04_KiCad/Modulo_RX_Test_50ohm_V4.3_STUDIO_SMA/...kicad_pcb`, **copia di studio** con 16 pad GND custom spostati ±0,18 mm. Inv. verticale 7,76 mm anziché 7,40. Stessa clearance inter-net del modello 2D 0,45 mm; connessioni GND locali senza regressioni. Non esiste ancora import CAD DXF/STEP TE: NON APPROVATA.
- ADL5535: pad esposto senza via-in-pad; termica, solder paste e PCB stack-up non approvati.
- KiCad CLI non disponibile in questa sessione: nessun DRC/ERC/parità; schema RX disponibile è V3.1, non un abbinamento sincronizzato con il PCB V3.8.
- Regressioni: 21 nuovi test V4.3 + 19 V4.2 + 12 V4.1; 2.400 combinazioni V4.0 del supervisore rieseguite con esito positivo (solo software).

## Dove leggere e come continuare
1. `README.md`, `00_Gestione_Progetto/REGISTRO_DECISIONI.md`, `00_Gestione_Progetto/CHANGELOG_V4.3.md`.
2. `03_Verifiche/V4.3/RAPPORTO_TECNICO_V4.3.md`, `RISULTATI_CANDIDATO_SMA_V4.3.json`, grafico e test; `01_Specifiche/Checklist_SMA_ADL5535_V4.3.md`.
3. Ottenere DXF/STEP e disegno cliente ufficiali TE `CONSMA002-SMD-G`, confrontare tutte le quote sul footprint copia, non adottare automaticamente l'ipotesi V4.3.
4. Concordare thermal via / paste / assemblaggio ADL5535 e ottenere stack-up PCBWay reale, calcolare CPWG.
5. Produrre schema KiCad RX allineato, eseguire ERC/DRC nativi con zone riempite su copie e registrare file report; collaudo RF/VNA/termico solo a prototipo autorizzato.
6. Ogni nuova revisione: ZIP cumulativo con SHA-256 e snapshot, senza eliminare PCB originale, manuali, sorgenti o test.
