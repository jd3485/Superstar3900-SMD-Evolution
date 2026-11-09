# ECO V7.0 — sovrapposizione e non sostituzione dello storico

1. **D991, B991, B992 della V6.9 NON MONTARE** se è attiva la nuova coppia U7101/U7102/U7103 della V7.0. Non è una revisione silenziosa delle vecchie netlist: eventuali connessioni conflittuali devono essere riconciliate nei futuri schemi KiCad.
2. **F823, F824 della V6.8 NON MONTARE**: nessun filtro fisico 455 kHz SSB 2.4k / CW 500Hz disponibile/qualificato confermato; FIR SSB/CW postdemod a 48kHz è la sola soluzione selettiva implementata e testata in questa versione. Questo NON sostituisce il filtraggio prima dell'AGC.
3. R7104 = terminazione 1.5k FM **DNP** finché si conosce la terminazione già montata della F821. Q7101 = opzione DNP; l'AM ENB richiede consenso indipendente dall' MCU realmente cablato. R7102 rende ENB OFF senza J7102. U7103 INH OFF senza consenso Q7102.
4. **U7121 GALI-3+**: esercita ~35 mA dal nuovo rail 5V_A_RF (non incluso nel vecchio budget V6.3). Alimentazione 3.3V_A_IF per AD8307/4046/TLV3201/TLV9062 da dimensionare. Per il LO2 il modello predice +6.7dBm solo assumendo 22.4dB di guadagno misurato dal costruttore a **100 MHz**, NON a 10.24MHz. Prima di collegare l'uscita LO di U802 serve verifica livello/spur, fase, riflessione 50Ω e termica.
5. Lo **schema KiCad non è ancora stato generato**: i fogli V7.0 sono una netlist a componenti e un contratto di montaggio. ERC/DRC, modelli IC SPICE, simulazioni RF EM e test hardware non sono superati.
6. **TX e produzione rimangono disabilitate.** I connettori J7101/J7103/J7122 descrivono contratti candidati; non sono cablaggi già funzionanti. 
