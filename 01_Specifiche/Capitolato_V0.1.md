# Capitolato di progetto — V0.1

## Obiettivo
Ricostruire lo spirito del ricetrasmettitore CB Superstar 3900, riprogettando l'elettronica prevalentemente in SMD e aggiungendo strumenti e protezioni. Interfaccia manuale con comandi vintage conservati; dimensioni originali da rilevare prima del PCB.

## Requisiti funzionali
| ID | Requisito | Criterio preliminare / nota |
|---|---|---|
| RF-01 | Ricezione AM, FM, USB, LSB | 25,615–28,305 MHz sulle 270 posizioni prestabilite |
| RF-02 | Piano canali vintage | 6 bande A–F, 40 canali di base + 5 ALFA per banda |
| UI-01 | ALFA separato | Interruttore fisico +10 kHz soltanto sui canali 3,7,11,15,19; altri invariati |
| UI-02 | CH9 separato | Richiama banda D, canale 9, 27,065 MHz, AM; restituisce stato precedente all'uscita |
| UI-03 | Selettori fisici | Banda, canale, volume, squelch, RF gain, microfono, modalità; posizioni da confermare |
| UI-04 | Strumenti | Display frequenza reale, potenza media e PEP, ROS, modulazione, strumento analogico conservato |
| RX-01 | Basso rumore | Preselettori commutabili, mixer con elevato margine di sovraccarico, filtraggio FI dedicato, AGC adeguato |
| RX-02 | Selettività | SSB circa 2,4 kHz; AM/FM filtri dedicati: banda definitiva da validare con test |
| RX-03 | Gestione rumore | NB, ANL e riduzione rumore audio disinseribile; modalità analogica diretta |
| RX-04 | Sensibilità | SSB ≤0,25 µV per 10 dB (S+N)/N; AM ≤0,5 µV per 10 dB (S+N)/N; target, non verificati |
| SY-01 | Sintonia | Sintetizzatore a riferimento stabile; rumore di fase e spurie da verificare rispetto a RX e TX |
| TX-01 | Trasmissione limitata | Abilitazione preliminare soltanto sui 40 canali ordinari della banda D; ALFA e altre bande bloccate |
| TX-02 | Potenza | Impostazione massima 4 W AM/FM e 12 W PEP SSB secondo condizioni CEPT, subordinata a requisiti nazionali e conformità |
| TX-03 | Protezioni | Inibizione TX su PLL unlock, guasti termici/elettrici, ROS eccessivo; interblocco hardware + software |
| ATU-01 | Accordo | Rete LC con bypass e misura diretta/riflessa, commutatori adeguati e controllo automatico con potenza ridotta |
| PW-01 | Alimentazione | 13,8 V nominali; protezioni inversione polarità, transitori e sottotensione; correnti da budgetizzare |
| PCB-01 | PCB | Prevalenza SMD; elementi THT solo se richiesti da RF, corrente, potenza, schermatura o connessioni |
| PCB-02 | EMI | Masse RF continue, schermature, separazione sezioni, ritorni di corrente controllati; stack-up dopo scelta fabbricante |
| MFG-01 | Produzione | Dati KiCad, Gerber, Excellon, BOM, file component placement, assembly drawing e istruzioni |

## Architettura preliminare
Antenna SO-239 → commutazione RX/TX → preselettori RF / RX → mixer / FI → demodulatori AM/FM/SSB → AGC/NB/ANL → audio analogico → filtro digitale opzionale → altoparlante.

Sintetizzatore RF a riferimento stabile e frequenze di conversione da selezionare con analisi di spurie e rumore di fase. Il telaio storico EPT360014B ha FI di 10,695 MHz e 455 kHz (AM/FM), ma il progetto SMD non ne è automaticamente una copia elettrica.

Catena TX su percorso separato: microfono / condizionamento → modulatori → conversione RF → driver / PA → filtro armoniche → sensore direzionale potenza/ROS → accordatore automatico con bypass → antenna. Percorsi e posizione del sensore da ottimizzare per distinguere potenza al PA e potenza all'antenna.

Controllo digitale: microcontrollore → lettura comandi / display / protezioni / logica 270 canali / sintonia / ATU. Il controllo non deve introdurre disturbi in RX.

## Scelte NON ancora chiuse
- Circuito PLL/VCO e relativo margine di copertura/rumore di fase.
- Topologia completa del ricevitore e prestazioni di dinamica/IP3.
- Transistor RF, PA, commutazione RF e dissipatore.
- Dimensioni, ingombri e compatibilità con il guscio originale.
- Tipo display, pinout dei connettori e tastiera/manopole.
- BOM, disponibilità componenti, costo e stack-up PCB effettivo.

## Vincolo di sicurezza normativa
La tabella software rende disponibili 270 posizioni in ricezione. L'abilitazione TX di progetto è limitata ai 40 canali ordinari in banda D, e solo dopo verifica della conformità dell'apparato nel paese d'uso. La Direttiva RED e norme armonizzate richiedono più del solo controllo di potenza: emissività, immunità, stabilità e sicurezza. Un PCB artigianale non diventa automaticamente un apparato CB omologato.

## Riferimenti
- https://www.cbradio.nl/superstar/Downloaded/Service_Manual_Superstar_SS3900_EPT360014B_Homer_ENG.pdf
- https://cbtricks.org/radios/superstar/3900/ss3900_band_chart_a.htm
- https://www.suzukituning.com/Electronics/SuperStar3900.htm
- https://docdb.cept.org/implementation/430
- https://www.etsi.org/deliver/etsi_en/300400_300499/300433/02.01.00_20/en_300433v020100a.pdf
- https://www.pcbway.com/helpcenter/pcb_assembly_ordering/What_files_are_requested_for_assembly_production_.html
