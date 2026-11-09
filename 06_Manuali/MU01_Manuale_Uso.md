# MU-01 — Manuale d'uso

**Stato: struttura, da confermare dopo il progetto del pannello e del firmware.**

1. Sicurezza, alimentazione, antenna e vincoli di utilizzo e trasmissione.
2. Descrizione pannello, comandi e connettori.
3. Accensione, volume, squelch, RF gain, microfono.
4. Bande A–F e 40 canali, comando fisico ALFA separato, frequenzimetro.
5. CH9: priorità, modalità AM e ripristino impostazioni originali.
6. Modalità AM, FM, USB, LSB e sintonia fine/clarifier.
7. Letture misuratori: frequenza, watt medi/PEP, ROS e modulazione.
8. Accordatore: connessione, bypass, accordo manuale/automatico, memorie, allarmi.
9. NB/ANL, DSP audio disattivabile, filtri e gestione ricezione difficile.
10. Protezioni: sovratemperatura, ROS elevato, interblocco canale TX, PLL unlocked.
11. Cosa fare in caso di problemi, manutenzione e cura dell'apparato.
12. Appendici: tabella frequenze, specifiche comprovate e glossario.

Le procedure operative definitive saranno basate sul dispositivo collaudato, non su funzioni solo proposte.


## Comandi di frequenza - descrizione provvisoria V0.2
Il selettore BAND scegliera A..F e CHANNEL 1..40. L'interruttore ALFA separato applica +10kHz solo nelle posizioni 3,7,11,15,19, senza effetto altrove. CH9 ON forza 27,065MHz AM e ha priorita sui comandi, CH9 OFF ripristina la selezione fisica preesistente. Le 270 posizioni sono previste in ricezione; la trasmissione sara inibita fuori dalla banda legalmente prevista e in caso di protezioni attive. Nessuna interfaccia fisica e ancora realizzata.


## V1.1 - funzioni richieste CW e PA (in progetto)
CW: ricezione telegrafica, filtro stretto, sidetone e presa key. CW TX restera disabilitato salvo verifica legale e progettuale. PA: amplificazione del microfono all'altoparlante esterno con interblocco che impedisce ogni trasmissione RF durante PA. I dettagli dei comandi saranno definiti quando hardware e software esisteranno.


## Aggiornamento V1.5
Frequenzimetro / selezione canali / display ancora da progettare; nessuna procedura operativa validata.


## V1.5.1 - Nuove funzioni da implementare (manuale NON operativo)
- **VOX**: attivazione a voce, sensibilita e ritardo di sgancio; il PTT resta disponibile, senza possibilita di scavalcare gli interblocchi RF.
- **DW / Doppio ascolto**: alternanza tra canale A e B con un solo ricevitore; quando si risponde in TX il canale di destinazione rimane A.
- **Roger Beep**: tono breve di fine comunicazione, disinseribile; automaticamente escluso su CH9 e PA.
- **Echo**: effetto voce TX regolabile e bypassabile, solo AM/FM/USB/LSB; escluso su CH9.
- **CTCSS / DCS**: in FM soltanto, TX e RX selezionabili separatamente; 50 toni CTCSS, 104 codici DCS N/I come obiettivi; OFF per default. Non danno privacy.
Questa sezione descrive i requisiti, **non le istruzioni di un circuito gia costruito**.

## V1.6 - Comandi DSP in progetto

VOX con soglia e tempo di rilascio, DW con canale A prioritario per TX, Roger Beep, Echo disinseribile, selezione CTCSS/DCS solo in FM. Tutte le funzioni restano in sviluppo, senza prestazioni o menu garantiti.
