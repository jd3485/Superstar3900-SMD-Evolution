# Manuale tecnico — aggiornamento modulo RX V3.8

Questo capitolo è **sperimentale** e non descrive la PCB definitiva del Superstar 3900.

Il coupon separa il percorso ADL5535 e il percorso attenuatore a 6 dB. Il front-end deve essere collaudato unicamente con generatori di segnale RF, VNA ed alimentazione a 5 V con limitazione di corrente. Non esiste protezione T/R e non va collegato al trasmettitore.

Sui quattro SMA, l'orientamento ipotizzato è J101/J103 verso sinistra e J102/J104 verso destra. La sagomatura delle piazzole di massa è stata introdotta come candidato; l'ingombro meccanico e il codice esatto del componente devono essere controllati sul prototipo reale. Non usare il progetto per ordinare componenti senza verificare la compatibilità del suffisso -G.

Per ADL5535, RFIN pin 1, GND pin 2/paddle e RFOUT/alimentazione pin 3. La bobina di polarizzazione da 470 nH e i disaccoppiamenti restano quelli dello schema sperimentale. In V3.8 è stata tracciata una connessione F.Cu fra pad termico e via GND prossimo, evitando un via aperto sotto il componente. La geometria non assicura ancora la temperatura di giunzione.

Verificare obbligatoriamente: orientamento SMA, corti PCB e maschera saldante, inserzione/ritorno VNA in condizioni scollegate dalla TX, consumo e temperatura dopo alimentazione, provando dapprima con RF disattiva. Seguire `01_Specifiche/Procedura_KiCad_DRC_Termico_V3.8.md` prima di qualsiasi ordine.
