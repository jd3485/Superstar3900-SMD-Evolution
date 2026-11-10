# KiCad V7.12 — RX / MCU / AUX POWER, reannotated source hierarchy

Open `S3900E_RX_POWER_INTEGRATION_V7_12_REANNOTATED_NOT_FOR_FAB.kicad_sch` with **KiCad 9**. This is an editable native KiCad schematic containing seven hierarchical sheets. Linked source folders:
- `../Gerarchico_Alimentazioni_V1.5` original power and 3 subpages, unchanged;
- `../Modulo_MCU_CODEC_V7.12_REANNOTATED_NOT_FOR_FAB`, 46 symbols uniquely renamed into ref range 6xxx;
- `../Modulo_RX_Test_50ohm_V7.12_SCHEMATIC_REPAIR_NOT_FOR_FAB`, 15 RX symbols uniquely renamed into range 9xxx, with a matching separately versioned coupon `.kicad_pcb`.

Two genuine KiCad 9 exported netlists prove **11→0 duplicate component references** while preserving **7 sheets /132 components /99 nets**. These are *not* electrically connected cross-module: the 15-interface manifest from V7.10 remains **OPEN/HOLD**. The PCB is only a 50Ω RX experiment board, **not** the complete radio PCB. Reference renumbering does not fix ERC root (43 errors/416 warnings) or DRC of the RX coupon (85 violations plus 63 unconnected).

Report: `../../Superstar3900_Rapporto_Tecnico_V7.12.md`.
Verify: `.github/workflows/v712_kicad_native_annotation.yml` from project root.

**NO FAB / NO TX. Do not order PCB, generate Gerbers or power RF TX hardware.**
