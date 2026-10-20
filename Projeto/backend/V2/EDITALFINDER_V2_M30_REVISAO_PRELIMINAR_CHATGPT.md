# EditalFinder V2 — Revisão técnica independente (ChatGPT) da M3.0

**Origem examinada:** `V2.tar(20261019-050617).gz`. **Escopo:** corpus congelado M3.0, contratos, anotações provisórias, verificador, reprodutibilidade e testes offline. **Não substitui** revisão humana autorizada e **não é** o relatório oficial `EDITALFINDER_V2_M30_RESULTADOS.md` (ausente neste pacote).

## Parecer resumido

**READY técnico condicional para a preparação do corpus offline**, com ressalvas sobre a ausência do relatório final da milestone, revisão humana e possíveis decisões semânticas discutíveis (em especial o grau de confirmação de anúncio futuro em `M30-I06-R1`). **Não autoriza** M3.1 automaticamente, métricas de precisão/recall, publicação, cadastro em banco, crawling ou aceitação/promulgação de oportunidades. Os rótulos continuam **PROVISIONAL**.

O pacote disponibiliza **28 documentos reais** (26 HTML, 2 PDF), **33 registros**, **95 evidências** e o protocolo `m3.0-annotation-v1` com data de referência explícita `2026-10-19`. Não contém `EDITALFINDER_V2_M30_RESULTADOS.md`; essa ausência impede encerrar administrativamente a M3.0 como um conjunto completo de entregáveis até que o relatório seja criado.

## Execuções independentes

| Procedimento | Resultado |
|---|---|
| Verificador `PYTHONPATH=src python -B -m editalfinder_v2.dataset_m30 data/m3` | PASS: 28 documentos / 33 registros |
| Testes M3.0: `PYTHONPATH=src pytest -q -p no:cacheprovider tests/test_m30_dataset.py tests/test_m30_corpus.py` | 95 passed em 1.96 s |
| Suíte completa: `PYTHONPATH=src pytest -q -p no:cacheprovider` | **2095 passed** em 32.40 s, Python 3.13.5 / Pydantic 2.13.5 |
| Reprodução passiva das 28 visões textuais: `python -B data/m3/provenance/verify_derivation.py` | PASS: 28/28 |
| SHA-256 das cópias originais e visões derivadas + comprimentos originais | PASS: 28/28 |
| IDs e escopos de múltiplos registros | C05: 2, C07: 2, F01: 4; escopos distintos |
| PDF original `M30-F07` | 14 páginas, sem JavaScript/criptografia; página 1 inspecionada visualmente |
| PDF original `M30-I07` | 14 páginas, sem JavaScript/criptografia; página 12 inspecionada visualmente |

Os comandos Ruff/mypy/Git **não foram reproduzidos neste ambiente**; a evidência salva no pacote `data/m3/evaluation/verification.json` informa saída exit 0 para Ruff global, formatação, mypy e Git no ambiente do Hermes (Python 3.11.16).

## Resumo de cobertura e limitações

- Modalidades nos 33 registros: **13 crédito, 12 fomento, 8 investimentos**.
- Descoberta: **18 confirmadas, 1 anúncio futuro, 8 sinais, 6 não acionáveis**.
- Existência: **18 genuine, 9 uncertain, 6 not_opportunity**.
- Temporal: **9 open, 18 undetermined, 6 not_applicable**. Não há amostras `closed`, `continuous` ou `future` na referência congelada, o que limita a avaliação futura dessas classes.
- **Todos os 33 rótulos são provisórios;** nenhum possui aprovação humana autenticada.
- O piloto não é uma amostra aleatória ou representativa, e não fornece precisão/recall porque não existem previsões avaliadas contra rótulos humanos independentes.

## Revisão semântica contextual

As 33 anotações foram inspecionadas contra os trechos citados, seus escopos no texto congelado, a justificativa e as incertezas. A correspondência formal de offsets, páginas e campos foi verificada pelo validador; também foram lidos trechos adjacentes nos casos de alto risco. A revisão é **AI-assisted**, não certifica autoria, veracidade institucional ou disponibilidade atual na web.

