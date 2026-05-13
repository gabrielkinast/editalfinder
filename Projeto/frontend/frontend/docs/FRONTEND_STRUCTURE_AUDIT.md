# Auditoria de estrutura — Frontend EditalFinder

**Data:** 2026-05-10  
**Escopo:** `Projeto/frontend/EditalFinder-React` (app React principal em uso com `npm run dev`).  
**Restrições desta fase:** apenas análise; sem alteração de código, movimentação de ficheiros ou novas páginas.

**Documentos de referência lidos:**

- `docs/FRONTEND_BACKEND_CONTEXT.md` — neste repositório não existe cópia na pasta `docs/` do frontend; foi utilizada a versão em `d:\Computational_Physics\My Projects\edital\docs\FRONTEND_BACKEND_CONTEXT.md` (conteúdo alinhado ao produto: views `vw_*`, separação `edital` vs `portal_estrategico`, consumo preferencial por views).

---

## 1. Visão geral

| Aspeto | Estado atual |
|--------|----------------|
| **Framework** | React **19** (`react`, `react-dom`), bundler **Vite 8** (`vite.config.js`, `base: "/editalfinder/"`). |
| **Routing** | **React Router DOM v7** — `BrowserRouter` com `basename="/editalfinder"` em `src/App.jsx`; rotas declarativas em `src/router/index.jsx`; proteção com `src/router/ProtectedRoute.jsx` (auth + RBAC via `permissions.js` / `usePermissions`). |
| **Linguagem** | **JavaScript (.jsx / .js)** — **sem TypeScript** no projeto; não há pasta `types/` nem ficheiros `.ts`/`.tsx`. |
| **Estilos** | Um ficheiro grande `src/styles/global.css` importado em `main.jsx`; **muitos estilos inline** (`style={{ ... }}`) em páginas e componentes. |
| **Backend / dados** | **Supabase JS** (`@supabase/supabase-js`): cliente central em `src/services/supabaseClient.js`; variáveis **`VITE_*`** via `src/config/env.js`; **chave anon** apenas (nunca service role no front). |
| **Estado global** | `AuthContext`, `SettingsContext`; resto é estado local em páginas (`useState`) e alguns hooks dedicados. |

---

## 2. Estrutura de pastas atual (mapa)

```
EditalFinder-React/
├── index.html
├── vite.config.js
├── package.json
├── public/
│   └── docs/…                    # PDF estático referenciado no pré-cadastro
├── src/
│   ├── main.jsx                  # Entrada React + global.css
│   ├── App.jsx                   # Providers + BrowserRouter
│   ├── permissions.js            # RBAC estático + getPermissions()
│   ├── config/
│   │   └── env.js                # VITE_* , nomes de views, feature flags
│   ├── contexts/
│   │   ├── AuthContext.jsx
│   │   └── SettingsContext.jsx
│   ├── router/
│   │   ├── index.jsx             # Rotas
│   │   └── ProtectedRoute.jsx
│   ├── pages/                    # Uma pasta plana com todas as páginas
│   ├── components/
│   │   ├── layout/Header.jsx
│   │   ├── dashboard/…           # Lista editais, filtros, modal detalhe
│   │   ├── feed/…              # Notícias/Pesquisas (lista genérica)
│   │   ├── radar/…
│   │   ├── admin/…             # Forms cadastro + pré-cadastro extenso
│   │   └── ui/Modal.jsx
│   ├── hooks/
│   ├── services/                 # Supabase + domínio + PDF + match + pré-cadastro PDF
│   ├── utils/                    # edital/, precadastro/, formatters, etc.
│   └── styles/global.css
├── .env.example / .env.local     # (local; não versionados)
└── [vários .txt, .sql, .pdf na raiz do pacote — artefactos / doc legado]
```

**Nota:** Na pasta pai `Projeto/frontend/` existem ainda `index.html`, `script.js`, `style.css` (stack **não React**). A auditoria foca na app **Vite/React** que está em produção no fluxo atual.

---

## 3. Rotas e páginas existentes

| Rota (relativa ao basename `/editalfinder`) | Componente | Função |
|-----------------------------------------------|------------|--------|
| `/login` | `Login.jsx` | Autenticação (`authService` + Supabase `usuario` ou demo fixo). |
| `/dashboard` | `Dashboard.jsx` | **Editais** — lista principal, filtros pesados, export PDF/XLSX. |
| `/cadastros` | `Cadastros.jsx` | CRUD usuários/clientes/editais admin + pré-cadastro projeto (modal). |
| `/radar-fomento` | `RadarFomento.jsx` | Radar cliente × editais (`matchService`, `useRadarMatches`). |
| `/indice` | `IndiceCompatibilidade.jsx` | Conteúdo **estático** (explicação do índice); **sem fetch**. |
| `/noticias` | `Noticias.jsx` | Wrapper → `FeedListaPage` + `dataService.getNoticias()`. |
| `/pesquisas` | `Pesquisas.jsx` | Idem → `getPesquisas()`. |
| `/edital/:id` | `EditalDetalhes.jsx` | Detalhe edital + lógica local de compatibilidade mock. |
| `/` | redirect → `/dashboard` | |
| `*` | redirect → `/login` | |

