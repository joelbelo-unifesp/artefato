"""Protocolo de validação (RF-05).

Rastreabilidade (RNF-03):
    Premissa: a validade do artefato apoia-se em simulação parametrizada e reprodutível
              (validação principal), com validação complementar por dados reais do
              Living Lab quando disponíveis.
    Requisito: RF-05 — protocolo documentado (parâmetros, cenários, réplicas,
               resultados), execução parametrizada, comparação com referência, e
               rastreabilidade cenário simulado ↔ cenário real.
    Implementação: este módulo + docs/PROTOCOLO-DE-VALIDACAO.md.

Estratégia (spec §12):
    - Validação PRINCIPAL: simulação (aqui). Obrigatória, sustenta a tese sozinha.
    - Validação COMPLEMENTAR: Living Lab (Sapiens Parque). Condicional à disponibilidade
      de dados reais — [A VERIFICAR]. A ausência desses dados NÃO invalida a tese.

Este módulo produz um relatório de validação estruturado para um conjunto de cenários,
incluindo a comparação capacidade analítica vs. simulação de eventos discretos (T-01),
os indicadores do pipeline por cenário, e campos de rastreabilidade simulado↔real.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .. import pipeline as pipe
from . import capacidade as cap


@dataclass
class ResultadoValidacaoCapacidade:
    vertiporto_id: str
    replicas: int
    cap_analitica_wq_min: float
    des_wq_min: float
    desvio_pct: float
    desvio_max_aceitavel_pct: float
    aprovado: bool

    def to_dict(self) -> dict:
        return {
            "vertiporto_id": self.vertiporto_id,
            "replicas": self.replicas,
            "cap_analitica_wq_min": round(self.cap_analitica_wq_min, 4),
            "des_wq_min": round(self.des_wq_min, 4),
            "desvio_pct": round(self.desvio_pct, 4),
            "desvio_max_aceitavel_pct": self.desvio_max_aceitavel_pct,
            "aprovado": self.aprovado,
        }


def validar_capacidade(
    vertiporto: dict,
    *,
    atraso_aceitavel_min: float,
    desvio_max_pct: float,
    replicas: int,
    seed: int,
) -> ResultadoValidacaoCapacidade:
    """T-01: compara Wq analítico (M/M/c) com a DES de referência no ponto de operação."""
    prat = cap.capacidade_pratica(vertiporto, atraso_aceitavel_min)
    teo = cap.capacidade_teorica(vertiporto)
    taxa_op = prat.cap_pratica_mov_h if prat.cap_pratica_mov_h > 0 else teo.cap_teorica_mov_h * 0.5
    wq_analitico = cap.espera_media_min(taxa_op, vertiporto)
    des = cap.simular_des_referencia(taxa_op, vertiporto, replicas=replicas, seed=seed)

    if des.espera_media_min > 0:
        desvio = abs(wq_analitico - des.espera_media_min) / des.espera_media_min * 100.0
    else:
        desvio = 0.0 if wq_analitico <= 1e-9 else 100.0

    return ResultadoValidacaoCapacidade(
        vertiporto_id=vertiporto.get("id", "?"),
        replicas=replicas,
        cap_analitica_wq_min=wq_analitico,
        des_wq_min=des.espera_media_min,
        desvio_pct=desvio,
        desvio_max_aceitavel_pct=desvio_max_pct,
        aprovado=desvio <= desvio_max_pct,
    )


@dataclass
class RelatorioValidacao:
    cenarios: list[dict] = field(default_factory=list)
    validacao_capacidade: list[dict] = field(default_factory=list)
    rastreabilidade_living_lab: dict = field(default_factory=dict)
    parametros: dict = field(default_factory=dict)
    rf: str = "RF-05"

    def to_dict(self) -> dict:
        return {
            "rf": self.rf,
            "parametros": self.parametros,
            "validacao_capacidade_T01": self.validacao_capacidade,
            "cenarios": self.cenarios,
            "rastreabilidade_living_lab": self.rastreabilidade_living_lab,
        }


def executar_protocolo(
    cfgs: list[pipe.ConfiguracaoCenario],
    *,
    living_lab_disponivel: bool = False,
) -> RelatorioValidacao:
    """Executa o protocolo de validação sobre um conjunto de cenários (RF-05).

    - Para cada cenário: roda o pipeline e coleta indicadores.
    - Para cada vertiporto do primeiro cenário: valida capacidade (T-01, analítico↔DES).
    - Estrutura a rastreabilidade simulado↔real (Living Lab): status [A VERIFICAR].
    """
    if not cfgs:
        raise ValueError("Nenhum cenário fornecido para o protocolo de validação.")

    rel = RelatorioValidacao()
    rel.parametros = {
        "n_cenarios": len(cfgs),
        "replicas_referencia": cfgs[0].replicas_referencia,
        "desvio_capacidade_max_pct": cfgs[0].desvio_capacidade_max_pct,
        "atraso_aceitavel_min": cfgs[0].atraso_aceitavel_min,
        "seed": cfgs[0].seed,
        "nota": "Limiares [A DEFINIR]; placeholders. Validação principal = simulação.",
    }

    # execução parametrizada por cenário
    for cfg in cfgs:
        res = pipe.executar(cfg)
        rel.cenarios.append(
            {
                "cenario": cfg.nome,
                "aceito": res.aceito,
                "taxa_atendimento": res.rede["taxa_atendimento_agregada"],
                "atraso_medio_min": res.rede["atraso_medio_agregado_min"],
                "restricao_limitante": res.restricao_limitante,
                "gargalos": res.rede["gargalos"],
            }
        )

    # comparação com referência (T-01) por vertiporto do primeiro cenário
    for vid, vp in cfgs[0].vertiportos.items():
        vr = validar_capacidade(
            vp,
            atraso_aceitavel_min=cfgs[0].atraso_aceitavel_min,
            desvio_max_pct=cfgs[0].desvio_capacidade_max_pct,
            replicas=cfgs[0].replicas_referencia,
            seed=cfgs[0].seed,
        )
        rel.validacao_capacidade.append(vr.to_dict())

    # rastreabilidade simulado ↔ real (Living Lab)
    rel.rastreabilidade_living_lab = {
        "living_lab": "Sapiens Parque",
        "disponibilidade_dados_reais": "DISPONIVEL" if living_lab_disponivel else "A_VERIFICAR",
        "papel": "validacao_complementar",
        "nota": (
            "Se indisponível, a validação principal por simulação sustenta a tese "
            "(spec §12). Mapeamento cenário simulado ↔ real a preencher quando houver dados."
        ),
        "mapeamento_cenarios": [
            {"cenario_simulado": c.nome, "cenario_real_correspondente": None}
            for c in cfgs
        ],
    }
    return rel
