# Piano di costruzione per revisioni successive — priorità alla RADIO COMPLETA

La nuova sequenza non è una promessa di fabbricazione: ciascuna revisione deve aggiungere elaborati di progetto reali, senza rimandare ogni volta al solo DRC.

| Prossima revisione obiettivo | Sottosistema da dettagliare | Elaborati da aggiungere | Stato iniziale |
|---|---|---|---|
| V6.0 | Audio/PA completo | schema componenti, livelli, mux RX, mute, ampli, BOM, connessioni | da fare |
| V6.1 | MCU / pannello e strumenti | matrici GPIO/pin, selettori, CH9/ALFA, LCD, frequenzimetro, ADC strumenti | da fare |
| V6.2 | Alimentazioni / interblocco HW TX | rail, assorbimenti, protezioni, gate indipendente, sequenza e watchdog | da fare |
| V6.3 | Sintetizzatore / BFO | LMX2572, TCXO, LO buffers, distribuzione, filtro PLL, moduli RX/TX | da fare |
| V6.4 | FI / demodulazione RX | filtro FI, 455 kHz se adottata, AGC, rami AM/FM/SSB/CW | da fare |
| V6.5 | TX IF / conversione | modulazione AM/FM/SSB, filtri immagini e gain budget, default disabilitato | da fare |
| V6.6 | Finale TX / armoniche | drive, PA, polarizzazione, LPF, controllo fisico e termica | da fare |
| V6.7 | ATU / SWR / PEP | rilevatori, reti L/C, relè, calibrazione e misura | da fare |
| V6.8 | PCB, cablaggi e meccanica radio completa | schede e connettori pin-numerati, pannello, dissipazione, schermature | da fare |
| V6.9 | Firmware e documentazione finale di progettazione | software MCU target, manuali, BOM consolidata, tracciabilità | da fare |
| DOPO progetto completo | RIESAME / SIMULAZIONI / KICAD | ERC/DRC reali, simulazioni RF/audio/power/termica, prototipi | programmato dopo |

**Questa tabella è un piano indicativo, non una dichiarazione di completezza né un divieto di correggere errori trovati prima.** In caso di dipendenza progettuale fra moduli, le revisioni possono cambiare ordine. Se si scopre una contraddizione o rischio durante la progettazione, si corregge subito; le campagne sistematiche di validazione restano successive.

**Obiettivo di completezza progettuale:** ogni modulo ha schema con valori e MPN candidati, connettori pin numerati, controllo I/O e power budget, componenti e software associati; ogni requisito radio ha un responsabile e una verifica pianificata. Solo allora si dichiara 'DESIGN COMPLETE, UNVERIFIED' e si avvia la fase di validazione.
