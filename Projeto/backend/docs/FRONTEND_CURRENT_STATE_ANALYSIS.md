# Frontend — Current State Analysis (React/Vite) — EditalFinder

**Objetivo:** entender e documentar o frontend atual (sem alterar código), para orientar próximos passos.

**Escopo analisado:** apenas o frontend React/Vite dentro deste repositório, e a documentação existente relacionada ao frontend.

---

## 1) Local do frontend (pasta real)

O frontend React/Vite está em:

- `frontend/EditalFinder-React/`

Evidências:

- `frontend/EditalFinder-React/package.json`
- `frontend/EditalFinder-React/vite.config.js`
- `frontend/EditalFinder-React/src/` (router, pages, components, services)

Observação: existe também uma pasta `frontend/docs/` com documentação do frontend (ver secção 11).

---

## 2) Stack detectada (framework, versões, toolchain)

### Framework e bundler

- **React**: `^19.2.4`
- **React Router DOM**: `^7.13.1`
- **Vite**: `^8.0.0`
- **Supabase JS**: `^2.99.2`
- **Exportação**: `jspdf`, `jspdf-autotable`, `xlsx`

Fonte: `frontend/EditalFinder-React/package.json`.

### Modo de deploy / basepath

Há configuração explícita para publicar a SPA sob subpath **`/editalfinder/`**:

- Vite: `base: "/editalfinder/"` em `frontend/EditalFinder-React/vite.config.js`
- Router: `BrowserRouter basename="/editalfinder"` em `frontend/EditalFinder-React/src/App.jsx`
- Em dev, existe middleware para redirecionar `/` → `/editalfinder/` (evita “página em branco”).

### Linguagem / typing

- Código majoritariamente em **JavaScript** (`.js` / `.jsx`).
- Existe **JSDoc de shapes** em `src/types/*.js` (sem TypeScript).

### CSS / estilos globais

- CSS global importado em `src/main.jsx`: `src/styles/global.css`.
- Há CSS local em páginas/componentes específicos (ex.: portais e cards).

---

## 3) Estrutura de pastas (mapa técnico)

Raiz do app:

```
frontend/EditalFinder-React/
  vite.config.js
  package.json
  src/
    main.jsx
    App.jsx
    router/
      index.jsx
      ProtectedRoute.jsx
    config/
      env.js
    contexts/
      AuthContext.jsx
      SettingsContext.jsx
    pages/
      Dashboard.jsx
      Cadastros.jsx
      RadarFomento.jsx
      Noticias.jsx
      Pesquisas.jsx
      PortaisEstrategicos/PortaisEstrategicosPage.jsx
      EditalDetalhes.jsx
      IndiceCompatibilidade.jsx
      FeedListaPage.jsx
      Login.jsx
    components/
      layout/Header.jsx
      ui/Modal.jsx
      states/{LoadingState,ErrorState,EmptyState}.jsx
      badges/StatusBadge.jsx
      dashboard/* (cards, filtros, modal detalhe, stats)
      feed/* (card e sidebar de filtros)
      radar/* (lista clientes, card radar, loading)
      admin/* (CRUD, forms, pré-cadastro)
    services/
      supabaseClient.js
      api.js
      dataService.js
      authService.js
      matchService.js
      classificationService.js
      pdfExportService.js
      precadastroProjetoPdf.js
      precadastroPdf/* (render/model/theme)
      *Service.js (wrappers por domínio, incluindo portais)
    hooks/*
    utils/*
    styles/global.css
  docs/ (documentos de UX e pré-cadastro, ver secção 11)
```

---

## 4) Rotas e páginas (mapeamento completo)

Definição de rotas: `frontend/EditalFinder-React/src/router/index.jsx`.

**Nota importante:** todas as rotas abaixo são **relativas** ao `basename="/editalfinder"`.

### Rotas registradas

