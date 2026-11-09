# Checklist approvazione footprint SMA / termica ADL5535 — V4.3

## SMA TE CONSMA002-SMD-G (4 posizioni)

- [ ] Ricevuti disegno cliente Rev D + DXF 2D + STEP 3D esatti del part number
- [ ] Confronto quotato di posizione contatto centrale, 4 GND, spessore terminali e bordo PCB
- [ ] Confermata tipologia pad RF (pasta, maschera, foro o pad) con documenti TE
- [ ] Controllata reale sporgenza meccanica e interferenza con contenitore/assemblaggio
- [ ] Controllati mask expansion, paste apertures, via e transizioni CPWG per ciascun SMA
- [ ] Signoff footprint e 3D del montatore e progettista; non basato sulla sola quota 7,76 mm

## U101 ADL5535

- [ ] Verificata dissipazione alla massima temperatura ambiente prevista (specifica ancora da fissare)
- [ ] Pad esposto/pin 2 saldato su massa continua con stitching fra layer approvati
- [ ] Scelto numero/diametro/posizione via, riempimento/tenting per impedire lo wicking dello stagno
- [ ] Definite aperture pasta e spessore stencil con assemblatore (non assumere -10% universale)
- [ ] Controllati clearance verso RFIN/RFOUT e return path RF dopo via termici
- [ ] Definito test strumentale temperatura e alimentazione a corrente limitata

## Elettrico RF / fabbricazione

- [ ] Schema KiCad del modulo RX aggiornato alla PCB corrente; ERC e controllo parità
- [ ] DRC con zone GND riempite realmente e regole di fabbricazione del fornitore
- [ ] Stack-up PCBWay reale e soluzione CPWG 50 Ω con soldermask/copper
- [ ] Verifica BOM, sourcing SMA, assemblabilità, quote and tolerances
- [ ] Signoff documentato; solo dopo realizzare coupon RX, VNA e termica

**Finché anche solo uno dei punti bloccanti manca, NO FAB/NO PCBWAY/NO TX.**
