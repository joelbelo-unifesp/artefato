# Especificação do Artefato do Doutorado — FIGOV

**Framework Integrado de Gestão Operacional de Vertiportos**

| Campo | Conteúdo |
|---|---|
| **Identificador do artefato** | FIGOV |
| **Nome por extenso** | Framework Integrado de Gestão Operacional de Vertiportos |
| **Natureza** | Artefato científico-tecnológico de apoio à decisão (computacional + metodológico) |
| **Versão do documento** | 0.1 (baseline inicial) |
| **Data** | 14 SET 2026 |
| **Autor** | Joel Belo |
| **Status** | Documento-base para orientação e controle de evolução do doutorado |

> **Nota de fonte.** Este documento reconstrói RF-01 a RF-06 e os RNFs a partir da
> discussão de escopo registrada com o orientando, **não** a partir da leitura direta
> do arquivo `PROBLEMA DE PESQUISA E REQUISITOS DO ARTEFATO - 9 SET 2026 - Joel Belo.docx`,
> que não foi disponibilizado à ferramenta. Todos os pontos em que a redação original
> do `.docx` é determinante estão marcados com **`[CONFIRMAR CONTRA O DOCX]`**. Antes de
> apresentar ao orientador, concilie estes marcadores com o documento original.

---

## 1. Enquadramento metodológico

O FIGOV é tratado como **artefato de Design Science Research (DSR)**. Isso significa
que ele não é apenas um conjunto de conceitos, mas um objeto com **estrutura, entradas,
processamento, saídas, regras de decisão e critérios de aceitação**, projetado para
resolver um problema de classe (gestão operacional de vertiportos) e avaliado por
protocolo explícito.

A tese distingue dois produtos:

- **Produto tecnológico:** framework operacional implementado em protótipo computacional
  (com possibilidade de evolução posterior para software).
- **Produto científico:** conhecimento sistematizado sobre a integração das dimensões de
  capacidade, agendamento, energia, rede, segurança e regulação.

Essa distinção neutraliza, de forma antecipada, a arguição *"mas onde está o produto
tecnológico?"* — a resposta deixa de ser "é um framework" e passa a ser "é um framework
operacional implementado em protótipo computacional, cientificamente rastreável".

---

## 2. Baseline congelado do doutorado

Estes elementos são o **baseline** — concretos o suficiente para orientar, abertos o
suficiente para não engessar decisões técnicas futuras.

| Elemento | Definição congelada |
|---|---|
| **Problema** | Ausência de um modelo integrado de gestão operacional de vertiportos que trate conjuntamente capacidade, agendamento, energia, rede e segurança. |
| **Questão de pesquisa** | Qual framework pode apoiar decisões operacionais integrando capacidade, agendamento, energia e segurança? |
| **Objeto** | Gestão operacional de vertiportos (eVTOL). |
| **Artefato** | FIGOV — framework computacional e metodológico de apoio à decisão. |
| **Escopo** | Planejamento tático-operacional; passageiros e carga; 2 a 4 vertiportos; ambiente urbano brasileiro. |
| **Núcleo operacional** | Capacidade + frota + energia + rede. |
| **Camadas** | Segurança (transversal) + regulação/implementação brasileira (contextual). |
| **Validação** | Simulação parametrizada (principal) + eventual Living Lab (complementar). |
| **Produto tecnológico** | Framework operacional implementado em protótipo computacional. |
| **Produto científico** | Conhecimento sistematizado sobre a integração dessas dimensões. |
| **Produtos intermediários** | Artigos (incrementos sucessivos do artefato). |
| **Produto final** | Artefato validado + documentação metodológica + diretrizes de implementação. |

**Formulação do objetivo da tese:**

> Desenvolver e validar um framework computacional de gestão operacional de vertiportos,
> aplicável a operações individuais e em rede, capaz de integrar capacidade, agendamento
> de frotas heterogêneas, restrições energéticas e segurança operacional, fornecendo
> suporte à tomada de decisão no planejamento tático-operacional de operações eVTOL no
> contexto regulatório e urbano brasileiro.

---

## 3. Usuários e uso pretendido

