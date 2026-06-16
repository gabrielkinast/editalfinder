# EditalFinder — Schema atual do banco (auditoria)

Documentação gerada em **2026-06-03** a partir do banco **Supabase (PostgreSQL)** em staging, sem alterar dados nem schema.

| Artefato | Caminho |
|----------|---------|
| SQL consolidado | `backend/database/schema_current.sql` |
| Gerador (re-run) | `backend/scripts/generate_schema_current_docs.py` |
| Diagnóstico SQL | `backend/docs/sql/check_existing_schema.sql` |

---

## Fonte da verdade

Ordem de precedência usada nesta auditoria:

1. **Banco real** — introspecção via PostgREST OpenAPI (`/rest/v1/`, service role, somente leitura).
2. **Migrations** — `backend/migrations/*.sql` (ordem cronológica no nome do ficheiro).
3. **Backend** — `CORE/loader.py`, transformers, scripts de carga e auditoria.
4. **Frontend** — apenas para **divergências**; não define o schema.

Não foi encontrado SQLite local (`.db` / `.sqlite`) no repositório. O backend usa **`supabase-py`** (`CORE/db.py`).

---

## Ambiente

| Item | Valor |
|------|--------|
| Motor | PostgreSQL (Supabase) |
| Schema | `public` |
| Conexão app | `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` (ou `SUPABASE_KEY` / `SUPABASE_ANON_KEY`) |
| Extensão | `pgcrypto` |

---

## Tabelas expostas no staging (PostgREST)

| Tabela | PK | Colunas | Notas |
|--------|-----|---------|--------|
| `edital` | `id_edital` (bigint) | **107** | `link` UNIQUE NOT NULL; núcleo de oportunidades |
| `noticia` | `id` (uuid) | 34 | Migração antiga usava `id_noticia`; live usa `id` |
| `pesquisa` | `id` (uuid) | 37 | Migração antiga usava `id_pesquisa`; live usa `id` |
| `edital_anexo` | `id_anexo` (uuid) | 13 | FK → `edital` |
| `edital_extra_campo` | `id_extra` (uuid) | 11 | EAV; FK → `edital` |
| `carga_execucao` | `id_execucao` (uuid) | 30 | Log de cargas do loader |
| `edital_historico` | `id_historico` (uuid) | 13 | Auditoria de mudanças (vazia no staging) |
| `cliente` | `id_cliente` (integer) | 30 | Workspace consultivo |
| `usuario` | `id_usuario` (bigint) | 8 | Perfis de acesso |
| `edital_favorito` | `id_favorito` (uuid) | 21 | Favoritos por utilizador |
| `edital_feedback` | `id_feedback` (uuid) | 13 | Feedback por edital |
| `concurso_selecao` | `id_concurso` (bigint) | 35 | UNIQUE (`fonte`, `link`) |
| `portal_estrategico` | `id_portal` (uuid) | 44 | Portais BNB/EIC/etc.; `link` UNIQUE |

### Tabelas referenciadas no código mas ausentes no staging

| Tabela | Estado | Impacto |
|--------|--------|---------|
| `organizacao` | **Não exposta** (PGRST205) | Frontend `dataService.getOrganizations()` e formulário admin falham se chamados |
| `app_feedback` | **Não exposta** | Proposta em `docs/sql/CREATE_APP_FEEDBACK.sql` |
| `edital_backend_enrichment_shadow` | **Não exposta** | Dry-run Backend 9–10.1; proposta em `docs/sql/STAGING_BACKEND_ENRICHMENT_SHADOW_TABLE.sql` |

---

## Views expostas

| View | Uso principal |
|------|----------------|
| `vw_editais_front` | Feed / radar de editais (frontend) |
| `vw_editais_admin` | Admin (espelha `vw_editais_front` + crédito) |
| `vw_editais_favoritos_front` | Favoritos |
| `vw_noticias_front` | Notícias |
| `vw_pesquisas_front` | Pesquisa / conteúdo científico |
| `vw_concursos_front` / `vw_vestibulares_front` | Concursos |
| `vw_fornecedores_front` / `vw_investimentos_front` | Portais estratégicos |
| `vw_concursos_admin` / `vw_portais_estrategicos_admin` | Admin |

