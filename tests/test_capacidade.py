"""Testes do Modelo A — Capacidade (RF-01), teste T-01."""

from figov.models import capacidade as cap


VP_FATO_GARGALO = {
    "id": "T-fato",
    "fatos": 1,
    "stands": 10,
    "tempo_ocupacao_fato_min": 4.0,
    "turnaround_min": 8.0,
}

VP_STAND_GARGALO = {
    "id": "T-stand",
    "fatos": 4,
    "stands": 2,
    "tempo_ocupacao_fato_min": 2.0,
    "turnaround_min": 12.0,
}


def test_capacidade_teorica_identifica_gargalo_fato():
    teo = cap.capacidade_teorica(VP_FATO_GARGALO)
    assert teo.recurso_gargalo == "fato"
    # 60/4 * 1 = 15 mov/h
    assert abs(teo.cap_teorica_mov_h - 15.0) < 1e-6
    assert teo.cap_teorica_mov_h <= teo.cap_stand_mov_h


def test_capacidade_teorica_identifica_gargalo_stand():
    teo = cap.capacidade_teorica(VP_STAND_GARGALO)
    assert teo.recurso_gargalo == "stand"
    # 60/12 * 2 = 10 mov/h
    assert abs(teo.cap_teorica_mov_h - 10.0) < 1e-6


def test_capacidade_pratica_nao_excede_teorica():
    teo = cap.capacidade_teorica(VP_FATO_GARGALO)
    prat = cap.capacidade_pratica(VP_FATO_GARGALO, atraso_aceitavel_min=5.0)
    assert 0 < prat.cap_pratica_mov_h <= teo.cap_teorica_mov_h
    # No ponto encontrado, a espera respeita o limiar.
    assert prat.atraso_no_ponto_min <= 5.0 + 1e-6


def test_espera_cresce_com_a_demanda():
    """Monotonicidade: mais chegadas → maior espera média."""
    wq_baixo = cap.espera_media_min(5.0, VP_FATO_GARGALO)
    wq_alto = cap.espera_media_min(12.0, VP_FATO_GARGALO)
    assert wq_alto > wq_baixo


def test_analitico_proximo_da_des_reference():
    """T-01: modelo analítico (M/M/c) deve aproximar a DES de referência.

    Usa tolerância folgada porque o critério x% é [A DEFINIR]; aqui verificamos
    apenas que as duas abordagens convergem qualitativamente (mesma ordem de
    grandeza) no ponto de operação.
    """
    vp = VP_STAND_GARGALO
    taxa = 8.0  # abaixo da capacidade teórica (10)
    wq_analitico = cap.espera_media_min(taxa, vp)
    # Horizonte longo → regime estacionário → comparação justa com M/M/c.
    des = cap.simular_des_referencia(taxa, vp, horas=200.0, replicas=10, seed=1)
    assert des.espera_media_min > 0
    desvio = abs(wq_analitico - des.espera_media_min) / des.espera_media_min
    assert desvio < 0.15  # convergência quantitativa em regime estacionário


def test_reprodutibilidade_des_mesma_seed():
    """RNF-01: mesma seed → mesmo resultado."""
    vp = VP_STAND_GARGALO
    a = cap.simular_des_referencia(8.0, vp, replicas=5, seed=123)
    b = cap.simular_des_referencia(8.0, vp, replicas=5, seed=123)
    assert a.espera_media_min == b.espera_media_min