| Perfil | Uso do artefato |
|---|---|
| **Operador de vertiporto / planejador** | Configurar cenários, gerar/avaliar agendas, identificar gargalos, comparar alternativas. |
| **Autoridade / regulador (ANAC, DECEA)** | Verificar conformidade e critérios de aceitação de segurança sob parametrização regulatória. |
| **Pesquisador (o próprio doutorando)** | Executar experimentos parametrizados, gerar evidência científica, rastrear premissa → resultado. |

**Uso pretendido:** apoio à decisão no **planejamento tático-operacional** — não
controle em tempo real, não certificação de aeronave, não projeto de infraestrutura civil.


---

## 4. Arquitetura do artefato em três níveis

O FIGOV é organizado em três níveis, do abstrato ao executável. Este arranjo é o que
garante que exista um **produto tecnológico demonstrável** (Nível 3) sem exigir o
compromisso prematuro de desenvolver um software comercial completo.

### Nível 1 — Framework conceitual

Define a cadeia lógica de raciocínio, independente de implementação:

```
Problema → Entradas → Modelos → Restrições → Processamento → Indicadores → Decisão
```

É a camada que responde *"o que o artefato faz e por quê"*.

### Nível 2 — Framework operacional

Transforma os conceitos do Nível 1 em elementos manipuláveis e verificáveis:

- **Parâmetros** (constantes de configuração de cenário);
- **Variáveis** (grandezas de decisão e de estado);
- **Regras** (lógica de negócio e restrições);
- **Algoritmos** (procedimentos de cálculo/otimização);
- **Indicadores** (métricas de saída);
- **Critérios de aceitação** (limiares de viabilidade);
- **Procedimentos de utilização** (como o usuário opera o framework).

É a camada que responde *"como o artefato funciona, de forma precisa e reproduzível"*.

### Nível 3 — Protótipo computacional

Implementa **pelo menos uma versão funcional** do framework, capaz de:

- receber dados;
- configurar vertiportos, aeronaves, demanda e energia;
- gerar cenários;
- gerar e avaliar agendas;
- identificar conflitos;
- verificar restrições;
- produzir indicadores;
- **rejeitar soluções que violem requisitos de segurança**;
- comparar cenários.

É a camada que responde *"onde está o produto tecnológico"*.

> **Posicionamento de defesa.** O produto do doutorado é um **framework operacional
> implementado em protótipo computacional**, com possibilidade de evolução posterior
> para software. Não se assume, desde já, o desenvolvimento de um software comercial
> completo — isso é uma trajetória de evolução, não um requisito de conclusão.

---

## 5. Artefato vs. modelos

Distinção deliberada para permitir artigos incrementais **sem fragmentar** a tese:

- **Artefato:** o FIGOV (o todo integrado).
- **Modelos:** componentes internos, integrados *pelo* framework.

| Modelo | Domínio | Módulo do pipeline |
|---|---|---|
| **Modelo A** | Capacidade do vertiporto | Módulo 1 |
| **Modelo B** | Agendamento de frota heterogênea | Módulo 2 |
| **Modelo C** | Energia (autonomia, SoC, recarga) | Módulo 3 |
| **Modelo D** | Coordenação de rede (multi-vertiporto) | Módulo 4 |
| **Modelo E** | Segurança operacional | Módulo 5 (camada transversal) |
| **Modelo F** | Conformidade regulatória | Módulo 6 (camada contextual) |

**Reorganização conceitual da arquitetura** (mais elegante que a lista linear de seis pilares):

- **Núcleo operacional (solvers):** Capacidade → Scheduling → Energia → Rede.
- **Camada transversal (guardrails):** Segurança — restrições e validações aplicadas
  *sobre* os quatro solvers, não uma etapa isolada do pipeline.
- **Camada contextual:** Regulação / implementação brasileira — parametriza restrições
  segundo ANAC/DECEA e demais condicionantes.
- **Mecanismo de verificação:** Validação — protocolo que avalia o artefato como um todo.

> **Distinção-chave para a arguição.** *Camadas* = constraints/guardrails (Segurança,
> Regulação). *Componentes* = solvers (Capacidade, Scheduling, Energia, Rede). Segurança
> e regulação não são "etapas" do pipeline: são condições de validade aplicadas sobre
> as soluções produzidas pelos solvers.


---

## 6. Arquitetura de processamento (entradas → módulos → saídas)

### 6.1 Entradas