| Path | Página | Proteção | Função |
|------|--------|----------|--------|
| `/login` | `pages/Login.jsx` | pública | Login (Supabase `usuario` + fallback demo). |
| `/dashboard` | `pages/Dashboard.jsx` | `ProtectedRoute` | Lista de Editais (catálogo principal), filtros, export. |
| `/cadastros` | `pages/Cadastros.jsx` | `ProtectedRoute(requiredPermission="canViewCadastros")` | CRUD e pré-cadastro por cliente (modal). |
| `/radar-fomento` | `pages/RadarFomento.jsx` | `ProtectedRoute` | Radar cliente × editais (compatibilidade + progress). |
| `/indice` | `pages/IndiceCompatibilidade.jsx` | `ProtectedRoute` | Conteúdo explicativo do índice (página estática). |
| `/noticias` | `pages/Noticias.jsx` | `ProtectedRoute` | Feed de notícias (usa `FeedListaPage`). |
| `/pesquisas` | `pages/Pesquisas.jsx` | `ProtectedRoute` | Feed de pesquisas (usa `FeedListaPage`). |
| `/portais-estrategicos` | `pages/PortaisEstrategicos/PortaisEstrategicosPage.jsx` | `ProtectedRoute` | Portais Estratégicos (Fornecedores / Investimentos). |
| `/edital/:id` | `pages/EditalDetalhes.jsx` | `ProtectedRoute` | Detalhe do edital + anexos e lógica local de compatibilidade. |
| `/` | redirect | — | `Navigate` → `/dashboard`. |
| `*` | redirect | — | `Navigate` → `/login`. |

### ProtectedRoute / RBAC

`ProtectedRoute` (`src/router/ProtectedRoute.jsx`) faz:

- Bloqueia se `authenticated` for falso → manda para `/login`.
- Se `requiredPermission` existir, resolve permissões via `getPermissions(user.nivel || user.tipo)` e redireciona para `/dashboard` se não tiver.

Permissões RBAC (estáticas): `src/permissions.js` (ADMIN/CONSULTOR/FUNCIONARIO).

---

## 5) Conexão com backend/Supabase (env, cliente, views e fallbacks)

### Arquivo de ambiente (Vite)

Central: `frontend/EditalFinder-React/src/config/env.js`.

Variáveis **lidas** (nomes apenas; valores não expostos aqui):

- **Conexão**:
  - `VITE_SUPABASE_URL`
  - `VITE_SUPABASE_ANON_KEY` (ou fallback legado `VITE_SUPABASE_KEY`)
  - `VITE_APP_ENV`, `VITE_APP_NAME`
- **Views do backend** (contrato de consumo do frontend):
  - `VITE_VIEW_EDITAIS` (default `vw_editais_front`)
  - `VITE_VIEW_NOTICIAS` (default `vw_noticias_front`)
  - `VITE_VIEW_PESQUISAS` (default `vw_pesquisas_front`)
  - `VITE_VIEW_FORNECEDORES` (default `vw_fornecedores_front`)
  - `VITE_VIEW_INVESTIMENTOS` (default `vw_investimentos_front`)
- **Flags**:
  - `VITE_ENABLE_PORTAIS_ESTRATEGICOS`
  - `VITE_ENABLE_FORNECEDORES`
  - `VITE_ENABLE_INVESTIMENTOS`
  - `VITE_ENABLE_RADAR`
  - `VITE_ENABLE_DEBUG_PIPELINE`

Observação: existe também um uso direto no header de:

- `import.meta.env.VITE_ENABLE_INDICE === 'true'` (menu da rota `/indice`).

### Cliente Supabase

- Cliente: `src/services/supabaseClient.js`
- Cria `createClient(SUPABASE_URL, SUPABASE_ANON_KEY)` quando configurado.
- Quando **não** configurado, cria client “placeholder” (`https://offline.invalid`) para não quebrar imports, e emite aviso **sem secrets**.
- Exporta `isSupabaseConfigured` e `getSupabaseConfigHint()` (host sem query / sem chaves).

### Camada de dados

O frontend tem um serviço central monolítico:

- `src/services/dataService.js`

Características relevantes:

- **Preferência por views** (nomes vindos de `env.js`).
- **Fallbacks** quando view falha (por diferença de colunas/ordenação/RLS ou inexistência):
  - Editais: `VIEW_EDITAIS` → fallback para tabela `edital`.
  - Notícias: `VIEW_NOTICIAS` → fallback para tabela `noticia`.
  - Pesquisas: `VIEW_PESQUISAS` → fallback para tabela `pesquisa`.
