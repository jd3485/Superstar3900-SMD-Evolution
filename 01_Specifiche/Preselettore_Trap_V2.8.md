# V2.8 - Preselettore LP7 con zeri di trasmissione nella banda immagine

**Stato: candidato NON APPROVATO.**

## Risultato
Nel modello a 50 ohm, 7 stadi con due risonatori paralleli L||C inseriti in serie hanno 9 componenti fisici e possono sostituire un filtro HP5+LP9 di 14 componenti. Con HP3 opzionale da 12 MHz sono 12 componenti fisici. Valori selezionati per lo studio: due L da 180 nH, due L da 470 nH, tre C shunt 120/140/120 pF e due C di risonanza 56/62 pF. NON e' una sintesi ellittica formale ottimizzata, ma una rete esplorativa con zeri di trasmissione.

* LP7 + trap Q=30: perdita 1.056 dB, reiezione immagini 65.37 dB, S11 peggiore -17.25 dB.
* HP3 + LP7 + trap Q=30: perdita 1.274 dB, reiezione immagini 65.59 dB, S11 peggiore -12.83 dB.
* A 10 MHz il filtro LP solo attenua 0.31 dB, quello con HP3 6.88 dB: HP3 aiuta, ma anche questa soppressione puo' essere insufficiente con un trasmettitore HF forte nelle vicinanze.

## Nota su Q / BOM
Il Coilcraft 0805CS-181 e 0805CS-471 sono famiglie candidate (non MPN completi). Il Q va misurato o ricavato da curve esatte intorno a 27 MHz e 47-50 MHz, non copiato da specifiche a 100/250 MHz. Il condensatore shunt da 140 pF e' un valore da verificare in una serie specifica. L'induttanza shunt del passa-alto HP3 richiede un codice distinto e un'analisi della SRF.

## Gate/limiti
Stress numerico: 1200 casi per rete, tolleranza L±5%, C±2%, Q globale uniformemente distribuito tra 20 e 60; non e' una distribuzione produttiva. I modelli SPICE sono stati **generati ma NON eseguiti**; usano ESR fisso a 27 MHz, mentre il modello Python assume Q costante: confrontare i risultati e' necessario. Nessuna validazione EMC/PCB.

Azioni successive: (1) scegliere se realizzare un test coupon a due porte con switch HP3/bypass; (2) selezionare MPN esatti e S2P; (3) prova VNA e misure di blocco LF; (4) ricalcolare NF e IIP3 nel ricevitore reale; (5) ERC/DRC e layout finale.
