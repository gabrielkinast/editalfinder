# Workspace do Consultor — Plano de produto e arquitetura

**Status:** Fases **2a**, **2b**, **migração de fluxo** e **seleção múltipla de oportunidades → pré-projeto** implementadas no frontend. Cadastros reorientado para admin. Favoritos/relatório no painel — pendentes.

**Data:** 2026-05-18 (fluxo consultor no Workspace)

**Documentação pré-projeto:** `docs/PRE_PROJETO_CONSULTOR_IMPROVEMENTS.md`

---

## 1. Objetivo de produto

Criar uma área **Workspace do Consultor** no EditalFinder para consultores que atendem vários clientes e precisam transformar editais/oportunidades em **propostas acionáveis**, não apenas descobrir editais.

O workspace deve centralizar, por cliente:

- organização e priorização de oportunidades;
- explicabilidade (“por que combina?”);
- pré-projetos e relatórios para o cliente;
- favoritos e prazos;
- próximas ações e checklist de submissão.

**Princípio:** reaproveitar ao máximo o que já existe (Radar, Cadastros, favoritos, pré-cadastro em `localStorage`) antes de novas tabelas ou telas monolíticas desconectadas.

---

## 2. Público-alvo

| Perfil | Necessidade |
|--------|-------------|
| **Consultor** (`CONSULTOR` em `permissions.js`) | Carteira de clientes próprios (`cliente.id_usuario`), priorizar oportunidades, preparar material para reunião com cliente |
| **Administrador** | Visão de todos os clientes; mesmo fluxo de workspace |
| **Funcionário** | Hoje tem `canViewCadastros` mas não `canCreate`/`canEdit`; workspace deve respeitar o mesmo isolamento (só leitura onde aplicável) |

---

## 3. Dores do consultor (problema)

1. **Contexto fragmentado** — Radar, Cadastros, Editais e favoritos vivem em rotas separadas; trocar de cliente exige repetir navegação e filtros.
2. **Favoritos ambíguos** — favoritos remotos são **por usuário** (`edital_favorito.id_usuario`); no Radar ainda existe **localStorage por cliente** (`radar_favoritos`) quando remoto está off ou em paralelo.
3. **Pré-projeto no Workspace** — modal `ProjetoPrecadastroForm`; top **20** no painel; seleção de **1 a 20** → **Gerar pré-projeto com selecionadas** (`openPreProjetoFromOpportunities`); fluxo de uma oportunidade preservado via wrapper `openPreProjetoFromOpportunity`; rascunhos `precadastro_draft_*` inalterados. Cadastros: consultor redirecionado; admin mantém aba Clientes legada.
4. **Relatório para cliente** — export PDF existe para **lista de editais** (Dashboard) e para **pré-cadastro** (`precadastroProjetoPdf.js`); não há relatório executivo “oportunidade + aderência + próximos passos” no workspace.
5. **Checklist de submissão** — campos existem no formulário de pré-cadastro (`bloco_estr_pendencias_checklist`, `bloco_estr_docs_recomendados`); falta painel dedicado no fluxo do consultor.

---

## 4. Mapeamento do que já existe

### 4.1 Rotas atuais (`src/router/index.jsx`)

| Rota | Página | Relação com workspace |
|------|--------|------------------------|
| `/dashboard` | `Dashboard.jsx` | Editais + favoritos usuário + export PDF/Excel |
| `/cadastros` | `Cadastros.jsx` | Clientes, usuários, editais admin; **hub pré-projeto** |
| `/radar-fomento` | `RadarFomento.jsx` | Match cliente × catálogo; favoritos Radar |
| `/edital/:id` | `EditalDetalhes.jsx` | Detalhe de oportunidade |
| `/indice` | `IndiceCompatibilidade.jsx` | Legenda do motor (flag `VITE_ENABLE_INDICE`) |

**Proposta de rota nova (fase 2):** `/workspace-consultor`  
*(alternativa aceitável: `/consultor-workspace`; recomenda-se a primeira por alinhar ao label em português e ao padrão `radar-fomento`.)*

**Feature flag:** `VITE_ENABLE_CONSULTOR_WORKSPACE=true` (menu + rota; default `false`).

**Basename:** app em `/editalfinder` → URL completa exemplo: `/editalfinder/workspace-consultor`.

---

### 4.2 Frontend — módulos reaproveitáveis

#### Clientes

| Artefato | Caminho | Função |
|----------|---------|--------|
| Listagem / CRUD | `pages/Cadastros.jsx`, `components/admin/ClientForm.jsx` | CRUD com RLS via `dataService` |
| Serviço | `services/dataService.js` → `getClients`, `createClient`, `updateClient` | `supabase.from('cliente').select('*')` |
| Normalização | `utils/normalizeCliente.js` | Unifica `id_cliente`, `nome_empresa`, etc. |
| Permissões | `utils/permissions.js`, `permissions.js` | `filterClientsForUser`, `canViewClient`, papel `CONSULTOR` |
| Lista UI (Radar) | `components/radar/ListaClientes.jsx` | Tags porte/setor, badge de favoritos locais |

