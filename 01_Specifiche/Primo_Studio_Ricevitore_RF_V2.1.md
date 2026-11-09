# Studio ricevitore RF - fase iniziale V2.1

**Stato:** parametri derivati algebricamente, non prestazioni validate.

Ricezione richiesta: 25.615-28.305 MHz (270 posizioni RX). Prima FI candidata: 10.695 MHz. Con iniezione alta: LO = RF + FI => 36.310-39.000 MHz. La risposta immagine appare a LO+FI => 47.005-49.695 MHz, cioe' 21,390 MHz sopra la stazione desiderata.

L'ingresso RF dovra' usare un preselettore da dimensionare e provare; il semplice filtro a ingresso largo non fornisce automaticamente la reiezione richiesta. Target ipotizzato: >=60 dB attenuazione immagine. Un filtro troppo dissipativo degrada figura di rumore, mentre un LNA ad alto guadagno puo' peggiorare la tenuta ai segnali forti. Il circuito finale richiede un trade study NF/IIP3 e misure VNA/analizzatore.

## Budget indicativo sensibilita'

Con segnale 0,2 uV RMS su 50 ohm: -120.97 dBm. Rumore termico ideale su 2,4 kHz, assumendo -174 dBm/Hz: -140.20 dBm. Per un SNR di 10 dB rimangono 9.23 dB come figura di rumore massima *equivalente nel modello semplificato*. Per progetto si propone NF <=6 dB con margine, **senza dichiarare sensibilita' raggiunta**.

## Sottosistemi da costruire

1. Filtri di preselezione ad alta dinamica e comando della banda.
2. Attenuatore commutabile e/o LNA con protezione ESD e T/R.
3. Primo mixer, livello del LO verificato per P1dB e IP3.
4. Filtraggio della FI 10,695 MHz e percorso modulazioni AM/FM/SSB/CW.
5. Catena a 455 kHz se mantenuta, o FI alternativa se scelta in analisi.
6. Misure previste: NF, IP3, blocking, image rejection, spurie, sensibilita' per demodulazione, AGC, NB/ANL e protezioni TX.

Vincolo progettuale: trasmissione consentita solo dove autorizzata, con interblocchi di sicurezza hardware/software. Frequenze espanse al di fuori della CB restano RX.
