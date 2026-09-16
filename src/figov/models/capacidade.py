"""Modelo A — Capacidade do vertiporto (RF-01).

Rastreabilidade (RNF-03):
    Premissa: a capacidade de um vertiporto é limitada pelo recurso mais restritivo
              entre áreas de pouso/decolagem (FATO/TLOF) e posições de estacionamento
              (stands), dados os tempos de ocupação e de turnaround.
    Requisito: RF-01 — determinar capacidade teórica e prática.
    Implementação: este módulo (analítico) + simulação de eventos discretos de
                   referência para verificação (T-01).

Definições:
- Capacidade teórica (movimentos/hora): limite superior imposto pelo recurso gargalo,
  assumindo utilização ideal (sem filas).
      cap_fato   = 60 / tempo_ocupacao_fato_min * n_fatos
      cap_stand  = 60 / turnaround_min          * n_stands   (movimentos servidos por stand)
      cap_teorica = min(cap_fato, cap_stand)
- Nível de serviço: atraso médio por movimento, estimado por fila M/M/c sobre o
  recurso gargalo, dada uma taxa de chegada (demanda).
- Capacidade prática: maior taxa de chegada cuja espera média (Wq) <= atraso
  aceitável `y` (parâmetro [A DEFINIR], config/cenario.json).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


# --------------------------------------------------------------------------
# Capacidade teórica
# --------------------------------------------------------------------------
@dataclass
class CapacidadeTeorica:
    cap_fato_mov_h: float
    cap_stand_mov_h: float
    cap_teorica_mov_h: float
    recurso_gargalo: str  # "fato" ou "stand"
    rf: str = "RF-01"


def capacidade_teorica(vertiporto: dict) -> CapacidadeTeorica:
    """Capacidade teórica (movimentos/hora) do vertiporto."""
    n_fatos = vertiporto["fatos"]
    n_stands = vertiporto["stands"]
    t_ocup = vertiporto["tempo_ocupacao_fato_min"]
    t_turn = vertiporto["turnaround_min"]

    cap_fato = (60.0 / t_ocup) * n_fatos if t_ocup > 0 else math.inf
    cap_stand = (60.0 / t_turn) * n_stands if t_turn > 0 else math.inf

    if cap_fato <= cap_stand:
        gargalo = "fato"
        cap = cap_fato
    else:
        gargalo = "stand"
        cap = cap_stand

    return CapacidadeTeorica(
        cap_fato_mov_h=round(cap_fato, 4),
        cap_stand_mov_h=round(cap_stand, 4),
        cap_teorica_mov_h=round(cap, 4),
        recurso_gargalo=gargalo,
    )


# --------------------------------------------------------------------------
# Fila M/M/c — nível de serviço (atraso médio)
# --------------------------------------------------------------------------
def _erlang_c(c: int, a: float) -> float:
    """Probabilidade de espera (fórmula C de Erlang). a = lambda/mu (Erlangs)."""
    if a <= 0:
        return 0.0
    rho = a / c
    if rho >= 1.0:
        return 1.0  # sistema saturado
    # soma dos termos a^n/n!
    soma = sum(a ** n / math.factorial(n) for n in range(c))
    ultimo = a ** c / math.factorial(c) * (1.0 / (1.0 - rho))
    return ultimo / (soma + ultimo)


def espera_media_min(taxa_chegada_h: float, vertiporto: dict) -> float:
    """Espera média na fila Wq (minutos) para o recurso gargalo, via M/M/c.

    - c = número de servidores do recurso gargalo (fatos ou stands).
    - mu = 60 / tempo de serviço (movimentos/hora por servidor).
    - lambda = taxa de chegada (movimentos/hora).
    Retorna infinito se o sistema estiver saturado (rho >= 1).
    """
    teo = capacidade_teorica(vertiporto)
    if teo.recurso_gargalo == "fato":
        c = vertiporto["fatos"]
        tempo_servico_min = vertiporto["tempo_ocupacao_fato_min"]
    else:
        c = vertiporto["stands"]
        tempo_servico_min = vertiporto["turnaround_min"]

    if tempo_servico_min <= 0:
        return 0.0

    mu = 60.0 / tempo_servico_min          # mov/hora por servidor
    a = taxa_chegada_h / mu                  # Erlangs
    rho = a / c
    if rho >= 1.0:
        return math.inf

    pw = _erlang_c(c, a)
    # Wq = Pw / (c*mu - lambda), em horas → converte para minutos
    wq_h = pw / (c * mu - taxa_chegada_h)
    return wq_h * 60.0


# --------------------------------------------------------------------------
# Capacidade prática — por atraso aceitável (y minutos, [A DEFINIR])
# --------------------------------------------------------------------------
@dataclass
class CapacidadePratica:
    cap_pratica_mov_h: float
    atraso_aceitavel_min: float
    atraso_no_ponto_min: float
    rf: str = "RF-01"


def capacidade_pratica(
    vertiporto: dict, atraso_aceitavel_min: float, *, passo: float = 0.5
) -> CapacidadePratica:
    """Maior taxa de chegada (mov/h) cuja espera média <= atraso aceitável.

    Busca incremental da taxa de chegada até a espera média M/M/c exceder o
    limiar `y`. O limiar é parâmetro de cenário [A DEFINIR].
    """
    teo = capacidade_teorica(vertiporto)
    limite = teo.cap_teorica_mov_h
    melhor = 0.0
    atraso_melhor = 0.0
    taxa = passo
    while taxa < limite:
        wq = espera_media_min(taxa, vertiporto)
        if wq <= atraso_aceitavel_min:
            melhor = taxa
            atraso_melhor = wq
            taxa += passo
        else:
            break
    return CapacidadePratica(
        cap_pratica_mov_h=round(melhor, 4),
        atraso_aceitavel_min=atraso_aceitavel_min,
        atraso_no_ponto_min=round(atraso_melhor, 4),
    )


# --------------------------------------------------------------------------
# Simulação de eventos discretos (DES) de referência — T-01
# --------------------------------------------------------------------------
@dataclass
class ResultadoDES:
    taxa_chegada_h: float
    espera_media_min: float
    n_atendidos: int
    replicas: int
    rf: str = "RF-01"


def _simular_uma_replica(
    taxa_chegada_h: float, vertiporto: dict, horas: float, seed: int
) -> tuple[float, int]:
    """Uma réplica de DES de fila multi-servidor (recurso gargalo)."""
    import random

    rng = random.Random(seed)
    teo = capacidade_teorica(vertiporto)
    if teo.recurso_gargalo == "fato":
        c = vertiporto["fatos"]
        tempo_servico_min = vertiporto["tempo_ocupacao_fato_min"]
    else:
        c = vertiporto["stands"]
        tempo_servico_min = vertiporto["turnaround_min"]

    lam_por_min = taxa_chegada_h / 60.0
    fim = horas * 60.0

    # Gera chegadas por processo de Poisson (exponencial entre chegadas).
    chegadas = []
    t = 0.0
    while True:
        if lam_por_min <= 0:
            break
        t += rng.expovariate(lam_por_min)
        if t > fim:
            break
        chegadas.append(t)

    # c servidores; cada um livre a partir de um instante. Serviço ~ exponencial(média).
    livre_em = [0.0] * c
    esperas = []
    for chegada in chegadas:
        # escolhe o servidor que fica livre mais cedo
        idx = min(range(c), key=lambda i: livre_em[i])
        inicio = max(chegada, livre_em[idx])
        espera = inicio - chegada
        esperas.append(espera)
        servico = rng.expovariate(1.0 / tempo_servico_min) if tempo_servico_min > 0 else 0.0
        livre_em[idx] = inicio + servico

    media = sum(esperas) / len(esperas) if esperas else 0.0
    return media, len(esperas)


def simular_des_referencia(
    taxa_chegada_h: float,
    vertiporto: dict,
    *,
    horas: float = 200.0,
    replicas: int = 10,
    seed: int = 0,
) -> ResultadoDES:
    """Média de `replicas` réplicas da DES (default 10, conforme Tarefa 1.5).

    O horizonte default (200 h) é longo o suficiente para diluir o transiente de
    aquecimento da fila e permitir que a estimativa de espera média convirja para o
    regime estacionário — condição necessária para uma comparação justa com o modelo
    analítico M/M/c no teste T-01. Horizontes curtos (p.ex. 8 h) subestimam a espera.
    """
    esperas = []
    total = 0
    for r in range(replicas):
        media, n = _simular_uma_replica(taxa_chegada_h, vertiporto, horas, seed + r)
        esperas.append(media)
        total += n
    media_geral = sum(esperas) / len(esperas) if esperas else 0.0
    return ResultadoDES(
        taxa_chegada_h=taxa_chegada_h,
        espera_media_min=round(media_geral, 4),
        n_atendidos=total,
        replicas=replicas,
    )


# --------------------------------------------------------------------------
# Relatório consolidado de capacidade
# --------------------------------------------------------------------------
@dataclass
class RelatorioCapacidade:
    vertiporto_id: str
    teorica: CapacidadeTeorica
    pratica: CapacidadePratica
    des_ref: ResultadoDES
    desvio_vs_des_pct: float
    desvio_max_aceitavel_pct: float
    aprovado: bool
    rf: str = "RF-01"
    avisos: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "rf": self.rf,
            "vertiporto_id": self.vertiporto_id,
            "capacidade_teorica_mov_h": self.teorica.cap_teorica_mov_h,
            "recurso_gargalo": self.teorica.recurso_gargalo,
            "cap_fato_mov_h": self.teorica.cap_fato_mov_h,
            "cap_stand_mov_h": self.teorica.cap_stand_mov_h,
            "capacidade_pratica_mov_h": self.pratica.cap_pratica_mov_h,
            "atraso_aceitavel_min": self.pratica.atraso_aceitavel_min,
            "des_espera_media_min": self.des_ref.espera_media_min,
            "des_replicas": self.des_ref.replicas,
            "desvio_vs_des_pct": self.desvio_vs_des_pct,
            "desvio_max_aceitavel_pct": self.desvio_max_aceitavel_pct,
            "aprovado_RF01": self.aprovado,
            "avisos": self.avisos,
        }


def avaliar_capacidade(
    vertiporto: dict,
    *,
    atraso_aceitavel_min: float,
    desvio_max_pct: float,
    replicas: int = 10,
    seed: int = 0,
) -> RelatorioCapacidade:
    """Consolida RF-01: teórica, prática, e comparação analítico vs. DES (T-01).

    O critério de aceitação (desvio <= x%) usa x = `desvio_max_pct`, parâmetro de
    cenário [A DEFINIR]. Comparamos a espera média analítica (M/M/c) com a da DES
    de referência, no ponto de operação = capacidade prática.
    """
    teo = capacidade_teorica(vertiporto)
    prat = capacidade_pratica(vertiporto, atraso_aceitavel_min)

    # Ponto de operação para a comparação: a capacidade prática encontrada.
    taxa_op = prat.cap_pratica_mov_h if prat.cap_pratica_mov_h > 0 else teo.cap_teorica_mov_h * 0.5
    wq_analitico = espera_media_min(taxa_op, vertiporto)
    des = simular_des_referencia(taxa_op, vertiporto, replicas=replicas, seed=seed)

    avisos: list[str] = []
    if des.espera_media_min <= 0:
        # evita divisão por zero: sem espera na referência
        desvio = 0.0 if wq_analitico <= 1e-9 else 100.0
        if wq_analitico > 1e-9:
            avisos.append("DES de referência sem espera no ponto de operação; desvio marcado como 100%.")
    else:
        desvio = abs(wq_analitico - des.espera_media_min) / des.espera_media_min * 100.0

    aprovado = desvio <= desvio_max_pct
    avisos.append(
        "x% (desvio_capacidade_max_pct) e y min (atraso_aceitavel_min) são parâmetros "
        "[A DEFINIR] — placeholders, não ancorados em literatura."
    )

    return RelatorioCapacidade(
        vertiporto_id=vertiporto.get("id", "?"),
        teorica=teo,
        pratica=prat,
        des_ref=des,
        desvio_vs_des_pct=round(desvio, 4),
        desvio_max_aceitavel_pct=desvio_max_pct,
        aprovado=aprovado,
        avisos=avisos,
    )
