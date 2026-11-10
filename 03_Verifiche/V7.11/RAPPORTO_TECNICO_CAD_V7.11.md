# SUPERSTAR 3900 SMD EVOLUTION — RAPPORTO TECNICO CAD V7.11

**10 novembre 2026 — Prima correzione native KiCad del PCB RX coupon, nessun FAB/TX.** Base V7.10, progetto gerarchico RX/POWER/MCU preservato, firmware e DSP conservati. La V7.11 non è un PCB integrato della radio, né risolve il progetto elettrico completo. La sua utilità è una modifica reale, reversibile, verificata mediante un **confronto DRC nativo KiCad 9**.

## 1. Sorgente CAD modificato

**Originale inalterato:** `04_KiCad/Modulo_RX_Test_50ohm_V5.2_PARITY_LINK_STUDY_NOT_FOR_FAB/S3900E_RX_TEST_50R_V5_2_LINKED_STUDY_NOT_FOR_FAB.kicad_pcb`.

**Nuova copia:** `04_KiCad/Modulo_RX_Test_50ohm_V7.11_DRC_REPAIR_NOT_FOR_FAB/S3900E_RX_TEST_50R_V7_11_DRILL_LIBRARY_REPAIR_NOT_FOR_FAB.kicad_pcb`.

Sei vie `GND_RF` nelle posizioni (67,640;32,500), (68,360;32,500), (67,640;33,650), (68,360;33,650), (67,640;34,800), (68,360;34,800) mm hanno foro **0,25→0,30 mm**, diametro rame **0,55→0,60 mm**, mantenendo un anello nominale **0,15 mm**. Sono invariati numero 70 vias, 15 footprints, nets e riferimenti. Non è stata instradata alcuna nuova pista. I file `.kicad_pcb` sono sorgenti nativi editabili, non immagini.

È stato creato anche `fp-lib-table` nella directory nuova, con riferimenti relativi alle tre librerie footprint preesistenti. **La prova nativa ha continuato a segnalare 15 warning `lib_footprint_issues`**: il solo file tabella non li risolve. SMA footprint e termica LNA richiedono qualificazione vendor e lavoro CAD ulteriore.

## 2. Audit DRC comparativo veramente eseguito

Workflow `.github/workflows/v711_rx_coupon_native_drc.yml`, GitHub Actions **[run 42856926563](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42856926563)** job **129972377360**, conclusione **success**, log controllato. Installa KiCad nativo, esegue `kicad-cli pcb drc` su vecchia e nuova versione e confronta i loro report `.rpt`, scaricabili come artifact `v711-original-vs-fixed-native-kicad-drc-NO-FAB`.

| Categoria KiCad | RX V5.2 originale | RX V7.11 copia | Interpretazione |
|---|---:|---:|---|
| Violazioni DRC generali | **91** | **85** | Diminuzione di 6, DRC totale ancora NON PASS |
| `drill_out_of_range` | **6** | **0** | **Correzione verificata** su tutte le sei via |
| `via_dangling` | 70 | 70 | **Ancora da correggere**; non rimuovere alla cieca le vias GND |
| `lib_footprint_issues` | 15 | 15 | **Ancora aperti** nonostante `fp-lib-table` |
| `unconnected_items` | 63 | 63 | **Ancora aperti**; KiCad riporta gli unconnected separatamente dalle 85 violazioni |

Lo script `03_Verifiche/V7.11/confronta_drc_rx_v711.py` rifiuta regressioni sul conteggio DRC, esige 6→0 via under-drilled e conserva 63 unconnected nel rapporto. Non sopprime categorie o cambia soglie DRC. Il gate **PASS** prova soltanto un miglioramento, non un PCB completato.

## 3. Regressioni di elettronica digitale, RF matematica e firmware

La V7.11 preserva tutte le revisioni V7.1–V7.10 e ripete:
- **8** test statici del file KiCad copiato e delle sei modifiche,
- **12** test V7.10 integrazione gerarchica,
- **143** test Python DSP/PLL/firmware/safety V7.1–V7.9,

per un totale di **163 Python PASS, 0 FAIL e 0 SKIP**, log GitHub Actions verificato.

**NON** sono stati rieseguiti il testbench Icarus o la sintesi Yosys nel nuovo workflow: i loro PASS delle revisioni precedenti rimangono storici e non vengono attribuiti a questo controllo.

## 4. Blocchi progettuali ancora aperti

Il primo root KiCad V7.10 continua a essere un **indice gerarchico senza connessioni elettriche tra i tre moduli**. Audit V7.10 segnala **132 istanze /11 refs duplicati, 99 nets, 43 errori ERC+416 warning**; schema RX V5.2 standalone fallisce `kicad-cli sch erc` exit3. Nel PCB RX V7.11: 70 via dangling, 15 warning library, 63 unconnected. Restano **15 contratti inter-modulo OPEN/HOLD**, footprint SMA/PA termici e Pinout iCE40 SG48 **HOLD**, interfaccia alimentazione/MCU/PLL e IF2 incomplete. Le nuove vie da 0,30 mm non certificano via-in-pad di processo; manca verifica della pasta e del fornitore.

**NON ESEGUITI:** schema radio completo elettricamente collegato, DRC/ ERC senza errori, board finale, garanzie RF o EMC, collaudi hardware, Gerber, assemblaggio e TX. Tutte le protezioni TX, DAC, FPGA e PA rimangono DNP/unpowered/unrouted. **NO FAB / NO TX**.

## 5. Prossima V7.12

Riparare il caricamento standalone dello schematic RX V5.2 su copia KiCad verificata, sanare designatori duplicati della gerarchia, auditare footprint e massa GND con return currents, risolvere le connessioni RX realmente necessarie prima di sbrogliare, integrare gradualmente connessioni qualificate power/MCU/RX e rieseguire DRC/ERC. Continuare in parallelo firmware/DSP e test automatici. Non produrre una PCB finché i gate CAD ed elettrici non sono superati.

**Decisione:** merge V7.11 autorizzabile **soltanto come miglioramento CAD documentato e verificato**, non come release circuito.
