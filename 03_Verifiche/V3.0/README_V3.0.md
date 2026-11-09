# V3.0 - calcolo integrato del front end RX

`python 03_Verifiche/V3.0/model_rx_v30.py`

Legge il codice produttore/modello V2.9 e calcola le 5 modalità RX con formule Friis e IIP3 reciproco, in ciascuna delle 101 frequenze RX. Salva CSV, JSON e grafici con assunzioni esplicite. Nessuna prova RF reale o ERC è stata eseguita.

Il filtro diviso (segnalato `RX_POST_FILTER_HYPOTHETICAL`) non ha reiezione immagine verificata. Non confondere risultati statistici di simulazioni precedenti con resa di produzione.

V3.0 non aggiunge schemi KiCad definitivi. La scelta di progetto resta preliminare, percentuale complessiva stimata 35%, invariata V2.9, perché ancora nessuna sezione RX validata.
