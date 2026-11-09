# Superstar 3900 SMD Evolution
## MU-01 - Manuale d'uso illustrato, BOZZA V4.0
**Data:** 8 novembre 2026 | **Stato:** specifiche, non apparecchio collaudato | **Produzione:** NO FAB / NO PCBWAY

> ATTENZIONE: manuale di un progetto sperimentale. Il pannello qui schematizzato e' concettuale. Non connettere il PCB di prova a un trasmettitore.

## 1. Scopo del manuale
La radio definitiva non esiste ancora come prodotto verificato. Questo testo e' una guida progettuale per validare comandi, schermate e sicurezza prima di fissare il pannello e il firmware. Nessuna procedura qui descritta autorizza TX o uso su antenna.

## 2. Identita' e principali funzioni
Aspetto ispirato al Superstar 3900 storico; comandi fisici preferiti, elettronica prevalentemente SMD. RX in 270 posizioni su 6 bande A-F, modalita' AM/FM/USB/LSB/CW, PA separata. Funzioni future: NB/ANL, DSP audio bypassabile, VOX, Dual Watch, Roger Beep, Echo, CTCSS/DCS e accordatore automatico ATU.

## 3. Sicurezza e alimentazione
Alimentazione nominale prevista 13,8 V CC, protezione da inversione polarita', disturbi e temperatura ancora da validare. Vietato collegare il coupon RX V3.8 al trasmettitore. Non usare un prototipo TX senza verifiche elettriche, EMC e di conformita' normativa. La ricezione estesa non attribuisce diritti di trasmissione.

## 4. Pannello: legenda preliminare
VOLUME/POWER: accensione e livello audio. SQUELCH: soglia di silenziamento. RF GAIN: attenuazione/guadagno RX. BAND: A-F. CHANNEL: 1-40. ALFA: switch fisico, +10 kHz solo su 3/7/11/15/19. CH9: forzatura AM 27,065 MHz. MODE: AM/FM/USB/LSB/CW/PA. CLARIFIER: sintonia fine RX (intervallo da definire). DISPLAY: frequenza e stato blocchi. NB/ANL, DSP, DW, VOX e ATU: comandi/menù da progettare; layout non congelato.

## 5. Accensione e ricezione - procedura prevista
1) Verificare alimentazione conforme e collegamenti passivi. 2) Accendere e regolare VOLUME. 3) Scegliere BAND e CHANNEL; controllare il display. 4) Selezionare AM/FM/USB/LSB o CW. 5) Regolare SQUELCH, RF GAIN e filtro audio; non considerare il silenzio una conferma del corretto funzionamento RF. Procedura dimostrativa: non ancora testata su hardware.

## 6. Bande, ALFA e canali
Le sei bande comprendono ciascuna 40 posizioni normali e 5 ALFA (3A, 7A, 11A, 15A, 19A). Quando l'interruttore ALFA e' ON su tali canali, viene aggiunto +10 kHz; su tutti gli altri canali e' inattivo. CH23/CH24 seguono la tabella storica e non sono in sequenza crescente. La tabella completa di 270 posizioni e' in appendice.

## 7. CH9 prioritario
Inserendo CH9 il ricevitore e' portato a 27,065 MHz AM e sospende Dual Watch, Echo, Roger Beep e subtoni. Disinserendolo si torna ai comandi fisici precedenti. CH9 non scavalca le protezioni; non e' un canale di emergenza garantito in tutti i territori o un permesso TX.

## 8. Modalita' operative
AM: modulazione di ampiezza. FM: modulazione di frequenza e, se previsti, subtoni CTCSS/DCS. USB/LSB: bande laterali per SSB. CW: ricezione telegrafica con filtro stretto e sidetone previsto; CW TX bloccata nel modello. PA: percorso microfono-verso-altoparlante esterno con RF TX sempre disabilitata. Interfacce finali da definire.

## 9. VOX, Dual Watch, Roger Beep ed Echo
VOX: avvio PTT logico da voce con soglia e hang-time, subordinato a interblocchi; prevenire autoinneschi da altoparlante. Dual Watch: ricevitore singolo alterna A/B, non ascolto simultaneo; si trasmetterebbe sempre sul primario A, mai automaticamente sul secondario B. Roger Beep: segnale di fine TX prima del rilascio, non in CH9/PA. Echo: effetto sulla voce trasmessa, bypassabile, non in CH9/PA. Tutti da collaudare.

