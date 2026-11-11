# V7.31 - J100/J101 AUX native grid correction, NOT FOR FAB

Based on actual V7.29 KiCad9 ERC artifact 13856172598 downloaded and parsed: baseline 132 components, 100 nets, ERC 36 errors and 220 warnings (219 endpoint_off_grid, one Y1 footprint HOLD). J100 pin1 (27.92,32.46)mm and J101 pin1 (84.92,28.65)mm are off 50mil/1.27mm grid.

Versioned CAD correction: AUX parent J100 symbol origin moved to (33.02,35.56), J101 to (90.17,35.56), associated 8 labels moved exactly to new physical pin endpoints on 1.27mm grid and reference/value/footprint text moved consistently. No electrical wire, pin type, value, footprint, sub-sheet, net name or ground is deliberately changed. Three AUX sub-sheets preserved byte-for-byte. Old V7.29 CAD preserved.

Required true KiCad9 proof: all 132 components and 100 full-radio nets with zero changed pin-net nodes; 42 missing footprint assignments preserved; 36 ERC errors unchanged, 220 to 218 warnings by exactly two endpoint_off_grid issues (219 to 217), other rule counts unchanged. 10 fail-closed tests; one targeted PR-only native run and quick policy check. No PCB, DRC/global assembly qualification or Gerber. 15 crossdomain interfaces OPEN/HOLD, SG48 HOLD, NO FAB / NO GERBER / NO PCBWAY / NO TX.
