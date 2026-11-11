# V7.26 — Native KiCad symbol library repair without electrical edits — NO FAB / NO TX

11 Nov 2026, input integrated V7.25 132 components /100 nets/ 42 missing footprints, KiCad ERC 36 errors+340 warnings. Source: vendor-unqualified review; physical approval NOT granted.

## Root cause and actual CAD ECO

The root V7.25 `sym-lib-table` points at the RX test-only external S3900E symbol library, which omits AUX and MCU symbols. There are **32 original main embedded symbol definitions** across six hierarchical source sheets; names `S3900E:R` and `S3900E:C` recur in EFUSE, BUCK and PLL but are **not byte-identical**. Pin names/numbers stay 1,2 passive in each, but some pin lengths and graphical dimensions differ; merging blindly would corrupt the library semantic parity.

This revision creates 32 uniquely named real KiCad external S3900E symbols in `04_KiCad/Librerie_Simboli_V7.26_UNIFIED_NOT_FOR_FAB/S3900E.kicad_sym`, precisely from the current embedded definitions, retaining all distinct versions. Only six R/C library identities and their nested unit references are renamed **in versioned copies of three AUX sub-schematics**: `R_EFUSE,C_EFUSE,R_BUCK,C_BUCK,R_PLL,C_PLL`. No pin locations, pin types, wires or labels change. The parent AUX is byte-identical; new root V7.26 points only to new AUX directory and full library via local `sym-lib-table`, keeps the V7.25 MCU, V7.14 RX and exactly the same `fp-lib-table`.

## Required native gate (NOT initially proven)

`kicad-cli sch export netlist` and `sch erc` on original V7.25 root and V7.26 root, compare all 132 components and every node in all 100 nets, 42 missing footprint fields, 36 original ERC errors, at least one fewer `lib_symbol_issues` and fewer than 340 warnings without any ERC waiver; no new/fewer error categories just by hiding pending interfaces. 12 Python tests also verify source-only specific changes and 32 library definitions; CI on `pull_request` only, to minimize paid Actions. No new board, Gerber, TX or DRC fabricated.

**15 cross-domain RX/MCU/AUX interfaces remain OPEN/HOLD. SG48 HOLD.** F200/Y1 still unvalidated, source/return 13.8→5→3.3 and thermal design unresolved, PCB unified absent. No manufacturing claims.
