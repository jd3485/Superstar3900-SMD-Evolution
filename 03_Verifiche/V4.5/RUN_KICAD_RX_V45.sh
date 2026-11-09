#!/usr/bin/env bash
# Native KiCad validation of the V4.5 study candidate, ALWAYS on a temp copy.
# Returns nonzero when KiCad is absent or violations/errors exist. No Gerber exported.
set -u -o pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BASE=S3900E_RX_TEST_50R_V4_5_LIBS_CANDIDATE_NOT_FOR_FAB
SOURCE="$ROOT/04_KiCad/Modulo_RX_Test_50ohm_V4.5_LIBS_PORTABILI_NOT_FOR_FAB"
DEST="${1:-$PWD/KICAD_V45_NATIVE_REPORTS}"
mkdir -p "$DEST"
DEST="$(cd "$DEST" && pwd)"
if ! command -v kicad-cli >/dev/null 2>&1; then
  echo 'NOT_RUN: kicad-cli not installed. Native ERC, DRC, zone refill and schematic parity not checked.' | tee "$DEST/STATUS.txt"
  exit 3
fi
TMP="$(mktemp -d -t s3900e-v45-XXXXXXXX)" || exit 4
trap 'rm -rf "$TMP"' EXIT
cp -a "$SOURCE/." "$TMP/" || exit 4
# Do not use save-board, generate fabrication files, or touch source directory.
set +e
kicad-cli sch erc --severity-all --exit-code-violations --format json --output "$DEST/ERC_V4.5.json" "$TMP/$BASE.kicad_sch" > "$DEST/ERC_STDOUT.txt" 2>&1
ERC=$?
kicad-cli pcb drc --severity-all --exit-code-violations --schematic-parity --refill-zones --format json --output "$DEST/DRC_PARITY_V4.5.json" "$TMP/$BASE.kicad_pcb" > "$DEST/DRC_STDOUT.txt" 2>&1
DRC=$?
set -e
printf 'ERC_EXIT_CODE=%s\nDRC_PARITY_EXIT_CODE=%s\n' "$ERC" "$DRC" | tee "$DEST/STATUS.txt"
if [ "$ERC" -ne 0 ] || [ "$DRC" -ne 0 ]; then
 echo 'NOT_APPROVED: review reports, including warnings; do not manufacture.' | tee -a "$DEST/STATUS.txt"
 exit 5
fi
echo 'ERC/DRC commands completed with 0 exit codes; engineering approval and TE/ADI verification STILL REQUIRED.' | tee -a "$DEST/STATUS.txt"
