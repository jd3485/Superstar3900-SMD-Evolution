# V7.34 — Audit tecnico dei 30 condensatori MCU/CODEC (HOLD, non autorizzato per fabbricazione)

Data: 12 novembre 2026. Baseline: V7.33 integrata su `main`, 132 componenti, 100 reti, ERC 36 errori / 218 warning, 33 footprint non assegnati. Questa è una fase di *qualifica preliminare*, **non** una ECO CAD completata.

## Inventario estratto dal file KiCad V7.33

Sorgente: `04_KiCad/Modulo_MCU_CODEC_V7.33_YAGEO_8R_0402_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch`. I 30 simboli da C6201 a C6230 hanno tutti la proprietà Footprint vuota.

| Valore nello schema | Quantità | Riferimenti |
| --- | ---: | --- |
| 100nF | 12 | C6201, C6203, C6205, C6207, C6209, C6210, C6211, C6212, C6214, C6217, C6220, C6227 |
| 10uF | 5 | C6202, C6204, C6206, C6208, C6219 |
| 1uF | 11 | C6213, C6215, C6216, C6218, C6221, C6222, C6223, C6224, C6225, C6226, C6229 |
| 4.7nF | 1 | C6228 |
| 10nF | 1 | C6230 |
| **Totale** | **30** | |

## Evidenze vendor (candidati, NON design-in approvato)

- Murata GRM155R71C104KA88D: 100nF, X7R, 16 V, ±10%, package 0402 (1005 metrico). Fonte distributore: https://www.mouser.it/it/ProductDetail/Murata-Electronics/GRM155R71C104KA88D ; famiglia Murata 100nF 0402: https://pim.murata.com/asset/pim4/ceramicCapacitorSMD/GRM155R71C104JA88-01A-EN_PDF_CERAMICCAPACITORSMD?lastModifiedDatetime=20250813144737 . Il PDF della variante **JA88** non è prova delle caratteristiche esatte **KA88D** oltre ai campi effettivamente coincidenti.
- Murata GRM21BR71A106KE51: 10uF, X7R, 10 V, ±10%, package 0805 (2012 metrico), *candidato per analisi* e non assegnato. Elenco ufficiale Murata: https://www.murata.com/-/media/webrenewal/tool/library/common-pdf/dynamic-model/component-list-d-mlcc-2504.ashx?cvid=20250523010405000000&la=en .
- Nessun MPN approvato per gli undici 1uF, il 4.7nF e il 10nF; nessuna decisione sul package per nessuno dei 30.

## Blocchi tecnici che impediscono l'assegnazione dei footprint

1. Non sono ancora documentate pin-per-pin le rail effettive, compresi i nodi di alimentazione/uscita analogica per ogni C62xx; il valore nello schema non prova la tensione applicata.
2. Per i MLCC classe II la capacità **effettiva** varia con DC bias, temperatura, invecchiamento e tolleranza. Per i 10uF serve curva specifica per MPN e tensione, non basta '10uF/10V'.
3. Verificare prescrizioni di bypass, ESR/ESL, impedenza e ordine di grandezza del ripple per i datasheet di MCU, codec e alimentazioni. Reti analogiche o di filtro richiedono valutazione del dielettrico e della precisione prima di usare X7R.
4. Verificare geometria di land *del produttore per MPN esatto*, pad 1/2, clearance, saldatura e stencil; non riciclare il footprint delle resistenze 0402.
5. Prima di cambiare il CAD: prova KiCad9 netlist/ERC prima-dopo, 132 componenti, 100 reti identiche, zero pin-net delta; verificare che ogni footprint sia associato esclusivamente a un condensatore approvato.
6. Attendere vera qualifica elettrica e meccanica, non ridurre artificialmente gli errori/ERC o il numero di footprint HOLD.

## Stato e ripartenza

La V7.34 è **audit in corso**, non integrata né CAD-validata; nessuna modifica alla V7.33 da questo documento. Target successivo: mappa C62xx→nodi elettrici→tensione in tutti gli stati (nominale, start-up, fault) e verifica delle curve DC-bias di vendor; soltanto allora ECO KiCad con test nativi e PR idonea. I 33 footprint mancanti, 36 errori ERC e 218 warning restano invariati. HOLD: 15 interfacce cross-domain, SG48, Y1 pin10 AFC/GND, thermal/power/PLL. **NO FAB / NO GERBER / NO PCBWAY / NO TX.**

