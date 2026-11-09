# Superstar 3900 SMD Evolution — Rapporto tecnico V6.3

**9 novembre 2026 · sviluppo progettazione completa radio · NON FAB · NO TX.**

## Contenuto concretamente aggiunto

La V6.3 definisce l'architettura d'ingresso della radio alimentata nominalmente a 13,8 V: protezione inversa, sovratensione/sovracorrente in studio, conversione 5 V/3,3 V, rami audio, RF e codec. Aggiunti **79 componenti candidati, 219 terminali funzionali con reti nominate, 12 trasformazioni di potenza e 11 gruppi di carico**. Le interfacce con V6.0/V6.1/V6.2 sono riportate negli allegati. **Non sono pin fisici verificati, non sono ancora `.kicad_sch` nativi, non generano PCB rilasciabili.**

Tutte le revisioni precedenti, compresi KiCad RX, manuale e storico, sono conservate immutate. Nessuna emissione RF è stata autorizzata; connettore del finale J907 **DNI**.

## Prima progettazione di potenza

| Blocco | Scelta V6.3 | Stato |
|---|---|---|
| Ingresso | J901, fusibile F901 5 A T *provvisorio*, TVS D901 *da selezionare*, induttanza CM L901 | Non dimensionati per carico finale e surge |
| Protezione | U901 **LM74900-Q1**, Q901/Q902 N-FET back-to-back (sorgenti ai lati e drenaggi collegati attraverso shunt R901 5 mΩ), comando ON S901→VS | Direzione funzionale corretta, SOA/timer/ladders incompleti |
| 5 V | U902 **LM61460** 400 kHz, L902 4,7 µH, COUT 4×22 µF, feedback 100 kΩ / 24,9 kΩ | Componenti candidato dalla nota applicativa TI |
| 3,3 V digitali | U903 **LM61460** 1 MHz, L903 2,2 µH, COUT 3×22 µF, feedback 100 kΩ / 43,2 kΩ | Componenti candidato dalla nota applicativa TI |
| 3V3_A / 1V8_CODEC | **TPS7A20** LDO da 5 V / da 3,3 V | Preliminari, correnti budget 80/100 mA |
| 13V8_AUD | ramo Q903 high-side, driver da definire e anti-pop | NON regolato, audio classe D soltanto |
| PA RF TX | J907 non montato, nessuna alimentazione | TX bloccata |

**Correzione effettuata prima dei test:** la prima bozza della V6.3 dipendeva dai 3,3 V per attivare il controller che deve generarli. È stata eliminata la dipendenza circolare: S901 SPST meccanico porta EN del LM74900 a VS, J902 di laboratorio resta DNI e R902 47 kΩ impone OFF quando l'interruttore è aperto. L'EN di entrambi i LM61460 è alimentato dal bus protetto tramite R915 e pull-down R914; il pin è tollerante a tensioni di ingresso secondo TI. PGOOD open drain richiede pull-up a 3,3 V (R916/R917). L'avvio reale **non è stato misurato**.

## Bilancio di potenza e calcoli effettivi

I carichi sono **ipotesi progettuali**, non correnti misurate né dati certi dei moduli ancora incompleti. Nel modello nominale 13,8 V, rendimento buck ipotizzato 90% sul 5 V e 88% sul 3,3 V, resistenza totale del percorso di ingresso ipotizzata 15 mΩ, la corrente d'ingresso è **0.750 A**. Il budget sul buck 5 V comprende il consumo dell'LDO analogico; quello 3,3 V comprende l'LDO 1,8 V.

