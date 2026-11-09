# MA-01 — Manuale di assemblaggio componente per componente

**Stato: struttura; la guida per ogni componente non è ancora realizzabile senza PCB/BOM definitivi.**

1. Sicurezza ESD, strumenti, stazione saldante e attrezzatura di ispezione.
2. Identificazione revisione PCB e visualizzazione dei due lati.
3. BOM univoca con ogni riferimento (Rxxx, Cxxx, Uxxx, Lxxx, Qxxx...).
4. Preparazione PCB: controllo visivo, pulizia e controllo orientamento.
5. Sequenza montaggio per gruppi: protezioni, alimentazione, logica, PLL, RX/FI, TX, ATU.
6. Scheda **per ogni riferimento**: nome e posizione, valore, package, codice produttore, foto/diagramma di orientamento, pin 1/polarità, temperatura/processo saldatura se applicabile, ispezione, prova immediata.
7. Montaggio eventuali THT, connettori, schermature, dissipatori e componenti RF critici.
8. Controlli prima della prima alimentazione, corti, polarità e correnti limitate.
9. Bring-up a step: rail, clock, logica, RX, TX solo su carico fittizio schermato e conforme.
10. Taratura oscillatori, filtri, ricevitore, wattmetro/ROS, AGC, trasmettitore, accordatore.
11. Collaudo funzionale, ambientale e diagnostica guasti tipici.
12. Tabelle accettazione qualità, rework documentato e serializzazione.

Le fotografie reali, coordinate di placement, curve di reflow, footprint e procedure di collaudo dipenderanno da componenti e PCB scelti; non sono disponibili ora.

## Nota per assemblaggio V0.6 (NON utilizzabile per montaggio)
Footprint TCXO, reflow profile, termal pad DAP e componenti di disaccoppiamento non sono ancora verificati sul PCB. Nessuna disposizione in layout definita. Non e' approvata la saldatura o accensione del modulo sulla base dei valori candidati.

## V0.9 - preparazione assemblaggio (solo pianificazione)
U2/U3 SOT-23-5; X7R 0805/0402; Y1 7N 7x5 10 pad. Non saldare in base alla bozza: footprint TXC non validato, distinta non approvata e nessun ERC.


## V1.1 - avvertenze preassemblaggio
Non montare per ora U200/F200/D200. D200 e indicato DNP; F200 non ha ancora MPN. Il pad esposto di U200 va sulla rete RTN, non a GND principale. Non sono disponibili layout validato, footprint verificato, punti di misura sicuri, ERC/DRC o prove termiche.


## V1.2 - istruzioni di NON montaggio
Non usare il footprint 1206 per F200: il package 451 e di dimensioni maggiori e richiede impronta personalizzata. D200 DNP; TCXO pin10 irrisolto; nessuna validazione pin/footprint di tutti i blocchi. Non ordinare PCB.


## Aggiornamento V1.5
J101 richiede footprint e scelta meccanica; NON assemblare o alimentare su queste sole bozze.


## V1.5.1 - Componenti aggiunti alla pianificazione
Codec audio, amplificatore microfono, circuiti analogici di filtraggio toni, MCU/DSP ed eventuale memoria esterna: **BOM, footprint, piazzole e sequenza di montaggio da definire e validare**. Non montare o ordinare sulla base delle sole specifiche.

## V1.6 - Note montaggio (non istruzioni definitive)

Previsti MCU LQFP64 e codec VQFN32 con piazzola termica: stencil, orientamento pin 1, ispezione e reflow da definire. Prima del montaggio verificare footprint specifico e separazione delle alimentazioni codec 1.8V/3.3V.