| Registro | Modalidade | Descoberta | Temporal | Nota principal da revisão |
|---|---|---|---|---|
| `M30-C01-R1` | credito | confirmed_opportunity | undetermined | Produto de crédito com público, finalidade e rota de solicitação; temporal conservador. |
| `M30-C02-R1` | credito | confirmed_opportunity | undetermined | Produto de crédito com público, finalidade e rota de solicitação; temporal conservador. |
| `M30-C03-R1` | credito | confirmed_opportunity | undetermined | Produto de crédito com público, finalidade e rota de solicitação; temporal conservador. |
| `M30-C04-R1` | credito | confirmed_opportunity | undetermined | Produto de crédito com público, finalidade e rota de solicitação; temporal conservador. |
| `M30-C05-R1` | credito | opportunity_signal | undetermined | Página índice Finame, sinal sem condições completas. |
| `M30-C05-R2` | credito | confirmed_opportunity | undetermined | Finame Direto distinto com possibilidade de solicitar crédito. |
| `M30-C06-R1` | credito | confirmed_opportunity | undetermined | Título Inova Mais RS e caminho URL mais-inovacao divergentes; explicitamente não reconciliados. |
| `M30-C07-R1` | credito | unrelated_or_non_actionable | not_applicable | Empréstimo concedido a empresa identificada, não nova oferta. |
| `M30-C07-R2` | credito | confirmed_opportunity | undetermined | Outro registro na mesma notícia descreve CrediTur RS e elegibilidade; janela indeterminada. |
| `M30-C08-R1` | credito | opportunity_signal | undetermined | Índice BRDE sem linha/elegibilidade completa nesta unidade. |
| `M30-F01-R1` | fomento | confirmed_opportunity | open | Prazo MAI/DAI explícito na listagem; edital PDF integral não congelado. |
| `M30-F01-R2` | fomento | confirmed_opportunity | open | ARC com período explícito em unidade distinta da listagem. |
| `M30-F01-R3` | fomento | confirmed_opportunity | open | Chamada Brasil–França com período separado. |
| `M30-F01-R4` | fomento | confirmed_opportunity | open | Bolsas CNPq 33/2026; relação com F02/F07 não fundida. |
| `M30-F02-R1` | fomento | confirmed_opportunity | open | Prazo claro, mas retificação de anexo não foi congelada. |
| `M30-F03-R1` | fomento | opportunity_signal | undetermined | Pasta/índice sem prazo na unidade; não importa prazo de F01/F08. |
| `M30-F05-R1` | fomento | confirmed_opportunity | open | Notícia de chamada mineral com inscrições abertas e prazo futuro; não é negativo automático. |
| `M30-F06-R1` | fomento | confirmed_opportunity | open | Etapa nacional Eureka restrita a consórcios com Selo; não inventa elegibilidade geral. |
| `M30-F07-R1` | fomento | confirmed_opportunity | open | PDF original de 14 páginas; cronograma e objeto verificáveis; metadata “Minuta” e retificação exigem ressalva. |
| `M30-F08-R1` | fomento | confirmed_opportunity | open | MAI/DAI em página própria; mesma família que F01 sem fusão automática. |
| `M30-I01-R1` | investimentos | opportunity_signal | undetermined | Tese e público do fundo, mas não há canal comprovado na unidade. |
| `M30-I02-R1` | investimentos | confirmed_opportunity | undetermined | Convite explícito de submissão Criatec 4; sem inferir fluxo temporal contínuo. |
| `M30-I03-R1` | investimentos | unrelated_or_non_actionable | not_applicable | Portfólio já investido, corretamente separado de captação. |
| `M30-I04-R1` | investimentos | confirmed_opportunity | undetermined | Inscrição para análise de startup; ausência de prazo não implica aberto/contínuo. |
| `M30-I05-R1` | investimentos | opportunity_signal | undetermined | Inscrição encerrada era para gestor do FIP, não startups. |
| `M30-I06-R1` | investimentos | announced_future_opportunity | undetermined | Fundo de IA em diligência/estruturação; anúncio futuro é interpretação plausível porém revisável; janela de startup desconhecida. |
| `M30-I07-R1` | investimentos | opportunity_signal | undetermined | PDF BRDE pág. 12 fala da captação de FIPs; não equivale a chamada de startups. |
| `M30-I08-R1` | investimentos | opportunity_signal | undetermined | Critérios para fundos/gestores; não candidatura de startups. |
| `M30-N01-R1` | credito | unrelated_or_non_actionable | not_applicable | Crédito já concedido à Renault; futuro lançamento de veículo não é futura inscrição. |
| `M30-N02-R1` | credito | unrelated_or_non_actionable | not_applicable | Crédito já concedido ao Butantan; produção futura não abre candidatura. |
| `M30-N03-R1` | fomento | unrelated_or_non_actionable | not_applicable | Resultado de prêmio Finep, sem nova seleção. |
| `M30-N04-R1` | fomento | unrelated_or_non_actionable | not_applicable | Suplementação para propostas previamente analisadas; não abre nova janela. |
| `M30-S01-R1` | credito | opportunity_signal | undetermined | ProFloresta+2: potencial de crédito separado de compras de carbono e acordo sem transferência de recursos. |


