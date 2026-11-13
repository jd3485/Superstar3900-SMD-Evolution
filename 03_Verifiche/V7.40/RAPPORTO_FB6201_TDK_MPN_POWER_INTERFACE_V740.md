# V7.40 — FB6201: selezione TDK 600Ω/2A e isolamento fra AUX POWER e MCU/CODEC

**Data:** 13 novembre 2026. **Base:** V7.39 PR#42 integrata su `main` (squash `94347b21a45a618ccabdf814467dac91acf3751a`). La modifica CAD V7.40 è un'**ECO di identificazione MPN/valore** della ferrite `FB6201` nel nuovo modulo MCU/CODEC e nuovo master di 7 fogli, SENZA unire nuovi domini elettrici, senza footprint non qualificato, NO FAB/NO TX.

## 1. Ricostruzione del percorso reale da sorgenti

- Il master root `04_KiCad/Assemblaggio_RX_Power_V7.36_C6231_MURATA_GRM15_REVIEW_NOT_FOR_FAB/S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_sch` contiene istanze di sheet `AUX_POWER`, `MCU_CODEC` e `RX` **senza alcuna interfaccia gerarchica tra i tre domini**. L'indice non è una radio già collegata. Non considerare due nomi uguali di etichette locali prove di continuità.
- AUX: sotto `04_KiCad/Gerarchico_Alimentazioni_V7.31_AUX_CONNECTORS_ON_GRID_NOT_FOR_FAB/`, `U200 TPS26600PWPT` eFuse è nel sottofoglio `01_EFUSE_AUX.kicad_sch`; `U100 TPS54202DDCR` buck 5 V in `02_BUCK_5V.kicad_sch`; uscita etichettata `5V_RF_PREREGULATED`. Fonte TI https://www.ti.com/product/TPS54202 : **2A continui** nominali dell'IC, non 2A disponibili per il solo codec o sempre garantiti in ogni temperatura/layout.
- MCU/CODEC: `FB6201` 2 pin tra `5V_RF_PREREGULATED` (ingresso pin1) e `5V_DIGITAL_FILTERED` (pin2), il quale alimenta direttamente l'IN di quattro TPS7A2033PDBVR: U6203 (clock 3V3), U6204 (MCU 3V3), U6205 (codec I/O 3V3), U6206 (codec LDOIN 3V3). Al massimo 300mA di ciascun LDO la somma teorica di corrente OUT è **1.2A**, ma corrente IN reale più quiescenti, altre utenze e inrush sono non validati; 300mA è un rating, non corrente nominale reale del progetto. Questo NON basta per dichiarare I_rail,max ≤ 2A.
- Capacità locali su `5V_DIGITAL_FILTERED` sono 14.1µF nominali, quelle codec IOVDD 1.2µF e LDOIN 11.1µF nominali come verificato in V7.39. **Nessuna capacità full-board** è stata sommata arbitrariamente ai moduli isolati. Il bead può vedere corrente DC più componente impulsiva e alterare l'impedenza dello stadio nel transitorio.

## 2. Selezione part number e dati verificati produttore

**Candidato principale: TDK `MPZ2012S601ATD25`**, manufacturer product page https://product.tdk.com/en/search/emc/emc/beads/info?part_no=MPZ2012S601ATD25 . Stato **Production**, AEC-Q200, bead power-line, formato **2012 metrico / EIA0805**, **2.00±0.20 × 1.25±0.20 × 0.85±0.20mm**. `Z(100MHz)=600Ω±25%`, **rated DC current 2A**, **R_DC(max)=100mΩ**, `T_op -55..+125°C` includendo autoriscaldamento. Il vendor riporta un land consigliato parametrico A=0.80, B=1.00, C=1.20mm; **la geometria precisa dei due pad NON è stata ancora convertita in libreria CAD per evitare l'interpretazione arbitraria delle lettere A/B/C**. TDK fornisce curve d'impedenza e modello circuitale: https://product.tdk.com/system/files/dam/technicalsupport/tvcl/pdf/emc_beads_auto_power_mpz2012_ecm.pdf ; il semplice R2=0.052Ω del modello approssimato NON sostituisce l'obbligo di considerare R_DC max100mΩ.

