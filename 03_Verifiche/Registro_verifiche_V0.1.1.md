# Registro verifiche — V0.1.1

Questo documento integra, senza cancellarlo, `Registro_verifiche_V0.1.md`.

| Attività | Metodo | Esito | Note |
|---|---|---|---|
| Modello frequenze | `python 03_Verifiche/test_frequency_plan.py` | **PASS** il 2026-11-06 | 270 uniche; 240 ordinarie + 30 Alfa; CH9; ordine 23/24; 40 TX ammessi nel solo modello |
| Completeness archivio | Controllo presenza documenti + manifest | **PASS** | Non equivale a verifica elettronica |
| Schemi KiCad/ERC | Non eseguita | NON DISPONIBILE | Schemi ancora da progettare |
| PCB/DRC | Non eseguita | NON DISPONIBILE | Layout ancora da progettare |
| Simulazioni circuitali/EM/RF | Non eseguite | NON DISPONIBILE | Modelli e circuiti ancora da progettare |
| Collaudi su hardware | Non eseguiti | NON DISPONIBILE | Nessun prototipo realizzato |
| Conformità normativa | Non verificata | DA VALUTARE | Necessaria analisi tecnica indipendente prima di utilizzare TX |

## Esecuzione riproducibile
Dalla cartella radice del progetto: `python 03_Verifiche/test_frequency_plan.py`.
Il risultato PASS verifica soltanto la logica del modello frequenze in queste condizioni, non la stabilità di PLL, armoniche, prestazioni RF, validità del layout o conformità.