Per 25,000 combinazioni indipendenti **non probabilistiche** di carico (da 75% del nominale all'inviluppo assunto), tensione 11,88–15,36 V ed efficienza dei due buck (84–94% e 80–94%):

| Parametro | 99° percentile del campione | Massimo del campione |
|---|---:|---:|
| Corrente d'ingresso | 2.005 A | 2.144 A |
| Corrente buck 5 V | 1.041 A | 1.125 A |
| Corrente buck 3,3 V | 0.593 A | 0.644 A |
| Dissipazione LDO 3V3_A | 0.135 W | 0.136 W |
| Dissipazione LDO 1V8 | 0.149 W | 0.150 W |

**Escluso completamente il futuro finale RF**, che potrebbe richiedere ampia corrente e un altro fusibile/cablaggio. Il fusibile V6.3 da 5 A, le soglie e il dimensionamento dei MOSFET non autorizzano la TX. Inoltre il Monte Carlo non sostituisce analisi worst-case, profilo reale dei carichi o revisione del fabbricante.

I rapporti nominali di feedback con Vref ideale 1,000 V danno **5.0161 V** e **3.3148 V**; la precisione sul sistema fisico dipenderà da riferimento, tolleranze, derating e layout.

## Transitorio e risposta ideale

Il datasheet LM74900-Q1 fornisce il rapporto ideale per CdVdT: con Cbulk 470 µF, Cdvdt 47 nF e IHGATE 55 µA, il modello di sola carica del condensatore produce **0.550 A** e una rampa fino a 13,8 V di **11.79 ms**. Esclude il carico dei buck durante la rampa, resistenze di linea, gate/MOSFET/SOA, isteresi e tolleranze; non è un'onda certificata da TI.

Una perdita istantanea della sorgente, con sole capacità e consumo nominale costante, dà un limite di hold-up **1.20 ms** sul bus da 13,8 V fino alla soglia nominale 11,88 V V6.2 (nominale 470µF), oppure **0.96 ms** con 20% di capacità in meno. Le capacità locali isolate dei buck darebbero circa 0.039ms (5 V da 5→4,5 V) e 0.029ms (3,3 V da 3,3→3 V). **La risposta reale dei convertitori può essere diversa**: non abbiamo simulato il loro loop, il carico dinamico o il hold-up simultaneo.

## Verifica buck ideale e limite di modalità di conduzione

A 13,8 V, i calcoli nel modello in corrente continua (CCM) danno ΔI induttore **1.696 A** sul 5 V e **1.141 A** sul 3,3 V. La conduzione continua richiederebbe in quel modello correnti medie circa **0.848 A** e **0.571 A**. I carichi nominali ipotizzati sono inferiori: i buck potrebbero lavorare in DCM/PFM; le stime di ripple capacitivo CCM (11.0 mV e 4.0 mV) **non si possono applicare al funzionamento nominale come ripple effettivo**. Serviranno modelli vendor e misure spettrali per le interferenze nella banda CB (26–28 MHz).

## Verifiche e risultato

- **45 test statici/numerici V6.3 PASS**, inclusi casi di perturbazione di pin, shunt, cambio rete, ponte RF TX, duplicati, cicli di dipendenza e mancanza alimentazione.
- Test sulle **512 combinazioni** di ingresso del modello PowerStatus: il TX rimane sempre FALSE. Logica MCU non sostituisce protezione hardware indipendente.
- **6 suite selezionate PASS**: V5.9, V6.0, due V6.1, V6.2, V6.3. Non è stato ripetuto tutto lo storico dalla V4.0.
- `kicad-cli` e `ngspice` **non disponibili**: schema KiCad, ERC/DRC nativi, simulazioni SPICE transistor/vendor, prove climatiche e collaudo fisico **NON ESEGUITI**.
- Ogni file storico V6.2 preservato e le vecchie versioni dei documenti attivi salvate come snapshot SHA-256.

## Blocchi aperti prima di qualunque produzione

Selezionare fusibile/TVS (energia di impulso, I²t, soglia di lavoro e verifica della sorgente), completare circuito LM74900-Q1 con tutti i pin, resistori e timer, MOSFET SOA e gestione inrush reale, selezione high-side audio Q903, temperatura reale di buck e LDO, cap MLCC dopo DC bias, taratura oscillatori, grounding EMI/ESD/EMC, polarizzazione reale dei moduli RF, regolazione per il finale TX, e schema/PCB KiCad. **Non collegare il finale RF o inviare Gerber: nessuna validazione di fabbricazione.**

## Riferimenti del produttore

- [Texas Instruments — LM74900-Q1](https://www.ti.com/product/LM74900-Q1)
- [Texas Instruments — LM61460](https://www.ti.com/product/LM61460)
- [Texas Instruments — TPS7A20](https://www.ti.com/product/TPS7A20)
- [Texas Instruments — TPSM63606 (possibile modulo alternativo)](https://www.ti.com/product/TPSM63606)

**Prossima V6.4:** progettazione dettagliata del sintetizzatore PLL/LO e distribuzione clock (LMX2572, configurazione filtri e interfaccia MCU), con calcoli di frequenza, verifiche programmatiche e simulazioni numeriche possibili, preservando i blocchi V6.0–V6.3 e la futura campagna finale di verifica integrale.
