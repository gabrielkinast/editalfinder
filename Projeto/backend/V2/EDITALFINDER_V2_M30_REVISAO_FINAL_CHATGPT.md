# EditalFinder V2 — Revisão técnica final (ChatGPT) da M3.0

**Pacote analisado:** `V2.tar(20261019-195049).gz`. **Escopo:** conferência do relatório final, integridade do corpus e do verificador, testes, comparativo com o pacote anterior, sondagens adversariais offline. **Parecer:** **READY condicional apenas para preparação técnica do corpus offline**; **não é ground truth aprovado**, nem autorização automática para M3.1 ou produção.

## 1. Confirmação do entregável e integridade

- `EDITALFINDER_V2_M30_RESULTADOS.md` está presente no pacote atual e não existia em `V2.tar(20261019-050617).gz`.
- Comparação SHA-256 de **todos os arquivos dos dois arquivos tar**: pacote anterior com 287 arquivos regulares, atual com 288; **nenhum arquivo anterior alterado ou removido**; único arquivo novo: `EDITALFINDER_V2_M30_RESULTADOS.md`.
- Os **108 arquivos regulares de `data/m3/`** são idênticos, byte a byte, entre os pacotes.
- O manifesto registra **28 documentos** (**26 HTML, 2 PDF**) com **6.466.530 bytes** de originais; há **33 registros**, **95 evidências** e 33 rótulos `provisional`. Referência temporal do corpus: **2026-10-19**.
- SHA-256 de `data/m3/corpus_manifest.json`: `841fb92e3bb353c5dd511a99f38901b2bb24ba20285ba508342598e3a6c7bdfa`.
- SHA-256 de `data/m3/annotations/records.json`: `515da22ed1e2a94e3b2815a07fb740e7481c99fe8d8dbb21c6ef97a518d99df7`.

## 2. Testes independentes reproduzidos

Ambiente local do revisor: **Python 3.13.5, Pydantic 2.13.5, pytest 9.0.2**, a partir do pacote descompactado. Não foi feita nenhuma consulta à internet nem alteração do pacote original.

| Verificação | Resultado |
|---|---|
| `PYTHONPATH=src python -m pytest -p no:cacheprovider -q tests/test_m30_dataset.py tests/test_m30_corpus.py` | **95 passed in 1.96s** |
| `PYTHONPATH=src python -m pytest -p no:cacheprovider -vv` (saída completa salva e consultada) | **2095 passed in 37.13s** |
| `PYTHONPATH=src python -m editalfinder_v2.dataset_m30 data/m3` | **Validated 28 documents and 33 records** |
| `python -B data/m3/provenance/verify_derivation.py` | **PASS: 28/28 derivados** |
| Comparação SHA-256 arquivo anterior versus atual | **108/108 arquivos do corpus iguais; único novo arquivo é relatório** |

**Limites de verificação:** Ruff, mypy e `git diff --check` passaram conforme as evidências **registradas pelo Hermes** no `M30_RESULTADOS.md` e `evaluation/verification.json`; esses três comandos **não foram executados independentemente neste ambiente**. A cópia da árvore contém arquivos não rastreados, não o contexto Git original. A suíte completa demorou mais do que o prazo configurado em duas execuções preliminares; uma execução posterior com log detalhado foi concluída com `2095 passed in 37.13s`, sem falhas.

## 3. Distribuição dos rótulos

| Dimensão | Resultados |
|---|---|
| Modalidade | 13 crédito, 12 fomento, 8 investimentos |
| Descoberta | 18 `confirmed_opportunity`, 8 `opportunity_signal`, 6 `unrelated_or_non_actionable`, 1 `announced_future_opportunity` |
| Existência | 18 `genuine_opportunity`, 9 `uncertain`, 6 `not_opportunity` |
| Temporal | 9 `open`, 18 `undetermined`, 6 `not_applicable` |
| Revisão | **33 `provisional`, nenhum aprovado** |

Há cobertura de múltiplos registros em uma mesma fonte (C05 com 2, C07 com 2, F01 com 4); isso não autoriza fusão de oportunidades ou empréstimo de evidência.

## 4. Sondagens adversariais próprias

Alterações testadas **apenas sobre uma cópia temporária** de `data/m3`:

| Ataque ou alteração | Resultado | Interpretação |
|---|---|---|
| Definir `review_status='approved'` em `M30-I06-R1` | **REJECT**, Pydantic ValidationError | Proíbe aprovação não autorizada no piloto |
| Falsificar a citação E1 de `M30-I06-R1` sem alterar fonte | **REJECT**, Pydantic ValidationError | Verifica correspondência entre referência textual e citação |
| Alterar `M30-I06-R1` de `undetermined` para `future` | **ACCEPT** | Coerência de schema **não prova** janela futura de candidatura |
| Reclassificar `M30-N04-R1` como oportunidade confirmada com disponibilidade indeterminada | **ACCEPT** | Verificador **não certifica** veracidade semântica das classes |

Os dois últimos resultados **não são defeitos contra o contrato declarado**: o verificador audita estrutura, escopos, citação e integridade, não a verdade das inferências do anotador. Tornam indispensáveis revisão humana autorizada e adjudicação antes de calcular métricas contra um *gold set*.

## 5. Revisão dos casos de maior risco

A revisão preliminar ChatGPT do **pacote anterior com os mesmos 108 arquivos de corpus** já inspecionou os 33 registros contra seus trechos e contexto, incluindo os dois PDFs. Essa revisão semântica **não foi repetida integralmente** nesta retomada; sua pertinência é reforçada pela igualdade byte a byte do corpus.

- **`M30-I06-R1`:** seleção de gestora e estruturação/diligência do fundo de IA sustentam relevância para monitoramento, mas não demonstram inscrições futuras já agendadas para startups. `announced_future_opportunity` continua hipótese **provisória**, com `temporal_status=undetermined`; um revisor pode preferir `opportunity_signal`.
- **`M30-F01`:** a listagem prova janelas dos registros listados, mas não substitui todos os PDFs de editais e seus requisitos integrais.
- **`M30-F07`:** registrar versão PDF com metadados “Minuta” e anexo retificado não congelado; não declarar cobertura normativa completa.
- **`M30-I07`:** FIPs em captação não implicam chamada para startups ou continuidade atual da captação.
- **`M30-C07`:** a mesma notícia possui uma operação individual já realizada (não é nova candidatura) e descrição de programa de crédito (oportunidade, janela indeterminada), com registros separados.
- **`M30-N01`–`N04`:** operações concedidas, resultado de prêmio e recursos a propostas já avaliadas não implicam novos períodos de inscrição.

O relatório oficial incorpora explicitamente essas limitações e não anuncia precisão/recall, verdade certificada nem prontidão de produção.

## 6. Pendências e documentação

1. **Revisão independente originalmente solicitada ao subagente:** interrompida por **HTTP 429**, ainda **não concluída**. O relatório final registra isso corretamente. Esta revisão ChatGPT independente do processo Hermes também é realizada por IA e **não substitui revisão humana autenticada** nem a revisão formal pendente.
2. **Referência local ausente no pacote:** `EDITALFINDER_V2_M30_RESULTADOS.md` faz link para `EDITALFINDER_V2_M30_REVISAO_PRELIMINAR_CHATGPT.md`, mas **esse documento não consta entre os 288 arquivos regulares do tar atual**. Ele foi fornecido em separado na conversa. Para tornar o pacote autocontido, copiar o `.md` à raiz do V2 e gerar novo arquivo de distribuição; isso não requer alterar o corpus.
3. **Cobertura temporal insuficiente para avaliação ampla:** não há exemplos reais `closed`, `continuous` ou `future` como estado de janela no corpus congelado. A exclusão de editais antigos é decisão de escopo prospectivo, não juízo de que editais históricos nunca existiram.
4. **Rótulos apenas provisórios:** não há anotação cega, discordância adjudicada ou autorização humana. As porcentagens de acerto de um extrator não devem ser relatadas como qualidade validada com esta versão do corpus.
5. **Riscos herdados:** limites M23D-F02 (observabilidade do oráculo) e M23D-F04 (tratamento de URLs M1/M2.1) permanecem. Nenhuma aquisição, crawling, Supabase, publicação ou integração de produção foi autorizada por esta revisão.

## 7. Veredito

**`READY` condicional para o corpus M3.0 como material de pesquisa e preparação offline**, com entregável de resultados agora presente, integridade e testes reproduzidos, e todos os limites de escopo explicitados.

**Não declarar `READY` como referência semântica humana, métrica de extração ou prontidão para produção.** Encerrar administrativamente a documentação da M3.0 é possível **mantendo a revisão do subagente como pendente**, não simulando sua conclusão. A M3.1 deve ser autorizada separadamente; se iniciar, priorizar adaptador estritamente offline e avaliação exploratória rotulada como provisória, sem promoção automática.