**Rota `/portais-estrategicos`:** **não existe** no `router/index.jsx` atual deste workspace; o menu em `Header.jsx` também **não** inclui item “Portais”. Qualquer implementação futura será adição nova.

**Configurações:** não é página dedicada — **modal** no `Header.jsx` com `SettingsForm.jsx` (alteração de tema/logo via `SettingsContext` + `localStorage`).

---

## 4. Layout, navbar e menu

- **`components/layout/Header.jsx`:** NavLinks para Editais (`/dashboard`), Cadastros (condicional), Radar, Índice, Notícias, Pesquisas; botões Configurações (se `canManageUsers`) e Sair; busca opcional via prop `onSearch`.
- **Estados de loading/erro/vazio:** variam por página (ver secção 6); não há biblioteca de “empty states” unificada.

---

## 5. Conexão Supabase e camada de serviços

| Ficheiro | Papel |
|----------|--------|
| `src/config/env.js` | Lê `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` (fallback legado `VITE_SUPABASE_KEY`), nomes **`VITE_VIEW_EDITAIS`**, `VITE_VIEW_NOTICIAS`, `VITE_VIEW_PESQUISAS`, etc., e **feature flags** (`VITE_ENABLE_*`). |
| `src/services/supabaseClient.js` | `createClient` com anon key; `isSupabaseConfigured`; aviso em consola se faltar env. |
| `src/services/api.js` | Reexport do cliente (compatibilidade com imports antigos). |
| `src/services/dataService.js` | **Monólito principal:** todas as queries Supabase às views/tabelas (paginação `.range`). Usa nomes de view vindos de **`env.js`**. Logs em dev para editais/notícias/pesquisas. |
| `src/services/authService.js` | Login: query `usuario` no Supabase + fallback demo; **não** usa service role. |

**Views/tabelas consumidas (via `dataService`):**

| Área | Fonte preferencial | Fallback / extra |
|------|-------------------|------------------|
| Editais | `VIEW_EDITAIS` → tipicamente `vw_editais_front` | `edital` direto |
| Notícias | `VIEW_NOTICIAS` → `vw_noticias_front` | tabela `noticia` |
| Pesquisas | `VIEW_PESQUISAS` → `vw_pesquisas_front` | tabela `pesquisa` |
| Radar / Dashboard | Mesmos editais + `cliente` | — |
| Cadastros | `usuario`, `cliente`, `edital`, `organizacao` | — |
| Detalhe edital | `edital`, `edital_anexo` | — |

**Consumo direto de Supabase fora de `dataService`:** essencialmente **`authService`** (e indiretamente o mesmo cliente). Não há chamadas `supabase.from` espalhadas por páginas.

---

## 6. Como cada página obtém dados (resumo)

| Página | Fetch | View/tabela | VITE_ | Loading / erro / empty | Filtros |
|--------|--------|-------------|-------|---------------------------|---------|
| **Dashboard (Editais)** | `dataService.getEditais()` | `VITE_VIEW_EDITAIS` + fallback `edital` | Sim (via `env` → `dataService`) | Loading sim; erro → lista vazia + console; empty + sugestões | Sidebar `filtersEngine`, busca, ordenação local |
| **Radar** | `getClients()` + `getEditais()` em paralelo | `cliente` + mesma origem de editais | Sim | `loading`, `loadError`, `RadarLoading`; cards progressivos | Filtros locais + `useRadarMatches` |
| **Notícias** | `getNoticias()` | `VIEW_NOTICIAS` / `noticia` | Sim | Via `FeedListaPage`: loading, erro, empty | `applyFeedFilters` + sidebar |
| **Pesquisas** | `getPesquisas()` | `VIEW_PESQUISAS` / `pesquisa` | Sim | Idem FeedListaPage | Idem |
| **Cadastros** | `getUsers` / `getClients` / `getAllEditaisAdmin` conforme aba | tabelas cruas | Sim | Loading global na secção; alert em erro | Busca + filtros por aba |
| **EditalDetalhes** | `getEditalById`, anexos | `edital`, `edital_anexo` | Sim | Estado local | — |
| **Login** | `authService.login` | `usuario` | Sim (cliente Supabase) | Loading no botão | — |
| **Índice** | *nenhum* | — | — | N/A | N/A |

