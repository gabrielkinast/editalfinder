# Sincronização Cursor — estado após alterações no Codex (VS Code)

**Data do snapshot:** 2026-05-09 (UTC, aproximado no momento da leitura).

Este documento **não** alterou código nem base de dados; apenas leu artefatos e ficheiros existentes e correu `py_compile` em scripts indicados.

---

## 1. Git

Na cópia do projeto em `D:\Computational_Physics\My Projects\edital` **não existe `.git`**, pelo que:

- `git status`, `git diff --stat` e `git diff --name-only` **falham** (`fatal: not a git repository`).

**Ação recomendada:** trabalhar na pasta que o Codex usa com git inicializado, ou clonar/copiar o `.git` para esta árvore, para poder listar ficheiros alterados por commit.

---

## 2. Ficheiros e scripts verificados (existência + compilação)

| Área | Estado |
|------|--------|
| `main.py` | Existe — orquestrador com subcomandos (`daily`, `status`, …); legado em `main_legacy_pipeline.py`. |
| `config/pipeline_sources.json` | Existe — ondas news ativas; `stable_apply_sources` vazio. |
| `scripts/validate_full_staging_after_daily.py` | Existe — `py_compile` OK. |
| `scripts/detect_removed_items.py` | Existe — `py_compile` OK. |
| `scripts/deactivate_removed_items.py` | Existe — `py_compile` OK. |
| `international_onda_c_common.py` | Existe — `py_compile` OK. |
| Crawlers Onda C (`innovate_uk`, `ukri_funding`, `eurostars`, `eit`, `esa_star`, `esa_osip`) | `main_*.py` existem — `py_compile` OK. |
| `CORE/taxonomy_filtros.py`, `CORE/transformer.py`, `scripts/load_ready_sources.py` | Existem; **sem** revisão linha-a-linha nesta sincronização. |
| `frontend/` (Radar / Pré-cadastro / PDF) | **Não** há pasta `frontend/` com `.tsx` neste workspace — a UI pode estar noutro repo ou caminho. |

---

## 3. Relatórios lidos

### Pós-daily / staging

- **`audit_reports_main_pipeline/post_daily_validation.json`** (2026-05-09T14:36:59Z): `ok: true`, `critical_errors: []`. Warnings agregados, entre outros: `prazo_vencido_ativo_true` (41), `titulo_ruidoso` (6), `credito_tipo_recurso_incoerente` (4), `setor_estrategico_muito_amplo` (72), `suspeito_ativo_true` (76). Contagens: edital 1105, notícia 109, pesquisa 47.
- **`audit_reports_main_pipeline/post_daily_warning_examples.md`**: exemplos acionáveis; inclui EIC e Eureka em `setor_estrategico_muito_amplo` (valores > 3 no **staging**).

### Onda C — inovação internacional

- **`audit_reports_credito/lote_inovacao_internacional_onda_c_diagnostico.json`** (+ `.md`): lote com 6 fontes; `safety.apply_executed: false`.
- **`audit_reports_credito/lote_inovacao_internacional_onda_c_semantic/`**: presente (resumo semântico por lote).
- **`audit_reports_credito/lote_inovacao_internacional_onda_c_fix/`**: retransform + `standardized/` por fonte.

### `last_run_summary.json`

O ficheiro **`audit_reports_main_pipeline/last_run_summary.json`** observado nesta leitura contém sobretudo uma execução **`deactivate_removed_items`** em modo dry-run (`group: removed_items`), **não** um resumo completo do `main.py daily`. O mesmo nome de ficheiro é partilhado por fluxos — sempre verificar o campo `modo` / `group` dentro do JSON.

---

## 4. Onda C — confirmação face ao resultado esperado

Valores no **`lote_inovacao_internacional_onda_c_diagnostico.json`**:

| Métrica | Valor no relatório |
|---------|-------------------|
| Raw total | **50** |
| Standardized total | **48** |
| Rejeitados (transform) | **2** |
| Loader dry-run `would_upsert_total` | **48** |
| `mapping_errors_total` | **0** |
| `setor_estrategico_gt3` (por fonte no `by_source`) | **0** em todas as entradas listadas |

**Readiness recomendado no relatório** (ainda **não** espelhado em `config/source_readiness.json` nesta árvore):

| Fonte | Recomendado |
|--------|-------------|
| ukri_funding | ready_with_notes |
| eit | ready_with_notes |
| esa_osip | ready_with_notes |
| innovate_uk | needs_manual_review |
| eurostars | needs_manual_review |
| esa_star | **blocked** |

### ESA STAR — permanece bloqueado

Conforme o diagnóstico: crawler encontra portal oficial; o transformer **rejeita** conteúdo como login/autenticação; **0** itens transformados. **Não** promover sem feed/API pública oficial ou estratégia documentada.

### Nota de risco (próprio relatório)

O JSON de diagnóstico indica que o dry-run do loader foi executado com **SUPABASE_URL local fictício** para não tocar staging real — as métricas do loader refletem os **artefatos**; reexecutar contra staging real quando for aplicável.

---

## 5. EIC / Eureka

- Em **`config/source_readiness.json`** constam **`eic`** e **`eureka_network`** em `ready_with_notes`.
- Os **warnings de staging** em `post_daily_warning_examples.md` ainda citam EIC/Eureka com `setor_estrategico` muito amplo — **compatível** com dados antigos em `public.edital` se o apply do standardized corrigido **ainda não** tiver sido feito ou não tiver atualizado esses registos.

---

## 6. Frontend (Radar, Editais, Pré-cadastro, PDF)

Não foi possível inspecionar componentes neste workspace (**sem** pasta `frontend/`). Para sincronizar UI/PDF com o Codex, abrir o repositório onde vive o frontend ou indicar o caminho.

---

## 7. Riscos

- **Sem git:** não há diff/commit para cruzar com o Codex nesta cópia.
- **Staging vs artefatos:** validações pós-daily refletem o estado **atual** da base; o lote Onda C é sobretudo **offline** até apply explícito.
- **Warnings persistentes:** prazos vencidos com `ativo=true`, títulos ruidosos, `setor_estrategico_muito_amplo` — exigem curadoria ou pipeline de desativação/retaguarda (sem DELETE automático).

---

## 8. Tarefas pendentes (sugeridas)

1. Restaurar `.git` ou apontar Cursor para o clone correto e repetir `git status` / `git diff`.
2. Decidir promoção das fontes Onda C em `config/source_readiness.json` **após** revisão humana.
3. Manter **esa_star** em `blocked` até haver fonte pública estável.
4. Alinhar standardized canónico + `load_ready_sources` dry-run/apply para EIC/Eureka se o objetivo for limpar warnings de `setor_estrategico` no staging.
5. Encontrar o repositório frontend para validar Radar / filtros Editais / Pré-cadastro / bug de PDF (cabeçalho).

---

## 9. Comandos seguros para continuar

```powershell
# Git (num clone com .git)
git status
git diff --stat
git diff --name-only

# Orquestrador
python main.py status
python main.py list-readiness

# Dry-run edital restrito (exemplo Onda C promovível no futuro)
python main.py daily --dry-run --skip-crawl --skip-transform --skip-news --skip-edital-audits --sources ukri_funding,eit,esa_osip
```

**Não executar nesta sincronização:** apply, migrations, reset de schema, escrita Supabase.

---

## 10. Entregável JSON

Ver **`audit_reports_main_pipeline/cursor_sync_after_codex.json`** (estrutura máquina-legível, mesma informação).