## V7.34 — Mappatura diretta delle etichette sui pin, dal sorgente nativo (12 novembre 2026)

Il simbolo `S3900E:C_DRAFT` ha pin 1 a coordinate relative (0,+5.08) KiCad e pin 2 (0,-5.08); nelle coordinate disegno i rispettivi contatti corrispondono a `y-5.08` e `y+5.08`. Tutte le 30 istanze sono orientate a zero gradi. Il seguente inventario è determinato dalle **etichette di rete posizionate esattamente sui terminali**, non da ipotesi di vicinanza ai nomi dei componenti. Non prova da solo continuità globale, tensioni o corretta connessione elettrica, per cui la netlist KiCad resta il riferimento di qualifica finale.

| C | Pin 1: etichetta di rete | Pin 2: etichetta di rete |
| --- | --- | --- |
| C6201 | `3V3_CODEC_IO` | `GND` |
| C6202 | `CODEC_REF` | `GND` |
| C6203 | `CODEC_AVDD_LDO_OUT` | `GND` |
| C6204 | `CODEC_AVDD_LDO_OUT` | `GND` |
| C6205 | `CODEC_DVDD_LDO_OUT` | `GND` |
| C6206 | `CODEC_DVDD_LDO_OUT` | `GND` |
| C6207 | `3V3_CODEC_LDOIN` | `GND` |
| C6208 | `3V3_CODEC_LDOIN` | `GND` |
| C6209 | `3V3_MCU` | `GND` |
| C6210 | `3V3_MCU` | `GND` |
| C6211 | `3V3_MCU` | `GND` |
| C6212 | `3V3_MCU` | `GND` |
| C6213 | `3V3_MCU` | `GND` |
| C6214 | `3V3_ANA_MCU` | `GND` |
| C6215 | `5V_DIGITAL_FILTERED` | `GND` |
| C6216 | `3V3_AUDIO_CLK` | `GND` |
| C6217 | `3V3_AUDIO_CLK` | `GND` |
| C6218 | `3V3_AUDIO_CLK` | `GND` |
| C6219 | `5V_DIGITAL_FILTERED` | `GND` |
| C6220 | `5V_DIGITAL_FILTERED` | `GND` |
| C6221 | `5V_DIGITAL_FILTERED` | `GND` |
| C6222 | `3V3_MCU` | `GND` |
| C6223 | `5V_DIGITAL_FILTERED` | `GND` |
| C6224 | `3V3_CODEC_IO` | `GND` |
| C6225 | `5V_DIGITAL_FILTERED` | `GND` |
| C6226 | `3V3_CODEC_LDOIN` | `GND` |
| C6227 | `MIC_PREAMP_OUT` | `MIC_AC_COUPLED` |
| C6228 | `MIC_CODEC_IN` | `GND` |
| C6229 | `FM_DISCRIM_RAW` | `FM_AC_COUPLED` |
| C6230 | `FM_CODEC_IN` | `GND` |

**Risultati tecnici rilevanti:** `C6227` e `C6229` sono condensatori *in serie* ai segnali MIC e FM; non vanno qualificati come semplici MLCC di alimentazione. `C6228` e `C6230` sono tra ingressi del codec e GND, probabili elementi di rete analogica, ma funzione e frequenza di taglio richiedono l'analisi del circuito completo. `C6202` 10uF è su `CODEC_REF`, non su un rail nominale 3.3 V; `C6204` e `C6206` 10uF sono sulle uscite LDO interne `CODEC_AVDD_LDO_OUT` e `CODEC_DVDD_LDO_OUT`: prima di approvare MPN, verificare specifiche TI su stabilità, capacità effettiva, ESR e startup. Le etichette `5V_DIGITAL_FILTERED` / `3V3_*` non certificano da sole livelli effettivi, sovratensioni transitorie o tensione massima.

### Gate immediato

Il nuovo `test_capacitor_inventory_v734.py` vincola l'inventario e i 60 accoppiamenti pin/etichette estratti dal sorgente KiCad. Qualunque cambiamento inatteso va bloccato e riesaminato. **Non modifica lo schema, non esegue netlist/ERC nativi, non è signoff fabbricativo.** Il prossimo passaggio elettrico è confrontare questi 60 nodi con netlist esportata in KiCad9 e le specifiche dei regolatori codec, poi scegliere MPN esatti con curve DC-bias e land del produttore.


