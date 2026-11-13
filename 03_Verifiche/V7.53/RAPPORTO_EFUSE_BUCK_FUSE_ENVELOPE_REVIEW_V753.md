# V7.53 — Ingresso eFuse / buck 5V / fusibile: finestra di potenza (REVIEW, NO FAB)

Data: 2026-11-13. Baseline immutata V7.52, PR #56 merged. Questa revisione NON sceglie né qualifica un percorso di reset autonomo. Collegamento di SHDN U200 pin 7 ancora assente. Nessuna ECO CAD, netlist invariata per costruzione. Issue blocker: #57.

## Fatti certificati vs ipotesi

- TPS26600PWPT U200: R203=8k2 ±1% (ILIM), R204=402k ±1% (MODE->EFUSE_RTN = **latch-off**), C201=22 nF, SHDN NC; GND_MAIN U200.9 separato da EFUSE_RTN U200.8 e 17. TI SLVSDG2G Rev G §9.3.5.1, §9.4, Tab 2.
- F200=1.5A Littelfuse 045101.5MRL **candidate**. 75% of nameplate =1.125 A is a *preliminary design heuristic*, not a measured fuse trip or manufacturer guarantee. Need manufacturer time-current/derating proof at temperature and inrush.
- TPS54202 5V, maximum rated 2A output, 5ms internal soft-start (TI SLVSD26C Rev C Feb 2026). No assertion that current real load equals 2A or efficiency equals 85%.
- Static simplified eFuse nominal setpoint from TI I_OL=12/R_ILIM[kΩ]: 12/8.2 ≈1.4634A. Tolerances, thermal response, transient fast-trip and actual fault waveforms NOT modeled. 1.46A nominal current regulation does not guarantee 1.5A fuse clearing.

## Hypothetical 5 V rail full-load example (not system demand)

At Pout=5V*2A=10W and **assumed** eta=.85: Iin=Pout/(Vin*eta).

| eFuse/buck input voltage | Hypothetical buck input current |
|---|---:|
| 10.25V | 1.1478A |
| 13.8V | 0.8525A |
| 17.05V | 0.6900A |

The minimum-input hypothetical full-load case slightly exceeds the conservative 1.125A *design target*, not the nominal 1.5A fuse rating. At Vin=10.25V and eta=.85, an input design target 1.125A would support only 1.9603A of 5V load, BEFORE additional AUX consumption and transients. This is a CONDITIONAL sizing warning, not an actual overload finding. Efficiency is load-, temperature- and input-dependent; VIN at buck is AFTER fuse/eFuse drops and may be below upstream J100 under load.

## Reset decision (BLOCKED)

MODE=402k current-limit latch-off is safer against repeated thermal retry in some faults but cannot recover solely from a downstream STM32. TI specifies recovery after VIN below falling POR threshold or SHDN toggling. Presence, electrical topology, off-time and accessibility of independent upstream power switch have not been verified. Do not add an unqualified button/harness to SHDN: manufacturer reference domain, EMC, ESD and accidental contact between unlike connectors require proof. Other modes (MODE open breaker auto-retry, short RTN active-limit auto-retry) MUST be qualified against repeated short-circuit stress before changing CAD.

## Release gate

1. Acquire complete real 5V/AUX/MCU/RX worst-case current budget including startup.
2. Obtain TPS54202 efficiency, input capacitor DC bias / Ceff, 5ms soft-start interaction and ripple measured or justified in envelope.
3. Coordinate F200 melt/time-current, ambient temperature, eFuse thermal/latchoff, R203 tolerance, 13.8V supply and 10.25–17.05V case; simulate startup/fault and validate on bench later.
4. Demonstrate an accessible independent upstream power-cycle or properly isolated/qualified SHDN reset architecture **before** implementing as ECO. Then run KiCad9 native 7-sheet before/after netlist/ERC, strict net parity and manufacturer land review.
5. Keep 15 crossmodule OPEN/HOLD, GND_MAIN/EFUSE_RTN separation, SG48/Y1 pin10 HOLD. **NO FAB / NO GERBER / NO PCBWAY / NO TX.**

Proof: `03_Verifiche/V7.53/test_efuse_buck_input_envelope_v753.py` checks source fields, SHDN NC, RTN separation and 12 conditional numerical/hold assertions. These are static regression tests, NOT native KiCad ERC, circuit simulation, physical measurement or approval.

Sources: https://www.ti.com/lit/ds/symlink/tps2660.pdf ; https://www.ti.com/lit/ds/symlink/tps54202.pdf ; https://github.com/jd3485/Superstar3900-SMD-Evolution/issues/57
