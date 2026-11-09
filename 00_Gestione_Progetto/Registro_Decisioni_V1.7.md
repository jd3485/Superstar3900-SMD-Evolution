# Decisioni V1.7
- Confermati come candidati STM32G474RET6 LQFP64 e TLV320AIC3204 RHB32 (non acquistare ancora).
- Codec su I2C (SPI_SELECT=0); DAC/ADC su SAI1 a 48 kHz con due blocchi in sync; verifica STM32CubeMX da fare.
- Codec in uso con LDO interni, 3.3V solo su IOVDD e LDOIN, non su AVDD/DVDD.
- MCLK 12.288MHz da oscillatore a parte: sorgente non implementata.
- R201 pulldown su RESET del codec per mantenere condizioni sicure finché MCU non lo rilascia.
- Avanzamento complessivo stimato 26% (dal 25%): NON rappresenta un collaudo.