## Verifica vendor TI TLV320AIC3204: REF, LDO e ingresso audio (12 novembre 2026)

**Fonte primaria:** Texas Instruments *TLV320AIC3204 Ultra Low Power Stereo Audio Codec*, SLOS602E (rev. settembre 2019), https://www.ti.com/lit/ds/symlink/tlv320aic3204.pdf , pagine stampate 15, 16, 41 e 45 (PDF 0-index: 14, 15, 40, 44). Controllate anche le figure/tabelle originali, non solo estratti di terzi.

| Elementi V7.33 | Rete su pin 1 | Valore schema | Indicazione TI | Giudizio conservativo |
| --- | --- | --- | --- | --- |
| C6202 | CODEC_REF | 10uF | REF verso ground 10uF per alto SNR (sez. 10.2.1.1, p41); tabella 7.10 min 1uF, tipico 10uF | **Valore nominale coerente**, MPN, capacità effettiva, ground AVSS e layout ancora HOLD |
| C6203/C6204 | CODEC_AVDD_LDO_OUT | 100nF + 10uF | LDO AVDD: decoupling 1uF nella tabella 7.9 p15 | **Non prova di errore**: 10uF nomin. più 100nF, ma stabilità e start-up dei LDO vanno qualificati, non sostituire con 1uF senza analisi |
| C6205/C6206 | CODEC_DVDD_LDO_OUT | 100nF + 10uF | LDO DVDD: decoupling 1uF tabella 7.9 p15 | Stesso HOLD: capacitance derating, carico, avvio, ESR |
| C6227/C6229 | MIC_PREAMP_OUT / FM_DISCRIM_RAW | **100nF (C6227) / 1uF (C6229)** in serie | Sez. 10.2.2.1 p41: ingressi analogici AC-coupled, valore C in funzione dell'impedenza di ingresso programmata | **Topologia di principio coerente**, impedenza, f_c, livello e bias non dimostrati |
| C6228/C6230 | MIC_CODEC_IN / FM_CODEC_IN | 4.7nF/10nF verso GND | Sez. 12.2 p45 mostra un condensatore *opzionale* vicino al pin per ridurre RF, esempio 33pF | **Non considerare 4.7nF /10nF equivalenti a 33pF**: occorrono circuito R/C, ampiezza, banda passante e verifica attesa del filtro |

Per il filtro passa-alto del condensatore serie, solo nel caso di una resistenza equivalente conosciuta, `f_c = 1/(2*pi*R_eq*C_eff)`. Il datasheet TI indica inoltre che `R_eq` dipende dalle impostazioni del PGA; senza firmware/configurazione e impedenza non dare valori numerici di taglio. L'esempio TI da **33pF** è un suggerimento di layout per mitigazione RF e non giustifica i valori in nF esistenti. Il disegno TI chiede i decoupling vicino ai pin e riferimento analogico AVSS: l'etichetta generica `GND` nello schema non certifica la strategia di ritorno fisica.

**Alimentazione del codec:** il documento TI *Design and Configuration Guide* SLAA404C (p9–10) distingue l'uso degli LDO interni da AVDD/DVDD esterni; il comportamento di `LDO_SELECT` e la sequenza IOVDD/LDOIN/RESET vanno confermati su schema, firmware e transitori prima di concludere sulla stabilità. Fonte: https://www.ti.com/lit/an/slaa404/slaa404.pdf .

### Riesame scelta MLCC 10uF e ciclo di vita commerciale

La precedente citazione del candidato `GRM21BR71A106KE51` (Murata 10uF/10V X7R 0805) **non autorizza design-in**: nel catalogo Murata SimSurfing consultato risulta *To be discontinued*. Evitare una nuova scelta di approvvigionamento senza conferma di lifecycle/stock. Murata elenca `GCM21BR71A106KE22` 10uF/10V X7R 0805 come *In Production*, ma **non è approvato**: servono curve Ceff(Vdc,T,aging), ESR/ESL e land del codice esatto, oltre al suo utilizzo su rail/REF specifico. Catalogo ufficiale: https://ds.murata.com/simsurfing/mlcc.html?oripartnumbers=%5B%22GRM21BR71A106KE51K%22%5D&partnumbers=%5B%22GRM21BR71A106KE51%22%5D&rgear=suaykx&rgearinfo=com&videoId=5970369965001 .

