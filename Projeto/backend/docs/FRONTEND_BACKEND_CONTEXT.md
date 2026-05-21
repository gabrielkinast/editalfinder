# Frontend ↔ Backend Context — EditalFinder

Este documento explica como o frontend deve consumir o backend do EditalFinder.

O backend está organizado para separar tipos diferentes de informação:

- Editais, chamadas, crédito e fomento;
- Notícias científicas;
- Pesquisas e publicações;
- Portais estratégicos;
- Fornecedores;
- Investimentos.

A regra central do produto é:

**Nem toda oportunidade estratégica é um edital.**

Por isso, o backend separa `public.edital` de `public.portal_estrategico`.

---

## 1. Visão geral do produto

O EditalFinder é uma plataforma de inteligência de oportunidades.

Ele reúne e organiza:

- editais;
- chamadas públicas;
- linhas de crédito;
- programas de fomento;
- notícias científicas;
- pesquisas e publicações;
- portais de fornecedores;
- portais de investimento;
- hubs de procurement;
- programas de internacionalização;
- oportunidades estratégicas.

O frontend não deve tratar todos esses dados como “editais”. Cada módulo tem sua própria fonte de dados.

**Retenção e expiração (sem delete por vencimento):** [`DATA_RETENTION_AND_EXPIRATION_POLICY.md`](./DATA_RETENTION_AND_EXPIRATION_POLICY.md) — o histórico fica nas tabelas base; as **views públicas** (`vw_*_front`) definem o que aparece nas listagens (editais após `prazo_envio`, notícias 12m, pesquisas 24m, concursos por datas de inscrição/prova).

---

## 2. Tabelas principais

### `public.edital`

Tabela principal para:

- editais;
- chamadas públicas;
- linhas de crédito;
- subvenção;
- fomento;
- oportunidades tradicionais;
- programas com submissão, prazo, valor ou elegibilidade.

Esta tabela alimenta principalmente:

- página de Editais;
- Radar de Fomento;
- dashboards de oportunidades.

**Visibilidade na listagem (Editais):** o histórico permanece em `public.edital`. A view `public.vw_editais_front` aplica filtros de recência, prazo, fluxo contínuo e `extras.curadoria_front` (ver [`EDITAIS_VISIBILITY_AND_NOISE_POLICY.md`](./EDITAIS_VISIBILITY_AND_NOISE_POLICY.md) e `docs/sql/UPDATE_VW_EDITAIS_FRONT_VISIBILITY.sql`). Auditoria: `scripts/audit_editais_visibility_noise.py`.

---

### `public.noticia`

Tabela para notícias científicas, tecnológicas e institucionais relevantes.

Não deve ser misturada com editais.

Alimenta:

- página de Notícias.

---

### `public.pesquisa`

Tabela para pesquisas, publicações, relatórios técnicos e documentos de pesquisa.

Não deve ser misturada com editais.

Alimenta:

- página de Pesquisas.

---

### `public.portal_estrategico`

Tabela nova para itens estratégicos que não são editais tradicionais.

Exemplos:

- supplier portals;
- supplier registration;
- iSupplier;
- HICX;
- hubs de fornecedores;
- documentação de fornecedores;
- procurement;
- portais de investimento;
- desenvolvimento;
- internacionalização;
- corporate venture;
- funding hubs.

Esta tabela alimenta a nova área:

**Portais Estratégicos**

com abas:

- Fornecedores;
- Investimentos;
- futuramente Procurement;
- futuramente Internacionalização.

O pipeline de carga dedicado (`load_portais_estrategicos`) **não escreve** em `public.edital`, evitando duplicar semanticamente oportunidades de fomento “fortes” com portais estratégicos.

---

## 3. Views principais para o frontend

O frontend deve consumir **preferencialmente as views**, não as tabelas brutas, sempre que existirem views estáveis no ambiente (staging/produção). As definições canónicas de recriação em desenvolvimento estão em `migrations/20260504_recreate_front_views_staging.sql`.

### Editais

Usar:

```sql
public.vw_editais_front
```

- Lista pública de oportunidades de fomento com colunas já alinhadas ao contrato do front (inclui aliases como `fonte` / `fim_inscricao` espelhando `fonte_recurso` / `prazo_envio`).
- Para operações ou ecrãs administrativos que espelhem a mesma projeção:

```sql
public.vw_editais_admin
```

