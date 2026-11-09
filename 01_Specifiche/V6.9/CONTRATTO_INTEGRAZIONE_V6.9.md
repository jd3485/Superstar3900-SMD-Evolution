# Contratti V6.9 con revisioni precedenti

| Collegamento | Fonte | Destinazione | Stato |
|---|---|---|---|
| REF_12M8_BUFFERED | TCXO / fanout V6.4 da realizzare | U971 CLKIN pin6 | FUTURO BUFFER |
| 3V3_LO2 | V6.3 distribuzione da aggiornare con budget | U971 VDD + VDDO | ECR ALIMENTAZIONE |
| CODEC_I2C_SCL/SDA | STM32 PB6/PB7 | U971 pin4/5 + codec + 2 expander | I²C indirizzi e pullup da valutare |
| LO2_EN_HARDWARE_GRANTED | V6.2 condizioni RX hardware + MCU PC12 | Q971/R977 | HARDWARE LOGIC PENDING |
| LO2_INTR_N | U971 pin3 open drain | MCU PB11 candidato | ECO V6.1 |
| LO2_RF_7DBM_PENDING | B971 driver LO2 da scegliere | U802 ADE-1+ LO pin6 | **NESSUNA USCITA ATTUALE** |
| IF2_SSB_CW_FILTERED | V6.8 F823/F824 non selezionati | B981 ±IF2, U981, audio | INTERFACCIA SOLO CANDIDATA |
| IF2_AM_FILTERED | V6.8 F822 storico Murata | D991 envelope | matching e sensibilità aperti |
| IF2_FM_FILTERED | V6.8 F821 storico Murata | B991/B992 quadratura | LIMITER/DISCRIM NON SELEZIONATI |
| AUDIO di AM FM USB LSB CW | J982 J992 J994 | V6.0 ingresso multiplex codec ADC_R | livello e qualità audio da validare |
| TX | nessuna | nessuna | NO CONNECTION / NO LICENSE |

**Sequenza:** durante qualsiasi cambio modo o canale `mute=ON`, CLK OEB alto, aggiornamento I²C, verifica lock/status e guardia HW, poi rilascio. Il modello firmware non abilita mai RF TX.

**Nota fondamentale:** le simulazioni numeriche digitali non rappresentano prove dell'AD8338, degli IF filter Murata, di TS5A3157 con buffer reale, della tensione del riferimento CLKIN o delle interferenze fra oscillator PLL1 e PLL2.
