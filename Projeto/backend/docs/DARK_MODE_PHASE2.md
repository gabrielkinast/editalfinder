# Dark Mode — Fase 2 (dashboard / Editais / filtros)

Continuação da [Fase 1](./DARK_MODE_PHASE1.md): reduzir “ilhas claras” no tema escuro, com foco na **página Editais**, **sidebar de filtros**, **cards** e **controles de listagem**, sem alterar backend, Supabase, lógica de filtros/Radar/PDF ou fórmula de score.

**Atualização:** a área **Cadastros / Pré-cadastro** foi tratada na [Fase 3 — Cadastros](./DARK_MODE_PHASE3_CADASTROS.md).

## Arquivos alterados

- `frontend/EditalFinder-React/src/styles/global.css` — tokens, overrides `.theme-dark` e regras de layout/cards/filtros.
- `docs/DARK_MODE_PHASE1.md` — link para esta fase.
- `docs/DARK_MODE_PHASE2.md` — este documento.

## Tokens CSS (Fase 2)

Os seguintes tokens já existiam ou foram consolidados no `:root` e redefinidos em `.theme-dark` (ver blocos “Fase 2” em `global.css`):

| Token | Uso principal |
| --- | --- |
| `--color-bg-page` | Fundo do layout dashboard |
| `--color-sidebar` | Sidebar / painel de filtros |
| `--color-card` / `--color-card-hover-border` | Superfície e hover dos cards |
| `--color-input-bg` / `--color-input-text` | Inputs, selects, buscas |
| `--color-range-track` / `--color-highlight-soft` | Sliders e realces suaves |
| `--nav-hover-bg` / `--nav-active-bg` | Itens de navegação no header |
| `--color-table-header` / `--color-table-row` | Tabelas (preparação) |
| `--color-overlay` / `--color-backdrop` | Sobreposições |
| `--color-focus-ring` | Foco acessível |
| `--badge-*` | Badges semânticos (ok / warn / bad / info / muted) |
| `--stat-*` | Pills da barra de estatísticas e chips relacionados |
| `--chip-filter-bg` / `--chip-filter-text` | Chips de filtro ativos |
| `--skeleton-shine-from` / `--skeleton-shine-mid` | Skeleton loading |
| `--color-search-hit-bg` | Destaque de termo na busca |

## Áreas corrigidas nesta fase

- **Layout dashboard**: `.dashboard-container`, `.sidebar`, `.main-content` (superfícies escuras coerentes).
- **Navegação (header)**: `.nav-item` com hover/active baseados em tokens (sem `#F0F7FF` fixo); labels só texto (sem emojis/ícones decorativos no menu principal).
- **Filtros Editais v2**: barra de estatísticas (`.editais-stats-bar`, pills), hints com `code`, ações rápidas (`.editais-quick-actions`), blocos colapsáveis (`.editai-filter-collapse*`), chips (`.filter-chip*`), toolbar de exportação/ordenação (`select`).
- **Cabeçalho da sidebar de filtros**: `.editai-filters-head` (flex, borda inferior, botão “Limpar filtros” sem `width: 100%` conflitante).
- **Cards de edital (visual)**: descrição, texto secundário, badges mini, prazo vencido/vazio, botão outline, destaque de busca, skeleton.
- **Modal detalhes edital**: título, descrição, labels/valores, alertas e bloco `pre` com fundo/borda temáticos.
- **Radar (apenas CSS do campo de busca)**: `.radar-busca-input` passa a usar `--color-border`, `--color-input-bg`, `--color-input-text` e foco com `--color-focus-ring` (sem mudança de comportamento).

## Testes manuais (checklist)

Verificação recomendada com **tema escuro** e **claro** (Configurações → Aparência):

| Rota | O que observar |
| --- | --- |
| `/editais` | Sidebar, filtros colapsáveis, chips, stats bar, cards, skeleton |
| `/cadastros` | Legibilidade geral (muitos estilos ainda legados “precad”) |
| `/radar-fomento` ou `/radar` | Campo de busca e painéis |
| `/portais-estrategicos`, `/noticias`, `/pesquisas` | Nenhuma área crítica ilegível |

**Build:** após alterações, executar na pasta do frontend:

`npm run build`

## Limitações restantes

- **Login e marketing-style blocks**: gradientes claros propositais; não foram redesenhados.
- **Radar**: além do input de busca, outros painéis ainda podem ter fundos claros herdados (`#fff`, `#f8fafc` em alguns estados de cartão/lista).
- **Cadastros / Pré-cadastro**: ver [Fase 3 — Cadastros](./DARK_MODE_PHASE3_CADASTROS.md) (coberto na Fase 3).
- **Variáveis legadas** (`--text-dark`, `--bg-white`, `--border-light`) ainda aparecem em várias seções do `global.css`; a migração continua incremental.

## Próximos passos sugeridos (Fase 4)

- Revisar **feed / notícias / portais** para superfícies e tipografia.
- Formulários admin dentro dos modais de cadastro (UserForm / ClientForm / EditalForm).
- Opcional: `--border-color` legado → unificar em `--color-border` em todo o ficheiro.
- Checklist de regressão visual automatizada ou screenshots por rota.
