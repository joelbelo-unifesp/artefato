"""Testes do Modelo B — Agendamento (RF-02), teste T-02."""

import time

from figov.io.demanda_gen import gerar_demanda
from figov.models import agendamento as ag


def _vp(vid, fatos=2, stands=6):
    return {
        "id": vid,
        "fatos": fatos,
        "stands": stands,
        "tempo_ocupacao_fato_min": 3.0,
        "turnaround_min": 10.0,
    }


def _frota(n, **kw):
    base = {
        "tipo": "eVTOL-4pax",
        "quantidade": n,
        "autonomia_min": 30.0,
        "soc_inicial": 1.0,
        "soc_minimo": 0.2,
        "taxa_recarga_pct_min": 2.0,
        "assentos": 4,
        "consumo_pct_min": 3.0,
    }
    base.update(kw)
    return {"aeronaves": [base]}


def test_agenda_factivel_gera_alocacoes():
    vps = {"VPA": _vp("VPA"), "VPB": _vp("VPB")}
    dem = gerar_demanda(["VPA", "VPB"], seed=42, n_movimentos=100)
    res = ag.agendar(dem, _frota(12), vps, atraso_aceitavel_min=5.0)
    assert res.n_total == 100
    assert len(res.alocacoes) > 0
    # atraso de toda alocação respeita o limiar
    assert all(a.atraso_min <= 5.0 + 1e-6 for a in res.alocacoes)


def test_toda_rejeicao_indica_restricao():
    """Tarefa 2.4 / critério RF-02: agenda rejeitada indica a restrição violada."""
    vps = {"VPA": _vp("VPA"), "VPB": _vp("VPB")}
    dem = gerar_demanda(["VPA", "VPB"], seed=7, n_movimentos=300)
    res = ag.agendar(dem, _frota(4), vps, atraso_aceitavel_min=5.0)
    assert len(res.rejeicoes) > 0
    for r in res.rejeicoes:
        assert r.restricao in ag.Restricao
        assert r.detalhe  # mensagem não-vazia


def test_restricao_energia_sem_recarga():
    """Sem tempo de recarga suficiente e consumo alto, a energia limita a operação."""
    vps = {"VPA": _vp("VPA"), "VPB": _vp("VPB")}
    dem = gerar_demanda(["VPA", "VPB"], seed=1, n_movimentos=120)
    # consumo alto, recarga lenta → deve haver rejeições por energia
    res = ag.agendar(dem, _frota(4, consumo_pct_min=9.0, taxa_recarga_pct_min=0.2),
                     vps, atraso_aceitavel_min=5.0)
    cont = res._contar_rejeicoes()
    assert cont.get(ag.Restricao.ENERGIA.value, 0) > 0


def test_soc_nunca_abaixo_do_minimo_nas_alocacoes():
    """Modelo C: nenhuma alocação parte com SoC que viole o SoC mínimo na chegada."""
    vps = {"VPA": _vp("VPA"), "VPB": _vp("VPB")}
    dem = gerar_demanda(["VPA", "VPB"], seed=5, n_movimentos=150)
    res = ag.agendar(dem, _frota(10), vps, atraso_aceitavel_min=5.0)
    for a in res.alocacoes:
        assert a.soc_chegada >= 0.2 - 1e-6


def test_mais_aeronaves_maior_atendimento():
    """Monotonicidade: frota maior → atendimento >= frota menor."""
    vps = {"VPA": _vp("VPA"), "VPB": _vp("VPB")}
    dem = gerar_demanda(["VPA", "VPB"], seed=3, n_movimentos=400)
    r_pequena = ag.agendar(dem, _frota(6), vps, atraso_aceitavel_min=5.0)
    r_grande = ag.agendar(dem, _frota(18), vps, atraso_aceitavel_min=5.0)
    assert r_grande.taxa_atendimento >= r_pequena.taxa_atendimento


def test_desempenho_dia_completo_sob_60s():
    """Tarefa 2.5: ~2800 pax/dia agendados em muito menos de 60 s."""
    vps = {f"VP{i}": _vp(f"VP{i}") for i in range(4)}
    dem = gerar_demanda(list(vps.keys()), seed=42, n_movimentos=1120, max_pax=4)
    t0 = time.time()
    res = ag.agendar(dem, _frota(20), vps, atraso_aceitavel_min=5.0)
    dt = time.time() - t0
    assert res.n_total == 1120
    assert dt < 60.0


def test_reprodutibilidade_mesma_seed():
    """RNF-01: mesma entrada → mesma saída."""
    vps = {"VPA": _vp("VPA"), "VPB": _vp("VPB")}
    dem = gerar_demanda(["VPA", "VPB"], seed=99, n_movimentos=100)
    r1 = ag.agendar(dem, _frota(10), vps, atraso_aceitavel_min=5.0)
    r2 = ag.agendar(dem, _frota(10), vps, atraso_aceitavel_min=5.0)
    assert r1.to_dict() == r2.to_dict()
