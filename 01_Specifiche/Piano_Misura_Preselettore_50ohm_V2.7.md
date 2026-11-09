# Procedura VNA e piano prototipo a 50 Ohm - studio V2.7

**Sicurezza:** circuito di sola ricezione; NON applicare potenza di trasmissione al prototipo filtro. Connettere il DUT a VNA con potenza di prova ridotta (es. -20 dBm), isolato dalla trasmittente.

1. Stampare una test-board RF 50 Ohm con due connettori SMA, massa continua, via stitching e spazio separato per HP5 e LP9, jumper di bypass, impronte 0805 (L) e 0603 (C). Il board non e' ancora progettato in KiCad.
2. Registrare calibrazione SOLT completa alle estremita' del cavo (o TRL con coupon adeguati); effettuare controllo thru 50 Ohm; salvare data, potenza, IFBW e piano di riferimento.
3. Acquisire S11 e S21 complessi a 401-1601 punti su 5-70 MHz; salvare Touchstone .s2p con impedenza di riferimento 50 Ohm. Riportare peggiore perdita 25,615-28,305 MHz, reiezione minima 47,005-49,695 MHz e S11 peggiore in banda.
4. Ripetere con HP5 isolato e LP9 isolato, poi cascata; se possibile usare fixture de-embedding Open/Short e confrontare l'effetto delle piste.
5. Misurare almeno tre esemplari di induttore per ciascun valore (270, 330, 560 nH), con fixture dedicata; usare R_ac e L_ac a 27 MHz e Q = |Im(Z)|/Re(Z) dopo rimozione parassiti di fixture. Non estrapolare il Q @50/250MHz.
6. Ripetere a temperatura ambiente, dopo riscaldamento operativo e a tensione di ingresso nulla per il filtro passivo; annotare dispersone e deriva.
7. Verificare la risposta del filtro con l'LNA reale: impedenze ingresso/uscita e trasporto segnale; poi misurare figura di rumore e due-toni IIP3 su ricevitore completo.

**Gate prima della release RF:** conferma di MPN e footprint di tutti i componenti, dataset S2P o misura VNA, perdita nell'intera banda RX <= 1,5 dB (target provvisorio), reiezione immagini >= 60 dB, return loss >= 10 dB come soglia esplorativa; test realistici con componenti in tolleranza; ERC/DRC e test prototipo.

L'assenza di una misura NON si sostituisce con un PASS da test software.