- Para portais, busca via `VIEW_FORNECEDORES` e `VIEW_INVESTIMENTOS` usando ordenações com fallback (`criado_em`, `atualizado_em`, `id`, `id_edital`).
- **Paginação**: usa `.range(from, from + PAGE - 1)` em loops.
- **Logs em DEV**: `console.info`/`console.warn` controlados por `VITE_ENABLE_DEBUG_PIPELINE` e heurísticas (ex.: count 0 / erro).

### Serviços por domínio

Existem wrappers finos que chamam `dataService` (ex.: `src/services/editaisService.js`, `noticiasService.js`, `pesquisasService.js`, `portaisEstrategicosService.js`).

No estado atual, muitas páginas ainda importam `dataService` diretamente (Dashboard, feeds, cadastros, detalhe).

---

## 6) Páginas principais (estado atual + fontes de dados)

### 6.1) Editais (Dashboard)

Página: `src/pages/Dashboard.jsx`

- **Fonte de dados**: `dataService.getEditais()`
  - Preferência: `VITE_VIEW_EDITAIS` (default `vw_editais_front`)
  - Fallback: tabela `edital`
- **Filtros**:
  - Motor dedicado: `src/utils/edital/filtersEngine.js`
  - Busca global: `tokenizeSearchQuery` (`utils/edital/search.js`) + debounce (`useDebouncedValue`)
  - Facets/rollups: `rollupFacet`, `loosenSidebarForFacet`
  - Ordenação: `SORT_OPTIONS` / `sortEditais` (`utils/edital/scoring.js`)
- **UI**:
  - `Header` com busca (prop `onSearch`)
  - Sidebar de filtros: `components/dashboard/EditaisFiltersSidebar`
  - Cards: `components/dashboard/EditalCard`
  - Modal detalhe: `components/dashboard/EditalDetailsModal`
  - “Favoritos” em `localStorage` (`editais_favoritos_v1`)
- **Export**:
  - PDF (tabela paisagem) via `services/pdfExportService.js` (`exportLandscapeTablePdf`)
  - XLSX via `xlsx`
- **Observação técnica**:
  - A página implementa um painel de debug em dev (contagens de pipeline) e sugestões quando filtro zera resultados.

### 6.2) Radar de Fomento

Página: `src/pages/RadarFomento.jsx`

- **Fonte de dados**:
  - Clientes: `dataService.getClients()` (tabela `cliente`)
  - Editais: `dataService.getEditais()` (mesma origem do Dashboard)
- **Cálculo**:
  - Hook dedicado: `hooks/useRadarMatches.js`
    - Cache em memória (`Map`) com limite de entradas
    - Cancelamento por `AbortController`
    - Progresso granular (`processed`, `total`, `excludedPreScore`) + percent
  - Motor/serviço: `services/matchService.js` e `utils/radarMatch.js`
- **UI/UX atual** (inferível pelo código):
  - Seleção de cliente com ID estável (`clienteIdSelecionado`)
  - Favoritos por cliente persistidos em `localStorage` (`radar_favoritos`), com limpeza de órfãos quando o catálogo muda
  - Render progressivo dos cards (“visibleCap”) para não renderizar centenas de elementos de uma vez
  - Filtros locais: tipo de recurso, órgão, compatibilidade, favoritos e busca por texto
- **Pontos fortes atuais**:
  - “Loading/progresso” bem estruturado via hook e componente `RadarLoading`
  - Prevenções de crash com localStorage corrompido
- **Áreas naturalmente delicadas**:
  - O motor de score (heurísticas, stopwords, sinônimos, cortes) é extenso; mudanças pequenas podem afetar ranking e confiança do usuário.

### 6.3) Cadastros (Usuários / Clientes / Editais cadastrados)

Página: `src/pages/Cadastros.jsx`

- **Acesso**: protegido e com permissão `canViewCadastros`.
- **Abas**:
  - Usuários: `dataService.getUsers()` (tabela `usuario`)
  - Clientes: `dataService.getClients()` (tabela `cliente`)
  - Editais cadastrados: `dataService.getAllEditaisAdmin()` (tabela `edital`)
