"""Orquestração do FIGOV — pipeline sequencial iterativo (spec §7.1).

Integra os solvers (capacidade → agendamento → rede) e aplica o guardrail de
segurança SOBRE a agenda produzida (spec §5, §10). Uma solução só é ACEITA se passar
pelo guardrail de segurança (RF-04); caso contrário é rejeitada, independentemente da
sua qualidade nos solvers.

Também oferece a comparação de cenários (RF-07): dado um conjunto de configurações
alternativas, executa o pipeline em cada uma e apresenta as diferenças nos principais
indicadores, identificando a restrição limitante.

Ordem de resolução adotada (decisão de projeto, spec §7.1): SEQUENCIAL ITERATIVA.
Nesta versão do protótipo, a realimentação Energia↔Agendamento está embutida no
próprio agendador (recarga por tempo ocioso), de modo que uma única passada já
produz uma agenda energeticamente consistente; a estrutura iterativa fica preparada
para acoplar realimentações adicionais em versões futuras.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import capacidade as cap
from .models import rede as rede_mod
from .models import seguranca as seg_mod


@dataclass
class ConfiguracaoCenario:
    """Uma configuração completa de cenário para o pipeline."""
    nome: str
    vertiportos: dict[str, dict]
    frota: dict
    demanda: dict
    seguranca: dict
    atraso_aceitavel_min: float
    desvio_capacidade_max_pct: float = 10.0
    replicas_referencia: int = 10
    seed: int = 0


@dataclass
class ResultadoPipeline:
    cenario: str
    capacidade: list[dict]          # relatório de capacidade por vertiporto (RF-01)
    rede: dict                      # relatório de rede (RF-03)
    seguranca: dict                 # relatório do guardrail (RF-04)
    aceito: bool                    # aprovado pelo guardrail de segurança?
    restricao_limitante: str | None # principal restrição (para RF-07)
    rf: str = "RF-05"
    avisos: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "rf": self.rf,
            "cenario": self.cenario,
            "aceito": self.aceito,
            "restricao_limitante": self.restricao_limitante,
            "capacidade": self.capacidade,
            "rede": self.rede,
            "seguranca": self.seguranca,
            "avisos": self.avisos,
        }


def _restricao_limitante(rel_rede: dict) -> str | None:
    """Identifica a restrição que mais limita a operação (RF-07)."""
    contagem: dict[str, int] = {}
    for v in rel_rede["por_vertiporto"]:
        for restr, n in v["rejeicoes_por_restricao"].items():
            contagem[restr] = contagem.get(restr, 0) + n
    if not contagem:
        return None
    return max(contagem, key=contagem.get)


def executar(cfg: ConfiguracaoCenario) -> ResultadoPipeline:
    """Executa o pipeline completo para uma configuração de cenário."""
    janela_min = rede_mod._janela(cfg.vertiportos)

    # 1) Capacidade (RF-01) — por vertiporto
    rel_cap = []
    for vid, vp in cfg.vertiportos.items():
        r = cap.avaliar_capacidade(
            vp,
            atraso_aceitavel_min=cfg.atraso_aceitavel_min,
            desvio_max_pct=cfg.desvio_capacidade_max_pct,
            replicas=cfg.replicas_referencia,
            seed=cfg.seed,
        )
        rel_cap.append(r.to_dict())

    # 2) Agendamento + 3) Rede (RF-02, RF-03)
    rel_rede = rede_mod.operar_em_rede(
        cfg.demanda, cfg.frota, cfg.vertiportos,
        atraso_aceitavel_min=cfg.atraso_aceitavel_min,
    )

    # reconstruir o ResultadoAgenda para o guardrail: reexecuta o agendador global
    from .models import agendamento as ag
    resultado_agenda = ag.agendar(
        cfg.demanda, cfg.frota, cfg.vertiportos,
        atraso_aceitavel_min=cfg.atraso_aceitavel_min,
    )

    # 4) Guardrail de segurança (RF-04) — aplicado SOBRE a agenda
    aceito, rel_seg = seg_mod.aplicar_guardrail(
        resultado_agenda, cfg.seguranca, janela_min=janela_min
    )

    limitante = _restricao_limitante(rel_rede.to_dict())
    if not aceito:
        # segurança sempre domina a razão de rejeição do plano (spec §10)
        limitante = "seguranca"

    return ResultadoPipeline(
        cenario=cfg.nome,
        capacidade=rel_cap,
        rede=rel_rede.to_dict(),
        seguranca=rel_seg.to_dict(),
        aceito=aceito,
        restricao_limitante=limitante,
        avisos=[
            "Limiares x%, y min e alvo de segurança são [A DEFINIR] (placeholders).",
        ],
    )


# --------------------------------------------------------------------------
# RF-07 — Apoio à decisão: comparação de alternativas
# --------------------------------------------------------------------------
@dataclass
class ComparacaoCenarios:
    resultados: list[ResultadoPipeline]
    rf: str = "RF-07"

    def to_dict(self) -> dict:
        linhas = []
        for r in self.resultados:
            linhas.append(
                {
                    "cenario": r.cenario,
                    "aceito": r.aceito,
                    "taxa_atendimento": r.rede["taxa_atendimento_agregada"],
                    "atraso_medio_min": r.rede["atraso_medio_agregado_min"],
                    "n_atendidos": r.rede["n_atendidos"],
                    "n_movimentos": r.rede["n_movimentos"],
                    "restricao_limitante": r.restricao_limitante,
                    "gargalos": r.rede["gargalos"],
                }
            )
        return {"rf": self.rf, "comparacao": linhas}


def comparar_cenarios(cfgs: list[ConfiguracaoCenario]) -> ComparacaoCenarios:
    """Executa o pipeline em >=2 alternativas e compara indicadores (RF-07).

    Critério de aceitação RF-07: comparar pelo menos duas alternativas, apresentando
    diferenças nos indicadores e identificando a restrição limitante de cada uma.
    """
    if len(cfgs) < 2:
        raise ValueError("RF-07 exige ao menos duas alternativas para comparação.")
    resultados = [executar(c) for c in cfgs]
    return ComparacaoCenarios(resultados=resultados)
