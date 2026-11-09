# Ricevitore RF - Prima rete preselettrice V2.2

**Stato: STUDIO ANALITICO / NON COSTRUIRE / non montare sulla PCB.**

Gamma RX **25,615-28,305 MHz**. Prima FI proposta 10,695 MHz, iniezione alta LO 36,310-39,000 MHz. Frequenze immagine **47,005-49,695 MHz**.

## Topologia studiata
Cin - 5 risonatori LC paralleli a massa, accoppiati da capacita' C12/C23 - Cout - passa-basso Chebyshev 7 poli (0,3 dB, fc 31,0 MHz) - uscita da 50 ohm.

Cin/Cout = 129.37 pF; C12/C45 = 30.41 pF; C23/C34 = 11.57 pF. Cinque induttori da 330 nH; Cedge = 55.69 pF, Cintermedio = 70.34 pF, Ccentrale = 83.89 pF. Valori **numerici ottimizzati** non normalizzati E-series, da NON assegnare ancora ai footprint.

## Risultati modello Q50
- Minimo S21 25,615-28,305: **-4.52 dB**.
- Peggior S21 sulle immagini: **-68.95 dB**.
- Monte Carlo 500 casi ±5% L, ±2% C, Q_RF uniforme 30-70 e Q_LPF uniforme 40-70: **399/500** rispettano S21 banda >= -6 dB e immagini <= -60 dB. NON e' rendimento produttivo reale.

**Punto critico:** circa 4,5 dB di perdita prima dell'LNA/mixer consuma quasi tutto il budget di rumore di 6 dB. NON si e' ancora trovato il miglior compromesso fra sensibilita', immunita' alle immagini e intermodulazione; testare filtro distribuito prima/dopo LNA, bypass e singoli filtri per sottobande.

## Componenti candidati
L'induttore Coilcraft 1008CS-331X_R_ 330 nH SMD ha valore specificato a 25 MHz e frequenza di autorisonanza minima dichiarata 570 MHz; Q minimo 45 e' **misurato a 100 MHz**, quindi NON puo' essere assegnato automaticamente a 27 MHz. Dati ufficiali: https://www.coilcraft.com/getmedia/9b59774c-05d4-40c5-99c9-417bb8e881ea/1008cs.pdf . Nessun componente viene marcato come confermato per assemblaggio.

## Verifiche mancanti prima del layout
1. Estrarre modelli S-parametro reali dei componenti e verificare Q a 27 MHz, SRF e tolleranze.
2. Simulare risposta S11/S21 con reti complesse, parasitismi e tecnologia PCB reale (fino a 6 bande).
3. Ripartire la selettivita' sui due lati dell'LNA per mantenere NF e grande dinamica.
4. Validare con VNA, analizzatore di spettro, generatore RF calibrato e misure d'NF.
5. Verificare spurie e TX-vs-RX switching. ERC/DRC nativi KiCad e simulazione SPICE non eseguiti.

## Riproducibilita'
`python 03_Verifiche/V2.2/rf_preselector_v22.py` aggiorna report JSON, CSV e immagini. Il netlist `.cir` e' un *modello di studio non ancora simulato in ngspice*.