- **Tabela e forms**:
  - Tabela: `components/admin/AdminTable.jsx`
  - Forms: `UserForm`, `ClientForm`, `EditalForm`
  - Modal genérico: `components/ui/Modal.jsx`
- **Tela Clientes melhorada** (evidência via docs e código):
  - Cards/resumo e filtros (incluindo setor)
  - Badges de pré-cadastro por cliente, calculados **localmente** com base em rascunhos no navegador:
    - `utils/precadastroProjetoInitialState.js` (`loadPrecadEnvelope`, `buildInitialPrecadastroState`)
    - `utils/precadastro/calculatePreCadastroCompleteness.js`
- **Pré-cadastro**:
  - “Abrir pré-cadastro” abre um modal grande com `components/admin/ProjetoPrecadastroForm.jsx`
  - O contexto opcional é lido de `sessionStorage` (`precadastro_context_${id}`) para associar título/score quando vier do Radar (sem backend).

### 6.4) Pré-cadastro de projeto (modal + PDF)

Componente central: `components/admin/ProjetoPrecadastroForm.jsx`

- **Estado**:
  - `buildInitialPrecadastroState` + envelope local (`loadPrecadEnvelope`)
  - “Rascunho inteligente”: `utils/precadastro/buildPreCadastroDraft.js`
  - “Intel” de campos (manual vs sugerido): `markFieldManual`, `clearAutoSuggestions`
- **Estrutura de UI**:
  - Header do modal: `components/admin/precadastro/PrecadastroHeader.jsx`
  - Abas: `PrecadNavTabs`
  - Secções: `PrecadCompanyStrip`, `PrecadProductLines`, `PrecadProjectScope`, `PrecadFitSection`, `PrecadObservations`, `PrecadLegacyFormBody`, `PrecadPendenciasPanel`, etc.
  - Toolbar/assistente: `PrecadIntelToolbar`
- **PDF**:
  - Serviço: `services/precadastroProjetoPdf.js`
    - `exportPrecadastroProjetoPdf` (gera e salva)
    - `buildPrecadastroProjetoPdfBlob` (preview em nova aba)
  - Render: `services/precadastroPdf/*` com `jsPDF` (não é “print” da tela).
- **Referência estática**:
  - Há URL para PDF de referência: `BASE_URL + /docs/formulario-apresentacao-projeto-referencia.pdf` (pasta `public/docs` do frontend).
- **Estado “rollback parcial” do assistente**:
  - A doc `PRE_CADASTRO_ASSISTENTE_PARTIAL_ROLLBACK.md` descreve retorno ao layout antigo internamente, preservando header/modal/PDF.

### 6.5) Portais Estratégicos (MVP)

Página: `src/pages/PortaisEstrategicos/PortaisEstrategicosPage.jsx`

- **Rota**: `/portais-estrategicos` (protegida)
- **Abas**:
  - Fornecedores
  - Investimentos
- **Fonte de dados**:
  - `services/portaisEstrategicosService.js`
    - `fetchFornecedoresFront()` → `dataService.getPortaisFornecedoresFront()` → `VITE_VIEW_FORNECEDORES` (default `vw_fornecedores_front`)
    - `fetchInvestimentosFront()` → `dataService.getPortaisInvestimentosFront()` → `VITE_VIEW_INVESTIMENTOS` (default `vw_investimentos_front`)
- **Componentes**:
  - `components/cards/PortalEstrategicoCard.jsx`
  - `components/filters/PortalEstrategicoFilters.jsx`
  - Estados: `components/states/LoadingState`, `ErrorState`, `EmptyState`
- **Filtros**:
  - Validação (`validacao_status`) / incluir suspeitos
  - Fonte (fonte_recurso ou fonte)
  - Tipo do portal (display via utils)
  - Qualidade (`qualidade_dado`)
  - Acesso (público vs limitado/login)
  - Setor estratégico (array ou string)
  - Busca full-text local (concatena campos + labels humanizados)
- **Ordenação**:
  - recentes, fonte, tipo, qualidade, “acesso público primeiro”
- **Contrato de produto aplicado no UI**:
  - Linguagem e filtros específicos para “portais” (não trata como edital).
  - EmptyState sugere checar views e RLS anon.

### 6.6) Notícias

Página: `src/pages/Noticias.jsx` (wrapper)