(Atualmente definida como `SELECT *` a partir de `vw_editais_front`; confirmar no cluster se políticas RLS diferenciam admin vs público.)

**Consumo típico (Supabase JS):** `from('vw_editais_front').select(...)`.

**Visibilidade pública:** após `prazo_envio` / fim de inscrição passado, o registo sai da view padrão mas permanece em `public.edital` — ver [`DATA_RETENTION_AND_EXPIRATION_POLICY.md`](./DATA_RETENTION_AND_EXPIRATION_POLICY.md) §4.

---

### Notícias

Usar:

```sql
public.vw_noticias_front
```

- Agrega campos de `public.noticia` com nomes e coalescências úteis ao UI (ex.: `fonte` a partir de `fonte_recurso` / `fonte`).

**Consumo típico:** `from('vw_noticias_front').select(...)`.

---

### Pesquisas

Usar:

```sql
public.vw_pesquisas_front
```

- Agrega campos de `public.pesquisa` (publicações, relatórios, conteúdo de pesquisa).

**Consumo típico:** `from('vw_pesquisas_front').select(...)`.

**Janela pública:** 24 meses a partir de `data_publicacao` (histórico na tabela).

---

### Concursos & Seleções

Usar:

```sql
public.vw_concursos_front
```

- Módulo separado de `public.edital` e do Radar; tabela base `public.concurso_selecao`.
- Listagem pública: inscrição e prova encerradas (ou prova ausente) → fora da view; `status` pode ser `encerrado` no loader sem apagar a linha.
- Certames em andamento com inscrição fechada: não promover como oportunidade principal; filtro “em andamento” é evolução futura.

**Consumo típico:** `from('vw_concursos_front').select(...)` — ver também [`CONCURSOS_FRONTEND_MVP.md`](./CONCURSOS_FRONTEND_MVP.md) e política §1 em [`DATA_RETENTION_AND_EXPIRATION_POLICY.md`](./DATA_RETENTION_AND_EXPIRATION_POLICY.md).

---

### Portais estratégicos (Fornecedores / Investimentos)

No repositório atual **não há** migration canónica que crie `public.vw_portais_estrategicos_front` (ou nome equivalente). O destino de dados é a tabela **`public.portal_estrategico`**.

O frontend deve:

1. Ler **`portal_estrategico`** com filtros de produto (ver secção 4).
2. Respeitar RLS e chaves públicas do projeto Supabase.
3. Ficar atento a evoluções: o script `scripts/validate_portais_estrategicos_after_load.py` referencia vistas opcionais (`vw_fornecedores_front` ligada a `edital`, `vw_investimentos_front` se existir). A proposta SQL em `docs/sql/VW_FORNECEDORES_FRONT_PROPOSTA.sql` é **documentação / proposta**, não contrato garantido até existir migration aplicada no ambiente.

Colunas úteis para separar abas e evitar mistura com o Radar (alinhadas ao loader `load_portais_estrategicos`):

| Coluna / conceito | Uso no front |
|-------------------|--------------|
| `categoria` | `fornecedores` \| `investimentos` — partição principal entre abas. |
| `frontend_section` | Espelha a secção de UI (`fornecedores`, `investimentos`, …). |
| `mostrar_em_fornecedores` | Incluir na listagem Fornecedores quando `true`. |
| `mostrar_em_investimentos` | Incluir na listagem Investimentos quando `true`. |
| `mostrar_em_procurement` | Reservado para futura aba Procurement. |
| `mostrar_no_radar` | Para lotes estratégicos curados, o desenho de produto espera **`false`** para **não** misturar estes itens no agregador Radar de Fomento. O Radar deve continuar a basear-se em **`edital`** / `vw_editais_front` com regras de negócio adequadas. |
| `portal_tipo`, `tipo_oportunidade`, `tipo_recurso` | Taxonomia e badges; valores finais dependem da CHECK/constraints do cluster. |
| `extras` (jsonb) | Metadados de pipeline (`loaded_to`, `wave`, tipos semânticos de investimento, etc.); tratar como opaco salvo necessidade explícita de UI. |

**Consumo típico:** `from('portal_estrategico').select(...).eq('categoria', 'fornecedores')` (e análogo para `investimentos`), combinando com as flags `mostrar_em_*`.

---

## 4. Como diferenciar módulos (regras de produto)