**Esito:** i valori esistenti di C6202, C6204, C6206 sono **candidati nominalmente plausibili**, non una qualifica completa né approvazione di footprint. Nessun corto o modifica alla topologia è giustificato dalle informazioni disponibili. Restano esattamente 33 footprint non attribuiti nella baseline. Nessuna CI/DRC/ERC nuova dichiarata.

**Correzione di audit (12 novembre 2026):** il valore vero di C6227 nel file KiCad è **100nF**, NON 1uF; C6229 è **1uF**. La precedente etichetta di gruppo era errata, non lo schema. Capacità diverse implicano tagli passa-alto diversi a parità di impedenza: nessun confronto quantitativo è valido prima di verificare configurazione PGA e resistenza equivalente.

## Analisi quantitativa MIC/FM da sorgente KiCad V7.33 (12 novembre 2026)

Nuova ricostruzione verificata per **tutti e sei** i componenti, ciascuno con valore, pin1, pin2 e label reali (non solo posizione grafica):

| Percorso | Componente | Valore | Pin1 → Pin2 |
|---|---|---|---|
| MIC | C6227 | 100nF | MIC_PREAMP_OUT → MIC_AC_COUPLED |
| MIC | R6207 | 1kΩ | MIC_AC_COUPLED → MIC_CODEC_IN |
| MIC | C6228 | 4.7nF | MIC_CODEC_IN → GND |
| FM | C6229 | 1uF | FM_DISCRIM_RAW → FM_AC_COUPLED |
| FM | R6208 | 1kΩ | FM_AC_COUPLED → FM_CODEC_IN |
| FM | C6230 | 10nF | FM_CODEC_IN → GND |

### Topologia e numeri verificabili

Entrambi i percorsi hanno sequenza **condensatore serie Cc → resistenza serie Rs → ingresso codec**, con condensatore Cf fra ingresso e GND. Nel modello *isolato* con sorgente ideale, ingresso ad impedenza infinita e accoppiamento non limitante, il polo Rs/Cf è `1/(2πRsCf)`: **MIC ~33.86 kHz, FM ~15.92 kHz**. Questi valori **NON sono la frequenza di taglio effettiva della catena completa**; non chiamarli limiti di banda certificati.

Per uno screening più realistico, `03_Verifiche/V7.34/test_mic_fm_passive_v734.py` contiene il modello lineare `H(jω) = Zload/(Rsource + 1/(jωCc) + Rs + Zload)`, con `Zload = (1/Req + jωCf)^(-1)`. **Req e Rsource sono parametri**, non valori misurati o firmware verificato. Verifica topologia contro le sei coppie pin-label originarie e include controlli numerici di passività. A titolo *meramente illustrativo*, con `Req=10 kΩ` e `Rsource=0`:
- **MIC**: risposta `|H|` a 100 Hz ~−5.84 dB, 1 kHz ~−1.25 dB, 3 kHz ~−1.20 dB, 10 kHz ~−1.44 dB.
- **FM**: a 100 Hz ~−0.99 dB, 1 kHz ~−0.91 dB, 3 kHz ~−1.02 dB, 10 kHz ~−2.11 dB.

I due filtri possono risultare intenzionalmente diversi; **non modificare C6227/C6229 a valori uguali** e **non equiparare C6228/C6230 a un piccolo condensatore antirumore RF** senza misure.

### Datasheet e blocchi

TI TLV320AIC3204, SLOS602E Rev.E, sez. 10.2.2.1 p41: `Fc=1/(2πReqCc)`, con `Req` dipendente da PGA, registro dB e resistenze interne selezionate su P1_R52–R57 e P1_R59–R60. Ingresso analogico ammesso fino a **0.5 Vrms**: verificare ampiezza massima, fault e distorsione dei segnali MIC_PREAMP_OUT e FM_DISCRIM_RAW; se supera la capacità del codec occorre attenuazione qualificata. Fonte primaria: https://www.ti.com/lit/ds/symlink/tlv320aic3204.pdf . Il layout d'esempio TI p45 raccomanda separazione dai clock, ritorno su massa appropriata e menziona 33pF *opzionale* per RF, non i nostri valori nF.

