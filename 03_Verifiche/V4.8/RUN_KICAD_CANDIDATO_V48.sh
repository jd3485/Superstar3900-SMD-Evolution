#!/usr/bin/env bash
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
SRC="$ROOT/04_KiCad/Modulo_RX_Test_50ohm_V4.8_TERMICA_6VIE_STUDIO_NON_FAB"
BASENAME='S3900E_RX_TEST_50R_V4_8_6VIE_STUDIO_NOT_FOR_FAB'
REPORT="${1:-$PWD/KICAD_V48_RESULTS}"
mkdir -p "$REPORT" || exit 4
REPORT="$(cd "$REPORT" && pwd)"
if ! command -v kicad-cli >/dev/null 2>&1; then
  printf '%s\n' 'NOT_RUN: kicad-cli unavailable; no native ERC/DRC, zone fill or parity.' | tee "$REPORT/STATUS.txt"
  exit 3
fi
HELP="$(kicad-cli pcb drc --help 2>&1)" || exit 4
for opt in --refill-zones --schematic-parity --exit-code-violations --severity-all --format; do
  if ! grep -Fq -- "$opt" <<< "$HELP"; then echo "NOT_RUN: missing $opt" | tee "$REPORT/STATUS.txt"; exit 4; fi
done
T="$(mktemp -d -t s3900e-v48-XXXXXXXX)" || exit 4
trap 'rm -rf "$T"' EXIT
cp -a "$SRC/." "$T/" || exit 4
kicad-cli version > "$REPORT/KICAD_VERSION.txt" 2>&1
kicad-cli sch erc --severity-all --exit-code-violations --format json -o "$REPORT/ERC.json" "$T/$BASENAME.kicad_sch" >"$REPORT/ERC_STDOUT.txt" 2>&1
ERC=$?
kicad-cli pcb drc --severity-all --exit-code-violations --schematic-parity --refill-zones --format json -o "$REPORT/DRC.json" "$T/$BASENAME.kicad_pcb" >"$REPORT/DRC_STDOUT.txt" 2>&1
DRC=$?
{ echo "ERC_EXIT=$ERC"; echo "DRC_EXIT=$DRC"; echo 'NOT APPROVED; review errors/warnings, TE, thermal stackup before manufacture.'; } > "$REPORT/STATUS.txt"
cat "$REPORT/STATUS.txt"
[[ "$ERC" == 0 && "$DRC" == 0 && -s "$REPORT/ERC.json" && -s "$REPORT/DRC.json" ]]
