# Superstar 3900 SMD Evolution — V3.9 audit documentale cumulativo

**Avanzamento complessivo stimato 37%, invariato. NO FAB / NO PCBWAY.**

Questa revisione verifica la documentazione TE del SMA `CONSMA002-SMD-G` e confronta alcune dimensioni nominali con il PCB V3.8. **Non introduce un nuovo PCB né autorizza la produzione.** I test statici V3.8 (44/44) e V3.7 (17/17) e tutti i 605 hash del manifest V3.8 sono stati verificati in questa ripresa. KiCad CLI è assente: nessun ERC/DRC nativo, refill delle zone o prova RF.

## Percorso essenziale
- `00_Gestione_Progetto/CHANGELOG_V3.9.md` — lavoro effettuato e limiti
- `03_Verifiche/V3.9/Esito_Confronto_Footprint_V3.9.json` — rilievi riproducibili
- `03_Verifiche/V3.9/review_v39.py` — script di verifica in sola lettura del PCB V3.8
- `03_Verifiche/V3.9/Confronto_Disegno_TE_V3.9.csv` — quote nominali e punti aperti
- `01_Specifiche/Protocollo_Accettazione_CAD_V3.9.md` — istruzioni per verifiche KiCad e DFM ancora da fare
- `04_KiCad/Modulo_RX_Test_50ohm_V3.8/` — ultimo PCB sperimentale, volutamente immutato
- `RIPRENDI_IN_UNA_NUOVA_CHAT.md` — stato aggiornato e istruzioni per proseguire

Nota: i documenti TE/ADI si citano tramite link, non si considerano certificazione del layout. Non collegare il coupon RX a un TX in funzione.
