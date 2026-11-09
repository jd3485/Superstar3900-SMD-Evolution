# LMX2572 - Filtro d'anello provvisorio V0.6

## Topologia confermata su TI SNAS740B §8.1.11 Fig.179
- Pin 12 **CPout**: C1 verso massa; ramo R2 in serie a C2 verso massa; R3 verso pin 35.
- Pin 35 **Vtune**: C3 verso massa VCO, posizionato vicino al pin.
- Il datasheet TI richiede almeno 1.5 nF di shunt su Vtune per non degradare il phase noise VCO a offset 100 kHz-1 MHz.

## Valori di studio, NON di produzione
- **C1 = 220 pF C0G 5%; C2 = 120 nF X7R 10%; C3 = 2.2 nF C0G 5%; R2 = 620 ohm 1%; R3 = 22 ohm 1%.**
- Corrente charge pump modello = 2.5 mA, **non ancora impostata in registri TI validati**.
- Kvco nominale assunto 55 MHz/V, sensibilita usata 39-85 MHz/V (intervallo artificiale di stress, NON garanzia TI).
- N nominale 3750, range 3631-3900.

## Modello matematico
Con g=1/R3, Y_A=s*C1+1/(R2+1/(s*C2))+g, Y_B=s*C3+g, il trasferimento da corrente CP a VTUNE e Z_VTUNE=g/(Y_A*Y_B-g^2). Definendo s=j*2*pi*f:
**L(s) = Icp * Kvco / N * Z_VTUNE(s) / s**.
L'unità viene coerentemente ottenuta per Kvco in Hz/V, Icp in A.

## Risultati modello (non TI PLLatinum)
- Nominale: attraversamento 0 dB 4016 Hz, margine di fase 59.76 gradi, picco del trasferimento chiuso 1.332x.
- 4000 campioni pseudocasuali (seed 390006) con Kvco uniforme 39-85 MHz/V, N uniforme 3631-3900, Icp gaussiano sigma 8%, C1 C3 sigma 5%, C2 sigma 10%, R sigma 1%. Percentile 5% margine fase: 52.92 gradi; minimo campionato 43.97 gradi; conteggio sotto 45 gradi: 2.
- **Questi valori NON costituiscono margini garantiti**: il modello non considera spurie, non linearita, ritardi di blocchi digitali, VCO autocalibrazione, rumore di fase reale, PCB, distribuzioni PVT reali, variazioni di capacità per polarizzazione DC né C di pad.

## Decisione
Filtro **CANDIDATO esclusivamente per studio**. Prossimo gate: ricalcolo TI PLLatinum Sim o modello equivalente caratterizzato da dati TI, simulazioni di spurie/phase noise e controllo comportamento al variare della banda/core VCO. Nessuna liberatoria per produzione.

Fonte: https://www.ti.com/lit/ds/symlink/lmx2572.pdf (SNAS740B §8.1.11).
