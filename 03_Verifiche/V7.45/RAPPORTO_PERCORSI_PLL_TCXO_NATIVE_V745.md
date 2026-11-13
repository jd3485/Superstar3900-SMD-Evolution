# V7.45 — Mappa dei veri percorsi di alimentazione PLL LMX2572 e TCXO Y1

**Data:** 13 novembre 2026. Baseline elettrica V7.41 integrata, V7.44 consumi vendor integrata tramite PR#47, ottimizzazione Actions PR#48 integrata. Revisione V7.45 **di connettività verificata mediante KiCad9 nativo**, senza ECO circuitale. 15 interfacce AUX↔MCU/RX ancora HOLD.

## Problema ingegneristico e topologia reale

Il LDO U2 ha come uscita `3V3_PLL_INPUT_FROM_LDO`; sarebbe sbagliato analizzare il carico guardando esclusivamente i componenti direttamente etichettati su questa rete, perché **LMX2572 U1 è alimentato attraverso sei resistori R10–R15 da zero ohm**. I resistori creano sei reti distinte dal nome, ma non sei consumi totali aggiuntivi: i numeri di corrente vendor LMX2572 si applicano all'intero IC in una configurazione determinata e comprendono l'assorbimento interno fra i domini.

| Dal regolatore U2.5 attraverso | Destinazione rete PLL | Pin del sintetizzatore U1 |
|---|---|---|
| R10, 0Ω, pin2→pin1 | `PLL_VCCDIG` | U1 pin7 |
| R11, 0Ω | `PLL_VCCCP` | U1 pin11 |
| R12, 0Ω | `PLL_VCCMASH` | U1 pin15 |
| R13, 0Ω | `PLL_VCCBUF` | U1 pin21 |
| R14, 0Ω | `PLL_VCCVCO2` | U1 pin26 |
| R15, 0Ω | `PLL_VCCVCO` | U1 pin37 |

Tutti i resistori e i nodi sono verificati **sulla netlist gerarchica KiCad9**, non dedotti dalla geometria o dalle etichette visibili. LMX2572 MPN `LMX2572RHA`. Dati TI SNAS740B §6.5: 75/79/82/86mA tipici per quattro configurazioni PLL (a 25°C); non usare 86mA come massimo termico, né moltiplicarlo per sei reti di alimentazione. `U2.1` è **già** sulla rete 5V secondo prova V7.43 e non necessita di una falsa ECO.

Il LDO U3 ha `3V3_REF_LDO` in uscita, fisicamente collegato a **Y1 pin9 VCC**, ai condensatori e a **R60 pin2**. R60 è **10kΩ ±1%** in pull-up e collega `TCXO_EN` a **Y1 pin8** tramite il suo pin1. Il componente `7N-12.800MBP-T` è un TCXO 12.8MHz, VCC3.3V e supply current max 10mA secondo dati precedenti del distributore sul MPN esatto: https://www.digikey.it/en/products/detail/txc-corporation/7N-12-800MBP-T/5222401 . Lo screening resistivo **R60 minimo9.9kΩ** comporterebbe 3.3V/9.9kΩ≈0.333mA nel solo caso ipotetico in cui il pin8 venisse mantenuto vicino a GND e il resistore vedesse tutta la tensione. **Non** significa che la rail di U3 assorba automaticamente 10.333mA: carichi accessori, corrente reale del pin enable, tolleranze e transienti sono ancora ignoti; 10mA è rating del TCXO alle condizioni di targa, non massimo dell'intero rail.

**Y1 pin10 AFC oppure GND rimane esplicitamente HOLD**: non forzare la scelta della variante, non collegarlo arbitrariamente, verificare dal produttore prima della realizzazione. U2 / U3 ritornano a `GND_MAIN` nel dominio AUX; `U6205` del MCU/CODEC ritorna a `GND` e la gerarchia root a 3 sheet è ancora un indice NON collegato. La somiglianza del nome 5V fra AUX e MCU **non** prova continuità fisica.

## Gate anti-regressione riusato senza nuovo workflow

- Artefatto con matrice MPN, nodi e stati di rischio `03_Verifiche/V7.45/MAPPA_PLL_TCXO_CARICHI_NATIVE_V745.json`.
- Test `03_Verifiche/V7.45/test_pll_tcxo_supply_paths_native_v745.py`: 20 test che leggono `03_Verifiche/V7.43/output-ci/v743.baseline.net` e `v743.baseline.erc.rpt`, entrambi generati da **KiCad9 CLI nativo** prima dei test in un'unica esecuzione, e ricontrollano i valori dei resistori e gli MPN del sorgente. Verificano tutti i 6 percorsi R0, la topologia Y1, MCU/AUX isolamento, ERC storico e fail-closed dei vincoli.
- **Nessun nuovo workflow aggiunto.** La pipeline già esistente `.github/workflows/v743_six_ldo_thermal_budget.yml` estende il trigger anche a `03_Verifiche/V7.45/**` e, dopo la regressione V7.43, lancia i 20 test V7.45 usando la **stessa netlist, lo stesso job e lo stesso export**, senza seconda installazione di KiCad. Si modifica quel workflow, quindi parte anche `actions_policy_quick.yml` per validare la policy; la CI CAD nativa rimane obbligatoria nonostante l'ottimizzazione costi.
- Le altre revisioni CAD restano intatte. Prima di dichiarare un PASS verificare la vera esecuzione GitHub con run ID, totali, ERC e artefatti. **Non eliminare errori ERC noti per ottenere verde.**

## Prossimo vero blocker

La dimostrazione dei percorsi di alimentazione non risolve **il consumo massimo a caldo** di U2/LMX2572 e U3/Y1 con load secondari, né i carichi digitali su `3V3_MCU`, `3V3_AUDIO_CLK`, `3V3_CODEC_IO`, `3V3_CODEC_LDOIN`. Prima di una ECO circuitale: simulazione/part numbers vendor per ogni carico, profilo firmware e clock 170MHz, codec PowerTune, temperature ambiente e θJA reale su PCB, transitori e power-down, ritorni eFuse/buck, eventuale rischio reverse current TPS7A20 e regolazione della ferrite. Nessun bilancio del buck da 2A è approvato.

**Stato CAD baseline invariato:** 134 comp, 101 reti, 32 footprint mancanti, ERC 36 errori/221 avvisi, non PCB unica completata, no DRC globale. Le 15 interfacce crossmodule OPEN/HOLD, SG48 e Y1 pin10 restano HOLD; **NO FAB / NO GERBER / NO PCBWAY / NO TX**. Avanzamento storico PCB ~10%, non aumentare per questa prova.