- Renderiza `FeedListaPage` com `loadItems={() => dataService.getNoticias()}`
- **Origem**:
  - Preferência: `VITE_VIEW_NOTICIAS` (default `vw_noticias_front`)
  - Fallback: tabela `noticia`

### 6.7) Pesquisas

Página: `src/pages/Pesquisas.jsx` (wrapper)

- Renderiza `FeedListaPage` com `loadItems={() => dataService.getPesquisas()}`
- **Origem**:
  - Preferência: `VITE_VIEW_PESQUISAS` (default `vw_pesquisas_front`)
  - Fallback: tabela `pesquisa`

---

## 7) Componentes reutilizáveis (inventário prático)

### Layout / navegação

- `src/components/layout/Header.jsx`
  - Menu: Editais, Cadastros (RBAC), Radar, Índice (flag), Notícias, Pesquisas, Portais.
  - Configurações: abre modal com `SettingsForm` quando `canManageUsers`.
  - Search input opcional quando a página passa `onSearch`.

### Modal / UI base

- `src/components/ui/Modal.jsx`
  - Fecha ao clicar no overlay, tecla `Escape`, controla `body.style.overflow`.

### States (carregando / erro / vazio)

- `src/components/states/LoadingState.jsx`
- `src/components/states/ErrorState.jsx`
- `src/components/states/EmptyState.jsx`

### Badges

- `src/components/badges/StatusBadge.jsx` (usado em algumas telas e no MVP de portais conforme doc)

### Dashboard/Editais

- `src/components/dashboard/EditalCard.jsx`
- `src/components/dashboard/EditaisFiltersSidebar.jsx`
- `src/components/dashboard/EditaisStatsBar.jsx`
- `src/components/dashboard/ActiveFiltersChips.jsx`
- `src/components/dashboard/EditalDetailsModal.jsx`

### Radar

- `src/components/radar/ListaClientes.jsx`
- `src/components/radar/CardEditalRadar.jsx`
- `src/components/radar/RadarLoading.jsx`

### Feed (Notícias/Pesquisas)

- `src/components/feed/FeedItemCard.jsx`
- `src/components/feed/FeedSidebarFilters.jsx`

### Admin/Cadastros + Pré-cadastro

CRUD:

- `src/components/admin/AdminTable.jsx`
- `src/components/admin/UserForm.jsx`
- `src/components/admin/ClientForm.jsx`
- `src/components/admin/EditalForm.jsx`
- `src/components/admin/SettingsForm.jsx`

Pré-cadastro (módulo delicado, muitas dependências):

- `src/components/admin/ProjetoPrecadastroForm.jsx` (shell)
- `src/components/admin/precadastro/*` (header, abas, seções, pendências, etc.)

Portais:

- `src/components/cards/PortalEstrategicoCard.jsx`
- `src/components/filters/PortalEstrategicoFilters.jsx`

---

## 8) Estado atual — Cadastros / Pré-cadastro (síntese)

### Cadastros/Clientes (melhorias UX)

Evidências:

- Código em `src/pages/Cadastros.jsx` com cards/resumo, badges de pré-projeto e filtros.
- Documentação:
  - `frontend/EditalFinder-React/docs/CADASTROS_CLIENTES_UX_AUDIT.md`
  - `frontend/EditalFinder-React/docs/CADASTROS_CLIENTES_UX_IMPROVEMENTS.md`

Pontos centrais:

- Badges de “Pré-projeto” dependem de rascunhos locais (localStorage) e do campo `bloco_estr_status_precadastro` no envelope.
- Existe risco de performance se a lista de clientes crescer muito (cálculo local por cliente).

### Pré-cadastro (assistente rollback parcial, PDF preservado)

Evidência:

- `frontend/EditalFinder-React/docs/PRE_CADASTRO_ASSISTENTE_PARTIAL_ROLLBACK.md`
- `frontend/docs/PRE_CADASTRO_PROJETO_UX_AUDIT.md`

Pontos centrais:

- O assistente “Fase 2” foi parcialmente revertido para um formato mais compacto.
- Header/modal/PDF e ações de export/preview foram preservados.
- PDF é gerado por `jsPDF` com modelo estruturado → alterações nessa área são de alto risco de regressão visual.

