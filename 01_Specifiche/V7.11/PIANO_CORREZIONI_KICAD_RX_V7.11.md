# V7.11 — Piano di correzione CAD nativa RX 50 Ω

**10 novembre 2026 — NO FAB / NO TX.** Proseguimento della V7.10 già presente su main. Non sostituisce né abilita i precedenti simulatori DSP, firmware, PLL, TX o la scheda completa.

## Lavoro CAD eseguito

La scheda KiCad **RX coupon** V5.2 resta immutata e ha una copia V7.11 realmente modificata:
`04_KiCad/Modulo_RX_Test_50ohm_V7.11_DRC_REPAIR_NOT_FOR_FAB/S3900E_RX_TEST_50R_V7_11_DRILL_LIBRARY_REPAIR_NOT_FOR_FAB.kicad_pcb`.

Sono state riparate sei vie GND_RF via-in-pad nei punti (67.640,32.500), (68.360,32.500), (67.640,33.650), (68.360,33.650), (67.640,34.800), (68.360,34.800) mm. Diametro foro: **0,25→0,30 mm**. Diametro rame: **0,55→0,60 mm** per mantenere anello geometrico 0,15 mm; permane qualifica produttore per via-in-pad, termica e solder paste. Nets e componenti **immutati**, nessuna pista RF o TX aggiunta.

È presente `fp-lib-table` con i tre nomi di libreria preesistenti e path relativi al modulo V5.2; **il DRC nativo continua a rilevare 15 warning lib_footprint_issues**. Questa è una diagnosi, non una correzione completata del problema delle librerie. Non disabilitare/sopprimere gli avvisi.

## Verifica KiCad 9 nativa — reale, comparativa

Il workflow `.github/workflows/v711_rx_coupon_native_drc.yml` esegue davvero `kicad-cli pcb drc` su entrambe le schede versionate e pubblica i due report originali. Run [42856926563](https://github.com/jd3485/Superstar3900-SMD-Evolution/actions/runs/42856926563), job 129972377360, log ispezionato:

| Rilievo | RX V5.2 originale | RX V7.11 copia |
|---|---:|---:|
| Total DRC violations | 91 | **85** |
| drill_out_of_range | 6 | **0** |
| via_dangling | 70 | **70** |
| lib_footprint_issues | 15 | **15** |
| unconnected_items (conteggio a parte) | 63 | **63** |

Il report `03_Verifiche/V7.11/confronta_drc_rx_v711.py` impone riduzione DRC, zero drill errors e nessun aumento degli unconnected. I report sono nell'artifact `v711-original-vs-fixed-native-kicad-drc-NO-FAB` del run. **Verifica DRC complessiva: FAIL / non conforme**; soltanto il *gate di miglioramento* è PASS.

**Regressioni:** 8 test Python V7.11 + 12 test statici V7.10 + 143 test firmware/DSP/sicurezza V7.1–V7.9 = **163 PASS / 0 FAIL / 0 SKIP**. Non sono state ripetute compilazioni Icarus/Yosys nella CI V7.11; restano registrate nello storico, non sono prove nuove.

## Priorità CAD prossime

1. Correggere su copia verificata lo schema RX V5.2 standalone che oggi non si carica in `kicad-cli sch erc` (exit 3). Prima identificare causa e verificare con KiCad CLI.
2. Gestire la **portabilità reale dei tre footprint**: anche con `fp-lib-table` versione V7.11 persiste 15 warning, quindi verificare i nomi e le loro impronte non approvate, non nascondere i messaggi.
3. Ridurre **70 via_dangling** solo con piani di massa e ritorni effettivamente analizzati; le **63 unconnected** richiedono revisione pad/net/PCB e non un'autorizzazione a instradare alla cieca.
4. Correggere i **11 designatori riutilizzati (14 istanze extra)** tra i 132 elementi dello schema gerarchico RX/power/MCU V7.10 usando una copia versionata e netlist KiCad reale.
5. Rieseguire ERC root V7.10 (43 errori +416 warning), poi collegare solo interfacce con rail, pin e polarità verificati. Tutti i 15 contratti cross-module restano **OPEN/HOLD**.
6. In parallelo proseguono test DSP/firmware, revisione componenti e modelli RF. Pinout FPGA SG48 HOLD. Nessuna connessione PA/antenna o TX.

**Non eseguiti:** circuito e PCB completo della radio, ERC/DRC senza errori, validazione footprint SMA/LNA, test elettrici, KiCad schemi interconnessi, prototipazione e trasmissione. **NO FAB / NO TX.**
