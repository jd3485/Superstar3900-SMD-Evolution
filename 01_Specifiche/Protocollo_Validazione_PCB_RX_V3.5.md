# V3.5 - Protocollo verifica sperimentale del coupon RX 50 ohm

**Non collegare ad un trasmettitore.** RX-only: la protezione TX/RX resta fuori dal coupon.

1. Scaricare dal produttore il CAD 3D + land pattern REV D del connettore TE CONSMA002-SMD. Confermare la lavorazione del feature circolare Ø2.05 mm e l'orientamento rispetto al bordo della PCB prima di modificare i fori/pad.
2. Aprire la scheda KiCad V3.5; controllare gerarchia schematico-vs-PCB per assegnazione di pin, footprint e netlist. Rigenerare da schematico in KiCad e verificare i diff.
3. Verificare pad ADL5535 Figure 17 su un modello 3D; distanze, soldermask, stencil del paddle e via di ritorno GND esterni alle piazzole.
4. Ottenere lo stack-up PCBWay effettivo: dielettrico L1-L2, Dk effettivo RF, copper finito, soldermask. Risolvere con field solver microstrip 50ohm e approvare fab tolerance.
5. Rifare il routing con T-branch controllati e i due resistori shunt. Preferire percorsi brevi e piani continui su L2. Fill delle zone e stitching GND.
6. Eseguire KiCad ERC + DRC con i parametri di PCBWay, correggere **ogni** errore. Il controllo geometrico Python incluso non li sostituisce.
7. Ispezionare i Gerber in CAM e fare revisione meccanica indipendente; solo dopo considerare un ordine PCBWay di prova.
8. Test da banco con generatore a potenza limitata e bias 5V con corrente max 0.20 A: prima i corti, poi consumo, S11/S21 20-60 MHz, misura risposte, guadagno a 27 MHz e termica. Nessun RF TX applicato al coupon.

Criteri di accettazione degli strumenti e soglie quantitative sono ancora da ratificare dopo caratterizzazione VNA e target del sistema.
