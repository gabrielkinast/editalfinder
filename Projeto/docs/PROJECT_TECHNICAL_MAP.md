# EditalFinder — Mapa técnico do projeto

Documentação de auditoria e mapeamento (somente leitura). **Não substitui** correções de bugs nem alterações de schema.

| Data | Escopo |
|------|--------|
| 2026-06-03 | Mapa geral alinhado ao schema auditado |

**Fonte de verdade do banco:**

- [`backend/database/schema_current.sql`](../backend/database/schema_current.sql)
- [`backend/docs/backend/DATABASE_CURRENT_SCHEMA.md`](../backend/docs/backend/DATABASE_CURRENT_SCHEMA.md)

Documentação antiga parecida (manter; pode divergir): `backend/docs/sql/schema_consolidado_editalfinder.sql`, `backend/CORE/schema_sql_completo.sql`, `frontend/EditalFinder-React/schema_sql_completo.sql`, `backend/docs/FRONTEND_BACKEND_CONTEXT.md`.

---

# 1. Visão geral do projeto

## O que é

O **EditalFinder** é uma plataforma de inteligência de oportunidades para consultoria, pesquisa e fomento. Agrega e organiza:

- editais e chamadas públicas;
- linhas de crédito e programas de fomento;
- notícias científicas e institucionais;
- pesquisas e publicações;
- portais estratégicos (fornecedores, investimentos, procurement);
- concursos e seleções;
- favoritos, clientes, feedback e radar de compatibilidade cliente × oportunidade.

## Problemas que resolve

- **Descoberta**: centralizar fontes dispersas (órgãos BR, bancos de fomento, UE, EUA, Ásia, etc.).
- **Triagem**: filtros por prazo, área, escopo geográfico, tipo de recurso.
- **Consultoria**: workspace com clientes, radar de fomento e pré-cadastro de projetos.
- **Operação**: pipeline Python de coleta → normalização → carga no Supabase; UI React consome views `vw_*_front`.

## Módulos principais (produto)

| Módulo | Onde vive | Persistência |
|--------|-----------|--------------|
| Editais / oportunidades | `/editais`, `/edital/:id`, Dashboard | `public.edital`, view `vw_editais_front` |
| Radar de Fomento | `/radar-fomento` | Views + `cliente` + match no front |
| Workspace Consultor | `/workspace-consultor` | `cliente`, editais via views |
| Notícias | `/noticias` | `public.noticia`, `vw_noticias_front` |
| Pesquisas | `/pesquisas` | `public.pesquisa`, `vw_pesquisas_front` |
| Portais estratégicos | `/portais-estrategicos` | `portal_estrategico`, `vw_fornecedores_front`, `vw_investimentos_front` |
| Concursos | `/concursos` | `concurso_selecao`, `vw_concursos_front`, `vw_vestibulares_front` |
| Cadastros / Admin | `/cadastros` | `edital`, `usuario`, `cliente` (+ `organizacao` esperada) |
| Favoritos | integrado | `edital_favorito`, `vw_editais_favoritos_front` |
| Feedback edital | modal | `edital_feedback` |
| Feedback app | global | `app_feedback` (proposta; não no PostgREST staging) |
| Ajuda / Tutorial | global | `helpContent.js` (sem DB) |

Regra de produto (backend): **nem toda oportunidade estratégica é um edital** — portais ficam em `portal_estrategico`, não em `edital`.

## Fluxo geral dos dados

```
Fontes externas (sites, APIs, PDFs)
        │
        ▼
Crawlers / scrapers (backend/<fonte>/, scripts/)
        │
        ▼
JSON padronizado (backend/CORE/transformer/*.json + transformer.py)
        │
        ▼
CORE/transformer.py  →  normalização, PDF, taxonomia, roteamento
        │
        ▼
CORE/loader.py  →  upsert Supabase (edital | noticia | pesquisa)
        │
        ▼
PostgreSQL (Supabase) — tabelas + views vw_*_front
        │
        ▼
Frontend React / Desktop Tauri — @supabase/supabase-js (anon + RLS)
        │
        ▼
Usuário (consultor, admin)
```

Orquestração: `backend/main.py` (`daily`, `apply-edital`, `apply-news`, validações). Legado: `main_legacy_pipeline.py`.

