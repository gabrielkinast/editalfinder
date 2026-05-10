# Regressão Recovery C — `setor_estrategico_muito_amplo` (72 → 85)

## Resumo executivo

O apply da Recovery C foi **executado com o diretório e as fontes corretos** (`audit_reports_main_pipeline/recovery_c_setores/standardized`, **embrapii** + **nuclep**, **41** atualizações, **0** inserções). O standardized local mantinha **no máximo 3** entradas em `extras.setor_estrategico` por item.

Após o apply e a validação global (`post_daily_validation.json`, `2026-05-10T07:08:09Z`), o contador **`setor_estrategico_muito_amplo` subiu de 72 para 85** (+13). Nos dois focos da Recovery C, o aviso por fonte **aumentou**: **EMBRAPII** 13 → 19 (+6), **NUCLEP** 12 → 19 (+7). A soma **+13** iguala o delta global, o que é coerente com um efeito concentrado nas linhas tocadas pelo loader nesta execução.

**Causa técnica provável:** no carregamento, `extras` existentes no banco são fundidos com o novo payload através de `merge_extras_dict`. Para **listas**, a implementação faz **união deduplicada** (`cur + v`), não substituição estrita. O `setor_estrategico` gravado na tabela (coluna espelho) vem de `extras_to_filter_columns` aplicado ao **`merged_extras`**. Assim, etiquetas antigas (por exemplo `aeroespacial`, `industria`) podem **permanecer** enquanto o payload Recovery C introduz outras até três (`ciencia_tecnologia`, `energia`, …), produzindo **mais de três valores únicos** na coluna — **pior** do que o capped local e **pior** do que só o estado antigo, em certas combinações.

Em uma frase operacional: **a Recovery C corrigiu o payload no disco, mas o merge do loader união-lista impediu que o cap de 3 se refletisse fielmente no staging; em alguns casos até ampliou o conjunto.**

Referências de código:

- `CORE/merge_utils.py` — `merge_extras_dict`: listas → união.
- `CORE/loader.py` — `_rebuild_merged_extras` encadeia merge com extras legados/fragmentos; `_merge_db_row` + `extras_to_filter_columns` propagam para a coluna.
- `CORE/taxonomy_filtros.py` — `extras_to_filter_columns` copia `setor_estrategico` dos extras fundidos para a coluna.

## Confirmação do apply (tarefa 2)

| Campo | Valor |
|--------|--------|
| `input_dir` | `…\audit_reports_main_pipeline\recovery_c_setores\standardized` |
| Fontes | `embrapii`, `nuclep` |
| Itens | 41 processados; 0 inseridos; 41 atualizados; 0 erros |
| Evidência | `audit_reports_loader_ready/load_ready_summary.json` (`id_execucao` `c6ae1239-3bbe-4585-a1e7-bf41e3ef0e14`, `mode`: apply); `staging_load_summary.json`; linha em `load_execution_history.jsonl` com mesma execução e `itens_processados`: 41 |

Não há indício de apply a partir de outro diretório de standardized para esta execução.

## Tabela — `setor_estrategico_muito_amplo` por fonte (tarefa 3)

Valores “antes” a partir de `recovery_c_setores_consolidado.json` / baseline documentada; “depois” de `post_daily_validation.json` → `warnings_by_source`.

| fonte | antes | depois | delta |
|--------|------:|-------:|------:|
| EMBRAPII | 13 | 19 | +6 |
| NUCLEP | 12 | 19 | +7 |

## Standardized vs staging (tarefas 4 e 6)

- Nos ficheiros `embrapii_standardized.json` / `nuclep_standardized.json` sob Recovery C, o **cap local** está garantido (bundle: 0 itens com length > 3).
- Exemplo documentado no JSON auxiliar: a chamada **“Chamada Pública 01/2017 – RESULTADO FINAL”** aparece no standardized com **3** setores em `extras.setor_estrategico**; o mesmo **link** surge nos exemplos de `post_daily_warning_examples.json` com **5** valores na coluna `setor_estrategico` lida na validação — evidência de **divergência pós-merge**, não de standardized incorreto.

Os primeiros exemplos do aviso incluem várias linhas **EMBRAPII** e **NUCLEP** com 4–5 setores na tabela, com links presentes no bundle Recovery C.

## Loader — “preservação” (tarefa 5)

- `_merge_db_row` prefere valores novos não vazios para a maioria dos campos escalares; o ponto crítico é o **`merged_extras`**, onde listas são **unidas**.
- O contador `fields_preserved_non_empty_total["setor_estrategico"]: 41` no `staging_load_summary` reflecte a métrica do dry-run/apply (“entrada e payload com campo não vazio”), **não** “valor antigo byte-a-byte mantido”.
- A frase pedida no enunciado pode ser afinada assim: **o payload Recovery C estava correto no ficheiro, mas o merge por união nas listas de `extras.setor_estrategico` não substituiu o conjunto antigo pelo cap, pelo que a coluna espelho pode continuar (ou passar a) violar o limite de 3.**

## Recomendações (tarefa 8 — sem executar)

| Opção | Veredicto |
|--------|-----------|
| **A** Refazer apply com outro `input_dir` | **Desnecessário** — o path e as fontes estão corretos na evidência. |
| **B** Modo seguro / política para `setor_estrategico` em update (substituição ou cap pós-merge para cargas taxonómicas) | **Principal.** Alinha comportamento do loader com a intenção da Recovery C. |
| **C** NUCLEP institucional como edital | **Complementar** (classificação de conteúdo); não substitui o fix de merge. |
| **D** Ajustar só o diagnóstico | **Inadequado** — o aviso reflecte dados reais na tabela. |

---

Artefacto JSON paralelo: `recovery_c_setores_regression_debug.json`.
