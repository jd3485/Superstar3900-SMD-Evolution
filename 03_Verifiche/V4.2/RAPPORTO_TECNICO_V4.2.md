# Rapporto di avanzamento RF V4.2 - 08/11/2026

## Oggetto e metodica

Controllo geometrico statico e indipendente, sul **PCB RX V3.8 originale, in sola lettura**, con forme poligonali custom di tutti i pad SMA, inclusi anchor/rotazioni, piste F.Cu e via. Non è stata effettuata alcuna modifica al PCB originale. Non è stato eseguito DRC/ERC nativo, non sono state riempite le zone (quattro zone GND non riempite). Richiede `shapely>=2.0` e i parser storici già nell'archivio.

## Risultati

| Voce | V4.2 | Significato |
|---|---:|---|
| Controlli automatici nuovi | **19/19** | Solo regressione del modello geometrico |
| Oggetti rame nel modello | 152 | Pad, tracce, via (sommati) |
| Minimo spazio tra reti distinte in F.Cu | **0,450 mm** | Più vicino tra pad dei condensatori e resistori; valore 2D nominale |
| Coppie sotto soglia analitica 0,20 mm | **0** | Non equivale a clearance DRC KiCad |
| Reti di segnale/alimentazione sul top layer senza isole | **7/7** | Copertura geometrica, non prova RF |
| Pad GND con percorso locale fino a un via GND | **24/24** | Connessione locale; global plane non ancora verificato |
| Zone GND | **4 dichiarate; 0 riempite** | Nessuna certificazione dei piani |
| SMA a 180 gradi (destra) | J102/J104 | Geometria trasformata correttamente nel modello |
| Ingombri SMA oltre bordo PCB | 7,2 mm per ciascun lato | Solo `F.CrtYd`, non sagoma 3D TE |

Tutti i risultati numerici sono disponibili in `RISULTATO_GEOMETRIA_RF_V4.2.json`; software e test inclusi e rieseguibili. La misura minima di 0,45 mm deriva dalla geometria semplificata sul top-layer: il progetto NON ha ancora un DRC nativo o regole di fabbricazione approvate.

## SMA TE `CONSMA002-SMD-G`

Il disegno ufficiale TE `C-CONSMA002-SMD-X-X`, rev. D, foglio 2, indica un footprint raccomandato con estensione verticale **7,76 mm**. Il footprint KiCad custom ha estensione verticale dell'inviluppo GND **7,40 mm**, scostamento nominale **-0,36 mm**. Il pad RF circolare ha Ø **2,05 mm** come riferimento dimensionale nell'immagine TE, ma deve essere chiarita la natura della superficie a centro (contatto/rame/meccanica) e confermato l'intero disegno. Non estendere arbitrariamente le piazzole: acquisire DXF/STEP del part number esatto, verificare stack-up, maschera, pasta, quote e sporgenze su copia del footprint. Il sito TE segnala prodotto attivo ma senza disponibilità immediata; prima di acquistare chiedere conferma della fornitura.

Il solo `F.CrtYd` si estende di **7,2 mm** oltre ciascun bordo sinistro/destro sui rispettivi due connettori; la cifra non è l'effettivo overhang meccanico validato. **SMA non approvato per montaggio.**

Fonte ufficiale: https://www.te.com/en/product-CONSMA002-SMD-G.html - Customer Drawing Rev. D, pagina 2; CAD TE disponibile dal catalogo del produttore, non ridistribuito.

## ADL5535 - necessità di revisione termica

ADI specifica al foglio 11, Fig. 17, il land pattern raccomandato e raccomanda di saldare il paddle esposto connesso a pin 2 al piano GND, con stitching via per i piani multipli. Il PCB RX V3.8 ha **zero via centrati nel pad esposto** (1,80 × 3,48 mm); il via più vicino ha bordo rame a 0,50 mm dal pad ed è raggiunto tramite pista F.Cu. Ciò non dimostra un guasto termico, ma **non certifica** che la soluzione dissipi adeguatamente 0,485 W elettrici tipici a 5 V/97 mA. Progettare via/stencil con produttore di montaggio, con attenzione alla migrazione della pasta e alle specifiche del via-in-pad; stimare e poi misurare Tj/case su esemplare reale.

Fonte ufficiale: https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf (rev. A, pp. 6, 11).

## Impedenza della pista da 0,28 mm - sola sensibilità teorica

In un **modello di microstrip isolata** (rame di spessore nullo, εr=4,2, senza soldermask e senza il rame di massa adiacente), una pista larga 0,28 mm dà:

| Altezza dielettrico L1-L2 simulata | Impedenza isolata nominale |
|---:|---:|
| 0,08 mm | 34,51 Ω |
| 0,12 mm | 45,37 Ω |
| 0,14 mm | 49,93 Ω |
| 0,18 mm | 57,77 Ω |
| 0,20 mm | 61,18 Ω |

Queste cifre NON sono l'impedenza del PCB in esame: il layout reale include GND adiacente (CPWG), via, transizioni SMA, maschera e parametri del fornitore non fissati. Il caso 0,14 mm non è una scelta progettuale, bensì una dimostrazione che lo stack-up è determinante. Serve modello CPWG basato su stack-up **approvato da PCBWay** e misura RF/VNA in seguito.

## Cancelli produzione / cosa fare

1. Importare CAD ufficiale TE in un ambiente KiCad; confrontare geometria, quote, bordo scheda, soldermask e 3D. Salvare relazione di approvazione; **non fare correzioni alla cieca**.
2. Riprogettare/approvare termica e pasta ADL5535 con assemblatore, non solo software.
3. KiCad nativo **ancora assente in questa sessione**: usare il launcher V4.1 su copia e allegare report reali (DRC/ERC) e revisione dei piani riempiti.
4. Chiedere a PCBWay stack-up 4 strati, materiali, maschera e regole; risolvere CPWG a 50 Ω.
5. Fabbricare coupon RX solo dopo signoff PCB/schematico/termico/impedenza; svolgere misure VNA e termiche con TX scollegata.

**Verdetto: NO FAB / NO PCBWAY / NO TX**. Avanzamento complessivo documentale stimato **37% invariato**, **0 hardware collaudati**.