Enriquecimento analítico (Backend 9–10.1): `noise_classifier`, `validity_resolver`, `opportunity_enricher` — **dry-run / scripts**; colunas não persistidas em `edital` no staging (ver schema auditado).

## Fluxo geral do usuário

```
Login (Supabase Auth) → AuthCallback
        │
        ▼
Dashboard (/dashboard) — métricas, atalhos, listas
        │
        ├── Editais (/editais) — filtros, export XLSX/PDF
        ├── Detalhe (/edital/:id)
        ├── Radar (/radar-fomento) — cliente × oportunidades
        ├── Workspace Consultor (/workspace-consultor)
        ├── Notícias / Pesquisas / Portais / Concursos
        └── Cadastros (/cadastros) — editais, usuários, clientes, orgs
```

Navegação: menu hambúrguer (`AppNavigationMenu.jsx` + `appNavigationConfig.js`).

## Backend vs frontend vs banco vs EXE

| Camada | Papel | Tecnologia |
|--------|--------|------------|
| **Banco** | Persistência, RLS, views para UI | Supabase = PostgreSQL + PostgREST |
| **Backend** | ETL, classificação, auditorias, cargas | Python (sem API HTTP própria para o app) |
| **Frontend** | UI web | React 19 + Vite 8, Supabase JS direto |
| **EXE / Desktop** | Mesmo frontend em WebView | Tauri 2 (`npm run desktop:build`) |

**“API” para o app:** não há servidor FastAPI/Flask consumido pelo React. A integração é **Supabase client** → PostgREST + Auth. Edge Function opcional: `backend/supabase/functions/report-edital-feedback/`.

---

# 2. Tecnologias utilizadas

Evidência: `package.json`, `vite.config.js`, `src-tauri/`, imports em `backend/CORE`, `backend/main.py`, venv em `backend/CORE/.venv` (quando presente).

| Camada | Tecnologia / biblioteca | Onde aparece | Função |
|--------|------------------------|--------------|--------|
| Backend — linguagem | Python 3.12+ (observado em ambiente) | `backend/`, `CORE/` | ETL, scrapers, testes |
| Backend — API HTTP própria | Não identificado | — | App não depende de REST Python |
| Backend — DB client | `supabase` (supabase-py) | `CORE/db.py`, `loader.py` | Upsert/select staging |
| Backend — env | `python-dotenv` | `CORE/db.py`, `main.py` | `.env.staging`, `CORE/.env` |
| Backend — HTTP | `requests` | `asia_source_common.py`, `link_health.py`, crawlers | Download páginas/APIs |
| Backend — HTML | `beautifulsoup4` | venv CORE / scrapers | Parsing HTML |
| Backend — PDF | `pypdf` (opcional) | `CORE/transformer.py` | Extração texto PDF |
| Backend — testes | `pytest` | `backend/tests/` (36 ficheiros) | Regressão CORE e crawlers |
| Backend — concorrência | `concurrent.futures` | `loader.py` | Cargas paralelas |
| Dados | PostgreSQL 15+ (Supabase) | PostgREST OpenAPI | Schema `public` |
| Dados — extensão | `pgcrypto` | migrations | UUIDs |
| Frontend — linguagem | JavaScript (JSX) | `frontend/EditalFinder-React/src` | UI |
| Frontend — framework | React 19 | `package.json` | Componentes |
| Frontend — router | React Router 7 | `src/router/index.jsx` | Rotas SPA |
| Frontend — bundler | Vite 8 | `vite.config.js` | Dev/build |
| Frontend — plugin | `@vitejs/plugin-react` | `vite.config.js` | JSX |
| Frontend — dados | `@supabase/supabase-js` | `services/supabaseClient.js` | Auth + queries |
| Frontend — virtualização | `react-window` | listas grandes | Performance listas |
| Frontend — PDF export | `jspdf`, `jspdf-autotable` | `pdfExportService.js` | Export tabelas PDF |
| Frontend — planilha | `xlsx` (SheetJS) | `EditaisPage.jsx`, etc. | Export Excel |
| Frontend — lint | ESLint 9 | `package.json` | Qualidade JS |
| Frontend — testes | Node `node:test` | `npm test`, `radarMatch.test.js` | Teste unitário limitado |
| Desktop | Tauri 2 + Rust | `src-tauri/` | Instalador Windows `.exe` |
| Desktop — API bridge | `@tauri-apps/api` | `package.json` | Shell nativo |
| Deploy web | `gh-pages` | `package.json` `deploy` | GitHub Pages `/editalfinder/` |
| Edge (opcional) | Deno/TS Supabase Function | `backend/supabase/functions/` | E-mail feedback (futuro) |
| Orquestração | Scripts PowerShell/bash implícitos | `docs/DAILY_PIPELINE.md` | Pipeline diário |
| requirements.txt central | **Não identificado** no repo | — | Dependências via `CORE/.venv` local |

