# Superstar 3900 SMD Evolution — V4.1 cumulativa (2026-11-08)

**Stato: 37% progettuale stimato, invariato. Zero moduli hardware collaudati. NO FAB / NO PCBWAY / NO TX.**

## Cosa cambia in V4.1

Nuovo audit statico *riproducibile* sul PCB RX sperimentale V3.8 (sorgente originale immutata), 12 test automatici, analisi dell'attenuatore π da 6 dB ideale e controllo geometrico del percorso termico ADL5535. Il footprint SMA TE resta **non approvato**; nessuna verifica nativa KiCad o fisica è stata eseguita in questa revisione.

## Avvio da nuova chat

1. Leggere `RIPRENDI_IN_UNA_NUOVA_CHAT.md`.
2. Leggere `00_Gestione_Progetto/REGISTRO_DECISIONI.md` e `00_Gestione_Progetto/CHANGELOG_V4.1.md`.
3. Consultare `01_Specifiche/Requisiti_Accettazione_RF_V4.1.md` e `03_Verifiche/V4.1/RAPPORTO_V4.1.md`.
4. Ripetere `python3 03_Verifiche/V4.1/test_audit_rf_v41.py` e confrontare i risultati JSON.
5. Manuale d'uso illustrato: `06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf` (11 pagine; **bozza**, non sostituito).
6. Prossimo blocco: eseguire import TE DXF/STEP ufficiale e validazioni KiCad su copia; script `03_Verifiche/V4.1/RUN_KICAD_NATIVE_V4.1.sh` per una macchina con KiCad 10+.

## Limitazioni

I file CAD TE sono documenti del produttore e non sono ridistribuiti. Le quote statiche e i calcoli sono prerequisiti, non conferme di saldabilità, DRC, impedenza o dissipazione. Il parametro 37% è una stima di progetto, non una metrica hardware. Non emettere Gerber né ordinare schede.

L'ultimo PCB sperimentale rimane la V3.8; il controllore software prototipo rimane V4.0. Sono stati conservati i file storici e gli snapshot dei documenti aggiornati, per poter ripartire da questo solo archivio ZIP.
