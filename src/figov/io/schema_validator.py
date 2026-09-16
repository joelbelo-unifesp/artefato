"""Validador de schema mínimo, baseado apenas na biblioteca padrão.

Suporta um subconjunto de JSON Schema suficiente para validar as entradas do FIGOV:
- "type": object | array | string | number | integer | boolean
- "required": [campos]
- "properties": {campo: subschema}
- "items": subschema (para arrays)
- "minimum" / "maximum" (para número/inteiro)
- "minItems" (para arrays)
- "enum": [valores permitidos]

O objetivo é manter o repositório executável do zero, sem dependências externas
(RNF-05). Se no futuro a robustez de `jsonschema` for necessária, este módulo pode
ser substituído sem alterar os chamadores.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SchemaValidationError(ValueError):
    """Erro de validação de dados de entrada contra um schema."""


_TYPE_MAP = {
    "object": dict,
    "array": list,
    "string": str,
    "number": (int, float),
    "integer": int,
    "boolean": bool,
}


def _check_type(value: Any, expected: str, path: str, errors: list[str]) -> bool:
    py_type = _TYPE_MAP.get(expected)
    if py_type is None:
        return True  # tipo não suportado: ignora silenciosamente
    # bool é subclasse de int em Python; tratamos com cuidado
    if expected == "integer" and isinstance(value, bool):
        errors.append(f"{path}: esperado integer, recebido boolean")
        return False
    if expected == "number" and isinstance(value, bool):
        errors.append(f"{path}: esperado number, recebido boolean")
        return False
    if not isinstance(value, py_type):
        errors.append(f"{path}: esperado {expected}, recebido {type(value).__name__}")
        return False
    return True


def _validate(value: Any, schema: dict, path: str, errors: list[str]) -> None:
    expected = schema.get("type")
    if expected and not _check_type(value, expected, path, errors):
        return

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: valor {value!r} fora do conjunto permitido {schema['enum']}")

    if expected in ("number", "integer") and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: {value} < mínimo {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: {value} > máximo {schema['maximum']}")

    if expected == "object" and isinstance(value, dict):
        for req in schema.get("required", []):
            if req not in value:
                errors.append(f"{path}: campo obrigatório ausente: '{req}'")
        for prop, subschema in schema.get("properties", {}).items():
            if prop in value:
                _validate(value[prop], subschema, f"{path}.{prop}", errors)

    if expected == "array" and isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{path}: array com {len(value)} item(ns) < minItems {schema['minItems']}")
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(value):
                _validate(item, item_schema, f"{path}[{i}]", errors)


def validate(data: Any, schema: dict, *, name: str = "<dados>") -> None:
    """Valida `data` contra `schema`. Levanta SchemaValidationError se inválido."""
    errors: list[str] = []
    _validate(data, schema, name, errors)
    if errors:
        joined = "\n  - ".join(errors)
        raise SchemaValidationError(f"Validação falhou para {name}:\n  - {joined}")


def load_json(path: str | Path) -> Any:
    """Carrega um arquivo JSON."""
    p = Path(path)
    with p.open(encoding="utf-8") as fh:
        return json.load(fh)


def load_and_validate(path: str | Path, schema: dict) -> Any:
    """Carrega um JSON e valida contra o schema, usando o nome do arquivo no erro."""
    data = load_json(path)
    validate(data, schema, name=str(path))
    return data