**Perfil consultivo (2026-05):** `ClientForm` em abas + `extras.perfil_consultivo` — ver `docs/CLIENTE_PROFILE_CONSULTIVO.md` e SQL opcional `docs/sql/ALTER_CLIENTE_ADD_PERFIL_CONSULTIVO.sql`.

**Campos usados no cadastro (form + pré-cadastro):**  
Colunas: `nome_empresa`, `razao_social`, `cnpj`, `setor`, `porte_empresa`, `status`, `interesse_temas`, `interesse_valor_min`, `interesse_valor_max`, `cidade`, `estado`, `regiao`, `data_abertura`, `cnae_principal`, `descricao_projeto`, `area_inovacao`, `faturamento_anual`, `numero_funcionarios`; em `extras.perfil_consultivo`: contato, dados econômicos estendidos, preferências de fomento, documentação, diagnóstico do consultor. Tema PDF: `cor_primaria`, `cor_secundaria`, `logo_url` quando existirem.

#### Radar de Fomento

| Artefato | Caminho | Função |
|----------|---------|--------|
| Página | `pages/RadarFomento.jsx` | Orquestra clientes + editais + filtros + favoritos |
| Hook | `hooks/useRadarMatches.js` | Cache memória/sessão, worker, **não alterar score** |
| Motor | `utils/radarMatch.js`, `utils/radar/radarMatchCore.js` | Cálculo de compatibilidade |
| Explicabilidade | `utils/radar/radarMatchExplain.js` | Textos “por que combina” (apresentação) |
| Cards | `components/radar/CardEditalRadar.jsx`, `RadarResultsGrid.jsx` | Score, razões, favoritar |
| Serviço | `services/matchService.js` | `recomendarEditaisAsync`, critérios |
| Performance | `utils/radar/radarPersistentCache.js`, worker | Ver `docs/RADAR_PERFORMANCE_DIAGNOSTIC.md` |

**Integração workspace → Radar (proposta):**  
`/radar-fomento?cliente=<id_cliente>` com leitura de query no mount de `RadarFomento` (hoje **não implementado**).

#### Favoritos

| Camada | Caminho | Escopo |
|--------|---------|--------|
| Remoto (Supabase) | `services/favoritosService.js`, `hooks/useEditalFavorites.js` | **`id_usuario`** — tabela `edital_favorito`, view `vw_editais_favoritos_front` |
| Dashboard | `pages/Dashboard.jsx` | Filtro “somente favoritos”, banner de prazo |
| Radar local | `RadarFomento.jsx` | `localStorage` chave `radar_favoritos`: `{ [clienteId]: [editalId, ...] }` |
| Alertas prazo | `utils/deadlineAlerts.js` | `status_prazo`, resumo para banner |

**Limitação documentada (MVP):** favoritos persistentes no banco são do **consultor logado**, não do **cliente**. No workspace, exibir:

- favoritos **remotos** do usuário (interseção manual com oportunidades do cliente no Radar, ou filtro por título/id);
- favoritos **Radar por cliente** (`radar_favoritos`) quando remoto desligado ou como complemento.

**Futuro (schema):** `id_cliente` opcional em `edital_favorito` ou tabela `cliente_edital_favorito`.

#### Pré-projeto / pré-cadastro

| Artefato | Caminho | Função |
|----------|---------|--------|
| Form principal | `components/admin/ProjetoPrecadastroForm.jsx` | Modal em Cadastros; props `cliente`, `editalAssociado`, `radarMatch` |
| Estado / persistência | `utils/precadastroProjetoInitialState.js` | `localStorage`: `precadastro_draft_{id}_{fingerprint}` |
| Rascunho inteligente | `utils/precadastro/buildPreCadastroDraft.js` | Preenche blocos a partir de cliente + edital + radar |
| Completude | `utils/precadastro/calculatePreCadastroCompleteness.js` | Score e pendências guiadas |
| PDF | `services/precadastroProjetoPdf.js` | Export PDF do pré-cadastro (não é relatório “cliente executivo” genérico) |
| Subcomponentes | `components/admin/precadastro/*` | Header, tabs, escopo, aderência, pendências |
| Contexto Radar | `sessionStorage` `precadastro_context_{id_cliente}` | JSON `{ titulo, scorePct }` — **só lido** em Cadastros; **Radar não grava** hoje |

**Integração proposta “Gerar pré-projeto”:**

1. Workspace passa `cliente`, `edital` (row ou id), objeto `radarMatch` (hit do `useRadarMatches`).
2. `buildPreCadastroDraft({ cliente, edital, radarMatch })` + `savePrecadEnvelope` (funções já em `precadastroProjetoInitialState.js`).
3. Abrir modal reutilizando `ProjetoPrecadastroForm` **ou** navegar para `/cadastros` com estado (mais invasivo).

