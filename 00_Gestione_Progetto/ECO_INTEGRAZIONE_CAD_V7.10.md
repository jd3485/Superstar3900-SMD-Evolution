# ECO V7.10 — DA SIMULAZIONI A KiCad NATIVO RX/POWER/MCU

**10 novembre 2026. NO FAB / NO TX.**

## Modifiche effettive
1. Introdotto **nuovo schema gerarchico KiCad .kicad_sch** `04_KiCad/Assemblaggio_RX_Power_V7.10_NOT_FOR_FAB/S3900E_RX_POWER_INTEGRATION_V7_10_NOT_FOR_FAB.kicad_sch`, referenzia senza modificare gli schemi esistenti AUX power V1.5 (3 sottopagine), MCU+codec V2.1 e RX 50Ω V5.2. Output KiCad reale: **7 fogli**; nessuna rete nuova tra moduli, nessuna uscita TX.
2. Nuovo contratto `MATRICE_INTERFACCE_DA_QUALIFICARE_V7_10.csv`: **15 interfacce OPEN/HOLD**, impedisce di fondere `5V_RF_PREREGULATED` con `+5V_BENCH` senza verifica e non inventa pin MCU/PLL o RF.
3. Avviata **verifica nativa KiCad CLI 9.0.8** via GitHub Actions, prima mai eseguita sui draft RX V5.2. Genera vera netlist `integration.net`, ERC su root e power/MCU, DRC sul PCB coupon RX V5.2, report/summary non filtrati e scaricabili. Non esporta Gerber, drill, posizioni assembly.
4. Evidenza: **7 fogli, 132 istanze componenti, 99 reti e 11 designatori duplicati** tra fogli (14 duplicazioni eccedenti), warning di annotazione KiCad.
5. ERC nativo nuovo root: **459 segnalazioni (43 errori + 416 avvisi)**. Alimentazioni V1.5: **270 (22 errori/248 avvisi)**, MCU V2.1: **110 (18/92)**. RX V5.2 come root autonomo: `kicad-cli sch erc` exit 3 `Failed to load schematic` (ER C non eseguito standalone); come child è presente nella gerarchia esportata.
6. DRC coupon PCB RX V5.2: **91 violazioni** e **63 unconnected**, fra cui 6 via drill Ø0,25mm vs min Ø0,30, 70 avvisi via dangling e 15 avvisi librerie footprint. Non si modificano valori DRC o pad senza revisione meccanica/termica.
7. Una proposta versionata di aggiungere `sheet_instances` all'RX V5.2 per risolvere l'errore di caricamento è stata **testata e non ha funzionato**, quindi è stata eliminata dal branch; non si falsifica un PASS. L'originale resta preservato. Audit report individua il difetto.
8. Test statici 12 V7.10 più tutte le regressioni Python V7.1–V7.9 **143 PASS** sul branch. Firmware/RTL e modelli non abbandonati e non modificati; continuare a verificarli in parallelo all'EDA.

## Nuovo criterio di avanzamento
La CI può essere verde se i comandi KiCad di **AUDIT** hanno realmente prodotto i rapporti e i 43/91 problemi sono documentati. Ciò NON equivale a ERC/DRC GREEN per la fabbricazione: i campi `erc_drc_zero_violations` e `manufacturing_release` restano **FALSE**.

**Prossima V7.11**: riparare il caricamento RX standalone su nuova copia realmente validata; annotare in modo univoco tutti i 132 componenti; risolvere errori ERC/DRC del coupon RX cominciando da reti aperte e librerie; validare SPI e rail Power↔MCU↔RX, poi realizzare connessioni sullo schema KiCad integrato. Solo con netlist elettrica approvata iniziare un PCB unico. Non toccare hardware TX, PTT, PA o antenna.

**NO FAB / NO TX** invariabile e tag `v7.0` preservato.