## Provas adversariais próprias (sobre cópia temporária)

| Mutação | Resultado | Interpretação |
|---|---|---|
| Transplantar evidência de C07-R2 para C07-R1, mantendo campo original | REJECT | Contrato de campo/evidência detecta ausência do valor citado |
| Trocar a página da evidência F07-E1 de 1 para 2 | REJECT | Validação de páginas do PDF funciona |
| Alterar `review_status` de I06 para `approved` | REJECT | Não há aprovação humana forjada |
| Alterar `temporal_status` I06 de `undetermined` para `future` | ACCEPT | **Limite esperado:** o verificador não prova verdade semântica; revisão de rótulo indispensável |
| Reclassificar notícia N04 indevidamente como confirmada, atualizando campos coerentemente | ACCEPT | **Limite esperado:** esquema garante coerência, não entailment do texto |

Esses dois últimos casos não são uma regressão em relação ao contrato declarado: o verificador *explicitamente* não certifica semântica, autoria, atualidade ou verdade dos rótulos. Evidenciam o motivo para manter status `provisional`.

## Pendências a registrar no relatório oficial

1. **Relatório M3.0 ausente:** produzir `EDITALFINDER_V2_M30_RESULTADOS.md` com comandos executados, escopo, aquisições, cobertura, fontes e limites. Não esperar uma falsa revisão independente do Hermes: registrar o bloqueio HTTP 429 e a impossibilidade de execução, se permanecer.
2. **M30-I06-R1:** a notícia comprova seleção de gestora, estimativa de fundo e fase de diligência; não comprova janela de candidaturas para startups. `announced_future_opportunity` é defensável como **descoberta futura provisória**, mas um revisor humano pode preferir `opportunity_signal`; preservar `temporal_status=undetermined`.
3. **M30-F01:** listagem oficial permite a classificação de janela, mas PDFs integrais das chamadas listadas não foram todos congelados; não afirmar verificação completa de elegibilidade.
4. **M30-F07:** a versão congelada do edital CNPq tem metadados PDF “Minuta” e o link institucional menciona alteração de Anexo I não congelada; documentar cobertura parcial de regras.
5. **M30-I07:** documento institucional descreve FIPs em captação; isso não prova estágio de candidaturas de startups nem atualidade da captação em outubro.
6. **Cobertura temporal restrita:** nenhum exemplo de janela fechada, futura datada ou contínua na amostra real; a exclusão `M30-F04` por estar encerrado está justificada pelo escopo prospectivo, não como `not_opportunity`.
7. **Classes/anotações provisórias:** a composição intencional da amostra não fundamenta estatísticas gerais, nem revisão humana certificada.
8. **Limites herdados:** F02 (observabilidade do oráculo) e F04 (URL M1/M2.1) da M2.3d permanecem conhecidos; evitar confundir `M23D-F04` com `M30-F04` (o documento histórico excluído).

## Veredito e continuidade

**Parecer técnico: READY condicional para o corpus offline M3.0 enquanto material de pesquisa e avaliação exploratória, não como conjunto de ground truth aprovado.** O **marco M3.0 ainda não está formalmente encerrado** enquanto faltar seu relatório de resultados e confirmação de revisão independente pendente; ambas podem ser registradas honestamente, sem suspender o trabalho ou inventar uma auditoria.

Recomenda-se que o agente principal produza o relatório oficial **sem relançar aquisição nem modificar o corpus**, e então submeta o pacote congelado a revisão humana/independente quando disponível. Não iniciar M3.1 automaticamente.
