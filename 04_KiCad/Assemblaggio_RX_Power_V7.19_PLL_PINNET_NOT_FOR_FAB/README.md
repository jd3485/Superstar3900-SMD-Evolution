# V7.19 — KiCad schematico di integrazione radio con filtro PLL a pin-net verificabili

**NO FAB / NO TX / NO GERBER.** Questo è il nuovo master elettrico a sette fogli per la radio, **non** un PCB completo.

Aprire `S3900E_RX_POWER_V7_14_LIB_NOT_FOR_FAB.kicad_pro` con KiCad 9 nella cartella V7.19. Il nome base `V7_14` è intenzionalmente mantenuto per preservare gli UUID e i riferimenti di progetto dei sette fogli preesistenti; la directory, titolo e rapporto di avanzamento sono **V7.19**.

## Correzione rispetto a V7.18

Il solo ramo AUX punta a `../Gerarchico_Alimentazioni_V7.19_PLL_PINNET_NOT_FOR_FAB/S3900E_AUX_POWER_V1_5.kicad_sch`; i fogli MCU e RX restano quelli già ereditati da V7.18. Il nuovo PLL contiene esattamente **sei nuove etichette** aggiunte ai terminali **R2:1, R3:1, R3:2, R2:2, C2:2, C3:2**. Il contratto [TI LMX2572 Figure 179](../../01_Specifiche/V7.19/PIANO_PINNET_LOOP_PLL_TI_V7_19.md) richiede tre nodi: `PLL_CPOUT` (U1:12, R2:1, R3:1, C1:2), `PLL_R2_C2` (R2:2, C2:2), `PLL_VTUNE` (R3:2, U1:35, C3:2); il ritorno dei condensatori resta `GND_MAIN` e va successivamente qualificato come VCO ground.

Non sono stati aggiunti fili, pin gerarchici, layer, stadi TX, alimentazioni o connessioni RX–MCU. Non sono stati modificati i valori R2 620 Ω, R3 22 Ω, C1 220 pF, C2 120 nF, C3 2,2 nF: **tutti ancora provvisori e non approvati per stabilità/rumore/fabbricazione**.

## Prova

Il workflow `.github/workflows/v719_pll_pin_native.yml` obbliga ad eseguire `kicad-cli sch export netlist` + `kicad-cli sch erc` su V7.18 e V7.19. La pipeline deve dimostrare **42→36 errori ERC**, **340 warning invariati**, **99→100 reti native** (unica nuova rete `PLL_R2_C2`), le 12 appartenenze pin/rete del filtro esatte, e **nessun altro ref/pin alterato**. Si conservano i report completi, senza modificare o nascondere severità.

La matrice mantiene tutte le **15 interfacce OPEN/HOLD** e **TX = 0**. Stadio RX_IF non progettato, rail 5V/3V3/GND non qualificate, output SMA lato destro a 180° da certificare, PCB unica assente. La percentuale della PCB completa resta **~10%** nonostante l'avanzamento di schematico.

**NO FAB / NO TX.**