| Grupo | Itens |
|---|---|
| **Vertiporto** | Configuração física; nº e tipo de FATO/TLOF e stands; slots; tempos de ocupação; tempo de *turnaround*. |
| **Demanda** | Perfil temporal de movimentos (chegadas/partidas); passageiros e/ou carga; padrão pico/fora-pico. |
| **Aeronave (frota heterogênea)** | Tipos; autonomia; estado de carga (SoC) inicial; taxa de recarga; capacidade de payload. |
| **Energia / infraestrutura** | Nº de pontos de recarga; potência disponível; limites da subestação/rede elétrica; política de recarga vs. troca de bateria. |
| **Operacional** | Condições ambientais; sítios de contingência; janelas operacionais; separação mínima. |
| **Regulatório** | Restrições ANAC/DECEA; alvo de segurança parametrizável; condicionantes locais. |

### 6.2 Pipeline de módulos

```
                         ENTRADAS
                            │
                            ▼
              ┌─────────────────────────┐
              │  MÓDULO 1 — CAPACIDADE   │  (solver)
              │  capacidade teórica/     │
              │  prática do vertiporto   │
              └─────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │ MÓDULO 2 — AGENDAMENTO   │  (solver)
              │ aloca aeronaves,         │
              │ movimentos e slots       │
              └─────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │  MÓDULO 3 — ENERGIA      │  (solver)
              │  autonomia, SoC,         │
              │  recarga, disponibilidade│
              └─────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │   MÓDULO 4 — REDE        │  (solver)
              │  coordena múltiplos      │
              │  vertiportos e fluxos    │
              └─────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼ (camada transversal)                  │
┌─────────────────────────┐                     │
│  MÓDULO 5 — SEGURANÇA    │  (guardrail)        │
│  critérios de aceitação  │  aplicado SOBRE     │
│  e contingência          │  os solvers 1–4     │
└─────────────────────────┘                     │
        ▼ (camada contextual)                    │
┌─────────────────────────┐                     │
│  MÓDULO 6 — REGULAÇÃO    │  (guardrail)        │
│  compatibilidade         │  ANAC/DECEA         │
│  ANAC/DECEA + local      │  parametrizável     │
└─────────────────────────┘                     │
        └───────────────────┬───────────────────┘
                            ▼
                          SAÍDAS
```

### 6.3 Saídas

Agenda operacional · capacidade (teórica/prática) · utilização da infraestrutura ·
atrasos · gargalos · utilização energética · conflitos · violações de restrição ·
indicadores de segurança · nível de serviço · alternativas de operação ·
**recomendação ao decisor**.

---

## 7. Grafo de dependências entre componentes

Os solvers **não são independentes**. Explicitar o acoplamento é um ponto sensível de
arguição e precisa constar do artefato.

```
  Capacidade ──restringe nº de movimentos viáveis──▶ Agendamento
  Agendamento ──consome janelas / define perfil de uso──▶ Energia
  Energia ──impõe janelas de recarga / SoC mínimo──▶ Agendamento   (realimentação)
  Agendamento (por vertiporto) ──fluxos entre nós──▶ Rede
  Rede ──redistribui demanda / redireciona fluxos──▶ Capacidade    (realimentação)

  Segurança  ── valida/rejeita soluções de TODOS os solvers (transversal)
  Regulação  ── parametriza limites de TODOS os solvers (contextual)
```

**Realimentações relevantes:**

1. **Energia → Agendamento:** janelas de recarga e SoC mínimo restringem quando uma
   aeronave pode ser reagendada. Sem essa realimentação, a agenda é energeticamente
   inviável.
2. **Rede → Capacidade:** ao redistribuir demanda entre vertiportos, a coordenação de
   rede altera a carga sobre a capacidade de cada nó.

### 7.1 Ordem de resolução — decisão de projeto

Há duas estratégias possíveis; a especificação deve declarar qual será adotada no
protótipo (Nível 3):

| Estratégia | Descrição | Trade-off |
|---|---|---|
| **Sequencial iterativa** *(recomendada para a v1)* | Resolve 1→2→3→4 e itera até convergência das realimentações (Energia↔Agendamento, Rede↔Capacidade). | Mais simples de implementar e rastrear; ótimo local, não global. |
| **Otimização acoplada** | Formula um único problema com todas as restrições simultâneas. | Solução mais "correta"; alto custo computacional e menor rastreabilidade. |

