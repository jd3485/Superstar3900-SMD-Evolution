#!/usr/bin/env bash
# Safe native ERC/DRC on an ephemeral copy. NEVER authorizes manufacture.
# Native DRC with refilled zones requires supported KiCad CLI flags (KiCad 10).
set -u -o pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
SOURCE="$ROOT/04_KiCad/Modulo_RX_Test_50ohm_V4.5_LIBS_PORTABILI_NOT_FOR_FAB"
NAME='S3900E_RX_TEST_50R_V4_5_LIBS_CANDIDATE_NOT_FOR_FAB'
DEST="${1:-$PWD/KICAD_V46_NATIVE_REPORTS}"
mkdir -p -- "$DEST" || exit 4
DEST="$(cd -- "$DEST" && pwd)"
if ! command -v kicad-cli >/dev/null 2>&1; then
    printf '%s\n' 'NOT_RUN: kicad-cli not available; ERC/DRC/parity/zone refill not executed.' > "$DEST/STATUS.txt"
    cat "$DEST/STATUS.txt"
    exit 3
fi
VERSION="$(kicad-cli version 2>&1)" || { echo 'NOT_RUN: could not read KiCad version' > "$DEST/STATUS.txt"; exit 4; }
HELP="$(kicad-cli pcb drc --help 2>&1)" || { echo 'NOT_RUN: cannot inspect pcb drc capabilities' > "$DEST/STATUS.txt"; exit 4; }
SCHHELP="$(kicad-cli sch erc --help 2>&1)" || { echo 'NOT_RUN: cannot inspect sch erc capabilities' > "$DEST/STATUS.txt"; exit 4; }
printf 'KICAD_VERSION=%s\n' "$VERSION" > "$DEST/TOOL_VERSION.txt"
for OPTION in --refill-zones --schematic-parity --severity-all --exit-code-violations --format; do
    if ! grep -Fq -- "$OPTION" <<<"$HELP"; then
        echo "NOT_RUN: KiCad PCB CLI does not support required option $OPTION; install KiCad 10 with working CLI." > "$DEST/STATUS.txt"
        cat "$DEST/STATUS.txt"
        exit 4
    fi
done
for OPTION in --severity-all --exit-code-violations --format; do
    if ! grep -Fq -- "$OPTION" <<<"$SCHHELP"; then
        echo "NOT_RUN: KiCad ERC CLI missing option $OPTION." > "$DEST/STATUS.txt"
        cat "$DEST/STATUS.txt"
        exit 4
    fi
done
TMP="$(mktemp -d -t s3900e-v46-XXXXXXXX)" || exit 4
trap 'rm -rf -- "$TMP"' EXIT
cp -a -- "$SOURCE/." "$TMP/" || exit 4
set +e
kicad-cli sch erc --severity-all --exit-code-violations --format json --output "$DEST/ERC_V4.6.json" "$TMP/$NAME.kicad_sch" >"$DEST/ERC_STDOUT.txt" 2>&1
ERC=$?
kicad-cli pcb drc --severity-all --exit-code-violations --schematic-parity --refill-zones --format json --output "$DEST/DRC_PARITY_REFILL_V4.6.json" "$TMP/$NAME.kicad_pcb" >"$DEST/DRC_STDOUT.txt" 2>&1
DRC=$?
set -e
{
    echo "ERC_EXIT=$ERC"
    echo "DRC_EXIT=$DRC"
    if [[ "$ERC" -ne 0 || "$DRC" -ne 0 || ! -s "$DEST/ERC_V4.6.json" || ! -s "$DEST/DRC_PARITY_REFILL_V4.6.json" ]]; then
        echo 'NATIVE_CHECK_FAILED_OR_INCOMPLETE: read full output; NOT_APPROVED'
    else
        echo 'NATIVE_COMMANDS_SUCCEEDED: needs engineering review, CAD TE, thermals, RF tests; NOT_APPROVED'
    fi
} >"$DEST/STATUS.txt"
cat "$DEST/STATUS.txt"
if [[ "$ERC" -ne 0 || "$DRC" -ne 0 || ! -s "$DEST/ERC_V4.6.json" || ! -s "$DEST/DRC_PARITY_REFILL_V4.6.json" ]]; then exit 5; fi
exit 0
