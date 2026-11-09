# Registro verifiche V0.6 - 06/11/2026
| ID | Verifica | Esito | Limite |
|---|---|---|---|
| V6-01 | 270 righe da V0.5, range N | PASS software | solo matematica |
| V6-02 | Core indicato da TI Table 136, confine 4.650 GHz | PASS aritmetico | nucleo autocalibrato realmente non testato: 2 righe VCO3, 268 VCO4 |
| V6-03 | Pinmap 40+pad contro TI SNAS740B | PASS revisione documentale | pin NC/pull inutilizzati non ancora fissati; necessita ERC |
| V6-04 | Conformita C3 >= 1.5 nF TI | PASS documentale, 2.2 nF | tolleranze e bias da validare |
| V6-05 | Crossover e margine nominali | PASS modello lineare | 4016 Hz, PM 59.76 gradi; NON simulazione circuito IC |
| V6-06 | 4000 campioni stress parametri fittizi | PASS Monte Carlo codice | PM minimo nel campione 43.97 gradi, <45: 2; non distribuzioni di produzione |
| V6-07 | TCXO TXC 12,8MHz disponibile | PASS verifica documentale/web | manca curva PN e datasheet footprint originale |
| V6-08 | PLLatinum Sim e phase noise totale | NON ESEGUITO | non simulato / misurato |
| V6-09 | KiCad ERC/DRC, PCB e Gerber | NON ESEGUITO | mancano schematici e PCB formalizzati |
| V6-10 | TX power, spurious, conformity | NON ESEGUITO | necessario prototipo e banco misura |

Test eseguibili da radice archivio:
`python3 03_Verifiche/run_all_tests.py`
`python3 03_Verifiche/PLL_LMX2572_V0.6_riproduci.py`
`python3 03_Verifiche/test_stage3_v06.py`