## 10. CTCSS e DCS
Solo FM: obiettivo 50 toni CTCSS e 104 codici DCS con polarita' N/I, TX e RX indipendenti, OFF per impostazione iniziale. Non sono sistemi di cifratura e non garantiscono privacy. L'interfaccia deve evitare conflitti CTCSS/DCS sullo stesso ramo. Tabelle codici e test di interoperabilita' da completare.

## 11. Strumenti e accordatore
Indicazioni progettate: frequenza, potenza media, PEP, SWR/ROS, modulazione e strumento analogico. Per ATU sono previsti BYPASS, accordo automatico, regolazione manuale/memorie ipotizzate e protezione SWR. Nessuna misura e' stata calibrata e nessuna procedura di accordo TX e' autorizzata su hardware inesistente.

## 12. Interblocchi e messaggi
Blocco TX previsto se posizione TX non permessa, modo CW, PLL sbloccato, interblocco hardware assente, alimentazione non corretta, temperatura alta, ROS elevato, relè antenna non confermato, ATU occupata o profilo paese non approvato. Prima di considerare sicura una radio servono test indipendenti su guasti, timeout e reset.

## 13. Problemi comuni (ipotetici)
Nessun audio: controllare volume, squelch, modo, filtri e collegamento altoparlante. Frequenza inattesa: controllare CH9, ALFA e banda. RX alterna i canali: verificare Dual Watch. TX negata: il blocco e' intenzionale; non bypassarlo. ROS elevato: sospendere qualunque prova TX e verificare con strumenti appropriati. Queste indicazioni non sostituiscono diagnosi su prototipo.

## 14. Dati tecnici - stato di verifica
RX 25,615-28,305 MHz a passi discreti nella tabella; 270 combinazioni 6x(40+5). Prima FI proposta 10,695 MHz; DSP e codec candidati STM32G474RE e TLV320AIC3204; PLL candidato LMX2572. Alimentazione nominale 13,8 V, PCB RF 4 strati da convalidare. Sensibilita', selettivita', potenza, interferenze e emissioni NON misurati.

## 15. Glossario
ALFA: posizioni intercanale +10 kHz. AGC: controllo automatico guadagno. ATU: antenna tuning unit. CTCSS/DCS: codifica selettiva squelch, non privacy. DSP: elaborazione digitale del segnale. FI: frequenza intermedia. PEP: peak envelope power. PLL: sintetizzatore ad aggancio di fase. PTT: push to talk. SWR/ROS: rapporto di onde stazionarie.

## 16. Revisioni e limiti
Questo manuale fa parte del pacchetto cumulativo V4.0. Per nuove chat leggere README.md, RIPRENDI_IN_UNA_NUOVA_CHAT.md, registro decisioni e rapporti test. La versione del pannello e i menu non sono finalizzati; disegni e procedure sono provvisori.

