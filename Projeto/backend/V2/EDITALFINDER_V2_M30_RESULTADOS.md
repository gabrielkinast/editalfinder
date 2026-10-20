# EditalFinder V2 — M3.0: resultados do piloto documental congelado

## 1. Parecer e limite de encerramento

**Preparação técnica do corpus offline: READY condicional. Revisão independente originalmente solicitada: NÃO CONCLUÍDA, interrompida por HTTP 429. M3.1: NÃO INICIADA.**

Este relatório completa o entregável documental ausente da M3.0; não declara concluída a revisão pendente nem transforma o corpus em referência humana aprovada. READY refere-se exclusivamente à preparação técnica para pesquisa offline, condicionada às limitações abaixo. Não significa aprovação semântica, prontidão de fontes ou autorização para produção.

O bloqueio HTTP 429 da revisão independente originalmente solicitada é registrado conforme o histórico informado na retomada e a pendência descrita em `EDITALFINDER_V2_M30_REVISAO_PRELIMINAR_CHATGPT.md`, seção “Pendências”. Não houve nova tentativa nesta retomada; não se inventam execução, parecer, identidade do revisor ou log de resposta ausente. A revisão preliminar ChatGPT existente é uma evidência separada, AI-assisted; não sana esse bloqueio, não equivale à revisão originalmente solicitada e não autentica aprovação humana.

Foram preservados os **33 registros com `review_status=provisional`**, sem relabeling, fusões ou alteração de evidências. Nenhuma aquisição foi repetida, e nenhum arquivo de `data/m3` foi alterado. Não foram iniciados adaptador, previsões, avaliação de extração, integração de domínio ou atividades da M3.1.

## 2. Base documental e proveniência

Fontes locais autoritativas, relativas a `backend/V2`:

- [Manifesto](data/m3/corpus_manifest.json): IDs, URLs originais/finais, coleta UTC, tipo, tamanho, caminhos, hashes separados de original e visão textual, autoridade e restrições.
- [Anotações estruturadas](data/m3/annotations/records.json) e [referência legível](data/m3/annotations/REFERENCE_LABELS.md): rótulos, campos literais, escopos, justificativas, incertezas e evidências.
- [Cobertura](data/m3/evaluation/coverage.json): contagens, lacunas e `metrics=null`.
- [Verificação original](data/m3/evaluation/verification.json): execuções efetivamente registradas e versões do ambiente original.
- [Protocolo](data/m3/annotation_protocol.md) e [README](data/m3/README.md): rubrica, fronteiras e governança.
- [Exclusões](data/m3/provenance/acquisition_exclusions.json), manifestos auxiliares `provenance/*acquired.json`, seleções e curadorias: histórico, não substitutos do manifesto final.
- [Alinhamento contratual](data/m3/provenance/CONTRACT_ALIGNMENT_REVIEW.md) e [revisão preliminar ChatGPT](EDITALFINDER_V2_M30_REVISAO_PRELIMINAR_CHATGPT.md): ressalvas de arquitetura e semântica.

Dataset `m3.0-pilot-v1`, protocolo `m3.0-annotation-v1`, dia civil de referência **2026-10-19**. Esse dia é fixo, não “hoje” implícito. Coletas dos documentos incluídos: de `2026-10-19T04:37:38.233146+00:00` a `2026-10-19T04:43:35.657879+00:00`, segundo o manifesto. Esta retomada apenas leu os artefatos existentes e executou verificações locais.

Há 28 documentos reais: 26 HTML e 2 PDF; originais totalizam 6.466.530 bytes, maior original 2.831.952 bytes. O manifesto registra 14 datas de publicação não nulas; datas/versões nulas continuam não verificadas. URL com ano, metadados de criação e cronograma de lançamento não foram promovidos a data de publicação. Os detalhes por documento e URLs estão no manifesto e no inventário ao final.