**Estado global frontend:** Context API — `AuthContext`, `SettingsContext`, `AppFeedbackContext`, `AppHelpContext` (`src/contexts/`).

**Formulários:** componentes controlados (`useState`); sem React Hook Form identificado.

**Gráficos:** CSS/custom no Dashboard (`dashboard.css`, agregações JS); sem Chart.js/Recharts no `package.json`.

**PyInstaller:** não identificado; desktop usa **Tauri**, não PyInstaller.

---

# 3. Estrutura de pastas

Árvore principal (sem `node_modules`, `dist`, `.venv`, `target`, caches, `audit_reports*` massivos).

```txt
edital/                                    # Raiz do repositório
├── docs/                                  # Documentação transversal (este ficheiro, desktop, release)
├── scripts/                               # Utilitários raiz (ex.: create_desktop_release.py)
├── releases/                              # Artefactos desktop versionados (README)
│
├── backend/                               # Python ETL + Supabase
│   ├── CORE/                              # Núcleo: loader, transformer, classificadores, db
│   │   ├── transformer/                   # JSON *_standardized.json por fonte
│   │   ├── logs/
│   │   └── *.py                           # pipeline, schema, merge, enricher, etc.
│   ├── scripts/                           # ~91 scripts: audit, load, crawl, dry-run
│   ├── migrations/                        # SQL versionado (Supabase)
│   ├── database/
│   │   └── schema_current.sql             # ★ Schema auditado (fonte de verdade)
│   ├── docs/                              # Documentação backend + sql/
│   │   └── backend/
│   │       └── DATABASE_CURRENT_SCHEMA.md # ★ Mapa do banco auditado
│   ├── tests/                             # pytest (36 test_*.py)
│   ├── outputs/                           # Saídas dry-run (gitignored em uso normal)
│   ├── config/                            # pipeline_sources.json, source_readiness.json
│   ├── concursos/                         # Módulo concursos (crawlers MVP)
│   ├── supabase/functions/                # Edge functions
│   ├── main.py                            # Orquestrador pipeline diário
│   ├── main_legacy_pipeline.py            # Pipeline monolítico legado
│   ├── README.md
│   └── <fonte>/                          # Um diretório por fonte (cnpq, bnb, grants_gov, …)
│       └── main_*.py ou scraper           # Centenas de pastas de fonte
│
└── frontend/EditalFinder-React/           # App React
    ├── src/
    │   ├── pages/                         # Dashboard, Editais, Radar, Concursos, …
    │   ├── components/                    # UI (dashboard, radar, admin, layout, help)
    │   ├── services/                      # Supabase, export PDF, favoritos, match
    │   ├── contexts/                      # Auth, Settings, Feedback, Help
    │   ├── router/                        # Rotas protegidas
    │   ├── config/                        # env.js, routerBase, navigation
    │   ├── utils/                         # edital, radar, dashboard, permissions
    │   ├── constants/
    │   └── styles/
    ├── src-tauri/                         # Desktop Tauri (Rust)
    ├── public/
    ├── package.json
    ├── vite.config.js
    └── .env.example
```

### Pastas `backend/<fonte>/` (amostra)

Cada fonte costuma ter `main_<fonte>.py` ou padrão `scraper_generic.py` + config. Exemplos reais no repo:

`cnpq`, `bndes`, `bnb`, `bdmg`, `finep`, `fapesp`, `fapemig`, `grants_gov`, `horizon_europe`, `eic`, `embrapii`, `concursos` (várias bancas), `china_*`, `japan_*`, `dod_sbir_sttr`, `petrobras`, `aneel`, …

### `backend/CORE/` — módulos Python centrais