**Confronto documentato, non sostituzione indiscriminata:** Murata `BLM21AG601SN1D`, 600Ω@100MHz e 0805, viene riportata come **700mA** nominali, DCR iniziale max **0.20Ω** da specifica vendor JENF243A_0005AE-01 https://www.murata.com/products/productdata/8796738977822/ENFA0005.pdf ; il rating di alcuni distributori è **600mA** e DCR 0.21Ω. La discrepanza è un ulteriore motivo per non sceglierla automaticamente per un ramo che alimenta 4 LDO; conservare i limiti del produttore e condizioni di derating. TDK 2A lascia più margine con DCR inferiore, ma non è un signoff di tutto il power budget.

## 3. Modello dissipazione *worst-case DC resistivo* (non prova termica)

Con la DCR massima TDK 0.100Ω e corrente DC ipotizzata I:

| I (A) | ΔV=I×0.100Ω | P=I²×0.100Ω |
|---:|---:|---:|
| 0.5 | 50mV | 25mW |
| 1.0 | 100mV | 100mW |
| 1.2 | 120mV | 144mW |
| 1.5 | 150mV | 225mW |
| 2.0 | 200mV | 400mW |

Sono **limiti nominali calcolati con R_DC max del vendor a temperatura/riferimento di prova**; non certificano capacità termica del PCB, limite di temperatura rame, saturazione/nonlinearità, corrente di ripple, impedenza AC su DC bias o self-heating. Corrente vera e stress non misurati.

## 4. Modifica KiCad e gate nativo obbligatorio

Nuovo MCU `04_KiCad/Modulo_MCU_CODEC_V7.40_FB6201_TDK_0805_REVIEW_NOT_FOR_FAB/S3900E_MCU_CODEC_AFE_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch`: `FB6201` valore da `600R@100MHz_CANDIDATE` a `600R@100MHz_TDK_2A_REVIEW`, più proprietà hidden MPN `MPZ2012S601ATD25`. `Footprint` resta **vuoto** fino a verifica geometria TDK/DFM. Il bead non va rappresentato come 600Ω di resistenza continua: è l'**impedenza complessa @100MHz**, DCR max 0.1Ω. Nessuna modifica a pin, nets, reti cross-domain, MPN degli altri 133 componenti o connessioni gerarchiche.

Nuovo master sette fogli `04_KiCad/Assemblaggio_RX_Power_V7.40_FB6201_TDK_0805_REVIEW_NOT_FOR_FAB/`. Test `03_Verifiche/V7.40/test_fb6201_tdk_native_v740.py` verifica source-diff fail closed, 134 comp/101 reti, **zero differenze ai nodi ref/pin/net**, solo valore FB6201, 33 missing footprints invariati, ERC baseline 36 errori/221 warning e nessuna crescita errori, 12 test per DCR/current budget/safety. Nuovo workflow KiCad9 PR-only mirato, senza apt/pip. Non dichiarare CI PASS finché non effettivamente osservata.

## 5. HOLD / prossimo passo

**Power budget completo**, ripple/dc-bias della ferrite, eventuale risonanza tra FB6201 e COUT/MLCC, TDK land, attenuazione a frequenza reale, voltage drop termico worst-case, 5V al limite basso per i LDO, ground-return, eFuse vs buck e funzione di shutdown/eFuse HOLD. L'interfaccia AUX→MCU e le 15 crossmodule sono ancora **OPEN/HOLD**: il matching label `5V_RF_PREREGULATED` non collega nulla sul root. Per una futura ECO reale dell'interfaccia servono specifica dei ritorni, carichi, compatibilità 5V tra moduli e test KiCad9 prima-dopo.

Nessuna PCB completa, nessun DRC globale, firmware RESET/ALDO, SG48 e Y1 TCXO pin10 HOLD. **NO FAB / NO GERBER / NO PCBWAY / NO TX**. Avanzamento globale storico ~10% senza incremento per questa ECO MPN. 
