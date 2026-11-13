# V7.44 — Load anchors vendor per sei TPS7A20 3.3V: LMX2572, STM32G474, codec

**Data:** 13 novembre 2026. **Baseline:** V7.43 [PR #46](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/46) integrata su main, con 36 test nativi/sorgente PASS. V7.44 **non modifica alcun sorgente KiCad, netlist, footprints o schemi**: aggiunge una matrice per poter distinguere **correnti condizionali di singoli IC** dai **massimi di rail non ancora qualificati**. La matrice precedente è `03_Verifiche/V7.43/MATRICE_CARICHI_TERMICA_5V_V743.json`; questa estensione è `03_Verifiche/V7.44/MATRICE_CONSUMI_VENDOR_CONDIZIONALI_V744.json`.

## 1. Dati reali del produttore, condizioni precise

| Dispositivo | Rete del LDO nel progetto | Punti del datasheet e condizioni | Valore, non trasferibile automaticamente al rail |
|---|---|---|---:|
| TI **LMX2572** U1 | AUX_PLL U2, `3V3_PLL_INPUT_FROM_LDO` | SNAS740B §6.5 p6, VCC3.3V a 25°C, VCO direct, fPD20MHz/ICP1.25mA | **75mA typ** |
| TI LMX2572 U1 | stesso | direct, fPD100MHz/ICP2.5mA | **79mA typ** |
| TI LMX2572 U1 | stesso | RFout diviso, fPD20MHz/ICP1.25mA | **82mA typ** |
| TI LMX2572 U1 | stesso | RFout diviso, fPD100MHz/ICP2.5mA | **86mA typ** |
| TI LMX2572 U1 | stesso | chip power down, testo §6.5 | **2.5mA typ** |
| ST **STM32G474RET6** U6201 | MCU U6204, `3V3_MCU` | DS12288 Rev6 tab21 p89, 170MHz Range1 Boost, Flash single bank, ART ON, cache ON, prefetch OFF, **tutte periferiche disabilitate**, 25°C | **29.5mA typ /31mA max** |
| ST STM32G474RET6 U6201 | stesso | stessa modalità CPU, 85°C | **31mA typ /42mA max** |
| TI **TLV320AIC3204** U6202 | MCU U6205 `3V3_CODEC_IO`, U6206 `3V3_CODEC_LDOIN` | SLOS602E §11 p44, PowerTune e blocchi interni | **150mA capacità della sorgente suggerita per analogici abilitati**, NON consumo e NON per forza sola LDOIN; **~20mA picco sulla DVDD interna** in modalità PRB, NON corrente ingresso 3.3V. |

Fonti **originali lette e screenshot pagina effettuati**:
- https://www.ti.com/lit/ds/symlink/lmx2572.pdf — p6 SNAS740B, tab6.5, i campi MIN/MAX per corrente tipica sono vuoti per queste modalità. In assenza di max **NON inventare** un massimo garantito di 86mA. La temperatura delle osservazioni tipiche è 25°C, non 85°C.
- https://www.st.com/resource/en/datasheet/stm32g474rb.pdf — p89 DS12288 Rev6 tab21 (valori garantiti **solo** per le condizioni descritte della tabella).
- https://www.ti.com/lit/ds/symlink/tlv320aic3204.pdf — p44 SLOS602E, §11; IOVDD dipende anche da frequenza di commutazione e carico delle uscite, e LDOIN AVDD/DVDD dipendono dai blocchi interni abilitati e sequenza dei registri.

**Distinzioni essenziali:** non sommare direttamente `150mA` e `20mA` al 3.3V perché il primo è suggerimento sulla **capacità di alimentazione** e il secondo riguarda la DVDD interna alimentata da DLDO o altra sorgente, non l'ingresso 3.3V. Non dichiarare 42mA come corrente massima radio dell'MCU: la tab21 esclude periferiche e GPIO. Il clock U6203 e il reference U3 restano senza stime qualificate.

## 2. Stress termico numerico *condizionale*, non signoff

Usando solo per comparazione `VIN=5.0V`, `VOUT=3.3V`, `RθJA=187.1°C/W` *su PCB reference TI*, `T_A=85°C`, `I_GND=0` (non fisicamente garantito), `P≈1.7×I`, `T_J≈T_A+RθJA×P`:

| Dispositivo al punto datasheet | I condizionale | P minima nel modello | T_J illustrativo a 85°C | Margine geometrico a 125°C |
|---|---:|---:|---:|---:|
| LMX2572 RF diviso fPD100MHz (**typ a 25°C**, non a 85°C) | 86mA | 146.2mW | **112.35°C** | circa **12.65°C**, prima di altre utenze/IGND |
| STM32G474 170MHz no peripherals (**max 85°C**) | 42mA | 71.4mW | **98.36°C** | circa 26.64°C, prima di altre utenze/IGND |

**Non applicare la riga LMX2572 per sostenere una temperatura massima reale a 85°C**: i dati ICC 86mA sono tipici a 25°C. Il modello termico usa un θJA sul board JEDEC non la futura PCB Superstar e ignora consumi indiretti; nessuno dei due numeri approva il margine termico realizzato. Per il PLL, questa analisi rende **sensibile** il consumo del carico RF ad altre utenze, ma NON dimostra surriscaldamento. A 85°C ambiente l'envelope teorico ideale per TJ125, I_GND0 è `(125−85)/(187.1×1.7)≈125.8mA` per singolo LDO; a 86mA rimarrebbero **circa 39.8mA solo nel modello**, non un budget garantito da allocare.

## 3. Associazioni schematiche preservate

V7.43 ha già dimostrato in **KiCad9 nativo** la correttezza delle sei reti LDO; in particolare U2.1 IN del PLL **è già collegato correttamente** anche senza un'etichetta immediata sul pin. Non ricreare una falsa ECO. Nella matrice V7.44 i test confrontano sempre le effettive associazioni `ref→output_net` rispetto a V7.43: `U2→3V3_PLL_INPUT_FROM_LDO` per LMX2572; `U6204→3V3_MCU` per STM32; `U6205→3V3_CODEC_IO`, `U6206→3V3_CODEC_LDOIN` per codec. **Nessuna modifica dell'associazione, nessun nuovo ponte AUX/MCU e nessun carico supposto**.

## 4. Prove e prossimi gate decisionali

`03_Verifiche/V7.44/test_vendor_conditional_5v_loads_v744.py` verifica **25 condizioni**: citazioni vendor con condizioni di applicazione, coerenza fra matrici V7.43→V7.44, valori tipici vs max, termica illustrativa e **fail closed** in caso di dati mancanti. Workflow minimale `.github/workflows/v744_vendor_5v_load_anchors.yml` (Python standard library, path PR mirato, nessun apt/pip, no KiCad9 ripetuto perché i file CAD sono identici). **Non dichiarare test superati prima del run reale**.

Il passo successivo più sostanziale non è scegliere resistori o convertitori a tentativi: serve attribuire profili **RX_ACTIVE / RX_SCAN / STANDBY** e profili hard startup/shutdown a configurazione precisa di clock MCU, GPIO carichi, PLL fPD/ICP/uscite, codec PowerTune/ALDO, RC clock, TCXO, amplificatori accessori. Conoscendo `Iout` massimo, `Iground` massimo, `T_A,max` deciso, `RθJA PCB` e margine thermal, si potrà confrontare regolatori attuali contro alternative a rumore basso e buona PSRR senza compromettere PLL/audio. Il 5V del buck TPS54202 rimane un **2A condiviso** e le quattro correnti dietro FB6201 devono stare nel rating termico/DC della ferrite; entrambe le correnti sono ancora UNKNOWN. Non convertire i punti tipici in un totale 5V fittizio.

**Rimane HOLD:** sei load maxima (incl. transienti), TCXO/Y1 pin10, SG48, 15 interfacce crossmodule e massa `GND_MAIN` vs `GND`, reverse TPS7A20/brownout, power stages, thermal layout, EMC, DRC e prototipo. **NO FAB / NO GERBER / NO PCBWAY / NO TX**. Baseline CAD V7.41 **134 componenti, 101 reti, 32 footprint mancanti, ERC 36/221**, PCB unica non completata, stima storica ~10%, non aumentata da nuova analisi.