| Ficheiro | Função |
|----------|--------|
| `db.py` | Cliente Supabase |
| `loader.py` | Upsert `edital`, anexos, extra_campo, histórico |
| `transformer.py` | Normalização massiva → payload DB |
| `schema.py` / `merge_utils.py` | Normalização e sanitização Postgres |
| `content_routing.py` | Roteamento edital vs notícia vs pesquisa |
| `taxonomy_filtros.py` | Colunas filtro + extras |
| `noise_classifier.py` | Backend 10.1 acionabilidade/ruído |
| `validity_resolver.py` | Validade/prazo lógico |
| `opportunity_enricher.py` | Pacote enriquecimento |
| `link_health.py` | Saúde de links (auditoria) |
| `editais_visibility.py` | Curadoria visibilidade front |

### `backend/scripts/` — categorias

| Tipo | Exemplos |
|------|----------|
| Carga | `load_ready_sources.py`, `load_news_research_sources.py`, `load_portais_estrategicos.py`, `load_concursos_selecao.py` |
| Auditoria | `audit_noise_backend.py`, `audit_validity_backend.py`, `audit_edital_links.py`, `dry_run_quality_enrichment.py` |
| Validação pós-carga | `validate_database_after_load.py` |
| Notícias/pesquisa | `crawl_news_research_sources.py` |
| Shadow Backend 7+ | `_backend_shadow_common.py` |

---

# 4. Banco de dados (resumo alinhado ao schema auditado)

**Motor:** Supabase PostgreSQL. **Sem SQLite** como banco principal.

| Conceito | Valor confirmado (staging) |
|----------|----------------------------|
| Tabela central | `public.edital` (107 colunas) |
| PK | `id_edital` (bigint) |
| URL canónica / dedup | `link` UNIQUE NOT NULL |
| Organização (texto) | `orgao_responsavel` — **não** `organizacao_responsavel` |
| FK organização | `id_organizacao` — tabela `organizacao` **ausente** no PostgREST |
| PDF / inscrição / detalhe | `pdf_url`, `link_inscricao`, `url_detalhe` |
| Não usar como canónico | `url_edital`, `url_pdf`, `inscricao_url`, `url_inscricao` |
| Enriquecimento B10.1 | `actionability_type`, `is_noise`, `validade_status`, etc. — **não** colunas em `edital` |
| View feed editais | `vw_editais_front` — **sem** `orgao_responsavel` / `id_organizacao` |

Tabelas ausentes no staging mas no código: `organizacao`, `app_feedback`, `edital_backend_enrichment_shadow`.

Detalhe completo: [`DATABASE_CURRENT_SCHEMA.md`](../backend/docs/backend/DATABASE_CURRENT_SCHEMA.md).  
DDL: [`schema_current.sql`](../backend/database/schema_current.sql).

---

# 5. Integração de dados (frontend ↔ Supabase)

| Serviço | Ficheiro | Tabela / view |
|---------|----------|----------------|
| Editais | `editaisService.js` / `dataService.js` | `VITE_VIEW_EDITAIS` → `vw_editais_front` |
| Notícias | `noticiasService.js` | `vw_noticias_front` |
| Pesquisas | `pesquisasService.js` | `vw_pesquisas_front` |
| Portais | `portaisEstrategicosService.js` | `vw_fornecedores_front`, `vw_investimentos_front` |
| Concursos | `concursosService.js` | `vw_concursos_front`, `vw_vestibulares_front` |
| Favoritos | `favoritosService.js` | `edital_favorito`, `vw_editais_favoritos_front` |
| Auth | `authService.js` | `usuario`, Supabase Auth |
| Clientes | `dataService.js` | `cliente` |
| Organizações | `dataService.js` | `organizacao` (**falha se tabela não exposta**) |
| Admin CRUD edital | `dataService.js` | `edital` (escrita direta) |
| Match radar | `matchService.js` | lógica client-side + dados carregados |
| Classificação UI | `classificationService.js` | heurística local (não persiste B10) |

Mapeamento de linha: `utils/edital/editalRowMapper.js` (view → modelo UI).

---

# 6. Pipeline backend (Python)

