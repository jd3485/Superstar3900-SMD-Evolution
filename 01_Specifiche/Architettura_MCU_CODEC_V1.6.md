# V1.6 - Architettura microcontrollore e audio/DSP (bozza verificabile)

**Stato: progetto di interfacce e software prototipale. NON e' ancora schema elettrico esecutivo.**

## Candidati selezionati, non approvati per acquisto
- **U_MCU: ST STM32G474RET6**, Arm Cortex-M4F 170 MHz, 512 KB Flash, 128 KB SRAM nominali, acceleratori CORDIC/FM(A)C, SAI/I2S, SPI e I2C. Package previsto LQFP64: pin assignment/alternate functions/clock tree ancora da validare usando ST datasheet + CubeMX.
- **U_CODEC: TI TLV320AIC3204IRHBR** (VQFN32), stereo ADC/DAC e I2S per due ingressi MIC/DEMOD_FM e due uscite TX_AUDIO/RX_AUDIO; controllo I2C. Da verificare livelli, passivi, disponibilita', clock e pinout esatto del package.
- **Elettronica audio completamente SMD** con disaccoppiamento e partizioni analogico/digitale; controlli, connettori e RF di potenza saranno scelti in base a prestazioni.

## Motivazioni e limiti
- Un RX analogico filtra RF/FI; la sezione DSP modifica solo l'audio in banda base, non sostituisce l'AGC RF e la selettivita' dei filtri.
- Il CTCSS/DCS RX richiede un **prelievo dal discriminatore FM prima dei filtri voce passa-alto**; l'altoparlante deve sopprimere la componente subaudio.
- PA e' solo amplificazione audio, con inibizione hardware della RF.
- Dual Watch e' una scansione alternata A/B con **un solo RX**, con freeze su canale occupato; la TX e' solo sul canale A e soggetta alle autorizzazioni. CH9 prevale.
- Il percorso microfonico e quello di ricezione richiedono anti-alias analogico, livelli di ingresso corretti e protezioni; non ancora dimensionati.

## Pipeline a 48 ksample/s (profilo preliminare)
- Codec ADC L: microfono; codec ADC R: segnale dal discriminatore FM (NON audio altoparlante gia' filtrato).
- DMA I2S doppio buffer: 10 ms = 480 frame stereo; RX e TX hanno ciascuno 480*2*2=1920 byte per frame a 16 bit; totale buffer doppio RX+TX = 7680 byte.
- Codec DAC L: audio modulatore TX da catena limitata e con eventuale mix subaudio; codec DAC R: audio RX filtrato / monitor / PA, pilotando amplificatore esterno.
- VOX: energia di MIC con attacco e isteresi, con interblocco RF; non trigger dall'audio dell'altoparlante.
- Roger Beep: solo prima di chiudere TX quando consentito, temporizzazioni e spettro ancora da dimensionare.
- Echo: delay TX disinseribile, prova di fattibilita' a 250 ms / 48 kHz mono / 16 bit -> 24.000 byte; buffer in SRAM con permessi DMA da studiare.
- CTCSS: filtro subaudio 50-300 Hz, rivelatore a finestra, TX subaudio FM prima del modulatore; prova numerica su 50 toni in 8 ksps, non decodifica su hardware.
- DCS: specifica 104 codici N/I; **non ancora implementato** framing, sincronismo, correzione errori, rivelazione: non confondere con test CTCSS.

## Alimentazione (vincolo bloccante)
- MCU: VDD nominale +3V3_MCU con LDO dedicato separato dal +3V3_PLL e dal +3V3_TCXO; corrente e filtraggio da misurare.
- Codec: IOVDD 3,3 V ammissibile; LDOIN 3,3 V ammissibile. I nuclei AVDD e DVDD richiedono circa 1,8 V (alimentazioni esterne o LDO interni secondo schema TI). **NON collegare AVDD/DVDD direttamente a 3,3 V.** Sequenza di power-up e RESET da datasheet/TI SLAA557.
- Massa PCB continua con layout suddiviso funzionalmente; impedire che i ritorni di clock/DMA digitali attraversino i nodi audio/RF sensibili. Non creare masse isolate senza analisi del ritorno.

## Budget di interfacce, da assegnare a pin reali in fase successiva
- LMX2572 SPI monodirezionale: CLK, DATA, CSB; CE output; MUXout input.
- Audio codec: I2S_BCLK, I2S_LRCLK, I2S_SDOUT, I2S_SDIN, eventuale MCLK; I2C_SCL, I2C_SDA, RESET output.
- PTT, CH9, ALFA, PA, BAND, CANALE, RF_GAIN, SQUELCH, VOX, DW, RB, ECHO, protezioni, sensori, display, SWD.
- Nessun pin specifico STM32 viene dichiarato assegnato in questa revisione: priorita' e verificare assenza di conflitti SAI/I2S/SPI e disponibilita' dei timer.

## Criteri di accettazione successivi
1. Aprire schema KiCad ed esportare netlist/E RC senza errori bloccanti.
2. Collegare correttamente codec (tutti i pin), clock, pin di configurazione, LDO interni, condensatori, sequenza RESET.
3. Dimostrare sulla scheda campione SNR e spurie/clock compatibili con RX sensibile, e latenza audio.
4. Test automatici in HIL per commutazione CH9 e blocco TX; mai test RF con antenna finche' non qualificato.
5. Provare CTCSS/DCS contro generatori e apparati campione. I test sintetici V1.6 verificano soltanto l'algoritmo CTCSS dimostrativo.

## Fonti primarie
- ST STM32G474RE: https://www.st.com/en/microcontrollers-microprocessors/stm32g474re.html
- TI TLV320AIC3204: https://www.ti.com/product/TLV320AIC3204
- TI Application Reference Guide: https://www.ti.com/lit/ml/slaa557/slaa557.pdf
- TI LMX2572: https://www.ti.com/product/LMX2572
- Tabella toni CTCSS (50): https://keyandcarrier.com/tools/ctcss-dcs/
