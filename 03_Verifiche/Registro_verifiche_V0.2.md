# Registro verifiche - V0.2 - 2026-11-06

| ID | Attivita | Strumento | Esito | Limite |
|---|---|---|---|---|
| T-001 | 270 frequenze uniche, ALFA e CH9 | Python test_frequency_plan.py | PASS | Piano RX/TX solo software |
| T-002 | 270 f_LO a 36,310..39,000MHz, VCO 2,32384..2,496GHz, INT=3631..3900, FRAC=0, errori matematici=0 | Python test_pll_plan.py | PASS | Non e programmazione/simulazione fisica PLL |
| T-003 | CH9 priorita AM, ALFA separato, blocco TX altre bande, fault injection logica | Python test_control_model.py | PASS | Non sostituisce interlock fisico |
| T-004 | Friis/SNR modello con valori ipotizzati | Python test_rx_noise_budget.py | PASS | Confermata sola consistenza dei calcoli, non prestazione RX |
| T-005 | Spice/PLL fase-spurie | non installato/eseguito | NON ESEGUITO | Richiede schematico e modelli |
| T-006 | KiCad/ERC/DRC | non installato/eseguito | NON ESEGUITO | Nessuno schematico o board |
| T-007 | Prove RF e RED | laboratorio non disponibile | NON ESEGUITO | Servono prototipo e strumentazione |

Comando: `python 03_Verifiche/run_all_tests.py` con Python 3.13.5; 4 suite PASS. Per ripetibilita: tutte le frequenze in Hz interi, niente floating-point nella programmazione sintetizzatore.
