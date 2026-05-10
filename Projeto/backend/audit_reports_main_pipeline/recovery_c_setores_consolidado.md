# Recovery C — Setores estratégicos (EMBRAPII, NUCLEP) — Consolidado final

## 1. Resumo executivo

A Recovery C aplicou cap e evidencia em setor_estrategico para EMBRAPII e NUCLEP (41 itens). O primeiro apply corrigiu standardized na origem mas o merge de extras no loader unia listas antigas e novas, fazendo regressao global 72->85. Foi implementado --overwrite-fields setor_estrategico no load_ready_sources; o segundo apply gravou o setor do payload. Pos-validacao (2026-05-10T08:02:47Z): ok=true, setor_estrategico_muito_amplo=47; ganho liquido versus pre-Recovery C: 72->47 (-25).

## 2. Contexto

Metrica pre-Recovery C: **72**. Fontes foco: embrapii, nuclep. Primeiro staging apply (standardized correto) elevou metrica para **85** por comportamento documentado em recovery_c_setores_regression_debug. Segundo apply (**2026-05-10T07:44:28Z**) com --overwrite-fields setor_estrategico alinhou BD ao cap. Validacao final **2026-05-10T08:02:47Z**.

`merge_extras_dict` em `CORE/merge_utils.py` concatena listas deduplicadas; para `setor_estrategico` isso somava etiquetas antigas com novas. `extras_to_filter_columns` republicava esse conjunto na coluna espelho.

## 3. O que foi alterado

- **Calibacao**: `taxonomy_filtros` + transformer para EMBRAPII/NUCLEP (cap 3 + evidencia).
- **Loader**: `taxonomy_replace_keys` em `_rebuild_merged_extras`; CLI `--overwrite-fields setor_estrategico` (obrigatorio `--sources`; allowlist v1).
- **Operacao**: segunda carga 41 atualizados, 0 erros (`staging_load_summary.json`). Sem alteracao de schema, readiness oficial ou gate global nesta geracao de relatorio.

## 4. Resultado operacional

| Métrica | Antes | Depois | Variação | Interpretação |
|---|---:|---:|---:|---|
| `setor_estrategico_muito_amplo (global)` | 72 | 47 | -25 | liquido vs linha base; pico intermediario 85 |
| `setor_estrategico_muito_amplo (apos 1º apply)` | 72 | 85 | +13 | merge uniao listas no loader |
| `setor_estrategico_muito_amplo (apos 2º apply)` | 85 | 47 | -38 | overwrite taxonomico |
| `would_upsert Recovery C` | - | 41 | 0 | Duas aplicacoes, 41 updates cada |

Pré-visualização com `--overwrite-fields` (dry-run com leitura à BD): **`overwritten_fields_count` = 38** em `recovery_c_taxonomy_overwrite_dryrun/` — contagem por diferença de multiconjunto, não necessariamente igual a 41.

## 5. Resultado por fonte

| Fonte | Antes | Depois | Ganho | Observação |
|---|---:|---:|---:|---|
| EMBRAPII | 13 warnings setor_ampli (linha base) | 0 neste problema (warnings_by_source atual) | -13 | Residual global inclui outras fontes. |
| NUCLEP | 12 | 0 neste problema | -12 | Idem. |

## 6. Interpretação

1. O problema original era listas amplas (~4 tags) nos dois sources.
2. O standardized Recovery C ficou correto (<=3) mas extras_to_filter_columns lia merged_extras com uniao BD+payload.
3. A solucao de overwrite substitui setor_estrategico pelo payload apos merge, apenas com flag e --sources.
4. Os 47 restantes vivem noutras fontes; tratados fora desta Recovery.

## 7. Riscos e limitações

1. Reutilizar --overwrite-fields sem revisao pode substituir setor mesmo quando BD tiver valor curado diferente.
2. Paginas institucionais NUCLEP seguem como linhas editais ate roteamento de produto.
3. Residual 47 depende de ondas posteriores; nao e bug de crawler.

## 8. Decisão recomendada

- **considerar_recovery_c_encerrada_fase_setores_EMBRAPII_NUCLEP**: metricas globais dentro do esperado apos segunda carga; sem novos criticos.

Proximo foco: **Fase seguinte — outras fontes com `setor_estrategico_muito_amplo` (DoD SBIR, EIC, Eureka, …)**.

## 9. Próximos passos

1. Planejar Recovery C.2 / onda seguinte por fontes com alto setor_estrategico_muito_amplo.
2. Opcional: alargar campos sob overwrite com allowlist institucional (nao automatizar extras inteiro sem revisao).
3. Monitorizar post_daily apos cargas ordinarias dos mesmos dois sources para evitar regressao de merge.

## 10. Evidências técnicas

1. audit_reports_main_pipeline/recovery_c_setores_regression_debug.json
2. audit_reports_main_pipeline/recovery_c_taxonomy_preservation_debug.json
3. audit_reports_main_pipeline/recovery_c_taxonomy_overwrite_dryrun/recovery_c_taxonomy_overwrite_dryrun.json
4. audit_reports_main_pipeline/post_daily_validation.json
5. audit_reports_main_pipeline/post_daily_warning_examples.json
6. audit_reports_loader_ready/staging_load_summary.json
7. audit_reports_loader_ready/load_execution_history.jsonl
8. Ver tambem CORE/merge_utils.py, CORE/loader.py, CORE/taxonomy_filtros.extras_to_filter_columns
