# V3.6 - audit return paths, pin-map sync and footprint blockers

**Not for fabrication.** This V3.6 revision is a research/test coupon, NOT the final transceiver PCB.

### Source baseline and direct changes
- Input V3.5 PCB with 15 footprints, 8 assigned nets, 23 pilot track segments and 4 ground vias; deliberately not changed in place.
- Added 20 explicit F.Cu GND segments from 16 GND shell pads of four candidate SMA connectors and 4 grounded decoupling/bench pads to vias. Added 20 matching vias, plus **40 parametric grounded fence vias** (64 total incl. the original 4). Stitching selected heuristically and checked only by conservative 2D geometry, not EM.
- Added declared GND zone on `In2.Cu`: F.Cu/In1.Cu/In2.Cu/B.Cu all now have matching GND polygon declarations, but **NONE have native KiCad filled polygons**. This is NOT measured shielding.
- Corrected the passive-inductor **physical pad NUMBERING only**: L101 pin 1 is +5V, pin 2 is RFOUT_BIAS. The V3.5 board had reversed pin numbers, inconsistent with V3.1 connection table. The inductor's two copper paths remain unchanged. `audit_v36.py` tests the schematic reference table with aliases.
- The F.Cu model uses shapely to check copper-to-copper net clearance, directly attached ground local vias, pad connectivity and 31 logical pin-to-net relationships; 2D clearance for the measured model is 0.45 mm minimum, with **0 clashes below 0.20 mm**. Roundrect pads are approximated as full rectangles, conservative. Copper zones, 3D, mask/paste, manufacturing annular rings and native DRC are NOT checked.

### Footprint and stack-up blockers
- **SMA connector:** manufacturer Rev D sheet 2 depicts a **Ø2.05 mm circular feature** in recommended footprint. Previous file treated it as a 2.05-mm F.Cu circular pad. This remains a PLACEHOLDER, not evidence that the center feature is a solder pad. DO NOT manufacture until official CAD/3D establishes function and drill/copper/soldermask shapes, orientation, panel mounting. Body overhang is not checked.
- **ADL5535:** manufacturer Rev A Figure 17 shows paddle/pin2 GND and stitching guidance. Our copper representation requires stencil and exact dimensions to be verified against manufacturer board/reference Gerber. Current vias are outside exposed paddle to avoid unfilled via-in-pad, but thermal impedance is not calculated.
- **PCBWay** catalog 1.6 mm 4L regular example: L1-L2 0.1855 mm, Dk 4.74; 1 oz finished outer copper. The previous provisional 0.28 mm 50-ohm width is NOT a verified impedance value; calculate with finite copper, mask and chosen fab stack-up before release.
- Native `kicad-cli` and `pcbnew` not available in this runtime. Static parsing is not equivalent to KiCad opening, ERC, DRC, zone refilling, 3D validation or Gerber export. No PCBWay production package has been generated.

### Source references
- https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf (Fig 16-17)
- https://www.te.com/en/product-CONSMA002-SMD.html (Rev D mechanical drawing)
- https://www.pcbway.com/multi-layer-laminated-structure.html (unconfirmed example)