| Módulo de UI | Fonte de dados | Regra prática |
|--------------|-----------------|----------------|
| **Editais** (lista geral) | `vw_editais_front` | Oportunidades com modelo “edital/chamada/crédito/fomento”. |
| **Radar de Fomento** | `vw_editais_front` (ou `edital` com mesma semântica) | Agregador de **fomento**; **excluir** ou não misturar conteúdo cuja intenção é “portal estratégico” (`portal_estrategico` com `mostrar_no_radar = false` não deve aparecer como card de edital no Radar). Se existirem flags em `extras` no `edital`, alinhar com o backend antes de filtrar. |
| **Notícias** | `vw_noticias_front` | Conteúdo jornalístico; **nunca** tratar como edital; feed ~12m (ver política de retenção). |
| **Pesquisas** | `vw_pesquisas_front` | Publicações e documentos de pesquisa; **nunca** tratar como edital; feed ~24m. |
| **Concursos & Seleções** | `vw_concursos_front` | Concursos, vestibulares, bolsas; **nunca** misturar com `vw_editais_front` / Radar. |
| **Fornecedores** (Portais Estratégicos) | `portal_estrategico` | `categoria = 'fornecedores'` e/ou `mostrar_em_fornecedores = true` conforme produto. |
| **Investimentos** (Portais Estratégicos) | `portal_estrategico` | `categoria = 'investimentos'` e/ou `mostrar_em_investimentos = true`. |
| **Procurement / Internacionalização** (futuro) | `portal_estrategico` | Prever filtros por `mostrar_em_procurement` ou extensões de `categoria` / taxonomia acordadas com o backend. |

**Resumo:** se o utilizador procura “submeter proposta até à data X” ou “linha de crédito com reembolso”, o caminho é **`edital` / `vw_editais_front`**. Se procura “registar-se como fornecedor”, “hub de funding” ou “portal corporativo de suppliers”, o caminho é **`portal_estrategico`** com os filtros acima.

---

## 5. Contrato com o Supabase

- Use a **anon key** no browser e políticas **RLS** adequadas nas views/tabelas expostas.
- Chaves **service role** e operações de carga pertencem apenas a scripts/backend; **não** embutir no frontend.
- Após deploy de migrations, validar no ambiente a existência das views (`vw_editais_front`, `vw_noticias_front`, `vw_pesquisas_front`) — o pipeline de staging referencia estas vistas em validações pós-diárias.

---

## 6. Referências no repositório

| Artefacto | Conteúdo |
|-----------|----------|
| `migrations/20260504_recreate_front_views_staging.sql` | DDL das views `vw_editais_*`, `vw_noticias_front`, `vw_pesquisas_front`. |
| `docs/DATA_RETENTION_AND_EXPIRATION_POLICY.md` | Política de visibilidade pública vs histórico no banco (todos os módulos). |
| [`docs/BACKEND_SOURCES_INVENTORY.md`](./BACKEND_SOURCES_INVENTORY.md) | Inventário centralizado de fontes, pipelines, `source_id`, status e artefatos (JSON: [`BACKEND_SOURCES_INVENTORY.json`](./BACKEND_SOURCES_INVENTORY.json)). |
| [`docs/EDITAIS_LINK_HEALTH_POLICY.md`](./EDITAIS_LINK_HEALTH_POLICY.md) | **Grants.gov:** links `view-opportunity.html?oppId=` são legados (SPA Page Not Found com HTTP 200); canônico **`https://simpler.grants.gov/opportunity/…`**. |
| `docs/sql/UPDATE_VW_CONCURSOS_FRONT_RECENCY.sql` | Recência actual de `vw_concursos_front`. |
| `scripts/load_portais_estrategicos.py` | Mapeamento standardized → `portal_estrategico`, categorias e flags. |
| `scripts/validate_portais_estrategicos_after_load.py` | Validação pós-carga e menção a vistas opcionais. |
| `docs/sql/VW_FORNECEDORES_FRONT_PROPOSTA.sql` | Proposta histórica baseada em `edital` para UI Fornecedores — **não** confundir com `portal_estrategico`. |

Este ficheiro é documentação de produto/contrato para equipas de frontend; alterações de schema ou RLS devem ser coordenadas com migrations e revisão DBA.

---

## 7. Workspace do Consultor (fluxo principal)

Área onde **consultores** trabalham clientes, Radar e pré-projetos. **Cadastros** permanece administrativo (usuários; clientes só para admin legado).