Definição inline no SQL: `vw_editais_front` / `vw_editais_admin` (migration `20260505_recreate_edital_views_credito_staging.sql`). Demais views: migrations `20260504_recreate_front_views_staging.sql` e scripts em `backend/docs/sql/`.

**Importante:** `vw_editais_front` **não** expõe `orgao_responsavel`, `id_organizacao` nem campos de enriquecimento Backend 9–10.

---

## Migrations (ordem sugerida)

| Ficheiro | Propósito |
|----------|-----------|
| `20260430_add_edital_filter_columns.sql` | Filtros iniciais em `edital` |
| `20260501_create_carga_execucao_and_edital_historico.sql` | Carga + histórico |
| `20260504_create_noticia_pesquisa_tables.sql` | Separação notícia/pesquisa |
| `20260504_add_missing_columns_for_consolidated_schema.sql` | Colunas consolidadas |
| `20260504_align_supabase_backend_contract.sql` | Alinhamento tipos + FKs + helpers |
| `20260504_recreate_front_views_staging.sql` | Views front (notícias, pesquisas, editais base) |
| `20260505_add_missing_edital_columns_from_loader_payload.sql` | Payload real do loader (crédito, i18n, etc.) |
| `20260505_recreate_edital_views_credito_staging.sql` | Views editais com campos de crédito |

`DANGER_RESET_STAGING_SCHEMA.sql` — **não** usar em auditoria; reset destrutivo apenas referência.

Documentação histórica: `docs/sql/schema_consolidado_editalfinder.sql`, `CORE/schema_sql_completo.sql` (podem estar parcialmente desatualizados).

---

## `public.edital` — campos pedidos na tarefa

| Campo / conceito | No staging | Onde |
|------------------|------------|------|
| `id_edital` | Sim | PK |
| `titulo` | Sim | |
| `fonte` | Alias | `fonte_recurso` (view: `fonte`) |
| `source` | Não (coluna) | Usar `fonte_recurso` / `origem_portal` |
| `tipo` | Parcial | `tipo_oportunidade`, `tipo_recurso` |
| `area` | Sim | `area` (text[]) + `area_cientifica` / `area_tecnologica` |
| `estado` | Sim | |
| `pais` | Sim | |
| `url` / `link` | Sim | **`link`** (canónico, UNIQUE) |
| `link_edital` | Não em `edital` | Em `concurso_selecao.link_edital` |
| `url_edital` | Não | Usar `link` ou `url_detalhe` |
| `pdf_url` | Sim | |
| `url_pdf` | Não | `pdf_url` |
| `inscricao_url` | Não | `link_inscricao` |
| `url_inscricao` | Não | `link_inscricao` |
| `data_publicacao` | Sim | |
| `prazo` | Não (coluna) | `prazo_envio` (date); view: `fim_inscricao` |
| `prazo_envio` | Sim | |
| `prazo_status` | Não (coluna) | Proposta em `PROPOSAL_BACKEND_ENRICHMENT_COLUMNS.sql`; pode estar em `extras` |
| `validade_status` | **Não (coluna)** | Calculado em `validity_resolver.py` / enricher |
| `situacao` | Sim | |
| `actionability_type` | **Não (coluna)** | Backend 10.1 em memória / shadow proposto |
| `classification_bucket` | **Não (coluna)** | Idem |
| `is_noise` / `noise_type` | **Não (coluna)** | Idem |
| `quality_score` / `quality_level` | **Não (coluna)** | `qualidade_dado` (integer legado) existe |
| `flags` | Parcial | `warnings` (text[]), `tags`, `extras` jsonb |
| `organizacao_responsavel` | **Não** | Não existe com este nome |
| `organization` | **Não** | |
| `responsavel` | Parcial | **`orgao_responsavel`**, `unidade_responsavel`, `orgao`, `instituicao` |

