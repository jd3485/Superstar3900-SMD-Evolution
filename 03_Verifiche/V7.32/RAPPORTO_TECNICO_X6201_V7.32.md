# V7.32 — SiTime X6201 12.288 MHz vendor land review (NO FAB/TX)

**Date 2026-11-11.** Exact MPN from schematic and distributor: **SiT8008AI-22-33E-12.288000**. SiTime SiT8008 revision A, -40..85C industrial, ±25ppm, code 2 3.2x2.5mm 3225, 33=3.3V, E=OE, oscillator 12.288MHz. Distributor exact part: https://www.digikey.com/en/products/detail/sitime/SIT8008AI-22-33E-12-288000/11352695

Vendor documentation: SiTime **SiT8008A Rev1.11, pages 2, 8, 10** (do not substitute rev B), https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/2092/SiT8008A.pdf . Land recommendation 3225: pad centers 2.20mm horizontal and 1.90mm vertical; each copper pad 1.40mm horizontal x 1.20mm vertical. Top view pins 1=OE bottom-left, 2=GND bottom-right, 3=OUT top-right, 4=VDD top-left. Coordinates in KiCad where Y increases downward: 1(-1.1,+0.95), 2(+1.1,+0.95), 3(+1.1,-0.95), 4(-1.1,-0.95), mm. Pad gaps 0.80mm horiz / 0.70mm vert. Courtyard and paste/mask are reviewer candidates, not DFM approved. Original symbol pins and existing netlist already match this vendor pinout.

**Real CAD change:** only X6201 instance footprint assignment to `S3900E_SITIME_3225_V732_HOLD:SiT8008AI_3225_VENDOR_CANDIDATE` in versioned MCU sheet; revised root references that sheet, reuses AUX V7.31 and unchanged RX. New four-pad KiCad footprint in `04_KiCad/Librerie_Footprint_V7.32_SITIME_X6201_HOLD/`, new fp-lib-table. Old CAD retained.

**Native fail-closed acceptance:** KiCad9 before/after seven sheets: exactly 132 components, 100 identical pin-net mappings, only X6201 footprint changed, 42->41 unassigned footprints, ERC 36 errors /218 warnings before and after, 217 existing offgrid warnings unchanged; pcbnew.FootprintLoad verifies exact 4 pads and x/y/width/height. 10 native CI tests. Any mismatch blocks merge.

**HOLDs:** 36 ERC errors, 15 RX/MCU/AUX crossmodule interfaces OPEN/HOLD, Y1 TXC pin10 AFC/GND unresolved, SG48 HOLD, no unified PCB/no global DRC, clock jitter/EMI/enable/assembly/DFM not measured, no hardware qualification. **NO FAB / NO GERBER / NO PCBWAY / NO TX.**