## Appendice A - Tabella integrale delle 270 posizioni RX
| Banda | Canale | ALFA | Frequenza MHz | TX preliminare* |
|---|---:|:---:|---:|:---:|
| A | 1 | NO | 25,615 | NO |
| A | 2 | NO | 25,625 | NO |
| A | 3 | NO | 25,635 | NO |
| A | 3A | SI | 25,645 | NO |
| A | 4 | NO | 25,655 | NO |
| A | 5 | NO | 25,665 | NO |
| A | 6 | NO | 25,675 | NO |
| A | 7 | NO | 25,685 | NO |
| A | 7A | SI | 25,695 | NO |
| A | 8 | NO | 25,705 | NO |
| A | 9 | NO | 25,715 | NO |
| A | 10 | NO | 25,725 | NO |
| A | 11 | NO | 25,735 | NO |
| A | 11A | SI | 25,745 | NO |
| A | 12 | NO | 25,755 | NO |
| A | 13 | NO | 25,765 | NO |
| A | 14 | NO | 25,775 | NO |
| A | 15 | NO | 25,785 | NO |
| A | 15A | SI | 25,795 | NO |
| A | 16 | NO | 25,805 | NO |
| A | 17 | NO | 25,815 | NO |
| A | 18 | NO | 25,825 | NO |
| A | 19 | NO | 25,835 | NO |
| A | 19A | SI | 25,845 | NO |
| A | 20 | NO | 25,855 | NO |
| A | 21 | NO | 25,865 | NO |
| A | 22 | NO | 25,875 | NO |
| A | 23 | NO | 25,905 | NO |
| A | 24 | NO | 25,885 | NO |
| A | 25 | NO | 25,895 | NO |
| A | 26 | NO | 25,915 | NO |
| A | 27 | NO | 25,925 | NO |
| A | 28 | NO | 25,935 | NO |
| A | 29 | NO | 25,945 | NO |
| A | 30 | NO | 25,955 | NO |
| A | 31 | NO | 25,965 | NO |
| A | 32 | NO | 25,975 | NO |
| A | 33 | NO | 25,985 | NO |
| A | 34 | NO | 25,995 | NO |
| A | 35 | NO | 26,005 | NO |
| A | 36 | NO | 26,015 | NO |
| A | 37 | NO | 26,025 | NO |
| A | 38 | NO | 26,035 | NO |
| A | 39 | NO | 26,045 | NO |
| A | 40 | NO | 26,055 | NO |
| B | 1 | NO | 26,065 | NO |
| B | 2 | NO | 26,075 | NO |
| B | 3 | NO | 26,085 | NO |
| B | 3A | SI | 26,095 | NO |
| B | 4 | NO | 26,105 | NO |
| B | 5 | NO | 26,115 | NO |
| B | 6 | NO | 26,125 | NO |
| B | 7 | NO | 26,135 | NO |
| B | 7A | SI | 26,145 | NO |
| B | 8 | NO | 26,155 | NO |
| B | 9 | NO | 26,165 | NO |
| B | 10 | NO | 26,175 | NO |
| B | 11 | NO | 26,185 | NO |
| B | 11A | SI | 26,195 | NO |
| B | 12 | NO | 26,205 | NO |
| B | 13 | NO | 26,215 | NO |
| B | 14 | NO | 26,225 | NO |
| B | 15 | NO | 26,235 | NO |
| B | 15A | SI | 26,245 | NO |
| B | 16 | NO | 26,255 | NO |
| B | 17 | NO | 26,265 | NO |
| B | 18 | NO | 26,275 | NO |
| B | 19 | NO | 26,285 | NO |
| B | 19A | SI | 26,295 | NO |
| B | 20 | NO | 26,305 | NO |
| B | 21 | NO | 26,315 | NO |
| B | 22 | NO | 26,325 | NO |
| B | 23 | NO | 26,355 | NO |
| B | 24 | NO | 26,335 | NO |
| B | 25 | NO | 26,345 | NO |
| B | 26 | NO | 26,365 | NO |
| B | 27 | NO | 26,375 | NO |
| B | 28 | NO | 26,385 | NO |
| B | 29 | NO | 26,395 | NO |
| B | 30 | NO | 26,405 | NO |
| B | 31 | NO | 26,415 | NO |
| B | 32 | NO | 26,425 | NO |
| B | 33 | NO | 26,435 | NO |
| B | 34 | NO | 26,445 | NO |
| B | 35 | NO | 26,455 | NO |
| B | 36 | NO | 26,465 | NO |
| B | 37 | NO | 26,475 | NO |
| B | 38 | NO | 26,485 | NO |
| B | 39 | NO | 26,495 | NO |
| B | 40 | NO | 26,505 | NO |
| C | 1 | NO | 26,515 | NO |
| C | 2 | NO | 26,525 | NO |
| C | 3 | NO | 26,535 | NO |
| C | 3A | SI | 26,545 | NO |
| C | 4 | NO | 26,555 | NO |
| C | 5 | NO | 26,565 | NO |
| C | 6 | NO | 26,575 | NO |
| C | 7 | NO | 26,585 | NO |
| C | 7A | SI | 26,595 | NO |
| C | 8 | NO | 26,605 | NO |
| C | 9 | NO | 26,615 | NO |
| C | 10 | NO | 26,625 | NO |
| C | 11 | NO | 26,635 | NO |
| C | 11A | SI | 26,645 | NO |
| C | 12 | NO | 26,655 | NO |
| C | 13 | NO | 26,665 | NO |
| C | 14 | NO | 26,675 | NO |
| C | 15 | NO | 26,685 | NO |
| C | 15A | SI | 26,695 | NO |
| C | 16 | NO | 26,705 | NO |
| C | 17 | NO | 26,715 | NO |
| C | 18 | NO | 26,725 | NO |
| C | 19 | NO | 26,735 | NO |
| C | 19A | SI | 26,745 | NO |
| C | 20 | NO | 26,755 | NO |
| C | 21 | NO | 26,765 | NO |
| C | 22 | NO | 26,775 | NO |
| C | 23 | NO | 26,805 | NO |
| C | 24 | NO | 26,785 | NO |
| C | 25 | NO | 26,795 | NO |
| C | 26 | NO | 26,815 | NO |
| C | 27 | NO | 26,825 | NO |
| C | 28 | NO | 26,835 | NO |
| C | 29 | NO | 26,845 | NO |
| C | 30 | NO | 26,855 | NO |
| C | 31 | NO | 26,865 | NO |
| C | 32 | NO | 26,875 | NO |
| C | 33 | NO | 26,885 | NO |
| C | 34 | NO | 26,895 | NO |
| C | 35 | NO | 26,905 | NO |
| C | 36 | NO | 26,915 | NO |
| C | 37 | NO | 26,925 | NO |
| C | 38 | NO | 26,935 | NO |
| C | 39 | NO | 26,945 | NO |
| C | 40 | NO | 26,955 | NO |
| D | 1 | NO | 26,965 | SI |
| D | 2 | NO | 26,975 | SI |
| D | 3 | NO | 26,985 | SI |
| D | 3A | SI | 26,995 | NO |
| D | 4 | NO | 27,005 | SI |
| D | 5 | NO | 27,015 | SI |
| D | 6 | NO | 27,025 | SI |
| D | 7 | NO | 27,035 | SI |
| D | 7A | SI | 27,045 | NO |
| D | 8 | NO | 27,055 | SI |
| D | 9 | NO | 27,065 | SI |
| D | 10 | NO | 27,075 | SI |
| D | 11 | NO | 27,085 | SI |
| D | 11A | SI | 27,095 | NO |
| D | 12 | NO | 27,105 | SI |
| D | 13 | NO | 27,115 | SI |
| D | 14 | NO | 27,125 | SI |
| D | 15 | NO | 27,135 | SI |
| D | 15A | SI | 27,145 | NO |
| D | 16 | NO | 27,155 | SI |
| D | 17 | NO | 27,165 | SI |
| D | 18 | NO | 27,175 | SI |
| D | 19 | NO | 27,185 | SI |
| D | 19A | SI | 27,195 | NO |
| D | 20 | NO | 27,205 | SI |
| D | 21 | NO | 27,215 | SI |
| D | 22 | NO | 27,225 | SI |
| D | 23 | NO | 27,255 | SI |
| D | 24 | NO | 27,235 | SI |
| D | 25 | NO | 27,245 | SI |
| D | 26 | NO | 27,265 | SI |
| D | 27 | NO | 27,275 | SI |
| D | 28 | NO | 27,285 | SI |
| D | 29 | NO | 27,295 | SI |
| D | 30 | NO | 27,305 | SI |
| D | 31 | NO | 27,315 | SI |
| D | 32 | NO | 27,325 | SI |
| D | 33 | NO | 27,335 | SI |
| D | 34 | NO | 27,345 | SI |
| D | 35 | NO | 27,355 | SI |
| D | 36 | NO | 27,365 | SI |
| D | 37 | NO | 27,375 | SI |
| D | 38 | NO | 27,385 | SI |
| D | 39 | NO | 27,395 | SI |
| D | 40 | NO | 27,405 | SI |
| E | 1 | NO | 27,415 | NO |
| E | 2 | NO | 27,425 | NO |
| E | 3 | NO | 27,435 | NO |
| E | 3A | SI | 27,445 | NO |
| E | 4 | NO | 27,455 | NO |
| E | 5 | NO | 27,465 | NO |
| E | 6 | NO | 27,475 | NO |
| E | 7 | NO | 27,485 | NO |
| E | 7A | SI | 27,495 | NO |
| E | 8 | NO | 27,505 | NO |
| E | 9 | NO | 27,515 | NO |
| E | 10 | NO | 27,525 | NO |
| E | 11 | NO | 27,535 | NO |
| E | 11A | SI | 27,545 | NO |
| E | 12 | NO | 27,555 | NO |
| E | 13 | NO | 27,565 | NO |
| E | 14 | NO | 27,575 | NO |
| E | 15 | NO | 27,585 | NO |
| E | 15A | SI | 27,595 | NO |
| E | 16 | NO | 27,605 | NO |
| E | 17 | NO | 27,615 | NO |
| E | 18 | NO | 27,625 | NO |
| E | 19 | NO | 27,635 | NO |
| E | 19A | SI | 27,645 | NO |
| E | 20 | NO | 27,655 | NO |
| E | 21 | NO | 27,665 | NO |
| E | 22 | NO | 27,675 | NO |
| E | 23 | NO | 27,705 | NO |
| E | 24 | NO | 27,685 | NO |
| E | 25 | NO | 27,695 | NO |
| E | 26 | NO | 27,715 | NO |
| E | 27 | NO | 27,725 | NO |
| E | 28 | NO | 27,735 | NO |
| E | 29 | NO | 27,745 | NO |
| E | 30 | NO | 27,755 | NO |
| E | 31 | NO | 27,765 | NO |
| E | 32 | NO | 27,775 | NO |
| E | 33 | NO | 27,785 | NO |
| E | 34 | NO | 27,795 | NO |
| E | 35 | NO | 27,805 | NO |
| E | 36 | NO | 27,815 | NO |
| E | 37 | NO | 27,825 | NO |
| E | 38 | NO | 27,835 | NO |
| E | 39 | NO | 27,845 | NO |
| E | 40 | NO | 27,855 | NO |
| F | 1 | NO | 27,865 | NO |
| F | 2 | NO | 27,875 | NO |
| F | 3 | NO | 27,885 | NO |
| F | 3A | SI | 27,895 | NO |
| F | 4 | NO | 27,905 | NO |
| F | 5 | NO | 27,915 | NO |
| F | 6 | NO | 27,925 | NO |
| F | 7 | NO | 27,935 | NO |
| F | 7A | SI | 27,945 | NO |
| F | 8 | NO | 27,955 | NO |
| F | 9 | NO | 27,965 | NO |
| F | 10 | NO | 27,975 | NO |
| F | 11 | NO | 27,985 | NO |
| F | 11A | SI | 27,995 | NO |
| F | 12 | NO | 28,005 | NO |
| F | 13 | NO | 28,015 | NO |
| F | 14 | NO | 28,025 | NO |
| F | 15 | NO | 28,035 | NO |
| F | 15A | SI | 28,045 | NO |
| F | 16 | NO | 28,055 | NO |
| F | 17 | NO | 28,065 | NO |
| F | 18 | NO | 28,075 | NO |
| F | 19 | NO | 28,085 | NO |
| F | 19A | SI | 28,095 | NO |
| F | 20 | NO | 28,105 | NO |
| F | 21 | NO | 28,115 | NO |
| F | 22 | NO | 28,125 | NO |
| F | 23 | NO | 28,155 | NO |
| F | 24 | NO | 28,135 | NO |
| F | 25 | NO | 28,145 | NO |
| F | 26 | NO | 28,165 | NO |
| F | 27 | NO | 28,175 | NO |
| F | 28 | NO | 28,185 | NO |
| F | 29 | NO | 28,195 | NO |
| F | 30 | NO | 28,205 | NO |
| F | 31 | NO | 28,215 | NO |
| F | 32 | NO | 28,225 | NO |
| F | 33 | NO | 28,235 | NO |
| F | 34 | NO | 28,245 | NO |
| F | 35 | NO | 28,255 | NO |
| F | 36 | NO | 28,265 | NO |
| F | 37 | NO | 28,275 | NO |
| F | 38 | NO | 28,285 | NO |
| F | 39 | NO | 28,295 | NO |
| F | 40 | NO | 28,305 | NO |

* Flag solo documentale, privo di qualunque valore autorizzativo. Il prototipo non e' certificato e il profilo paese non e' approvato.

## Fonti e documenti di lavoro
- Tabella canali: `02_Piano_Frequenze/Tabella_270_canali.csv` (verificata con test software, non in RF).
- Registro decisioni e Specifica firmware V4.0 inclusi nel medesimo archivio.
- TE drawing per SMA: https://www.te.com/en/product-CONSMA002-SMD-G.html
- KiCad CLI documentazione: https://docs.kicad.org/master/en/cli/cli.html
- MIMIT CB e prescrizioni italiane: https://www.mimit.gov.it/it/comunicazioni/radio/autorizzazioni-e-licenze/cb-banda-cittadina