| Etapa | Componente |
|-------|------------|
| Config fontes | `config/pipeline_sources.json`, `config/source_readiness.json` |
| Crawl | `backend/<fonte>/`, `scripts/crawl_*.py` |
| Transform | `CORE/transformer.py` → `CORE/transformer/*_standardized.json` |
| Roteamento | `content_routing.py` → `edital` \| `noticia` \| `pesquisa` |
| Load | `loader.py` — upsert `on_conflict=link` |
| Log carga | `carga_execucao` |
| Histórico | `edital_historico` (opcional no load) |
| Orquestração | `main.py` subcomandos `daily`, `apply-edital`, `apply-news`, `clean-staging` |

Documentação operacional: `backend/docs/DAILY_PIPELINE.md`, `backend/docs/STAGING_LOADER.md` (se existir).

Variáveis críticas (loader):

- `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` ou `SUPABASE_KEY`
- `EDITALFINDER_ENV=staging`, `EDITALFINDER_ALLOW_STAGING_APPLY=true` (para escrita)

---

# 7. Frontend (React)

| Área | Localização |
|------|-------------|
| Entrada | `main.jsx` → `App.jsx` |
| Rotas | `src/router/index.jsx` |
| Layout | `components/layout/Header.jsx`, `AppNavigationMenu.jsx` |
| Proteção | `router/ProtectedRoute.jsx` |
| Permissões | `utils/permissions.js` |
| Export PDF | `services/pdfExportService.js` |
| Export XLSX | `xlsx` em `EditaisPage.jsx` |
| Erros globais | `AppErrorBoundary`, `AppFeedback` |
| Ajuda | `helpContent.js`, `AppHelpModal.jsx` |

**Basename web:** `/editalfinder` (`vite.config.js`, `ROUTER_BASENAME`).  
**Desktop Tauri:** basename vazio, `base: /`.

Build: `npm run build` → `dist/`. Deploy: GitHub Pages (`gh-pages`).

---

# 8. Desktop (EXE)

| Item | Detalhe |
|------|---------|
| Tecnologia | Tauri 2 (Rust + WebView2) |
| Scripts | `npm run desktop:dev`, `desktop:build`, `desktop:release` |
| Doc | [`DESKTOP_APP_WINDOWS.md`](DESKTOP_APP_WINDOWS.md) |
| Requisitos rede | Online — mesmo Supabase que a web |
| Versão | `src-tauri/tauri.conf.json` + `config/appVersion.js` |

Não confundir com backend Python empacotado; o “EXE” é o shell Tauri à volta do React buildado.

---

# 9. Variáveis de ambiente (resumo)

### Frontend (`.env.local` — ver `.env.example`)

| Variável | Uso |
|----------|-----|
| `VITE_SUPABASE_URL` | Projeto Supabase |
| `VITE_SUPABASE_ANON_KEY` | Chave anon (RLS) |
| `VITE_VIEW_EDITAIS` | Default `vw_editais_front` |
| `VITE_ENABLE_CONSULTOR_WORKSPACE` | Workspace consultor |
| `VITE_APP_ENV` | local / staging / production |

### Backend (`.env.staging` — ver `.env.staging.example`)

| Variável | Uso |
|----------|-----|
| `SUPABASE_URL` | URL projeto |
| `SUPABASE_SERVICE_ROLE_KEY` | Carga/auditoria (nunca no Vite) |
| `EDITALFINDER_ENV` | staging |
| `EDITALFINDER_ALLOW_STAGING_APPLY` | Gate de escrita |

---

# 10. Testes

| Camada | Comando | Quantidade |
|--------|---------|------------|
| Backend | `cd backend && python -m pytest tests/` | 36 ficheiros (261+ testes observados) |
| Frontend | `cd frontend/EditalFinder-React && npm test` | `radarMatch.test.js` (Node test) |

---

# 11. Bugs e limitações conhecidos (inventário — sem correção nesta etapa)

Registados para alinhamento futuro; **não corrigidos** nesta tarefa.

