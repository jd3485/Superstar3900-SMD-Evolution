# Procedura KiCad 10 — V4.9, da eseguire su un PC con KiCad installato

**Questa procedura non è stata eseguita in questo ambiente.** Non confondere la disponibilità degli script con un DRC superato.

1. Estrarre l'intero ZIP V4.9 in una cartella locale; conservarne una copia intatta.
2. Installare e verificare la disponibilità effettiva di `kicad-cli` (`kicad-cli version`); non inventare il risultato se non presente.
3. Prima di avviare, prendere visione dello script storico `03_Verifiche/V4.8/RUN_KICAD_CANDIDATO_V48.sh`, che lavora su copia in una directory temporanea, verifica opzioni e blocca l'esecuzione se mancano funzioni richieste.
4. Eseguire lo script con una cartella risultati, per esempio `bash 03_Verifiche/V4.8/RUN_KICAD_CANDIDATO_V48.sh ./KICAD_V49_ESTERNO` dalla radice del progetto. Esegue ERC e DRC con parità e refill zone su copia. Se il programma segnala `NOT_RUN`, fermarsi.
5. Archiviare versione KiCad, output JSON, stdout, exit code, eventuali violazioni e screenshot/correzioni proposte. Controllare separatamente il numero e l'esito delle violazioni, senza basarsi soltanto su un file esistente.
6. Dopo eventuali correzioni su una **nuova copia candidata**, ripetere la suite V4.9: `PYTHONDONTWRITEBYTECODE=1 python3 03_Verifiche/V4.9/test_v49.py`. Il candidato V4.8 originale deve mantenere il proprio SHA-256.
7. Solo dopo l'approvazione DFM e CAD TE avviare una revisione CAM; questo documento non autorizza export di Gerber per ordine.

Fonte documentazione CLI: https://docs.kicad.org/10.0/en/cli/cli.html