As visões HTML são derivações passivas, sem execução de scripts, e podem conter navegação/texto não visível. Os PDFs usam `pdftotext`, páginas físicas 1-based e separadores formfeed, sem inferência por página impressa. Offsets são `[start,end)` em caracteres Unicode na visão congelada, não bytes do HTML nem ponteiros nativos RFC6901. A reprodução foi comparada em memória/saída padrão; não se regeneraram visões em seus caminhos congelados.

`M30-F04` não integra os 28 documentos nem os 33 rótulos: foi excluído por chamada histórica encerrada no escopo prospectivo, **não** por inexistência de oportunidade. O log preserva a rejeição da proposta preliminar de usar expiração como `not_opportunity`. Seus caminhos históricos não indicam presença no release atual. Falhas de aquisição e rascunhos não contam como documentos ou negativos. Não há nova aquisição nem complementação de quota neste relatório.

Hospedagem institucional é observação de proveniência, não autenticação criptográfica de autoria, licença de redistribuição ou prova de disponibilidade atual. As cópias são material local controlado, não documentos ativos para execução.

## 3. Cobertura efetivamente observada

Contagens de `coverage.json` foram recalculadas a partir do manifesto e das anotações nesta retomada; tipos, fontes, categorias, modalidades, classes, campos anotados, evidências, bytes e datas não nulas coincidiram. Não são métricas de qualidade do modelo.

| Dimensão | Distribuição |
|---|---|
| Documentos por organização | BNDES 11; BRDE 4; CNPq 5; MCTI 2; Criatec 4 4; Finep 2 |
| Categoria documental | financing_program 5; program_information 6; institutional_news 9; application_call 6; investment_program 1; selection_result 1 |
| Modalidade dos registros | credito 13; fomento 12; investimentos 8 |
| Documentos por modalidade (contagem não exclusiva) | credito 11; fomento 9; investimentos 8 |
| Descoberta | confirmed_opportunity 18; opportunity_signal 8; unrelated_or_non_actionable 6; announced_future_opportunity 1 |
| Existência | genuine_opportunity 18; uncertain 9; not_opportunity 6 |
| Temporal | open 9; undetermined 18; not_applicable 6 |
| Revisão | provisional 33; nenhum aprovado |
| Evidências | 95 itens |

Os rótulos de existência, descoberta e janela temporal são dimensões distintas. `confirmed_opportunity` é nome de uma classe provisória: não certificação externa. O anúncio futuro de descoberta não implica `temporal_status=future`. Ausência de prazo, botão de solicitação ou página acessível não comprova janela aberta/contínua.

Não há exemplos reais `closed`, `continuous` ou `future` na referência temporal congelada. Todas as classes de descoberta estão presentes formalmente, mas a única ocorrência de anúncio futuro é semanticamente discutível (I06). Não se presume cobertura robusta dessa classe. Casos sintéticos não preenchem lacunas do corpus real.

`M30-C05` contém 2 registros, `M30-C07` contém 2 e `M30-F01` contém 4, com escopos próprios. Registros/documentos não são oportunidades canônicas únicas: relações aparentes entre F01/F02/F07/F08 não foram fundidas. Conteúdo fora dos escopos anotados é não avaliado, não negativo implícito. A amostra é intencional, não aleatória nem representativa. Não foram comparadas previsões com referência humana independente; portanto **não há precisão, recall, F1 ou estimativas populacionais**.

## 4. Observações verificadas versus decisões semânticas provisórias

“Verificado” abaixo distingue correspondência documental/estrutural de verdade semântica. Os julgamentos de classe permanecem provisórios mesmo quando seus trechos e offsets são válidos.

