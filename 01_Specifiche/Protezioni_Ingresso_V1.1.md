# Progetto front-end di protezione SMD - V1.1 (BOZZA)

Il nuovo foglio schematico `04_KiCad/Sorgenti_Protezione_Ingresso_V1.1/S3900E_EFUSE_TPS26600_V1_1_DRAFT.kicad_sch` e un *sotto-modulo* che protegge **solamente il convertitore ausiliario 5V** di V1.0. Non e dimensionato per la potenza assorbita dal finale trasmittente e dall'audio PA.

## Sequenza elettrica

`PWR_13V8_AUX_RAW` -> F200 (fusibile SMD, valore finale TBD) -> `EFUSE_VIN` -> U200 TPS26600 (PWP) -> `BUCK_VIN_PROTECTED` -> buck TPS54202 V1.0 -> 5V LDO.

D200 rappresenta una piazzola TVS bidirezionale **DNP/non montare**. Si scegliera un componente solo dopo il modello di transitori e il coordinamento con il fusibile e l'eFuse. EMI input e filtro di ripple dello switching sono ancora da progettare.

## Logica e soglie nominali

- R200 = 365 kOhm tra EFUSE_VIN e UVLO_NODE; R201 = 16.2 kOhm tra UVLO_NODE e OVP_NODE; R202 = 30.1 kOhm tra OVP_NODE e EFUSE_RTN.
- Datasheet TI Eq 10-11, comparatore Vref nominale 1.19 V.
- Soglia UVLO salita = 1.19 * (365 + 16.2 + 30.1) / (16.2 + 30.1) = **10.571 V**.
- Soglia OVP salita = 1.19 * (365 + 16.2 + 30.1) / 30.1 = **16.261 V**.
- R203 = 8.2 kOhm da ILIM a EFUSE_RTN: I_OL = 12 / 8.2 = **1.463 A** teorici.
- Con R_ON tip 150 milliohm, a I=1A dissipa ~0.150 W; a I=Ilim ~0.321 W. Stima non equivalente a validazione termica.
- Corner analitici con resistori ±1% e riferimento comparatore 1.17-1.225V (senza leakage): UVLO **10.21 - 11.08 V**, OVP **15.69 - 17.05 V**. Non sono valori garantiti del circuito completo.

## ATTENZIONE: RTN vs GND

**EFUSE_RTN != GND_MAIN.** La tabella TI 9.3.5.5 e la sezione 'Do's and Don'ts' indicano esplicitamente che collegarli direttamente disabilita la protezione da polarita inversa e puo danneggiare il circuito. Tutti i componenti di controllo (UVLO/OVP/ILIM/dVdT e pad centrale) devono riferirsi a EFUSE_RTN; pin GND deve riferirsi a GND_MAIN. Nella PCB sono due domini diversi e NON devono essere uniti dal progettista.

## Non definito / bloccante

- F200: MPN, curva intervento, I²t, tensione d'esercizio e coordinamento con eFuse.
- D200: TVS solo non montata, surge IEC e protezione cavi da validare.
- MODE, SHDN, FLT, IMON per questa fase restano non connessi; MODE aperto e un modo consentito dall'integrato, ma scelta fail-safe generale da completare. Non usare FLT senza valutare polarita inversa.
- Rampa C201 e condensatori C200/C202 sono candidati; ESR, DC bias, inrush, EMI, termica da simulare.
- Footprint e pin visualizzati nello schema generato richiedono apertura in KiCad, vero ERC e confronto con package TI. File non approvato per ordinare.

## Fonti primarie

- TI TPS2660 datasheet SLVSDG2G Rev.G (2019), pin functions p.4-5, §§9.3.5.5,10.2.2,11,12: https://www.ti.com/lit/ds/symlink/tps2660.pdf
- TI TPS2660 product info e ordini: https://www.ti.com/product/TPS2660
