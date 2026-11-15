# V7.77 — verifica fisica 11 footprint critici sul master KiCad9 a 7 fogli

**Obiettivo progettuale:** ridurre il rischio di integrare sul PCB un pin elettrico senza pad fisico corrispondente. Il programma `test_critical_native_pad_numbering_v777.py` usa **la netlist nativa V7.74** (140 componenti/103 reti) generata dalla suite KiCad9 V7.74 nello stesso job, legge **tutti i 140 riferimenti/footprint reali** e produce l'inventario completo dei footprint assenti. Analizza i file `.kicad_mod` reali delle librerie versionate e le impronte standard effettivamente installate in KiCad9, non una BOM inventata.

## Matrice di verifica effettiva

| Ref | Footprint in sorgente V7.74 | Pad fisici necessari | Vincolo |
| --- | --- | ---: | --- |
| F200 | Littelfuse Nano2 vendor candidate | 1–2 | Fusibile; numerazione e footprint CAD non sono qualifica curva termica |
| U200 | TI TPS26600 PWP TSSOP-16-1EP | 1–17 | **EP17 = EFUSE_RTN** suddiviso in **8 pad rame sovrapposti logicamente** nel footprint KiCad9 generico; distinto da GND9 |
| SW200 | C&K KMR223NG ULC LFG 4pad | 1–4 | Contatti 1+4 SHDN, 2+3 GND_MAIN; ESD e accessibilità HOLD |
| U100 | TI TPS54202 DDC SOT-23-6 | 1–6 | Fonte buck, layout SW/FB e termica da qualificare |
| L100 | Bourns SRP1038A-150M | 1–2 | Percorso corrente e calore, footprint vendor candidato |
| U6201 | ST STM32G474RE LQFP64 | 1–64 | Interfacce e sorgenti MCU OPEN/HOLD |
| U6202 | TI TLV320AIC3204 RHB-32+EP | 1–33 | **EP33 obbligatorio**, includere paste/thermal review |
| U6203–U6206 | TI TPS7A2033 DBV0005A (4 unità) | 1–5 ciascuno | Carichi/temperatura reali ignoti |

Il gate **fallisce** su riferimento mancante, libreria non trovata, footprint assegnato diverso, pad mancante o duplicato diverso dagli **otto pad rame EP17 previsti in U200**, pin connesso senza pad o regressione del numero di componenti; non corregge e non cancella ERC. Conta e pubblica la lista completa dei componenti senza footprint per scegliere una reale ECO BOM+CAD a partire dal blocco fisico più importante.

**Limitazioni non negoziabili:** pad numbers presenti non dimostrano geometria/land pattern vendor, pin-function elettrici corretti, saldabilità o approvazione di produzione. La valutazione EP33/EP17 deve includere massa/ritorno separati, solder paste, layout termico e DRC PCB. La suite finale V7.77 non certifica hardware né acquisisce dati di carico 5V/3,3V. Restano **28 errori/ERC + 180 warning come ultima evidenza V7.74**, 15 interfacce HOLD, SG48/Y1 pin10 HOLD, **NO FAB / NO GERBER / NO PCBWAY / NO TX**.

**Criterio di successo:** passaggio del job nativo con inventario JSON in `03_Verifiche/V7.77/output-ci/`, nessun impatto ad altri 476+ test o agli output prima/dopo KiCad9. Nessuna modifica CAD in V7.77; prossimo lavoro deve scegliere i reali footprint assenti da questo inventario e qualificare datasheet simbolo→pad→land, oppure completare interconnessioni elettriche fondate.

**Scoperta fail-closed CI iniziale:** il footprint standard `Package_SO:TSSOP-16-1EP_4.4x5mm_P0.65mm` contiene 16 pad laterali e **otto rettangoli F.Cu/F.Paste/F.Mask** con numero 17, totale 24 primitive rame ma solo **17 numeri elettrici**. Non sono aperture esclusivamente pasta: ogni isola porta anche F.Cu; il conteggio ingenuo `len(pads)==len(set(pads))` fallisce correttamente sulla geometria complessa ma non indica pin elettrici duplicati indipendenti. Gate aggiornato per consentire *soltanto* U200 pad17 ×8, lasciando fallire tutte le altre duplicazioni e obbligando alla qualifica fisica TI PWP. Non si deve dichiarare footprint U200 validato per produzione con il mero conteggio di 17 numeri.
