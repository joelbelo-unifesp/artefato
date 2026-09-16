# artefato — FIGOV

**Framework Integrado de Gestão Operacional de Vertiportos**

Repositório do artefato de doutorado (Design Science Research) para gestão operacional
de vertiportos em operações de eVTOL, aplicável a vertiportos individuais e em rede.

O FIGOV é um **artefato científico-tecnológico de apoio à decisão** (computacional +
metodológico), organizado em três níveis:

1. **Framework conceitual** — Problema → Entradas → Modelos → Restrições → Processamento → Indicadores → Decisão.
2. **Framework operacional** — parâmetros, variáveis, regras, algoritmos, indicadores e critérios de aceitação.
3. **Protótipo computacional** — implementação funcional do framework (este repositório).

## Núcleo e camadas

- **Núcleo operacional (solvers):** Capacidade → Agendamento → Energia → Rede.
- **Camada transversal (guardrails):** Segurança.
- **Camada contextual:** Regulação / implementação brasileira (ANAC/DECEA).
- **Mecanismo de verificação:** Validação (simulação parametrizada + eventual Living Lab).

## Estrutura do repositório

```
artefato/
├── config/         # Entradas de configuração (vertiportos, frota, segurança, cenário)
├── data/           # Dados de entrada gerados/realistas (demanda)
├── docs/           # Especificação, tarefas e diretrizes
│   ├── FIGOV-Especificacao-do-Artefato.md   # Especificação de referência
│   ├── FIGOV                                 # Lista de tarefas de implementação
│   ├── PROTOCOLO-DE-VALIDACAO.md             # Protocolo de validação (RF-05)
│   └── DIRETRIZES-IMPLEMENTACAO-BRASIL.md    # Diretrizes para o Brasil (RF-06)
├── src/figov/      # Protótipo (pacote Python, apenas biblioteca padrão)
│   ├── io/         # Schemas, validação e carregamento de entradas
│   ├── models/     # Modelos A–E (capacidade, agendamento, rede, segurança)
│   ├── pipeline.py # Orquestração sequencial iterativa (solvers + guardrails)
│   └── cli.py      # Interface de linha de comando
└── tests/          # Testes (pytest)
```

## Requisitos

- Python ≥ 3.10 (desenvolvido/testado em 3.12).
- **Sem dependências externas de runtime** — o MVP usa apenas a biblioteca padrão,
  para permanecer executável do zero. `pytest` é usado apenas para testes.

## Como executar o MVP

Do diretório do repositório:

```bash
# 1. Executar o pipeline completo sobre as configs de exemplo
PYTHONPATH=src python -m figov.cli run \
  --vertiporto config/vertiporto_A.json \
  --vertiporto config/vertiporto_B.json \
  --frota config/frota.json \
  --seguranca config/seguranca.json \
  --cenario config/cenario.json

# 2. Comparar duas alternativas de planejamento (RF-07)
PYTHONPATH=src python -m figov.cli comparar --cenario config/cenario.json

# 3. Rodar o protocolo de validação (RF-05)
PYTHONPATH=src python -m figov.cli validar --cenario config/cenario.json
```

Para rodar os testes:

```bash
pip install pytest
PYTHONPATH=src pytest -q
```

## Valores pendentes de definição

Vários limiares são **parâmetros de cenário deliberadamente não fixados** (marcados
`[A DEFINIR]` na documentação), para não introduzir valores arbitrários:

| Parâmetro | Onde | Significado |
|---|---|---|
| `desvio_capacidade_max_pct` (x%) | `config/cenario.json` | Desvio máximo aceitável da capacidade vs. simulação de referência (RF-01). |
| `atraso_aceitavel_min` (y min) | `config/cenario.json` | Atraso aceitável por movimento (RF-01/RF-02). |
| `nivel_alvo_risco` | `config/seguranca.json` | Alvo de segurança ar-solo (RF-04) — fonte pretendida EASA PTS-VPT / ANAC. |
| `replicas_referencia` | `config/cenario.json` | Nº de réplicas da simulação de referência (RF-05). |

Os valores presentes nas configs são **placeholders operacionais** que permitem a
execução; **não** estão ancorados em literatura/benchmark e devem ser justificados
antes de qualquer conclusão científica (ver checklist da especificação).

## Documentação

- [`docs/FIGOV-Especificacao-do-Artefato.md`](docs/FIGOV-Especificacao-do-Artefato.md) — especificação de referência.
- [`docs/FIGOV`](docs/FIGOV) — lista de tarefas de implementação.

## Objetivo

> Desenvolver e validar um framework computacional de gestão operacional de vertiportos,
> aplicável a operações individuais e em rede, capaz de integrar capacidade, agendamento
> de frotas heterogêneas, restrições energéticas e segurança operacional, fornecendo
> suporte à tomada de decisão no planejamento tático-operacional de operações eVTOL no
> contexto regulatório e urbano brasileiro.
