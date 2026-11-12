# V7.38 — Power-down U6205/U6206 TPS7A2033PDBVR: carica residua e screening della corrente inversa

**Data:** 13 novembre 2026. **Repository** `jd3485/Superstar3900-SMD-Evolution`. **Baseline tecnica:** V7.37 PR #40 MERGED, e CAD V7.36 a 7 fogli V7.36 (134 componenti / 101 reti / ERC 36 errori +221 warning, 33 footprint ancora HOLD). Nessuna modifica CAD in questa revisione: analisi quantitativa di un rischio elettrico nuovo, con gate che legge le capacità collegate ai terminali reali.

## 1. Evidenza della topologia attuale

Modulo `04_KiCad/Modulo_MCU_CODEC_V7.36_C6231_MURATA_GRM15_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch`.

| Uscita LDO | Componenti tra rail e GND presenti sul foglio | Capacità nominale totale | Carica teorica a 3.3 V |
|---|---|---:|---:|
| `U6205 TPS7A2033PDBVR` `3V3_CODEC_IO` | C6201=100nF, C6224=1uF, C6231=100nF | **1.2µF** | **3.96µC** |
| `U6206 TPS7A2033PDBVR` `3V3_CODEC_LDOIN` | C6207=100nF, C6208=10uF, C6226=1uF | **11.1µF** | **36.63µC** |

Capacità nominali, **NON Ceff** in condizioni di DC bias, T, aging, tolleranza. Nessuna prova sul carico contemporaneo o sulle capacità fuori dal foglio. Il modello non considera elementi parassiti, ramo di scarica attiva, carichi e regolatori upstream.

## 2. Divieto di inferire direttamente la corrente inversa

**Fonte produttore TI:** TPS7A20 SBVS338H Rev.H §6.3.7 *Active Discharge* e §6.4.3 *Dropout*, https://www.ti.com/lit/ds/symlink/tps7a20.pdf . TI indica che il circuito di scarica attiva dell'uscita nei TPS7A20 versione P è attivato da `EN LOW` oppure da input sotto UVLO; **non affidarsi** a questo circuito per scaricare una grande capacità quando l'ingresso collassa, perché la corrente **OUT → IN** può danneggiare il regolatore. TI prescrive di limitare tale corrente inversa a **non più del 5% della corrente nominale per un periodo breve**. Con rated 300mA, limite indicativo **15mA** per un periodo breve (NON rating continuo, NON autorizzazione a far circolare 15mA senza limite di tempo).

La formula `I_equiv = C_nom × ΔV/Δt × f_reverse` quantifica **solo la porzione ipoteticamente trasferita** dalla carica dei condensatori attraverso un percorso inverso, con `f_reverse` arbitrario compreso fra 0 e 1. **NON è la corrente inversa misurata del TPS7A20.** La topologia può scaricare energia nei carichi, nella scarica attiva, tramite protezioni o mediante altri percorsi. Senza la frazione e le funzioni temporali delle rail, qualsiasi stima del vero picco è indimostrata.

| Scarica ipotetica 3.3V → 0V | C 1.2µF, tutta carica sul percorso inverso | C 11.1µF, tutta carica sul percorso inverso |
|---|---:|---:|
| Δt = 1ms | 3.96mA equivalenti | **36.63mA equivalenti** |
| Δt = 5ms | 0.792mA equivalenti | 7.326mA equivalenti |
| Δt min per `I_equiv ≤ 15mA` con f_reverse=1, corrente media | 0.264ms | 2.442ms |

**Interpretazione:** anche uno spegnimento della durata di 1ms **non dimostra guasto**, ma lo scenario conservativo sulla rail LDOIN produce una corrente media ipotetica >15mA se tutta la carica passa all'indietro. Il confronto con il limite TI non è utilizzabile come signoff: il limite vale per la corrente inversa **reale e per tempo breve**, mentre il modello è un trasferimento di carica ideale. Un carico che assorbe il 100% della carica può dare corrente inversa zero; questo è ammesso nel modello `f_reverse=0`.

## 3. Priorità tecnica per chiudere il rischio

1. Ricostruire su netlist nativa e schemi effettivi il percorso **OUT→IN** dei TPS7A2033PDBVR (U6205 e U6206), le capacità del ramo `5V_DIGITAL_FILTERED` e le eventuali protezioni e scariche upstream; le etichette locali non attestano il percorso fisico e la sequenza tra più moduli.
2. Simulare con un modello **validato** della scarica attiva e della corrente inversa TI, parametrizzando V_IN(t), V_OUT(t), carichi, Ceff, ESR, tolleranze; in alternativa dimostrare con prove reali sul prototipo la corrente inversa nel peggior caso di spegnimento e brownout. **Non si può desumere la corrente inversa reale dalla sola formula capacitiva**.
3. Verificare i 10µF su LDOIN, inclusi capacità DC-biased e caratteristiche di stabilità/avvio. Non ridurli arbitrariamente: potrebbe peggiorare il ripple o una sequenza.
4. Qualificare un eventuale clamp/diodo di protezione OUT→IN, scarica condizionata, supervisore upstream o scelta diversa LDO **solo dopo** confronto delle correnti normali, reverse current, tensioni, dissipazione, ripple e polarità. Non introdurre un collegamento fra due domini soltanto per ottenere ERC verdi.
5. Proseguire separatamente la verifica V7.37 sotto VPOR e l'ordine MCU RESET/ALDO; **nessuna garanzia** di sequenza sicura prima di queste analisi.

## 4. Gate riproducibile

`03_Verifiche/V7.38/test_codec_ldo_reverse_current_v738.py` contiene **20 unit test** di inventory KiCad, somma capacità nominali, conversione di unità, carica, frazioni ipotetiche, tempi di trasferimento condizionali e **fail closed** quando manca un tracciato validato della corrente inversa. Test soltanto con libreria standard Python; non necessita di KiCad9 perché CAD e footprint non cambiano. CI PR separata e breve; aggiornare questo file con esito effettivo dopo esecuzione, non inventare un PASS.

**Stato di progettazione:** *rischio reverse-current identificato, non guasto dimostrato*. Nessuna modifica di rete, MPN o footprint in V7.38. `main` resta V7.37 fino a verifica e merge; nessuna PCB completa, nessuna nuova ERC/DRC, 15 interfacce OPEN/HOLD, SG48 HOLD, Y1 pin10 AFC/GND HOLD, **NO FAB / NO GERBER / NO PCBWAY / NO TX**. Percentuale PCB storica ~10% stimata, nessun incremento da un modello.

