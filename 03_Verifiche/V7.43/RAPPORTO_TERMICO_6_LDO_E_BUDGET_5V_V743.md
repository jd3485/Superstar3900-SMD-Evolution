# V7.43 — Sei TPS7A2033: budget del ramo 5 V e limite termico SOT-23-5

Data: 13 novembre 2026. Base **V7.42** PR#45 integrata, contratto AUX/MCU approvato **solo come descrizione HOLD**, NON come collegamento elettrico. **Aggiornamento tecnico:** durante l'audit dei sei pin sono stati individuati il pin U2.1 IN privo di etichetta/filo nel PLL AUX. Una ECO CAD V7.43 in una copia separata di AUX + master sette fogli aggiunge SOLO una etichetta 5V al pin U2.1, mantenendo in HOLD i collegamenti tra moduli. È necessaria la prova KiCad9 nativa before/after.

## Nuova verifica fondamentale — dissociazione della portata di corrente e dell'ammissibilità termica

Fonti Texas Instruments verificate:
- **TPS7A20**, datasheet *SBVS338H* revision July 2024, [datasheet ufficiale](https://www.ti.com/lit/ds/symlink/tps7a20.pdf) §5.3–5.5 p.5–6: `TPS7A2033PDBVR`, package DBV (SOT-23-5), `I_OUT≤300mA`, `T_J operativo≤125°C`, resistenza termica `RθJA=187.1°C/W` *per la board usata dal produttore nel test JEDEC*. Non è un `RθJA` garantito per il futuro layout del progetto. Corrente GND tipica a IOUT=300mA `I_GND≈2mA`, **non garantita come massimo**.
- **TPS54202**, datasheet *SLVSD26C* revision Feb 2026, [TI PDF](https://www.ti.com/lit/ds/symlink/tps54202.pdf), §1 e §5.3–5.4, convertitore buck `I_OUT max 2A` totale, uscita condivisa `5V_RF_PREREGULATED`. Ha limitazione di corrente, ma il rating **non è prova** di erogazione a qualunque temperatura e qualunque PCB.
- **TDK MPZ2012S601ATD25**, [scheda](https://product.tdk.com/en/search/emc/emc/beads/info?part_no=MPZ2012S601ATD25): bead nominalmente 2A, DCR massimo 100mΩ, `Z(100MHz)` 600Ω nominali; rating del bead distinto dai 2A condivisi del buck.

La potenza ideale dissipata da ogni LDO in regolazione vale circa `P_LDO=(VIN−VOUT)*I_OUT + VIN*I_GND`. A `VIN=5V,VOUT=3.3V` e senza termine `I_GND`, `P=1.7×I_OUT`. L'eventuale ingresso più basso dei quattro LDO MCU dopo il bead diminuisce `VIN−VOUT`, ma è ancora da verificare il requisito di regolazione. Usare 5V come caso illustrativo condiviso non equivale a una tensione misurata a tutti i pin.

| IOUT *per un LDO* (mA) | P ideale senza IGND (mW) | ΔTJ con θJA=187.1°C/W (°C) |
|---:|---:|---:|
| 50 | 85 | 15.9 |
| 100 | 170 | 31.8 |
| 150 | 255 | 47.7 |
| 200 | 340 | 63.6 |
| 300 | 510 | 95.4 |

A `T_A=25°C` e `I_OUT=300mA` l'esempio porta `T_J≈120.4°C`, già vicino a 125°C **anche trascurando IGND**. A `T_A=85°C`, lo stesso esempio porterebbe `T_J≈180.4°C`, **oltre l'intervallo operativo TI**. La soglia puramente teorica per restare entro 125°C a 85°C ambiente, senza IGND e usando θJA del test TI, è `I_OUT≤(125−85)/(187.1×1.7)=0.1258A`, circa **126mA per singolo LDO**. **Questo NON è un nuovo rating garantito di 126mA**: nel layout reale θJA, correnti a vuoto, effettiva dissipazione, vicinanza dei sei regolatori, temperatura del contenitore e hotspot sono ignoti. Includendo `I_GND≈2mA tipici` al punto 300mA l'esempio P aumenta da 510mW a circa 520mW: dato tipico, non worst-case.

## Identificazione topologica di tutti i sei carichi 3.3V

| Ref reale | Gruppo scheda | Alimentazione IN | Rete OUT 3.3 V | Ritorno GND |
|---|---|---|---|---|
| **U6203** | MCU_CODEC | `5V_DIGITAL_FILTERED` | `3V3_AUDIO_CLK` | `GND` |
| **U6204** | MCU_CODEC | `5V_DIGITAL_FILTERED` | `3V3_MCU` | `GND` |
| **U6205** | MCU_CODEC | `5V_DIGITAL_FILTERED` | `3V3_CODEC_IO` | `GND` |
| **U6206** | MCU_CODEC | `5V_DIGITAL_FILTERED` | `3V3_CODEC_LDOIN` | `GND` |
| **U2** | AUX_PLL | `5V_RF_PREREGULATED` | `3V3_PLL_INPUT_FROM_LDO` | `GND_MAIN` |
| **U3** | AUX_PLL | `5V_RF_PREREGULATED` | `3V3_REF_LDO` | `GND_MAIN` |

Tutti i riferimenti e nomi dei nodi OUT/IN/return sono ottenuti **direttamente dalle posizioni fisiche dei pin** dei simboli KiCad inclusi nel progetto, non inferiti dal solo nome dei componenti. La matrice completa macchina è `03_Verifiche/V7.43/MATRICE_CARICHI_TERMICA_5V_V743.json`, sottoposta a prove su sorgenti. **Non esiste ancora una misura o un modello validato della corrente assorbita da ciascuna rete**. Per questo `load_max_known_a:null` e `transient_max_known_a:null` restano *volutamente* vuoti, non zero.

## Limiti di carico del buck e del bead

- Se i sei LDO erogassero 300mA ciascuno, la **somma delle loro correnti OUT** sarebbe 1.8A. Resterebbero nominalmente 0.2A rispetto al rating 2A del buck, **prima** di includere I_GND, utenze 5V dirette, transienti, altre sezioni, inrush e derating termico. Quindi **la condizione a 1.8A NON è approvata**.
- Quattro LDO MCU sono dietro **FB6201**: somma nominale OUT 4×0.3=**1.2A**. Due LDO AUX_PLL sono sul ramo 5V preregolato, esterni al bead: 2×0.3=**0.6A**. Ogni altra utenza su `5V_DIGITAL_FILTERED` consuma ulteriore corrente nel bead; ogni altra utenza su `5V_RF_PREREGULATED` consuma ulteriore corrente sul buck.
- Il buck ha una sorgente power input protetta da eFuse e fusibile F200 sulla **tensione 13.8V**: non confrontare direttamente 1.5A della fusibile con il 2A 5V in uscita senza un bilancio di potenza/efficienza e analisi di spunto.
- **Condizioni di signoff futuro:** per tutte le modalità RX, scanning, startup, standby, low voltage e temperatura, definire `I_LDO_OUT`, `I_LDO_IN/I_GND`, `I_other5V`, `I_FB6201`, `T_A`, `T_J`, `RθJA(board)`, rumore/ripple, rampa e ritorni. Validare `I_5V,total≤I_buck_permitted(T,VIN,PCB)`, `I_bead≤I_bead_permitted(T,I_DC)`, `T_J_each≤125°C` con margine non nullo e compatibilità temporale. Le soglie e il margine di progetto devono essere definiti prima del signoff, non scelti dopo aver visto i risultati.

## Gate realizzato e limiti di interpretazione

`03_Verifiche/V7.43/test_six_ldo_thermal_budget_v743.py` verifica 24 condizioni, inclusi sei **pin OUT reali**, i nomi reti IN/OUT/GND dei due domini, la contabilità differenziata buck/bead, il modello `P=(VIN−VOUT)I+VIN*IGND`, i tre esempi ambientali, e rifiuta una certificazione se mancano carichi, temperatura e modello di PCB. La sorgente JSON contiene flag **fail-closed**, non fabbrica/transmette. Il workflow V7.43 ora è **KiCad9 nativo e mirato** (ERC/netlist sette fogli prima/dopo), perché si corregge davvero U2.1; conserva prove sorgente e termiche dei sei LDO. Registrare l'esito soltanto dopo workflow reale.

**Conclusione:** *nuovo blocker termico individuato* (non guasto dimostrato), e **un pin U2.1 non alimentato nella copia precedente di AUX** da correggere con ECO mirata. Il valore di θJA e 300mA non possono essere combinati per dichiarare sicuro l'esercizio in contenitore caldo. Non sostituire i LDO senza correnti reali e analisi noise/PSRR/EMC. `main` fino al merge resta V7.42; baseline CAD V7.41 = 134 componenti, 101 reti, 32 footprint mancanti, ERC 36 errori/221 warning. **15 interfacce cross-domain OPEN/HOLD, GND_MAIN/GND separati, SG48 HOLD, Y1 TCXO pin10 HOLD, NO FAB / NO GERBER / NO PCBWAY / NO TX**. Percentuale PCB storica ~10%, nessun incremento per i soli audit.

## ECO CAD V7.43 — U2 IN non collegato nel sorgente AUX precedente

Audit in `03_PLL_LDO_TCXO.kicad_sch`: `U2 TPS7A2033PDBVR` simbolo `S3900E:TPS7A2033_DBV` centro (412,80), orientamento 0. Secondo definizione embedded, pin1 IN endpoint **(388,72)**, pin3 EN endpoint (388,80), pin2 GND endpoint (388,88), pin5 OUT endpoint (436,72). La copia precedente conteneva **etichetta `5V_RF_PREREGULATED` solo su EN (388,80)** e nessuna etichetta né segmento `wire` su **IN (388,72)**. Contrariamente a U3 (IN=388,165, EN=388,173, entrambi correttamente etichettati), U2 non riceveva una alimentazione dimostrabile. **È un errore elettrico del sorgente CAD, non una semplice questione di documentazione.**

Correzione motivata da TPS7A20 §4 DBV pin1 IN, pin3 EN e raccomandazione supply: https://www.ti.com/lit/ds/symlink/tps7a20.pdf . Aggiunta SOLO `(label "5V_RF_PREREGULATED" (at 388 72 0) ...)` alla copia **V7.43** `04_KiCad/Gerarchico_Alimentazioni_V7.43_U2_LDO_IN_REVIEW_NOT_FOR_FAB/03_PLL_LDO_TCXO.kicad_sch`. Tutti gli altri sottofogli AUX copiati senza differenza. Nuovo master `04_KiCad/Assemblaggio_RX_Power_V7.43_U2_PLL_IN_REVIEW_NOT_FOR_FAB/` referenzia AUX V7.43 ma mantiene invariati MCU V7.41 e RX, senza nuove cross-domain connessioni. Test `03_Verifiche/V7.43/test_u2_pll_input_native_v743.py` verifica l'esatta differenza sorgente, 134 comp invariati, **solo pin U2.1** che acquisisce `5V_RF_PREREGULATED`, e ERC non peggiorato. **Non pre-assegnare numeri di reti o esito ERC finale fino a nuovo run nativo.** Il root resta INDEX/REVIEW: 15 interfacce OPEN/HOLD, `GND_MAIN` non unito a `GND`, SG48, Y1 pin10, **NO FAB / NO GERBER / NO TX**.