---

## 9) Estado atual — Radar (síntese)

Pontos fortes detectados no código:

- Cálculo assíncrono em lotes, progresso e cache (`useRadarMatches`).
- Render progressivo para evitar gargalos de UI em listas grandes.
- Heurísticas extensas de normalização textual/sinônimos/stopwords no motor (`matchService` + `radarMatch`).

Pontos delicados:

- Ajustes em stopwords/sinônimos/pesos/cortes podem mudar bastante o ranking.
- A UI depende de múltiplos estados (loading do fetch, loading do cálculo, filtros locais, favoritos persistidos).

---

## 10) Estado atual — Portais Estratégicos (síntese)

Implementação atual existe e está conectada às views configuráveis por env:

- Página: `src/pages/PortaisEstrategicos/PortaisEstrategicosPage.jsx`
- Services: `portaisEstrategicosService` → `dataService.getPortaisFornecedoresFront()` / `getPortaisInvestimentosFront()`
- Views:
  - `VITE_VIEW_FORNECEDORES` (default `vw_fornecedores_front`)
  - `VITE_VIEW_INVESTIMENTOS` (default `vw_investimentos_front`)

Há uma doc específica do MVP:

- `frontend/docs/PORTAIS_ESTRATEGICOS_FRONTEND_MVP.md`

---

## 11) Documentação existente (presença + resumo curto)

### Solicitada (lista do pedido)

- **`docs/FRONTEND_STRUCTURE_AUDIT.md`**: **ausente** em `docs/` da raiz do repo, mas existe em `frontend/docs/FRONTEND_STRUCTURE_AUDIT.md` (auditoria de estrutura; contém uma proposta de reorg e observações históricas).
- **`docs/FRONTEND_REORGANIZATION_PHASE1.md`**: **ausente** em `docs/`, mas existe em `frontend/docs/FRONTEND_REORGANIZATION_PHASE1.md` (centralização `env.js`, wrappers services, states components, tipos JSDoc).
- **`docs/PORTAIS_ESTRATEGICOS_FRONTEND_MVP.md`**: **ausente** em `docs/`, mas existe em `frontend/docs/PORTAIS_ESTRATEGICOS_FRONTEND_MVP.md`.
- **`docs/CADASTROS_CLIENTES_UX_AUDIT.md`**: **ausente** em `docs/`, mas existe em `frontend/EditalFinder-React/docs/CADASTROS_CLIENTES_UX_AUDIT.md`.
- **`docs/CADASTROS_CLIENTES_UX_IMPROVEMENTS.md`**: **ausente** em `docs/`, mas existe em `frontend/EditalFinder-React/docs/CADASTROS_CLIENTES_UX_IMPROVEMENTS.md`.
- **`docs/PRE_CADASTRO_PROJETO_UX_FIX.md`**: **ausente** no workspace sob `docs/`; existe `frontend/docs/PRE_CADASTRO_PROJETO_UX_FIX.md` (não lido nesta síntese por limitação de escopo, mas está presente).
- **`docs/PRE_CADASTRO_ASSISTENTE_AUDIT.md`**: **ausente** em `docs/`, mas existe em `frontend/EditalFinder-React/docs/PRE_CADASTRO_ASSISTENTE_AUDIT.md` (presente).
- **`docs/PRE_CADASTRO_ASSISTENTE_IMPROVEMENTS.md`**: **ausente** em `docs/`, mas existe em `frontend/EditalFinder-React/docs/PRE_CADASTRO_ASSISTENTE_IMPROVEMENTS.md` (presente).
- **`docs/CADASTROS_PRE_CADASTRO_FINAL_STATUS.md`**: **não encontrado**.
- **`docs/FRONTEND_BACKEND_CONTEXT.md`**: **presente** em `docs/FRONTEND_BACKEND_CONTEXT.md` (raiz do repo; contrato de produto e views/tabelas).

### Nota de consistência (docs vs código)

Alguns documentos em `frontend/docs/*` descrevem estados “de fase” e podem ficar desatualizados em relação ao código atual.
Para orientar próximos passos, o código-fonte (router/header/services) deve ser tratado como fonte primária.

---

## 12) Riscos (áreas delicadas e cuidados)

