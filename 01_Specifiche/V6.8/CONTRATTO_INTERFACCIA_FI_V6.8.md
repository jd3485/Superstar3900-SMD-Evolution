# Interfacce e stato V6.8 (RX only)

| Nodo | Sorgente | Destinazione | Stato |
|--|--|--|--|
| IF1_MIXER_RAW | U501 ADE-1+ IF pin2 (V6.5) | R801 49.9Ω + C801 | pin legacy; matching reale non verificato |
| 3V3_A_IF_SW | distribuzione V6.3 | U801 AD8338 pin15 | corrente nuova ~3mA typ a 40dB, budget da rivedere |
| IF1_AGC_OUTP/OUTM | U801 pin11/pin10 | J802 e B811...B812 | differenziale; stadi non scelti |
| IF1_TANK1/2 | risonatori LC accordabili | U802 RF pin3 | solo modello buffered; impedanze fisiche non chiuse |
| LO2_10M24_RF | J803 oscillator candidato | U802 LO pin6 | target +7 dBm non realizzato |
| IF2_455K_RAW | U802 IF pin2 | banco SW821/F821...F824/SW822 | matching e disaccoppiamenti 50→1500Ω/2000Ω da progettare |
| IF2_MODE_SELECTED | SW822 uscita | J805 demodulatori | analog demod AM/FM/USB/LSB/CW da progettare |
| IF2_BFO_MODE | J806 | futuri product detector | LO2/BFO da sintetizzare e qualificare |
| MODE_IF_CTL | sistema digitale V6.1 | filtro, LO2, mute | non allocare pin senza ECO MCU |

MUTE obbligatorio: PA, PTT, power bad, PLL1 not-lock, LO2 not-ready, filtro invalido, cambio canale, configurazione sconosciuta. La trasmissione resta fisicamente non collegata. Dual Watch commuta nel tempo; NON simultaneo. Squelch, NB, ANL e DSP continuano in sviluppo.

**Disallineamento tra grafico ideale e filtro prodotto:** il programma simula BPF Butterworth a 455kHz per i 5 modi; i codici Murata non garantiscono tale risposta esatta e gli SSB/CW non hanno ancora MPN.
