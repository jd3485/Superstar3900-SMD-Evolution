# V2.7 - Valori commerciali nel preselettore RX

**Ambito:** 25,615-28,305 MHz RX; immagine 47,005-49,695 MHz; filtro di studio HP5 Butterworth 18 MHz + LP9 Chebyshev 29,5 MHz, 0,1 dB ripple, 50 Ohm. Il progetto finale del ricevitore resta da sviluppare.

## Conclusioni
- La V2.6 considerava bobine fino a 270 nH, ma la rete LP9 della V2.4 richiede fino a 595 nH. Sono stati introdotti candidati Coilcraft 330/560 nH.
- Il nuovo confronto E12 ed E24 usa valori discreti di L e C, non ancora MPN finali per tutti i condensatori.
- La rete con valori E24, nel modello Q=60, peggiora la perdita e S11 rispetto alla rete ideale; E12 perde selettivita' sulle frequenze immagini ma e' piu' semplice da reperire.
- A Q=20-30 le perdite diventano troppo elevate: Q a 27 MHz non e' documentato dai dati di catalogo. 560 nH Coilcraft Qmin=23 @50MHz, non 27MHz.
- I risultati Monte Carlo utilizzano Q comune uniforme 20-60, condensatori indipendenti ±2% e bobine indipendenti ±5% (solo assunzioni). Le frequenze e i coefficienti di perdita del componente reale sono assenti.

## Limiti e approvazione
Nessun S2P importato, nessuna simulazione SPICE effettivamente eseguita, niente ERC/DRC su questi filtri, niente misure VNA; valori C0G generici da trasformare in codici esatti; topologia HP5+LP9 a 14 passivi non e' ancora ottimizzata con i veri Q. **NO GO per PCBWay.**

## File
- `07_Componenti/BOM_Preselettore_Valori_Commerciali_V2.7_BOZZA.csv`
- `03_Verifiche/V2.7/Confronto_Quantizzazione_V2.7.csv` e `Stress_Componenti_Commerciali_V2.7.csv`
- `04_KiCad/Architettura_RX_V2.7/*.cir`: netlist SPICE non ancora eseguite
- `01_Specifiche/Piano_Misura_Preselettore_50ohm_V2.7.md`: piano prototipo e test VNA.
