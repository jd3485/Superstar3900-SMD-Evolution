# Cancelli di accettazione RF — V4.1 (nessun rilascio produttivo)

**Stato complessivo:** BLOCCATO / NO FAB / NO PCBWAY / TX DISCONNESSA. Nessuna delle evidenze di questa revisione è un DRC/ERC, una misura RF o una verifica termica reale.

| Cancello | Criterio di chiusura e prova richiesta | Stato V4.1 |
|---|---|---|
| A — TE SMA | Confronto *approvato* tra footprint J101–J104 e DXF/STEP TE esatti `CONSMA002-SMD-G`: centro, massa, keep-out, corpo fuori bordo, orientamento, F.Mask e F.Paste | APERTO: Ø2,05 nominale; 7,40 contro 7,76 mm estensione GND; CAD produttore non acquisito in file nel pacchetto |
| B — ADL5535 | Revisione geometria land ADI Fig. 17; progetto termico, maschera pasta, via/tenting e contatto a piani; approvazione PCB assembler | APERTO: paddle 1,80×3,48 mm; via più vicino esterno e connesso con pista; nessuna misura temperatura |
| C — KiCad | Apertura file, riempimento 4 zone, verifica DRC e correzione di ogni violazione reale; versione KiCad e report allegati | APERTO: `kicad-cli` assente qui; script di esecuzione nativa per KiCad 10+ incluso |
| D — Schema reale | ERC e confronto parità schematica/PCB usando schema completo, associazione footprint e BOM | APERTO: schema V3.1 provvisorio, non progetto finale |
| E — Impedenza | Stack-up reale PCBWay, L1-L2, via, apertura soldermask, modello CPWG/microstrip, target 50 Ω | APERTO: nessun stack-up produttivo approvato |
| F — Coupon RX | Alimentatore con limitazione corrente; collaudo di dissipazione, S11/S21, rumore e comportamento a 27 MHz sul PCB fisico | APERTO: 0 prototipi fabbricati/collaudati |
| G — Trasmissione | Separazione TX, rispondenza normative applicabili, RF HW interlocks, prove indipendenti | BLOCCATA: non collegare TX |

## Nuova evidenza utile, senza sign-off

- Analisi statica controllata `03_Verifiche/V4.1/audit_rf_v41.py`, risultati JSON e 12 test automatici. Verifica integrità SHA-256 del PCB V3.8; non modifica le coordinate né genera Gerber.
- Attenuatore π **ideale a 50 Ω**: R201=150 Ω shunt, R203=37,4 Ω serie, R202=150 Ω shunt. Attenuazione teorica ~6,013 dB, return loss nominale calcolata ~67,04 dB nel modello perfettamente resistivo. La return loss reale sarà limitata dalle tolleranze e dai parassiti. Analisi puramente illustrativa ±1% resistori: perdita ~5,955–6,071 dB e return loss peggiore ~47,51 dB tra otto angoli; verificare tolleranze reali BOM.
- ADL5535 con 5 V e corrente a riposo tipica di 97 mA: ingresso elettrico ~0,485 W. Il datasheet indica 650 mW come massimo assoluto dissipazione interna **con paddle saldato**, θJA=30,7 °C/W nelle condizioni del documento; la stima aritmetica 14,9 °C **non è una temperatura di giunzione validata per questo PCB**. Serve prova termica con pad e piani definitivi.
- Il via GND (68,00;31,05) ha bordo rame a 0,50 mm dalla piazzola esposta U101 e una pista esplicita fino al suo rame; **zero** via con centro interno alla piazzola. Ciò non implica automaticamente un guasto: impedisce però di qualificare la dissipazione sulla sola base del PCB.

## Fonti primarie, accessibili esternamente (non ridistribuite)

1. TE Connectivity `CONSMA002-SMD-G` e Customer Drawing `C-CONSMA002-SMD-X-X`, rev. D, foglio 2: https://www.te.com/en/product-CONSMA002-SMD-G.html
2. Analog Devices ADL5535, datasheet rev. A, pp. 6–7 e 11, Figure 17: https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf
3. KiCad 9 CLI (senza `--refill-zones`) https://docs.kicad.org/9.0/en/cli/cli.html ; KiCad 10 CLI (con `--refill-zones --save-board`) https://docs.kicad.org/10.0/en/cli/cli.html

La documentazione TE contiene risorse CAD di proprietà del produttore: il pacchetto contiene riferimenti e calcoli derivati, non i suoi DXF/STEP.
