# V6.0 — pinout interfacce candidate (DA TRASCRIVERE IN SCHEMATICO)

Il file `CIRCUITO_COMPONENTI_AUDIO_PA_V6.0.json` e la `NETLIST_PIN_AUDIO_PA_V6.0.csv` sono le fonti numeriche del progetto. Ogni numero del connettore è assegnato una volta. Nessuna piedinatura fisica del connettore è approvata come footprint.

| Connettore | Pin | Segnale |
|---|---:|---|
| J601 MIC/PTT | 1/2/3/4 | MIC_SIGNAL / MIC_RETURN / PTT_N / SHIELD_CHASSIS |
| J602 speaker radio | 1/2 | RADIO_SPK_P / RADIO_SPK_N (BTL, nessun GND) |
| J603 PA esterna | 1/2 | PA_SPK_P / PA_SPK_N (BTL, nessun GND) |
| J605 demod RX | 1–6 | AM / FM / USB / LSB / CW / AGND |
| J606 codec | 1–6 | CODEC_ADC_L / CODEC_ADC_R / CODEC_DAC_L / CODEC_MICBIAS / AGND / RISERVATO NO CONNECT |
| J604 controllo | 1–16 | 3V3_AF / 13V8_AUD / AGND / PGND / MUX_A0 / MUX_A1 / MUX_A2 / MUX_EN_N / PA_RELAY_CMD / AMP_SD / AMP_FAULT_N / PA_MODE_HW / PTT_N / CODEC_READY / POWER_GOOD / SHIELD_CHASSIS |

**Nessun pin TX/RF è attivo nel modulo audio/PA.** Il pin riservato J606.6 non deve essere reinterpretato come permesso di modulazione o di trasmissione.