> **Decisão de projeto (proposta):** adotar **sequencial iterativa** no protótipo inicial,
> declarando explicitamente o critério de convergência e o número máximo de iterações.
> `[CONFIRMAR COM ORIENTADOR]` — a otimização acoplada pode ser trabalho futuro / artigo posterior.


---

## 8. Requisitos funcionais (RF)

> **Aviso de conciliação.** A redação abaixo reconstrói a intenção discutida. Os textos
> exatos, códigos e valores numéricos originais devem ser conferidos no `.docx`. Marcadores
> `[CONFIRMAR CONTRA O DOCX]` indicam onde isso é crítico.

### RF-01 — Capacidade
O framework deve determinar a **capacidade teórica e prática** de um vertiporto a partir
de sua configuração física, slots, tempos de ocupação e *turnaround*.

- **Critério de aceitação:** a capacidade calculada deve reproduzir um modelo/benchmark de
  referência com desvio máximo de **`x%`** `[CONFIRMAR CONTRA O DOCX — definir e justificar x]`.
- **Nota:** o valor de `x` **não deve ser arbitrário**; deve decorrer de literatura,
  benchmark, dado empírico ou decisão metodológica explicitamente justificada.

### RF-02 — Agendamento
O framework deve **alocar aeronaves, movimentos e slots** para uma frota heterogênea,
respeitando capacidade e restrições energéticas.

- **Critério de aceitação:** gerar agenda viável atendendo à demanda com atraso aceitável
  de até **`y minutos`** `[CONFIRMAR CONTRA O DOCX — definir e justificar y]`.

### RF-03 — Rede
O framework deve **coordenar a operação de múltiplos vertiportos** (2 a 4), redistribuindo
fluxos e demanda entre nós da rede.

- **Critério de aceitação:** demonstrar redução de rejeições/atrasos ao coordenar em rede
  frente à operação isolada dos nós. `[CONFIRMAR CONTRA O DOCX]`

### RF-04 — Segurança *(requisito sujeito à parametrização regulatória)*
O framework deve **avaliar critérios de aceitação de segurança e contingência**, rejeitando
soluções que os violem.

- **Estado:** requisito **aberto por decisão metodológica** — o alvo numérico de segurança
  depende de especificações EASA e da regulação ANAC em formação. Tratado como
  **parametrizável**, não amarrado prematuramente a um valor que pode mudar durante o doutorado.
- **Critério de aceitação:** para um alvo de segurança parametrizado, o framework deve
  identificar e rejeitar toda solução que o viole. `[CONFIRMAR CONTRA O DOCX]`

### RF-05 — Validação
O framework deve suportar **validação por simulação parametrizada**, com cenários
reproduzíveis. (Ver seção 11.)

### RF-06 — Regulação / contexto brasileiro
O framework deve **verificar compatibilidade** com requisitos ANAC/DECEA e condicionantes
locais, de forma parametrizável.

### RF-07 — Apoio à tomada de decisão *(novo)*
O framework deve permitir ao usuário **configurar diferentes cenários operacionais e
comparar seus resultados** quanto à capacidade, nível de serviço, utilização da
infraestrutura, disponibilidade energética, desempenho da frota e atendimento aos
critérios de segurança operacional.

- **Critério de aceitação:** para um mesmo conjunto de condições operacionais, o framework
  deve permitir a comparação de **pelo menos duas alternativas** de planejamento,
  apresentando diferenças nos principais indicadores e **identificando as restrições
  responsáveis pela inviabilidade** de cada alternativa.
- **Justificativa:** aproxima o artefato do problema real — não apenas calcular capacidade,
  mas **apoiar decisões operacionais**.

---

## 9. Requisitos não funcionais (RNF)

