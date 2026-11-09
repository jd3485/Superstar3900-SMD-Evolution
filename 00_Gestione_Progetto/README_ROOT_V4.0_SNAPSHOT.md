# Superstar 3900 SMD Evolution - V4.0 cumulativa

**DATA 2026-11-08 | Avanzamento documentale stimato 37% (invariato) | ZERO moduli hardware collaudati | NO FAB / NO PCBWAY**.

Questa revisione aggiunge manuale d'uso illustrato (BOZZA, 11 pagine) e un prototipo di **supervisione logica software in pura simulazione**. Convalida di pannello, test hardware e conformita' sono aperti. Ultimo PCB RF sperimentale: **V3.8 immutata**, con SMA TE e pad ADL5535 non approvati.

## Avvio rapido di una chat nuova
1. Leggere `RIPRENDI_IN_UNA_NUOVA_CHAT.md` (cartella root).
2. Leggere `00_Gestione_Progetto/REGISTRO_DECISIONI.md`, `00_Gestione_Progetto/CHANGELOG_V4.0.md` e il rapporto V4.0.
3. Usare `06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf` e l'omonimo sorgente `.md` per specifiche d'uso.
4. Usare `01_Specifiche/Matrice_Supervisione_Firmware_V4.0.md` e il modello/test di `08_Firmware_Prototipi/radio_supervisor_v40.py` e `03_Verifiche/V4.0/` per proseguire la logica firmware.
5. Prossimo blocco tecnico RF: procedura `01_Specifiche/Protocollo_Accettazione_CAD_V3.9.md` e PCB `04_KiCad/Modulo_RX_Test_50ohm_V3.8/`.

## Evidenza e limitazioni
- Test statici V3.8: 44/44, V3.7: 17/17; V4.0: 2400 casi parametrici + prove di priorita', input avversi e otto guard simulati.
- KiCad CLI non disponibile. Non eseguiti ERC/DRC nativi, refill zone, misure VNA/termiche, conformita' RF.
- Il nuovo `tx_request=True` del modello non e' mai un consenso TX reale; non esistono circuiti o firmware di trasmissione validati.
- Documenti CAD TE disponibili online ma non acquisiti come file locali; proprieta' TE rispettata senza ridistribuirli.

Conservazione: tutti gli elaborati originali V3.9 presenti, salvo file attivi aggiornati la cui copia V3.9 e' nella cartella gestione; storico versionato, changelog e manifest SHA-256 cumulativi.
