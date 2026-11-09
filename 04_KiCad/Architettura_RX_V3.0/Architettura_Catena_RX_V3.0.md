# Catena RX - V3.0 (scelta sperimentale, NON approvata)

ANT 50 ohm -> TX/RX switch & ESD/overload protection (TO DESIGN) -> CORE9 V2.9 (complete nine-element vendor-based preselector) -> RF switch (TO DESIGN) -> ADL5535 5 V (LNA on / bypass) -> optional 6 dB matched RF pad AFTER LNA -> ADE-1+ double-balanced mixer -> IF 10.695 MHz (TO DESIGN).

PLL LMX2572, LO buffer and LO clean-up filter are NOT wired to ADE-1+ yet. Required LO drive nominal +7dBm at mixer port must be measured.

## Invariant
- Protect front-end during transmit, including 4W AM/FM / 12W PEP SSB nominal operating limits, before connecting LNA or test board.
- Single board demonstration only with RF signal source / no TX connection until T/R isolation designed.
- Low-noise mode: LNA inserted; strong station mode: 6dB pad after LNA; optional LNA bypass for extremely high signals.
- Attenuator POST LNA is more favorable for noise than the same pad at the antenna. It does not prevent LNA overloading from strong RF, hence bypass is separate.
- Image rejection for the complete CORE9 passive section follows V2.9 nominal model; no claim for switching network, PCB, or gain-state passband.

## PCB Coupon Proposed (NOT ROUTED)
50ohm SMA IN -> 9-element CORE9 -> SMA OUT; dedicated grounds, via fence, accessible test nodes, not connected to an antenna or transmitter. Coupon is a proposed validation artifact, not a finished board.

## Barriers to approval
1. Native KiCad ERC/DRC and footprints of inductors; 2. VNA s11/s21 from 1 to 70 MHz; 3. NF and two-tone intercept at 27 MHz; 4. LNA supply noise/thermal; 5. switch insertion loss & TX isolation; 6. LO power and leakage; 7. out-of-band blocker and reciprocal-mixing testing.