---

## 7. Hooks

| Hook | Uso |
|------|-----|
| `usePermissions` | RBAC a partir do utilizador em contexto. |
| `useDebouncedValue` | Busca no Dashboard e Radar. |
| `useEditaisPagePrefs` | Preferências persistidas (tamanho página, ruído, etc.). |
| `useRadarMatches` | Cálculo assíncrono de matches (usa `matchService`, não Supabase direto). |

Não existem hooks dedicados `useEditais` / `useNoticias` — a lógica de fetch está nas páginas ou em `FeedListaPage`.

---

## 8. Tipos e interfaces

- **Nenhum** ficheiro de tipos TypeScript.
- Contratos de dados implícitos nos **mappers** (`utils/edital/editalRowMapper.js`) e objetos normalizados no código.

---

## 9. Estilos e padrões UI

- **`global.css`:** milhares de linhas — layout dashboard, admin, radar, modais, responsivo.
- **Inline:** frequente em `Dashboard`, `Radar`, `Cadastros`, `Header`, índice — dificulta tema consistente e manutenção.
- **Design tokens:** variáveis CSS (`:root`) parciais; `SettingsContext` injeta `--primary-blue` / `--primary-yellow` quando configurado.

---

## 10. Estados loading / erro / empty

| Padrão | Onde |
|--------|------|
| Spinner / texto “Carregando” | `Dashboard`, `FeedListaPage`, `RadarFomento`, `Cadastros`, `AuthContext` |
| Mensagem de erro | `FeedListaPage`, `RadarFomento` |
| Empty state | `Dashboard` (sugestões + empty-state CSS), `FeedListaPage`, grelhas sem cards |
| Sem padronização | Componentes duplicam markup em vez de um `components/states/*` |

---

## 11. Problemas de organização identificados

1. **`dataService.js` monolítico** — todas as entidades num único ficheiro; difícil testar e evoluir por domínio (editais vs notícias vs cadastros).
2. **Duplicação de filtros de “feed”** — `FeedListaPage` + `FeedSidebarFilters` vs motor de editais (`filtersEngine`) — modelos de dados diferentes mas UX semelhante.
3. **Páginas muito grandes** — sobretudo `Dashboard.jsx` e `RadarFomento.jsx` (centenas de linhas + lógica + UI).
4. **Sem camada `types/` ou JSDoc** — risco de divergência face ao PostgREST e às views.
5. **Feature flags em `env.js`** — exportadas mas **não** usadas para ocultar rotas/abas (ex.: radar sempre visível no menu).
6. **Nomes inconsistentes** — `Dashboard` = “Editais” no menu; `FeedItemCard` acoplado a campos de notícia/pesquisa com meta tipo “Prazo/Limite” (semântica de edital em feeds não-editais — ver contexto backend: separar linguagem).
7. **Artefactos na raiz do pacote** — `.sql`, `.txt`, PDF em `EditalFinder-React/` misturam código e documentação de BD.
8. **Duas “camadas” frontend** na pasta `frontend/` (React vs HTML estático) — risco de confusão para novos devs.
9. **Código morto / risco** — sem análise estática automática nesta auditoria; módulo pré-cadastro é grande — alterações exigem testes manuais.

---

## 12. Proposta de estrutura (adaptada ao projeto real)

Sugestão em **JavaScript** (o projeto não usa TS hoje); se migrarem a TS, renomear para `.ts`/`.tsx` gradualmente.

```
src/
  app/
    providers.jsx           # Auth + Settings (hoje App.jsx)
    routes.jsx              # ou routes/index.jsx
  pages/
    editais/                # Dashboard + eventualmente split
    radar/
    noticias/
    pesquisas/
    cadastros/
    indice/
    login/
    edital-detalhe/
    portais-estrategicos/   # futuro
  components/
    layout/                 # Header, shell
    edital/                 # cards, sidebars, chips (hoje dashboard/)
    feed/                   # lista genérica + filtros feed
    radar/
    admin/
    ui/
    states/                 # EmptyState, ErrorBanner, PageLoader
  services/
    supabaseClient.js
    env.js → pode ficar em config/ ou ser importado só por services
    editaisService.js       # extrair de dataService
    noticiasService.js
    pesquisasService.js
    cadastrosService.js     # usuario, cliente, org, edital admin
    authService.js
    matchService.js
    pdfExportService.js
  hooks/
    useEditais.js           # opcional: fetch + estado
    useFeedCollection.js    # genérico para notícias/pesquisas
    …
  config/
    env.js
  utils/
  styles/
    global.css
    tokens.css              # opcional: extrair variáveis
```

