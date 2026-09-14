"""Gerador determinístico de demanda de movimentos (RNF-01: mesma seed → mesma saída).

Produz um perfil diário de movimentos entre vertiportos de uma rede, com picos de
manhã e fim de tarde. Serve como dado de entrada realista e reproduzível para a
validação por simulação parametrizada (RF-05).
"""

from __future__ import annotations

import math
import random


def _perfil_horario(minuto: int) -> float:
    """Peso relativo da demanda ao longo do dia (dois picos gaussianos)."""
    # Pico da manhã ~ 8h (480 min) e da tarde ~ 18h (1080 min).
    manha = math.exp(-((minuto - 480) ** 2) / (2 * 90 ** 2))
    tarde = math.exp(-((minuto - 1080) ** 2) / (2 * 90 ** 2))
    return 0.5 + manha + tarde


def gerar_demanda(
    vertiportos: list[str],
    *,
    seed: int,
    n_movimentos: int = 200,
    janela_min: int = 1080,
    inicio_min: int = 360,
    duracao_voo_min: float = 12.0,
    max_pax: int = 4,
) -> dict:
    """Gera um dicionário de demanda válido contra DEMANDA_SCHEMA.

    - vertiportos: ids dos nós da rede (>= 2).
    - seed: reprodutibilidade.
    - n_movimentos: total de movimentos no dia.
    - janela_min / inicio_min: janela temporal (default 06:00–24:00).
    """
    if len(vertiportos) < 2:
        raise ValueError("São necessários ao menos 2 vertiportos para gerar demanda O-D.")

    rng = random.Random(seed)
    # Amostragem de horários ponderada pelo perfil diário.
    grade = list(range(inicio_min, inicio_min + janela_min, 5))
    pesos = [_perfil_horario(m) for m in grade]

    movimentos = []
    for _ in range(n_movimentos):
        horario = rng.choices(grade, weights=pesos, k=1)[0]
        origem = rng.choice(vertiportos)
        destino = rng.choice([v for v in vertiportos if v != origem])
        pax = rng.randint(1, max_pax)
        movimentos.append(
            {
                "origem": origem,
                "destino": destino,
                "horario_desejado_min": float(horario),
                "duracao_voo_min": float(duracao_voo_min),
                "passageiros": pax,
            }
        )
    movimentos.sort(key=lambda m: m["horario_desejado_min"])
    return {
        "descricao": f"Demanda sintética determinística (seed={seed}, n={n_movimentos})",
        "movimentos": movimentos,
    }