Campos já mapeados para aderência/riscos/documentos/cronograma (blocos `bloco_estr_*`, `bloco1_*`, `bloco2_*`) — ver `precadastroEmptyState()` em `precadastroProjetoInitialState.js`.

#### Relatório / export

| Tipo | Onde | Conteúdo |
|------|------|----------|
| PDF tabela editais | `services/pdfExportService.js` + `Dashboard.jsx` | Lista filtrada/favoritos — **não** por cliente |
| PDF pré-cadastro | `precadastroProjetoPdf.js` | Documento longo de pré-projeto |
| Excel editais | `Dashboard.jsx` (XLSX) | Exportação em massa |

**MVP relatório workspace:** componente **somente leitura em tela** (`ConsultorClientReport.jsx` futuro) montado com:

- dados do cliente;
- top N hits do Radar (`score`, `compatibilidade`, `razoesPositivas`, `radarAlertas` de `CardEditalRadar`);
- `buildRadarMatchExplain` / campos do hit;
- prazo (`deadlineAlerts`);
- próximos passos de `bloco_estr_proximos_passos` se existir rascunho local.

Export PDF/DOCX do relatório → **fase 3**.

#### Diagnóstico / aderência / proposta

| Conceito | Implementação atual |
|----------|---------------------|
| Aderência | Score % + label Alta/Média/Baixa no Radar; `bloco_estr_aderencia_nivel` no pré-cadastro |
| Diagnóstico edital | `utils/edital/editalVisibility.js`, `linkHealth.js` (aba Editais) |
| Proposta | Não há entidade “proposta” no banco; pré-cadastro é o substituto funcional |
| Índice | `/indice` — documentação estática do motor |

---

### 4.3 Backend / dados (sem schema novo nesta fase)

| Tabela / view | Uso no workspace |
|---------------|------------------|
| `public.cliente` | Lista de clientes; RLS por `id_usuario` |
| `public.vw_editais_front` | Catálogo Radar (via `dataService.getEditais`) |
| `public.edital_favorito` | Favoritos do usuário logado |
| `public.vw_editais_favoritos_front` | Leitura favoritos |
| `public.usuario` | Auth + `id_usuario` para favoritos |

**Não existe hoje:** tabela de proposta, pipeline de consultor, checklist persistido, favorito por cliente.

**Proposta futura (somente documentada):** `docs/sql/RADAR_CLIENTE_CACHE.sql` — cache de scores; opcional para workspace mas **não obrigatório** no MVP.

**Pré-cadastro:** persistência **100% browser** (`localStorage` + `sessionStorage`); não há `projeto_precadastro` no Supabase no código atual.

---

## 5. Layout inicial proposto (fase 2 — UI)

```
┌─────────────────────────────────────────────────────────────────┐
│ Workspace do Consultor                                          │
│ Transforme oportunidades em propostas acionáveis...             │
├──────────────────┬──────────────────────────────────────────────┤
│ ConsultorClient  │ ConsultorClientOverview (cliente selecionado) │
│ List             │  ┌─────────────┐ ┌─────────────┐ ┌──────────┐ │
│  - busca         │  │ Radar top 5 │ │ Favoritos   │ │ Prazos   │ │
│  - tags          │  └─────────────┘ └─────────────┘ └──────────┘ │
│  - Abrir WS      │  ┌─────────────────────────────────────────┐ │
│                  │  │ ConsultorOpportunityPipeline (lista)    │ │
│                  │  └─────────────────────────────────────────┘ │
│                  │  ConsultorQuickActions (barra fixa)           │
└──────────────────┴──────────────────────────────────────────────┘
```

### Blocos

**A) Cabeçalho** — título + subtítulo fixos.

**B) Coluna clientes** — reutilizar padrão `ListaClientes` (estilos `radar-cliente-*`) ou variante `ConsultorClientList` com busca e botão “Abrir workspace” (= selecionar cliente).

**C) Painel cliente** — cards:

| Card | Fonte MVP |
|------|-----------|
| Oportunidades recomendadas | `useRadarMatches` — top 5–10 por score, mesmas regras de exibição do Radar |
| Favoritos | `useEditalFavorites` + opcional contagem `radar_favoritos[clienteId]` |
| Pré-projetos | `loadPrecadEnvelope` / badges como em `Cadastros.jsx` (`clientPrecadById`) |
| Alertas de prazo | `deadlineAlerts` sobre hits + favoritos com prazo |
| Próximas ações | Heurística: pendências de `getPendenciasGuiadas` + “ir ao Radar” / “completar pré-projeto” |

**D) Ações rápidas** (`ConsultorQuickActions`)

