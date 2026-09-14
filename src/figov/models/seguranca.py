"""Modelo E — Segurança operacional como critério de aceitação (RF-04).

Guardrail transversal (spec §5): a segurança NÃO é uma etapa do pipeline de solvers;
é uma condição de validade aplicada SOBRE as agendas produzidas (Modelo B/D). Planos
que violem o nível alvo de risco são REJEITADOS automaticamente, com indicação
explícita da violação.

Rastreabilidade (RNF-03):
    Premissa: a operação eVTOL sobre área urbana impõe risco ar-solo; um plano só é
              aceitável se o risco agregado não exceder um nível alvo, e se houver
              sítios de contingência disponíveis.
    Requisito: RF-04 — avaliar critérios de aceitação de segurança e contingência,
               rejeitando soluções que os violem.
    Implementação: este módulo (guardrail).

Modelo de risco ar-solo (1a ordem):
    - risco_por_movimento: proxy configurável (probabilidade de evento por movimento).
      [A DEFINIR] — fonte pretendida: EASA PTS-VPT e regulação ANAC em formação.
    - risco agregado por hora de voo = risco_por_movimento * movimentos_por_hora.
    - critério: risco agregado por hora <= nivel_alvo_risco (parâmetro [A DEFINIR]).
    - contingência: cada vertiporto de origem deve ter ao menos um sítio de
      contingência alcançável; a ausência de sítios é violação obrigatória (o schema
      já exige a lista não-vazia — aqui verificamos a regra operacional).

IMPORTANTE: nivel_alvo_risco e risco_por_movimento são PLACEHOLDERS. Não representam
valores validados; devem ser justificados antes de qualquer conclusão (ver docs).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ViolacaoSeguranca(str, Enum):
    RISCO_EXCEDE_ALVO = "risco_ar_solo_excede_nivel_alvo"
    SEM_CONTINGENCIA = "sem_sitio_de_contingencia"


@dataclass
class RelatorioSeguranca:
    aprovado: bool
    nivel_alvo_risco: float
    risco_agregado_por_hora: float
    n_sitios_contingencia: int
    violacoes: list[dict] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)
    rf: str = "RF-04"

    def to_dict(self) -> dict:
        return {
            "rf": self.rf,
            "aprovado_RF04": self.aprovado,
            "nivel_alvo_risco": self.nivel_alvo_risco,
            "risco_agregado_por_hora": self.risco_agregado_por_hora,
            "n_sitios_contingencia": self.n_sitios_contingencia,
            "violacoes": self.violacoes,
            "avisos": self.avisos,
        }


def _movimentos_por_hora(resultado, janela_min: float) -> float:
    n = len(resultado.alocacoes)
    horas = janela_min / 60.0 if janela_min > 0 else 1.0
    return n / horas if horas > 0 else 0.0


def avaliar_seguranca(
    resultado,
    seguranca: dict,
    *,
    janela_min: float = 1080.0,
) -> RelatorioSeguranca:
    """Aplica o guardrail de segurança sobre uma agenda (ResultadoAgenda).

    Retorna um RelatorioSeguranca; `aprovado=False` implica que o plano deve ser
    REJEITADO (RF-04). Cada violação é registrada explicitamente.
    """
    nivel_alvo = seguranca["nivel_alvo_risco"]
    risco_mov = seguranca.get("risco_por_movimento", 0.0)
    sitios = seguranca.get("sitios_contingencia", [])

    violacoes: list[dict] = []

    # Regra de contingência (obrigatória).
    if not sitios:
        violacoes.append(
            {
                "tipo": ViolacaoSeguranca.SEM_CONTINGENCIA.value,
                "detalhe": "Nenhum sítio de contingência configurado (RF-04 exige ao menos um).",
            }
        )

    # Risco ar-solo agregado.
    mov_h = _movimentos_por_hora(resultado, janela_min)
    risco_agregado = risco_mov * mov_h
    if risco_agregado > nivel_alvo + 1e-18:
        violacoes.append(
            {
                "tipo": ViolacaoSeguranca.RISCO_EXCEDE_ALVO.value,
                "detalhe": (
                    f"Risco agregado {risco_agregado:.3e}/h excede o nível alvo "
                    f"{nivel_alvo:.3e}/h."
                ),
                "risco_agregado_por_hora": risco_agregado,
                "nivel_alvo_risco": nivel_alvo,
            }
        )

    aprovado = len(violacoes) == 0
    avisos = [
        "nivel_alvo_risco e risco_por_movimento são [A DEFINIR] (placeholders); "
        "fonte pretendida EASA PTS-VPT / ANAC. Não usar para conclusões sem justificar."
    ]

    return RelatorioSeguranca(
        aprovado=aprovado,
        nivel_alvo_risco=nivel_alvo,
        risco_agregado_por_hora=round(risco_agregado, 12),
        n_sitios_contingencia=len(sitios),
        violacoes=violacoes,
        avisos=avisos,
    )


def aplicar_guardrail(resultado, seguranca: dict, *, janela_min: float = 1080.0):
    """Aplica o guardrail e devolve (aprovado, relatorio).

    Uso no pipeline: uma agenda só é ACEITA se `aprovado` for True. Caso contrário, o
    plano é rejeitado por segurança, independentemente da sua qualidade nos solvers
    (spec §10, regra geral de aceitação).
    """
    rel = avaliar_seguranca(resultado, seguranca, janela_min=janela_min)
    return rel.aprovado, rel
