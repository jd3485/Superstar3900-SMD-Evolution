# V3.4 - Piano PCB sperimentale RF 50 ohm

## Stato reale
Il file `.kicad_pcb` include i 15 footprint preesistenti, 3 zone GND_RF **definite ma non riempite**, 2 via GND di studio e i nomi delle 8 reti. Non contiene piste di segnale. **NON PRODURRE.**

## Criticità bloccanti
1. Il footprint provvisorio dei quattro SMA `CONSMA002-SMD` NON è approvato. Nel disegno del produttore è quotato un elemento circolare centrale di diametro 2,05 mm; il tipo di lavorazione (pad, foro o entrambi) deve essere confermato sul disegno CAD ufficiale prima di modificare il footprint. Scaricare e verificare il modello CAD ufficiale TE.
2. Il footprint SOT-89 dell'ADL5535 e il pad termico non sono ancora conformati esattamente alla figura 17 del datasheet. Non usare via-in-pad non tappati sotto il pad di saldatura. I due via esterni sono soltanto una prima indicazione.
3. Il lato L1 deve avere ritorno GND continuo vicino ai microstrip; L2 piano massa senza tagli; L3 alimentazione e massa; L4 massa e servizi. Il riempimento delle zone va effettuato in KiCad con DRC.
4. Nessuna pista a 50 ohm è ancora stata disegnata. Calcolo di larghezza V3.4 e' preliminare: dipende dal rame finito, dalla solder mask e dallo stack-up PCBWay scelto.
5. Rete di protezione TX/RX non presente: usare esclusivamente generatore a bassa potenza/strumenti di misura da banco, **mai collegare a trasmettitore o antenna con trasmissione attiva**.

## Parametri da chiedere al fabbricante prima del routing
- Stack-up di 4 strati, 1,6 mm, L1-L2, spessori rame finiti, epsilon_r e soldermask;
- Servizio di controllo impedenza 50 ohm: larghezza proposta e tolleranza effettiva;
- Specifica via min e distanza via-pad;
- Orientamento e fori del connettore SMA, stencil e fixture.

## Prove da eseguire
A. Confrontare footprint con package drawings ufficiali, in 3D e sulla scheda.
B. Completare connessioni e piani massa, ERC/DRC nativo KiCad senza errori bloccanti.
C. Preparare Gerber provvisori solo dopo DRC, quindi controllo CAM e revisione indipendente.
D. Assemblare un coupon RX e misurare VNA S11/S21, guadagno a 27 MHz, comportamento da 20 a 60 MHz e corrente a 5V (limitazione di corrente attiva).

### Fonti
- Analog Devices ADL5535 Rev. A, Figure 16 e 17: https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf
- TE/Linx CONSMA002-SMD, Product Drawing Rev. D: https://www.te.com/en/product-CONSMA002-SMD.html
- PCBWay Stack-up, struttura quattro strati: https://www.pcbway.com/multi-layer-laminated-structure.html
