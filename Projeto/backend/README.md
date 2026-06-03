# EditalFinder

Plataforma para monitorar oportunidades de fomento, editais, notícias e pesquisas — com painéis para consultoria e radar de clientes.

## Stack

| Camada | Tecnologia |
|--------|------------|
| Frontend | React 19, Vite 8, React Router, Supabase JS (chave **anon**) |
| Backend / ETL | Python (scrapers, transformers, loaders) |
| Dados | Supabase (PostgreSQL + views `vw_*_front`) |

## Estrutura do repositório

```
edital/
├── frontend/EditalFinder-React/   # App React (UI)
├── docs/                          # Planos, SQL de referência, contexto front/back
├── supabase/                      # Migrações e config Supabase
├── scripts/                       # Utilitários e auditoria de pipeline
├── migrations/                    # SQL versionado (quando aplicável)
├── fixtures/                      # Dados de teste (se houver)
└── <fontes>/                      # Scrapers por órgão/fonte (Python)
```

## Como rodar o frontend (local)

```bash
cd frontend/EditalFinder-React
cp .env.example .env.local
# Edite .env.local: VITE_SUPABASE_URL e VITE_SUPABASE_ANON_KEY (apenas anon)
npm install
npm run dev
```

Abra a URL indicada pelo Vite (ex.: `http://localhost:5173/editalfinder`).

## Variáveis de ambiente (frontend)

Copie `frontend/EditalFinder-React/.env.example` → `.env.local`.

Obrigatórias para dados reais:

- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`

Opcionais úteis: `VITE_PUBLIC_SITE_URL`, `VITE_AUTH_CALLBACK_URL`, flags `VITE_ENABLE_*` (Consultor, Radar, Concursos).

**Backend / loader (Python):** use `.env.staging.example` na raiz como modelo — nunca commitar `.env` ou `.env.staging` com chaves reais.

## Scripts principais (frontend)

| Comando | Descrição |
|---------|-----------|
| `npm run dev` | Servidor de desenvolvimento |
| `npm run build` | Build de produção (`dist/`) |
| `npm run preview` | Preview do build |
| `npm test` | Testes unitários (Node test runner) |

## Módulos da aplicação (UI)

- **Dashboard** — `/dashboard` — métricas, prioridades, gráficos, atalhos
- **Editais** — `/editais` — listagem com filtros (prazo, escopo, etc.)
- **Radar de Fomento** — cruzamento cliente × oportunidades
- **Workspace do Consultor** — triagem e pré-cadastro consultivo (`VITE_ENABLE_CONSULTOR_WORKSPACE`, default true)
- **app_feedback** — reportar problema (fila local + envio)
- **Cadastros**, **Notícias**, **Pesquisas**, **Concursos** (conforme flags)

Navegação via menu hambúrguer no header.

## Segurança e Git

- **Não commitar** `.env`, `.env.local`, `.env.staging` nem chaves `service_role`.
- Use apenas **`.env.example`** (valores vazios ou placeholders).
- `node_modules/`, `dist/`, `outputs/`, `audit_reports*/` e dumps estão no `.gitignore`.
- No frontend, use somente a chave **anon** do Supabase (`VITE_SUPABASE_ANON_KEY`).

Documentação adicional: `docs/FRONTEND_BACKEND_CONTEXT.md`, `docs/SECURITY_AUDIT_AND_HARDENING_PLAN.md`.

## Pipeline Python (backend)

Ver `docs/DAILY_PIPELINE.md` e `docs/STAGING_LOADER.md`. Requer `SUPABASE_URL` e chave de serviço **apenas no servidor** — nunca no bundle Vite.

```bash
# Exemplo (ajuste ao seu fluxo)
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt   # se existir na raiz/CORE
```
