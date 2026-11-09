# V2.3 - Studio catena RF preselettore/LNA/mixer

**Stato: confronto matematico riproducibile, NON schema costruttivo e NON test hardware.**

## Contesto e correzione del progetto V2.2
La V2.2 ha modellato un preselettore RF complesso con perdita nel caso nominale fino a 4,52 dB prima dell'amplificatore; tale perdita deteriora direttamente la figura di rumore. Con specifiche ADL5536 @20 MHz e mixer ADE-1+ generico si stima **NF complessiva 7,05 dB**, oltre il limite interno orientativo di 6 dB. Il filtro V2.2 NON e' approvato per il primo stadio RF.

## Ipotesi V2.3 - NOTA CRITICA
Per esaminare il compromesso, si assume *solo a livello parametrico* una suddivisione di perdite nominali **1,5 dB prima** e **3,0 dB dopo** l'LNA, mantenendo il mixer ADE-1+ a 5 dB di conversion loss. Questa suddivisione **non rappresenta un filtro progettato e simulato**. Soprattutto, **la reiezione immagine di circa 69 dB calcolata per il circuito V2.2 NON e' trasferibile alla nuova disposizione**. Inoltre un filtro dopo l'LNA protegge il mixer, ma NON protegge l'LNA da segnali fuori banda elevati.

## Dati di partenza dei componenti (tipici; verificare a 27 MHz)
- Analog Devices ADL5536, @20 MHz: guadagno 20,2 dB; NF 2,5 dB; OIP3 +39,5 dBm; alimentazione 5 V / ca. 105 mA.
- Analog Devices ADL5535, @20 MHz: guadagno 16,7 dB; NF 3,0 dB; OIP3 +41,5 dBm; alimentazione 5 V / ca. 97 mA.
- Mini-Circuits ADE-1+ mixer SMT: conversion loss tipica 5 dB; IIP3 indicativa +15 dBm; richiede LO +7 dBm; **NF mixer assunta pari alla perdita**, semplificazione non validata per singola banda laterale.
- Mini-Circuits ADE-1H+: livello LO +17 dBm, IIP3 tipico +23 dBm; caso G solo teorico; richiede una catena LO diversa e non e' compatibile con +7,3 dBm stimati nella revisione V0.4.

## Confronto dei 7 scenari nominali
| Scenario | NF (dB) | IIP3 (dBm) | Guadagno netto (dB) |
|---|---:|---:|---:|
| A | 7.05 | -0.72 | +10.70 |
| B | 4.12 | -0.73 | +10.70 |
| C | 4.74 | +2.78 | +7.20 |
| D | 5.50 | +8.72 | +1.20 |
| E | 4.53 | +5.18 | +4.70 |
| F | 9.50 | +19.50 | -9.50 |
| G | 4.76 | +10.68 | +6.90 |

Il parametro IIP3 rappresenta un'estrapolazione di terz'ordine in condizioni ideali, non specifica la tenuta a bloccanti vicini né la compressione. Un'alta IIP3 non assicura assenza di mixing reciproco da rumore PLL.

## Possibile architettura provvisoria
1. Ingresso antenna, protezioni e commutazione RX/TX (non progettate).
2. Preselettore RF **low-loss** prima dell'LNA; obiettivo di studio perdita <= 1,5 dB, da dimostrare con adattamento e selettività.
3. Stadio SMD candidato **ADL5535** su percorso opzionalmente bypassabile, senza scelta definitiva.
4. Pad commutabile ~6 dB **dopo** LNA per contenere livello verso il mixer quando necessario; non evita sovraccarico dell'LNA.
5. Filtraggio selettivo tra LNA e mixer. Le caratteristiche di reiezione immagini sono ignote finche' non saranno riprogettate le reti passive.
6. Mixer ADE-1+ con pilotaggio LO e isolamento da verificare; FI 10,695 MHz provvisoria.
7. Percorso bypass LNA/attenuazione RF in ingresso in caso di interferenze forti (controlli e soglie da progettare).

## Equazioni riproducibili
Con guadagni lineari G e fattori di rumore F (F >=1), la figura di rumore totale segue Friis:

`Ftot = 1 + SUM_i((Fi-1) / PRODUCT_(j before i)(Gj))`

con `NF_dB=10 log10(Ftot)`. Un attenuatore ideale a temperatura di riferimento ha `F=L` e `G=1/L` (valori lineari).

Per stadi non lineari con IIP3 misurata in mW e stadi precedenti con guadagno di potenza G:

`1 / IIP3_total_mW = SUM_i(G_pre_i / IIP3_i_mW)`

**Le formule di IIP3 presuppongono segnali e intervalli in cui l'estrapolazione cubica e' applicabile**. Per i mixer RF a 10 kHz di separazione e in presenza di bloccanti occorrono prove specifiche.

## Analisi incertezza
Lo script effettua 2000 variazioni pseudocasuali *illustrative* per quattro configurazioni; variazioni modellate: +/-0,5 dB filtro ingresso, +/-0,8 dB post filtro, +/-0,8 dB guadagno LNA, +/-0,5 dB NF LNA, +/-3 dB OIP3 LNA e mixer, +/-0,8 dB perdita mixer. Le estrazioni non sono distribuzioni industriali documentate e NON quantificano rendimento produttivo, affidabilita' o probabilita' reali.

## Gates per la V2.4 e successive
- Scegliere topologia/banchi di preselettore per sei bande, con componenti C0G e induttori Q misurabile a 27 MHz.
- Modellare **S11/S21 a 25,615..28,305 MHz** e immagine **47,005..49,695 MHz**, inclusi parassiti, commutatori RF e corrente di ritorno.
- Preservare la protezione dell'LNA contro immagini e radio vicine: separare specifiche di **blocking pre-LNA** e di attenuazione **pre-mixer**.
- Validare guadagno/NF/IIP3/P1dB reali a 27 MHz, LO +7 dBm, IF, stabilita' e isolamento.
- Verificare ergonomia RF Gain, percorso bypass LNA, attenuazione RF ingresso e protezioni di trasmissione.
- Progettare schemi KiCad effettivi, completare ERC/DRC e collaudo su PCB con VNA e generatori calibrati.

## Fonti primarie, consultate il 7 novembre 2026
- ADL5535, datasheet tabella a 20 MHz: https://www.analog.com/media/en/technical-documentation/data-sheets/ADL5535.pdf
- ADL5536, datasheet tabella a 20 MHz: https://www.analog.com/media/en/technical-documentation/data-sheets/ADL5536.pdf
- ADE-1+, scheda Mini-Circuits: https://www.minicircuits.com/WebStore/dashboard.html?model=ADE-1%2B
- ADE-1H+, scheda Mini-Circuits: https://www.minicircuits.com/WebStore/dashboard.html?model=ADE-1H%2B
