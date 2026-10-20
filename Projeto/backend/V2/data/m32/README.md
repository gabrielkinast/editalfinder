# M3.2 — avaliação offline semântica exploratória

PROVISIONAL / EXPLORATORY. Nenhuma referência humana autenticada; os 33 rótulos M3.0 continuam provisórios. Avaliação de desenvolvimento sobre corpus exposto, não holdout ou certificação de acurácia. Extrator M3.1, suas previsões run-v2 e todo M3.0 são somente leitura.

## Artefatos canônicos

- `input_binding.json`: versões, data civil, digests e IDs esperados de documentos/registros.
- `evaluation_plan.md`: tarefas A–L, unidades, denominadores, incerteza e limites.
- `evaluation_results.json`: core determinístico, 33 registros/127 slots de campos, grafo completo e 332 claims, separado de tempos.
- `per_document/document-000.json` até `document-027.json`: 28 documentos; ID e URL dentro do payload, sem usar IDs arbitrários como caminho. Incluem campos/testemunhas reais, referências, segmentos, erros e juízos AI daquele documento.
- `semantic_reviews.json`: 39 observações AI, intencionais e não representativas, com hashes, locadores e contexto. 13 sobre fields, 26 sobre classificações; sem assinatura/aprovação humana.
- `error_cases.json`, `error_taxonomy.md`, `review_queue.json`: desacordos, observações e erros sob rubrica explícita, com certainty e confiança causal. Fila não autoriza mudanças de rótulo.
- `diagnostic_probes.json`: experimentos de contexto selecionado por referência e janela de dinheiro; não são novas previsões nem ganho medido de qualidade.
- `case_studies.md`: F01/C05/C07/I03/I05/I06/I07 e casos adicionais, com trechos/fontes/locadores.
- `improvement_backlog.md`: oito propostas M3.3, NÃO implementadas.
- `baseline.json`, `initial_inventory.json`, `quality_gates.json`, `reproducibility.json`: evidência de execução e preservação.
- `independent_review.json`: parecer AI técnico read-only concluído, PASS limitado ao código/metodologia/artefatos examinados. Não executou pytest novamente nem revisou a redação final do relatório. Sugestões interpretativas foram incorporadas ao relatório, sem alterar resultados congelados.
- `freeze.json`: hashes do core, módulos e diagnósticos; recibo de integridade, não autenticação de emissor.
- `performance.json`: tempos exclusivos da avaliação por documento/registro/estágio e RSS Linux, separados dos timings históricos do extrator.
- `preliminary-v1/`: primeiro diagnóstico preservado byte a byte. Seu comparador tratava campo fora do recorte provisório como candidato ATTRIBUTION_ERROR; foi refinado ANTES da revisão independente para exigir outro registro explícito. O canônico na raiz marca F05/F06 como UNRESOLVED, não erro de atribuição confirmado. Não usar o draft como resultado final.

Relatório final: `../../EDITALFINDER_V2_M32_RESULTADOS.md`. A revisão M3.1 v1 FAIL permanece em docs/v2/M31_INDEPENDENT_REVIEW.md; o parecer ChatGPT posterior da run-v2 é outro documento, não reescrita do FAIL.

## Reproduzir

De backend/V2, escolher diretório NOVO ou sem arquivos de saída existentes, fora de M3/M31:

    PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m editalfinder_v2.evaluation_m32 data/m3 data/m31/run-v2 data/m32/input_binding.json <novo-diretorio> --semantic-reviews data/m32/semantic_reviews.json

O core, error_cases, review_queue e os 28 JSONs por documento devem coincidir byte a byte. Timings não. Binding e recebimento inválidos retornam diagnósticos estruturados e results=null; versão desconhecida, hash obsoleto, ausência ou duplicata não reduzem denominadores silenciosamente. Uma falha operacional explícita em outcome válido continua no denominador.

## Limites indispensáveis

32/33 overlap mede geometria textual, NÃO recall de oportunidades. 27/127 strict role/value mede coincidência literal de nomes/papéis, NÃO precisão real. MATCH é diagnóstico candidato; entailment requer revisão separada. Localizador 719/719 válido não certifica 332 papéis financeiros/organizacionais. Os 319 campos não revisados semanticamente continuam visíveis. Não somar resultados de tarefas em um score global. Taxas com denominador zero retornam null. Undetermined/uncertain/abstain não são negativos.

M3.2 não modifica extração. Não houve aquisição, rede, banco, deploy, promoção, merge, staging ou commit. M3.3 não iniciada.