**Qualifica mancante:** codice/registri della configurazione PGA e routing audio, impedenze d'uscita dei circuiti precedenti, banda target audio modulazione (MIC e FM), livelli di ingresso e armoniche/EMI, impedenza e leakage dei MLCC effettivi e prove SPICE più hardware. Non è ragionevole proporre una ECO di valori CAD senza questi dati. Non eseguita CI nativa KiCad9 né full SPICE in questa revisione; screening con formula lineare e controllo sorgente. Resta tutto **REVIEW/HOLD — NO FAB / NO TX**.

## V7.34 — Sweep parametrici ingresso MIC/FM, 12 novembre 2026

Modello piccolo segnale esistente `H=Zload/(Rsource+Zcoupling+Rseries+Zload)`, `Zload=(1/Req+jωCf)^−1`; ipotesi a **Rsource=0 Ω**, valori C/R nominali, nessuna parassita, nessun bias e nessuna non-linearità. Le colonne 10k/20k/40k sono **Req effettiva ipotizzata**, non valori di configurazione firmware verificati né identici automaticamente a Rin. Fonte: Texas Instruments TLV320AIC3204 SLOS602E, sezione analog input e app note SLAA557, che distinguono input resistance selezionata (Rin) dalla resistenza equivalente Req, dipendente dal guadagno PGA. Datasheet https://www.ti.com/lit/ds/symlink/tlv320aic3204.pdf ; guida https://www.ti.com/lit/ml/slaa557/slaa557.pdf .

| Via | Frequenza | Req=10 kΩ | Req=20 kΩ | Req=40 kΩ |
| --- | ---: | ---: | ---: | ---: |
| MIC | 100 Hz | −5.84 dB | −2.63 dB | −1.16 dB |
| MIC | 1 kHz | −1.25 dB | −0.81 dB | −0.60 dB |
| MIC | 10 kHz | −1.44 dB | −1.09 dB | −0.91 dB |
| FM | 100 Hz | −0.99 dB | −0.53 dB | −0.30 dB |
| FM | 1 kHz | −0.91 dB | −0.52 dB | −0.31 dB |
| FM | 10 kHz | −2.11 dB | −1.81 dB | −1.66 dB |

Dati calcolati in doppia precisione con Python locale usando la stessa equazione complessa; **non** sono simulazioni SPICE né misure del segnale vero. Il codice versionato `test_mic_fm_passive_v734.py` è stato aggiornato con riferimenti numerici di regressione e test del cambiamento della risposta al variare di Req; l'esecuzione della suite completa su file nativi GitHub **non è ancora attestata**.

### Decisioni tecniche vincolanti

- Non confondere `Rin` selezionata dal PGA e `Req` effettiva: TI fornisce formule diverse per modalità single-ended/differenziale. Non assegnare adesso un taglio passa-alto reale da una sola capacità e `Rin` indicata.
- Per le vie in ricezione microfono/FM, definire configurazione PGA in firmware, ampiezza massima e impedenza della sorgente; verificare i guadagni su tutti i percorsi ADC selezionati.
- Confermare che le etichette MIC/FM si colleghino davvero ai pin previsti del codec nella netlist nativa e che il filtro sia compatibile con le specifiche della comunicazione radio da soddisfare; la mappatura topologica locale e il modello non bastano.
- Non modificare il CAD per ottenere semplicemente una risposta numerica apparentemente migliore. Nessuna nuova assunzione su PCB, ERC, layout e footprint; restano NO FAB / NO TX.

## Audit indipendente pin fisici U6202 (V7.34, 12 novembre 2026)

**Confronto fonte primaria:** Texas Instruments `TLV320AIC3204` SLOS602E, RHB bottom view, tabella pin funzione (pagine stampate 5–7), https://www.ti.com/lit/ds/symlink/tlv320aic3204.pdf . La variante embedded in `04_KiCad/Modulo_MCU_CODEC_V7.33_YAGEO_8R_0402_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch` utilizza simbolo `S3900E:TLV320AIC3204_RHB32_DRAFT` origin (400,160), unità 1, rotazione 0°.

Il controllo sorgente individua **33 pin numerati 1–33 senza duplicati**, nomi compatibili con SLOS602E e le seguenti etichette *locali applicate agli endpoint dei pin* (non è una netlist elettrica esportata da KiCad):

