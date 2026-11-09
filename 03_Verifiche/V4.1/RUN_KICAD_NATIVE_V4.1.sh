#!/usr/bin/env bash
# NOT run on package creation. KiCad 10+ for automated refill-on-copy + DRC.
# Does not modify source PCB; cannot authorize fabrication by itself.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PCB="$ROOT/04_KiCad/Modulo_RX_Test_50ohm_V3.8/S3900E_RX_TEST_50R_V3_8_SHAPED_LAND_THERMAL_REVIEW_NOT_FOR_FAB.kicad_pcb"
SCH="$ROOT/04_KiCad/Modulo_RX_Test_50ohm_V3.1/S3900E_RX_TEST_50R_V3_1_DRAFT.kicad_sch"
OUT="${1:-$PWD/KICAD_VALIDAZIONE_V4_1}"
mkdir -p "$OUT"
if ! command -v kicad-cli >/dev/null 2>&1; then
    printf 'BLOCKED: kicad-cli not installed. No DRC/ERC executed.\n' | tee "$OUT/STATUS.txt"
    exit 2
fi
kicad-cli version >"$OUT/KICAD_VERSION.txt" 2>&1
# Never run a native DRC on unfilled zones without a saved refill of the COPY.
if ! kicad-cli pcb drc --help | grep -q -- '--refill-zones'; then
    printf 'BLOCKED: this KiCad CLI lacks --refill-zones. Refill and save a COPY in PCB Editor, then run manual native DRC.\n' | tee "$OUT/STATUS.txt"
    exit 3
fi
if ! kicad-cli pcb drc --help | grep -q -- '--save-board'; then
    printf 'BLOCKED: this KiCad CLI lacks --save-board. Use PCB Editor on a COPY.\n' | tee "$OUT/STATUS.txt"
    exit 3
fi
cp "$PCB" "$OUT/BOARD_COPY_FOR_NATIVE_DRC.kicad_pcb"
cp "$SCH" "$OUT/SCHEMATIC_COPY_FOR_NATIVE_ERC.kicad_sch"
set +e
kicad-cli pcb drc --refill-zones --save-board --severity-all --exit-code-violations \
    -o "$OUT/DRC_KICAD_V4.1.rpt" "$OUT/BOARD_COPY_FOR_NATIVE_DRC.kicad_pcb" \
    >"$OUT/DRC_stdout.txt" 2>"$OUT/DRC_stderr.txt"
DRC=$?
kicad-cli sch erc --severity-all --exit-code-violations \
    -o "$OUT/ERC_KICAD_V4.1.rpt" "$OUT/SCHEMATIC_COPY_FOR_NATIVE_ERC.kicad_sch" \
    >"$OUT/ERC_stdout.txt" 2>"$OUT/ERC_stderr.txt"
ERC=$?
set -e
printf 'Native DRC return code: %s\nNative draft-schematic ERC return code: %s\n' "$DRC" "$ERC" | tee "$OUT/STATUS.txt"
printf 'Do not release to fabrication: TE footprint/thermal/RF stack-up/physical test signoff still open.\n' | tee -a "$OUT/STATUS.txt"
if [ "$DRC" -ne 0 ] || [ "$ERC" -ne 0 ]; then exit 4; fi
exit 0
