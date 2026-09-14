# Diretrizes de Implementação para o Brasil — FIGOV (RF-06)

Este documento reúne diretrizes para a implementação de operações de vertiportos eVTOL
no Brasil, compatíveis com a regulação em formação (ANAC/DECEA) e com o ambiente
nacional de inovação. Atende ao RF-06 e à camada contextual da especificação
(`docs/FIGOV-Especificacao-do-Artefato.md`, §5 e §6).

> **AVISO METODOLÓGICO — NÃO INVENTAR REFERÊNCIAS.**
> Conforme a Tarefa 6.2, cada diretriz **deve** referenciar a norma, o instrumento
> regulatório ou a prática institucional correspondente. Este documento **não fixa**
> números de norma, títulos oficiais, artigos ou datas que não possam ser confirmados
> na fonte primária. Cada referência está marcada como **`[PENDENTE DE FONTE — verificar
> na fonte primária]`**. O preenchimento dessas referências é uma etapa obrigatória de
> conciliação documental antes de qualquer uso/publicação, a ser feita consultando os
> instrumentos oficiais da ANAC, do DECEA e demais órgãos.

Legenda de status da referência:
- **`[PENDENTE DE FONTE]`** — a diretriz é aplicável, mas a referência normativa/institucional
  precisa ser localizada e citada na fonte primária.

---

## 1. Escopo e enquadramento

| # | Diretriz | Referência |
|---|---|---|
| D-01 | O planejamento tático-operacional de vertiportos deve observar o arcabouço regulatório de infraestrutura aeroportuária/heliportuária aplicável a operações VTOL. | `[PENDENTE DE FONTE — ANAC: regulamento de infraestrutura aplicável a vertiportos/heliportos]` |
| D-02 | A operação deve observar as regras de tráfego aéreo e de gerenciamento do espaço aéreo brasileiro. | `[PENDENTE DE FONTE — DECEA: normas de gerenciamento do espaço aéreo / ICA aplicável]` |

## 2. Segurança operacional

| # | Diretriz | Referência |
|---|---|---|
| D-03 | O nível alvo de segurança (risco ar-solo) adotado no FIGOV é **parametrizável** e deve ser fixado conforme a regulação aplicável e as especificações técnicas de referência. | `[PENDENTE DE FONTE — EASA PTS-VPT (referência técnica) e regulação ANAC em formação]` |
| D-04 | Sítios de contingência são **obrigatórios** no planejamento; sua localização deve constar dos dados de entrada e observar critérios de segurança da autoridade. | `[PENDENTE DE FONTE — critério de contingência da autoridade aeronáutica]` |
| D-05 | Planos que violem o nível alvo de segurança devem ser rejeitados; a rastreabilidade da rejeição deve ser preservada para auditoria. | `[PENDENTE DE FONTE — requisito de auditoria/segurança operacional aplicável]` |

## 3. Capacidade e infraestrutura

| # | Diretriz | Referência |
|---|---|---|
| D-06 | O dimensionamento de FATO/TLOF e stands deve observar os parâmetros físicos e de separação da autoridade. | `[PENDENTE DE FONTE — parâmetros de projeto de vertiporto/heliporto ANAC]` |
| D-07 | A capacidade prática deve considerar o nível de serviço (atraso aceitável) parametrizado e justificado. | `[PENDENTE DE FONTE — referência de nível de serviço; valor y [A DEFINIR]]` |

## 4. Energia e frota

| # | Diretriz | Referência |
|---|---|---|
| D-08 | A infraestrutura de recarga/troca de bateria deve observar normas elétricas e de segurança aplicáveis à instalação. | `[PENDENTE DE FONTE — normas elétricas/segurança de instalação de recarga]` |
| D-09 | O planejamento energético deve preservar SoC mínimo operacional e reservas de contingência por tipo de aeronave. | `[PENDENTE DE FONTE — reserva operacional/energia mínima aplicável]` |

## 5. Ambiente de inovação nacional

| # | Diretriz | Referência |
|---|---|---|
| D-10 | A validação em ambiente controlado (Living Lab) deve ser tratada como **complementar**, condicionada à disponibilidade de dados reais e a acordos institucionais. | `[PENDENTE DE FONTE — instrumento do Living Lab (Sapiens Parque) / acordo institucional]` |
| D-11 | A implementação deve buscar aderência a instrumentos de fomento e sandbox regulatório eventualmente disponíveis. | `[PENDENTE DE FONTE — instrumento de sandbox regulatório/fomento aplicável]` |

## 6. Rastreabilidade e conformidade

| # | Diretriz | Referência |
|---|---|---|
| D-12 | Cada decisão do artefato deve ser rastreável (premissa → requisito → implementação → resultado), permitindo verificação de conformidade. | Especificação FIGOV, RNF-03 (interno) |
| D-13 | Parâmetros regulatórios (segurança, capacidade, energia) devem ser mantidos externos ao código (configuração), permitindo atualização sem alteração do artefato. | Especificação FIGOV, RNF-02 (interno) |

---

## 7. Critério de aceitação (RF-06)

Cada diretriz referencia a norma, o instrumento regulatório ou a prática institucional
correspondente. **As referências externas estão marcadas `[PENDENTE DE FONTE]`** e devem
ser preenchidas com a citação da fonte primária antes de qualquer uso oficial — nenhuma
referência foi inventada. As referências marcadas como *(interno)* remetem à própria
especificação do FIGOV e estão resolvidas.

## 8. Checklist de conciliação documental

- [ ] Localizar e citar o regulamento ANAC de infraestrutura de vertiportos (D-01, D-06).
- [ ] Localizar e citar as normas DECEA de espaço aéreo aplicáveis (D-02).
- [ ] Confirmar a referência técnica de segurança (EASA PTS-VPT) e a regulação ANAC em formação (D-03).
- [ ] Definir e justificar o nível alvo de risco e o atraso aceitável `y` (D-03, D-07).
- [ ] Confirmar critérios de contingência da autoridade (D-04).
- [ ] Confirmar normas elétricas/segurança da infraestrutura de recarga (D-08).
- [ ] Formalizar o instrumento do Living Lab e eventuais sandbox/fomento (D-10, D-11).
