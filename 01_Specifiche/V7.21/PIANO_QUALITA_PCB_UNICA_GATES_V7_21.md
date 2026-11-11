# Superstar 3900 SMD Evolution — V7.21, disciplinare di progettazione PCB senza errori noti

**11 novembre 2026 · revisione di sicurezza e pre-layout. NO FAB / NO GERBER / NO PCBWAY / NO TX.**

## Decisione progettuale

Obiettivo: **una sola PCB funzionale, elettricamente verificata, con ERC/DRC nativi senza errori o waiver ingiustificati**, footprint MPN-pin-pad verificati dal datasheet, netlist/PCB confrontate, corrente/termica/EMC validate, test su prototipo reale prima di autorizzare produzione. Non è corretto promettere difetti fisici assolutamente impossibili: si devono invece chiudere e documentare tutti i rischi identificati.

**Non generare una falsa PCB completa** finché manca la netlist integrata, lo chassis/meccanica e la qualifica dei pad. Una `.kicad_pcb` con componenti scollegati e DRC verde non è un layout di radio.

## Fatti riproducibili dal vero KiCad a 7 fogli

La CI `.github/workflows/v721_full_board_foundations.yml` esporta la vera netlist dalla schematica V7.19, conta componenti, footprint e reti senza leggere solo commenti del README.

| Misura | Stato |
|---|---:|
| Componenti nella schematica 7 fogli | **132** |
| Assegnazioni footprint presenti | **84** |
| Footprint ancora vuoti | **48** |
| Di cui nel blocco MCU/CODEC/AFE | **46** |
| Di cui connettori AUX J100/J101 | **2** |
| Footprint già assegnati ma con nome esplicito «non validato» | **2** (F200, Y1) |
| Root ERC | **36 errori / 340 warning** |
| Interfacce fisiche fra moduli | **15 OPEN/HOLD** |
| PCB unica della radio | **inesistente** |

**Le 84 assegnazioni NON equivalgono a 84 qualifiche vendor.** F200 (fusibile candidato) contiene `FOOTPRINT_NON_VALIDATO`; Y1 (TCXO TXC 7N) contiene `UNVALIDATED`. Tutte le altre assegnazioni richiedono comunque verifica della corrispondenza MPN/pad/3D/protezione ESD.

## Primo pacchetto di IC MCU/CODEC: sei candidati di package, non ancora assegnati

Verifica degli effettivi numeri dei pad disponibili nella libreria standard **KiCad9 installata dalla CI**, incrociando dimensioni di package dal vendor:

| IC | Package candidato da confronto | Verifica ancora necessaria |
|---|---|---|
| U6201 STM32G474RET6 | **ST LQFP64 10×10 mm, passo 0,5 mm**; footprint KiCad `Package_QFP:LQFP-64_10x10mm_P0.5mm` | 64 pin di simbolo DRAFT ↔ pad/pinout ST, land pattern IPC, 3D e orientamento |
| U6202 TLV320AIC3204 | **TI RHB VQFN32 5×5 mm passo 0,5 mm**, EP nominale 3,45 mm; candidato `Package_DFN_QFN:VQFN-32-1EP_5x5mm_P0.5mm_EP3.5x3.5mm` | **33° pad termico centrale** da ricondurre correttamente allo schema e a un piano elettrico approvato; land pattern/paste mask e via termiche vendor |
| U6203..U6206 TPS7A2033PDBVR | **TI DBV SOT-23-5**, footprint `Package_TO_SOT_SMD:SOT-23-5` | 5 pad ↔ pin fisici (IN/GND/EN/NC/OUT), corrente/termica, decoupling e posizione rame |

Il pad centrale dell'RHB è fisico: la documentazione TI indica esplicitamente che **deve essere saldato al PCB**. Un simbolo che gestisse solo i 32 pin perimetrali senza rappresentare/attribuire la piazzola 33 richiederebbe una ECO specifica; NON inventare il potenziale da assegnare senza controllo applicativo.

