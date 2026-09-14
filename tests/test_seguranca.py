"""Testes do Modelo E — Segurança (RF-04), teste T-04."""

from figov.io.demanda_gen import gerar_demanda
from figov.models import agendamento as ag
from figov.models import seguranca as seg


def _vp(vid):
    return {"id": vid, "fatos": 2, "stands": 6,
            "tempo_ocupacao_fato_min": 3.0, "turnaround_min": 10.0}


def _frota(n):
    return {"aeronaves": [{"tipo": "e4", "quantidade": n, "autonomia_min": 30.0,
                           "soc_inicial": 1.0, "soc_minimo": 0.2,
                           "taxa_recarga_pct_min": 2.0, "assentos": 4,
                           "consumo_pct_min": 3.0}]}


def _agenda():
    vps = {"VPA": _vp("VPA"), "VPB": _vp("VPB")}
    dem = gerar_demanda(["VPA", "VPB"], seed=42, n_movimentos=200)
    return ag.agendar(dem, _frota(12), vps, atraso_aceitavel_min=5.0)


def test_aprova_quando_risco_abaixo_do_alvo():
    res = _agenda()
    seguranca = {"nivel_alvo_risco": 1e-4, "risco_por_movimento": 1e-9,
                 "sitios_contingencia": [{"id": "C1", "lat": 0.0, "lon": 0.0}]}
    ok, rel = seg.aplicar_guardrail(res, seguranca, janela_min=18 * 60)
    assert ok
    assert rel.violacoes == []


def test_rejeita_quando_risco_excede_alvo():
    """T-04: plano que viola o nível alvo é automaticamente rejeitado."""
    res = _agenda()
    seguranca = {"nivel_alvo_risco": 1e-12, "risco_por_movimento": 1e-6,
                 "sitios_contingencia": [{"id": "C1", "lat": 0.0, "lon": 0.0}]}
    ok, rel = seg.aplicar_guardrail(res, seguranca, janela_min=18 * 60)
    assert not ok
    tipos = [v["tipo"] for v in rel.violacoes]
    assert seg.ViolacaoSeguranca.RISCO_EXCEDE_ALVO.value in tipos


def test_rejeita_sem_sitio_de_contingencia():
    """RF-04: sítios de contingência são obrigatórios."""
    res = _agenda()
    seguranca = {"nivel_alvo_risco": 1e-4, "risco_por_movimento": 1e-9,
                 "sitios_contingencia": []}
    ok, rel = seg.aplicar_guardrail(res, seguranca, janela_min=18 * 60)
    assert not ok
    tipos = [v["tipo"] for v in rel.violacoes]
    assert seg.ViolacaoSeguranca.SEM_CONTINGENCIA.value in tipos


def test_violacao_tem_indicacao_explicita():
    """RF-04: rejeição deve indicar explicitamente a violação (detalhe não-vazio)."""
    res = _agenda()
    seguranca = {"nivel_alvo_risco": 1e-12, "risco_por_movimento": 1e-6,
                 "sitios_contingencia": []}
    _ok, rel = seg.aplicar_guardrail(res, seguranca, janela_min=18 * 60)
    assert len(rel.violacoes) >= 1
    for v in rel.violacoes:
        assert "tipo" in v and "detalhe" in v and v["detalhe"]
