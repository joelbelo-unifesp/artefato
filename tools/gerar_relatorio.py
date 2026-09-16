"""Gera o PDF de acompanhamento do artefato FIGOV para apresentação ao orientador.

Uso: PYTHONPATH=tools python tools/gerar_relatorio.py
Saída: docs/FIGOV-Relatorio-de-Andamento.pdf
"""

from __future__ import annotations

import datetime as _dt
from pdfgen import PDF


def build():
    pdf = PDF()
    hoje = "14 de setembro de 2026"

    # --- Capa / cabeçalho --------------------------------------------------
    pdf.title("FIGOV — Relatório de Andamento do Artefato")
    pdf.para("Framework Integrado de Gestão Operacional de Vertiportos", size=11)
    pdf.small(f"Documento de acompanhamento para orientação  |  {hoje}  |  Autor: Joel Belo")
    pdf.small("Natureza: artefato científico-tecnológico de apoio à decisão (Design Science Research)")
    pdf.rule()

    # --- 1. Sumário executivo ---------------------------------------------
    pdf.h1("1. Sumário executivo")
    pdf.para(
        "O artefato FIGOV avançou da fase de especificação para a de protótipo "
        "computacional funcional. Encontra-se implementada uma primeira versão executável "
        "(MVP) que integra as seis dimensões previstas — capacidade, agendamento de frota "
        "heterogênea, energia, coordenação em rede, segurança e diretrizes regulatórias — "
        "e adiciona uma camada de apoio à decisão. Todos os requisitos funcionais "
        "(RF-01 a RF-07) possuem implementação verificável por testes automatizados."
    )
    pdf.bullet("Nível 1 (framework conceitual): consolidado na especificação.")
    pdf.bullet("Nível 2 (framework operacional): parâmetros, variáveis, algoritmos e critérios definidos.")
    pdf.bullet("Nível 3 (protótipo computacional): implementado e executável (MVP).")
    pdf.spacer(2)
    pdf.para(
        "Situação-chave para a banca: à pergunta \"onde está o produto tecnológico?\", a "
        "resposta agora é um protótipo que recebe dados, gera e avalia agendas, identifica "
        "conflitos, verifica restrições, rejeita soluções inseguras e compara cenários."
    )

    # --- 2. Números do protótipo ------------------------------------------
    pdf.h1("2. Estado atual do protótipo (números)")
    pdf.table(
        ["Indicador", "Valor"],
        [
            ["Requisitos funcionais implementados", "RF-01 a RF-07 (7 de 7)"],
            ["Linhas de código (pacote figov)", "aprox. 1.900"],
            ["Testes automatizados", "29 (100% aprovados)"],
            ["Dependências externas de runtime", "nenhuma (apenas biblioteca padrão)"],
            ["Interface", "CLI: run / comparar / validar"],
            ["Reprodutibilidade", "determinística por semente (RNF-01)"],
        ],
        widths=[300, 183],
    )

    # --- 3. Cobertura por requisito ---------------------------------------
    pdf.h1("3. Cobertura por requisito")
    pdf.table(
        ["Req.", "Componente", "Situação / evidência"],
        [
            ["RF-01", "Capacidade", "Capacidade teórica e prática + fila M/M/c + simulação de eventos discretos de referência (10 réplicas). Comparação analítico x simulado converge (desvios de 5,1% e 4,1%)."],
            ["RF-02", "Agendamento", "Frota heterogênea com energia (SoC/recarga). Cerca de 2.800 passageiros/dia agendados em menos de 10 ms (critério: 60 s). Toda rejeição indica a restrição violada."],
            ["RF-03", "Rede", "Coordenação de 2 a 4 vertiportos. Operação em rede eleva o atendimento de 4% (isolado) para 81% (rede); melhoria robusta em 10 de 10 sementes."],
            ["RF-04", "Segurança", "Guardrail transversal: risco ar-solo parametrizável, sítios de contingência obrigatórios, rejeição automática com indicação explícita."],
            ["RF-05", "Validação", "Pipeline sequencial iterativo + protocolo documentado + rastreabilidade simulado x real (Living Lab: A VERIFICAR)."],
            ["RF-06", "Regulação/Brasil", "13 diretrizes de implementação; referências externas marcadas como PENDENTE DE FONTE (nenhuma referência inventada)."],
            ["RF-07", "Apoio à decisão", "Comparação de pelo menos duas alternativas com identificação da restrição limitante."],
        ],
        widths=[40, 92, 351],
    )

    # --- 4. Resultado científico central ----------------------------------
    pdf.h1("4. Resultado preliminar de maior relevância científica")
    pdf.para(
        "A comparação entre operação isolada e coordenada em rede é a evidência que "
        "sustenta a lacuna científica do trabalho: a integração das dimensões altera "
        "materialmente as decisões operacionais."
    )
    pdf.table(
        ["Modo de operação", "Atendimento (exemplo, 3 nós)", "Restrição limitante"],
        [
            ["Isolado (nós independentes)", "aprox. 4%", "frota/energia por nó"],
            ["Coordenado em rede", "aprox. 81%", "capacidade do vertiporto"],
        ],
        widths=[200, 170, 113],
    )
    pdf.small(
        "Observação: o baseline isolado é deliberadamente severo (frota particionada por "
        "nó, sem compartilhamento). Serve para evidenciar o ganho da coordenação; um "
        "baseline mais fino é um refinamento previsto."
    )

    # --- 5. Decisões metodológicas e integridade --------------------------
    pdf.h1("5. Decisões metodológicas e integridade dos dados")
    pdf.bullet(
        "Valores em aberto tratados como parâmetros, não como constantes: o desvio máximo "
        "de capacidade (x%), o atraso aceitável (y min), o nível alvo de segurança e o "
        "número de réplicas estão marcados como A DEFINIR e implementados como configuração."
    )
    pdf.bullet(
        "Nenhum valor foi atribuído a fontes de literatura sem justificativa: os números "
        "presentes são espaços reservados operacionais, explicitamente sinalizados."
    )
    pdf.bullet(
        "Referências regulatórias (RF-06) permanecem como PENDENTE DE FONTE, a preencher "
        "na fonte primária (ANAC/DECEA/EASA)."
    )
    pdf.bullet(
        "Living Lab (Sapiens Parque) tratado como validação complementar, condicional à "
        "disponibilidade de dados reais; a validação principal por simulação sustenta a tese."
    )
    pdf.bullet(
        "Rastreabilidade científica (premissa -> requisito -> implementação -> teste) "
        "adotada como característica central do artefato."
    )

    # --- 6. Ajuste de rota durante a implementação ------------------------
    pdf.h1("6. Ajuste técnico relevante registrado")
    pdf.para(
        "Durante a implementação identificou-se que, sem a realimentação Energia -> "
        "Agendamento, a frota nunca recarregava e o atendimento estagnava (cerca de 10%). "
        "A correção — recarga pelo tempo ocioso antes de avaliar a viabilidade energética — "
        "elevou o atendimento para cerca de 87% e tornou a agenda energeticamente "
        "consistente. O episódio confirma, na prática, o acoplamento entre dimensões "
        "previsto na especificação (grafo de dependências)."
    )

    # --- 7. Situação das tarefas ------------------------------------------
    pdf.h1("7. Situação das tarefas de implementação")
    pdf.table(
        ["Tarefa", "Descrição", "Situação"],
        [
            ["Tarefa 0", "Estrutura do repositório e schemas de entrada", "Concluída"],
            ["Tarefa 1", "RF-01 Capacidade", "Concluída"],
            ["Tarefa 2", "RF-02 Agendamento de frota heterogênea", "Concluída"],
            ["Tarefa 3", "RF-03 Coordenação multi-vertiporto", "Concluída"],
            ["Tarefa 4", "RF-04 Segurança operacional", "Concluída"],
            ["Tarefa 5", "RF-05 Protocolo de validação", "Concluída"],
            ["Tarefa 6", "RF-06 Diretrizes para o Brasil", "Concluída"],
        ],
        widths=[70, 313, 100],
    )

    # --- 8. Próximos passos -----------------------------------------------
    pdf.h1("8. Próximos passos propostos")
    pdf.bullet("Definir e justificar os limiares em aberto (x%, y min, nível de segurança).")
    pdf.bullet("Preencher as referências regulatórias na fonte primária (ANAC/DECEA/EASA).")
    pdf.bullet("Refinar o baseline de operação isolada para uma comparação mais conservadora.")
    pdf.bullet("Avaliar a otimização acoplada como alternativa à heurística (trabalho futuro / artigo).")
    pdf.bullet("Verificar a disponibilidade de dados reais do Living Lab (validação complementar).")
    pdf.bullet("Preparar o recorte do artigo de congresso (capacidade + agendamento + energia).")

    # --- 9. Questões para o orientador ------------------------------------
    pdf.h1("9. Pontos para decisão em orientação")
    pdf.bullet("Aprovação da inclusão do RF-07 (apoio à decisão) como requisito.")
    pdf.bullet("Aprovação da ordem de resolução sequencial iterativa para o protótipo v1.")
    pdf.bullet("Validação do recorte e do cronograma do primeiro artigo.")
    pdf.bullet("Direcionamento sobre os limiares numéricos e suas fontes.")

    pdf.rule()
    pdf.small(
        "Este relatório reflete o estado do protótipo na data indicada. Métricas de "
        "execução (atendimento, atrasos, desvios) referem-se a cenários de exemplo "
        "parametrizados e reprodutíveis; os limiares de aceitação permanecem A DEFINIR."
    )
    return pdf


if __name__ == "__main__":
    pdf = build()
    out = "docs/FIGOV-Relatorio-de-Andamento.pdf"
    pdf.save(out)
    print("PDF gerado:", out)