- **Pré-cadastro / PDF (alto risco)**
  - Muitas peças (modelo, render, theme, autosave/draft, preview).
  - Qualquer ajuste visual pode causar sobreposição/quebra de paginação.
  - Recomendação: isolar mudanças e validar com casos reais + regressão manual.

- **Radar / compatibilidade (alto risco)**
  - Mudanças pequenas no motor (sinônimos, stopwords, pesos) alteram ranking.
  - Recomendação: criar “dataset de regressão” (clientes + editais) e comparar outputs antes/depois.

- **`dataService.js` monolítico (médio/alto risco)**
  - Qualquer alteração pode impactar múltiplas páginas.
  - Há fallbacks e ordenações alternativas por cluster; refactors devem preservar esse comportamento.

- **Env / basename / basepath (médio risco)**
  - `vite.config.js base` e `BrowserRouter basename` precisam continuar alinhados.
  - Recomendação: sempre testar navegação direta (refresh) em rotas internas no ambiente de deploy.

- **Header/menu + permissões (médio risco)**
  - Itens condicionais por RBAC e flag (`VITE_ENABLE_INDICE`).
  - Recomendação: validar comportamento por perfil (ADMIN/CONSULTOR/FUNCIONARIO).

- **Portais Estratégicos (médio risco)**
  - Depende de views específicas (`vw_fornecedores_front`, `vw_investimentos_front`) e RLS anon.
  - Recomendação: garantir que as views existam e tenham colunas usadas pelo UI (ex.: `ativo`, `validacao_status`, `qualidade_dado`, `setor_estrategico`, `requer_login`).

- **Feeds (Notícias/Pesquisas) (médio risco)**
  - `FeedListaPage` assume um conjunto de campos que pode variar entre `vw_noticias_front` e `vw_pesquisas_front`.
  - Recomendação: manter coerência de colunas nas views (ou mapear no frontend) para evitar “undefined” em export/filtros.

---

## 13) Próximos passos recomendados (sem alterar nada agora)

1. **Congelar contrato de dados do frontend** (documentar oficialmente quais colunas o frontend usa de cada view).
2. **Revalidar `VITE_VIEW_*` no ambiente alvo** (staging/prod) e confirmar RLS anon em views consumidas.
3. **Criar um “manual QA” curto** por página (Dashboard/Radar/Cadastros/Pré-cadastro/PDF/Portais/Feeds).
4. **Adicionar testes mínimos de regressão**:
   - Unit test do motor do Radar (já existe `src/utils/radarMatch.test.js`).
   - (Futuro) E2E para rotas críticas: login → dashboard → cadastros → abrir pré-cadastro → preview PDF.
5. **Reduzir risco de refactor futuro**:
   - Migrar páginas para importar wrappers (`editaisService`, `noticiasService`, etc.) antes de dividir o `dataService`.
6. **Padronizar estados de loading/erro/vazio**:
   - Há componentes `components/states/*`, mas nem todas as páginas usam (ganho rápido e baixo risco).
7. **Padronização de logs**:
   - Confirmar que logs em produção não são verbosos; manter apenas logs DEV (já é a tendência do código).

---

## Apêndice A — Relação “página → fonte de dados”

- **Editais (`/dashboard`)**: `VITE_VIEW_EDITAIS` (default `vw_editais_front`) → fallback `edital`
- **Radar (`/radar-fomento`)**: `cliente` + mesma origem de editais do dashboard
- **Cadastros (`/cadastros`)**: `usuario`, `cliente`, `edital` (admin), `organizacao` (quando usado)
- **Notícias (`/noticias`)**: `VITE_VIEW_NOTICIAS` (default `vw_noticias_front`) → fallback `noticia`
- **Pesquisas (`/pesquisas`)**: `VITE_VIEW_PESQUISAS` (default `vw_pesquisas_front`) → fallback `pesquisa`
- **Portais (`/portais-estrategicos`)**:
  - Fornecedores: `VITE_VIEW_FORNECEDORES` (default `vw_fornecedores_front`)
  - Investimentos: `VITE_VIEW_INVESTIMENTOS` (default `vw_investimentos_front`)
- **Detalhe edital (`/edital/:id`)**: tabela `edital` + `edital_anexo`

