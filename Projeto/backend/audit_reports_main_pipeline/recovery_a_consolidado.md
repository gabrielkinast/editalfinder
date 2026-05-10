# Recovery A — Consolidado

## 1. Resumo executivo

A **Recovery A** visou **recuperar oportunidades reais** na **BASA** (crédito/financiamento), **filtrar ruído** no **DoD SBIR/STTR** mantendo apenas tópicos oficiais (`/topics/<id>` quando a API falha), e **não** ingerir **ESA STAR** sem listagem pública sem SSO. O **dry-run oficial** do loader apontou **32** upserts simulados com **0** erros de mapeamento e **0** vazios críticos. A **validação global** pós-carga em staging (**2026-05-10T04:59:30Z**) ficou **`ok=true`** com **0** erros críticos. O **ganho central** foi **`suspeito_ativo_true` 80 → 61 (−19)** e **`titulo_ruidoso_ativo_true` = 0**. O **principal risco residual** é operacional: o **`staging_load_summary.json` mais recente** no repositório documenta **apenas** carga **BASA** (26 linhas); o **DoD** foi **excluído** por `not_in_sources_filter` nessa execução — pode ser necessário **apply dedicado** `dod_sbir_sttr`. **Decisão:** considerar a **onda A concluída** em termos de código e BASA; **recomendar** confirmar **staging DoD** e, se faltar, **aplicar só essa fonte**.

## 2. Contexto

**Antes:** muitos itens **suspeitos** ou **ruído ativo** (títulos/contas genéricas); DoD com **hubs** institucionais; ESA inacessível sem SSO.

**Problema:** perda de **oportunidades reais** e **poluição** do catálogo **edital**.

**Fontes:** `banco_da_amazonia`, `dod_sbir_sttr`, `esa_star` (bloqueada).

**Artefatos:** `recovery_a_official_loader_dryrun.json`, `recovery_a_summary.json` / `recovery_a_by_source.json` (se existirem), `staging_load_summary.json`, `post_staging_validation.json`, `post_daily_validation.json`, `load_execution_history.jsonl`.

## 3. O que foi alterado

### Código

- **BASA:** relax local crédito BR + `validacao_status` **incompleto** em linhas oficiais em vez de **suspeito** automático onde aplicável.
- **DoD:** denylist de paths (Success Stories, Events, `/api`, FAQ, etc.); fallback HTML só **detalhe** de tópico; soft-continue `dod_sbir_sttr_recovery_a_local`; setor ≤ 3.
- **ESA:** `allow_empty`; sem alteração ao **gate global**.

### Crawler

- BASA: exclusões **PF**, **conta-pj**, **renegociação**, hubs genéricos; reforço de listas **noise** / `credito_brasil_onda_a`.
- DoD: só URLs elegíveis de tópico/solicitação.

### Transformação / qualidade

- Menos promoção de páginas institucionais a edital; títulos genéricos "Topic" enriquecidos com ID onde aplicável.

## 4. Resultado operacional

| Métrica | Antes | Depois | Variação | Interpretação |
|---|---:|---:|---:|---|
| `suspeito_ativo_true` | 80 | 61 | −19 | melhora |
| `titulo_ruidoso_ativo_true` | (presente na operação anterior) | 0 | →0 | melhora |
| `prazo_vencido_ativo_true` | — | 41 | — | baseline pós-carga; política futura |
| `credito_tipo_recurso_incoerente` | — | 4 | — | baseline; revisão por fonte |
| `setor_estrategico_muito_amplo` | — | 72 | — | dívida transversal |

**Banco:** `ok=true`, **0** críticos na validação citada.

## 5. Resultado por fonte

| Fonte | Antes | Depois | Ganho | Observação |
|---|---|---|---|---|
| **banco_da_amazonia** | Ruído + suspeitos altos | **26** processados no último load guardado (**3** ins, **23** upd, **0** err) | Carga limpa documentada | Dry-run global 32 inclui DoD no plano |
| **dod_sbir_sttr** | Hubs + listagens | **6** tópicos no standardized A + presença em warnings staging | Recuperação de sinais reais | **Verificar** apply dedicado — excluído do último `staging_load_summary` mostrado |
| **esa_star** | blocked | blocked | 0 | Correto até haver feed público sem SSO |

## 6. Interpretação

- **−19 suspeitos** indica que **itens úteis** deixaram de ser empurrados para **suspeito** por defeito de gate/ruído.
- **0 título ruidoso ativo** mostra que a **frente “edital”** ficou mais **apresentável**; os **6** `titulo_ruidoso_inativo` são **histórico** (`ativo=false`) — não confundir com warning ativo.
- **Prazo / crédito / setor** no snapshot pós-A são **baseline** para **ondas seguintes** (Recovery B/C), não falha da A.

## 7. Riscos e limitações

- **DoD** pode estar **desalinhado** do standardized A se a última execução guardada **não** incluiu `--sources dod_sbir_sttr`.
- **API sbir.gov** (429) limita **enriquecimento** contínuo.
- **ESA** continua **blocked** — expectativa de dados zero.
- **Prazo vencido (41)** pode **crescer** com mais honestidade de datas — precisa **produto** (arquivo, filtros).

## 8. Decisão recomendada

**Decisão recomendada:** **concluir** a Recovery **A** no âmbito de **entrega de código + BASA em staging**; **acionar** verificação e, se necessário, **`aplicar_staging` só para `dod_sbir_sttr`** com readiness acordado. **Manter `esa_star` bloqueada.** **Próximo alvo:** confirmar DoD em staging, em seguida **Recovery B** (já documentada à parte) e **ondas** de prazo/setor.

## 9. Próximos passos

1. Validar se os **6** tópicos DoD Recovery A estão refletidos na base; caso contrário, **load_ready_sources** dedicado.
2. Re-correr **crawler DoD** quando API estável.
3. Continuar **pesquisa ESA** pública (sem SSO).
4. Atacar **prazo vencido** e **setor amplo** em **onda própria**.
5. Definir política para **legados** `titulo_ruidoso_inativo`.

## 10. Evidências técnicas

**Arquivos lidos / citados**

- `audit_reports_main_pipeline/post_daily_validation.json` (validação **2026-05-10T04:59:30Z**)
- `audit_reports_loader_ready/staging_load_summary.json` (**2026-05-10T04:54:39Z** — só BASA nesta linha)
- `audit_reports_loader_ready/post_staging_validation.json`
- `audit_reports_loader_ready/load_execution_history.jsonl`
- `audit_reports_main_pipeline/recovery_a_official_loader_dryrun.json`

**Arquivos gerados**

- `audit_reports_main_pipeline/recovery_a_consolidado.md`
- `audit_reports_main_pipeline/recovery_a_consolidado.json` (inclui `padrao_documentacao_onda`)

**Comandos**

- Ver `recovery_a_apply_recommendation.json` e entradas em `load_execution_history.jsonl` para comandos exatos (`load_ready_sources`, filtros `--sources`).

**Restrições**

- **Apply:** não reexecutado na elaboração deste consolidado.
- **Supabase / schema / readiness / gate global:** **sem alterações** nesta tarefa de relatório.

**Template:** `scripts/recovery_report_template.py`.
