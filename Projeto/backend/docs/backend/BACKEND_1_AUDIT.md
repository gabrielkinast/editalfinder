# Backend 1 — Auditoria: prazos, classificação e view de editais

**Fase:** diagnóstico + biblioteca central (sem UPDATE em massa, sem mudança destrutiva de schema).  
**Data:** 2026-05 (gerado na implementação Backend 1).

---

## 1. Escopo e objetivos

Problemas observados no Dashboard (frontend):

1. Alta proporção de editais **sem prazo estruturado** (`prazo_envio` vazio no banco).
2. Gráfico de modalidade depende de **heurística no React**.
3. Fontes internacionais (ex.: China International) dominam sem contexto de escopo.
4. Risco de misturar **edital**, **notícia**, **pesquisa** e **concurso** na mesma tabela.
5. A view `vw_editais_front` expõe poucos campos “prontos” para UI.

**Entregáveis desta fase:**

| Artefato | Caminho |
|----------|---------|
| Normalizador de prazo | `CORE/deadline_normalizer.py` |
| Classificador | `CORE/opportunity_classifier.py` |
| Script auditoria prazos | `scripts/audit_deadlines_backend.py` |
| Script auditoria classificação | `scripts/audit_edital_classification_backend.py` |
| Proposta SQL (não aplicar) | `docs/sql/PROPOSAL_VW_EDITAIS_FRONT_BACKEND_1.sql` |
| Testes | `tests/test_deadline_normalizer.py`, `tests/test_opportunity_classifier.py` |

---

## 2. Tabelas e views envolvidas

| Objeto | Papel |
|--------|--------|
| `public.edital` | Tabela principal de oportunidades ingeridas pelo pipeline |
| `public.vw_editais_front` | View consumida pelo frontend (`dataService.getEditais`) |
| `public.vw_editais_admin` | Alias admin (staging: `select * from vw_editais_front`) |
| `public.noticia` / `vw_noticias_front` | Notícias (roteamento separado) |
| `public.pesquisa` / `vw_pesquisas_front` | Pesquisas |
| `public.concurso_selecao` / views concursos | Concursos (módulo paralelo, `data_fim_inscricao`) |

**Migrações relevantes:** `migrations/20260505_add_missing_edital_columns_from_loader_payload.sql`, `migrations/20260505_recreate_edital_views_credito_staging.sql`.

---

## 3. Campos atuais — prazo

### Banco (`public.edital`)

| Coluna | Origem no pipeline |
|--------|-------------------|
| `prazo_envio` | `loader.map_to_db_schema` ← `item.fim_inscricao` (transformer) |
| `data_encerramento` | extras / extended schema |
| `situacao`, `ativo` | loader marca encerrado se `prazo_envio < hoje` |

### View `vw_editais_front`

- Expõe `prazo_envio` e alias `fim_inscricao` (= `prazo_envio`).
- **Não** expõe: `prazo_status`, `prazo_confidence`, `escopo_geografico`, `modalidade_normalizada`.

### Transformer (`CORE/transformer.py`)

Ordem típica de resolução de prazo (~2767+):

1. Campos estruturados: `fim_inscricao`, `prazo_envio`, `deadline`, `inscricoes_fim`
2. `extract_deadline_from_text(full_text)` via `CORE/date_parser.py`
3. Saída canônica transform: **`fim_inscricao`** (ISO)
4. Original em `extras.fim_inscricao_original`

### Crawlers

| Padrão | Exemplo |
|--------|---------|
| Campo nativo | `finep` → `prazo_envio` no modelo crawler |
| Filtro pré-crawl | `fapergs` descarta se `prazo_envio < hoje` |
| API internacional | `grants_gov/simpler` → `close_date` → `fim_inscricao` |
| Texto na página | `CORE/scraper_dates.py`, `date_parser.py` |

### Visibilidade (`CORE/editais_visibility.py`)

- Lê múltiplos aliases: `prazo_envio`, `fim_inscricao`, `data_limite`, `extras.close_date`, etc.
- Classifica `review_missing_deadline`, `hidden_expired`, fluxo contínuo.

### Lacuna principal

Muitos registros chegam ao banco **sem** `fim_inscricao` resolvido no transform; o frontend tenta reparse em `prazo_envio_raw` / extras — daí o Dashboard mostrar ~90% “sem prazo”.

---

