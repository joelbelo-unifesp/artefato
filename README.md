# artefato — FIGOV

**Framework Integrado de Gestão Operacional de Vertiportos**

Repositório do artefato de doutorado (Design Science Research) para gestão operacional
de vertiportos em operações de eVTOL, aplicável a vertiportos individuais e em rede.

O FIGOV é um **artefato científico-tecnológico de apoio à decisão** (computacional +
metodológico), organizado em três níveis:

1. **Framework conceitual** — Problema → Entradas → Modelos → Restrições → Processamento → Indicadores → Decisão.
2. **Framework operacional** — parâmetros, variáveis, regras, algoritmos, indicadores e critérios de aceitação.
3. **Protótipo computacional** — implementação funcional do framework.

## Núcleo e camadas

- **Núcleo operacional (solvers):** Capacidade → Agendamento → Energia → Rede.
- **Camada transversal (guardrails):** Segurança.
- **Camada contextual:** Regulação / implementação brasileira (ANAC/DECEA).
- **Mecanismo de verificação:** Validação (simulação parametrizada + eventual Living Lab).

## Documentação

- [`docs/FIGOV-Especificacao-do-Artefato.md`](docs/FIGOV-Especificacao-do-Artefato.md) —
  Especificação do Artefato do Doutorado: identidade, arquitetura, entradas/saídas,
  modelos A–F, requisitos (RF-01…RF-07 e RNFs), métricas, critérios de aceitação,
  matriz de rastreabilidade e estratégia de validação.

## Objetivo

> Desenvolver e validar um framework computacional de gestão operacional de vertiportos,
> aplicável a operações individuais e em rede, capaz de integrar capacidade, agendamento
> de frotas heterogêneas, restrições energéticas e segurança operacional, fornecendo
> suporte à tomada de decisão no planejamento tático-operacional de operações eVTOL no
> contexto regulatório e urbano brasileiro.