| Caso | Observação documental/estrutural | Decisão preservada e ressalva |
|---|---|---|
| M30-I06-R1 | E2 informa seleção da Monashees e etapa de análise, diligência e estruturação; E3/E4 descrevem fundo e público de startups. Não há abertura/prazo de candidatura de startups demonstrado. | Preservar announced_future_opportunity / uncertain / undetermined. Anúncio futuro é interpretação plausível, não confirmação de acesso futuro; um revisor humano pode preferir opportunity_signal. Não mudar para temporal future; capital estimado não é ticket individual. |
| M30-F01 | Quatro unidades da listagem têm períodos explícitos, com evidências próprias. | Preservar os quatro confirmed/open; listagem não é verificação integral de elegibilidade. Nem todos os PDFs completos foram congelados; paginação não foi seguida. |
| M30-F02 e M30-F07 | A anotação F07 registra PDF de 14 páginas, cronograma e objeto, metadado “Minuta” e ressalva de alteração de Anexo I indicada em F02, não congelada. | Preservar confirmed/open; regras e retificação têm cobertura parcial. Não afirmar versão normativa integralmente atualizada nem autenticação do edital. Inspeção visual de páginas e metadados relatada pela revisão ChatGPT não foi repetida nesta retomada. |
| M30-I07-R1 | Evidências da página física 12 descrevem FIPs em captação e Sul Ventures. | Preservar signal/uncertain/undetermined; captação do fundo não demonstra candidatura de startups ou captação vigente em outubro. Pasta /2026/01/ não prova publicação. |
| M30-I05 e M30-I08 | Material descreve seleção/condições para gestores ou fundos. | Manter sinais, sem inventar candidatura ou prazo de startups. |
| M30-C06-R1 | Título Inova Mais RS difere do caminho URL mais-inovacao. | Divergência explicitamente não reconciliada; não normalizar identidade automaticamente. |
| M30-C07 | A mesma notícia contém negócio concluído e descrição de programa em unidades distintas. | Preservar C07-R1 não acionável e C07-R2 confirmado, com janela indeterminada; não transplantar condições entre unidades. |
| M30-N01/N02/N03/N04 | Financiamentos concedidos, resultado de prêmio e suplementação para propostas já analisadas são o conteúdo dos registros. | Não acionáveis como nova candidatura, sem negar existência histórica dos programas. Desembolso, fabricação futura ou suplementação não criam janela de inscrição. |
| M30-F05/F06 | Notícias contêm linguagem de submissão e prazo; Eureka descreve etapa nacional condicionada a consórcios com Selo. | Notícias não são negativas por gênero; preservar confirmed/open sem ampliar elegibilidade. |
| M30-S01-R1 | Evidência distingue potencial de crédito, compras de carbono e acordo sem transferência de recursos. | Preservar signal/uncertain/undetermined; não converter todos os componentes em subvenção ou chamada aberta. |

O verificador prova schema, hashes, escopos, citações literais, vínculos de campos, limites de páginas e contradições estruturais previstas. **Não prova entailment, verdade dos rótulos, autoria, atualidade, licença ou autorização de revisão.**

A revisão ChatGPT relata provas adversariais em cópia temporária: rejeitou transplante de evidência C07, página incorreta F07 e `review_status=approved`; aceitou I06 temporal `future` e N04 indevidamente confirmado quando os campos foram ajustados coerentemente. São achados atribuídos à revisão, não mutações repetidas nesta retomada nem resultados do corpus intacto. Os dois ACCEPT demonstram limite semântico do contrato, não aprovação dessas interpretações. Justificam manter a revisão autorizada pendente e todos os rótulos provisórios.

## 5. Testes e verificações: três proveniências distintas

### 5.1 Execução original preservada em evaluation/verification.json

O arquivo registra `all_gates_passed=true`, todos os comandos com exit 0: suíte pytest (duração externa 18,89 s), Ruff, formatação, mypy, Git, Ruff dos scripts de proveniência, reprodução textual e CLI do dataset. A saída pytest salva contém truncamento e **não expõe seu resumo final de contagem**; não se deduz dela uma linha “2095 passed”. As contagens de testes abaixo provêm de execuções que efetivamente as expõem.

