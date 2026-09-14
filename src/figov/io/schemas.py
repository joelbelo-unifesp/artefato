"""Schemas das entradas do FIGOV (seção 6.1 da especificação).

Cada schema documenta os campos de um grupo de entrada. Os valores numéricos de
limiar de aceitação (x%, y minutos, alvo de segurança, nº de réplicas) NÃO são
fixados aqui: são parâmetros de configuração de cenário, marcados [A DEFINIR] na
documentação, para não introduzir valores arbitrários (ver docs/FIGOV, notas).
"""

from __future__ import annotations

# --- Vertiporto (RF-01, Modelo A) -----------------------------------------
VERTIPORTO_SCHEMA = {
    "type": "object",
    "required": ["id", "fatos", "stands", "tempo_ocupacao_fato_min", "turnaround_min"],
    "properties": {
        "id": {"type": "string"},
        "nome": {"type": "string"},
        # Nº de FATO/TLOF (áreas de pouso/decolagem).
        "fatos": {"type": "integer", "minimum": 1},
        # Nº de posições de estacionamento (stands).
        "stands": {"type": "integer", "minimum": 1},
        # Tempo médio de ocupação de um FATO por movimento (pouso ou decolagem), min.
        "tempo_ocupacao_fato_min": {"type": "number", "minimum": 0},
        # Tempo de turnaround em stand (embarque/desembarque/serviço), min.
        "turnaround_min": {"type": "number", "minimum": 0},
        # Janela operacional diária, horas (default 24 se ausente).
        "janela_operacional_h": {"type": "number", "minimum": 0, "maximum": 24},
        # Nº de pontos de recarga disponíveis no vertiporto.
        "pontos_recarga": {"type": "integer", "minimum": 0},
    },
}

# --- Frota heterogênea (RF-02, Modelos B e C) ------------------------------
AERONAVE_SCHEMA = {
    "type": "object",
    "required": ["tipo", "autonomia_min", "soc_inicial", "taxa_recarga_pct_min", "assentos"],
    "properties": {
        "tipo": {"type": "string"},
        "quantidade": {"type": "integer", "minimum": 1},
        # Autonomia de voo com SoC 100%, em minutos.
        "autonomia_min": {"type": "number", "minimum": 0},
        # Estado de carga inicial (0.0 a 1.0).
        "soc_inicial": {"type": "number", "minimum": 0, "maximum": 1},
        # SoC mínimo operacional permitido (0.0 a 1.0). Guardrail energético (Modelo C).
        "soc_minimo": {"type": "number", "minimum": 0, "maximum": 1},
        # Taxa de recarga em pontos percentuais de SoC por minuto.
        "taxa_recarga_pct_min": {"type": "number", "minimum": 0},
        # Capacidade de passageiros.
        "assentos": {"type": "integer", "minimum": 0},
        # Consumo de SoC por minuto de voo (pontos percentuais/min).
        "consumo_pct_min": {"type": "number", "minimum": 0},
    },
}

FROTA_SCHEMA = {
    "type": "object",
    "required": ["aeronaves"],
    "properties": {
        "aeronaves": {"type": "array", "minItems": 1, "items": AERONAVE_SCHEMA},
    },
}

# --- Demanda (entrada de movimentos) ---------------------------------------
MOVIMENTO_SCHEMA = {
    "type": "object",
    "required": ["origem", "destino", "horario_desejado_min", "passageiros"],
    "properties": {
        # Vertiporto de origem (id).
        "origem": {"type": "string"},
        # Vertiporto de destino (id).
        "destino": {"type": "string"},
        # Horário desejado de partida, em minutos desde o início do dia.
        "horario_desejado_min": {"type": "number", "minimum": 0},
        # Duração de voo estimada, em minutos.
        "duracao_voo_min": {"type": "number", "minimum": 0},
        "passageiros": {"type": "integer", "minimum": 0},
    },
}

DEMANDA_SCHEMA = {
    "type": "object",
    "required": ["movimentos"],
    "properties": {
        "descricao": {"type": "string"},
        "movimentos": {"type": "array", "minItems": 1, "items": MOVIMENTO_SCHEMA},
    },
}

# --- Segurança (RF-04, Modelo E) -------------------------------------------
SITIO_CONTINGENCIA_SCHEMA = {
    "type": "object",
    "required": ["id", "lat", "lon"],
    "properties": {
        "id": {"type": "string"},
        "lat": {"type": "number", "minimum": -90, "maximum": 90},
        "lon": {"type": "number", "minimum": -180, "maximum": 180},
    },
}

SEGURANCA_SCHEMA = {
    "type": "object",
    # Sítios de contingência são OBRIGATÓRIOS (RF-04, critério de aceitação).
    "required": ["nivel_alvo_risco", "sitios_contingencia"],
    "properties": {
        # Nível alvo de risco ar-solo (probabilidade de fatalidade por hora de voo, p.ex.).
        # VALOR [A DEFINIR]: fonte EASA PTS-VPT e regulação ANAC em formação. Parâmetro,
        # não constante — ver RF-04. O framework rejeita planos que excedam este alvo.
        "nivel_alvo_risco": {"type": "number", "minimum": 0},
        # Risco estimado por movimento (proxy de 1a ordem). Em [A DEFINIR] o cálculo
        # detalhado; aqui usa-se um proxy configurável por tipo de sobrevoo.
        "risco_por_movimento": {"type": "number", "minimum": 0},
        "sitios_contingencia": {
            "type": "array",
            "minItems": 1,
            "items": SITIO_CONTINGENCIA_SCHEMA,
        },
    },
}

# --- Parâmetros de cenário (limiares [A DEFINIR]) --------------------------
CENARIO_SCHEMA = {
    "type": "object",
    "required": ["seed"],
    "properties": {
        # Semente para reprodutibilidade (RNF-01).
        "seed": {"type": "integer", "minimum": 0},
        # x% (RF-01): desvio máximo aceitável vs. simulação de referência. [A DEFINIR]
        "desvio_capacidade_max_pct": {"type": "number", "minimum": 0},
        # y minutos (RF-01/RF-02): atraso aceitável por movimento. [A DEFINIR]
        "atraso_aceitavel_min": {"type": "number", "minimum": 0},
        # Nº de réplicas da simulação de eventos discretos de referência (RF-01/RF-05).
        "replicas_referencia": {"type": "integer", "minimum": 1},
    },
}

SCHEMAS = {
    "vertiporto": VERTIPORTO_SCHEMA,
    "frota": FROTA_SCHEMA,
    "demanda": DEMANDA_SCHEMA,
    "seguranca": SEGURANCA_SCHEMA,
    "cenario": CENARIO_SCHEMA,
}
