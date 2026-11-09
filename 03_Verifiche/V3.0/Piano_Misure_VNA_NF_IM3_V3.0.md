# Piano di verifica V3.0 — prova RX

1. Preselettore passivo su coupon con connettori da 50 ohm: VNA calibrato SOLT, S11/S21 misurati da 1 a 70 MHz, con attenzione a 25.615–28.305 MHz, 47.005–49.695 MHz e 1–20 MHz; misura su almeno più campioni per tolleranze.
2. ADL5535 su circuito di valutazione: alimentazione 5V filtrata, corrente nominale 97mA tipica e dissipazione ~0.485W da controllare; misura di NF, guadagno, S11/S22 a 27 MHz e temperatura.
3. Mixer ADE-1+: verificare potenza LO al suo connettore RF (+7dBm nominale), spurie e isolamento; prova a due toni a potenze di ingresso progressive con analizzatore spettro e attenuatori; mai connettere a trasmettitore durante esperimenti.
4. Ripetere NF, due toni, IM3 e ricezione con LNA on / post-pad / bypass; includere segnali fuori banda di grande ampiezza.
5. Calibrare, salvare file Touchstone reali, foto del setup, numeri seriali degli strumenti e report firmato del collaudo. Confrontare le curve misurate con le curve **simulate** V2.9 e V3.0.
6. Solo dopo la validazione RF passare a layout PCB RX integrata. Non utilizzare la percentuale di avanzamento come certificazione di conformità o prestazioni.