| Ação | Comportamento MVP |
|------|-------------------|
| Gerar pré-projeto | Modal `ProjetoPrecadastroForm` + `buildPreCadastroDraft` |
| Gerar relatório | Painel/modal relatório em tela |
| Ver Radar deste cliente | `navigate('/radar-fomento?cliente=' + id)` (após implementar query) |
| Ver favoritos | Filtro local ou link Dashboard com query futura |
| Criar checklist | Editar/visualizar `bloco_estr_pendencias_checklist` via pré-cadastro ou mini-modal |

---

## 6. Componentes sugeridos (estrutura de pastas)

```
frontend/EditalFinder-React/src/
  pages/
    ConsultorWorkspace.jsx          # shell da página, feature flag
  components/consultor/
    ConsultorWorkspaceHeader.jsx
    ConsultorClientList.jsx
    ConsultorClientOverview.jsx
    ConsultorOpportunityPipeline.jsx
    ConsultorQuickActions.jsx
    ConsultorDeadlineAlerts.jsx
    ConsultorPreProjectPanel.jsx
    ConsultorClientReport.jsx       # relatório MVP em tela (fase 2b)
```

**Hooks sugeridos (fino, sem duplicar Radar):**

- `useConsultorWorkspace.js` — cliente selecionado, carrega clientes + dispara `useRadarMatches` para o cliente ativo;
- reexportar `useEditalFavorites` sem mudança.

---

## 7. Integrações detalhadas

### 7.1 Radar

- **Reuso:** `useRadarMatches(cliente, editais, options)` com mesmas opções default que `RadarFomento` (não mudar `radarMatch.js`).
- **Explicabilidade:** importar funções de `radarMatchExplain.js` para painel “Por que combina?” (mesmo texto dos cards).
- **Deep link:** adicionar em `RadarFomento.jsx` leitura de `useSearchParams().get('cliente')` → `setClienteIdSelecionado` (mudança mínima, isolada).
- **Performance:** um cliente ativo por vez no workspace; cache do hook beneficia re-seleção.

### 7.2 Favoritos

- Painel lista favoritos remotos cujo `id_edital` apareça no top Radar do cliente **ou** título/link match (`favoritoRowMatchesEdital`).
- Documentar badge “favorito Radar (local)” separado do “favorito conta”.
- Não migrar dados nesta fase.

### 7.3 Pré-projeto

Fluxo alvo:

```
Oportunidade no pipeline → ConsultorQuickActions "Gerar pré-projeto"
  → buildPreCadastroDraft({ cliente, edital, radarMatch })
  → savePrecadEnvelope (localStorage)
  → ProjetoPrecadastroForm em Modal
```

Preenchimento automático já cobre: resumo, aderências Radar (`bloco_estr_principais_aderencias`), lacunas/alertas (`bloco_estr_lacunas`), referência edital, linhas de crédito sugeridas (`projectIntel.js`).

### 7.4 Relatório para cliente (MVP)

Seções em tela:

1. Identificação cliente  
2. Oportunidade (título, fonte, prazo, valor)  
3. Score / aderência / compatibilidade  
4. Por que vale a pena (razões positivas Radar)  
5. Riscos / alertas (`radarAlertas`, penalidades)  
6. Próximos passos (template + campo pré-cadastro se houver)  
7. Documentos necessários (`bloco_estr_docs_recomendados` ou elegibilidade do edital)

---

## 8. Funcionalidades MVP vs futuras

### MVP (fase 2 — sem schema novo)

- [ ] Rota `/workspace-consultor` + flag + item de menu  
- [ ] Lista de clientes (ativos) com tags  
- [ ] Painel por cliente: top oportunidades Radar, status pré-cadastro local, alertas de prazo  
- [ ] Ações: abrir Radar com cliente, abrir pré-projeto modal, relatório em tela  
- [ ] Favoritos: visão híbrida usuário + local Radar (com legenda de limitação)  
- [ ] Deep link Radar `?cliente=`

### Fase 3

- Relatório export PDF (reuso tema `getClientTheme` / jsPDF)  
- Checklist de submissão dedicado (sem passar pelo form completo)  
- Favoritos por `id_cliente` (migration + RLS)  
- Persistência pré-cadastro no Supabase (opcional)

### Fase 4

- Pipeline kanban (oportunidade → pré-projeto → submissão)  
- Notas por cliente/oportunidade  
- Integração alertas e-mail  
- Cache servidor `radar_cliente_resultado`

---

## 9. Dependências técnicas

| Dependência | Estado |
|-------------|--------|
| Supabase + RLS `cliente` | Existente |
| `VITE_ENABLE_RADAR` | Deve permanecer `true` |
| `VITE_ENABLE_EDITAL_FAVORITOS` | Recomendado para favoritos remotos |
| `canViewCadastros` | Workspace deve exigir mesma permissão que Cadastros (consultor vê clientes) |
| Worker Radar | Opcional; workspace herda comportamento do hook |
| Não alterar | `radarMatch.js` (score), Notícias, Pesquisas, Concursos, Portais |

**Novas env (proposta):**

```env
VITE_ENABLE_CONSULTOR_WORKSPACE=false
```

