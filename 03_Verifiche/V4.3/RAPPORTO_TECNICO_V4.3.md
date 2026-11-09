# Superstar 3900 — rapporto tecnico V4.3 (08/11/2026)

## Oggetto

**Variante SMA esclusivamente sperimentale**, basata su V3.8, in una cartella di lavoro separata. Lo schema/PCB V3.8 e tutti gli altri sorgenti rimangono byte-identici. La variazione NON è tratta da un CAD TE importato: è una variazione *parametrica* destinata a valutare l'effetto sulle connessioni mentre si attende il modello ufficiale, non una soluzione approvata. Non vengono prodotti Gerber.

## Modifica introdotta nella sola copia

- 4 connettori SMA **J101, J102, J103, J104**.
- Spostati i centri dei **16 pad GND custom** da Y=±2,950 mm a Y=±3,130 mm (spostamento 0,180 mm verso l'esterno del singolo SMA); pad RF, vertici dei poligoni, maschera, pasta, piste, via, componenti e bordo invariati.
- L'inviluppo verticale nominale del GND diventa **7,76 mm**, invece dei **7,40 mm** V3.8; questo dato da solo **NON dimostra** che il land pattern corrisponda al part number `CONSMA002-SMD-G`.
- La variante non è una modifica dello sbroglio approvata. Dopo import DXF/STEP ufficiale potrebbero servire una sagoma diversa, nuovi fori, mask/paste, rimozione o riposizionamento dei pad o un diverso connettore.

## Verifiche statiche su copia

| Controllo | Originale V3.8 | V4.3 ipotesi |
|---|---:|---:|
| Ingombro verticale GND SMA | 7,40 mm | **7,76 mm** |
| Footprint | 15 | 15 |
| Tracce/via | 44/64 | 44/64 |
| Reti | 8 | 8 |
| Distanza minima nominale F.Cu inter-reti | 0.45 mm | 0.45 mm |
| Coppie sotto 0,20 mm nel modello | 0 | 0 |
| Pad GND non collegati localmente ad almeno un via | 0 | 0 |
| Reti non GND senza isole su F.Cu | 7/7 | 7/7 |
| Zone GND non riempite | 4 | 4 |

**Regressioni:** 21 nuovi test sul modello V4.3; ri-eseguite le verifiche V4.2 (19 test), V4.1 (12 test) e le 2.400 combinazioni software del supervisore V4.0 (risultati registrati). Questi test sono indipendenti da KiCad e non rilevano tutte le violazioni DRC/DFM o RF.

## Termica ADL5535 — stato invariato

U101 ha pad esposto 1,80 × 3,48 mm, **zero via sotto il pad**, e via GND esterno con separazione geometrica di circa 0,50 mm dal rame del paddle. Sorgente ADI: alimentazione 5 V, consumo tipico 97 mA, quindi ingresso elettrico ~0,485 W (non confondere con potenza dissipata garantita). Mancano via pattern termico approvato, analisi IPC/assemblaggio per aperture di pasta e saldatura, θJA reale e misure della temperatura su prototipo. **NESSUN SIGNOFF TERMICO**.

## Mancanze bloccanti

1. Acquisire da TE i files `ENG_CVM_CVM_CONSMA002-SMD-G_D.2d_dxf.zip`, `...3d_stp.zip` e disegno cliente Rev. D; qui il sito mostra i download, ma l'accesso diretto al contenuto non è riuscito; **non rivendichiamo confronto CAD eseguito**.
2. Importare CAD e verificare asse meccanico, bordo scheda, piedini/mask/paste/courtyard e distanza delle 4 SMA dalle piste. Nessuna approvazione TE fino al confronto quotato completo.
3. Concordare pad esposto U101, stitching via, stencil e profilo reflow con assemblatore e ricontrollare geometria/termica.
4. KiCad nativo **non disponibile in questo ambiente**: eseguire `03_Verifiche/V4.3/RUN_KICAD_NATIVE_CANDIDATO_V4.3.sh` su macchina KiCad 10+; refill 4 zone + DRC sul **file copiato** e revisione manuale. Il launcher qui ha prodotto codice di uscita 2 (BLOCCATO), non un rapporto DRC.
5. Il solo schema disponibile RX V3.1 non è una sorgente coerente con la PCB V3.8; progettare sincronizzazione schema, poi ERC e controllo parità con il PCB.
6. Ottenere stack-up a quattro strati approvato, risolvere CPWG 50 Ω, collaudo RX/VNA e termico dopo fabbricazione autorizzata.

**Fonti ufficiali:** https://www.te.com/en/product-CONSMA002-SMD-G.html ; https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf ; https://docs.kicad.org/10.0/en/cli/cli.html .

**Stato: 37% stimato come documentazione, 0 hardware collaudato, NO FAB / NO PCBWAY / NO TX**.
