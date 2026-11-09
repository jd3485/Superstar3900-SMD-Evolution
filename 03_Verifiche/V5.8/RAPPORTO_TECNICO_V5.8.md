# Rapporto tecnico V5.8 — Distanza geometrica delle piste RF dalle vie GND

**Data:** 9 novembre 2026. **Progetto:** Superstar 3900 SMD Evolution. **Stato:** solo studio RF RX 50 Ω, **NON FAB / NON PCBWay / NO TX**. Nessun prototipo fisico collaudato, nessun KiCad ERC/DRC nativo eseguito.

## Avanzamento concreto

Analisi riproducibile delle distanze **fra la linea centrale dei 13 segmenti di piste RF su F.Cu e il centro della via GND più vicina**, misurate lungo le sei reti RF del PCB candidato V5.2. È esclusa dalla tabella la rete di alimentazione `+5V_BENCH`; la net `RF_BIAS_OUT` include il ramo di polarizzazione RF dell'ADL5535. Sono state esaminate **70 vie GND passanti**, tutte le 13 piste RF e **6 reti**. I file CAD sono invariati.

Campionamento dei segmenti rettilinei ogni **al massimo 0,20 mm**, con estremi inclusi. Siccome la funzione distanza dal centro della via più vicina è 1-Lipschitz, il vero massimo lungo ogni tratto rettilineo non può superare il massimo campionato di oltre **0,10 mm** (limite conservativo per questo modello di centro-pista e centro-via, senza considerarne gli ingombri). I massimi riportati sono valori campionati, non un'analisi elettromagnetica.

| Rete | Segmenti | Sviluppo piste (mm) | Massima distanza campionata da via GND (mm) | Limite superiore geometrico (mm) | Punto peggior campionato (x,y mm) |
|---|---:|---:|---:|---:|---|
| `RF_ATTEN_IN` | 2 | 47.200 | 9.5811 | 9.6807 | (67.47, 65.00) |
| `RF_ATTEN_OUT` | 2 | 49.200 | 6.9385 | 7.0382 | (85.52, 65.00) |
| `RF_BIAS_OUT` | 5 | 31.672 | 5.7306 | 5.8306 | (72.20, 45.00) |
| `RF_LNA_INPUT` | 1 | 23.450 | 5.7195 | 5.8188 | (28.00, 36.00) |
| `RF_LNA_OUT` | 1 | 29.450 | 5.7195 | 5.8190 | (122.00, 36.00) |
| `RF_LNA_IC_IN` | 2 | 14.213 | 5.2989 | 5.3983 | (56.52, 36.00) |

**Risultato per priorità geometrica:** `RF_ATTEN_IN` ha il massimo campionato di **9,5811 mm** presso (67,47; 65,00); `RF_ATTEN_OUT` segue con **6,9385 mm**. Si tratta di una metrica di *prossimità delle vie*, NON della lunghezza della corrente di ritorno. Non significa che queste reti siano difettose. La soglia **5 mm** è scelta unicamente come marcatore di esame comparativo, **non una regola KiCad, limite RF o specifica PCBWay**. Non è stata introdotta alcuna via nuova.

## Il ritorno RF reale resta da verificare

Le quattro zone GND `F.Cu`, `In1.Cu`, `In2.Cu`, `B.Cu` del PCB candidato rimangono **UNFILLED**. Un piano di massa solido, quando realmente connesso e vicino alla traccia, può fornire il percorso di ritorno principale anche dove le vie sono lontane: dunque **la distanza dalla via NON è un indicatore sufficiente dell'impedenza di ritorno RF, di perdite o del matching a 50 Ω**. I piani teorici della V5.7 non riproducono thermals, isole eliminate o le regole di KiCad. Mancano stack-up con quota dielettrica, Er, rame, gap coplanare, taratura/EM simulata e dati di prova.

In particolare occorre esaminare dopo il riempimento nativo: continuità GND dei quattro SMA; percorsi R201/R202/R203 nell'attenuatore; pad termico U101 e le 6 vie da 0,55/0,25 mm; area dei piani sotto i tratti RF lunghi; piani effettivamente connessi; parità schema/PCB; assenza di violazioni ERC/DRC. **Non approvare le zone perché un modello geometrico mostra un'unica regione.**

## Documentazione produttore / riferimenti indipendenti

- Analog Devices, [scheda EVAL-ADL5535](https://www.analog.com/en/resources/evaluation-hardware-and-software/evaluation-boards-kits/eval-adl5535.html): riferimento ufficiale ADI di una scheda 4 layer FR4 alimentata a 5 V, con file Gerber di valutazione disponibili sul sito; NON garantisce il layout del nostro progetto.
- [KiCad 10 PCB Editor — Design Rules / Zones](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html): clearance, larghezza minima, connessioni ai pad e gestione delle zone richiedono il **riempimento effettivo** prima del controllo DRC. Un `--refill-zones` con parità è necessario, ma da solo non sostituisce il controllo RF/termico/DFM.

## Test, preservazione e riproduzione

- `audit_ritorno_rf_v58.py`: parser sorgente KiCad e misura NumPy; output `AUDIT_RITORNO_RF_V5.8.json`, con ogni segmento, massimo e coordinate.
- `SINTESI_RITORNO_RF_V5.8.csv`: sei reti, ordinate dalla maggior distanza alla via GND.
- `genera_mappa_rf_v58.py` e `MAPPA_VIE_E_PISTE_RF_V5.8.svg`: mappa ottenuta da coordinate di piste e vie nel file KiCad, NON il rendering PCB KiCad.
- `test_ritorno_rf_v58.py`: **30/30 test superati**, comprese mutazioni di piste, larghezze, net, geometria pad e vie, layer zone e variazione passo campionamento.
- `run_audit_e_kicad_v58.py`: lanciatore fail-closed: audit statico poi runner nativo V5.7, se presente `kicad-cli`. Il controllo locale ha dato `NOT_RUN_KICAD_MISSING` e codice 5; nessuna falsificazione di ERC/DRC.
- `run_regressioni_v58.py`: **19/19 suite V4.0–V5.8 superate**, comprese le 2.400 condizioni del supervisore V4.0. Questi sono test software, non certificazioni RF o PCB.
- PCB originale V3.8 invariato (hash SHA-256 `57dd24b13edb5dc987e3ad8cdae0d2d8cc7a1fa3aefb455a63ebc86559eec489`); V4.8 e V5.2 non alterati, copie storiche preservate.

## Gate di rilascio

I nove gate di V5.0 restano tutti OPEN. **ERC/DRC nativi NOT_RUN, CAD TE SMA non approvato, termica ADL5535 e stencil via-in-pad senza risposta scritta DFM, nessuna caratterizzazione RF.** Percentuale storica 37% stimata, non rappresenta un hardware costruibile. Nessuna produzione PCB, nessuna TX.
