# M3.1 — revisão independente AI do estado v1

Status: concluída como revisão técnica somente leitura, parecer **FAIL / passed=false**. Não é referência humana autenticada. Revisão originalmente solicitada na M3.0 continua interrompida por HTTP 429 e não concluída; este é outro escopo.

Revisor: subagente `sa-0-de7eb92e`, delegação `deleg_a18e0e61`, modelo reportado gpt-6-astra. Retorno da revisão preservado na conversa e transcript local:
`/home/lorenzozm/.hermes/cache/delegation/live/deleg_a18e0e61/task-0.log`.

## Achados confirmados

1. HIGH — `structure.py`: chamada final de F01 absorve conteúdo após contêiner. Segmento v1 segment-0011 8213–13344 inclui Próximo, navegação/cookies e Refazer a busca. Os 4 matches de rótulos não validam fronteiras.
2. HIGH — `models.py`/`pipeline.py`: verificação usa limites recebidos, não reconstruídos. Ampliar o primeiro segmento e copiar testemunha do segundo com segment_id trocado satisfaz os checks existentes (gap confirmado por código; a prova dinâmica do revisor foi negada por approval e não executada).

## Limitações/sugestões

- C07 negócio concluído pode gerar sinal; I06 expressão `R$ 500 mi` foi capturada como `R$ 500`, sem normalização monetária. Limitações semânticas, sem promoção.
- Testar fim de contêiner, expansão de limites com empréstimo de evidência, poisoning real de categorias e recusa de sobrescrita.
- Transporte da avaliação lê bytes antes de testar tamanho; leitura deveria ser bounded.
- Inspeção adicional completa de página 12 de I07 estava no comando negado e não foi concluída pelo revisor.

## O que foi efetivamente verificado pelo revisor

Reexecução em memória: 28 documentos, 1630 segmentos, 332 campos, previsões determinísticas idênticas e hashes do receipt válidos. `compare()` reproduziu avaliação existente. Os 107 arquivos M3.0 abrangidos pelo inventário inicial sem caches estavam inalterados. Inspeção de casos especiais e evidências; nenhuma escrita, rede, instalação, SQL/DB ou modelo externo. Testes pytest não executados pelo revisor (criam arquivos temporários); um comando combinado de probes foi negado e não repetido. Não afirmar esses probes aprovados.

Hashes do código revisado permanecem em `data/m31/run-v1/freeze.json`. A regressão de import absoluto detectada pelo agente principal depois do despacho não entrou no parecer: a mensagem de steering chegou após conclusão. Gates v1 preservados em `data/m31/quality_gates.json`: 1 failed/2127 passed; recorte histórico 1 failed/2094 passed. Causa: __main__.py import absoluto interno contraria teste de fronteira existente; corrigir para import relativo, sem alterar teste histórico.

## Tratamento após revisão

Os dois defeitos HIGH foram reproduzidos dinamicamente pelo agente principal antes da correção: os três testes de fim de contêiner/expansão de limites/F01 real falharam no código v1. Após preservação de ancestralidade e reconstrução de unidades, passaram. A regressão histórica de importação também foi reproduzida e corrigida sem modificar o teste histórico. Testes de expressão monetária abreviada e transporte bounded passaram após suas correções; poisoning de categorias e exclusive-create foram exercitados.

Gates finais executados pelo agente principal: 2134 passed; recorte histórico sem o novo arquivo: 2095 passed; Ruff, formatação e mypy aprovados. `run-v2` é separado, com 28 documentos processados, 1649 segmentos e 332 campos. O parecer v1 permanece FAIL e não é aprovação independente da versão corrigida. Não foi solicitada segunda revisão AI: revisão externa da versão final continua pendente. Ver relatório M31 e `data/m31/quality_gates_final.json` para evidência completa.
