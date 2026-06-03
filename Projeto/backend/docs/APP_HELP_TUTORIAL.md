# Ajuda / Tutorial — EditalFinder

Guia para manter e estender o sistema de ajuda global do frontend (`frontend/EditalFinder-React`).

## Público-alvo

Consultores e usuários que podem ter dificuldade com tecnologia. Textos em linguagem simples: onde clicar, para que serve, o que fazer depois.

## Componentes

| Arquivo | Responsabilidade |
|---------|------------------|
| `src/components/help/helpContent.js` | Seções, busca, mapa rota → seção |
| `src/components/help/AppHelpModal.jsx` | Modal/drawer: índice, busca, corpo da seção |
| `src/components/help/AppHelpButton.jsx` | Botão reutilizável (header, menu, ícone) |
| `src/components/help/HelpPageLink.jsx` | Link **?** em páginas específicas |
| `src/components/help/HelpFirstVisitBanner.jsx` | Banner “Primeira vez aqui?” |
| `src/contexts/AppHelpContext.jsx` | Provider, `openHelp`, `?help=` |
| `src/styles/app-help.css` | Estilos (dark-friendly, responsivo) |

Integração:

- `App.jsx` — `AppHelpProvider` dentro de `BrowserRouter`
- `main.jsx` — import de `app-help.css`
- `Header.jsx` — `AppHelpButton` (texto + ícone **?**)
- `AppNavigationMenu.jsx` — item **Ajuda** no grupo Sistema

## Seções atuais

| `id` | Título |
|------|--------|
| `getting-started` | Como começar |
| `menu` | Menu principal |
| `dashboard` | Dashboard |
| `editais` | Editais |
| `edital-detalhe` | Detalhe do edital |
| `radar` | Radar de Fomento |
| `cadastros` | Cadastros |
| `workspace-consultor` | Workspace do Consultor |
| `noticias` | Notícias |
| `pesquisas` | Pesquisas |
| `portais` | Portais |
| `reportar-problema` | Reportar problema |
| `configuracoes` | Configurações |
| `faq` | Dúvidas frequentes |
| `glossario` | Glossário rápido |

Cada seção em `helpContent.js` pode ter: `objective`, `whenToUse`, `steps`, `tips`, `commonErrors`, `blocks` (subtítulos do Workspace).

Grupos do índice: `HELP_NAV_GROUPS` — Começando, Páginas, Sistema, Referência.

## Como editar conteúdo

1. Abra `src/components/help/helpContent.js`.
2. Localize o objeto em `HELP_SECTIONS` pelo `id`.
3. Altere textos (`steps`, `tips`, etc.) sem mudar componentes React.
4. Rode `npm run build` no frontend para validar.

Evite textos longos; prefira listas curtas e frases diretas.

## Como adicionar uma nova seção

1. Adicione um objeto em `HELP_SECTIONS` com `id`, `title`, `group` (um de `HELP_NAV_GROUPS`).
2. Preencha `objective`, `steps`, `tips` conforme necessário.
3. Se a seção corresponder a uma rota, adicione em `ROUTE_SECTION_MAP`:

```js
{ prefix: '/minha-rota', sectionId: 'minha-secao' },
```

4. (Opcional) Adicione `HelpPageLink` na página:

```jsx
<HelpPageLink sectionId="minha-secao" label="Como usar esta página?" />
```

## Como abrir o tutorial

### Pelo usuário

- Botão **Ajuda** no header (telas largas)
- Ícone **?** no header (mobile)
- Item **Ajuda** no menu hambúrguer (☰)
- Links **?** nas páginas principais
- Banner da primeira visita (até `editalfinder_help_seen` no `localStorage`)

### Por URL

Query `help` com o `id` da seção:

- `/dashboard?help=dashboard`
- `/editais?help=editais`
- `/workspace-consultor?help=workspace-consultor`

### Por código

```js
import { useAppHelp } from '../contexts/AppHelpContext';

const { openHelp, openHelpForCurrentPage } = useAppHelp();
openHelp('workspace-consultor');
openHelpForCurrentPage(); // usa ROUTE_SECTION_MAP
```

## Busca no tutorial

Campo “Buscar no tutorial…” no modal. Filtra por título e texto agregado (`buildSearchableText` / `HELP_SECTIONS_WITH_SEARCH`).

## Comportamento do modal

- Fecha com **Esc** ou clique fora (overlay)
- Foco inicial no campo de busca
- `body` com scroll bloqueado enquanto aberto
- Responsivo: índice acima do conteúdo em telas estreitas

## Persistência

Chave `localStorage`: `editalfinder_help_seen` = `'1'`.

Gravada ao abrir o tutorial, ao fechar o banner ou ao clicar “Ver tutorial” no banner. O modal **não** abre automaticamente.

## O que não alterar

- Backend / schema
- Workspace Científico arquivado
- Fluxo de `app_feedback` / Reportar problema (apenas documentado no tutorial)

## Validação

```bash
cd frontend/EditalFinder-React
npm run build
```

Checklist manual: header Ajuda, modal com índice e busca, seções listadas, mobile (menu + **?**), Esc fecha, menu ☰ e Reportar problema intactos.