| Aspecto | Decisão atual |
|---------|----------------|
| **Rota** | `/workspace-consultor` (basename `/editalfinder`) |
| **Menu** | **Workspace** (`VITE_ENABLE_CONSULTOR_WORKSPACE`) |
| **Permissões (reuso)** | `canViewCadastros`, `canCreate`, `canEdit`, `filterClientsForUser`, `canViewClient`, `canEditClient` — sem novas flags nesta fase |
| **Clientes** | **Briefing rápido** (CTA principal se completude &lt; 70%; callout se &lt; 50%) + `ClientForm` (cadastro completo). `ConsultorClientBriefingModal`, `clientBriefingSignals`, `extras.perfil_consultivo`, card **Perfil do cliente** |
| **Pré-projeto** | `ProjetoPrecadastroForm`, rascunho local; hints no card quando há briefing (`buildPreCadastroDraft` consome perfil consultivo) |
| **Esteira visual** | `ConsultorWorkflowSteps` — etapa Perfil com badge de briefing; depois Carteira → Seleção → Pré-projeto → Relatório (PDF *em breve*) |
| **Oportunidades** | Painel **Carteira de oportunidades** (top 20 triagem); **Explorar carteira completa** → modal com lista **ou tabela** (estilo planilha), resumo de triagem, busca/filtros/ordenação; seleção compartilhada (até **20**); pré-projeto multi |
| **Exportação CSV** | `exportConsultorPortfolioCsv.js` — UTF-8 BOM, colunas da tabela. **Menu Exportar** no header: top 20, selecionadas, abrir carteira completa (filtradas); modal carteira: CSV selecionadas ou filtradas. **Relatório executivo PDF** — placeholder |
| **Armazenamento multi** | `bloco_estr_oportunidades_selecionadas` no rascunho local (sem alteração de schema) |
| **Plano de ação** | `ConsultorActionPlanCard` + `buildConsultorActionPlan.js`; conclusões em `consultor_action_plan_done_<id_cliente>` (localStorage, sem backend) |
| **Oportunidades acompanhadas** | `ConsultorTrackedOpportunitiesCard` + `buildConsultorTrackedOpportunities.js`; seleção, pré-projeto, favoritos Radar/Supabase; snapshots `consultor_tracked_opportunities_<id_cliente>` ao gerar triagem/pré-projeto |
| **Histórico do cliente** | `ConsultorClientTimelineCard` + `consultorClientTimeline.js`; eventos em `consultor_client_timeline_<id_cliente>` (localStorage, sem backend) |
| **Status do cliente** | `deriveConsultorClientStatus.js` — badge na lista (versão leve) e banner no painel (carteira/seleção/pré-projeto); filtro por status na coluna de clientes |
| **Cadastros (consultor)** | Banner + link para Workspace; aba **Clientes** oculta (admin mantém acesso legado) |

Futuro documentado (não implementado): `canManageUsers`, `canManageClients`, `canUseWorkspace`.

Ativar: `VITE_ENABLE_CONSULTOR_WORKSPACE=true` em `.env.local`.

**Planos:** [`CONSULTOR_WORKSPACE_PLAN.md`](./CONSULTOR_WORKSPACE_PLAN.md), [`PRE_PROJETO_CONSULTOR_IMPROVEMENTS.md`](./PRE_PROJETO_CONSULTOR_IMPROVEMENTS.md).

---

## 8. Reporte de problemas em editais (MVP)

Na aba **Editais**, cada card (e o modal/página de detalhes) pode abrir o fluxo **Reportar problema**. O MVP persiste em **`public.edital_feedback`** via Supabase client (`id_usuario` de `public.usuario`). Opcional: `VITE_EDITAL_FEEDBACK_ENDPOINT` tem prioridade se definido.

| Aspecto | Detalhe |
|---------|---------|
| **Documentação** | [`EDITAIS_FEEDBACK_AND_REPORTING.md`](./EDITAIS_FEEDBACK_AND_REPORTING.md) |
| **Tabela** | `public.edital_feedback` (RLS insert/select own) |
| **Suporte (e-mail ref.)** | `VITE_SUPPORT_EMAIL` — padrão `editalfinder@gmail.com` |
| **Edge Function** | `supabase/functions/report-edital-feedback/index.ts` (futuro e-mail) |
| **Curadoria** | Reporte não altera `vw_editais_front` nem `extras.curadoria_front` automaticamente |