Registrar em `.env.example` na fase de implementação.

---

## 10. Riscos

| Risco | Mitigação |
|-------|-----------|
| Duplicar lógica do Radar | Um único `useRadarMatches` por página; não fork do motor |
| Performance (2× carga editais) | Compartilhar cache global ou carregar editais uma vez no workspace |
| Favoritos “errados” para o cliente | UX clara: “favoritos da sua conta”; filtrar por match com oportunidades do cliente |
| Pré-cadastro só local | Badge “rascunho neste navegador”; não prometer sync entre dispositivos |
| Regressão no Radar | Deep link e flag isolados; testes manuais de seleção de cliente |
| Escopo creep | Não implementar kanban/checklist DB na fase 2 |

---

## 11. Fases de implementação

| Fase | Entrega | Esforço relativo |
|------|---------|------------------|
| **1 (esta rodada)** | `CONSULTOR_WORKSPACE_PLAN.md` + atualização `FRONTEND_BACKEND_CONTEXT.md` | Concluído |
| **2a** | Rota, flag, menu, shell + `ConsultorClienteList` + seleção cliente | **Concluído** |
| **2b** | `useConsultorWorkspace` + overview + pipeline (read-only Radar) | **Concluído** |

### Fase 2b — entregue (frontend)

| Item | Implementação |
|------|----------------|
| Hook | `hooks/useConsultorWorkspace.js` — `getEditais` + `useRadarMatches` (sem duplicar score) |
| Pipeline | `components/consultor/ConsultorOpportunityPipeline.jsx` — top 20 compacto (scroll) |
| Painel | `ConsultorRecommendedSection.jsx` — totais, estados, resumo de prazos |
| Deep link Radar | `RadarFomento.jsx` lê `?cliente=<id>` (só quando o param muda) |
| Prazos | `utils/consultorDeadlineSummary.js` — vence ≤7d, sem prazo, confortável |
| Logs DEV | `radar_load_*`, `top_matches_ready`, `open_radar_cliente` |

### Fase 2a — entregue (frontend)

| Item | Implementação |
|------|----------------|
| Flag | `VITE_ENABLE_CONSULTOR_WORKSPACE` (default `false`) em `config/env.js` e `.env.example` |
| Rota | `/workspace-consultor` — só registada se flag `true` (`router/index.jsx`) |
| Menu | **Workspace** — visível com flag + `canViewCadastros` (`Header.jsx`) |
| Página | `pages/ConsultorWorkspace.jsx` |
| Lista | `components/consultor/ConsultorClienteList.jsx` — `dataService.getClients`, `filterClientsForUser`, tags porte/setor/estado/interesses |
| Painel | Empty state + 4 cards placeholder + ações rápidas (Radar ativo; pré-projeto/relatório “Em breve”) |
| Logs DEV | `utils/consultorWorkspaceLog.js` — prefixo `[consultor-workspace]` |
| Radar link | `navigate('/radar-fomento?cliente=<id>')` (query ainda opcional no Radar) |
| **2c** | Quick actions: pré-projeto modal, relatório tela, link Radar | M |
| **2d** | Seleção múltipla (1–20) + pré-projeto multi | **Concluído** |
| **3** | PDF relatório, checklist UI, favoritos por cliente (schema) | G |

### Fase 2d — seleção múltipla e pré-projeto consultivo (multi)

| Item | Implementação |
|------|----------------|
| UI seleção | `ConsultorOpportunityPipeline.jsx` — checkbox por linha; `stopPropagation` nos controles |
| Barra de ações | `ConsultorRecommendedSection.jsx` — contagem, **Gerar pré-projeto com selecionados**, **Limpar seleção** |
| Estado | `ConsultorWorkspace.jsx` — `Map` de linhas Radar por chave estável |
| Chave | `getOpportunitySelectionKey` — `id_edital` → `link` → `hash:título\|fonte` |
| Visão rápida | Top **20** no painel (`CONSULTOR_WORKSPACE_TOP_OPPORTUNITIES`) |
| Lista completa | Modal `ConsultorAllOpportunitiesModal` — todos os `allMatches` do hook; filtros client-side; “Mostrar mais” +30 |
| Exibição incremental | `CONSULTOR_ALL_OPPORTUNITIES_INITIAL_CAP` / `_INCREMENT` = 30 |
| Limite seleção | `MAX_PREPROJECT_OPPORTUNITIES = 20` (estado `selectedOpportunityRows` compartilhado painel ↔ modal) |
| Principal | Maior `scorePct` / compatibilidade; uma selecionada = principal única |
| Corpo pré-projeto | Até 5 **complementares** detalhadas; restantes **em observação** (resumo compacto no PDF) |
| Orquestração | `openPreProjetoFromOpportunities.js` — valida cliente + lista; `buildPreCadastroDraft` com `oportunidadesSelecionadas` |
| Compatibilidade | `openPreProjetoFromOpportunity` → wrapper `source: single_opportunity` |
| Draft local | `bloco_estr_oportunidades_selecionadas` (JSON leve, sem schema DB) |
| Formulário | `PrecadOpportunitiesConsidered.jsx` na aba Visão geral |
| Logs DEV | `opportunity_select`, `opportunity_unselect`, `selected_opportunities_count`, `preproject_multi_*` |
| Modal completo | `ConsultorAllOpportunitiesModal.jsx`, `ConsultorOpportunityCompactRow.jsx`, `consultorAllOpportunitiesFilter.js` |
| Logs modal | `all_opportunities_open/close`, `all_opportunities_filter_change`, `all_opportunities_show_more`, `opportunity_select_from_all`, `preproject_from_all_start` |

