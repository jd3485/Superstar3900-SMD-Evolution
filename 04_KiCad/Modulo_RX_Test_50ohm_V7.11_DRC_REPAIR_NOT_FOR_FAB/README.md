# Superstar 3900 SMD Evolution — V7.11 coupon RX KiCad, prima riparazione DRC

**Scopo:** modifica reale di un `.kicad_pcb` esistente su **copia** controllata, non una nuova scheda completa e non una release di fabbricazione. **NO FAB / NO TX.**

File sorgente originale conservato invariato:
`../Modulo_RX_Test_50ohm_V5.2_PARITY_LINK_STUDY_NOT_FOR_FAB/S3900E_RX_TEST_50R_V5_2_LINKED_STUDY_NOT_FOR_FAB.kicad_pcb`.

File nuovo:
`S3900E_RX_TEST_50R_V7_11_DRILL_LIBRARY_REPAIR_NOT_FOR_FAB.kicad_pcb`.

## Modifiche reali

1. **6 vie GND** presso U101, coordinate in mm: (67.640,32.500), (68.360,32.500), (67.640,33.650), (68.360,33.650), (67.640,34.800), (68.360,34.800). Diametro foro **0.25 → 0.30mm** (regola KiCad min 0.30mm); diametro rame **0.55 → 0.60mm** per mantenere anello nominale di 0.15mm. Non è stata approvata alcuna realizzabilità via-in-pad: attenzione a pasta, wicking, solder mask, microvia, produttore e costo. Potrebbero comparire nuove violazioni di clearance, da misurare con DRC nativo.
2. **`fp-lib-table` locale** con riferimenti **relativi** ai tre archivi `S3900E_V38_Review.pretty`, `S3900E_v33.pretty` e `S3900E_v35.pretty` esistenti nel repository. Non modifica né convalida i footprint SMA e SOT-89: serve solo a consentirne la risoluzione e a diagnosticare errori autentici.

Nessuna nuova pista, cambio di net, modifica di un footprint, collegamento di alimentazione, DAC, PLL o TX. Non creare Gerber o drill di produzione. La scheda V7.11 è **solo una variante del coupon RF di prova RX**, non il PCB integrato della radio.

## Verifica oggettiva

Workflow `.github/workflows/v711_rx_coupon_native_drc.yml`: esegue **KiCad CLI vero** sul PCB vecchio e nuovo, pubblica entrambi i file `.rpt`, poi `03_Verifiche/V7.11/confronta_drc_rx_v711.py` esige 6 errori `drill_out_of_range` prima e **zero** dopo. Deve diminuire il totale violazioni senza aumentare le connessioni aperte. I warning footprint / via dangling e gli `unconnected_items` rimangono visibili, non soppressi.

Regressioni: 8 test statici V7.11 +12 V7.10 +143 Python V7.1–V7.9. **Un workflow verde significa miglioramento DRC verificato, non DRC pulito**.

## Lavoro successivo (sequenza vincolante)

- Diagnosticare/caricare lo schema RX V5.2 standalone che oggi fallisce `kicad-cli sch erc` con exit3.
- Correggere **11 designatori duplicati** fra 132 istanze del root V7.10, solo sulle copie versionate con KiCad netlist reale.
- Portare via dangling e 63 unconnected RX a zero **senza inventare piste** e verificando tutti i pad/net del coupon e dei footprint.
- Ridurre ERC root V7.10 (43 errori +416 warning) prima di connettere fisicamente power/MCU/RX; i 15 confini rimangono OPEN/HOLD finché rail, pin e schemi validati.
- Continuare test, modelli IF2/DSP, firmware e report senza far passare loro per verifiche elettriche.

**NO FAB / NO TX**.
