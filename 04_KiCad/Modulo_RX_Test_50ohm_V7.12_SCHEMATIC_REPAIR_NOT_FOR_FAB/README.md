# KiCad V7.12 — RX coupon standalone repaired and schematic/PCB refs consistent

The two native files are meant for **KiCad 9**:
- `S3900E_RX_STANDALONE_V7_12_NOT_FOR_FAB.kicad_sch`: repaired copy of legacy RX V5.2, all 15 refs +9000 and project instances aligned.
- `S3900E_RX_STANDALONE_V7_12_NOT_FOR_FAB.kicad_pcb`: copy of RX V7.11 with **same 15 refs**, unchanged pads, nets, via positions and drill diameters. Six GND via Ø0.30 mm fixes from V7.11 retained.

Actual standalone parser root cause: legacy graphical `(text)` contained raw LF characters inside a quoted S-expression string and lacked a UUID. KiCad `sch erc` returned **exit3 Failed to load schematic**. V7.12 text now uses escaped literal `\\n`, supplies its UUID and includes sheet root metadata; **native standalone ERC now loads (exit0)** and returns **0 errors +76 warnings**: 46 off-grid endpoints, 15 footprint links, 15 symbol library issues. This is NOT clean ERC.

Actual KiCad native PCB DRC still returns **85 violations** (70 dangling vias, 15 footprint warnings) plus **63 unconnected**, not DRC clean. The local `fp-lib-table` lists existing library paths and does not certify any SMD land pattern or SMA/LNA assembly.

All original KiCad files are preserved. No crossmodule nets or RF TX hardware added. **NO FAB / NO TX.**
