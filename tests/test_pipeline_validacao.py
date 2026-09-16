"""Testes do pipeline (RF-05/RF-07) e do protocolo de validação (RF-05)."""

import copy

from figov.io.demanda_gen import gerar_demanda
from figov import pipeline as pipe
from figov.models import validacao as val


def _vps(n=2):
    return {
        f"VP{i}": {
            "id": f"VP{i}", "fatos": 2, "stands": 6,
            "tempo_ocupacao_fato_min": 3.0, "turnaround_min": 10.0,
            "janela_operacional_h": 18.0,
        }
        for i in range(n)
    }


def _frota(n):
    return {"aeronaves": [{"tipo": "e4", "quantidade": n, "autonomia_min": 30.0,
                           "soc_inicial": 1.0, "soc_minimo": 0.2,
                           "taxa_recarga_pct_min": 2.0, "assentos": 4,
                           "consumo_pct_min": 3.0}]}


def _seg(alvo=1e-4, risco=1e-9):
    return {"nivel_alvo_risco": alvo, "risco_por_movimento": risco,
            "sitios_contingencia": [{"id": "C1", "lat": 0.0, "lon": 0.0}]}


def _cfg(nome, vps, frota, seg):
    dem = gerar_demanda(list(vps.keys()), seed=42, n_movimentos=250)
    return pipe.ConfiguracaoCenario(
        nome=nome, vertiportos=vps, frota=frota, demanda=dem, seguranca=seg,
        atraso_aceitavel_min=5.0, desvio_capacidade_max_pct=10.0,
        replicas_referencia=10, seed=42,
    )


def test_pipeline_executa_e_aceita_com_seguranca_ok():
    vps = _vps(2)
    res = pipe.executar(_cfg("c", vps, _frota(12), _seg()))
    assert res.aceito
    assert res.rede["n_movimentos"] == 250
    assert len(res.capacidade) == 2


def test_pipeline_rejeita_por_seguranca():
    """Guardrail domina: segurança violada → plano não aceito, limitante='seguranca'."""
    vps = _vps(2)
    res = pipe.executar(_cfg("c", vps, _frota(12), _seg(alvo=1e-15, risco=1e-3)))
    assert not res.aceito
    assert res.restricao_limitante == "seguranca"


def test_rf07_compara_pelo_menos_duas_alternativas():
    """RF-07: comparação de >=2 alternativas com indicadores e restrição limitante."""
    vps = _vps(3)
    frota2 = _frota(24)
    comp = pipe.comparar_cenarios([
        _cfg("base", vps, _frota(12), _seg()),
        _cfg("frota_2x", vps, frota2, _seg()),
    ])
    d = comp.to_dict()
    assert len(d["comparacao"]) == 2
    for linha in d["comparacao"]:
        assert "taxa_atendimento" in linha
        assert "restricao_limitante" in linha


def test_rf07_exige_duas_alternativas():
    vps = _vps(2)
    try:
        pipe.comparar_cenarios([_cfg("unico", vps, _frota(12), _seg())])
        assert False, "deveria exigir >=2 alternativas"
    except ValueError:
        pass


def test_protocolo_validacao_estrutura_completa():
    """RF-05: protocolo documenta parâmetros, capacidade (T-01), cenários e Living Lab."""
    vps = _vps(2)
    rel = val.executar_protocolo(
        [_cfg("base", vps, _frota(12), _seg()),
         _cfg("alt", vps, _frota(16), _seg())],
        living_lab_disponivel=False,
    )
    d = rel.to_dict()
    assert d["parametros"]["n_cenarios"] == 2
    assert len(d["validacao_capacidade_T01"]) == 2
    assert d["rastreabilidade_living_lab"]["disponibilidade_dados_reais"] == "A_VERIFICAR"
    assert len(d["cenarios"]) == 2


def test_protocolo_capacidade_T01_converge():
    """T-01: no ponto de operação, analítico e DES ficam dentro do desvio aceitável."""
    vps = _vps(2)
    rel = val.executar_protocolo([_cfg("base", vps, _frota(12), _seg())])
    for vc in rel.to_dict()["validacao_capacidade_T01"]:
        assert vc["aprovado"], f"desvio {vc['desvio_pct']}% > {vc['desvio_max_aceitavel_pct']}%"


def test_reprodutibilidade_pipeline():
    """RNF-01: pipeline determinístico."""
    vps = _vps(2)
    a = pipe.executar(_cfg("c", vps, _frota(12), _seg()))
    b = pipe.executar(_cfg("c", vps, _frota(12), _seg()))
    assert a.to_dict()["rede"] == b.to_dict()["rede"]
