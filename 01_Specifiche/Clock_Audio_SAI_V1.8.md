# Clock audio, V1.8 - decisione tecnica e verifiche

**Stato:** bozza per verifica; nessun ERC, SPICE, PCB, misura realizzata.

## Errore di architettura corretto rispetto alla V1.7
La V1.7 ipotizzava oscillatore indipendente da 12.288 MHz al codec e STM32 master dei clock SAI. Due domini di clock non coerenti portano a perdita/duplicazione di campioni se non vi e' ASRC o recupero di clock. **Decisione V1.8:** codec TLV320AIC3204 come **master BCLK/WCLK** derivati dallo stesso clock 12.288 MHz; STM32G474 SAI1 A slave (RX/TX full-duplex tramite blocco B sincrono, configurazione effettiva da verificare in STM32CubeMX e hardware). Direzione delle reti cambia, etichette no.

## Clock di riferimento e calcoli nominali
- X201 candidato: SiTime SiT8008AI-22-33E-12.288000, SMD 3.2x2.5, 3.3 V, OE, +/-25 ppm a condizioni dichiarate. Non ancora acquistato o misurato; EMI e jitter reale da validare.
- Per **Fs = 48 kHz**, rapporto **MCLK/Fs = 256**, slot audio **2 x 32 bit**, BCLK **3.072 MHz**, rapporto MCLK/BCLK **4**.
- Configurazione modello senza PLL del codec: NDAC=1, MDAC=2, DOSR=128, NADC=1, MADC=2, AOSR=128: 12.288 MHz / (1*2*128) = 48 kHz. Opzione clock master BCLK via divisore 4; implementazione registri, sequenza di abilitazione e clock tree da convalidare contro TI SLAA404C e reference guide. NON scrivere ancora firmware di configurazione reale da questi dati.
- Frequenze nominali calcolate, non misurate.

## Collegamenti KiCad aggiunti (bozza)
- U203 TPS7A2033PDBVR: pin1 IN => `5V_AUX_PROTECTED`, pin2 GND, pin3 EN=> `5V_AUX_PROTECTED`, pin4 NC, pin5 OUT=> `3V3_AUDIO_CLK`.
- X201 SiT8008: pin1 OE=> `XO_OE`, pin2 GND, pin3 OUT=> `XO_MCLK_RAW`, pin4 VDD=>`3V3_AUDIO_CLK`.
- R204 4.7k da `3V3_AUDIO_CLK` a `XO_OE` (pullup OE), R205 33R da `XO_MCLK_RAW` a `AUDIO_MCLK_12M288` (resistenza di smorzamento candidata, da ottimizzare secondo PCB e fronte CMOS).
- C215 1uF ingresso LDO; C216 1uF uscita; C217 100nF e C218 1uF sull'alimentazione XO.
- `5V_AUX_PROTECTED` e' solo contratto di rete: collegamento al progetto generale DA ESEGUIRE. Pin codec MCLK e X201 OUT sono sulla stessa rete *attraverso R205*. I nomi di rete non sostituiscono la verifica elettrica.

## Criticita' aperte prima del PCB
1. Controllare con **KiCad ERC** simboli custom e pin passive/power, esportare netlist nativa; assegnare footprint del componente ordinato ed eseguire DRC.
2. Verificare realmente i quattro pin dello specifico ordine SiTime e la polarita' OE; la stima jitter non e' una misura EMI.
3. Confrontare MCU SAI slave 32-bit stereo e codec master clock output in STM32CubeMX; latenza di avvio codec e reset.
4. Confermare registri TI di clock, bit BCLK, NDAC, MDAC, AOSR/DOSR e ADC routing, nella revisione firmware successiva.
5. Aggiungere regolatori separati 3V3 MCU/codec, consolidare collegamento `5V_AUX_PROTECTED`, quantificare correnti e termica (circa 8.5 mW dissipati per ogni 5mA nel LDO da 5V a 3.3V).
6. Verificare ref clock, ringing, clock return paths e spurie RF durante TX e RX su PCB di prova. CTCSS/DCS devono essere letti prima dei filtri audio voce.

## Fonti verificabili
- TLV320AIC3204, TI: https://www.ti.com/lit/ds/symlink/tlv320aic3204.pdf
- TI SLAA404C, configurazione clock e alimentazioni: https://www.ti.com/lit/an/slaa404c/slaa404c.pdf
- SiTime pagina prodotto: https://www.sitime.com/products/mhz-oscillators/lvcmos-oscillators/sit8008
- SiTime versione candidata: https://www.digikey.com/en/products/detail/sitime/SIT8008AI-22-33E-12-288000/11352695
- TPS7A20 TI datasheet: https://www.ti.com/lit/ds/symlink/tps7a20.pdf
