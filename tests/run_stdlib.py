"""Runner de testes mínimo baseado apenas na biblioteca padrão.

Descobre funções `test_*` nos módulos `tests/test_*.py`, executa-as e reporta.
Fallback para quando `pytest` não está disponível (mantém a filosofia de zero
dependências externas). Uso: `python tests/run_stdlib.py`.
"""

from __future__ import annotations

import importlib.util
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    test_files = sorted((ROOT / "tests").glob("test_*.py"))
    total = passed = failed = 0
    failures: list[str] = []

    for tf in test_files:
        mod = _load_module(tf)
        for name in dir(mod):
            if not name.startswith("test_"):
                continue
            fn = getattr(mod, name)
            if not callable(fn):
                continue
            total += 1
            try:
                fn()
                passed += 1
                print(f"PASS {tf.name}::{name}")
            except Exception:  # noqa: BLE001
                failed += 1
                tb = traceback.format_exc()
                failures.append(f"FAIL {tf.name}::{name}\n{tb}")
                print(f"FAIL {tf.name}::{name}")

    print("\n" + "=" * 60)
    for f in failures:
        print(f)
    print(f"Total: {total} | Passou: {passed} | Falhou: {failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