---

## 12. Arquivos existentes — índice de reaproveitamento

| Prioridade | Arquivo |
|------------|---------|
| Alta | `pages/RadarFomento.jsx`, `hooks/useRadarMatches.js`, `components/radar/ListaClientes.jsx`, `components/radar/CardEditalRadar.jsx` |
| Alta | `pages/Cadastros.jsx`, `components/admin/ProjetoPrecadastroForm.jsx`, `utils/precadastro/buildPreCadastroDraft.js` |
| Alta | `services/dataService.js`, `utils/permissions.js` |
| Média | `hooks/useEditalFavorites.js`, `services/favoritosService.js`, `utils/deadlineAlerts.js` |
| Média | `utils/radar/radarMatchExplain.js`, `components/layout/Header.jsx`, `router/index.jsx`, `config/env.js` |
| Baixa (fase 3) | `services/precadastroProjetoPdf.js`, `services/pdfExportService.js` |

---

## 13. Fora de escopo (confirmado)

- Alterar schema ou executar SQL  
- Mexer em Notícias, Pesquisas, Concursos, Portais Estratégicos  
- Alterar cálculo de score do Radar  
- Remover funcionalidades existentes  
- Tela monolítica sem integração com Cadastros/Radar/Editais  

---

## 14. Fluxo de trabalho inspirado no processo NotebookLM do cliente

### Fluxo antigo (manual)

1. Criar notebook no NotebookLM  
2. Deep Research para pesquisar oportunidades  
3. Selecionar/importar fontes  
4. Pedir tabela estruturada de editais  
5. Exportar para Google Sheets  
6. Análise manual e montagem de projetos por cliente  

### Fluxo EditalFinder (esteira de consultoria)

| Etapa | NotebookLM (referência) | EditalFinder |
|-------|-------------------------|--------------|
| 1 | Notebook / contexto | **Perfil do cliente** (`ClientForm`, completude ≥ 70%) |
| 2 | Deep Research + fontes | **Carteira de oportunidades** (Radar → matches por cliente) |
| 3 | Tabela estruturada | **Triagem** — painel top 20 + modal **Lista/Tabela** + filtros |
| 4 | Seleção na planilha | **Seleção** (até 20, compartilhada painel ↔ modal) |
| 5 | Análise manual | **Pré-projeto consultivo** (rascunho local + PDF) |
| 5b | Revisão antes do projeto | **Relatório de triagem** (visualização em tela; PDF *em breve*) |
| 6 | Export Sheets | **Menu Exportar** (top 20, selecionadas, filtradas via modal); PDF executivo *em breve* |

**Componentes (2026-05):**

- `ConsultorWorkflowSteps.jsx` — barra de etapas com status (completo / em andamento / pendente / em breve)  
- `ConsultorPortfolioSummary.jsx` — resumo “Triagem deste cliente” no modal da carteira  
- `ConsultorOpportunitiesTable.jsx` — visão tabela (colunas: programa, fonte, prazo, tipo, foco, observações, compat., link)  
- `ConsultorAllOpportunitiesModal.jsx` — alternância Lista/Tabela, filtros, **Exportar CSV**  
- `ConsultorExportMenu.jsx` — dropdown no header do cliente  
- `ConsultorTriageReportModal.jsx` + `buildTriageReportModel.js` — relatório de triagem (ver §15)

**Linguagem consultiva:** “Carteira de oportunidades”, “Explorar carteira completa”, “Relatório de triagem” (na seleção/carteira), “Gerar pré-projeto consultivo”, “Top 20 para triagem inicial”, etc.

O objetivo **não** é replicar o NotebookLM nem integrar com ele; é manter **familiaridade** com tabela estruturada e **reduzir** etapas manuais.

---

## 15. Relatório de triagem (entrega intermediária)

Entrega **mais simples** que o pré-projeto consultivo: visão resumida das oportunidades **já selecionadas** (até 20), para alinhar com o cliente antes de abrir o rascunho do pré-projeto.

### Escopo e restrições

- **Sem** alteração de schema, SQL ou score do Radar.  
- **Sem** PDF complexo nesta fase — apenas visualização em tela.  
- **Não** substitui nem quebra o fluxo de pré-projeto (`openPreProjetoFromOpportunities`).

