#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# interpreter discovery: $PYTHON_BIN, python3.14, python3.13, python3.12, python3, python
for bin in "${PYTHON_BIN:-}" python3.14 python3.13 python3.12 python3 python; do
  [ -z "$bin" ] && continue
  if command -v "$bin" >/dev/null 2>&1; then
    PYTHON_BIN="$bin"
    break
  fi
done

if [ -z "${PYTHON_BIN:-}" ]; then
  echo "error: no python interpreter found (tried python3.14, python3.13, python3.12, python3, python)" >&2
  exit 1
fi

echo "Using: $PYTHON_BIN ($("$PYTHON_BIN" --version 2>&1))"
echo
"$PYTHON_BIN" -m py_compile run_lab.py test_lab.py
"$PYTHON_BIN" run_lab.py
echo
"$PYTHON_BIN" -m unittest -v
