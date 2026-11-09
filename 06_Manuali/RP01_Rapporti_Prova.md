# RP-01 — Rapporti di prova e di simulazione

**Stato: registro/scaletta, nessuna prova RF fisica realizzata.**

Per ogni prova o simulazione archiviare: ID; scopo/requisito; versione HW/FW e modelli; metodo; condizioni di misura; strumenti e taratura (per misure); dati grezzi; screenshot/grafici; criteri pass/fail; risultato; problemi; autore e data.

Prove previste: calcoli di filtraggio, analisi RF/phase noise, alimentazioni e termica; ERC/DRC/DFM; sensibilità e SINAD, selettività, blocking, intermodulazione, AGC, rumore audio; stabilità PLL; prestazioni AM/FM/SSB; emissioni armoniche/spurie e potenza; misura ROS/Watt; accordatore su carichi variabili; funzionalità di CH9/ALFA e blocchi TX; EMC e requisiti RED/ETSI ove applicabili.

**Al momento:** solo test di logica frequenze descritto nei registri 03_Verifiche.

## Simulazioni V0.6
Superate verifiche numeriche di 270 frequenze e 4000 campioni di modello di anello. Nessun test di laboratorio, PN, spurie, sensibilita o EMC. Registro: `03_Verifiche/Registro_verifiche_V0.6.md`.


## V1.1 - rapporto prove
Verificati solo calcoli matematici statici, confronto pin con datasheet e integrita dei sorgenti. Da fare: KiCad ERC/DRC, SPICE eventi di sovra/inversione, inrush, EMI, misure su banco, test PA e keying CW.


## V1.2 - verifiche
Test automatico di consistenza etichette e calcolo scenari nominali (rendimento ipotizzato 85%). Non effettuate verifiche elettriche native KiCad, SPICE, EMI, prove di laboratorio, termiche o surge.


## Aggiornamento V1.5
Test V1.5: statici SPI e contratti gerarchici PASS, KiCad ERC e test hardware NON ESEGUITI.

## V1.6 - Test numerici non hardware

Il test `03_Verifiche/test_dsp_control_v16.py` verifica 50 frequenze sintetiche CTCSS, alcuni casi VOX e DW. Non certifica algoritmi DCS, false aperture in ambiente reale, latenza codec, RF, conformita o qualita audio.
