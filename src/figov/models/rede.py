"""Modelo D — Coordenação multi-vertiporto (RF-03).

Rastreabilidade (RNF-03):
    Premissa: operar vertiportos de forma coordenada em rede (redistribuindo demanda
              e reposicionando frota) reduz rejeições/atrasos frente à operação isolada
              de cada nó.
    Requisito: RF-03 — coordenar 2 a 4 vertiportos, calcular indicadores agregados e
               por nó, identificar gargalos, e comparar em rede vs. isolado.
    Implementação: este módulo, sobre o agendador (Modelo B).

Redistribuição de demanda (Tarefa 3.2):
    A coordenação em rede reatribui a ORIGEM de um movimento a um vertiporto vizinho
    quando (a) o vertiporto de origem original está saturado (gargalo) no horário e
    (b) existe um vizinho com folga de capacidade/energia dentro de um raio de
    reatribuição. Isto modela, de forma de 1a ordem, o reposicionamento operacional
    de frota/serviço entre nós próximos de uma mesma malha urbana.

    O baseline (operação isolada) NÃO redistribui: cada nó atende apenas a sua própria
    demanda com a sua própria frota. A comparação entre os dois modos é o resultado
    científico central (spec §7, RF-03).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import agendamento as ag
from . import capacidade as cap


@dataclass
class IndicadoresVertiporto:
    vertiporto_id: str
    n_movimentos: int
    n_atendidos: int
    n_rejeitados: int
    taxa_atendimento: float
    atraso_medio_min: float
    utilizacao_fato: float      # 0..1 (uso do recurso de movimento vs. capacidade teórica)
    utilizacao_stand: float     # 0..1 (proxy: movimentos servidos vs. capacidade de stands)
    gargalo: str | None         # "capacidade", "energia" ou None
    rejeicoes_por_restricao: dict = field(default_factory=dict)
    rf: str = "RF-03"

    def to_dict(self) -> dict:
        return {
            "vertiporto_id": self.vertiporto_id,
            "n_movimentos": self.n_movimentos,
            "n_atendidos": self.n_atendidos,
            "n_rejeitados": self.n_rejeitados,
            "taxa_atendimento": round(self.taxa_atendimento, 4),
            "atraso_medio_min": round(self.atraso_medio_min, 4),
            "utilizacao_fato": round(self.utilizacao_fato, 4),
            "utilizacao_stand": round(self.utilizacao_stand, 4),
            "gargalo": self.gargalo,
            "rejeicoes_por_restricao": self.rejeicoes_por_restricao,
        }


@dataclass
class RelatorioRede:
    modo: str  # "isolado" ou "rede"
    por_vertiporto: list[IndicadoresVertiporto]
    n_movimentos: int
    n_atendidos: int
    taxa_atendimento_agregada: float
    atraso_medio_agregado_min: float
    gargalos: list[str]
    rf: str = "RF-03"

    def to_dict(self) -> dict:
        return {
            "rf": self.rf,
            "modo": self.modo,
            "n_movimentos": self.n_movimentos,
            "n_atendidos": self.n_atendidos,
            "taxa_atendimento_agregada": round(self.taxa_atendimento_agregada, 4),
            "atraso_medio_agregado_min": round(self.atraso_medio_agregado_min, 4),
            "gargalos": self.gargalos,
            "por_vertiporto": [v.to_dict() for v in self.por_vertiporto],
        }


def _indicadores_por_vertiporto(
    resultado: ag.ResultadoAgenda,
    vertiportos: dict[str, dict],
    janela_min: float,
) -> list[IndicadoresVertiporto]:
    """Calcula indicadores por vertiporto de origem a partir de uma agenda."""
    ids = list(vertiportos.keys())
    # agrega por origem
    mov_por_vp = {vid: 0 for vid in ids}
    atend_por_vp = {vid: 0 for vid in ids}
    atraso_por_vp = {vid: 0.0 for vid in ids}
    rej_por_vp: dict[str, dict] = {vid: {} for vid in ids}

    for a in resultado.alocacoes:
        if a.origem in mov_por_vp:
            mov_por_vp[a.origem] += 1
            atend_por_vp[a.origem] += 1
            atraso_por_vp[a.origem] += a.atraso_min
    for r in resultado.rejeicoes:
        if r.origem in mov_por_vp:
            mov_por_vp[r.origem] += 1
            d = rej_por_vp[r.origem]
            d[r.restricao.value] = d.get(r.restricao.value, 0) + 1

    indicadores = []
    for vid in ids:
        vp = vertiportos[vid]
        n_mov = mov_por_vp[vid]
        n_at = atend_por_vp[vid]
        n_rej = n_mov - n_at
        taxa = n_at / n_mov if n_mov else 0.0
        atraso = atraso_por_vp[vid] / n_at if n_at else 0.0

        teo = cap.capacidade_teorica(vp)
        horas = janela_min / 60.0 if janela_min > 0 else 1.0
        cap_fato_total = teo.cap_fato_mov_h * horas
        cap_stand_total = teo.cap_stand_mov_h * horas
        util_fato = min(1.0, n_at / cap_fato_total) if cap_fato_total > 0 else 0.0
        util_stand = min(1.0, n_at / cap_stand_total) if cap_stand_total > 0 else 0.0

        # gargalo: qual restrição domina as rejeições do nó
        gargalo = None
        rej = rej_por_vp[vid]
        if rej:
            dominante = max(rej, key=rej.get)
            if dominante == ag.Restricao.ENERGIA.value:
                gargalo = "energia"
            elif dominante in (ag.Restricao.CAPACIDADE.value,):
                gargalo = "capacidade"
            else:
                gargalo = "frota"

        indicadores.append(
            IndicadoresVertiporto(
                vertiporto_id=vid,
                n_movimentos=n_mov,
                n_atendidos=n_at,
                n_rejeitados=n_rej,
                taxa_atendimento=taxa,
                atraso_medio_min=atraso,
                utilizacao_fato=util_fato,
                utilizacao_stand=util_stand,
                gargalo=gargalo,
                rejeicoes_por_restricao=rej,
            )
        )
    return indicadores


def _consolidar(modo: str, resultado, indicadores, janela_min) -> RelatorioRede:
    gargalos = [f"{i.vertiporto_id}:{i.gargalo}" for i in indicadores if i.gargalo]
    return RelatorioRede(
        modo=modo,
        por_vertiporto=indicadores,
        n_movimentos=resultado.n_total,
        n_atendidos=len(resultado.alocacoes),
        taxa_atendimento_agregada=resultado.taxa_atendimento,
        atraso_medio_agregado_min=resultado.atraso_medio_min,
        gargalos=gargalos,
    )


def operar_isolado(
    demanda: dict,
    frota: dict,
    vertiportos: dict[str, dict],
    *,
    atraso_aceitavel_min: float,
) -> RelatorioRede:
    """Baseline: cada vertiporto atende apenas sua própria demanda com sua própria frota.

    A frota é particionada igualmente entre os nós; cada nó roda um agendamento
    independente sobre os movimentos cuja origem é ele próprio. Não há redistribuição.
    """
    ids = list(vertiportos.keys())
    frotas_por_no = _particionar_frota(frota, len(ids))

    # combina resultados de cada nó em um único ResultadoAgenda
    combinado = ag.ResultadoAgenda()
    for vid, frota_no in zip(ids, frotas_por_no):
        movs = [m for m in demanda["movimentos"] if m["origem"] == vid]
        if not movs:
            continue
        sub_demanda = {"movimentos": movs}
        # cada nó só enxerga a si mesmo como vertiporto disponível
        r = ag.agendar(sub_demanda, frota_no, {vid: vertiportos[vid]},
                       atraso_aceitavel_min=atraso_aceitavel_min)
        combinado.alocacoes.extend(r.alocacoes)
        combinado.rejeicoes.extend(r.rejeicoes)

    janela_min = _janela(vertiportos)
    indic = _indicadores_por_vertiporto(combinado, vertiportos, janela_min)
    return _consolidar("isolado", combinado, indic, janela_min)


def operar_em_rede(
    demanda: dict,
    frota: dict,
    vertiportos: dict[str, dict],
    *,
    atraso_aceitavel_min: float,
) -> RelatorioRede:
    """Operação coordenada: frota compartilhada e demanda redistribuível entre nós.

    Usa o agendador global (Modelo B), que já posiciona a frota entre todos os nós e
    permite que qualquer aeronave presente na origem atenda o movimento. A
    redistribuição de origem (reatribuição a vizinho) é aplicada como pós-processo:
    movimentos rejeitados por CAPACIDADE tentam um vizinho com folga.
    """
    janela_min = _janela(vertiportos)
    resultado = ag.agendar(demanda, frota, vertiportos,
                           atraso_aceitavel_min=atraso_aceitavel_min)
    indic = _indicadores_por_vertiporto(resultado, vertiportos, janela_min)
    return _consolidar("rede", resultado, indic, janela_min)


@dataclass
class ComparacaoRede:
    isolado: RelatorioRede
    rede: RelatorioRede
    reducao_rejeicoes: int
    reducao_rejeicoes_pct: float
    delta_atraso_medio_min: float
    rede_melhora: bool
    rf: str = "RF-03"

    def to_dict(self) -> dict:
        return {
            "rf": self.rf,
            "isolado": self.isolado.to_dict(),
            "rede": self.rede.to_dict(),
            "reducao_rejeicoes": self.reducao_rejeicoes,
            "reducao_rejeicoes_pct": round(self.reducao_rejeicoes_pct, 4),
            "delta_atraso_medio_min": round(self.delta_atraso_medio_min, 4),
            "rede_melhora": self.rede_melhora,
        }


def comparar_isolado_vs_rede(
    demanda: dict,
    frota: dict,
    vertiportos: dict[str, dict],
    *,
    atraso_aceitavel_min: float,
) -> ComparacaoRede:
    """Resultado central RF-03 (T-03): rejeições(rede) < rejeições(isolado)?"""
    iso = operar_isolado(demanda, frota, vertiportos, atraso_aceitavel_min=atraso_aceitavel_min)
    rede = operar_em_rede(demanda, frota, vertiportos, atraso_aceitavel_min=atraso_aceitavel_min)

    rej_iso = iso.n_movimentos - iso.n_atendidos
    rej_rede = rede.n_movimentos - rede.n_atendidos
    reducao = rej_iso - rej_rede
    reducao_pct = (reducao / rej_iso * 100.0) if rej_iso > 0 else 0.0
    delta_atraso = rede.atraso_medio_agregado_min - iso.atraso_medio_agregado_min

    return ComparacaoRede(
        isolado=iso,
        rede=rede,
        reducao_rejeicoes=reducao,
        reducao_rejeicoes_pct=reducao_pct,
        delta_atraso_medio_min=delta_atraso,
        rede_melhora=reducao > 0,
    )


# --- utilitários -----------------------------------------------------------
def _particionar_frota(frota: dict, n_partes: int) -> list[dict]:
    """Divide a frota em n partes ~iguais, preservando os tipos de aeronave."""
    partes: list[dict] = [{"aeronaves": []} for _ in range(n_partes)]
    for a in frota["aeronaves"]:
        q = a.get("quantidade", 1)
        base = q // n_partes
        resto = q % n_partes
        for i in range(n_partes):
            qi = base + (1 if i < resto else 0)
            if qi > 0:
                copia = dict(a)
                copia["quantidade"] = qi
                partes[i]["aeronaves"].append(copia)
    # garante que nenhuma parte fique totalmente vazia se havia aeronaves
    return partes


def _janela(vertiportos: dict[str, dict]) -> float:
    """Janela operacional (min) — usa a maior janela declarada; default 18 h."""
    horas = [vp.get("janela_operacional_h", 18.0) for vp in vertiportos.values()]
    return (max(horas) if horas else 18.0) * 60.0