| ID | Requisito | Observação |
|---|---|---|
| **RNF-01** | Reprodutibilidade: mesma entrada → mesma saída (seeds/configuração versionadas). | `[CONFIRMAR CONTRA O DOCX]` |
| **RNF-02** | Configurabilidade: parâmetros de vertiporto, frota, demanda, energia e regulação editáveis sem alterar código. | `[CONFIRMAR CONTRA O DOCX]` |
| **RNF-03** | **Rastreabilidade científica**: cadeia `premissa → requisito → implementação` (elevada a característica central — ver seção 12). | `[CONFIRMAR CONTRA O DOCX]` |
| **RNF-04** | Modularidade: cada modelo (A–F) isolável para experimentação e artigo próprio. | proposto |
| **RNF-05** | Extensibilidade: evolução de protótipo para software sem redesenho da arquitetura. | proposto |
| **RNF-06** | Transparência da decisão: toda recomendação ao decisor deve expor as restrições que a sustentam. | proposto (liga-se ao RF-07) |


---

## 10. Métricas e critérios de aceitação por componente

Cada critério de aceitação segue a tríade **métrica · baseline · limiar**. Sem *baseline*
ancorado, um critério não é verificável e vira alvo fácil de arguição.

| Modelo / Módulo | Métrica | Baseline (âncora) | Limiar de aceitação |
|---|---|---|---|
| **A — Capacidade** | Erro relativo da capacidade calculada | Modelo/benchmark de referência da literatura | ≤ `x%` `[DEFINIR + JUSTIFICAR]` |
| **B — Agendamento** | Taxa de atendimento da demanda; atraso médio/máximo | Demanda de entrada; agenda de referência | Atendimento ≥ limiar; atraso ≤ `y min` `[DEFINIR + JUSTIFICAR]` |
| **C — Energia** | Viabilidade de SoC (nº de violações de SoC mínimo) | SoC mínimo operacional parametrizado | 0 violações em solução aceita |
| **D — Rede** | Redução de rejeições / atrasos (rede vs. nós isolados) | Operação isolada dos vertiportos | Redução > 0 e estatisticamente relevante |
| **E — Segurança** | Nº de soluções aceitas que violam alvo de segurança | Alvo de segurança parametrizado (EASA/ANAC) | 0 (rejeição obrigatória) |
| **F — Regulação** | Nº de violações regulatórias não sinalizadas | Conjunto de regras ANAC/DECEA parametrizado | 0 |
| **RF-07 — Decisão** | Nº de alternativas comparáveis; rastreio da restrição limitante | — | ≥ 2 alternativas + restrição limitante identificada |

> **Regra geral de aceitação do artefato:** uma solução só é "aceita" se **passar
> simultaneamente** pelos guardrails E (segurança) e F (regulação). Soluções que violem
> segurança são **rejeitadas independentemente** de sua qualidade nos solvers 1–4.

---

## 11. Matriz de rastreabilidade (requisito → componente → variável → teste)

| Requisito | Modelo / Módulo | Variáveis principais | Teste de verificação |
|---|---|---|---|
| **RF-01** | A / Módulo 1 | slots, tempo de ocupação, turnaround, nº FATO/TLOF | T-01: erro relativo vs. benchmark ≤ `x%` |
| **RF-02** | B / Módulo 2 | alocação aeronave↔slot, movimentos, atraso | T-02: agenda viável, atendimento ≥ limiar, atraso ≤ `y` |
| **RF-03** | D / Módulo 4 | fluxos inter-nós, demanda redistribuída | T-03: rejeições(rede) < rejeições(isolado) |
| **RF-04** | E / Módulo 5 | alvo de segurança, sítios de contingência | T-04: toda solução violadora é rejeitada |
| **RF-05** | Validação | cenários, seeds, parâmetros | T-05: reprodutibilidade + cobertura de cenários |
| **RF-06** | F / Módulo 6 | regras ANAC/DECEA, condicionantes locais | T-06: 0 violações não sinalizadas |
| **RF-07** | Camada de decisão | conjunto de cenários, indicadores comparativos | T-07: ≥2 alternativas + restrição limitante exibida |
| **RNF-01** | Infra do protótipo | seed, config versionada | T-08: execução repetida → saída idêntica |
| **RNF-03** | Transversal | tags de rastreio premissa→resultado | T-09: cada resultado rastreável até a premissa |

> Esta matriz é o instrumento operacional de controle da tese: qualquer alteração em um
> requisito propaga-se de forma visível até o teste correspondente.


---

## 12. Estratégia de validação

A validade da tese **não pode depender** da disponibilidade de dados reais.

