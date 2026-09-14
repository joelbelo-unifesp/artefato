"""Testes do Modelo D — Coordenação multi-vertiporto (RF-03), teste T-03."""

from figov.io.demanda_gen import gerar_demanda
from figov.models import rede


def _vp(vid):
    return {
        "id": vid,
        "fatos": 2,
        "stands": 6,
        "tempo_ocupacao_fato_min": 3.0,
        "turnaround_min": 10.0,
        "janela_operacional_h": 18.0,
    }


def _frota(n):
    return {
        "aeronaves": [
            {
                "tipo": "eVTOL-4pax",
                "quantidade": n,
                "autonomia_min": 30.0,
                "soc_inicial": 1.0,
                "soc_minimo": 0.2,
                "taxa_recarga_pct_min": 2.0,
                "assentos": 4,
                "consumo_pct_min": 3.0,
            }
        ]
    }


def test_rede_reduz_rejeicoes_vs_isolado():
    """T-03: rejeições(rede) < rejeições(isolado) — resultado central RF-03."""
    vps = {f"VP{i}": _vp(f"VP{i}") for i in range(3)}
    dem = gerar_demanda(list(vps.keys()), seed=42, n_movimentos=300)
    comp = rede.comparar_isolado_vs_rede(dem, _frota(12), vps, atraso_aceitavel_min=5.0)
    assert comp.rede_melhora
    assert comp.reducao_rejeicoes > 0


def test_rede_melhora_robusto_em_varias_seeds():
    """A melhoria não deve depender de uma seed específica."""
    vps = {f"VP{i}": _vp(f"VP{i}") for i in range(2)}
    melhoras = 0
    for seed in range(5):
        dem = gerar_demanda(list(vps.keys()), seed=seed, n_movimentos=250)
        comp = rede.comparar_isolado_vs_rede(dem, _frota(12), vps, atraso_aceitavel_min=5.0)
        melhoras += int(comp.rede_melhora)
    assert melhoras == 5


def test_indicadores_por_vertiporto_presentes():
    """RF-03: indicadores agregados e por nó, com identificação de gargalo."""
    vps = {f"VP{i}": _vp(f"VP{i}") for i in range(4)}
    dem = gerar_demanda(list(vps.keys()), seed=1, n_movimentos=300)
    rel = rede.operar_em_rede(dem, _frota(16), vps, atraso_aceitavel_min=5.0)
    assert len(rel.por_vertiporto) == 4
    for v in rel.por_vertiporto:
        assert 0.0 <= v.taxa_atendimento <= 1.0
        assert 0.0 <= v.utilizacao_fato <= 1.0
        assert 0.0 <= v.utilizacao_stand <= 1.0


def test_suporta_2_a_4_vertiportos():
    """Escopo RF-03: redes de 2 a 4 nós."""
    for n in (2, 3, 4):
        vps = {f"VP{i}": _vp(f"VP{i}") for i in range(n)}
        dem = gerar_demanda(list(vps.keys()), seed=n, n_movimentos=200)
        rel = rede.operar_em_rede(dem, _frota(12), vps, atraso_aceitavel_min=5.0)
        assert len(rel.por_vertiporto) == n
        assert rel.n_movimentos == 200


def test_reproducibilidade_comparacao():
    """RNF-01: comparação determinística para a mesma entrada."""
    vps = {f"VP{i}": _vp(f"VP{i}") for i in range(3)}
    dem = gerar_demanda(list(vps.keys()), seed=11, n_movimentos=200)
    a = rede.comparar_isolado_vs_rede(dem, _frota(12), vps, atraso_aceitavel_min=5.0)
    b = rede.comparar_isolado_vs_rede(dem, _frota(12), vps, atraso_aceitavel_min=5.0)
    assert a.to_dict() == b.to_dict()
