# S3900E — Protocollo collaudo modulo RX 50 Ω (V3.6)

**STATO: STUDIO, NON ANCORA FABBRICABILE.** Questa procedura non dichiara misure già effettuate. Vale soltanto per un futuro prototipo isolato dalla catena TX. Non applicare RF di potenza o collegare il trasmettitore alla scheda.

## Prima della fabbricazione (obbligatorio)

1. Aprire il file `.kicad_pcb` V3.6 con una versione KiCad che lo supporti. Confermare che si apra senza errori e che i 15 footprint e 43 segmenti siano presenti. Confrontare fisicamente l'SMA TE/Linx CONSMA002-SMD, in particolare la caratteristica Ø2.05 mm, la posizione dei quattro contatti esterni, orientamento, bordo, overhang e disegno di foratura. NON dedurre il foro dallo schema 2D senza conferma meccanica/CAD.
2. Verificare ADL5535 Rev. A, figura 17, con land pattern ufficiale e stencil; il paddle e Pin 2 sono GND. Verificare l'induttore L101 pin 2 lato RFOUT + bias e pin 1 lato +5 V, come nello schema V3.1.
3. Richiedere a PCBWay lo stack-up effettivamente ordinabile (h L1-L2, DK, rame finito, soldermask), calcolare la microstriscia 50 Ω con field solver e aggiornare le piste.
4. Riempire TUTTE le zone di rame KiCad sui quattro layer, verificare il collegamento dei via, i ritorni di massa e l'assenza di frammentazioni della massa In1.Cu.
5. Eseguire ERC sullo schema, aggiornare netlist e footprint, eseguire DRC completo incluse clearance/soldermask/courtyard/annular ring/unconnected; risolvere ogni errore, rivedere tutti i warning.
6. Controllare l'allineamento 3D meccanico e la polarità/corrispondenza della BOM, poi produrre Gerber e file di foratura solo dopo il via libera.

## Misure di laboratorio — SOLO dopo realizzazione e ispezione

| Sequenza | Stato iniziale | Misura/metodo | Annotare |
|---|---|---|---|
| 1 | Modulo non alimentato, non collegato a TX | Ispezione visiva microscopica, corti DC rail vs massa, continuità GND | esiti e resistenze |
| 2 | 5.00 V da alimentatore protetto, limite indicativo 200 mA | Corrente DC, riscaldamento, assenza di oscillazioni evidenti | corrente mA, temperatura °C |
| 3 | Sezione attenuatore passiva separata, VNA calibrato SOLT | S11/S21 su 20–60 MHz e dettaglio 25.615–28.305 MHz | S11, S21 (atteso da modello resistivo circa -6.01 dB nominale) |
| 4 | ADL5535 alimentato, VNA in modalità a basso livello (es. -45 dBm iniziali) | Guadagno e return loss su 20–60 MHz, dettagli 25.615–28.305 MHz | S11/S21, ripple, corrente |
| 5 | Sempre RX e con alimentazione isolata dalla TX | Verifica di stabilità a ingresso terminato, analizzatore spettro | frequenze spurie, picchi, offset |
| 6 | Misure dopo certificazione di protezione strumentale | Figura di rumore, IIP3 con due toni a livelli sicuri e instradamento schermato | livelli, Δf, taratura, incertezza |

N.B.: il datasheet ADI riporta a 20 MHz guadagno tipico 16.7 dB e corrente tipica 97 mA; non trattarli come criteri garantiti a 27 MHz senza caratterizzazione. La scheda di test non contiene T/R switch, filtro TX né protezione sufficiente per connetterla al trasmettitore.

## Provenienza

- Analog Devices ADL5535 Rev. A pp. 11 e 15: https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf
- TE/Linx CONSMA002-SMD Rev. D: https://www.te.com/en/product-CONSMA002-SMD.html
- PCBWay riferimento standard 4 strati: https://www.pcbway.com/multi-layer-laminated-structure.html
