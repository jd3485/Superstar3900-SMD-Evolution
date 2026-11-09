# V6.1 — MCU + pannello Superstar 3900 · schema a pin e componenti CANDIDATO

**Non è uno schematico KiCad collaudato né una scheda pronta per PCBWay.**
Il file JSON e la netlist rappresentano 156 riferimenti, 476 contatti numerati e 143 reti, basati sul datasheet ST LQFP64 e Microchip MCP23017 SSOP28. MPN dei controlli meccanici, cablaggi, impedenze fisiche e filtraggio alimentazioni devono ancora essere determinati.

## 1. U201 STM32G474RET6
Mappatura completa dei 64 pin (anche alimentazioni, SWD, bootstrap, riserve) in `PINMAP_MCU_LQFP64_V6.1.csv`. **Conservare il contratto V2.1 più recente**: PC1/9 SAI TX, PB10/30 BCLK, PA9/43 WCLK, PB5/58 SAI RX; PB6/59 e PB7/60 I2C, PA5/19 SPI1 SCK, PA7/21 SPI1 MOSI. PC2/10 codec reset, PA4/18 PLL CS, PB1/25 PLL CE, PB0/24 PLL MUXOUT. PA13/49 e PA14/50 solo SWD; PB8/61 strap boot, NON pannello.

**Controlli critici sulla MCU, non sugli espansori:** PTT_N PA0/12, PA_SENSE_N PC0/8, CH9_SENSE_N PC13/2; encoder incrementale direttamente su PC10/52 e PC11/53. Il secondo polo del selettore PA (S742) va alla logica di inibizione RF fisica **ancora da sviluppare in V6.2**. Nessuna connessione 13,8 V deve arrivare a una GPIO.

**U601 audio V6.0:** PC6/38 MUX_A0; PC7/39 MUX_A1; PC8/40 MUX_A2; PC9/41 MUX_EN_N (pull-up 47 kΩ su scheda audio); PA10/44 PA_RELAY_CMD; PA11/45 AMP_FAULT_N. PA8/42 è soltanto `AMP_SD_REQUEST` e deve attraversare un **gating hardware** (power-good, PA mute, relè, fault) prima del pin AMP_SD fisico. `J604/14 CODEC_READY` in V6.0 è una **etichetta logica**, non un pin READY hardware documentato sul codec: NON collegare arbitrariamente a una GPIO; confermare o eliminare in V6.2.

## 2. Espansori MCP23017 I2C
U701 a **0x20**, U702 a **0x21**, entrambi SSOP28 alimentati 3V3_UI. **GPA7 e GPB7 solo output** per il datasheet DS20001952D: usati per spie, mai ingressi. Gli altri 14 pin per chip accettano contatti 3,3 V verso DGND. Reset EXP_RESET_N via PC3/11; U701 INTA → PC4/22, U702 INTA → PC5/23; INTB lasciati scollegati. Inizializzare IOCON.MIRROR=1 (notifiche di entrambi i banchi verso INTA), ingressi, polarità e priorità prima della scansione. Se un expander smette di rispondere: **RX MUTE, RF TX OFF**; PA e CH9 restano direttamente leggibili da MCU e hanno precedenza (senza concedere TX).

U701: selettore banda sei posizioni one-hot, ALFA fisico, selettore modo cinque posizioni one-hot, tasti RIT +/-; due LED. U702: VOX, Dual Watch, Roger Beep, Echo, CTCSS/DCS, DSP, ATU, Scan, memoria, blocco, NB/ANL, strumento, guadagno MIC, assistenza; altri due LED. Funzioni avanzate **assegnate ai tasti, non ancora implementate**.

## 3. Elettrico d'ingresso e bus
Ogni contatto su espansore: pull-up esterna 10 kΩ a 3V3_UI + R serie 220 Ω verso il contatto a DGND + C 100 nF verso DGND. Pressione nominale: 0.071 V (VIL MCP <= 0.66 V); rilascio HIGH 0,8·VDD dopo 1.59 ms nel modello RC. Firmware richiede 20 ms validi (4 campioni a 5 ms); **non è una prova anti-EMI/ESD fisica**. PTT, CH9 e PA usano ingressi 3V3_D diretti con stessa rete; PC13 impiegato soltanto come input a basso carico. Encoder con pull-up 10 kΩ, 220 Ω, 10 nF e campionamento firmware 1 ms; 2 campioni identici per transizione, uno scatto ogni 4 transizioni Gray. Disturbi del commutatore e perdite di impulsi a velocità elevate restano da misurare.

**I2C1 unico:** R830/R831 = 4,7 kΩ (UNA SOLA COPPIA PER L'INTERO BUS) e modello conservativo Cbus=150 pF → salita 30–70% = 0.597 µs, compatibile con Fast-Mode? NO: maggiore di 300 ns. **Operare inizialmente a 100 kHz Standard-Mode** (limite di salita 1 µs); limite nominale capacitivo ~251110536 pF. Alimentazioni e masse del codec già presente devono essere 3,3 V con dominio coerente, e nessuna seconda coppia di resistori va montata in parallelo senza ricalcolo. Isolare I2C dei pannelli via cavi rumorosi e prevedere misure di capacità reale.

## 4. Memoria frequenze e priorità
Sorgente unica `02_Piano_Frequenze/Tabella_270_canali.csv`: 6 bande × (40 normali + 5 ALFA: 3A/7A/11A/15A/19A) = 270 combinazioni RX. La tabella storica riporta 40 righe D come `TX_preliminarmente_consentita=SI`, ma è **soltanto un marcatore storico di studio**: la logica V6.1 NON lo usa mai per abilitare la RF; TX resta OFF ovunque. Il commutatore ALFA è fisico; encoder permette di scorrere 1–40 oppure 5 canali ALFA per la banda. Gestione normal/ALFA indipendente per ciascuna banda. CH9 fisico prevale su selettori e impone **27,065 MHz AM**; al rilascio si torna allo stato selezionato prima dell'override. PA prevale su CH9, permette soltanto MIC verso altoparlante PA con PTT (a condizione che power/codec siano pronti): **mai TX RF**. Se i selettori sono invalidi (0 o 2 contatti), ricezione muta finché lo stato non è nuovamente stabile. L'encoder è ignorato quando CH9 o PA sono attivi.

## 5. Rischi aperti
- Hardware PTT/PA/CH9 e AMP_SD da chiudere in V6.2: il software disabilita TX, ma non basta per garantire l'interblocco fisico.
- Tensione VDDA/VREF+ e filtri analogici, tolleranze VDD, WCLK/SAI e SPI devono essere controllati nell'integrazione; I2C pullups in un solo punto fisico.
- MPN reali rotative, encoder, contatti, LED, display I2C e connettori non finali; nessun Gerber, ERC/DRC, simulazione SPICE o hardware.
- Segnalazioni LED non significano 'TX permessa'. All'accensione ogni GPIO non configurata e la logica di controllo restano fail-closed (TX fisico da implementare).

## Fonti
- ST DS12288 Rev6 LQFP64 (Fig.7): https://www.st.com/resource/en/datasheet/stm32g474re.pdf
- Microchip DS20001952D (MCP23017): https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MCP23017-Data-Sheet-DS20001952.pdf
