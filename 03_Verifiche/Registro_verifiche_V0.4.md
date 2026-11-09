# Registro verifiche V0.4 - 2026-11-06

| Test | Esito | Limiti |
|---|---|---|
| Modello di controllo L(s) / filtro passivo C1-C3 | PASS numerico | modello continuo linearizzato, componenti ideali |
| Crossover e margine fase nominali | 4489.0Hz / 54.73° | dipendono da Kv 40MHz/V tipica, Icp 2.5mA |
| Monte Carlo 4000 campioni | PM min 49.11° | intervalli ipotizzati, non prova per tutte le condizioni |
| Calcolo pad adattati 50ohm | PASS formule | valori ideali, non misurati |
| LO bilancio nominale | +7.30dBm | **non verificato**: amp gain e perdita filtri assunti |
| Confronto banda PHA-1+ e ADL5611 | PASS datasheet | prova a 36MHz sul campione mancante |
| Rumore fase dBc/Hz, spurie e 2.4GHz spur | DA FARE | serve riferimento con noise model e misure reali |
| ADIsimPLL / ngspice | NON ESEGUITO | non disponibili nell'ambiente |
| KiCad ERC/PCB DRC | NON ESEGUITO | schemi PCB non realizzati |
| Banco hardware RF / EMC / conformita TX | NON ESEGUITO | nessun prototipo fisico |

Risultati e tracciati: Report_PLL_Loop_V0.4.json, grafici, CSV, script riproducibile. Sono stati calcolati internamente con Python/numpy/scipy; nessuna affermazione di misura strumentale.
