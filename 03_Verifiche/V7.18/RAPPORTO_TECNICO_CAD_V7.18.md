# Superstar 3900 SMD Evolution — Rapporto tecnico V7.18: eFuse ERC ed esperimenti sul filtro PLL

**11 novembre 2026 — revisione di SCHEMA dell'intera radio, non di PCB. NO FAB / NO TX.**

## 1. Sorgente, oggetto e limiti

Dal master nativo V7.17 a 7 fogli è stata creata una **copia V7.18**, senza sovrascrivere lo storico:
- `04_KiCad/Gerarchico_Alimentazioni_V7.18_PINMODEL_NOT_FOR_FAB/`: modulo AUX e tre figli. Tutti i file originali restano byte-identici; **una sola modifica** nel simbolo embedded `S3900E:TPS26600_PWP` del foglio `01_EFUSE_AUX.kicad_sch`.
- `04_KiCad/Assemblaggio_RX_Power_V7.18_POWER_PINMODEL_NOT_FOR_FAB/`: master gerarchico a 7 pagine che punta alla nuova copia AUX, preservando MCU/RX V7.17 e le loro connessioni.

L'ECO **NON** crea PCB dell'intera radio, cablaggio moduli, Gerber o interfacce. Il TX è ancora HOLD.

## 2. Correzione supportata dal datasheet Texas Instruments

