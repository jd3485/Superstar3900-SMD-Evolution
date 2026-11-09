# RIPRENDI - Superstar 3900 SMD Evolution V4.2 - 2026-11-08

**Archivio unico:** `Superstar3900_SMD_Evolution_V4.2.zip`. Non occorrono ZIP precedenti; lo storico è incluso.

## Visione radio definitiva (REQUISITI, non hardware)

Stile Superstar vintage; 6 bande A-F, 40 canali ordinari + 5 ALFA per banda = 270 RX; ALFA fisico, CH9 prioritario 27,065 MHz AM, AM/FM/USB/LSB/CW RX e PA senza RF, VOX, Dual Watch, Echo, Roger Beep, CTCSS/DCS, DSP e misure SWR/PEP/modulazione, ATU. Trasmissione solo con profilo normativo conforme, circuiti fail-safe indipendenti e dopo collaudo. Manuale MU01 V4.0 PDF è **BOZZA**.

## Stato documentale/tecnico

37% stimato invariato; 0 moduli hardware validati. Ultimo PCB fisico da file è ancora **V3.8 RX 110x62 mm**, 15 footprint, 8 reti, 44 piste, 64 via e 4 zone GND non riempite; SHA-256 `57dd24b13edb5dc987e3ad8cdae0d2d8cc7a1fa3aefb455a63ebc86559eec489`. NON per produzione. V4.0 simulatore supervisione 2.400 casi software; V4.1 12 test RF statici; **V4.2 19 test geometria 2D**, senza collaudo hardware. Il PCB V3.8 è identico alle revisioni precedenti.

### Nuovo V4.2

- Audit con geometria vera del pad custom e rotazioni, 152 forme F.Cu (pad/track/via), distanza minima modellata inter-reti 0,45 mm, nessuna coppia sotto 0,20 mm, 7/7 reti non massa continue nel modello, 24/24 pad GND con pista locale verso un via. Non è KiCad DRC né conferma del piano GND globale.
- SMA: orientamento e courtyard con 7,2 mm di sporgenza nominale oltre bordo; land GND totale 7,40 mm mentre TE indica 7,76 mm. DXF/STEP originale non importato né footprint approvato.
- ADL5535: 0 via sotto exposed paddle; collegamento a via esterno 0,50 mm dal rame. Termica/stencil non approvati.
- 0,28 mm di pista RF non garantisce 50 Ω in mancanza di stack-up (studio microstrip isolata su h variabile, NO modello CPWG).
- KiCad CLI assente qui; nessun DRC/ERC o zone refill verificato. NO FAB / NO PCBWAY / NO TX.

## Ripresa operativa

1. Leggere `README.md`, `00_Gestione_Progetto/REGISTRO_DECISIONI.md`, `00_Gestione_Progetto/CHANGELOG_V4.2.md`, `03_Verifiche/V4.2/RAPPORTO_TECNICO_V4.2.md` e JSON corrispondente.
2. Ripetere regressione `python3 03_Verifiche/V4.2/test_geometria_rf_v42.py` (richiede Shapely 2.x); non reinterpretare un test statico come DRC.
3. Confrontare ed eventualmente modificare **solo una copia** footprint SMA usando DXF/STEP del pezzo esatto TE; ottenere signoff termico ADI/stencil e stack-up CPWG PCBWay.
4. KiCad 10+ CLI su copia: DRC con 4 zone riempite, ERC schema corretto, controllo parità e verifiche manuali meccaniche; salvare i report.
5. Solo dopo approvazioni complete: coupon RX, alimentazione limitata, VNA/termocamera; TX scollegata.

Ogni revisione futura deve essere un **nuovo ZIP cumulativo**, con manifest SHA-256 e snapshots di README, RIPRENDI e registro decisioni. Non perdere manuali, sorgenti, né il PCB V3.8 originale. Nessun Gerber finché i cancelli non si chiudono.