### Onde acionar

| Local | Botão | Condição |
|-------|--------|----------|
| Barra de seleção (`ConsultorSelectionBar`) | **Relatório de triagem** | ≥1 oportunidade selecionada |
| Modal **Explorar carteira completa** | **Relatório de triagem** (mini-btn ativo) | idem |

### Conteúdo do modal (`ConsultorTriageReportModal`)

0. **Abertura executiva** — parágrafo consultivo (cliente, N selecionadas, confirmação da principal).  
1. **Resumo do cliente** — nome, razão social (se houver), perfil/segmento, % de completude do cadastro consultivo.  
2. **Resumo da carteira** — linha `X analisadas · Y selecionadas · … sem prazo · … prazo confortável`; alerta `N vencem em até 7 dias` quando aplicável. Total via `resolveAnalyzedOpportunityCount` (`totalMatches` + fallback `allMatches.length`).  
3. **Tabela das selecionadas** — Programa/Edital, Fonte, Prazo, Tipo de apoio, Compatibilidade, Observação, Link (linha da principal destacada).  
4. **Recomendação** — agrupamento heurístico (`buildTriageRecommendations`): Priorizar agora · Validar com o cliente · Acompanhar · Descartar/revisar.  
5. **Próximos passos** — checklist fixo (confirmar interesse, revisar regulamentos, reunir documentos, escolher principal, gerar pré-projeto).

### Rodapé do relatório

- **Exportar PDF — Em breve** — `disabled`.  
- **Gerar pré-projeto consultivo** — ativo; fecha o relatório e abre o modal de pré-projeto com a mesma seleção.

### Implementação

| Artefato | Função |
|----------|--------|
| `src/utils/consultor/buildTriageReportModel.js` | Monta modelo (`cliente`, `carteira`, `tableRows`, `recommendations`, `proximosPassos`) a partir de `selectedOpportunities` + `deadlineSummary` |
| `src/utils/consultor/resolveAnalyzedOpportunityCount.js` | Total analisado sem exibir 0 indevido |
| `src/utils/consultor/derivePortfolioStatusMessage.js` | Estados da carteira no painel (carregando / prévia / carregada / background) |
| `src/components/consultor/ConsultorTriageReportModal.jsx` | UI do relatório |
| `ConsultorWorkspace.jsx` | `isTriageReportOpen`, `handleGerarRelatorioTriagem`, props para carteira e modal |
| `global.css` | `.modal-consultor-triage-report`, `.consultor-triage-report-*` |

### Telemetria (`consultorWorkspaceLog`)

- `triage_report_open`, `triage_report_close`, `triage_report_preproject_click`, `triage_report_open_from_all`

### Briefing rápido do cliente (UX destacada)

| Elemento | Comportamento |
|----------|----------------|
| **Callout** (`ConsultorProfileBriefingCallout`) | Se completude &lt; 50%: alerta âmbar escuro abaixo da esteira; CTAs briefing + completar cadastro |
| **Card Perfil** | Lead + **Fazer briefing rápido** (primário se &lt; 70%) / **Atualizar briefing** (secundário se ≥ 70%) |
| **Esteira etapa 1** | Badge: Briefing recomendado (&lt; 50%), pendente (&lt; 70%), salvo (`hasBriefingContent`) |
| **Pré-projeto** | Hint se briefing disponível ou link para briefing se perfil muito baixo |
| **Modal** | 3–5 min, copy “responda só o que souber”; footer sticky com salvar / salvar + cadastro completo |

- Persistência: `applyBriefingToFormState` + `mergeClientWritePayload` (sem schema/SQL).  
- Após salvar: toast/alert, recarga da lista, completude e badge da esteira atualizam; cadastro completo só se o usuário escolher.  
- Impacto: carteira/triagem (temas, critérios); pré-projeto (`buildPreCadastroDraft`). Radar: score inalterado.

Logs DEV `[cliente-briefing]`: ver `docs/CLIENTE_PROFILE_CONSULTIVO.md`.

### Status automático do cliente

| Item | Detalhe |
|------|---------|
| **Util** | `deriveConsultorClientStatus.js` — `deriveConsultorClientStatus` (painel) e `deriveConsultorClientStatusLight` (lista, sem Radar) |
| **UI** | badge em `ConsultorClienteList`; banner em `ConsultorClientStatusBanner` no topo do painel |
| **Filtro** | select Status na lista lateral (`client_status_filter_change`) |
| **Schema** | Nenhum — sinais: completude, briefing, top/seleção, `precadSummary`, acompanhadas |

Status (prioridade): Pronto para cliente → Pré-projeto em elaboração → Triagem em andamento → Carteira pronta → Em acompanhamento → Precisa briefing → Perfil em montagem → Em análise.

Logs DEV: `client_status_derived`, `client_status_filter_change`.

