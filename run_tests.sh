#!/usr/bin/env bash
# Executa a suíte de testes do FIGOV.
# Preferência: pytest, se disponível no ambiente; caso contrário, runner stdlib.
set -euo pipefail
cd "$(dirname "$0")"

PY="${PYTHON:-python}"
SITE="$($PY -c 'import site,sys; print(site.getsitepackages()[0])' 2>/dev/null || true)"

export PYTHONPATH="${SITE}:src"

if $PY -c "import pytest" 2>/dev/null; then
  exec $PY -m pytest -q "$@"
else
  echo "pytest indisponível; usando runner stdlib (tests/run_stdlib.py)"
  exec $PY tests/run_stdlib.py "$@"
fi
