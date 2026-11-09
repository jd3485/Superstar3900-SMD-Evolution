# V2.2 - Piano di registri per due ADC simultanei, NON firmware validato

## Obiettivo
- Microfono collegato a U202/13 `IN1_L` -> ADC sinistro.
- Discriminatore FM collegato a U202/16 `IN2_R` -> ADC destro.
- 48 kHz, 2 canali a 32 bit, interfaccia I2S con BCLK = 3,072 MHz e WCLK = 48 kHz. Il codec e' master dei clock; SAI1 STM32 e' slave. MCLK esterno 12,288 MHz.

## Sottoinsieme dei registri (TI SLAA557 e SLAA404C)
L'ordine completo dell'accensione / clock / LDO / RESET resta da chiudere prima di provare i registri seguenti. Tutti i valori qui sono esempio di studio, non sequenza di bootstrap da caricare direttamente.

| Pagina | Registro (dec) | Valore | Funzione |
|---|---:|---:|---|
| 1 | 52 | `0x80` | IN1_L -> L MICPGA via 20 kohm |
| 1 | 54 | `0x80` | CM1L -> L MICPGA ingresso negativo 20 kohm |
| 1 | 55 | `0x20` | IN2_R -> R MICPGA via 20 kohm: D5:D4=`10` |
| 1 | 57 | `0x80` | CM1R -> R MICPGA negativo 20 kohm |
| 1 | 59 | `0x0C` | Sblocco PGA sinistro, compensazione nominale 6 dB |
| 1 | 60 | `0x0C` | Sblocco PGA destro, compensazione nominale 6 dB |
| 0 | 81 | `0xC0` | Alimentazione ADC sinistro e destro **solo dopo configurazione clock valida** |
| 0 | 82 | `0x00` | Unmute ADC sinistro e destro |

Verificare readback I2C e campionamento simultaneo con due sinusoidi di frequenza diversa (es. 1 kHz sul mic e 100 Hz sulla via FM). Confermare ritardi, guadagni e accoppiamento tra canali su prototipo.

**Rischi:** modalita' LDO e alimentazioni interne gia' aperte nelle V1.9/V2.1; disturbi da clock; aggancio dei segnali di subaudio CTCSS/DCS al discriminatore.
**Fonti:** https://www.ti.com/lit/pdf/slaa557 ; https://www.ti.com/lit/an/slaa404c/slaa404c.pdf
