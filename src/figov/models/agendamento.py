"""Modelo B — Agendamento de frota heterogênea (RF-02), com energia de 1a ordem (Modelo C).

Rastreabilidade (RNF-03):
    Premissa: uma frota heterogênea de eVTOL atende à demanda de movimentos sujeita a
              (a) capacidade do vertiporto (RF-01) e (b) restrições energéticas — SoC
              mínimo, autonomia e tempo de recarga.
    Requisito: RF-02 — alocar aeronaves, movimentos e slots gerando agenda factível;
               toda agenda/movimento rejeitado deve indicar a restrição violada.
    Implementação: heurística de list-scheduling (greedy) documentada abaixo.

Heurística (documentada — Tarefa 2.3):
    1. Ordena os movimentos por horário desejado (EDF-like).
    2. Para cada movimento, escolhe entre as aeronaves elegíveis a que:
         - esteja disponível (livre) no horário, respeitando separação/turnaround;
         - tenha SoC suficiente para o voo mantendo SoC >= soc_minimo (Modelo C);
         - respeite a capacidade do vertiporto de origem (nº de servidores/slots).
       Critério de escolha: menor atraso; empate → maior SoC (mais folga energética).
    3. Se nenhuma aeronave é elegível, o movimento é REJEITADO com a restrição violada
       (capacidade, energia ou frota) explicitamente registrada.
    4. Após o voo, a aeronave recarrega no destino; o SoC é atualizado pela taxa de
       recarga e pelo tempo disponível até a próxima alocação.

Restrições energéticas de 1a ordem (Modelo C):
    - consumo do voo (pontos % de SoC) = consumo_pct_min * duracao_voo_min
    - SoC após o voo = SoC_partida - consumo/100
    - viabilidade: SoC_partida - consumo/100 >= soc_minimo
    - recarga: SoC += (taxa_recarga_pct_min * tempo_recarga_min)/100, limitado a 1.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Restricao(str, Enum):
    CAPACIDADE = "capacidade_vertiporto"
    ENERGIA = "energia_soc_minimo"
    AUTONOMIA = "autonomia_insuficiente"
    FROTA = "frota_indisponivel"


@dataclass
class Aeronave:
    id: str
    tipo: str
    autonomia_min: float
    soc: float                # estado de carga atual (0..1)
    soc_minimo: float
    taxa_recarga_pct_min: float
    assentos: int
    consumo_pct_min: float
    # estado dinâmico
    local: str = ""           # vertiporto onde está
    livre_em_min: float = 0.0 # instante em que fica livre

    def consumo_voo_frac(self, duracao_voo_min: float) -> float:
        """Fração de SoC consumida por um voo de dada duração."""
        return (self.consumo_pct_min * duracao_voo_min) / 100.0

    def pode_voar(self, duracao_voo_min: float) -> tuple[bool, Restricao | None]:
        if duracao_voo_min > self.autonomia_min:
            return False, Restricao.AUTONOMIA
        if self.soc - self.consumo_voo_frac(duracao_voo_min) < self.soc_minimo - 1e-9:
            return False, Restricao.ENERGIA
        return True, None

    def recarregar(self, tempo_min: float) -> None:
        ganho = (self.taxa_recarga_pct_min * max(0.0, tempo_min)) / 100.0
        self.soc = min(1.0, self.soc + ganho)


def expandir_frota(frota: dict) -> list[Aeronave]:
    """Expande a definição de frota em aeronaves individuais."""
    aeronaves: list[Aeronave] = []
    contador = 0
    for a in frota["aeronaves"]:
        for _ in range(a.get("quantidade", 1)):
            aeronaves.append(
                Aeronave(
                    id=f"{a['tipo']}#{contador}",
                    tipo=a["tipo"],
                    autonomia_min=a["autonomia_min"],
                    soc=a.get("soc_inicial", 1.0),
                    soc_minimo=a.get("soc_minimo", 0.2),
                    taxa_recarga_pct_min=a["taxa_recarga_pct_min"],
                    assentos=a["assentos"],
                    consumo_pct_min=a.get("consumo_pct_min", 3.0),
                )
            )
            contador += 1
    return aeronaves


@dataclass
class Alocacao:
    movimento_idx: int
    aeronave_id: str
    origem: str
    destino: str
    horario_desejado_min: float
    horario_partida_min: float
    atraso_min: float
    duracao_voo_min: float
    soc_partida: float
    soc_chegada: float
    passageiros: int
    rf: str = "RF-02"


@dataclass
class Rejeicao:
    movimento_idx: int
    origem: str
    destino: str
    horario_desejado_min: float
    restricao: Restricao          # restrição violada (Tarefa 2.4)
    detalhe: str
    rf: str = "RF-02"


@dataclass
class ResultadoAgenda:
    alocacoes: list[Alocacao] = field(default_factory=list)
    rejeicoes: list[Rejeicao] = field(default_factory=list)
    rf: str = "RF-02"

    @property
    def n_total(self) -> int:
        return len(self.alocacoes) + len(self.rejeicoes)

    @property
    def taxa_atendimento(self) -> float:
        return len(self.alocacoes) / self.n_total if self.n_total else 0.0

    @property
    def atraso_medio_min(self) -> float:
        if not self.alocacoes:
            return 0.0
        return sum(a.atraso_min for a in self.alocacoes) / len(self.alocacoes)

    @property
    def atraso_max_min(self) -> float:
        return max((a.atraso_min for a in self.alocacoes), default=0.0)

    def to_dict(self) -> dict:
        return {
            "rf": self.rf,
            "n_movimentos": self.n_total,
            "n_atendidos": len(self.alocacoes),
            "n_rejeitados": len(self.rejeicoes),
            "taxa_atendimento": round(self.taxa_atendimento, 4),
            "atraso_medio_min": round(self.atraso_medio_min, 4),
            "atraso_max_min": round(self.atraso_max_min, 4),
            "rejeicoes_por_restricao": self._contar_rejeicoes(),
        }

    def _contar_rejeicoes(self) -> dict:
        cont: dict[str, int] = {}
        for r in self.rejeicoes:
            cont[r.restricao.value] = cont.get(r.restricao.value, 0) + 1
        return cont


def agendar(
    demanda: dict,
    frota: dict,
    vertiportos: dict[str, dict],
    *,
    atraso_aceitavel_min: float,
    separacao_min: float = 1.0,
) -> ResultadoAgenda:
    """Gera e avalia uma agenda por list-scheduling greedy (Tarefa 2.3).

    - demanda: dict com "movimentos".
    - frota: dict de frota (será expandido em aeronaves individuais).
    - vertiportos: mapa id -> config de vertiporto (para capacidade / nº de servidores).
    - atraso_aceitavel_min: y [A DEFINIR]; movimentos além do atraso são REJEITADOS
      por capacidade insuficiente no horário desejado.
    - separacao_min: separação mínima entre movimentos no mesmo servidor.

    Retorna ResultadoAgenda com alocações e rejeições (cada rejeição com a restrição).
    """
    aeronaves = expandir_frota(frota)
    if not aeronaves:
        raise ValueError("Frota vazia.")

    # posiciona a frota inicialmente distribuída pelos vertiportos disponíveis
    ids_vp = list(vertiportos.keys())
    for i, ac in enumerate(aeronaves):
        ac.local = ids_vp[i % len(ids_vp)]

    # servidores por vertiporto = nº de FATO (recurso de movimento). Cada FATO só
    # pode iniciar um movimento a cada (tempo_ocupacao + separacao).
    fato_livre_em: dict[str, list[float]] = {}
    for vid, vp in vertiportos.items():
        fato_livre_em[vid] = [0.0] * vp["fatos"]

    resultado = ResultadoAgenda()
    movimentos = sorted(
        enumerate(demanda["movimentos"]), key=lambda kv: kv[1]["horario_desejado_min"]
    )

    for idx, mov in movimentos:
        origem = mov["origem"]
        destino = mov["destino"]
        t_desejado = mov["horario_desejado_min"]
        dur = mov.get("duracao_voo_min", 0.0)
        pax = mov.get("passageiros", 0)

        vp = vertiportos.get(origem)
        if vp is None:
            resultado.rejeicoes.append(
                Rejeicao(idx, origem, destino, t_desejado, Restricao.CAPACIDADE,
                         f"Vertiporto de origem '{origem}' não configurado.")
            )
            continue

        t_ocup = vp["tempo_ocupacao_fato_min"]

        # 1) primeiro slot de FATO disponível na origem
        fatos = fato_livre_em[origem]
        idx_fato = min(range(len(fatos)), key=lambda i: fatos[i])
        t_slot = max(t_desejado, fatos[idx_fato])
        atraso_capacidade = t_slot - t_desejado
        if atraso_capacidade > atraso_aceitavel_min + 1e-9:
            resultado.rejeicoes.append(
                Rejeicao(idx, origem, destino, t_desejado, Restricao.CAPACIDADE,
                         f"Menor atraso possível {atraso_capacidade:.1f} min > "
                         f"aceitável {atraso_aceitavel_min:.1f} min (FATO ocupado).")
            )
            continue

        # 2) aeronaves elegíveis: no local de origem, livres até t_slot, com energia.
        #    Realimentação Energia↔Agendamento (spec §7): antes de avaliar a energia,
        #    recarrega-se a aeronave pelo tempo ocioso no destino desde que ficou livre
        #    até o instante do slot (recarga de 1a ordem, Modelo C).
        candidatas: list[tuple[float, float, Aeronave]] = []  # (atraso, -soc, ac)
        motivo_energia = False
        motivo_assentos = False
        alguma_no_local = False
        for ac in aeronaves:
            if ac.local != origem:
                continue
            alguma_no_local = True
            if ac.assentos < pax:
                motivo_assentos = True
                continue
            t_partida = max(t_slot, ac.livre_em_min)
            # recarga pelo tempo ocioso disponível até a partida
            tempo_ocioso = max(0.0, t_partida - ac.livre_em_min)
            soc_projetado = min(1.0, ac.soc + (ac.taxa_recarga_pct_min * tempo_ocioso) / 100.0)
            # viabilidade energética com o SoC projetado
            if dur > ac.autonomia_min:
                motivo_energia = True
                continue
            if soc_projetado - ac.consumo_voo_frac(dur) < ac.soc_minimo - 1e-9:
                motivo_energia = True
                continue
            atraso = t_partida - t_desejado
            if atraso > atraso_aceitavel_min + 1e-9:
                continue
            candidatas.append((atraso, -soc_projetado, ac))

        if not candidatas:
            if not alguma_no_local:
                restr, det = Restricao.FROTA, f"Nenhuma aeronave posicionada em '{origem}'."
            elif motivo_energia:
                restr, det = Restricao.ENERGIA, "Aeronaves no local sem SoC suficiente (>= soc_minimo)."
            elif motivo_assentos:
                restr, det = Restricao.FROTA, f"Nenhuma aeronave com assentos >= {pax}."
            else:
                restr, det = Restricao.CAPACIDADE, "Sem aeronave dentro do atraso aceitável."
            resultado.rejeicoes.append(Rejeicao(idx, origem, destino, t_desejado, restr, det))
            continue

        # 3) escolhe: menor atraso, depois maior SoC projetado
        candidatas.sort(key=lambda c: (c[0], c[1]))
        atraso, _neg_soc, ac = candidatas[0]
        t_partida = t_desejado + atraso

        # aplica a recarga pelo tempo ocioso até a partida (consistência de estado)
        tempo_ocioso = max(0.0, t_partida - ac.livre_em_min)
        ac.recarregar(tempo_ocioso)

        soc_partida = ac.soc
        soc_chegada = ac.soc - ac.consumo_voo_frac(dur)

        # atualiza aeronave: consome energia, muda de local, fica livre no destino
        ac.soc = soc_chegada
        ac.local = destino
        ac.livre_em_min = t_partida + dur

        # ocupa o FATO na origem
        fatos[idx_fato] = t_partida + t_ocup + separacao_min

        resultado.alocacoes.append(
            Alocacao(
                movimento_idx=idx,
                aeronave_id=ac.id,
                origem=origem,
                destino=destino,
                horario_desejado_min=t_desejado,
                horario_partida_min=t_partida,
                atraso_min=round(atraso, 4),
                duracao_voo_min=dur,
                soc_partida=round(soc_partida, 4),
                soc_chegada=round(soc_chegada, 4),
                passageiros=pax,
            )
        )

    resultado.alocacoes.sort(key=lambda a: a.horario_partida_min)
    return resultado
