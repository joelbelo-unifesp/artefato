"""Carregamento e validação das entradas do FIGOV a partir de arquivos JSON."""

from __future__ import annotations

from pathlib import Path

from .schema_validator import load_and_validate
from .schemas import SCHEMAS


def load_vertiporto(path: str | Path) -> dict:
    return load_and_validate(path, SCHEMAS["vertiporto"])


def load_frota(path: str | Path) -> dict:
    return load_and_validate(path, SCHEMAS["frota"])


def load_demanda(path: str | Path) -> dict:
    return load_and_validate(path, SCHEMAS["demanda"])


def load_seguranca(path: str | Path) -> dict:
    return load_and_validate(path, SCHEMAS["seguranca"])


def load_cenario(path: str | Path) -> dict:
    return load_and_validate(path, SCHEMAS["cenario"])
