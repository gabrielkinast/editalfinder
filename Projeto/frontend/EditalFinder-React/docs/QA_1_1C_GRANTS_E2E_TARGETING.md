# QA 1.1C — Grants.gov E2E Targeting Fix

## Problema

Após FRONTEND 1.1F, `grants-links.spec.js` falhou com **timeout de 180s** (antes skipava em ~20s).

## Causa do timeout

1. **`addInitScript` tardio** — o patch de `window.open` era aplicado *depois* de `requireCatalogReady` já ter navegado; o hook não valia para a página atual.
2. **`window.location.assign` como fallback** — em `openExternalUrl`, quando `window.open` retorna `null` (comum em headless), a app navega a página inteira para grants.gov → contexto Playwright fecha ou trava.
3. **Cliques em todos os cards** — o spec clicava até 15 botões externos em *qualquer* card (não só Grants), com timeout padrão de 30s por clique.
4. **Botões sem `href`** — `ExternalActionButton` usa `<button>`; leitura de `href` falhava e o teste dependia só de cliques.
5. **Dados filtrados** — catálogo pode não exibir Grants.gov até relaxar filtros / buscar / filtrar fonte.

## Correções (QA 1.1C)

| Item | Arquivo |
|------|---------|
| Hook `window.open` + bloqueio `location.assign/replace` **antes** de qualquer goto | `tests/e2e/_grants.js` → `installGrantsE2eHooks` em `beforeEach` |
| Descoberta multi-estratégia com deadline 20s | `discoverGrantsCards` |
| Skip rápido + evidência rica | `saveGrantsSkipEvidence` |
| URLs lidas de `data-qa-resolved-url` / `title` sem navegar | `collectGrantsUrlsFromCards` |
| Cliques só em cards Grants (máx. 3), `noWaitAfter`, 3s | `clickGrantsOfficialButtons` |
| Filtro fonte sidebar | `trySourceFilterGrants` + `data-testid="editais-fonte-busca"` |
| Detecção de fonte | `isGrantsGovSource`, `isGrantsCardRecord` |
| Atributo QA na URL resolvida | `data-qa-resolved-url` em `ExternalActionButton` |

## Estratégias de localização (ordem)

1. `data-fonte` / `data-source` + URLs resolvidas no DOM
2. Relaxar filtros (`relax-filters-button`)
3. Busca global por `Grants`
4. Filtro sidebar `Grants.gov`
5. Busca global por `Grants.gov`
6. Texto visível do card

Se nenhuma estratégia achar card em **≤20s** após catálogo carregado → **skip** (não timeout).

## Quando passa

- Encontrou ≥1 card Grants.gov
- Nenhuma URL coletada/clicada contém `page-not-found`, `simpler.grants.gov/opportunity`, `view-opportunity`

## Quando skipa

- `no_grants_cards_visible` — sem cards Grants no DOM visível após estratégias
- Evidência: `qa/artifacts/playwright/debug-authenticated-data/grants-links-skip.{json,txt,png}`

## Quando falha

- Card Grants encontrado, mas URL quebrada/não canonicalizada
- Evidência: `grants-links-failure.{json,txt,png}`

## Timeouts locais

| Fase | Limite |
|------|--------|
| Catálogo | 90s (`catalogTimeout`) |
| Busca Grants | 20s (`GRANTS_SEARCH_DEADLINE_MS`) |
| Clique por botão | 3s + `noWaitAfter` |
| Teste global | 120s (não 180s) |

## Limitações

- Skip é aceitável se o catálogo autenticado não expõe Grants.gov após filtros.
- Teste valida URLs **resolvidas no frontend** (canonicalização 1.1G), não o site grants.gov ao vivo.
- Máximo 3 cliques por execução (amostra).

## Próximo patch

**SECURITY 1.0A** ou **BACKEND 10.3B** (duplicatas Grants.gov) conforme prioridade do time.
