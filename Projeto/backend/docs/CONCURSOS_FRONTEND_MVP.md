# Concursos & Seleções — Frontend MVP

Primeira versão da listagem **Concursos & Seleções** no React (Vite), consumindo apenas a view pública do Supabase com a chave **anon** (sem `service_role`, sem alterações ao backend Python nem ao schema).

**Visibilidade vs banco:** a página mostra só o que `vw_concursos_front` expõe; registos encerrados ou fora da recência **permanecem** em `public.concurso_selecao`. Ver [`DATA_RETENTION_AND_EXPIRATION_POLICY.md`](./DATA_RETENTION_AND_EXPIRATION_POLICY.md) §1.

## Rota e menu

| Item | Valor |
|------|--------|
| Rota | `/concursos` (com `basename` da app: `/editalfinder/concursos` em deploy típico) |
| Ficheiro da página | `frontend/EditalFinder-React/src/pages/Concursos/ConcursosPage.jsx` |
| Menu | Entrada **Concursos** no `Header`, visível quando `VITE_ENABLE_CONCURSOS` é verdadeiro |

A página está protegida por `ProtectedRoute` como as restantes áreas autenticadas.

## Views consumidas

| Função (service) | View (env) | Uso na página MVP |
|------------------|------------|-------------------|
| `fetchConcursos()` | `VITE_VIEW_CONCURSOS` → default `vw_concursos_front` | Lista principal, filtros, abas e contadores |
| `fetchVestibulares()` | `VITE_VIEW_VESTIBULARES` → default `vw_vestibulares_front` | Implementada no service para reutilização futura; **a página MVP usa só `fetchConcursos`** e filtra a aba Vestibulares no cliente |

## Variáveis de ambiente

Definidas em `.env.example` e lidas em `src/config/env.js`:

| Variável | Export JS | Default |
|----------|-----------|---------|
| `VITE_VIEW_CONCURSOS` | `VIEW_CONCURSOS` | `vw_concursos_front` |
| `VITE_VIEW_VESTIBULARES` | `VIEW_VESTIBULARES` | `vw_vestibulares_front` |
| `VITE_ENABLE_CONCURSOS` | `ENABLE_CONCURSOS` | `true` |

Com `ENABLE_CONCURSOS=false`, o item de menu some e a rota mostra mensagem de módulo desativado.

## Service

`src/services/concursosService.js`

- `fetchConcursos()` — paginação interna (até 800 linhas por pedido) com fallback de ordenação (`atualizado_em` → `id_concurso` → `criado_em`).
- `fetchVestibulares()` — idem sobre `VIEW_VESTIBULARES`.
- `normalizeConcursoRow(row)` — booleans e números para campos calculados da view.

Cliente: `src/services/supabaseClient.js` (anon).

## Componentes

| Ficheiro | Função |
|----------|--------|
| `src/pages/Concursos/ConcursosPage.jsx` | Abas, filtros Fase 2, chips, contadores, grelha de cards |
| `src/pages/Concursos/ConcursosPage.css` | Layout sidebar, chips, contadores, tokens de tema |
| `src/utils/concursos/concursosFilters.js` | Lógica pura: filtros, abas, busca, chips, estatísticas |
| `src/utils/concursos/concursosFilters.test.js` | Testes Vitest da lógica de filtros |
| `src/components/cards/ConcursoCard.jsx` | Card com campos pedidos, badges e ações Abrir / Edital |
| `src/components/cards/ConcursoCard.css` | Estilo do card e badges |
| `src/utils/concursos/concursosLabels.js` | Rótulos PT para `tipo_selecao` e `status`; `getConcursoBadges()` |

Ajuste menor em `src/components/states/LoadingState.jsx`: cores com `var(--color-text)` / `var(--color-muted)` para alinhar ao dark mode.

## Filtros e abas (Fase 2 — 2026)

Documentação detalhada: [CONCURSOS_FILTROS_EXPANSAO.md](./CONCURSOS_FILTROS_EXPANSAO.md).

- **Abas**: Todos; Concursos públicos (`concurso_publico`, `processo_seletivo`); Professores; Técnicos/Administrativos; Vestibulares (`vestibular`, `programa_ingresso`); Residências (`residencia`); Bolsas (`bolsa_estudo`).
- **Filtros**: fonte/banca (select fixo), tipo, status, **instituição/órgão (texto)**, tipo de instituição (heurística), estado, município, escolaridade, área/cargo/curso; checkboxes (válidos, edital, data fim, inscrições abertas, prova próxima, salário/bolsa, taxa).
- **Busca**: título, órgão, instituição, banca, cargo, curso, área, município, estado, fonte, tags.
- **UX**: chips de filtros ativos, estado vazio explicativo, contadores (total, inscrições abertas, com edital, válidos, provas próximas, vestibulares/ingresso).
- **Ordenação**: `data_fim_inscricao` ascendente; sem datas, `id_concurso` descendente.

## Wave 1 — dados em staging

Com apply staging da Wave 1 (**33 upserts** nos relatórios loader), a rota `/concursos` em **staging** pode listar, entre outras:

| `fonte` | Notas para a UI |
|---------|-----------------|
| `pci_concursos` | 12 linhas; `validacao_status` em geral **incompleto**; útil para testes de volume |
| `fundatec` | 2 linhas do subset válido (ex. Porto Alegre, Morro Reuter) |
| `quadrix` | 10 linhas; todas **valido** no standardized |
| `legalle` | 5 linhas válidas |
| `objetiva` | 3 linhas válidas |
| `ibfc` | 1 linha válida |

A **view** `vw_concursos_front` aplica filtros de recência (`data_fim_inscricao`, `data_prova`, publicação recente). Registos na tabela podem não aparecer nos cards se estiverem fora da janela — especialmente PCI e certames já encerrados. Política canónica: [`DATA_RETENTION_AND_EXPIRATION_POLICY.md`](./DATA_RETENTION_AND_EXPIRATION_POLICY.md) (futuro filtro “em andamento” para inscrição fechada com prova futura).

Consolidado: [`concursos_wave1_consolidado.md`](../audit_reports_main_pipeline/concursos_wave1_consolidado.md). Filtros da página (banca, estado, inscrições abertas) passam a ter mais opções à medida que novas fontes entram em staging.

## Limitações (MVP)

- Sem favoritos de concursos, sem admin, sem crawler.
- `fetchVestibulares` não é chamada pela página (evita pedido duplicado); a aba Vestibulares filtra a lista já carregada.
- Contadores do topo são sobre **todo** o conjunto devolvido pela view (não refletem só a aba ativa).
- `prova_proxima` na view segue a regra SQL (ex.: janela de 30 dias); a UI apenas exibe o booleano.
- RLS e grants no Supabase têm de permitir `SELECT` anon na view; credenciais em `.env.local`.

## Próximos passos sugeridos

- Usar `fetchVestibulares` quando a lista global for grande e a aba Vestibulares for a única necessária.
- Paginação ou infinite scroll no cliente.
- Rota de detalhe e favoritos `concurso_favorito` (tabela própria).
- Integração com `vw_concursos_admin` para backoffice.

## Build

Validar localmente:

```bash
cd frontend/EditalFinder-React && npm run build
```
