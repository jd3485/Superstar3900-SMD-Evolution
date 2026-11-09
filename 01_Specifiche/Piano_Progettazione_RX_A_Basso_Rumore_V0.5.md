# RX silenzioso: revisione dei requisiti V0.5

**Architettura non approvata:** preselettore RF commutato 6 bande, primo mixer ad alta dinamica, prima FI 10,695 MHz, selezione SSB/AM/FM da dimensionare, seconda FI 455 kHz (se confermata), IF gain/AGC, NB/ANL, baseband DSP opzionale. Il filtro LO deve attenuare armoniche e spurie a RFOUT; usare uscita LO e schermatura separate dal percorso antenna.

## Invarianti e rischi
- Sensibilita' senza dinamica non e' un buon risultato: bisogna misurare blocco, intermodulazione e mixing reciproco prima di definire guadagno RF.
- Un anello PLL stretto favorisce reiezione della componente reference/PLL ma lascia emergere rumore del VCO vicino ai 10 kHz; un anello largo puo' sacrificare i parametri a bassa frequenza e aumentare spurie: scelta da simulare.
- Anche LMX2572 puo' introdurre spurie/toni discreti: misura su tutti i canali, non solo centro banda.
- Separare ritorni digitali e RF senza spezzare indiscriminatamente il piano di massa. Prevedere schermature metalliche, via stitching e filtri su linee SPI.
- Alimentazioni 13,8 V -> conversione efficiente -> regolatori locali low noise; nessun dispositivo alimentato prima del controllo dei massimi da datasheet.
- Resta bloccata la trasmissione al di fuori delle 40 frequenze CB regolari, secondo i requisiti nazionali/europei e iter di conformita' ancora da dettagliare.

## Test di accettazione prototipo (non effettuati)
- Rumore di fase LO misurato a offset 100 Hz/1 kHz/10 kHz/100 kHz in 3 punti di banda (inizio, centro, fine), prima e dopo il buffer.
- Spurie LO e riferimenti fPFD; lock detect dopo cambio frequenza e richiamo CH9.
- Noise figure del ricevitore, sensibilita' AM/FM/SSB, IMD3, blocking e reiezione adiacente con sorgenti calibrate.
- Presenza di prodotti di intermodulazione del display e sintetizzatore durante ricezione, squelch chiuso/aperto e scansione.
- Misure d'uscita TX su carico 50 ohm, armoniche, sovratemperatura e ROS (solo dopo la scheda TX e approvazioni).
