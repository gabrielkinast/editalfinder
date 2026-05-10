# Recovery B — Consolidado

## 1. Resumo executivo

A **Recovery B** tratou **AMAZUL**, **Ambev** e **BADESUL** para **reduzir `suspeito_ativo_true`** sem alargar o `opportunity_gate` global, sem promover ruído óbvio a edital e **sem** mexer em schema/readiness oficiais. O **apply em staging** processou **32** itens (**1** inserção, **31** atualizações, **0** erros). A **validação global** (`post_daily_validation.json`, **2026-05-10T05:51:55Z**) manteve **`ok=true`** e **zero erros críticos**. O **resultado principal** foi **`suspeito_ativo_true` 61 → 47 (−14)**, coerente com a soma das melhorias nas três fontes. **Prazo vencido** e **crédito incoerente** **subiram** ligeiramente no agregado (+7 e +2): isso reflete **mais linhas sujeitas a regras** após saírem do “balde” suspeito, **não** uma quebra de integridade. **Decisão:** considerar a **Recovery B concluída** para o seu objetivo; **próximo** investimento recomendado: **onda de prazos** (Recovery C ou equivalente) e, em paralelo, **afinação de crédito incoerente** / **setor amplo**.

## 2. Contexto

**Estado antes (baseline global imediato antes da B):** `suspeito_ativo_true` **61**, `prazo_vencido_ativo_true` **41**, `credito_tipo_recurso_incoerente` **4**, `setor_estrategico_muito_amplo` **72** (valores registados no JSON consolidado).

**Problema:** excesso de linhas **suspeitas ativas** nas três fontes por **gate genérico** e, no caso BADESUL, **ruído** (home, listagens).

**Fontes:** AMAZUL, Ambev, BADESUL.

**Artefatos base:** `recovery_b_official_loader_dryrun.json`, `recovery_b_official_semantic_summary.json`, `recovery_b_official_apply_recommendation.json`, `recovery_b_official_dryrun_context.json`, `staging_load_summary.json`, `post_daily_validation.json`, `post_daily_warning_examples.json`.

## 3. O que foi alterado

### Código

- **`CORE/item_quality.py`:** `opportunity_gate_relaxed` com scopes **`amazul_local`**, **`ambev_local`**, **`badesul_local`** — tendência para **`validacao_status = incompleto`** com avisos `recovery_b_*_gate_relaxed` em vez de cair em **suspeito** só por soft-continue.
- **`CORE/transformer.py`:** `calibrate_badesul_extras`; `_amazul_soft_continue` e `_badesul_soft_continue` aceitam também razão **“Noticia ou pagina generica”**.
- **`CORE/taxonomy_filtros.py`:** `calibrate_badesul_extras` — `tipo_oportunidade` e contenção de setores defesa/aero sem evidência textual.

### Crawler

- **`badesul/main_badesul.py`:** filtro de ruído (ex.: listagens de entidades inscritas); remoção do fallback para **home** institucional; `save_outputs(..., allow_empty=True)` quando não há publicações.

### Transformação / qualidade

- Menos **suspeito** automático nas três fontes; mais **incompleto** com rastreabilidade; BADESUL sem “item único” da home como edital.

## 4. Resultado operacional

| Métrica | Antes | Depois | Variação | Interpretação |
|---|---:|---:|---:|---|
| `suspeito_ativo_true` | 61 | 47 | −14 | melhora — objetivo principal |
| `prazo_vencido_ativo_true` | 41 | 48 | +7 | efeito esperado ao expor regra de prazo em linhas antes suspeitas ou recém-normalizadas |
| `credito_tipo_recurso_incoerente` | 4 | 6 | +2 | exposição de coerência; AMAZUL com +2 no agregado pós-B (ver warning examples) |
| `setor_estrategico_muito_amplo` | 72 | 72 | 0 | fora do escopo |

**Banco (staging):** `ok=true`, `critical_errors=0`.

## 5. Resultado por fonte

