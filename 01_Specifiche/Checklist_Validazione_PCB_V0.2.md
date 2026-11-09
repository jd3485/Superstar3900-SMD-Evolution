# Gate di verifica per prototipo PCB - bozza V0.2

## G0 - Specifiche
[ ] Misure contenitore frontale e fissaggi; [ ] topologia RF scelta; [ ] BOM MPN/fonti; [ ] target dinamica e NF definiti; [ ] vincoli normativi chiariti.

## G1 - Schematici reali
[ ] Schemi KiCad con componenti/footprint corretti; [ ] punti misura e connettori verificati; [ ] ERC chiuso; [ ] alimentazioni dimensionate e protette; [ ] pinout incrociato con datasheet; [ ] TX hard interlock progettato.

## G2 - Simulazioni
[ ] L-C reti passabanda RF/IF e immagine; [ ] PLL loop e phase-noise/spur budget usando software adatto; [ ] guadagno/NF, risposta AGC e sovraccarico; [ ] ATU su matrice di carichi; [ ] potenza armoniche e filtro PA; [ ] SPICE alimentazione e protezioni. **Non attribuire risultati prima che siano eseguiti.**

## G3 - PCB
[ ] 4-layer stackup confermato; [ ] DRC; [ ] footprint/dimensioni/thermal pad; [ ] percorsi RF e ritorni; [ ] schermature e vias; [ ] simulazione EM dove necessaria; [ ] controlli impedenza e isolamento; [ ] posizione relè, toroidali, dissipatore, connettori e frontale.

## G4 - Dati produttore
[ ] Gerber e file foratura visualizzati; [ ] DFM PCBWay; [ ] BOM/CPL validati; [ ] pin1 e polarita; [ ] substitute policy; [ ] disegno assemblaggio; [ ] controllo differenze versioni; [ ] checksum manifest e approvazione ordine.

## G5 - Lab RF e conformita
[ ] Prima accensione DC limitata; [ ] PLL su carico attenuato; [ ] misure fase/spurie; [ ] RX sensibilita, blocking, IMD, selettivita; [ ] TX solo carico fittizio 50ohm con verifica spurious, power, modulation; [ ] termica PA; [ ] ROS e ATU; [ ] test fault injection; [ ] verifiche requisiti RED/ETSI/nazionali con esperti e strumenti.

**La validazione software non equivale a un'omologazione o a un nulla osta di emissione.**
