#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python build_v36.py
python audit_v36.py
python test_v36.py
printf 'Checks completed: only independent static geometry/net audits, NOT native KiCad DRC.\n'