Saídas originais explícitas: Ruff `All checks passed!`; formatação `89 files already formatted` em src/tests e `4 files already formatted` em provenance; mypy `Success: no issues found in 29 source files`; derivação PASS 28 documentos; CLI `Validated 28 documents and 33 records (m3.0-pilot-v1; m3.0-annotation-v1)`; `git diff --check` sem saída. Versões registradas: Python 3.11.16, pytest 9.1.1, Pydantic 2.14.1, pydantic-core 2.50.1, Ruff 0.17.1, mypy 2.4.0, pdftotext 26.01.0 e Git 2.53.0.

O registro original também declara 154 arquivos preexistentes verificados sem mudanças, índice vazio inalterado e exclusão SQL preexistente preservada. Essas são afirmações da execução original, não reconstrução do estado histórico pela retomada.

### 5.2 Execuções relatadas pela revisão preliminar ChatGPT

A revisão existente relata CLI PASS 28/33; testes M3.0 **95 passed em 1,96 s**; suíte completa **2095 passed em 32,40 s**, em Python 3.13.5/Pydantic 2.13.5; reprodução e hashes PASS 28/28. Relata ainda inspeção passiva dos PDFs e os testes adversariais acima. Ruff/mypy/Git não foram reproduzidos naquele ambiente. São resultados atribuídos ao parecer existente, não evidência de conclusão da revisão originalmente bloqueada por HTTP 429.

### 5.3 Reexecução local nesta retomada

Comandos executados de `backend/V2`, no ambiente `.venv` existente, com `PYTHONPATH=src` e `PYTHONDONTWRITEBYTECODE=1`; Python 3.11.16. Sem rede, aquisição ou alteração do corpus. Tempos pytest abaixo são os impressos pelo próprio pytest, não duração externa do processo.

| Comando | Resultado real nesta retomada | Exit |
|---|---|---|
| `.venv/bin/python -B -m editalfinder_v2.dataset_m30 data/m3` | Validated 28 documents and 33 records (m3.0-pilot-v1; m3.0-annotation-v1) | 0 |
| `.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_m30_dataset.py tests/test_m30_corpus.py` | **95 passed in 0.39s** | 0 |
| `.venv/bin/python -B -m pytest -q -p no:cacheprovider` | **2095 passed in 20.31s** | 0 |
| `.venv/bin/ruff check --no-cache src tests data/m3/provenance` | All checks passed! | 0 |
| `.venv/bin/ruff format --check --no-cache src tests data/m3/provenance` | 93 files already formatted | 0 |
| `.venv/bin/mypy --no-incremental --cache-dir=/dev/null src` | Success: no issues found in 29 source files | 0 |
| `.venv/bin/python -B data/m3/provenance/verify_derivation.py` | PASS; 28 documentos reproduzidos | 0 |
| `git diff --check` | sem saída | 0 |

`git diff --check` não cobre por si só arquivos não rastreados, incluindo este relatório. O corpus é verificado por hashes; whitespace de originais/visões não é reescrito. A árvore já continha alterações e arquivos não rastreados anteriores à retomada, além de exclusão SQL preexistente; não houve limpeza, staging ou commit.

A evidência JSON integral da reexecução está no caminho local abaixo (scratch transitório, não novo artefato congelado). O resumo acima permanece neste relatório mesmo após eventual expiração do scratch.

/home/lorenzozm/.hermes/cache/scratch/m30_report_reverification.json

Início UTC da reexecução: `2026-10-19T19:31:43.478160+00:00`.

## 6. Integridade e fronteiras preservadas

O corpus continua uma camada documental de avaliação: HTML/PDF original não é `RawSnapshot` JSON sanitizado; spans/páginas não são `DocumentUnit`; registros não são `OpportunityCandidate`; fonte, publicador, financiador e identidade canônica continuam separados. Crédito não vira teto de proposta de subvenção; capital de fundo não vira ticket. Nenhuma taxonomia de produção, UUID canônico, fusão, publicação ou escrita Supabase/SQL foi criada.

Permanecem conhecidos os limites herdados M2.3d: F02 (observabilidade do oráculo) e F04 (fronteira de URL M1/M2.1). Não confundir `M23D-F04` com o documento excluído `M30-F04`. M3.0 não os corrige nem altera o oráculo sintético M2.3c.

