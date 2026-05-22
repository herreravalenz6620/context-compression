#!/bin/sh
set -eu

DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PY="$DIR/.venv/bin/python"

if [ ! -x "$PY" ]; then
  PY=python3
fi

exec "$PY" "$DIR/hook.py"