| Fonte | Antes (suspeito ativo) | Depois (suspeito ativo) | Ganho | Observação |
|---|---:|---:|---:|---|
| AMAZUL | 14 | 12 | −2 | Ainda 7 prazos vencidos + 2 crédito incoerente no agregado pós-B (subconjunto documentado) |
| Ambev | 7 | 0 | −7 | Sai do `warnings_by_source` de suspeitos no snapshot |
| BADESUL | 7 | 2 | −5 | Redução forte; curadoria residual |

## 6. Interpretação

- **−14 suspeitos globais** confirma que **itens reais** ou **limítrofes úteis** deixaram de ser classificados como **suspeitos** apenas por atrito com o gate.
- **+7 prazo vencido** não deve ser lido como “pior qualidade global”: muitas linhas **passam a ser avaliadas** pela regra de prazo quando deixam o estado suspeito ou quando a carga refresca datas — ver nota metodológica no JSON (`interpretacao_aumentos_prazo_e_credito`).
- **+2 crédito incoerente** idem: regra de coerência **visível** em mais linhas; AMAZUL concentrou parte desse efeito (**B.1** tratou depois especificamente AMAZUL).
- **Setor amplo inalterado:** confirmado que **não era meta** desta recovery.

## 7. Riscos e limitações

- **AMAZUL:** ainda **12** suspeitos e **7** prazos vencidos ativos no agregado analisado — risco de **perceção** de “recovery incompleta” se só se olhar suspeito global.
- **Crédito incoerente** pode **subir** noutras ondas quando mais fontes forem normalizadas — comunicar que é **efeito de medição**.
- **Flags semânticas** (ex.: `publico_alvo_sem_evidencia`) permanecem como **dívida incremental**, não bloqueio de carga no dry-run oficial.
- **Não** foi alterado `opportunity_gate` global: limita o quanto se pode “autocurar” sem novas políticas de produto.

## 8. Decisão recomendada

**Decisão recomendada:** **concluir** a **Recovery B** relativamente ao objetivo de **suspeitos nas três fontes**; **não** manter fontes bloqueadas por este motivo; **não** exigir novo apply B sem mudança de código. **Próximo passo de produto/dados:** abrir **onda Recovery C** (ou nome equivalente) focada em **`prazo_vencido_ativo_true`**, depois **`credito_tipo_recurso_incoerente`** remanescente e, em separado, **`setor_estrategico_muito_amplo`**. Opcional no frontend: **ocultar** ou **badger** suspeitos / prazo vencido conforme política.

## 9. Próximos passos

1. Comunicar internamente o significado de **+prazo** / **+crédito** no pós-B (evitar alarme falso).
2. Executar / acompanhar **Recovery B.1 AMAZUL** para crédito (já documentada à parte) se ainda não estiver merged.
3. Planejar **Recovery C** — prazos vencidos com `ativo=true` e política de arquivo.
4. Curadoria **12 AMAZUL** + **2 BADESUL** suspeitos remanescentes.
5. Manter **`validate_full_staging_after_daily.py --staging`** após cargas.

## 10. Evidências técnicas

**Arquivos lidos / referenciados**

- `audit_reports_main_pipeline/recovery_b_official_loader_dryrun.json`
- `audit_reports_main_pipeline/recovery_b_official_semantic_summary.json`
- `audit_reports_main_pipeline/recovery_b_official_apply_recommendation.json`
- `audit_reports_main_pipeline/recovery_b_official_dryrun_context.json`
- `audit_reports_loader_ready/staging_load_summary.json` (apply **2026-05-10T05:43:54Z**, 32 itens, 0 erros)
- `audit_reports_main_pipeline/post_daily_validation.json` (**2026-05-10T05:51:55Z**)
- `audit_reports_main_pipeline/post_daily_warning_examples.json`

**Arquivos gerados**

- `audit_reports_main_pipeline/recovery_b_consolidado.md`
- `audit_reports_main_pipeline/recovery_b_consolidado.json` (inclui `padrao_documentacao_onda`)

**Apply / infra**

- **Apply:** não executado na **edição** deste relatório; apply B já consta no `staging_load_summary` histórico.
- **Supabase / schema / readiness / opportunity_gate global:** **sem alterações** nesta tarefa de documentação.

**Template:** `scripts/recovery_report_template.py`.
