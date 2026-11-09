# V1.9 - alimentazioni e front-end audio, BOZZA

## Problema individuato V1.8
La rail `5V_AUX_PROTECTED` non corrisponde alla denominazione realmente prodotta dal blocco buck precedente (`5V_RF_PREREGULATED`). La V1.9 sostituisce la rail orfana con `5V_DIGITAL_FILTERED`, alimentata nel foglio MCU/audio dal bead FB201 a partire da `5V_RF_PREREGULATED`. Rimane da fare l'**integrazione gerarchica effettiva** tra i progetti KiCad: i nomi da soli non costituiscono una netlist nativa verificata.

## Regolatori SMD proposti (non approvati)
- U203 esistente: TPS7A2033, 3V3_AUDIO_CLK, dal 5V_DIGITAL_FILTERED.
- U204 nuovo: TPS7A2033, 3V3_MCU, dal 5V_DIGITAL_FILTERED.
- U205 nuovo: TPS7A2033, 3V3_CODEC_IO, dal 5V_DIGITAL_FILTERED.
- U206 nuovo: TPS7A2033, 3V3_CODEC_LDOIN, dal 5V_DIGITAL_FILTERED.
- C221-C226: condensatori 1uF ingressi/uscite LDO. TPS7A20 necessita selezione di condensatori, tolleranze, ESL e layout secondo datasheet.
- FB201 600 ohm @100MHz **solo modello candidato**: definire corrente DC, resistenza, dissipazione, impedenza reale e spunto. C219 10uF + C220 100nF sul 5V filtrato; attenzione risonanze e stabilità in combinazione con bead.
- Codec U202: AVDD/DVDD sono uscite di filtro interne quando LDO abilitati; non collegare a 3,3 V. Pin 30 LDO_SELECT ora tramite R206 4,7k a 3V3_CODEC_IO, seguendo TI SLAA404C.
- Resta aperta decisione di un regolatore dedicato MCU VDDA/VREF+, per ora `3V3_ANA_MCU` non realmente alimentata.

## Ingressi analogici
- Microfono preamplificato esterno -> C227 1uF -> R207 1k -> U202 IN1_L; C228 4,7nF a massa dal lato ingresso ADC. **Non è ancora il preamplificatore microfonico** e non include limitatore e protezione ESD finale.
- Discriminatore FM RAW -> C229 1uF -> R208 1k -> U202 IN2_L; C230 10nF a massa. La FM raw deve essere prelevata **prima di filtro voce e de-enfasi** per conservare CTCSS/DCS. Guadagno, ampiezza massima, impedenza di sorgente, distorsione e ingresso ADC da misurare/validare.
- RC 1k/10nF: fc ideale 15,9kHz, non sostituisce filtro di anti-alias; a 67-254Hz la perdita ideale e' trascurabile. C di accoppiamento 1uF/20k nominale: fc circa 8Hz se codec input effettivamente 20k, dipende dalla configurazione PGA.

## Vincoli e blocchi prima di fabbricazione
1. KiCad CLI assente: ERC/DRC non eseguiti. Non attribuire valenza elettrica ai soli test di stringhe o geometria.
2. Pin-to-footprint, pinout effettivo LDO e passivi ancora da validare con ordinazione MPN precisa.
3. Collegamento gerarchico a buck 5V, alimentazione MCU analogica, protezione ingresso TVS/fusibile, massa e ferrite con correnti nominali.
4. Audio ADC full-scale e margini, toni CTCSS 67-254Hz, dati DCS e interferenze elettriche.
5. SAI master codec / slave MCU hardware e configurazione registri, plus sequenza di reset e accensione.
6. Misure rumore audio, spurie 12,288MHz e armoniche con radio ricevente a basso livello.

## Fonti
- ST STM32G474RE: https://www.st.com/resource/en/datasheet/stm32g474re.pdf
- ST RM0440 SAI slave: https://www.st.com/resource/en/reference_manual/rm0440-stm32g4-series-advanced-armbased-32bit-mcus-stmicroelectronics.pdf
- TI TLV320AIC3204 SLOS602E: https://www.ti.com/lit/ds/symlink/tlv320aic3204.pdf
- TI SLAA404C AIC3204 config: https://www.ti.com/lit/an/slaa404c/slaa404c.pdf
- TI TPS7A20: https://www.ti.com/lit/ds/symlink/tps7a20.pdf
