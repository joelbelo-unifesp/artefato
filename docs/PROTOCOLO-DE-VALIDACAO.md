# Protocolo de Validação — FIGOV (RF-05)

Este documento define o protocolo de validação do artefato FIGOV, conforme RF-05 e a
seção 12 da especificação (`docs/FIGOV-Especificacao-do-Artefato.md`).

## 1. Estratégia de validação

| Nível | Papel | Descrição |
|---|---|---|
| **Principal** | Obrigatória | **Simulação computacional parametrizada.** Cenários reproduzíveis (seed versionada), baselines de comparação explícitos. Sustenta a tese isoladamente. |
| **Complementar** | Condicional | **Living Lab (Sapiens Parque).** Só se houver dados reais adequados — **[A VERIFICAR]**. Reforça, não fundamenta. |

> A validade da tese **não depende** da disponibilidade de dados reais. Se o Living Lab
> não fornecer dados suficientes, a arquitetura metodológica permanece íntegra.

## 2. Parâmetros do protocolo

Todos os parâmetros são versionados em `config/` e no `ConfiguracaoCenario`.

| Parâmetro | Símbolo | Fonte | Status |
|---|---|---|---|
| Desvio de capacidade máximo aceitável | `x%` | `config/cenario.json` | **[A DEFINIR]** — justificar |
| Atraso aceitável por movimento | `y min` | `config/cenario.json` | **[A DEFINIR]** — justificar |
| Réplicas da simulação de referência | — | `config/cenario.json` | placeholder (10) |
| Semente de reprodutibilidade | `seed` | `config/cenario.json` | fixa (RNF-01) |
| Nível alvo de risco (segurança) | — | `config/seguranca.json` | **[A DEFINIR]** — EASA PTS-VPT / ANAC |

## 3. Cenários

Cada cenário é uma `ConfiguracaoCenario` (vertiportos, frota, demanda, segurança,
limiares). Os cenários variam, no mínimo:

- **Demanda:** volume e perfil (picos manhã/tarde), via `figov.io.demanda_gen` (determinístico por seed).
- **Frota:** composição e tamanho (heterogênea).
- **Rede:** topologia de 2 a 4 vertiportos.
- **Energia:** SoC inicial, taxa de recarga, consumo.

## 4. Procedimento de execução

Para cada cenário:

1. Carregar e **validar** as entradas contra os schemas (`figov.io`).
2. Executar o **pipeline** (`figov.pipeline.executar`): capacidade (RF-01) →
   agendamento (RF-02) → rede (RF-03) → guardrail de segurança (RF-04).
3. Coletar indicadores: taxa de atendimento, atraso médio, gargalos, aceitação de segurança.
4. **Comparação com referência (T-01):** confrontar a espera média analítica (M/M/c)
   com a simulação de eventos discretos (DES) de referência, com o número de réplicas
   definido; aprovado se o desvio ≤ `x%`.

Execução via CLI:

```bash
PYTHONPATH=src python -m figov.cli validar --cenario config/cenario.json
```

## 5. Resultados registrados

O relatório de validação (`figov.models.validacao.RelatorioValidacao`) contém:

- `parametros` — parâmetros efetivos da execução (com nota de [A DEFINIR]).
- `validacao_capacidade_T01` — por vertiporto: Wq analítico, Wq da DES, desvio %, aprovação.
- `cenarios` — por cenário: aceitação, taxa de atendimento, atraso, restrição limitante.
- `rastreabilidade_living_lab` — mapeamento cenário simulado ↔ real e status de dados.

## 6. Rastreabilidade simulado ↔ real (Living Lab)

O relatório estrutura um **mapeamento** entre cada cenário simulado e o cenário real
correspondente do Living Lab. Enquanto `disponibilidade_dados_reais = A_VERIFICAR`, o
campo `cenario_real_correspondente` permanece `null`, e a validação principal
(simulação) é a evidência de sustentação.

## 7. Critério de aceitação (RF-05)

O protocolo documenta parâmetros, cenários executados (com o número de réplicas por
cenário), resultados e comparação com referência, mantendo rastreabilidade entre
cenário simulado e real. O número de réplicas (`replicas_referencia`) é **[A DEFINIR]**.
