# V2.4 - Studio preselettore RF a 50 ohm (NON APPROVATO)

**Obiettivo di progetto:** perdita di inserzione all'ingresso <=1,5 dB in 25,615-28,305 MHz; reiezione della frequenza immagine >=60 dB su 47,005-49,695 MHz. I due obiettivi sono requisiti, non risultati garantiti.

Il confronto include due possibili sottosezioni: passa-alto Butterworth a 5 poli (fc=18 MHz) per bloccare i segnali a bassa frequenza, seguito da passa-basso Chebyshev a 7/9/11 poli (fc=29,5 MHz, ripple=0,1 dB), entrambi terminati a 50 ohm. Sono stati confrontati anche i tre passa-basso da soli. La cascata NON e' un BPF sintonizzato di 6 bande.

## Risultato candidato HP5 + LP9

| Parametro | Modello Q_L=60 | Modello Q_L=35 |
|---|---:|---:|
| Perdita massima nella banda RX | 1.61 dB | 2.55 dB |
| Reiezione minima nella banda immagine | 59.3 dB | 59.5 dB |
| S11 peggiore nella banda RX | -12.5 dB | -13.0 dB |

Il modello nominale non raggiunge simultaneamente i due obiettivi principali (1,5 dB e 60 dB). **Nessuna approvazione per PCBWay**.

## Monte Carlo riproducibile

1200 scenari, seed 390024. Componenti indipendenti uniformi entro +/-2%; singolo Q equivalente uniforme in [25,75] per scenario. Criteri esplorativi meno severi: perdita <=2 dB, immagine >=55 dB. Frazione di scenari che li rispettano: 54.7%. 95° percentile della perdita: 3.10 dB. 5° percentile della reiezione: 58.7 dB.

Questa non e' una previsione statistica del rendimento di lotti reali; i limiti di Q e tolleranza sono ipotesi di stress test e non provengono da una BOM qualificata.

## Verifiche fisiche mancanti

- Valutare induttori ad alto Q **alla frequenza di 27 MHz**, tenendo conto del massimo DCR, SRF, accoppiamento magnetico e parassiti di package/pad; misurare o importare file Touchstone S-parameter reali per L e C.
- Inserire rete di matching e limitatore ESD di antenna compatibili con TX/RX; controllare il mismatch tra i due filtri in cascata.
- Validare il comportamento per forti segnali a bassa frequenza e le condizioni di bypass LNA / attenuatore, anche in presenza di spurie del LO.
- Considerare alternative più adatte: preselettore commutato per sottobande (6 bande) oppure pochi poli a bassissima perdita prima dell'LNA e ulteriore reiezione dopo LNA, verificando IIP3 e figura di rumore dell'intera catena.
- Simulare con modelli produttore e layout EM, poi eseguire VNA (S11/S21) e test su segnali deboli e forti. Un modello ABCD non sostituisce questi test.

## Riproducibilità

Eseguire `python 03_Verifiche/V2.4/rf_preselector_v24.py --output 03_Verifiche/V2.4` e `python 03_Verifiche/V2.4/test_rf_preselector_v24.py`. La netlist `.cir` e' una derivazione da verificare in un simulatore SPICE reale (non eseguito qui).

## Riferimenti tecnici

- Coilcraft, 0805HP SMD high-Q inductors (Q specificato a una frequenza di test; non estrapolare Q=60 a 27 MHz): https://www.coilcraft.com/en-us/products/rf/ceramic-core-chip-inductors/0805-%282012%29/0805hp/
- Mini-Circuits, rumore a cascata front end: https://blog.minicircuits.com/noise-and-signal-to-noise-ratio-snr-in-a-simple-microwave-front-end/
- Mini-Circuits, scelta LNA e formula Friis: https://blog.minicircuits.com/choosing-an-lna-for-your-receiver-front-end/
