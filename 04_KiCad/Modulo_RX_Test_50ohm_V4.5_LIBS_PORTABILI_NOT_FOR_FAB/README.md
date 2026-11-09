# V4.5 — modulo RX: KiCad study project with portable custom libraries

**NOT FOR FABRICATION / NO TX.** Contains a byte-for-byte copy of the **V4.3 experimental SMA board** plus the schematic candidate from V4.4, renamed for use together with KiCad. The geometries and pin mapping have not been approved by TE or ADI.

Open `S3900E_RX_TEST_50R_V4_5_LIBS_CANDIDATE_NOT_FOR_FAB.kicad_sch` and the corresponding `.kicad_pcb` in a **KiCad installation**. The two project-specific tables (`fp-lib-table`, `sym-lib-table`) reference only local `${KIPRJMOD}` paths:

- `S3900E_v33.pretty/` contains 6 models for passives and bench power connector.
- `S3900E_v35.pretty/` contains 1 perpendicular 0402 shunt model.
- `S3900E_V38_Review.pretty/` contains 2 models: 4 x SMA connector instances (study variant with pads moved ±0.18 mm), and ADL5535 solder/thermal candidate.
- `S3900E.kicad_sym` contains the 9 schematic symbol types.

The extracted custom libraries reproduce the *as-designed* candidate PCB footprints, **not** the original manufacturer's formally approved land patterns. Do **not** use the presence of a library as evidence of physical correctness.

To run checks, use `03_Verifiche/V4.5/RUN_KICAD_RX_V45.sh <report-directory>` from the archive root. It performs native ERC and DRC with filled zones and schematic parity on a temporary copy **only if** `kicad-cli` is available. Inspect all warnings and failures and compare the nets/UUIDs manually in KiCad. This script does not generate fabrication outputs.

This board is a receiver RF *test coupon*, not the complete CB radio. Its 50 Ω controlled impedance, TE connector body/land pattern, ADL5535 thermal design and final RF performance remain unverified.
