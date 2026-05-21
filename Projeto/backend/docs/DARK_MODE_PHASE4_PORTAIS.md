# Dark Mode — Fase 4 (Portais Estratégicos)

Continuação das fases anteriores ([Fase 1](./DARK_MODE_PHASE1.md), [Fase 2](./DARK_MODE_PHASE2.md), [Fase 3](./DARK_MODE_PHASE3_CADASTROS.md)): alinhar o **tema escuro** na rota **`/portais-estrategicos`**, sem alterar backend, Supabase, serviços de dados, Radar, Editais ou Cadastros.

## Arquivos alterados

| Arquivo | Alteração |
| --- | --- |
| `frontend/EditalFinder-React/src/styles/global.css` | Tokens `--portais-*`; estilos **`.status-badge`** (variantes com `--badge-*`); **`.precad-nav-tab`** com *fallbacks* para uso fora do modal + regra **`.precad-prof-wrap .precad-nav-tab.is-active`**; botão **`.filter-toggle-mobile`** com `--color-on-primary`. |
| `frontend/EditalFinder-React/src/pages/PortaisEstrategicos/PortaisEstrategicosPage.css` | Chips de estatísticas, toolbar, subtítulo, filtros, botão limpar, grelha; largura total dos inputs/selects na sidebar. |
| `frontend/EditalFinder-React/src/components/cards/PortalEstrategicoCard.css` | Título, meta, resumo, botões, *microhint* com tokens; bloco **`.theme-dark`** para **`.portais-tipobadge--*`** (contraste no escuro). |
| `frontend/EditalFinder-React/src/pages/PortaisEstrategicos/PortaisEstrategicosPage.jsx` | Classe **`portais-sort-select`** no `select` de ordenação (sem estilo inline). |
| `frontend/EditalFinder-React/src/components/filters/PortalEstrategicoFilters.jsx` | Remoção de estilo inline no campo de busca (usa `filter-input-large` + CSS da página). |
| `frontend/EditalFinder-React/src/components/badges/StatusBadge.jsx` | Passa a usar classes CSS em vez de cores inline (compatível com tema). |
| `docs/DARK_MODE_PHASE3_CADASTROS.md` | Referência à Fase 4 e atualização dos “próximos passos”. |
| `docs/DARK_MODE_PHASE4_PORTAIS.md` | Este documento. |

## Tokens (`:root` / `.theme-dark`)

| Token | Uso |
| --- | --- |
| `--portais-stat-bg` | Fundo dos contadores da barra de estatísticas |
| `--portais-stat-accent-bg` / `--portais-stat-accent-border` | Chip “Acesso limitado” |
| `--portais-stat-tab-bg` / `--portais-stat-tab-border` / `--portais-stat-tab-strong` | Destaque da aba ativa nos chips |
| `--portais-clear-btn-bg` / `--portais-clear-hover` | Botão “Limpar filtros” na sidebar de portais |

## Comportamento preservado (tema claro)

- No modo claro, **badges de tipo** (`.portais-tipobadge--*`) mantêm as cores **Material-like** já usadas (apenas metadados do card e CTAs passaram a tokens globais).
- Layout, filtros e ordenação **não** mudaram funcionalmente.

## Abas Fornecedores / Investimentos

A página reutiliza **`precad-nav-tabs` / `precad-nav-tab`** (mesmas classes do pré-cadastro). A Fase 4 corrige o uso **fora** do `.precad-prof-wrap` com variáveis de *fallback* (`--color-border`, `--color-input-bg`, …) e mantém o aspeto do **modal** com a regra mais específica **`.precad-prof-wrap .precad-nav-tab.is-active`**.

## Limitações

- **LoadingState / ErrorState / EmptyState** na página de portais: se ainda existirem cores fixas nesses componentes partilhados, podem precisar de uma fase dedicada “estados globais”.
- **Contraste fino** em algumas variantes raras de `tipo` de portal: ajustar sob feedback real de utilizadores.

## Como testar

1. Abrir **`/portais-estrategicos`** em tema **Escuro** e **Claro**.
2. Alternar **Fornecedores** / **Investimentos**; verificar abas, chips e contadores.
3. Usar filtros, ordenação, **Abrir portal** / **Copiar link**; validar legibilidade dos badges.
4. Largura estreita (&lt; 1024px): sidebar de filtros e botão móvel de filtros.

**Build:** `npm run build` na pasta `frontend/EditalFinder-React`.

## Próximos passos sugeridos (Fase 5)

- Estados partilhados (`LoadingState`, `ErrorState`, `EmptyState`) com tokens.
- **Notícias** / **Pesquisas** / outras rotas com ilhas claras.
