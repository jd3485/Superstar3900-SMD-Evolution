# Funzioni CW e PA - requisiti funzionali V1.1 (NON IMPLEMENTATE)

## CW / telegrafia
- Nuova posizione fisica CW nel selettore della modalita radio; connettore key 3.5 mm isolato con ESD e pull-up protetto.
- Logica di keying con debounce e rilevamento tasto bloccato; sidetone a frequenza 400-1000 Hz regolabile e silenziamento RF in assenza di autorizzazione.
- Filtro RX CW commutabile (obiettivo 300/500 Hz, risposta da simulare) con centro e BFO da determinare.
- Break-in semiautomatico e sequenza sicura RX -> TX -> RX (temporizzazioni, anti-hot-switching), con blocco TX per le frequenze non autorizzate.
- Potenza e compatibilita del modo CW non assumibili sulle sole autorizzazioni CB; verificare normativa, non attivare CW TX di default. Sidetone e ricezione sono permessi nel concept.
- Prove: tempi keying, click RF, armoniche, deviazioni frequenza e protezione per SWR elevato.

## PA / Public Address
- PA e una modalita AUDIO, NON una modulazione RF; il comando PA deve inibire sempre il PTT RF a livello hardware e firmware.
- Presa speaker dedicata, amplificatore audio SMD dimensionato al carico e al volume obiettivo (8 ohm ipotizzati ma da confermare).
- Utilizzo del microfono di bordo, circuito anti-feedback, volume PA e indicazione sul display.
- Transizione PA <-> radio senza colpi in altoparlante; sovracorrente/termica e connettore protetti.
- Prove: potenza non distorta, THD+N, risposta in frequenza, runaway termico, interblocco TX in modalità PA.

## Tracciabilita e stato
CW: requisito ufficiale, 0% schema/firmware e test. PA: requisito ufficiale, 0% schema/firmware e test.
In V1.1 esiste solo questa specifica, non componentistica finalizzata, nessun annuncio di modalita funzionanti.
