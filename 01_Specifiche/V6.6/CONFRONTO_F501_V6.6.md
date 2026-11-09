# V6.6 — Decisione preliminare su F501, senza fabbricazione

## Opzione A: rete discreta L/C a tre risonatori (8 elementi L/C)

Componenti previsti: L601/L603 2,0µH, L602 22nH; C601+602 16+1,5pF, C603+604 1500+91pF, C605+606 16+1,5pF. 50Ω sorgente/carico; analisi Python senza estrazioni EM né MPN certificati. Il modello a QL=60, QC=400 e C_FEED=0,05pF restituisce **IL RX max 5.59dB**, **RL minimo 6.18dB**, reiezione immagine relativa minima **47.96dB**. NON soddisfa il target interno preliminare RL>=10dB. Necessita di ottimizzazione, fisica e misure.

Nelle 4.000 variazioni indipendenti esplorative (L ±5%, C ±2%, QL 30–110, QC 300–700, SRF serie 55–150MHz, C_FEED 0–0,5pF), **46.83%** dei casi ha max perdita RX >6dB; **71.95%** dei casi ha reiezione relativa minore di 40dB; **96.85%** ha return loss minimo <10dB. Non sono probabilità reali: le distribuzioni sono arbitrarie e non derivano da produzione.

## Opzione B: filtro schermato SMD commerciale Mini-Circuits SXBP-27R5+

**Candidato preferenziale per la prossima integrazione** in assenza di un L/C discreto qualificato. Il datasheet ufficiale dichiara (a 25°C, 50Ω):

|Voce|Produttore|
|---|---|
|Banda utile|24–31MHz: comprende 270/270 frequenze RX 25,615–28,305MHz|
|Perdita di inserzione utile|1,3dB tipica, **2,5dB max** in banda| 
|Banda di stop superiore|39–900MHz: include 47,005–49,695MHz|
|Attenuazione stop superiore|**20dB min**, 31dB tipica sull'intera banda dichiarata (NON 50dB garantiti)|
|VSWR in banda|1,4 tipico; 1,7 max|
|Package|HF1139, circa 18,8×11,18×6,86mm (verificare spazio meccanico)|
|Pad|1 IN, 8 OUT, 2–7 GND|
|Potenza RF massima ingresso|0,25W; verificare ESD e protezione RX TX esterna|

Questa è una **scheda tecnica commerciale, non una simulazione del filtro**; non è stata scaricata una matrice S2P né estratto un modello equivalente. Il valore **20dB minimo di soppressione garantita in stopband** non soddisfa automaticamente un possibile obiettivo di sistema superiore (es. 40dB); si dovrà verificare se occorre uno stadio aggiuntivo, senza sommare ingenuamente dB in presenza di mismatch. Nessuna portata anti-blocker, noise figure globale o intermodulazione è garantita in questa fase.

**Riferimenti:**
- https://www.minicircuits.com/pdfs/SXBP-27R5%2B.pdf
- https://www.minicircuits.com/WebStore/dashboard.html?model=SXBP-27R5%2B
- https://www.minicircuits.com/pdfs/ADE-1%2B.pdf

## Gate non superati

- Non approvata **né A né B** per produzione (NO FAB). In B definire footprint originale vendor HF1139 e prove 50Ω, adattamento e protezione dell'ingresso.
- Il driver LO +7dBm, l'ordine relativo a LNA/protezione RX, il filtro FI 10,695MHz e le prove di blocker non sono chiusi.
- La posizione di F501 nel front-end storico va riconciliata prima del PCB; non modificare alla cieca il V5.8.
- Non selezionare B solo in base ai 31dB tipici: usare il minimo garantito e simulazioni di sistema con livelli interferenti.
