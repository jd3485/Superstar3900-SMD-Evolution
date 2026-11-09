# S3900E V1.0 - alimentazione 13,8 V -> 5 V, core buck (BOZZA NON FABBRICABILE)

## Scelta tecnica

Si introduce il TPS54202DDCR, 6 pin SOT-23-6, buck sincrono nominale 500 kHz, intervallo d'ingresso raccomandato 4,5-28 V, corrente d'uscita massima 2 A. **Questo foglio NON comprende la protezione a monte** contro inversione di polarita, sovratensioni, sovracorrenti esterne o disturbi automotive. Il suo nodo di ingresso si chiama `BUCK_VIN_PROTECTED` proprio per indicare tale dipendenza.

Per il primo banco di prova il riferimento TI per ingresso 8-28 V e uscita 5 V e una base di calcolo; l'uso definitivo per la radio e condizionato a protezioni, dissipazione, EMI e rumore del ricevitore. Non trasferire direttamente 13,8 V ai TPS7A20 a valle.

## Collegamenti (schematico S3900E_5V_BUCK_TPS54202_V1_0_DRAFT.kicad_sch)

| U100 pin | Nome | Rete |
|---:|---|---|
| 1 | GND | GND_RF_SUPPLY |
| 2 | SW | BUCK_SW -> L100 15uH -> 5V_RF_PREREGULATED |
| 3 | VIN | BUCK_VIN_PROTECTED |
| 4 | FB | BUCK_FB |
| 5 | EN | BUCK_EN (R103 510k da VIN, R104 105k a GND) |
| 6 | BOOT | BUCK_BOOT (C102 100nF fino a BUCK_SW) |

Altre reti: C100 10uF 35V, C101 100nF 50V tra VIN e GND; C103/C104 22uF 25V fra VOUT e GND; R100 49.9 ohm da VOUT a BUCK_DIV_TOP, R101 100k fra BUCK_DIV_TOP e FB, C105 75pF in parallelo a R101 e R102 13.3k da FB a GND. I valori sono quelli del reference design TI, non dimensionamento definitivo su PCB S3900E.

## Calcoli matematici (non prove SPICE)

- Reference FB tipica TI Vref=0,596 V; output teorico = 0,596*(1+100/13,3) = **5.0772 V**. Nel datasheet il circuito e chiamato 5 V nominali; non presentare come 5,000 V esatti.
- Limiti di riferimento 0,581-0,611 V e resistori +/-1% portano a **4.863 - 5.298 V** nel modello ideale, senza altre fonti di errore.
- A Vin=13,8 V, ripple induttore **0.428 A picco-picco** a 500 kHz e 15uH. E un modello di buck ideale, non corrente osservata.
- Quando scende la corrente di carico il TPS54202 usa pulse-skip; senza prove EMI sul ricevitore NON si puo proclamare la linea silenziosa.

## Punti bloccanti e test prima di produzione

1. Dimensionare front-end protetto: fusibile, inversione di polarita, scelta e verifica TVS rispetto a VIN max 28V e transitori della destinazione d'uso.
2. Scegliere MPN effettivi per 100nF 50V, condensatori di uscita con capacita effettiva e induttore con saturazione verificata.
3. KiCad CLI: aprire lo schematico, eseguire ERC e confrontare il netlist esportato con il CSV intenzionale; correggere eventuali discrepanze.
4. Layout: ingressi e output vicino a U100, minimizzare anello SW/BOOT, piano GND, via termiche, feedback lontano da SW e ritorno Kelvin (TI sezione layout).
5. SPICE: transitorio, start-up, step di carico, ripple; misure prototype: Vout, ripple, emissioni condotte/radiate e disturbi AM/SSB con radio accesa.
6. Integrare gerarchicamente nel progetto PLL (foglio per ora *separato*); EN/LDO e sequenziamento non ancora validati.
7. Il TCXO TXC 7N-12.800MBP-T **mantiene aperto il pin 10**: il datasheet della serie indica AFC oppure GND; senza configurazione di parte attestata non collegarlo arbitrariamente.

## Fonti primarie

- Texas Instruments, TPS54202, Rev C (Feb 2026), sezioni 4, 5, 6, 7, Figure 7-1: https://www.ti.com/lit/ds/symlink/tps54202.pdf
- TI TPS54202EVM-716, manuale / BOM, Rev A: https://www.ti.com/lit/ug/slvuap3a/slvuap3a.pdf
- TXC 7N series (pad 10 AFC or GND): https://www.nyang-tech.com/datasheet/1164170051/TXC-Corporation/7N-12.800MBP-T.pdf
