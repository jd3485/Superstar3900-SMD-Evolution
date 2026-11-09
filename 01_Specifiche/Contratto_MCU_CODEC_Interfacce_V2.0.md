# Contratto d'interfaccia digitale e audio - V2.0

Stato: **preliminare - da validare contro STM32G474RET6 alternate-function table e programma STM32CubeMX**.

| Linea | Verso codec TLV320AIC3204 | Stato V2.0 |
|---|---|---|
| AUDIO_MCLK_12M288 | pin 1 MCLK ingresso | Oscillatore esterno, schema V1.8 |
| AUDIO_BCLK | pin 2 BCLK, uscita master | MCU deve usare SAI slave RX/TX - da verificare AF e DMA |
| AUDIO_WCLK | pin 3 WCLK, uscita master | LRCK 48 kHz - da verificare AF |
| AUDIO_I2S_TX | pin 4 DIN, ingresso del codec | PCM da MCU, controllare formati e polarita |
| AUDIO_I2S_RX | pin 5 DOUT, uscita del codec | PCM verso MCU, controllare formati e polarita |
| CODEC_I2C_SCL/SDA | pin 9/10 | pull-up previsti, firmware I2C da scrivere |
| CODEC_RESET_N | pin 31 RESET | tenere basso durante avvio alimentazioni e clock |
| MIC_CODEC_IN | pin 13 IN1_L | filtro passivo, sensibilita/impedenza programmabili |
| FM_CODEC_IN | pin 15 IN2_L | conserva subaudio prima della de-enfasi |

**Formato desiderato**: 48 000 campioni/s, 2 canali, 32 bit per slot, BCLK 3,072 MHz; word clock 48 kHz, MCLK 12,288 MHz. Devono essere verificati gli alternate function dello STM32 (no conflitti di pin), e la modalita codec master.

**Bloccanti**: non eseguito KiCad ERC, clock e ADC non provati fisicamente, sorgenti d'ingresso senza dati di impedenza/livello, nessuna regolazione codec via I2C validata.