| Nível | Papel | Descrição |
|---|---|---|
| **Validação principal** | Obrigatória | **Simulação computacional parametrizada.** Cenários reproduzíveis, seeds versionadas, baselines de comparação explícitos. É o que sustenta a tese sozinho. |
| **Validação complementar** | Condicional | **Living Lab**, *se e somente se* houver dados adequados. Reforça, não fundamenta. |

> **Status do Living Lab:** `[disponibilidade de dados reais de operação no Living Lab: A VERIFICAR]`.
> Tratado como **validação complementar**, nunca como premissa. Se os dados não vierem ou
> forem insuficientes, a arquitetura metodológica permanece íntegra.

**Desenho experimental (simulação):** conjunto de cenários variando demanda (pico/fora-pico),
composição de frota, disponibilidade energética e topologia de rede (2 a 4 nós); cada cenário
executado sob os guardrails E/F; comparação de alternativas conforme RF-07.

---

## 13. Rastreabilidade científica (RNF-03 elevado a característica central)

Cada componente do artefato deve ser rastreável de ponta a ponta. É isto que demonstra que
o FIGOV **não é apenas um software** produzido pelo pesquisador, mas um **artefato
científico-tecnológico rastreável**.

```
Literatura / Regulação
        │
        ▼
     Premissa
        │
        ▼
     Requisito  (RF/RNF)
        │
        ▼
     Variável
        │
        ▼
      Modelo   (A–F)
        │
        ▼
    Algoritmo
        │
        ▼
  Implementação (protótipo, Nível 3)
        │
        ▼
       Teste   (T-01…T-09)
        │
        ▼
     Resultado
```

Recomendação: manter uma **tag de rastreio** (ex.: `RF-02`) atravessando premissa,
variável, código e teste, de modo que qualquer resultado no protótipo possa ser
percorrido de volta até a premissa/literatura que o originou.

---

## 14. Roadmap de artigos (incrementos sucessivos do artefato)

Os artigos deixam de ser trabalhos independentes e passam a ser **incrementos do artefato** —
adequado ao doutorado profissional.

| # | Título / foco | RF aprofundados | Objetivo |
|---|---|---|---|
| **Congresso / Artigo 1** | *Integrated Operational Management Framework for Urban Vertiports: Capacity, Fleet Scheduling and Energy Constraints* | RF-01 + RF-02 + energia | Estabelecer a **arquitetura** conceitual e computacional + caso inicial demonstrando que integrar as dimensões **altera** capacidade/scheduling. |
| **Artigo 2** | Fleet scheduling + energy | RF-02 (aprofundado) | Frotas heterogêneas, SoC, recarga, autonomia, restrições. |
| **Artigo 3** | Multi-vertiport network | RF-03 (aprofundado) | Operação em rede. |
| **Artigo 4** | Safety and regulatory acceptance | RF-04 + RF-06 | Segurança + contexto brasileiro. |
| **Tese / produto final** | FIGOV completo | Todos | Artefato validado + protótipo + documentação + diretrizes de implementação. |

> **Estratégia de congresso:** não apresentar o artefato completo. Apresentar a **primeira
> versão do framework**, concentrada na integração que constitui a lacuna científica
> (capacidade + scheduling + energia). A conclusão do artigo posiciona o framework como a
> arquitetura sobre a qual o artefato completo será desenvolvido e validado.

---

## 15. Pontos a fechar (checklist de conciliação com o orientador)

- [ ] Confirmar redação exata de RF-01…RF-06 e RNFs contra o `.docx`.
- [ ] **Definir e justificar** `x%` (RF-01) — via literatura/benchmark/dado empírico.
- [ ] **Definir e justificar** `y minutos` (RF-02).
- [ ] Confirmar RF-04 como **parametrizável** (alvo de segurança EASA/ANAC não fixado agora).
- [ ] Confirmar Living Lab como validação **complementar**, não premissa.
- [ ] Aprovar a inclusão do **RF-07** (apoio à decisão).
- [ ] Aprovar a **ordem de resolução sequencial iterativa** para o protótipo v1.
- [ ] Aprovar o **roadmap de artigos** e o recorte do artigo de congresso.

---

*Documento-base do FIGOV. Próximos passos possíveis: (i) detalhar o Nível 2 (operacional) —
parâmetros, variáveis e algoritmos por módulo; (ii) iniciar o Nível 3 (protótipo
computacional) a partir desta especificação.*
