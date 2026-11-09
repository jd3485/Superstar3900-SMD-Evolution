# Audit V3.5: status footprint and first-routing study

**NO GERBER / DO NOT FABRICATE.** Native KiCad CLI was not available for this run.

## ADL5535 package
Updated the in-board candidate pad geometry based on ADI ADL5535 Rev A Figure 17 (p.11):
- pin 1 input and pin 3 output: pad 0.86 x 1.27 mm centered +/-1.50 mm in x;
- pin 2 GND lead: 0.86 x 1.27 mm at x=0;
- exposed paddle GND (pin 2): pad 1.80 x 3.48 mm above leads;
- two ground via outside the pad: at x=68, y=31.05 and y=39.0, not via-in-pad.
These coordinates are an **interpretation of the drawing**, not manufacturer approved library files. The rectangular thermal pad is part of ground net. Check stencil, copper clearances, thermal pad placement, and reference Gerbers.

## TE/Linx CONSMA002-SMD
- Reviewed official manufacturer's rev D recommended footprint. Dimension diameter 2.05 mm is a circular *feature*; it is NOT established here whether it requires a drilled hole, copper pad, or a no-copper opening. **No drill added**. Four SMA footprint candidates retain electrical placeholder pads from V3.4 and are explicitly renamed `REVIEW_CENTER_FEATURE_UNRESOLVED`.
- Four pads at +/-2.85, +/-2.95 remain prior **unvalidated** values. Need manufacturer's CAD / IPC mechanical verification; SMA metal housing and edge alignment can cause assembly clashes.

## Shunt resistors and routing
- R201 and R202 are now perpendicular to RF trunk, moved to y=67.3, pin 1 at y=66.75, GND pin 2 at y=67.85, GND via at y=69.45.
- R203 remains in series. This corrects the poor RF topology of V3.4.
- RF signal pilot width approx 0.28 mm assuming h=0.1855 mm, Dk=4.74, copper t=0.035 mm; conductor correction is heuristic and **soldermask is omitted**.
- All seven non-GND nets have pilot top-layer routes; ground zones remain unfilled; no claim of functional continuity or RF behavior is made.
- The included geometric audit checks approximate segment/pad separation, *not* a KiCad ERC/DRC.

## Reference sources
- ADI ADL5535 Figure 16 / Figure 17: https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf
- TE/Linx official 2D product drawing: https://www.te.com/en/product-CONSMA002-SMD.html
- PCBWay stack-up examples (not a confirmed order): https://www.pcbway.com/multi-layer-laminated-structure.html
