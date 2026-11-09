# Rapporto tecnico — Superstar 3900 SMD Evolution V6.1

**Data:** 9 novembre 2026. **Fase:** progettazione incrementale COMPLETA della radio, controllata ad ogni revisione, con successiva revisione globale e simulazioni/validazioni finali.

## Sviluppo reale
Nuova specifica a componenti con **156 riferimenti elettronici**, **476 collegamenti pin-rete**, **143 reti** per la scheda STM32G474RET6 (LQFP64), due espansori MCP23017 SSOP28 e pannello vintage.

- **Pin STM32 tutti assegnati o espressamente riservati.** Allineati alla versione V2.1 dei moduli codec (PA9/43 = WCLK, NON PB9) e PLL. Le funzionalità in V6.0 (MUX, relè, FAULT) hanno pin di comando candidati; AMP_SD_REQUEST non pilota direttamente AMP_SD fisico, in attesa dell'interblocco della V6.2.
- **Pannello:** banda a sei posizioni one-hot, modo a cinque posizioni one-hot, ALFA fisico, encoder canale su PC10/PC11, CH9 su PC13, PTT su PA0, PA su PC0. Selettore PA con secondo contatto fisico verso futuro inibitore RF HW. 28 ingressi espansori + 4 indicatori. I due pin GPA7/GPB7 per ogni MCP23017 non vengono usati come ingressi, in accordo alla Rev D.
- **Software di base:** modello Python eseguibile con 40 canali + cinque ALFA in ciascuna delle sei bande, memorie per banda/ALFA, override CH9 27,065 MHz AM, priorità PA>CH9, invalidità one-hot => MUTE, TX sempre OFF. Integrato il router audio V6.0.
- **Bus I²C:** con codec sullo stesso bus PB6/PB7. Singola coppia pull-up 4,7 kΩ e Cbus ipotetica 150 pF => salita 0.597 µs, perciò 100 kHz Standard Mode candidato, NON 400 kHz. Il collegamento CODEC_READY sul precedente J604/14 rimane **etichetta logica da correggere**, non pin fisico certificato.

## Verifiche eseguite qui
- 55/55 test pannello e MCU + 5/5 di integrazione audio.
- 2.000 simulazioni digitali di rimbalzo interruttore (sintetiche): stabilizzazione fra 15 e 30 ms nel modello, TX OFF.
- Calcolo RC in dominio del tempo con SciPy ODE e sweep 10.000 combinazioni di tolleranza. Il livello LOW massimo nominale è <0.078 V ai limiti considerati; rilascio HIGH entro 1.998 ms nei modelli ideali.
- Regressioni storiche V4.0–V6.0: 2/21 riuscite, 19 non rieseguite nell'ultimo pacchetto per limiti di risorse. Dettagli in JSON.

## File significativi
- `01_Specifiche/V6.1/CIRCUITO_PIN_MCU_PANNELLO_V6.1.json` e `NETLIST_PIN_MCU_PANNELLO_V6.1.csv`
- `01_Specifiche/V6.1/PINMAP_MCU_LQFP64_V6.1.csv` (64 piedini)
- `01_Specifiche/V6.1/ESPANSORI_GPIO_V6.1.csv`
- `07_Componenti/BOM_MCU_PANNELLO_V6.1.csv` (candidata)
- `08_Firmware_Prototipi/V6.1/panel_controller_v61.py`
- `08_Firmware_Prototipi/V6.1/integration_audio_v61.py`
- `03_Verifiche/V6.1/STUDIO_ELETTRICO_RC_V6.1.json` e `TOLLERANZE_RC_ODE_V6.1.json`

## Restano aperti
1. Scelta meccanica/footprint reale, ESD, cablaggio, display, consumo e piani massa.
2. V6.2: inibizione TX fisica con secondo polo PA, supervisore PTT e gate reale AMP_SD; alimentazione regolata dei domini 3V3_UI/3V3_A.
3. Firmware STM32 concreto, DMA/SAI, implementazione delle funzioni accessorie e controlli di sincronizzazione fra moduli.
4. Fase finale: verifiche KiCad native, simulazione RF/EMC/termica con modelli adeguati e collaudo hardware.

**NO FAB / NO TX / 0 hardware verificato.** Le stime non sostituiscono le misure. Avanzamento storico circa 37%, da riconsiderare con la nuova architettura radio globale.

## Fonti ufficiali
- ST STM32G474RE Rev 6: https://www.st.com/resource/en/datasheet/stm32g474re.pdf
- Microchip MCP23017 Rev D: https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MCP23017-Data-Sheet-DS20001952.pdf