Documenti: [ST STM32G474 datasheet DS12288, LQFP64](https://www.st.com/resource/en/datasheet/stm32g474vb.pdf); [TI TLV320AIC3204 datasheet SLOS602E](https://www.ti.com/lit/ds/symlink/tlv320aic3204.pdf); [TI TPS7A20 datasheet SBVS338H](https://www.ti.com/lit/ds/symlink/tps7a20.pdf).

I **restanti 42 footprint vuoti** (passivi, oscillatore X6201, ferrite FB6201, connettori AUX) **rimangono HOLD** finché MPN, valore, tensione e modello d'ingombro non sono scelti. Nessuna libreria candidata viene automaticamente trascritta negli schemi.

## Bilancio delle alimentazioni: verifiche obbligatorie, non carichi inventati

La schematica contiene:
- **U200 TPS26600PWPT**: [TI TPS2660](https://www.ti.com/product/TPS2660) eFuse 4,2–60 V, limite di corrente regolabile fino a ~2,23 A, con terminale `EFUSE_RTN` distinto per la protezione inversa. **F200** è un fusibile 1,5 A *candidato*, non un prodotto verificato in footprint e derating.
- **U100 TPS54202DDCR**: [TI TPS54202](https://www.ti.com/product/TPS54202) buck 4,5–28 V, **2 A max continuativi**, switching 500 kHz nominale. Non confrontare 2 A *uscita a 5 V* con 1,5 A *fusibile lato 13,8 V* senza passare da potenza, efficienza, temperatura, inrush e transitori.
- **Sei LDO TI TPS7A2033PDBVR 3,3 V** con `Iout(max)=300mA` ciascuno: U2/U3 su AUX 5V e U6203..U6206 sulla **distinta** linea MCU `5V_DIGITAL_FILTERED`. I sei massimi di targa sommati (1,8 A) non sono *il carico effettivo*, né dimostrano che 5V MCU sia già alimentato dallo stesso buck: **le due reti sono ancora isolate e le loro interfacce HOLD**.

### Schermo termico conservativo TI TPS7A20 DBV

Secondo la [tabella termica TPS7A20 SBVS338H, DBV 5 pin](https://www.ti.com/lit/ds/symlink/tps7a20.pdf), la resistenza **RθJA JEDEC =187,1 °C/W** dipende fortemente dal layout PCB. Assumendo **5,0 V IN, 3,3 V OUT e 300 mA continui**, il singolo LDO dissiperebbe **0,51 W** e lo schermo JEDEC restituisce un innalzamento di giunzione di **~95,4 °C**. Con ambiente a 40°C si avrebbe **~135,4 °C**, superiore a 125°C della fascia di temperatura operativa, **nel solo modello JEDEC**.

**Risultato progettuale:** una progettazione che richieda 300mA continui a 40°C per ciascun DBV non può essere considerata automaticamente sicura. Servono corrente di carico reale, TJ consentita, geometria/piani del PCB, modello termico di scheda, prove ambientali e derating. È possibile che i carichi effettivi siano molto inferiori; non è stato misurato nessun assorbimento.

### Tolleranza del buck TPS54202

Dal circuito KiCad U100: **R101=100k 1%**, **R102=13k3 1%**. [TI TPS54202 SLVSD26C](https://www.ti.com/product/TPS54202), VREF tipico 0,596V (0,581–0,611V in specifica). Il solo calcolo statico `VOUT=VREF×(1+Rtop/Rbottom)` restituisce **5,077 V nominali** e uno scenario limite **~4,863–5,298 V** combinando limiti del riferimento e tolleranza resistori. Questo NON è un range complessivo garantito di sistema (ripple, bias feedback, transitori, capacità, caduta conduttori, layout non inclusi); l'architettura deve essere dimensionata su peggiore caso.

## Ordine decisionale verso la prima PCB unica

1. **Gate G1 — circuito elettrico integrato:** 15 interfacce ricondotte a segnale fisico con tensioni/direzioni/risoluzione transitori; progettare stadio RX→IF, definire supervisor interlock NO TX. Chiudere root ERC (36 errori) e diagnosticare 340 warning senza waiver silenziosi.
2. **Gate G2 — componenti e footprint:** MPN esatti; tutti i 132 componenti idonei per PCB hanno footprint; numero dei pin e dei pad, EP/pasta/courtyard, thermal, vendored CAD, BOM/MFG. F200/Y1 e SMA TE a 180° certificati; nessun `DRAFT` o `UNVALIDATED` rilasciato.
3. **Gate G3 — power/analog RF:** 13,8V eFuse/RTN, buck 5V e sei LDO 3V3 dimensionati su correnti/efficienze/termiche/power-up reali; PLLatinum Sim, margine fase, spurie, RF line impedance e misure; rispetto EMC/ESD e prevenzione emissioni.
4. **Gate G4 — definizione meccanica:** quote reali chassis Superstar 3900, fissaggi, pannelli, altezza componenti, posizioni ingressi/RF/antenna e raffreddamento. **Nessuna quota viene inventata** per far apparire un PCB completo.
5. **Gate G5 — layout fisico:** 4 layer come *ipotesi di lavoro, non stackup approvato*, valutando top signal/RF, riferimento di massa continuo dove richiesto, piani di alimentazione e bottom signal. La separazione dei domini GND_MAIN/GND_RF/MCU deve essere scelta con analisi di ritorno di corrente, non cortocircuitata per nome. Buck e suo SW-loop vicini, lontani da LNA e OSC; C3 VTUNE vicino LMX2572; MCU/codec lontani da RF sensibile; ritorni e bypass studiati fisicamente.
6. **Gate G6 — DRC, ispezione, prototipo:** DRC nativo zero problemi *effettivi*, 0 connessioni non sbrogliate, confronto netlist ↔ PCB, regole per distanze, impedanze/spessore/thermal/EMC, revisione manuale indipendente e collaudi su prototipo. **NO FAB / NO TX** fino a rilascio esplicito documentato.

**Stima PCB globale ~10% invariata**: questa revisione rafforza la qualità prima del layout, non aggiunge routing. Nessun layout meccanicamente completo può oggi essere garantito senza i dati sopra.
