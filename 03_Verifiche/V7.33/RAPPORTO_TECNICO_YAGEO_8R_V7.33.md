# V7.33 — Yageo RC0402 four real MPNs, eight MCU/CODEC resistors, native REVIEW/HOLD

11 November 2026; physical vendor candidate **not approved for production**. 8 resistor symbols in MCU 7-sheet baseline V7.32. No electrical change, all original resistance values retained. Proposed MPN ↔ values mapping:

- R6201: 47k → Yageo **RC0402FR-0747KL**
- R6202, R6203, R6204, R6206: 4.7k → **RC0402FR-074K7L**
- R6205: 33R → **RC0402FR-0733RL** (**series audio MCLK; SI and worst-fault thermal HOLD**)
- R6207, R6208: 1k → **RC0402FR-071KL**

Official individual Yageo documents:
- https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-0747KL
- https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-074K7L
- https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-0733RL
- https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-071KL

All four 0402 / 1005 metric (1.0±0.05 x 0.5±0.05mm), 1%, 0.063W at 70°C, maximum continuous rated working voltage 50V, temperature up to 155°C (manufacturer conditions). **Yageo Chip Resistor Surface Mount, Mounting v10, 13 Feb 2018, page4 table1**: https://www.y-ic.es/datasheet/94/TC164-JR-072K7L.pdf . Reflow PCB land A=1.50mm total outer, B=0.50mm internal gap, C=0.50mm each x pad, D=0.60mm pad y. Copper pad centres x±0.50mm. KiCad reviewer footprint `S3900E_YAGEO_0402_V733_HOLD:YAGEO_RC0402_REFLOW_VENDOR_CANDIDATE`: 2 pads (±0.5,0), each (0.5,0.6); gap 0.5, outer span 1.5. Symbol pins 1 and 2 passive, no electrical delta. New MCU schematic changes only 8 instance footprints and 8 hidden MPN fields. New root references MCU V7.33 and leaves AUX V7.31, RX, other sub-sheets untouched.

**Engineering hold:** physical MPN and land only; no board assembly, mask/paste DFM, placement/orientation, thermal evaluation, startup and waveforms. R6205 series clock 33Ω is not approved until worst transient/fault current and signal integrity known; direct hypothetical 3.3V short across 33Ω implies approx 0.33W, greater than nominal 0.063W; this is fault illustration, NOT expected operating dissipation. R6207/8 analog chain RF susceptibility and noise still to be measured. No proof supply or protections by mere rating.

**Required native CI gate:** KiCad9 `pcbnew.FootprintLoad`, 132 components, 100 identical nets, 0 pin-net delta, only 8 resistor footprint changes, 41→33 unassigned, 36 error+218 warning ERC identical, 10 tests PASS, final JSON/netlist/ERC native artifacts. Any mismatch BLOCKS integration.

**15 intermodule interfaces OPEN/HOLD, SG48 HOLD, Y1 10-pad AFC/GND HOLD. No complete PCB/DRC/hardware; NO FAB / NO GERBER / NO PCBWAY / NO TX.**
