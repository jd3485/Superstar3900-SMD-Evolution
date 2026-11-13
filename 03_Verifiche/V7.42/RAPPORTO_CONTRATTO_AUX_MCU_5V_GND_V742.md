# V7.42 — Contratto d'interfaccia AUX_POWER ↔ MCU_CODEC: budget 5 V e ritorno di massa (HOLD)

**Data:** 13 novembre 2026. **Baseline:** V7.41 integrata su main, [PR #44](https://github.com/jd3485/Superstar3900-SMD-Evolution/pull/44). Questa revisione è un **gate d'integrazione elettrica e di documentazione**, non introduce un ponte di alimentazione o un ritorno di massa arbitrario, né altera schemi, netlist, BOM e footprint. Stato macchina in `03_Verifiche/V7.42/CONTRATTO_INTERFACCIA_AUX_MCU_POWER_V742.json`.

## Catena di alimentazione — ciò che è effettivamente nel CAD

| Sezione | Componente e rete | Livello di evidenza |
|---|---|---|
| AUX esterna | `PWR_13V8_AUX_RAW`, fusibile **F200** da 1.5 A candidato, eFuse **U200 TPS26600PWPT** → `BUCK_VIN_PROTECTED` | Presente nel sottosistema AUX, con pin gerarchici interni |
| Buck | **U100 TPS54202DDCR**, uscite `5V_RF_PREREGULATED`, condensatori di uscita **C103+C104 = 44 µF nominali** | Presente nel modulo `02_BUCK_5V`, compatibilità full-board non dimostrata |
| Ingresso MCU/CODEC | `5V_RF_PREREGULATED` → **FB6201 pin 1**, **FB6201 pin 2** → `5V_DIGITAL_FILTERED` | Collegamento solo all'interno del foglio MCU, etichette locali |
| Ritorno | `GND_MAIN` in AUX, `GND` nel modulo MCU/CODEC | Connessione, stella/piano, corrente di fault e impedenza comune ancora **OPEN/HOLD** |
| Master a 7 fogli | Sheet AUX, MCU_CODEC e RX coupon | Tre sheet **senza pin gerarchici inter-modulo** nel root; nessuna unione fisica autorizzata |

**Attenzione:** la stringa identica `5V_RF_PREREGULATED` in due fogli NON significa una rete comune in KiCad; il master si definisce esplicitamente `REUSE INDEX ONLY`. Il sottosistema AUX possiede pin gerarchici **interni** per eFuse, buck e PLL: non confondere questa gerarchia locale con l'integrazione top-level. Non collegare `GND_MAIN` e `GND` con un simbolo globale soltanto per silenziare ERC.

## Verifica degli assorbimenti — limite condiviso, non somma di consumi

Nel codice attuale esistono **sei TPS7A2033PDBVR da 3.3 V nominali** che verrebbero alimentati dal ramo buck se l'interfaccia fosse approvata:

| Dominio | Regolatori identificati | Corrente nominale massima erogabile da ciascuno |
|---|---|---|
| MCU_CODEC | U6203, U6204, U6205, U6206 | 300 mA per canale |
| AUX_PLL | U2, U3 | 300 mA per canale |
| **Somma delle targhe** | **6 canali** | **1.8 A** |

Il **TPS54202** è un buck 2 A continui, **condivisi da tutta la linea a 5 V**, non una riserva da 2 A per ciascun modulo. Fonte Texas Instruments, [TPS54202 product data](https://www.ti.com/product/TPS54202), specifica 2 A continuous; il modello non dimostra la potenza di uscita a ogni temperatura/layout e ingresso. L'ipotetico caso **6×0.3 A = 1.8 A** lascia soltanto **0.2 A** *sulla carta* per le altre utenze: NON è il consumo misurato, non considera correnti a vuoto, correnti di spunto, perdite e DC-biased passives. Non dichiarare che `I_5V <=2 A` solo perché i sei canali sommano 1.8 A: potrebbero esserci altri carichi e una nuova PCB dissiperebbe ulteriori potenze. Allo stesso modo **il fusibile F200 da 1.5 A è sulla linea di ingresso**, non è un limite di 1.5 A direttamente sull'uscita regolata a 5 V (l'effetto dipende dalla conversione di potenza, perdite e tensione d'ingresso).

**FB6201**: ferrite TDK `MPZ2012S601ATD25`, rating DC 2 A, DCR max 0.1 Ω e Znom=600 Ω a 100 MHz secondo [scheda TDK](https://product.tdk.com/en/search/emc/emc/beads/info?part_no=MPZ2012S601ATD25). Non confondere i 600 Ω a 100 MHz con la caduta ohmica continua. A corrente ipotizzata di 1.8 A, `I×0.1 Ω=180 mV` e `I²×0.1 Ω=324 mW` come screening resistivo, **non** margine termico/stabilità provato. La ferrite è già assegnata a un vendor land 0805 di revisione in V7.41.

## Capitolo capacitivo e start-up

- Buck locale: `C103=C104=22 µF` nominali sull'uscita 5 V, totale **44 µF**, valori non equivalenti a Ceff reale a 5 V.
- MCU dietro FB6201: `5V_DIGITAL_FILTERED` ha **14.1 µF** locali nominali, verificati V7.39; i due gruppi non possono essere sommati automaticamente come uscita direttamente caricata da 58.1 µF perché la ferrite, la sua DCR/impedenza e le altre utenze cambiano la dinamica di avviamento.
- Il buck TPS54202 ha un **soft-start tipico di 5 ms**, ma non è un transitorio completo del nostro progetto. Sono da simulare ripple e inerzia del buck con impedenza della ferrite, carichi e capacity derating, spike di corrente, reverse-current dei LDO e prebias.

## Contratto proposto ma NON ancora approvato

**Intento di collegamento**: `AUX_POWER.5V_RF_PREREGULATED` → `MCU_CODEC.FB6201.1` → `FB6201.2 / 5V_DIGITAL_FILTERED`, con architettura di ritorno `AUX.GND_MAIN` ↔ `MCU_CODEC.GND` **da progettare**. I due legami in `CONTRATTO_INTERFACCIA_AUX_MCU_POWER_V742.json` riportano `approved:false`. Il JSON stabilisce inoltre i vincoli fail-closed `physical_crossmodule_net_exists:false`, `power_budget_signed_off:false`, `ground_return_signed_off:false`, `NO_FAB:true`, `NO_GERBER:true`, `NO_TX:true`.

**Richiesto prima di un'eventuale ECO top-level:**
1. Tracciare il percorso preciso di corrente di U200/U100 (UVLO/OVP, limitazione/temperatura, F200, protezioni e polarità dei ritorni) e budget massimo/nominale di ogni ramo 5 V.
2. Definire `GND_MAIN` e `GND`: connessione fisica, ritorni di segnale/driver, loop RF/audio, corrente di guasto e comune impedenza, evitando collegamenti RF accidentali.
3. Validare assorbimento MCU, ADC/DAC codec, PLL/TCXO, ingressi accessori, LDO e altre utenze con budget DC, dinamico e inrush. Non usare direttamente il rating del singolo LDO come assorbimento effettivo.
4. Valutare modellazione transitoria buck–ferrite–capacità, ripple e regolazione a fine rail; prove reverse-current `VOUT <= VIN +0.3V` e **15 mA per breve periodo** sui TPS7A20, più Ceff e sequenza RESET/ALDO.
5. Soltanto a evidenza sufficiente, introdurre pin gerarchici espliciti in una nuova copia di master/moduli e confrontare **native KiCad9** netlist ed ERC prima/dopo, senza sopprimere errori. Tenere tutte le altre interfacce in HOLD.

## Gate di regressione

Il codice `03_Verifiche/V7.42/test_aux_mcu_power_interface_contract_v742.py` (16 test) confronta il JSON con sorgenti reali di root, AUX e MCU, corrispondenza U100/U200/F200, sei LDO, pin e MPN ferrite, rail buck, 44 µF nominali, il limite 2 A e gli stati NO FAB. **Non è una simulazione SPICE, non dimostra la continuità del 5 V, e non cambia il CAD.** Per questa sola revisione non si richiede ripetere KiCad9: il codice legge la sorgente già validata. Esito CI da registrare soltanto dopo run reale.

**Stato invariato:** 134 componenti / 101 reti / 32 footprint mancanti / ERC 36 errori +221 warning (baseline CAD V7.41). 15 interfacce cross-module OPEN/HOLD, SG48 HOLD, Y1 pin10 AFC/GND HOLD, PCB unica non completata, nessuna DRC globale, **NO FAB / NO GERBER / NO PCBWAY / NO TX**. Stima PCB storica ~10%, non aumentare per un contratto di interfaccia.
