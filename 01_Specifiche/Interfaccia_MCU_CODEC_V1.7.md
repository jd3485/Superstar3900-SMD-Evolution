# Interfaccia MCU e CODEC - V1.7 (DRAFT)

Stato: bozza di connessione **non validata mediante ERC o layout**. Lo schema `.kicad_sch` contiene simboli locali e riferimenti di rete, ma i footprint sono lasciati vuoti intenzionalmente: NON usarlo per inviare una PCB.

## Scelte architetturali
- MCU: STM32G474RET6, LQFP64, alimentazione I/O e digitale nominale 3.3 V.
- CODEC: TLV320AIC3204 RHB VQFN32, IOVDD 3.3 V; LDOIN 3.3 V; **AVDD e DVDD sono uscite di filtro dei regolatori interni**, NON collegare a 3.3 V.
- I2C codec: MCU PB6 (pin 59, SCL), PB7 (pin 60, SDA); pull-up candidati 4.7k, da verificare sulla capacità del bus.
- Interfaccia SAI full-duplex: MCU PB10 (pin 30, SCK_A) -> CODEC pin 2 BCLK; PB9 (pin 62, FS_A) -> pin 3 WCLK; PC1 (pin 9, SD_A TX) -> pin 4 DIN; CODEC pin 5 DOUT -> PB5 (pin 58, SD_B RX, sincronizzato con block A). Verificare impostazioni SAI e formato 24/32 bit effettivo in STM32CubeMX, poi su hardware.
- Master clock codec 12.288 MHz da oscillatore separato, ancora **NON progettato**: puo' evitare l'uso di PB8/BOOT0 come MCLK e permette di valutare in seguito la configurazione master/slave senza impegnare BOOT0. MCU SAI master per BCLK/WCLK proposto, PLL codec da riferimento 12.288 MHz: verificare sincronismo e registri.
- SPI1 PLL: PA5 pin 19 SCK; PA7 pin 21 MOSI; PA4 pin 18 chip-select GPIO; PB1 pin 25 CE; PB0 pin 24 MUXout (ingresso MCU). La SPI del PLL e' separata dal bus I2C audio.
- Reset codec: PC2 pin 10 -> codec pin 31, con pulldown 47k (R201); fino a firmware attivo codec resta in reset; validare livello e sequenza alimentazioni.
- Pin 12 SPI_SELECT CODEC -> GND per I2C. Pin 30 LDO_SELECT -> IOVDD per attivare LDO digitale integrato. AVDD e DVDD solo condensatori di filtro come da riferimento produttore.
- ADC di microfono: CODEC IN1_L pin 13 da preamplificatore da progettare; ingresso FM raw IN2_L pin 15, **a monte del de-enfasi/filtro audio**, per CTCSS/DCS (da tarare); uscite codec LOL/LOR pin 22/23 verso futuri stadi audio.
- 4 VDD, 4 VSS MCU: bypass 100nF per ogni VDD previsti. VDDA/VREF+ alimentazione filtrata ancora da definire; attenzione ai 3.3 V e alla sequenza.

## Importanti vincoli aperti
- Mancano regolatori di alimentazione MCU e CODEC a 3.3 V, ingresso MCLK, filtro front-end AF e stadio amplificazione PA.
- Manca una verifica delle funzioni alternate con STM32CubeMX e la corretta configurazione di SAI A/B in modalità sincrona. Manca l'ERC nativo KiCad e non esiste PCB.
- Mancano clock e jitter budget; prove EMI con il trasmettitore attivo; distanze RF/AF/digitale; test ADC reali e curva distorsione.
- TX solo sui canali permessi e CW da sottoporre a verifica normativa; CH9 e PA con priorita' sulle funzioni automatiche.

## Fonti consultate 2026-11-07
- ST DS12288 Rev.6, STM32G474xB/C/E, Figura 7 e Tabelle 12/13: https://www.st.com/resource/en/datasheet/stm32g474cb.pdf
- TI SLOS602E (Rev E), TLV320AIC3204, sezioni 6-7: https://www.ti.com/lit/ds/symlink/tlv320aic3204.pdf
- TI SLAA404C, guide LDO codec: https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/6/Design-and-Configuration-Guide-for-the-TLV320AIC3204-_2600_amp_3B00_-TLV320AIC3254-Audio-Codec.pdf