Isto espelha a sugestão do utilizador, trocando `.ts` por `.jsx`/`.js` até decisão de migração.

---

## 13. Onde encaixa **Portais Estratégicos** (futuro)

Alinhado a `FRONTEND_BACKEND_CONTEXT.md` e variáveis já preparadas em `env.js`:

| Elemento | Proposta |
|----------|----------|
| **Rota** | `/portais-estrategicos` — novo `Route` + `NavLink` no `Header` (fora do âmbito desta auditoria). |
| **Página** | `pages/portais-estrategicos/PortaisEstrategicos.jsx` — abas Fornecedores / Investimentos. |
| **Dados** | `services/portaisEstrategicosService.js` ou métodos em serviço dedicado: `from(env.VIEW_FORNECEDORES)` e `from(env.VIEW_INVESTIMENTOS)` — **não** misturar com `vw_editais_front`. |
| **Componentes** | `PortalEstrategicoCard.jsx`, filtros próprios (ou generalizar `feed` com schema diferente). |
| **Feature flags** | `FEATURE_PORTAIS_ESTRATEGICOS`, `FEATURE_FORNECEDORES`, `FEATURE_INVESTIMENTOS` já existem em `env.js`; usar para render condicional e lazy load. |

---

## 14. Plano de reorganização em fases

| Fase | Ações | Risco |
|------|--------|-------|
| **0** | Documentar imports críticos (este relatório); congelar uma branch. | Baixo |
| **1** | Extrair `editaisService` / `noticiasService` / `pesquisasService` a partir de `dataService`; manter `dataService` como façade temporário reexportando. | Médio |
| **2** | Introduzir pasta `components/states/*` e substituir blocos repetidos sem mudar CSS global. | Baixo |
| **3** | Renomear pastas `pages/` por domínio (mover ficheiros + atualizar imports); ferramenta ou IDE refactor. | Médio |
| **4** | Reduzir inline styles aos poucos (componentes wrapper). | Baixo contínuo |
| **5** | (Opcional) Adicionar JSDoc `@typedef` ou migrar a TypeScript incremental (`allowJs`). | Médio |

---

## 15. Ficheiros que podem mover-se com **menor** risco

- Páginas “folha” pequenas: `Noticias.jsx`, `Pesquisas.jsx`, `Login.jsx`, `IndiceCompatibilidade.jsx` (após atualizar imports em `router/index.jsx`).
- `permissions.js` para `src/config/` ou `src/auth/` (import único em poucos sítios).
- PDF em `public/docs/` — já está no sítio correto para assets estáticos.

---

## 16. Ficheiros que exigem **cuidado**

- `Dashboard.jsx`, `RadarFomento.jsx`, `Cadastros.jsx`, `ProjetoPrecadastroForm.jsx` — muitas dependências internas.
- `utils/edital/*` — importado em cadeia pelo Dashboard e Radar.
- `services/pdfExportService.js` + `precadastroPdf/*` — caminhos e blobs.
- `router/ProtectedRoute.jsx` + `permissions.js` — qualquer mudança afeta todas as rotas.
- `vite.config.js` + `App.jsx` **basename** — não quebrar URLs em deploy GitHub Pages.

---

## 17. Riscos gerais

- **Regressões em imports** ao mover pastas sem path aliases (`@/`).
- **Deploy** com `base: "/editalfinder/"` — rotas e assets devem continuar alinhados.
- **RLS Supabase** — estrutura de pastas não corrige contagem zero; apenas facilita diagnóstico em serviços.

---

## 18. Próximos passos recomendados

1. Copiar ou sincronizar `FRONTEND_BACKEND_CONTEXT.md` para `Projeto/frontend/docs/` para referência única no repo.
2. Decidir se a reorganização inclui **alias** `@/` no `vite.config.js`.
3. Extrair serviços por domínio mantendo testes manuais nas rotas principais.
4. Quando for implementar Portais: criar rota, serviço dedicado às views `VITE_VIEW_FORNECEDORES` / `VITE_VIEW_INVESTIMENTOS`, respeitando semântica “não é edital” do documento de contexto.

---

## 19. Verificação rápida `vw_editais_front` (operacional)

Com `.env.local` preenchido e `npm run dev`:

1. Consola do browser (modo desenvolvimento): mensagens `[dataService.getEditais]` com `view` e `count`.
2. SQL no Supabase: `select count(*) from public.vw_editais_front;`
3. Dashboard: número de cards / mensagens de lista vazia coerentes com RLS anon.

---

*Fim do relatório — apenas documentação; nenhuma alteração de código foi efetuada durante esta auditoria.*