## 4. Campos atuais — tipo / modalidade

| Campo | Quem preenche |
|-------|----------------|
| `tipo_oportunidade` | `taxonomy_filtros.enrich_opportunity_classification()` |
| `tipo_recurso` | transformer + taxonomy |
| `area`, `setor_estrategico`, `area_tecnologica` | taxonomy / crawler |
| `classificacao_confianca`, `metodo_classificacao` | taxonomy |
| `extras.thematic_tags` | `keyword_taxonomy` |

Problema: `area` longa (“Tecnologia e Inovação…”) foi usada no front como proxy de “tipo”, gerando buckets duplicados.

---

## 5. Campos atuais — fonte

| Campo | Notas |
|-------|--------|
| `fonte_recurso` | Persistido pelo loader a partir de `item.fonte` |
| View alias `fonte` | = `fonte_recurso` |
| `pais`, `regiao`, `uf` | Colunas existentes, pouco normalizadas na view |

---

## 6. Roteamento edital vs notícia vs pesquisa

| Módulo | Função |
|--------|--------|
| `CORE/content_routing.py` | Destino na carga: `edital` / `noticia` / `pesquisa` |
| `CORE/opportunity_gate.py` | Intenção funding/procurement/… |
| `CORE/editais_visibility.py` | Ruído / visibilidade na listagem |

Backend 1 adiciona `classify_record_kind()` para auditoria pós-carga (não substitui routing na ingestão).

---

## 7. Pipeline de arquivos (mapa)

```
Crawler JSON
    → CORE/transformer.py (*_standardized.json)
    → CORE/schema.normalizar()
    → CORE/loader.py (upsert public.edital)
    → public.vw_editais_front
    → Frontend EditalFinder-React
```

**Scripts de auditoria existentes (referência):**

- `scripts/audit_pipeline.py` — dry-run transform+loader
- `scripts/audit_editais_visibility_noise.py` — visibilidade
- `scripts/audit_content_routing.py` — roteamento
- `scripts/audit_semantic_classification.py` — taxonomy

**Novos (Backend 1):**

- `scripts/audit_deadlines_backend.py`
- `scripts/audit_edital_classification_backend.py`

---

## 8. Como executar auditorias

```bash
# Com Supabase ( .env.staging na raiz )
python scripts/audit_deadlines_backend.py --from-db --limit 5000
python scripts/audit_edital_classification_backend.py --from-db --limit 5000

# Com export JSON (array de linhas edital)
python scripts/audit_deadlines_backend.py --input exports/editais_sample.json
```

Saídas:

- `outputs/audit_deadlines_backend/summary.md`
- `outputs/audit_edital_classification_backend/summary.md`
- `outputs/audit_kind_classification_review/review_candidates.json`

---

## 9. Integração — Backend 2 (dry-run, concluído)

| Entregável | Caminho |
|------------|---------|
| Enriquecedor | `CORE/opportunity_enricher.py` |
| Dry-run pipeline | `scripts/dry_run_backend_enrichment.py` |
| Mapa de integração | `docs/backend/BACKEND_2_PIPELINE_MAP.md` |
| Guia operacional | `docs/backend/BACKEND_2_ENRICHMENT_DRY_RUN.md` |

Hook opcional com `EDITALFINDER_ENABLE_BACKEND_ENRICHMENT=false` (padrão) em `transformer.py` e `loader.py` — grava preview em `extras.backend_enrichment` apenas.

## 10. Integração planejada (Backend 3+)

1. **Migration:** colunas da proposta SQL (`prazo_status`, `modalidade_normalizada`, …).
2. **Loader:** persistir colunas após backfill validado.
3. **View:** aplicar `PROPOSAL_VW_EDITAIS_FRONT_BACKEND_1.sql` após revisão humana.
4. **Batch report-only:** UPDATE só após relatório + amostra validada.

---

## 11. Riscos e restrições

- Não executar SQL da proposta em produção sem revisão.
- `service_role` apenas em servidor / `.env.staging` (nunca no frontend).
- Fontes internacionais legítimas não devem ser removidas — classificar escopo, não excluir.
- Concursos permanecem em tabela própria; regras de `classify_record_kind` na tabela `edital` são heurísticas.

---

## 12. Testes

```bash
python -m pytest tests/test_deadline_normalizer.py tests/test_opportunity_classifier.py tests/test_opportunity_enricher.py -q
```
