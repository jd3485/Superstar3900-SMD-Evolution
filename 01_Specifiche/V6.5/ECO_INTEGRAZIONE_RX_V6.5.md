# ECO interconnessioni V6.5 — integrazione V5.8/V6.0/V6.1/V6.2/V6.3/V6.4

- RX della V5.8: non modificare PCB del test 50 Ω; il modulo J501 richiede uscita 50 Ω qualificata della catena RX, non un collegamento inventato a un pad già esistente. Filtro immagine da collocare prima di U501, verificare se meglio prima/dopo ADL5535 nel bilancio blocker.
- PLL V6.4: J402 → J502, LO +7dBm sul pin U501. I pin LMX esistenti non cambiano. Rete/driver/filtro LO BLOCCANTE per la realizzazione; non contare due volte corrente PLL su V6.3.
- Supervisore MCU V6.1 e PLL V6.4: solo dopo lock stabile e PA non attiva, abilita IF audio; selezione del banco filtri IF ancora da assegnare su MCU (risorsa pin da riesaminare).
- PA V6.0 e interblocco V6.2: sempre RX muted durante PA, TX non disponibile e nessuna uscita RF TX; non utilizzare TX-permitted del piano storico.
- Alimentazioni V6.3: ADE-1+ mixer passivo senza rail proprio, ma stadi U502/U503 non sono stati dimensionati; budget alimentazione da aggiornare soltanto quando sono scelti.
- Collegamento audio V6.0: la FI 10,695 MHz **non è un segnale audio**; serve demodulazione e conversione a banda base PRIMA di TMUX1308. Non collegare FI direttamente all'ingresso audio.

**STATO: NESSUNO DEI BLOCCANTI QUI SOPRA CONFERISCE FAB APPROVAL.**
