#!/usr/bin/env bash
# Run KiCad native ERC/DRC on COPIES of the V4.4 candidate schematic and V4.3 PCB.
# It must not modify original historical or candidate source files; no Gerber generated.
# PASS does not establish TE, thermal, stack-up, footprint library or board parity signoff.
set -u -o pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCHEM="$ROOT/04_KiCad/Modulo_RX_Test_50ohm_V4.4_SCHEMA_MATCH/S3900E_RX_TEST_50R_V4_4_MATCH_NETS_NOT_FOR_FAB.kicad_sch"
PCB="$ROOT/04_KiCad/Modulo_RX_Test_50ohm_V4.3_STUDIO_SMA/S3900E_RX_TEST_50R_V4_3_SMA_ENVELOPE_HYPOTHESIS_NOT_FOR_FAB.kicad_pcb"
DEST="${1:-$PWD/KICAD_V44_NATIVE_REPORTS}"
mkdir -p "$DEST"
if ! command -v kicad-cli >/dev/null 2>&1; then
  echo 'BLOCKED: kicad-cli not installed. NO ERC OR DRC EXECUTED.' | tee "$DEST/STATUS.txt"
  exit 2
fi
kicad-cli version > "$DEST/KICAD_VERSION.txt" 2>&1
if ! kicad-cli pcb drc --help | grep -q -- '--refill-zones'; then
  echo 'BLOCKED: KiCad CLI does not support --refill-zones.' | tee "$DEST/STATUS.txt"
  exit 3
fi
if ! kicad-cli pcb drc --help | grep -q -- '--save-board'; then
  echo 'BLOCKED: KiCad CLI does not support --save-board.' | tee "$DEST/STATUS.txt"
  exit 3
fi
cp "$SCHEM" "$DEST/SCHEM_COPY_FOR_ERC.kicad_sch"
cp "$PCB" "$DEST/PCB_COPY_FOR_DRC.kicad_pcb"
set +e
kicad-cli sch erc --severity-all --exit-code-violations -o "$DEST/ERC_V4.4.rpt" "$DEST/SCHEM_COPY_FOR_ERC.kicad_sch" > "$DEST/ERC_stdout.txt" 2> "$DEST/ERC_stderr.txt"
ERC=$?
kicad-cli pcb drc --refill-zones --save-board --severity-all --exit-code-violations -o "$DEST/DRC_V4.4.rpt" "$DEST/PCB_COPY_FOR_DRC.kicad_pcb" > "$DEST/DRC_stdout.txt" 2> "$DEST/DRC_stderr.txt"
DRC=$?
set -e
{
 printf 'Native ERC exit: %d\nNative DRC exit: %d\n' "$ERC" "$DRC"
 echo 'NO SCHEMATIC PARITY: PCB symbols are not yet UUID-linked to this candidate schematic.'
 echo 'NO FAB: TE SMA CAD, U101 thermal signoff, final stack-up and RF measurements missing.'
} | tee "$DEST/STATUS.txt"
[ "$ERC" -eq 0 ] && [ "$DRC" -eq 0 ]
