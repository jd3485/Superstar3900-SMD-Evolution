#!/usr/bin/env bash
# Run native DRC against a COPY of V4.3 hypothesis. Must have KiCad >=10 CLI.
# This does NOT establish TE conformity, thermals, or release for fabrication.
set -u -o pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SOURCE="$ROOT/04_KiCad/Modulo_RX_Test_50ohm_V4.3_STUDIO_SMA/S3900E_RX_TEST_50R_V4_3_SMA_ENVELOPE_HYPOTHESIS_NOT_FOR_FAB.kicad_pcb"
OUT="${1:-$PWD/KICAD_V43_OUTPUT}"
mkdir -p "$OUT"
if ! command -v kicad-cli >/dev/null 2>&1; then
 echo 'BLOCKED: kicad-cli missing: NO DRC RUN' | tee "$OUT/STATUS.txt"
 exit 2
fi
kicad-cli version >"$OUT/VERSION.txt" 2>&1
if ! kicad-cli pcb drc --help | grep -q -- '--refill-zones'; then
 echo 'BLOCKED: CLI cannot refill zones; use KiCad PCB Editor on a COPY.' | tee "$OUT/STATUS.txt"
 exit 3
fi
if ! kicad-cli pcb drc --help | grep -q -- '--save-board'; then
 echo 'BLOCKED: CLI cannot persist zone refill on copy.' | tee "$OUT/STATUS.txt"
 exit 3
fi
cp "$SOURCE" "$OUT/CANDIDATE_COPY_FOR_DRC.kicad_pcb"
set +e
kicad-cli pcb drc --refill-zones --save-board --severity-all --exit-code-violations \
 -o "$OUT/DRC_V4.3.rpt" "$OUT/CANDIDATE_COPY_FOR_DRC.kicad_pcb" \
 >"$OUT/stdout.txt" 2>"$OUT/stderr.txt"
RESULT=$?
set -e
printf 'Native KiCad DRC process exit code: %s\n' "$RESULT" | tee "$OUT/STATUS.txt"
printf '%s\n' 'Always review DRC report and obtain real TE CAD / thermals / matched schematic. NO FAB.' | tee -a "$OUT/STATUS.txt"
exit "$RESULT"
