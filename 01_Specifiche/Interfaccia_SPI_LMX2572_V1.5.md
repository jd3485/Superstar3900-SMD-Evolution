# Interfaccia SPI - Revisione V1.5 (BOZZA)

## Fonte primaria
TI LMX2572, SNAS740B Rev.B, §6.6-6.7 e §7.5: https://www.ti.com/lit/ds/symlink/lmx2572.pdf

Il trasferimento usa 24 bit MSB-first: 1 bit R/W + 7 bit indirizzo + 16 bit dati.
Su scrittura R/W=0; il dato su SDI viene acquisito sul fronte di salita di SCK.
Su lettura R/W=1; MUXout fornisce i dati dal fronte di discesa dell'ottavo impulso secondo la temporizzazione TI.
Il software fornito in questa versione codifica SOLO frame, non campiona MUXout.

## Pin e direzioni
| J101 | Rete | U1 LMX2572 | Direzione vista dall'LMX2572 |
|--|--|--|--|
| 1 | PLL_SCK | pin 16 | ingresso |
| 2 | PLL_SDI | pin 17 | ingresso |
| 3 | PLL_CSB | pin 24 | ingresso (chip select attivo basso) |
| 4 | PLL_CE | pin 1 | ingresso (enable attivo alto) |
| 5 | PLL_MUXOUT | pin 20 | uscita multifunzione |
| 6 | GND_MAIN | ritorno | massa |

**I/O 3,3 V: non collegare direttamente logica 5 V.** La selezione del microcontrollore,
protezioni ESD, pull-up/pull-down, resistenze serie, forma d'onda e footprint J101
sono **non risolti**. La scheda PLL non ha ancora un percorso di controllo completo qualificato.

## Procedura di accensione documentata da TI
1. Alimentazioni presenti e stabilizzate.
2. CE alto.
3. Attesa di almeno 500 microsecondi per LDO interni.
4. Riferimento OSCin valido.
5. Scrittura R0 con RESET=1 (bit e resto del valore da profilo convalidato).
6. Scrittura registri dal 125 a 0, con valori definitivi validati.

Non sono qui fornite parole esadecimali dei registri: devono essere generate e controllate
per TCXO, divisione, uscite, calibrazione, condizioni di avvio e spettro RF.
Durante lock, evitare toggling SCK/SDI non necessario: TI indica possibile peggioramento del rumore di fase.

## Controlli software vs elettrici
- test_spi_transport_v15.py: struttura delle parole e ordine di invio con dati sintetici.
- test_spi_interface_v15.py: presenza di pin, nomi e rete root/leaf.
- NON eseguiti: KiCad ERC/netlist, timing elettrico SPI, simulazione EMI, misure con oscilloscopio e analizzatore di spettro.

## Collegamenti ancora bloccanti
TCXO Y1 pin 10 AFC/GND, CE all'avvio, MUXout configurazione, J101 footprint e host MCU, layout di ritorno segnali digitali, isolamento della parte RF, filtri di alimentazione, ERC.