Hashes SHA-256 dos artefatos usados, calculados nesta retomada; servem como identidade de conteúdo, não assinatura de aprovação:

| Artefato relativo a data/m3 | SHA-256 |
|---|---|
| `corpus_manifest.json` | `841fb92e3bb353c5dd511a99f38901b2bb24ba20285ba508342598e3a6c7bdfa` |
| `annotations/records.json` | `515da22ed1e2a94e3b2815a07fb740e7481c99fe8d8dbb21c6ef97a518d99df7` |
| `annotations/REFERENCE_LABELS.md` | `aaeba43394f0653c0855d5e5d2524f83f9e269fc77f1452e70f868c2d84d1874` |
| `evaluation/coverage.json` | `f07903b5f5ab1dd12e834d70929ec81565996b3e58cdea2129d190979a5283ca` |
| `evaluation/verification.json` | `cab9d8418f48b2ae579ae4e8303506e279f57c767d602a353f7a1fe4627bd1ca` |
| `annotation_protocol.md` | `b35446518b219904d50d3bb390bd87b9949bf795d7fb29507a2fef2d566036bd` |

## 7. Inventário dos 33 rótulos preservados

Transcrição programática de `annotations/records.json`; todos têm `review_status=provisional` e referência `2026-10-19`. A tabela não adjudica classes nem substitui as evidências, campos e justificativas originais.

| Registro | Modalidade | Descoberta | Existência | Temporal |
|---|---|---|---|---|
| `M30-C01-R1` | `credito` | `confirmed_opportunity` | `genuine_opportunity` | `undetermined` |
| `M30-C02-R1` | `credito` | `confirmed_opportunity` | `genuine_opportunity` | `undetermined` |
| `M30-C03-R1` | `credito` | `confirmed_opportunity` | `genuine_opportunity` | `undetermined` |
| `M30-C04-R1` | `credito` | `confirmed_opportunity` | `genuine_opportunity` | `undetermined` |
| `M30-C05-R1` | `credito` | `opportunity_signal` | `uncertain` | `undetermined` |
| `M30-C05-R2` | `credito` | `confirmed_opportunity` | `genuine_opportunity` | `undetermined` |
| `M30-C06-R1` | `credito` | `confirmed_opportunity` | `genuine_opportunity` | `undetermined` |
| `M30-C07-R1` | `credito` | `unrelated_or_non_actionable` | `not_opportunity` | `not_applicable` |
| `M30-C07-R2` | `credito` | `confirmed_opportunity` | `genuine_opportunity` | `undetermined` |
| `M30-C08-R1` | `credito` | `opportunity_signal` | `uncertain` | `undetermined` |
| `M30-F01-R1` | `fomento` | `confirmed_opportunity` | `genuine_opportunity` | `open` |
| `M30-F01-R2` | `fomento` | `confirmed_opportunity` | `genuine_opportunity` | `open` |
| `M30-F01-R3` | `fomento` | `confirmed_opportunity` | `genuine_opportunity` | `open` |
| `M30-F01-R4` | `fomento` | `confirmed_opportunity` | `genuine_opportunity` | `open` |
| `M30-F02-R1` | `fomento` | `confirmed_opportunity` | `genuine_opportunity` | `open` |
| `M30-F03-R1` | `fomento` | `opportunity_signal` | `uncertain` | `undetermined` |
| `M30-F05-R1` | `fomento` | `confirmed_opportunity` | `genuine_opportunity` | `open` |
| `M30-F06-R1` | `fomento` | `confirmed_opportunity` | `genuine_opportunity` | `open` |
| `M30-F07-R1` | `fomento` | `confirmed_opportunity` | `genuine_opportunity` | `open` |
| `M30-F08-R1` | `fomento` | `confirmed_opportunity` | `genuine_opportunity` | `open` |
| `M30-I01-R1` | `investimentos` | `opportunity_signal` | `uncertain` | `undetermined` |
| `M30-I02-R1` | `investimentos` | `confirmed_opportunity` | `genuine_opportunity` | `undetermined` |
| `M30-I03-R1` | `investimentos` | `unrelated_or_non_actionable` | `not_opportunity` | `not_applicable` |
| `M30-I04-R1` | `investimentos` | `confirmed_opportunity` | `genuine_opportunity` | `undetermined` |
| `M30-I05-R1` | `investimentos` | `opportunity_signal` | `uncertain` | `undetermined` |
| `M30-I06-R1` | `investimentos` | `announced_future_opportunity` | `uncertain` | `undetermined` |
| `M30-I07-R1` | `investimentos` | `opportunity_signal` | `uncertain` | `undetermined` |
| `M30-I08-R1` | `investimentos` | `opportunity_signal` | `uncertain` | `undetermined` |
| `M30-N01-R1` | `credito` | `unrelated_or_non_actionable` | `not_opportunity` | `not_applicable` |
| `M30-N02-R1` | `credito` | `unrelated_or_non_actionable` | `not_opportunity` | `not_applicable` |
| `M30-N03-R1` | `fomento` | `unrelated_or_non_actionable` | `not_opportunity` | `not_applicable` |
| `M30-N04-R1` | `fomento` | `unrelated_or_non_actionable` | `not_opportunity` | `not_applicable` |
| `M30-S01-R1` | `credito` | `opportunity_signal` | `uncertain` | `undetermined` |