| Pin fisico | Pin TI | Etichetta sul terminale in schema | Risultato |
| ---: | --- | --- | --- |
| 4 | DIN/MFP1 | AUDIO_I2S_TX | Compatibilità direzione da verificare rispetto al MCU |
| 5 | DOUT/MFP2 | AUDIO_I2S_RX | Compatibilità direzione da verificare rispetto al MCU |
| 6 | IOVDD | 3V3_CODEC_IO | 3.3V nominale nel campo 1.1–3.6V TI, transitori HOLD |
| 9 | SCL/SS | CODEC_I2C_SCL | I2C previsto |
| 10 | SDA/MOSI | CODEC_I2C_SDA | I2C previsto |
| 12 | SPI_SELECT | GND | Se livello effettivo 0, selezione I2C secondo TI; necessaria verifica ritorno |
| **13** | **IN1_L** | **MIC_CODEC_IN** | Pin fisico MIC corretto; routing ADC/PGA HOLD |
| **16** | **IN2_R** | **FM_CODEC_IN** | Pin fisico FM corretto; routing ADC/PGA HOLD |
| 17 | AVSS | GND | Ritorno analogico fisico/layout HOLD |
| 18 | REF | CODEC_REF | C6202 10uF alla massa locale; valore nominale compatibile, DC-bias HOLD |
| 24 | AVDD | CODEC_AVDD_LDO_OUT | Sequencing e decoupling effettivo HOLD |
| 26 | LDOIN | 3V3_CODEC_LDOIN | Alimentazione LDO, transitori HOLD |
| 28 | DVSS | GND | Ritorno digitale/layout HOLD |
| 29 | DVDD | CODEC_DVDD_LDO_OUT | Sequencing e decoupling effettivo HOLD |
| **30** | **LDO_SELECT** | **CODEC_LDO_SELECT** | **Livello effettivo startup NON dimostrato** |
| 31 | RESET | CODEC_RESET_N | Reset startup e firmware HOLD |
| **33** | **EP_GND_THERMAL_PAD** | **GND** | Endpoint locale documentato; via/plane/stencil reale HOLD |

Pin opzionali privi di etichetta locale nel simbolo: 8, 11, 14, 15, 20, 21, 25, 27, 32; ciò non dimostra connessione o non connessione nella netlist gerarchica. Non associare a tali pin una funzione di default inventata.

### Esito e azioni necessarie

1. **Nessuna evidenza di inversione pin fisici MIC/FM.** Il cablaggio locale usa IN1_L e IN2_R, compatibili con ingressi analogici TI. Attenzione: l'abilitazione del percorso ADC e la selezione ingresso/guadagno PGA sono configurazioni **software**, non provate da questo audit.
2. **Priorità elettrica:** stabilire cosa porta `CODEC_LDO_SELECT` sul pin 30 alla prima alimentazione, prima della configurazione MCU (pullup/down, tensione, drive, reset). Il pin seleziona l'abilitazione D-LDO; stabilire anche i livelli di `CODEC_RESET_N`, `3V3_CODEC_IO` e `3V3_CODEC_LDOIN` in avvio. Non aggiungere ponti o `PWR_FLAG` artificiali.
3. Verificare che le etichette audio MIC/FM e I2S raggiungano i pin MCU/AFE attesi nell'**intera netlist nativa** a sette fogli, senza violare 15 interfacce cross-domain OPEN/HOLD. Un match label–simbolo NON equivale a prova di rete end-to-end.
4. Per un'eventuale ECO di sicurezza su startup occorrono documentazione TI esatta, stato programmato del MCU, soluzione circuitale qualificata, poi confronto ERC/netlist prima/dopo KiCad9. Nessuna modifica elettrica autorizzata oggi dal solo parsing.

**Prova aggiunta:** `03_Verifiche/V7.34/test_codec_vendor_pinmap_v734.py`, audit sorgente fail-closed di 33 coppie pin-numero/nome rispetto a TI e di etichette terminali sulla baseline KiCad. Verifica incrociata separata effettuata sul sorgente GitHub: **33/33 pin univoci**, relazioni prioritarie 12/13/16/17/18/24/29/30/31/33 concordi. **Non dichiarare eseguita la nuova suite Python né KiCad9 ERC/DRC**. PR DRAFT, NO FAB / NO TX.