| # | Sintoma | Área provável | Notas técnicas |
|---|---------|---------------|----------------|
| 1 | Botão “Abrir edital” — clique normal sem efeito | Frontend / Desktop | Verificar handlers vs `<a href>`; Tauri WebView; rotas `/edital/:id` |
| 2 | Radar: botões “Inscrição” e “PDF” sem efeito | `RadarFomento.jsx`, `CardEditalRadar.jsx` | Componentes usam `<a href>` — validar URLs vazias no mapper ou bloqueio `linkHealth` |
| 3 | Export PDF editais/filtros desconfigurada | `pdfExportService.js`, `EditaisPage.jsx` | jsPDF + filtros Dashboard |
| 4 | Cadastro edital exige “Organização Responsável” | `EditalForm.jsx` | Campo `id_organizacao` + tabela `organizacao` **ausente** no staging |
| 5 | Reportar problema: modal OK, envio falha | `appFeedbackService.js` | Tabela `app_feedback` não exposta no PostgREST; fila `localStorage` |
| 6 | Planilha exporta OK | `EditaisPage.jsx` + `xlsx` | Referência positiva |
| 7 | Notícias exportam OK | `Noticias.jsx` | Referência positiva |
| 8 | Concursos carregam; validar “abrir edital” | `ConcursosPage.jsx` | `link` / `link_edital` em `concurso_selecao` |

**Divergência schema ↔ UI (organização):**

- Label: “Organização Responsável”.
- Campo salvo: `id_organizacao`.
- Coluna textual no DB: `orgao_responsavel`.
- View lista: não expõe órgão nem FK.

**Logging de links (DEV):** `onEditalLinkClick` em `logEditalLinkClick.js` só faz `console.log` em DEV; em produção é no-op — não deve bloquear navegação se `<a href>` estiver correto.

---

# 12. Documentação relacionada (índice)

| Documento | Tema |
|-----------|------|
| [`DATABASE_CURRENT_SCHEMA.md`](../backend/docs/backend/DATABASE_CURRENT_SCHEMA.md) | Schema auditado |
| [`schema_current.sql`](../backend/database/schema_current.sql) | DDL de referência |
| [`FRONTEND_BACKEND_CONTEXT.md`](../backend/docs/FRONTEND_BACKEND_CONTEXT.md) | Consumo views, módulos UI |
| [`DAILY_PIPELINE.md`](../backend/docs/DAILY_PIPELINE.md) | Pipeline `main.py` |
| [`BACKEND_10_1_ACTIONABILITY_PRIORITY_FIX.md`](../backend/docs/backend/BACKEND_10_1_ACTIONABILITY_PRIORITY_FIX.md) | Classificador ruído |
| [`DESKTOP_APP_WINDOWS.md`](DESKTOP_APP_WINDOWS.md) | Tauri / EXE |
| [`APP_HELP_TUTORIAL.md`](../backend/docs/APP_HELP_TUTORIAL.md) | Ajuda in-app |
| [`EDITAIS_FEEDBACK_AND_REPORTING.md`](../backend/docs/EDITAIS_FEEDBACK_AND_REPORTING.md) | Feedback edital |
| [`APP_FEEDBACK_SYSTEM.md`](../backend/docs/APP_FEEDBACK_SYSTEM.md) | Feedback app (proposta) |

---

# 13. Divergências documentação antiga vs estado auditado

| Tema | Doc antiga | Estado auditado (2026-06) |
|------|------------|---------------------------|
| PK notícia/pesquisa | `id_noticia` / `id_pesquisa` bigserial | `id` uuid |
| Coluna organização | `organizacao_responsavel` | **Não existe** — usar `orgao_responsavel` |
| Tabela `organizacao` | Presente em exemplos SQL | **Não exposta** no staging PostgREST |
| Enriquecimento B10 | Às vezes implícito como colunas | Só Python / proposta SQL |
| `README.md` raiz backend | Menciona `supabase/` na raiz | Migrações em `backend/migrations/`; functions em `backend/supabase/` |
| requirements.txt | Referenciado no README | **Não encontrado** — venv local `CORE/.venv` |

---

# 14. Como manter este mapa atualizado

1. Reexecutar introspecção: `python backend/scripts/generate_schema_current_docs.py`.
2. Revisar `backend/docs/backend/DATABASE_CURRENT_SCHEMA.md` se o OpenAPI mudar.
3. Atualizar secções 3 e 5 se novas rotas/views forem adicionadas (`src/router/index.jsx`, `config/env.js`).
4. Não usar o frontend como fonte do schema — usar sempre `schema_current.sql` + introspecção.

---

*Fim do mapa técnico — auditoria somente leitura.*
