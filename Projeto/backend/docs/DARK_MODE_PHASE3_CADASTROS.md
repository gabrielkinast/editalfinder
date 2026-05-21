# Dark Mode — Fase 3 (Cadastros + Pré-cadastro)

Continuação das [Fase 1](./DARK_MODE_PHASE1.md) e [Fase 2](./DARK_MODE_PHASE2.md): alinhar **tema escuro** na área **Cadastros** (Usuários, Clientes, Editais cadastrados), **AdminTable** e **modal Pré-cadastro de projeto**, apenas com **CSS** e pequenos ajustes de **marcup** (classes / wrapper), sem alterar backend, Supabase, lógica de negócio, PDF (geração/conteúdo), Radar ou **Portais** (tratados na [Fase 4 — Portais](./DARK_MODE_PHASE4_PORTAIS.md)).

## Arquivos alterados

| Arquivo | Alteração |
| --- | --- |
| `frontend/EditalFinder-React/src/styles/global.css` | Tokens Fase 3; layout `.admin-*`; tabela `.admin-table`; blocos `.cad-*`; filtros por órgão; pré-cadastro `.precad-*` + overrides `.theme-dark .modal-precad .precad-prof-wrap`; responsivo admin. |
| `frontend/EditalFinder-React/src/pages/Cadastros.jsx` | Wrapper `admin-body`; filtros por órgão sem inline styles (`cad-org-filters*`); loading `cad-loading-placeholder`. |
| `frontend/EditalFinder-React/src/components/admin/AdminTable.jsx` | Célula vazia com classe `admin-table-empty`. |
| `docs/DARK_MODE_PHASE2.md` | Link para esta fase. |
| `docs/DARK_MODE_PHASE3_CADASTROS.md` | Este documento. |

## Tokens globais adicionados (`:root` / `.theme-dark`)

| Token | Uso |
| --- | --- |
| `--color-admin-body-bg` | Fundo da página Cadastros (via `.admin-body`) |
| `--color-admin-sidebar-bg` | Sidebar Cadastros |
| `--color-admin-main-bg` | Área principal ao lado da sidebar |
| `--color-table-wrap-bg` | Fundo do wrapper da tabela (`.table-container`) |
| `--color-table-row-hover` | Hover das linhas da tabela |
| `--color-table-cell-text` | Texto nas células |
| `--color-danger-text` / `--color-danger-soft` | Destaque “excluir” / ações destrutivas suaves |

## Variáveis do shell Pré-cadastro (`.precad-prof-wrap`)

Definidas no CSS e herdadas por descendentes; em **tema escuro** apenas dentro do modal: **`.theme-dark .modal-precad .precad-prof-wrap`** redefine:

- `--precad-primary`, `--precad-secondary`, `--precad-on-primary` / `on-secondary` (contraste com botões; cores de cliente via `style={themeToCssVars(...)}` continuam a sobrescrever primárias onde aplicável).
- **`--precad-ui-*`**: fundos (`--precad-ui-bg`, `-soft`, `-muted`, `-slate`, `-toolbar`), bordas, texto e misturas (`--precad-mix-pct`, `--precad-mix-ink`) para substituir `white`/`#e2e8f0` em `color-mix` e gradientes.

## Classes / blocos ajustados (resumo)

- **Cadastros**: `.admin-body`, `.admin-sidebar`, `.admin-main`, `.sidebar-link` (desktop e breakpoint mobile), `.cad-hero`, `.cad-stat-card`, `.cad-filters-panel`, `.cad-filters-clear`, badges `.cad-badge-*`, ações `.cad-btn-*`, `.cad-org-filters*`, `.cad-loading-placeholder`.
- **Tabela**: `.table-container`, `.admin-table` (`th` / `td` / hover), `.admin-table-empty`, modo responsivo (cartões em vez de thead).
- **Modais de cadastro genéricos**: `.btn-cancel`, `.btn-save`, `.btn-primary`, `.btn-action` (editar / excluir / PDF / link / precad legado).
- **Pré-cadastro**: cabeçalho, chips, botões, abas, cards, formulário (`input`/`select`/`textarea` + foco), completude, toolbar do assistente, pendências, impactos, `status-select` (com *fallbacks* para tokens globais fora do escopo precad).

## O que não foi alterado

- Serviços PDF (`precadastroProjetoPdf`, `renderPreCadastroPdf`, etc.) e modelo de dados.
- `getClientTheme` / `themeToCssVars` (continua a injetar `--precad-primary`… no nó raiz do formulário).
- Lógica de filtros, permissões, colunas da tabela e fluxos de salvar / pré-visualizar / baixar PDF.

## Limitações restantes

- **Formulários** dentro do modal “Cadastrar/Editar” (UserForm, ClientForm, EditalForm) podem ainda usar estilos legados (`form-group` misturados com cores antigas em alguns cantos).
- **PDF gerado** permanece documento claro; nenhuma alteração foi feita ao pipeline de renderização.
- **Tema por cliente** (`cor_primaria` / `cor_secundaria`): combinações muito claras no modo escuro podem exigir afinação futura caso surjam queixas de contraste.

## Como testar

1. `/cadastros` — alternar **Usuários**, **Clientes**, **Editais**; verificar sidebar, hero, filtros, tabela e hover.
2. **Clientes** — “Abrir pré-cadastro”; percorrer abas, assistente, impactos, inputs; **Salvar rascunho**, **pré-visualizar PDF**, **baixar PDF** (comportamento deve ser idêntico).
3. **Configurações** — alternar Claro / Escuro / Sistema e recarregar a página.
4. **Mobile** (largura &lt; 768px) — sidebar horizontal da página Cadastros e cartões da tabela.

**Build:** na pasta `frontend/EditalFinder-React`, executar `npm run build`.

## Próximos passos sugeridos

- Tokenizar formulários admin (UserForm / ClientForm / EditalForm) e qualquer resto de `#fff` na área Cadastros.
- **Portais Estratégicos:** ver [Fase 4 — Portais](./DARK_MODE_PHASE4_PORTAIS.md).
- Revisar **Notícias** / **Pesquisas** / outros ecrãs com ilhas claras.
- Checklist de regressão visual automatizada ou screenshots por rota.
