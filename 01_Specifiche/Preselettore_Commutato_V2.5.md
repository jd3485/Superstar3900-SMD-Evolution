# Preselettore RF commutato: studio V2.5 (NON APPROVATO)

**Ambito**: SOLO RX 25,615–28,305 MHz, 270 posizioni, 6 bande A–F. Ogni banda contiene 45 posizioni (40 + 5 Alfa). Non modifica selettori ALFA e CH9 e non rende possibile TX sulle bande ampliate.

## Architettura studiata
Antenna (protetta e disaccoppiata dal TX; da progettare) -> commutatore a sei vie -> uno di sei filtri passivi LC -> commutatore a sei vie -> ADL5535 (studio precedente) -> comune LP7 29,5 MHz -> mixer ADE-1+.

Un ramo impiega **tre risonatori paralleli** collegati da **quattro condensatori serie** (10 elementi ideali: 3 L, 3 C in derivazione e 4 C serie). I valori sono scalati in funzione del centro banda; **il modello è relativamente largo**, non un filtro strettissimo da 440 kHz e non garantisce reiezione della banda adiacente. La commutazione resta quindi una proposta da dimostrare utile.

## Fatti modellati e ipotesi
- Dati reali di riferimento: 270 frequenze esistenti nella tabella V0.1; 6 gamme [A-F]. Frequenza immagine RF = frequenza desiderata + 21,390 MHz (LO alto e FI 10,695 MHz).
- Nel modello elettrico ABCD le bobine hanno Q costante (90 nominale; test da 45 a 120), i condensatori tan(delta)=0,001, non esistono piste, package, campi EM o perdite dielettriche PCB misurate.
- **Commutazione ipotizzata**: due dispositivi serie. Relè SMD 0,2 dB per elemento; switch SOI 0,7 dB per elemento. Le cifre **non sono parametri garantiti a 27 MHz** per i dispositivi reali.
- Il LP7 è posto **dopo** un amplificatore idealmente adattato/isolante: le reiezioni in dB sono sommate solo come stima di catena a 50 ohm, non la risposta reale montata. Non include leakage fra canali, che può limitare fortemente la reiezione effettiva.
- Per il confronto viene usato il filtro unico V2.4 Q=60 (1,614 dB inserzione; 59,3 dB reiezione). Il banco V2.5 usa Q=90 nominale, dunque **non è un confronto a parità di Q**: da verificare a pari induttore e tecnologia.

## Risultato e decisione
- Filtri ideali di banco: perdita massima ~0,87 dB per banda, minima reiezione immagine ~26-27 dB.
- Due relè SMD ipotetici: perdita anteriore max ~1,27 dB. Due SOI: ~2,27 dB. Comune LP7 post-LNA: min ~41,2 dB immagini aggiuntive solo per adattamento isolato.
- In 3.000 campioni sintetici (2% indipendente, Q distribuito uniformemente 45–120), **65,5%** degli scenari relè rispetta i criteri illustrativi (IL anteriore <= 1,5 dB; somma reiezioni >= 60 dB), **0%** degli scenari SOI. **Non è una resa produttiva**.
- **NO-GO per PCB**: non impegnare sei filtri senza verifica Q/SRF dei materiali, modelli S-parametri 27 MHz, isolamento, rapporto NF/IIP3 e prova VNA. Priorità a confrontare un unico filtro comune e un filtro per gruppi di bande, anche per evitare 2 switch serie.

## Protezioni e controlli futuri
- I sei rami sono rigorosamente RX-only; durante TX il preselector deve essere isolato, evitando che il finale trasmittente lo attraversi.
- Commutazione break-before-make e mute audio breve, stato sicuro all'avvio, vincoli CH9 e ALFA conservati.
- Verifiche necessarie: RF switch a 27 MHz, filtraggio 25,615–28,305 MHz, spurie mixer/LO, NF e IIP3, ERC/DRC KiCad, S11/S21 VNA, rumore in ricezione, sviluppo manuali.

## Riproducibilità
Eseguire `python 03_Verifiche/V2.5/filter_bank_v25.py --root .` dalla radice del progetto (numpy/matplotlib) e poi `python 03_Verifiche/V2.5/test_filter_bank_v25.py`. Elaborati: CSV risultati, 3000 casi MC, componenti ideali per banda, due grafici e JSON con ipotesi.

## Riferimenti produttori
- pSemi PE42462, scheda prodotto: https://psemi.com/products/rf-switches/high-isolation-rf-switches/pe42462/
- OMRON G6K-2F-RF, scheda famiglia: https://components.omron.com/eu-en/products/relays/G6K-2F-RF-V
- OMRON G6K-2F-RF, dato perdita a 1GHz: https://www.mouser.it/new/omron-electronics/omron-g6k-2f-rf-relays/
- Coilcraft 0805CS: https://www.coilcraft.com/en-us/products/rf/ceramic-core-chip-inductors/0805-%282012%29/0805cs/