## 8. Inventário de documentos e fontes congeladas

Links abaixo identificam a origem já registrada, não consultas atuais; nenhuma URL foi novamente adquirida nesta retomada. Proveniência integral, URLs finais, datas e hashes por documento permanecem no manifesto.

| Documento | Organização | Tipo | Origem registrada |
|---|---|---|---|
| `M30-C01` | BNDES | HTML | https://www.bndes.gov.br/wps/portal/site/home/financiamento/produto/bndes-automatico |
| `M30-C02` | BNDES | HTML | https://www.bndes.gov.br/wps/portal/site/home/financiamento/produto/programa-bndes-mais-inovacao-investimento |
| `M30-C03` | BNDES | HTML | https://www.bndes.gov.br/wps/portal/site/home/financiamento/produto/bndes-credito-pequenas-e-medias-empresas |
| `M30-C04` | BNDES | HTML | https://www.bndes.gov.br/wps/portal/site/home/financiamento/produto/fundo-clima/fundo-clima-florestas-nativas-recursos-hidricos |
| `M30-C05` | BNDES | HTML | https://www.bndes.gov.br/wps/portal/site/home/financiamento/finame |
| `M30-C06` | BRDE | HTML | https://brde.com.br/linha-financiamento/mais-inovacao/ |
| `M30-C07` | BRDE | HTML | https://www.brde.com.br/noticia/creditur-rs-amplia-acesso-ao-credito-para-fortalecer-turismo-na-area-metropolitana-de-porto-alegre/ |
| `M30-C08` | BRDE | HTML | https://brde.com.br/programas/ |
| `M30-F01` | CNPq | HTML | https://www.gov.br/cnpq/pt-br/chamadas/abertas-para-submissao |
| `M30-F02` | CNPq | HTML | https://www.gov.br/cnpq/pt-br/chamadas/todas-as-chamadas/chamadas-2026/chamada-no-33-2026/chamada-publica-cnpq-N-33-2026 |
| `M30-F03` | CNPq | HTML | https://www.gov.br/cnpq/pt-br/chamadas/todas-as-chamadas/chamadas-2026/chamada-no-30-2026 |
| `M30-F05` | MCTI | HTML | https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/noticias/noticias-julho-outubro-2026/chamada-para-projetos-de-transformacao-mineral-recebe-propostas-ate-30-de-novembro |
| `M30-F06` | MCTI | HTML | https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/noticias/noticias-julho-outubro-2026/chamada-eureka-recebe-propostas-para-projetos-de-resiliencia-e-resposta-a-desastres |
| `M30-F07` | CNPq | PDF | https://www.gov.br/cnpq/pt-br/chamadas/todas-as-chamadas/chamadas-2026/chamada-no-33-2026/Chamada_Produtividade_33_2026.pdf |
| `M30-F08` | CNPq | HTML | https://www.gov.br/cnpq/pt-br/chamadas/todas-as-chamadas/chamadas-2026/chamada-no-30-2026/chamada-publica-cnpq-N-30-2026 |
| `M30-I01` | Criatec 4 | HTML | https://criatec4.com/ |
| `M30-I02` | Criatec 4 | HTML | https://criatec4.com/novos-investimentos/ |
| `M30-I03` | Criatec 4 | HTML | https://criatec4.com/portfolio/ |
| `M30-I04` | Criatec 4 | HTML | https://criatec4.com/aplique-sua-startup/ |
| `M30-I05` | BNDES | HTML | https://agenciadenoticias.bndes.gov.br/noticia/BNDES-e-FINEP-recebem-19-propostas-para-FIP-Conexoes-Startups/ |
| `M30-I06` | BNDES | HTML | https://agenciadenoticias.bndes.gov.br/noticia/BNDES-e-Finep-selecionam-a-Monashees-para-gestao-de-fundo-de-IA-de-R$-500-mi |
| `M30-I07` | BRDE | PDF | https://brde.com.br/wp-content/uploads/2026/01/Folder-2026-Mais-Inovacao-AGCUR.pdf |
| `M30-I08` | BNDES | HTML | https://www.bndes.gov.br/wps/portal/site/home/mercado-de-capitais/fundos-de-investimentos/chamadas-publicas-para-selecao-de-fundos |
| `M30-N01` | BNDES | HTML | https://agenciadenoticias.bndes.gov.br/noticia/BNDES-aprova-R$-1818-milhoes-para-o-desenvolvimento-de-veiculo-hibrido-da-Renault-no-Brasil/ |
| `M30-N02` | BNDES | HTML | https://agenciadenoticias.bndes.gov.br/noticia/BNDES-aprova-R$-600-mi-para-Instituto-Butantan-implantar-Centro-de-Imunobiologicos/ |
| `M30-N03` | Finep | HTML | https://finep.gov.br/w/finep-divulga-o-resultado-do-pr%C3%AAmio-mulheres-inovadoras |
| `M30-N04` | Finep | HTML | https://finep.gov.br/w/mcti-e-finep-anunciam-aporte-de-r-450-milh%C3%B5es-para-114-empresas-das-regi%C3%B5es-norte-nordeste-e-centro-oeste |
| `M30-S01` | BNDES | HTML | https://agenciadenoticias.bndes.gov.br/noticia/BNDES-e-Instituto-Clima-e-Sociedade-firmam-parceria-com-foco-na-restauracao-dos-biomas-brasileiros |

## 9. Pendências e ponto de parada

1. Revisão independente originalmente solicitada **interrompida por HTTP 429, não concluída**; continua pendente, sem nova tentativa nesta retomada.
2. Revisão humana autorizada, anotações cegas independentes e adjudicação não existem neste release. Qualquer referência aprovada futura exigirá processo autenticado e nova versão; nenhum dos 33 rótulos foi promovido.
3. I06 deve conservar a dúvida entre anúncio futuro e sinal; F01/F02/F07 têm cobertura documental parcial; I07 não comprova disponibilidade de candidatura. Cobertura temporal continua sem closed/continuous/future reais.
4. Não há métricas de extração nem afirmação de precisão/recall ou prontidão para produção. A preparação técnica concluída não remove essas pendências.
5. **Parar na M3.0. M3.1 não iniciada.** `evaluation/M31_PREPARATION.md` é somente preparação preexistente, não execução ou autorização. Nenhum crawling, nova aquisição, adaptação, previsão, integração, publicação, staging ou commit é parte desta retomada.
