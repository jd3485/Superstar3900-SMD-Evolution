# Revisione contratti di interfaccia V2.1

**Correzione sostanziale rispetto alla V2.0:** il collegamento FM discriminator era destinato a U202/15 IN2_L, sullo **stesso ADC sinistro** del MIC (U202/13 IN1_L). Questo non permette due acquisizioni completamente indipendenti e simultanee come ipotizzato per VOX e CTCSS/DCS.

## Nuova proposta

- Microfono su **U202/13 IN1_L**, ADC sinistro.
- Audio FM prima di de-enfasi / squelch su **U202/16 IN2_R**, ADC destro.
- **U202/15 IN2_L** lasciato libero (`no_connect` nello schema bozza V2.1).
- Accoppiamento FM via C229 = 1 uF, R208 = 1 kohm, C230 = 10 nF resta *solo preliminare*: livello, polarizzazione, impedenza e risposte reali vanno verificati in laboratorio e con configurazione register codec.

## Temporizzazione digitale proposta

- Oscillatore MCLK 12,288 MHz -> U202/1.
- Codec in master per BCLK / WCLK, SAI1 A/B nello STM32 in slave sincronizzato.
- 48 kHz, 2 slot da 32 bit -> BCLK 3,072 MHz (calcolo, non validazione con firmware).
- Gestione I2C: U202/12 SPI_SELECT a livello basso, 9/10 I2C.
- U202/30 LDO_SELECT alto per D-LDO interno, A-LDO gestito da registri (ancora non sviluppati).

## Conflitti e vincoli

Il progetto V2.1 corregge il mapping dell'ingresso FM nello schema editabile e nella mappatura CSV, **non** dimostra la correttezza della configurazione interna dei due ADC: registri del codec e software STM32 mancano. Occorre testare l'acquisizione simultanea a 48 kHz e la commutazione SAI e DMA. Gli ingressi analogici potrebbero richiedere un AFE differenziale o una compensazione DC specifica.

### Fonti di riferimento
- ST STM32G474 datasheet, tabella pin alternate function: https://www.st.com/resource/en/datasheet/stm32g474re.pdf
- TI TLV320AIC3204 datasheet, pinout e ADC: https://www.ti.com/lit/ds/symlink/tlv320aic3204.pdf
- TI codec guide SLAA404: https://www.ti.com/lit/an/slaa404/slaa404.pdf