### Histórico do cliente (linha do tempo)

| Item | Detalhe |
|------|---------|
| **UI** | `ConsultorClientTimelineCard.jsx`, modal `ConsultorClientTimelineModal.jsx` |
| **Storage** | `localStorage` → `consultor_client_timeline_<id_cliente>` (até 120 eventos) |
| **Eventos** | briefing salvo, perfil atualizado, triagem gerada, pré-projeto atualizado, CSV exportado, oportunidade acompanhada (add/remove) |

Logs DEV: `timeline_event_added`, `timeline_open`, `timeline_clear`, `timeline_loaded`.

### Oportunidades acompanhadas

| Item | Detalhe |
|------|---------|
| **UI** | `ConsultorTrackedOpportunitiesCard.jsx`, modal `ConsultorTrackedOpportunitiesModal.jsx` |
| **Fontes (sem schema)** | Seleção atual; JSON do rascunho de pré-projeto (`bloco_estr_oportunidades_selecionadas`); favoritos Radar (`radar_favoritos` por cliente); favoritos Supabase (`useEditalFavorites`); snapshots em `localStorage` |
| **Persistência opcional** | `consultor_tracked_opportunities_<id_cliente>` — gravado ao gerar triagem ou pré-projeto; remoção manual com `consultor_tracked_opportunities_<id>_removed` |
| **Limite card** | 5 itens + “Ver todas acompanhadas” |

Badges: **Selecionada**, **Pré-projeto**, **Favorita**, **Acompanhada** (snapshot). Ações: Ver edital, Abrir no Radar; footer: Explorar carteira, Ver favoritos (Dashboard com filtro ativo).

Logs DEV: `tracked_opportunities_loaded`, `tracked_opportunity_add`, `tracked_opportunity_remove`, `tracked_opportunity_open`.

### Plano de ação do consultor

| Item | Detalhe |
|------|---------|
| **UI** | `ConsultorActionPlanCard.jsx` — substitui o placeholder no grid secundário |
| **Regras** | `buildConsultorActionPlan.js` — deriva ações de perfil, briefing, carteira (top), seleção, `precadSummary`, `deadlineSummary` |
| **Persistência** | `localStorage` chave `consultor_action_plan_done_<id_cliente>` — ids + `reopenKey`; reabre se o estado crítico mudar |
| **Schema** | Nenhum |

**Ações típicas (prioridade):** briefing (perfil &lt; 70% sem briefing), dados essenciais, explorar carteira, triagem, pré-projeto, pendências do rascunho, prazos 7 dias, preparar apresentação (fluxo avançado).

**CTAs** reutilizam handlers do `ConsultorWorkspace`: briefing, `ClientForm`, modal carteira completa, relatório de triagem, pré-projeto.

**Logs DEV `[consultor-workspace]`:** `action_plan_generated`, `action_plan_item_click`, `action_plan_item_done`, `action_plan_item_reopened`.

### Exportação CSV / menu Exportar (header)

| Opção | Origem dos dados | Arquivo |
|--------|------------------|---------|
| **Exportar top 20 CSV** | `topMatches` (visão rápida) | `carteira_top20_<cliente>_<data>.csv` |
| **Exportar selecionadas CSV** | `selectedOpportunityRows` (até 20) | `carteira_selecionadas_<cliente>_<data>.csv` |
| **Carteira filtrada** | Abre modal **Explorar carteira completa** → botão **Exportar CSV** (selecionadas ou filtradas) | `carteira_<cliente>_<data>.csv` |
| **Relatório executivo PDF** | *Em breve* (disabled) | — |

**Componentes:** `ConsultorExportMenu.jsx`, `exportConsultorPortfolioCsv.js` (UTF-8 BOM, colunas da tabela).

**Logs DEV:** `export_menu_open`, `export_top20_csv_start`, `export_selected_csv_start`, `export_filtered_requested`, `export_pdf_soon_click`, `export_csv_success` / `export_csv_error`.

### Próxima evolução (fora deste escopo)

- Export PDF do relatório de triagem e relatório executivo para o cliente.  
- Persistir relatório no backend (opcional).

---

## 16. Referências

- [`FRONTEND_BACKEND_CONTEXT.md`](./FRONTEND_BACKEND_CONTEXT.md) — contrato de módulos  
- [`EDITAIS_FAVORITOS_ALERTAS_MVP.md`](./EDITAIS_FAVORITOS_ALERTAS_MVP.md) — favoritos por usuário  
- [`RADAR_PERFORMANCE_DIAGNOSTIC.md`](./RADAR_PERFORMANCE_DIAGNOSTIC.md) — performance e cache  
- `frontend/EditalFinder-React/docs/PRE_CADASTRO_ASSISTENTE_IMPROVEMENTS.md` — módulo pré-cadastro  
- `frontend/EditalFinder-React/src/components/admin/precadastro/NOTAS-MODULO.txt` — contexto Radar → pré-cadastro  