### Organização responsável (divergência frontend)

- **Tabela `edital`:** existe `orgao_responsavel` (text), `orgao`, `instituicao`, `orgao_contratante`, `unidade_responsavel`, e `id_organizacao` (bigint, FK lógica para `organizacao` — tabela ausente no staging).
- **Formulário admin** (`EditalForm.jsx`): label *"Organização Responsável"* → campo **`id_organizacao`** (select de `organizacao.nome`), **não** `organizacao_responsavel`.
- **Loader** (`loader.py`): persiste `orgao_responsavel` no row; `orgao` pode vir de extras.
- **Conclusão:** o frontend exige `id_organizacao` + tabela `organizacao`, que **não está** no cache PostgREST do staging atual. O texto de organização no edital deve usar **`orgao_responsavel`** ou `fonte_recurso`.

---

## Enriquecimento Backend 9–10.1 (não persistido em `edital`)

Campos usados em `noise_classifier.py`, `validity_resolver.py`, `opportunity_enricher.py`:

- `actionability_type`, `classification_bucket`, `is_noise`, `noise_type`
- `is_actionable_opportunity`, `actionability_score`
- `validade_status`, `validade_data`, `validade_confidence`, `validade_source`
- `quality_score`, `quality_level`, `quality_flags`, `review_reasons`

Estes valores aparecem em **dry-run** (`outputs/`) e na proposta `docs/sql/PROPOSAL_BACKEND_ENRICHMENT_COLUMNS.sql`. **Não** foram listados nas 107 colunas de `edital` no OpenAPI do staging.

Alternativa atual: armazenar sinais em `extras` jsonb (ex.: curadoria, visibility) ou tabela shadow (proposta).

---

## Backend — uso principal por tabela

| Componente | Tabelas |
|------------|---------|
| `CORE/loader.py` | `edital`, `edital_anexo`, `edital_extra_campo`, `edital_historico`, `noticia`, `pesquisa` |
| `scripts/load_portais_estrategicos.py` | `portal_estrategico` |
| `scripts/load_concursos_selecao.py` | `concurso_selecao` |
| `scripts/load_news_research_sources.py` | `noticia`, `pesquisa` |
| `scripts/_backend_audit_io.py` | `edital` (read-only audits) |
| `CORE/scoring.py` | `organizacao` (legado; falha se tabela ausente) |

Upsert canónico: `edital` on conflict **`link`**; `noticia` / `pesquisa` on conflict **`link`**.

---

## Frontend — expectativas vs schema (sem correção)

| Área | Espera | Schema real |
|------|--------|-------------|
| Feed editais | `vw_editais_front` | OK; sem `orgao_responsavel` na view |
| Admin edital | `edital` + `organizacao` | `organizacao` ausente no staging |
| Favoritos | `edital_favorito`, `vw_editais_favoritos_front` | OK |
| Clientes | `cliente` | OK |
| Auth | `usuario` | OK |
| App feedback | `app_feedback` | Tabela não exposta |
| Classificação UI | `classificarEdital` (client-side) | Independente de colunas DB |

---

## Como regenerar esta documentação

```bash
cd backend
python scripts/generate_schema_current_docs.py
```

Requisitos: `.env.staging` (ou `CORE/.env`) com credenciais Supabase válidas.

Diagnóstico manual no SQL Editor:

```sql
-- backend/docs/sql/check_existing_schema.sql
```

---

## Resumo executivo

1. Banco principal: **Supabase Postgres**, não SQLite local.
2. Núcleo: **`public.edital`** com **107 colunas**; deduplicação por **`link`**.
3. **`organizacao_responsavel` não existe**; usar **`orgao_responsavel`** + **`id_organizacao`** (FK sem tabela no staging).
4. Campos Backend 10.1 (**ruído/validade/quality**) são **lógica Python**, não colunas em `edital` no staging.
5. SQL completo: **`backend/database/schema_current.sql`**.