**Fonte ufficiale:** [TI TPS2660x, datasheet SLVSDG2G rev. G](https://www.ti.com/lit/ds/symlink/tps2660.pdf), tabella «Pin Functions» p.5. I due pin **OUT15** e **OUT16** del TPS26600 package HTSSOP-16 sono **entrambi terminali dell'unica uscita di potenza** dell'eFuse. Nello schema storico sono collegati insieme alla stessa rete `BUCK_VIN_PROTECTED`. KiCad 9 segnalava `[pin_to_pin] Pins of type Power output and Power output are connected`: non è un corto tra due dispositivi differenti.

ECO **solo sul tipo elettrico per ERC**, nel simbolo incorporato:
- OUT15 = `power_out` (invariato, un output qualificante presente);
- OUT16 = `passive` (prima `power_out`). **NON è un cambiamento della funzione fisica**: nella realtà il pin16 resta un'uscita del componente e deve essere collegato al pin15/nodo di uscita secondo la raccomandazione del vendor.

Nessun cambiamento di coordinate, valore, MPN, footprint, numero pad, filo, net, copper o protezione. Il protocollo di audit blocca qualsiasi modifica al di fuori del cambio tipologico esatto. Dettaglio nell'[ECO V7.18](../../01_Specifiche/V7.18/ECO_EFUSE_DUAL_OUT_PINMODEL_V7_18.md).

## 3. Verifica con vero KiCad 9

Il workflow `.github/workflows/v718_efuse_pll_native.yml` (CI confermata [run 42964160297](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42964160297) **success**) esegue un **export di netlist KiCad** e un **ERC KiCad nativo** sia sul master V7.17 sia sul master V7.18, senza filtri di warning.

| Controllo | V7.17 | V7.18 |
|---|---:|---:|
| Errori ERC intera gerarchia | **43** | **42** |
| Warning ERC intera gerarchia | **340** | **340** |
| Violazioni `pin_to_pin` | 1 | **0** |
| Net della radio nella gerarchia | 99 | **99** |
| Stesse coppie *(nome rete, riferimento, pin)* | — | **SÌ, tutte** |
| Nuove interfacce fisiche RX/MCU/AUX | 0 | 0 |
| Interfacce OPEN/HOLD | 15 | 15 |

**Il solo errore rimosso è `pin_to_pin`**. Rimangono **26 `label_dangling` +16 errori elettrici/fili** (6 `power_pin_not_driven`, 5 `pin_not_driven`, 3 `wire_dangling`, 2 `pin_not_connected`), e 340 warning. Nel RX isolato la baseline ERC è 0/0, ma lo schema radio non è completo.

**12 test nuovi V7.18 +241 regressioni V7.1–V7.17 =253 Python PASS, 0 FAIL/0 SKIP** in CI. Non ci sono nuove sintesi Icarus/Yosys, simulazioni RF o collaudi reali.

## 4. Filtro di anello PLL R2/R3: quattro prove reali, nessun falso avanzamento

Dai report nativi V7.17 risultano:
- U1 LMX2572RHA pin 12 **CPOUT** e pin 35 **VTUNE**;
- R2 620Ω pin1 a (84,92;157,00 mm); R3 22Ω pin1 a (134,92;146,05 mm), entrambi riportati `pin_not_connected`;
- tre `wire_dangling` in corrispondenza del filtro; la netlist nativa non associa ancora a R2/R3 una rete reale.

Il [datasheet TI LMX2572 SNAS740B, p.4](https://www.ti.com/lit/ds/symlink/lmx2572.pdf) conferma che CPOUT è pin12 e VTUNE pin35, e che i pin SYNC(5), SysRefReq(28), RampClk(30), RampDir(32) sono ingressi con funzioni distinte. Nessun PIN è stato forzato a GND o 3V3 per ottenere un report verde.

`03_Verifiche/V7.18/probe_pll_loop_native_v718.py` esegue quattro esperimenti veri, **sempre su copie effimere dell'intero progetto KiCad**, preservando la schematica V7.18:

| Esperimento (NON APPROVATO PER PCB) | ERC errori | ERC warning | Differenze nei nodi ref/pin |
|---|---:|---:|---:|
| PLL originale V7.18 | 42 | 340 | 0 |
| R2: deviazione del filo dal corpo simbolo | 42 | **341** | 0 |
| R3: sola rotazione 180° del simbolo resistivo | 42 | 340 | 0 |
| R2 deviazione + R3 180° | 42 | **341** | 0 |

**Interpretazione:** nessun candidato ripara elettricamente il filtro, due peggiorano un warning. Tutti i cloni sono eliminati; i report `v718.*.root.erc.rpt` e `v718.pll_loop_candidates_native.json` conservano l'evidenza. **Nessuna variante è stata trasferita nel progetto V7.18.** Servono topologia esatta, geometria dei pin, confronto alla scheda TI e revisione KiCad GUI della connessione. Non aggiungere fili a caso.

## 5. Errori residui e prossime priorità

| Blocco aperto | Causa nota | Prossimo gate |
|---|---|---|
| eFuse U200 IN e RTN | `power_pin_not_driven` (2) | Qualificare sorgente 13,8 V, ritorni separati RTN / GND_MAIN |
| PLL LDO U2 IN e GND | `power_pin_not_driven` (2) | Origine reale 5 V e piano GND; non creare `PWR_FLAG` di comodo |
| MCU U6203 IN e GND | `power_pin_not_driven` (2) | Alimentazione 5V digitale filtrata, ritorni e protezione codec |
| LMX U1 pin SYNC / SysRefReq / RampClk / RampDir / VTUNE | `pin_not_driven` (5) | Specifiche TI, uso PLL normale vs ramp/SYSREF, feedback analogico |
| R2/R3 e filo loop filter | `pin_not_connected` (2), `wire_dangling` (3) | Ricostruire topologia dalla specifica TI, pin-to-net e verifica GUI |
| Etichette aperte | `label_dangling` (26) | Risolvere SOLO quando gli stadi/pin esterni sono qualificati |

Altre condizioni non risolte: **15 contratti OPEN/HOLD**, rail `5V_RF_PREREGULATED` ≠ `+5V_BENCH` ≠ `3V3_CODEC_IO`, ritorno `GND_MAIN` vs `GND_RF`, stadio `RX_IF_STAGE` assente, SG48 HOLD, connettori SMA lato destro a 180° con 2 mismatch, PCB unica non presente.

La stima PCB completa rimane **~10%**; eliminare un falso positivo ERC, pur costituendo una correzione reale di CAD, **non conta come routing o produzione**. Prossima V7.19: revisione grafica dei pin R2/R3, ricostruzione e qualifica del loop filter, poi analisi power driver e alimentazioni.

**NO FAB / NO TX / NO GERBER / NO PCBWAY.**
